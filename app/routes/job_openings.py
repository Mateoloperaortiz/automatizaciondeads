from flask import Blueprint, jsonify, request, render_template, current_app
from flask_login import current_user, login_required
from app.models.job_opening import JobOpening
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationCategory
from app.utils.realtime import broadcast_entity_change, entity_changed
from app import db
import logging

job_openings_bp = Blueprint('jobs', __name__, url_prefix='/jobs')
logger = logging.getLogger(__name__)

@job_openings_bp.route('/')
def list_jobs():
    """Get all job openings."""
    jobs = JobOpening.query.filter_by(active=True).all()
    return render_template('jobs/list.html', jobs=jobs)

@job_openings_bp.route('/<int:job_id>')
def get_job(job_id):
    """Get a specific job opening."""
    job = JobOpening.query.get_or_404(job_id)
    
    # Track entity access for analytics if user is authenticated
    if current_user.is_authenticated:
        from app.services.entity_subscription_service import EntitySubscriptionService
        EntitySubscriptionService.track_entity_access(
            entity_type='job_opening',
            entity_id=job_id,
            user_id=current_user.id
        )
        
    return render_template('jobs/detail.html', job=job)

# API routes
@job_openings_bp.route('/api/jobs', methods=['GET'])
def api_list_jobs():
    """API endpoint to get all job openings."""
    jobs = JobOpening.query.filter_by(active=True).all()
    return jsonify({
        'success': True,
        'data': [job.to_dict() for job in jobs]
    })

@job_openings_bp.route('/api/jobs/<int:job_id>', methods=['GET'])
def api_get_job(job_id):
    """API endpoint to get a specific job opening."""
    job = JobOpening.query.get_or_404(job_id)
    return jsonify({
        'success': True,
        'data': job.to_dict()
    })

@job_openings_bp.route('/api/jobs', methods=['POST'])
@login_required
@broadcast_entity_change('job_opening', 
    get_entity_id=lambda resp: resp.get('data', {}).get('id'),
    get_entity_data=lambda resp: resp.get('data', {}))
def api_create_job():
    """API endpoint to create a new job opening."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'company', 'location', 'description', 'job_type']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            'success': False,
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    # Create new job opening
    new_job = JobOpening(
        title=data.get('title'),
        company=data.get('company', 'Default Company'),  # Required field
        location=data.get('location', 'Remote'),  # Required field
        description=data.get('description', ''),  # Required field
        requirements=data.get('requirements'),
        job_type=data.get('job_type', 'Full-time'),  # Required field
        experience_level=data.get('experience_level'),
        salary_range=data.get('salary_range'),
        active=data.get('active', True)
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    # Create notification
    if current_user.is_authenticated:
        NotificationService.create_notification(
            title="Job Opening Created",
            message=f"New job opening created: '{new_job.title}'",
            type=NotificationType.SUCCESS,
            category=NotificationCategory.SYSTEM,
            related_entity_type="job_opening",
            related_entity_id=new_job.id
        )
    
    logger.info(f"New job opening created: {new_job.title} (ID: {new_job.id})")
    
    return jsonify({
        'success': True,
        'message': 'Job opening created successfully',
        'data': new_job.to_dict()
    }), 201

@job_openings_bp.route('/api/jobs/<int:job_id>', methods=['PUT'])
@login_required
@broadcast_entity_change('job_opening')
def api_update_job(job_id):
    """API endpoint to update a job opening."""
    job = JobOpening.query.get_or_404(job_id)
    data = request.get_json()
    
    # Update job opening fields
    if 'title' in data:
        job.title = data['title']
    if 'company' in data:
        job.company = data['company']
    if 'description' in data:
        job.description = data['description']
    if 'location' in data:
        job.location = data['location']
    if 'requirements' in data:
        job.requirements = data['requirements']
    if 'job_type' in data:
        job.job_type = data['job_type']
    if 'experience_level' in data:
        job.experience_level = data['experience_level']
    if 'salary_range' in data:
        job.salary_range = data['salary_range']
    if 'active' in data:
        # Store original status for notification
        original_status = job.active
        new_status = data['active']
        
        # Only create notification if status is actually changing
        if original_status != new_status:
            job.active = new_status
            
            # Create status change notification
            if new_status:
                NotificationService.create_notification(
                    title="Job Opening Activated",
                    message=f"Job opening '{job.title}' has been activated.",
                    type=NotificationType.SUCCESS,
                    category=NotificationCategory.SYSTEM,
                    related_entity_type="job_opening",
                    related_entity_id=job.id
                )
                
                # Manually trigger real-time status change event
                entity_changed(
                    entity_type='job_opening',
                    entity_id=job.id,
                    update_type='status_change',
                    entity_data=job.to_dict()
                )
            else:
                NotificationService.create_notification(
                    title="Job Opening Deactivated",
                    message=f"Job opening '{job.title}' has been deactivated.",
                    type=NotificationType.WARNING,
                    category=NotificationCategory.SYSTEM,
                    related_entity_type="job_opening",
                    related_entity_id=job.id
                )
                
                # Manually trigger real-time status change event
                entity_changed(
                    entity_type='job_opening',
                    entity_id=job.id,
                    update_type='status_change',
                    entity_data=job.to_dict()
                )
        else:
            job.active = new_status  # Set anyway for consistency
        
    db.session.commit()
    
    logger.info(f"Job opening updated: {job.title} (ID: {job.id})")
    
    return jsonify({
        'success': True,
        'message': 'Job opening updated successfully',
        'data': job.to_dict()
    })

@job_openings_bp.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@login_required
@broadcast_entity_change('job_opening', 
    get_entity_id=lambda resp: job_id,
    get_entity_data=lambda resp: {'id': job_id, 'title': resp.get('deleted_job_title', '')})
def api_delete_job(job_id):
    """API endpoint to delete a job opening."""
    job = JobOpening.query.get_or_404(job_id)
    job_title = job.title
    
    # Store job info before deletion
    job_data = job.to_dict()
    
    # Delete job opening
    db.session.delete(job)
    db.session.commit()
    
    # Create notification
    NotificationService.create_notification(
        title="Job Opening Deleted",
        message=f"Job opening '{job_title}' has been deleted.",
        type=NotificationType.WARNING,
        category=NotificationCategory.SYSTEM,
        related_entity_type="job_opening",
        related_entity_id=job_id,
        extra_data={'deleted_job_data': job_data}
    )
    
    logger.info(f"Job opening deleted: {job_title} (ID: {job_id})")
    
    return jsonify({
        'success': True,
        'message': 'Job opening deleted successfully',
        'deleted_job_id': job_id,
        'deleted_job_title': job_title
    })