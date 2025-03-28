from flask import Blueprint, jsonify, request, current_app, render_template, flash, redirect, url_for
from app.models.segment import Segment, candidate_segments
from app.models.candidate import Candidate
from app import db
import pandas as pd
import os
import sys
from sqlalchemy import func

# Add the project root to the path to import the ml module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ml.segmentation import AudienceSegmentation

# Create two blueprints, one for API and one for web routes
segments_api_bp = Blueprint('segments_api', __name__, url_prefix='/api/segments')
segments_bp = Blueprint('segments', __name__, url_prefix='/segments')

# Web routes for dashboard
@segments_bp.route('/', methods=['GET'])
def list_segments():
    """Display segments in the dashboard."""
    segments = Segment.query.all()
    
    # Count candidates per segment for visualization
    segment_data = []
    segment_names = []
    segment_counts = []
    
    for segment in segments:
        # Get candidates count
        candidate_count = db.session.query(func.count(candidate_segments.c.candidate_id)).filter(
            candidate_segments.c.segment_id == segment.id
        ).scalar() or 0
        
        # Get traits for this segment from its description
        traits = []
        if segment.description:
            # Parse traits from description (in a real app, this would be structured data)
            traits_desc = segment.description.split(". ")
            for trait_desc in traits_desc[:3]:  # Get at most 3 traits
                if ":" in trait_desc:
                    name, value = trait_desc.split(":", 1)
                    traits.append({"name": name.strip(), "value": value.strip()})
        
        segment_data.append({
            "id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "candidate_count": candidate_count,
            "traits": traits
        })
        
        segment_names.append(segment.name)
        segment_counts.append(candidate_count)
    
    return render_template(
        'dashboard/segments.html',
        segments=segment_data,
        segment_names=segment_names,
        segment_counts=segment_counts
    )

@segments_bp.route('/<int:segment_id>', methods=['GET'])
def view_segment(segment_id):
    """View details of a specific segment."""
    segment = Segment.query.get_or_404(segment_id)
    
    # Get candidates in this segment
    segment_candidates = Candidate.query.join(
        candidate_segments, candidate_segments.c.candidate_id == Candidate.id
    ).filter(
        candidate_segments.c.segment_id == segment_id
    ).all()
    
    # Process segment criteria for better visualization
    segment_criteria = {}
    if segment.criteria:
        try:
            if isinstance(segment.criteria, str):
                import json
                criteria_dict = json.loads(segment.criteria)
            else:
                criteria_dict = segment.criteria
                
            # Extract characteristics if they exist
            if 'characteristics' in criteria_dict:
                segment_criteria = criteria_dict['characteristics']
            else:
                segment_criteria = criteria_dict
        except Exception as e:
            current_app.logger.error(f"Error parsing segment criteria: {str(e)}")
    
    # Get all available segments for comparison
    all_segments = Segment.query.filter(Segment.id != segment_id).all()
    
    # Get segment benchmark data using the segmentation service
    from ml.segment_service import segmentation_service
    segment_details = segmentation_service.get_segment_details(segment_id)
    
    # Extract benchmark and percentile data
    segment_benchmark = segment_details.get('benchmark', {})
    segment_percentiles = segment_details.get('percentiles', {})
    
    return render_template(
        'dashboard/segment_detail.html',
        segment=segment,
        candidates=segment_candidates,
        segment_criteria=segment_criteria,
        all_segments=all_segments,
        segment_benchmark=segment_benchmark,
        segment_percentiles=segment_percentiles
    )

@segments_bp.route('/refresh', methods=['GET', 'POST'])
def refresh_segments():
    """Run segmentation algorithm to refresh segments."""
    from app.tasks.ml_tasks import run_segmentation_task
    from app.models.task import Task
    
    if request.method == 'POST':
        try:
            # Run segmentation asynchronously
            task = run_segmentation_task.delay(
                n_clusters=int(request.form.get('n_clusters', 5))
            )
            
            # Record task in database
            Task.create_task(task.id, 'run_segmentation')
            
            flash(f"Segmentation task started. Task ID: {task.id}", "info")
            return redirect(url_for('segments.list_segments'))
        except Exception as e:
            flash(f"Error starting segmentation task: {str(e)}", "danger")
            return redirect(url_for('segments.list_segments'))
    
    # Get recent tasks for display
    from app.models.task import Task
    recent_tasks = Task.get_recent_tasks(limit=5)
    
    return render_template(
        'dashboard/refresh_segments.html', 
        recent_tasks=recent_tasks
    )

@segments_bp.route('/<int:segment_id>/edit', methods=['GET', 'POST'])
def edit_segment(segment_id):
    """Edit a segment manually."""
    segment = Segment.query.get_or_404(segment_id)
    
    if request.method == 'POST':
        try:
            # Update segment details
            segment.name = request.form.get('name', segment.name)
            segment.description = request.form.get('description', segment.description)
            
            # Process criteria
            criteria = {}
            for key in request.form:
                if key.startswith('criteria_'):
                    criteria_key = key.replace('criteria_', '')
                    # Convert numeric values to appropriate types
                    value = request.form.get(key)
                    try:
                        if '.' in value:
                            criteria[criteria_key] = float(value)
                        else:
                            criteria[criteria_key] = int(value)
                    except (ValueError, TypeError):
                        criteria[criteria_key] = value
            
            # Check for reset requests
            reset_fields = []
            for key in request.form:
                if key.startswith('reset_'):
                    field_name = key.replace('reset_', '')
                    reset_fields.append(field_name)
            
            # If we have existing criteria, update it rather than replace completely
            if segment.criteria:
                try:
                    if isinstance(segment.criteria, str):
                        import json
                        existing_criteria = json.loads(segment.criteria)
                    else:
                        existing_criteria = segment.criteria
                    
                    # Store original values if this is the first edit
                    if 'characteristics' in existing_criteria and 'original_values' not in existing_criteria:
                        existing_criteria['original_values'] = existing_criteria['characteristics'].copy()
                    
                    # Handle reset requests
                    if reset_fields and 'original_values' in existing_criteria:
                        for field in reset_fields:
                            if field in existing_criteria['original_values']:
                                criteria[field] = existing_criteria['original_values'][field]
                    
                    # Update characteristics
                    if 'characteristics' in existing_criteria:
                        existing_criteria['characteristics'].update(criteria)
                    else:
                        existing_criteria.update(criteria)
                    
                    segment.criteria = existing_criteria
                except Exception as e:
                    current_app.logger.error(f"Error updating segment criteria: {str(e)}")
                    segment.criteria = criteria
            else:
                segment.criteria = {'characteristics': criteria}
            
            # Handle candidate assignments if provided
            candidate_ids = request.form.getlist('candidates')
            if candidate_ids:
                # Convert to integers
                candidate_ids = [int(cid) for cid in candidate_ids if cid.isdigit()]
                
                # Update candidate_ids JSON field
                segment.candidate_ids = candidate_ids
                
                # Clear existing associations
                db.session.execute(
                    candidate_segments.delete().where(candidate_segments.c.segment_id == segment_id)
                )
                
                # Create new associations
                for candidate_id in candidate_ids:
                    db.session.execute(
                        candidate_segments.insert().values(
                            candidate_id=candidate_id,
                            segment_id=segment_id
                        )
                    )
            
            db.session.commit()
            flash(f"Segment '{segment.name}' updated successfully", "success")
            return redirect(url_for('segments.view_segment', segment_id=segment_id))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating segment: {str(e)}", "danger")
    
    # Get segment criteria for form
    segment_criteria = {}
    original_values = {}
    if segment.criteria:
        try:
            if isinstance(segment.criteria, str):
                import json
                criteria_dict = json.loads(segment.criteria)
            else:
                criteria_dict = segment.criteria
                
            # Extract characteristics if they exist
            if 'characteristics' in criteria_dict:
                segment_criteria = criteria_dict['characteristics']
                
                # Get original values if they exist
                if 'original_values' in criteria_dict:
                    original_values = criteria_dict['original_values']
            else:
                segment_criteria = criteria_dict
        except Exception as e:
            current_app.logger.error(f"Error parsing segment criteria: {str(e)}")
    
    # Get candidates in this segment
    segment_candidates = Candidate.query.join(
        candidate_segments, candidate_segments.c.candidate_id == Candidate.id
    ).filter(
        candidate_segments.c.segment_id == segment_id
    ).all()
    
    # Get all candidates not in this segment for potential addition
    other_candidates = Candidate.query.filter(
        ~Candidate.id.in_([c.id for c in segment_candidates])
    ).limit(100).all()  # Limit to 100 to avoid performance issues
    
    # Get benchmark data for comparison
    from ml.segment_service import segmentation_service
    segment_details = segmentation_service.get_segment_details(segment_id)
    segment_benchmark = segment_details.get('benchmark', {})
    
    # Check if this is an ML-generated segment
    is_ml_generated = False
    if segment.segment_code and segment.segment_code.startswith('CLUSTER_'):
        is_ml_generated = True
    
    return render_template(
        'dashboard/segment_edit.html',
        segment=segment,
        segment_criteria=segment_criteria,
        segment_candidates=segment_candidates,
        other_candidates=other_candidates,
        segment_benchmark=segment_benchmark,
        original_values=original_values,
        is_ml_generated=is_ml_generated
    )

@segments_bp.route('/compare', methods=['GET'])
def compare_segments():
    """Compare multiple segments."""
    segment_ids = request.args.getlist('segment_ids', type=int)
    
    if not segment_ids or len(segment_ids) < 2:
        flash("Please select at least two segments to compare", "warning")
        return redirect(url_for('segments.list_segments'))
    
    segments = Segment.query.filter(Segment.id.in_(segment_ids)).all()
    
    if len(segments) < 2:
        flash("Could not find the selected segments", "warning")
        return redirect(url_for('segments.list_segments'))
    
    # Get segment benchmark data using the segmentation service
    from ml.segment_service import segmentation_service
    
    # Prepare comparison data
    comparison_data = []
    for segment in segments:
        # Get candidates count
        candidate_count = db.session.query(func.count(candidate_segments.c.candidate_id)).filter(
            candidate_segments.c.segment_id == segment.id
        ).scalar() or 0
        
        # Process criteria
        segment_criteria = {}
        if segment.criteria:
            try:
                if isinstance(segment.criteria, str):
                    import json
                    criteria_dict = json.loads(segment.criteria)
                else:
                    criteria_dict = segment.criteria
                    
                # Extract characteristics if they exist
                if 'characteristics' in criteria_dict:
                    segment_criteria = criteria_dict['characteristics']
                else:
                    segment_criteria = criteria_dict
            except Exception as e:
                current_app.logger.error(f"Error parsing segment criteria: {str(e)}")
        
        # Get detailed segment info including percentiles
        segment_details = segmentation_service.get_segment_details(segment.id)
        segment_percentiles = segment_details.get('percentiles', {})
        
        comparison_data.append({
            'id': segment.id,
            'name': segment.name,
            'description': segment.description,
            'candidate_count': candidate_count,
            'criteria': segment_criteria,
            'percentiles': segment_percentiles
        })
    
    # Get all criteria keys across all segments
    all_criteria_keys = set()
    for segment_data in comparison_data:
        all_criteria_keys.update(segment_data['criteria'].keys())
    
    # Get global benchmark data
    benchmark_data = segmentation_service.get_segment_benchmarks()
    
    return render_template(
        'dashboard/segment_compare.html',
        segments=comparison_data,
        all_criteria_keys=all_criteria_keys,
        segment_benchmark=benchmark_data
    )

@segments_bp.route('/create-manual', methods=['GET', 'POST'])
def create_manual_segment():
    """Create a new segment manually."""
    if request.method == 'POST':
        try:
            # Create new segment
            new_segment = Segment(
                name=request.form.get('name', 'New Manual Segment'),
                description=request.form.get('description', 'Manually created segment'),
                segment_code=f"MANUAL_{int(datetime.utcnow().timestamp())}"
            )
            
            # Process criteria
            criteria = {}
            for key in request.form:
                if key.startswith('criteria_'):
                    criteria_key = key.replace('criteria_', '')
                    criteria[criteria_key] = request.form.get(key)
            
            new_segment.criteria = {
                'characteristics': criteria,
                'manual': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            db.session.add(new_segment)
            db.session.flush()  # Get ID without committing
            
            # Handle candidate assignments if provided
            candidate_ids = request.form.getlist('candidates')
            if candidate_ids:
                # Convert to integers
                candidate_ids = [int(cid) for cid in candidate_ids if cid.isdigit()]
                
                # Update candidate_ids JSON field
                new_segment.candidate_ids = candidate_ids
                
                # Create associations
                for candidate_id in candidate_ids:
                    db.session.execute(
                        candidate_segments.insert().values(
                            candidate_id=candidate_id,
                            segment_id=new_segment.id
                        )
                    )
            
            db.session.commit()
            flash(f"Segment '{new_segment.name}' created successfully", "success")
            return redirect(url_for('segments.view_segment', segment_id=new_segment.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating segment: {str(e)}", "danger")
    
    # Get sample candidates for selection
    candidates = Candidate.query.limit(100).all()  # Limit to 100 to avoid performance issues
    
    return render_template(
        'dashboard/segment_create.html',
        candidates=candidates
    )

# API routes
@segments_api_bp.route('/', methods=['GET'])
def get_segments():
    """Get all segments."""
    from app.utils.api_responses import api_success
    
    segments = Segment.query.all()
    return api_success(
        data=[segment.to_dict() for segment in segments]
    )

@segments_api_bp.route('/<int:segment_id>', methods=['GET'])
def get_segment(segment_id):
    """Get a specific segment."""
    from app.utils.api_responses import api_success
    
    segment = Segment.query.get_or_404(segment_id)
    return api_success(
        data=segment.to_dict()
    )

@segments_api_bp.route('/', methods=['POST'])
def create_segment():
    """Create a new segment."""
    from app.utils.api_responses import api_success, api_error
    from app.utils.realtime import broadcast_entity_change, entity_changed
    from app.services.notification_service import NotificationService
    from app.models.notification import NotificationType, NotificationCategory
    from flask_login import current_user
    import logging
    
    logger = logging.getLogger(__name__)
    
    data = request.json
    
    if not data or not data.get('name'):
        return api_error('Missing required fields')
    
    new_segment = Segment(
        name=data.get('name'),
        description=data.get('description'),
        criteria=data.get('criteria', {})
    )
    
    db.session.add(new_segment)
    db.session.commit()
    
    # Create notification for new segment
    try:
        NotificationService.create_notification(
            title="Segment Created",
            message=f"New segment '{new_segment.name}' has been created.",
            type=NotificationType.SUCCESS,
            category=NotificationCategory.SEGMENT,
            related_entity_type="segment",
            related_entity_id=new_segment.id
        )
    except Exception as e:
        logger.error(f"Error creating notification for new segment: {str(e)}")
    
    # Broadcast real-time update
    try:
        entity_changed(
            entity_type='segment',
            entity_id=new_segment.id,
            update_type='created',
            entity_data=new_segment.to_dict()
        )
    except Exception as e:
        logger.error(f"Error broadcasting segment creation: {str(e)}")
    
    logger.info(f"New segment created: {new_segment.name} (ID: {new_segment.id})")
    
    return api_success(
        data=new_segment.to_dict(),
        message='Segment created successfully',
        status_code=201
    )

@segments_api_bp.route('/<int:segment_id>', methods=['PUT'])
def update_segment(segment_id):
    """Update an existing segment."""
    from app.utils.api_responses import api_success, api_error
    from app.utils.realtime import broadcast_entity_change, entity_changed
    from app.services.notification_service import NotificationService
    from app.models.notification import NotificationType, NotificationCategory
    import logging
    
    logger = logging.getLogger(__name__)
    
    segment = Segment.query.get_or_404(segment_id)
    data = request.json
    
    if not data:
        return api_error('No update data provided')
    
    # Track changes for notification
    changes_made = []
    
    if data.get('name'):
        old_name = segment.name
        segment.name = data.get('name')
        if old_name != segment.name:
            changes_made.append(f"Name changed from '{old_name}' to '{segment.name}'")
    
    if data.get('description') is not None:
        segment.description = data.get('description')
        changes_made.append("Description updated")
    
    if data.get('criteria') is not None:
        segment.criteria = data.get('criteria')
        changes_made.append("Criteria updated")
    
    db.session.commit()
    
    # Create notification for segment update
    if changes_made:
        try:
            notification_message = f"Segment '{segment.name}' has been updated. " + "; ".join(changes_made[:2])
            
            NotificationService.create_notification(
                title="Segment Updated",
                message=notification_message,
                type=NotificationType.INFO,
                category=NotificationCategory.SEGMENT,
                related_entity_type="segment",
                related_entity_id=segment.id,
                extra_data={'changes': changes_made}
            )
        except Exception as e:
            logger.error(f"Error creating notification for segment update: {str(e)}")
    
    # Broadcast real-time update
    try:
        entity_changed(
            entity_type='segment',
            entity_id=segment.id,
            update_type='updated',
            entity_data=segment.to_dict()
        )
    except Exception as e:
        logger.error(f"Error broadcasting segment update: {str(e)}")
    
    logger.info(f"Segment updated: {segment.name} (ID: {segment.id}). Changes: {', '.join(changes_made[:3])}")
    
    return api_success(
        data=segment.to_dict(),
        message='Segment updated successfully'
    )

@segments_api_bp.route('/<int:segment_id>', methods=['DELETE'])
def delete_segment(segment_id):
    """Delete a segment."""
    from app.utils.api_responses import api_success, api_error
    from app.utils.realtime import broadcast_entity_change, entity_changed
    from app.services.notification_service import NotificationService
    from app.models.notification import NotificationType, NotificationCategory
    import logging
    
    logger = logging.getLogger(__name__)
    
    segment = Segment.query.get_or_404(segment_id)
    
    # Store info before deletion
    segment_name = segment.name
    segment_data = segment.to_dict()
    
    # Delete segment
    db.session.delete(segment)
    db.session.commit()
    
    # Create notification for segment deletion
    try:
        NotificationService.create_notification(
            title="Segment Deleted",
            message=f"Segment '{segment_name}' has been deleted.",
            type=NotificationType.WARNING,
            category=NotificationCategory.SEGMENT,
            related_entity_type="segment",
            related_entity_id=segment_id,
            extra_data={'deleted_segment': segment_data}
        )
    except Exception as e:
        logger.error(f"Error creating notification for segment deletion: {str(e)}")
    
    # Broadcast real-time update
    try:
        entity_changed(
            entity_type='segment',
            entity_id=segment_id,
            update_type='deleted',
            entity_data={'id': segment_id, 'name': segment_name}
        )
    except Exception as e:
        logger.error(f"Error broadcasting segment deletion: {str(e)}")
    
    logger.info(f"Segment deleted: {segment_name} (ID: {segment_id})")
    
    return api_success(
        message='Segment deleted successfully',
        data={'deleted_segment_id': segment_id, 'deleted_segment_name': segment_name}
    )

@segments_api_bp.route('/<int:segment_id>/candidates', methods=['GET'])
def get_segment_candidates(segment_id):
    """Get candidates in a segment."""
    from app.utils.api_responses import api_success
    
    segment = Segment.query.get_or_404(segment_id)
    
    return api_success(
        data=[candidate.to_dict() for candidate in segment.candidates]
    )

@segments_api_bp.route('/run-segmentation', methods=['POST'])
def run_segmentation():
    """Run the segmentation algorithm on all candidates asynchronously."""
    from app.utils.api_responses import api_success, api_error
    from app.tasks.ml_tasks import run_segmentation_task
    from app.models.task import Task
    from app.services.notification_service import NotificationService
    from app.models.notification import NotificationType, NotificationCategory
    from app.utils.realtime import entity_changed
    from flask import url_for
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Check if we have candidates before starting expensive task
        candidate_count = Candidate.query.count()
        
        if candidate_count == 0:
            return api_error('No candidates found for segmentation')
        
        # Get number of clusters from request
        n_clusters = int(request.json.get('n_clusters', 5))
        
        # Start asynchronous task
        task = run_segmentation_task.delay(n_clusters=n_clusters)
        
        # Store task in database for tracking
        task_record = Task.create_task(task.id, 'run_segmentation')
        
        # Create notification for task start
        try:
            NotificationService.create_notification(
                title="Segmentation Task Started",
                message=f"Audience segmentation task started with {n_clusters} clusters and {candidate_count} candidates.",
                type=NotificationType.INFO,
                category=NotificationCategory.SYSTEM,
                related_entity_type="task",
                related_entity_id=task_record.id,
                extra_data={
                    'task_id': task.id,
                    'task_type': 'run_segmentation',
                    'n_clusters': n_clusters,
                    'candidate_count': candidate_count
                }
            )
        except Exception as e:
            logger.error(f"Error creating notification for segmentation task: {str(e)}")
        
        # Broadcast real-time update for task
        try:
            entity_changed(
                entity_type='task',
                entity_id=task_record.id,
                update_type='started',
                entity_data={
                    'id': task_record.id,
                    'task_id': task.id, 
                    'task_type': 'run_segmentation',
                    'status': 'PENDING',
                    'n_clusters': n_clusters,
                    'candidate_count': candidate_count
                }
            )
        except Exception as e:
            logger.error(f"Error broadcasting task start: {str(e)}")
        
        logger.info(f"Segmentation task started. Task ID: {task.id}, Clusters: {n_clusters}, Candidates: {candidate_count}")
        
        # Return task information to client
        return api_success(
            data={
                'task_id': task.id,
                'status': 'PENDING',
                'candidate_count': candidate_count,
                'n_clusters': n_clusters,
                'status_url': url_for('api.get_task_status', task_id=task.id, _external=True)
            },
            message='Segmentation task started successfully',
            status_code=202  # Accepted
        )
    
    except Exception as e:
        logger.error(f"Failed to start segmentation task: {str(e)}")
        return api_error(
            message=f'Failed to start segmentation task: {str(e)}',
            status_code=500
        )

@segments_api_bp.route('/visualization', methods=['GET'])
def get_segmentation_visualization():
    """Generate and return a visualization of the segments asynchronously."""
    from app.utils.api_responses import api_success, api_error
    from app.tasks.ml_tasks import generate_visualization_task
    from app.models.task import Task
    from flask import url_for
    import os
    
    try:
        # Check if visualization already exists and is recent
        visualization_path = 'app/static/images/cluster_visualization.png'
        if os.path.exists(visualization_path):
            # Get file modification time
            mod_time = os.path.getmtime(visualization_path)
            import time
            current_time = time.time()
            
            # If visualization is less than 1 hour old, return it directly
            if current_time - mod_time < 3600:  # 1 hour in seconds
                return api_success(
                    data={'visualization_url': '/static/images/cluster_visualization.png'},
                    message='Using existing visualization'
                )
        
        # Check if we have candidates before starting expensive task
        candidate_count = Candidate.query.count()
        
        if candidate_count == 0:
            return api_error('No candidates found for visualization')
        
        # Start visualization task asynchronously
        task = generate_visualization_task.delay()
        
        # Store task in database for tracking
        task_record = Task.create_task(task.id, 'generate_visualization')
        
        # Return task information
        return api_success(
            data={
                'task_id': task.id,
                'status': 'PENDING',
                'status_url': url_for('api.get_task_status', task_id=task.id, _external=True),
                'candidate_count': candidate_count
            },
            message='Visualization generation started',
            status_code=202  # Accepted
        )
    
    except Exception as e:
        return api_error(
            message=f'Failed to start visualization task: {str(e)}',
            status_code=500
        )

@segments_api_bp.route('/<int:segment_id>/reset_characteristic', methods=['POST'])
def reset_characteristic(segment_id):
    """Reset a segment characteristic to its original ML-generated value."""
    from app.utils.api_responses import api_success, api_error
    
    # Get the segment
    segment = Segment.query.get_or_404(segment_id)
    
    # Get the characteristic to reset
    data = request.json
    if not data or not data.get('characteristic'):
        return api_error('Missing characteristic name')
    
    characteristic = data.get('characteristic')
    
    # Process segment criteria
    if not segment.criteria:
        return api_error('Segment has no criteria to reset')
    
    try:
        # Parse criteria
        if isinstance(segment.criteria, str):
            import json
            criteria_dict = json.loads(segment.criteria)
        else:
            criteria_dict = segment.criteria
        
        # Check if we have original values
        if 'original_values' not in criteria_dict:
            # If we don't have original values, there's nothing to reset to
            return api_error('No original values found for this segment')
        
        # Check if the characteristic exists in the original values
        if characteristic not in criteria_dict['original_values']:
            return api_error(f'Characteristic {characteristic} not found in original values')
        
        # Reset the characteristic
        original_value = criteria_dict['original_values'][characteristic]
        
        # Update the characteristic in the current criteria
        if 'characteristics' in criteria_dict:
            criteria_dict['characteristics'][characteristic] = original_value
        else:
            criteria_dict[characteristic] = original_value
        
        # Save the updated criteria
        segment.criteria = criteria_dict
        db.session.commit()
        
        return api_success(
            data={
                'segment_id': segment_id,
                'characteristic': characteristic,
                'value': original_value
            },
            message=f'Characteristic {characteristic} reset to original value'
        )
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Error resetting characteristic: {str(e)}')

@segments_api_bp.route('/<int:segment_id>/benchmark', methods=['GET'])
def get_segment_benchmark(segment_id):
    """Get benchmark data for a segment."""
    from app.utils.api_responses import api_success, api_error
    from ml.segment_service import segmentation_service
    
    try:
        # Get segment
        segment = Segment.query.get_or_404(segment_id)
        
        # Get benchmark data using segmentation service
        segment_details = segmentation_service.get_segment_details(segment_id)
        
        # Extract benchmark and percentile data
        benchmark_data = segment_details.get('benchmark', {})
        percentiles = segment_details.get('percentiles', {})
        
        return api_success(
            data={
                'segment_id': segment_id,
                'segment_name': segment.name,
                'benchmark': benchmark_data,
                'percentiles': percentiles
            }
        )
        
    except Exception as e:
        return api_error(f'Error getting benchmark data: {str(e)}') 