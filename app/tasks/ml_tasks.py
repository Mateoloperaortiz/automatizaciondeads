"""
Asynchronous ML tasks for background processing.

This module contains Celery tasks for handling ML operations like
segmentation and model training that are too resource-intensive
to run synchronously during HTTP requests.
"""
import os
import sys
import pandas as pd
import logging
from celery import shared_task
import json
from datetime import datetime

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import ML modules
from ml.segmentation import AudienceSegmentation
from app.utils.celery_config import celery
from app import create_app, db
from app.models.segment import Segment, candidate_segments
from app.models.candidate import Candidate

# Configure logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, name='run_segmentation')
def run_segmentation_task(self, n_clusters=5, task_id=None):
    """
    Run segmentation algorithm asynchronously.
    
    Args:
        n_clusters: Number of clusters to create
        task_id: Optional task ID for tracking
        
    Returns:
        dict: Task result information
    """
    task_id = task_id or self.request.id
    
    # Create app context for database operations
    app = create_app()
    
    with app.app_context():
        try:
            # Log start of processing
            logger.info(f"Starting segmentation task {task_id} with {n_clusters} clusters")
            
            # Get all candidates
            candidates = Candidate.query.all()
            
            if not candidates:
                logger.warning("No candidates found for segmentation")
                return {
                    'success': False,
                    'message': 'No candidates found for segmentation',
                    'task_id': task_id
                }
            
            # Convert to dataframe
            candidates_data = []
            for candidate in candidates:
                candidates_data.append(candidate.to_dict())
                
            df = pd.DataFrame(candidates_data)
            
            # Log progress
            logger.info(f"Processing {len(df)} candidates")
            
            # Initialize segmentation model
            segmentation = AudienceSegmentation(n_clusters=n_clusters)
            
            # Train model
            segmentation.train(df)
            
            # Get cluster assignments
            cluster_labels = segmentation.model.labels_
            
            # Save model
            segmentation.save_model()
            
            # Clear existing segments
            db.session.query(candidate_segments).delete()
            db.session.query(Segment).delete()
            db.session.commit()
            
            # Create segments based on clusters
            segments = []
            for i in range(segmentation.n_clusters):
                # Analyze cluster to generate description
                cluster_indices = [idx for idx, label in enumerate(cluster_labels) if label == i]
                cluster_size = len(cluster_indices)
                
                # Extract sample data for description
                description = "Empty segment with no candidates."
                if cluster_indices:
                    cluster_df = df.iloc[cluster_indices]
                    avg_age = cluster_df['age'].mean() if 'age' in cluster_df else 0
                    avg_exp = cluster_df['years_of_experience'].mean() if 'years_of_experience' in cluster_df else 0
                    
                    description = f"Age: Average {avg_age:.1f} years. Experience: Average {avg_exp:.1f} years."
                    
                    if len(cluster_indices) > 10:
                        description += f" This is a {'large' if cluster_size > 30 else 'medium-sized'} segment with {cluster_size} candidates."
                    else:
                        description += f" This is a small segment with only {cluster_size} candidates."
                
                # Create segment
                segment = Segment(
                    name=f"Segment {i+1}",
                    segment_code=f"CLUSTER_{i}",
                    description=description,
                    criteria={
                        "cluster_id": i,
                        "algorithm": "KMeans",
                        "parameters": {
                            "n_clusters": segmentation.n_clusters,
                            "random_state": segmentation.random_state
                        }
                    }
                )
                db.session.add(segment)
                segments.append(segment)
            
            db.session.commit()
            
            # Process batch associations for improved performance
            logger.info("Assigning candidates to segments")
            
            # Map candidate IDs to cluster labels
            candidate_clusters = {}
            for i, candidate in enumerate(candidates):
                if i < len(cluster_labels):
                    candidate_clusters[candidate.id] = int(cluster_labels[i])
            
            # Use bulk operations to assign candidates to segments
            for candidate_id, cluster_id in candidate_clusters.items():
                if 0 <= cluster_id < len(segments):
                    segment = segments[cluster_id]
                    
                    # Store candidate ID in segment's candidate_ids field
                    if segment._candidate_ids is None:
                        segment._candidate_ids = []
                    segment._candidate_ids.append(candidate_id)
                    
                    # Create association record
                    db.session.execute(
                        candidate_segments.insert().values(
                            candidate_id=candidate_id,
                            segment_id=segment.id
                        )
                    )
            
            # Commit changes
            db.session.commit()
            
            # Log completion
            logger.info(f"Segmentation completed successfully: {len(segments)} segments created")
            
            # Create result object to return
            result = {
                'success': True,
                'message': 'Segmentation completed successfully',
                'task_id': task_id,
                'segments_count': len(segments),
                'segments': [{'id': s.id, 'name': s.name, 'count': len(s._candidate_ids or [])} for s in segments],
                'completed_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in segmentation task: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'Segmentation failed: {str(e)}',
                'task_id': task_id
            }

@shared_task(bind=True, name='generate_visualization')
def generate_visualization_task(self, task_id=None):
    """
    Generate segmentation visualization asynchronously.
    
    Args:
        task_id: Optional task ID for tracking
        
    Returns:
        dict: Task result with visualization URL
    """
    task_id = task_id or self.request.id
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Log start
            logger.info(f"Starting visualization generation task {task_id}")
            
            # Get all candidates
            candidates = Candidate.query.all()
            
            if not candidates:
                return {
                    'success': False,
                    'message': 'No candidates found for visualization',
                    'task_id': task_id
                }
            
            # Convert to dataframe
            df = pd.DataFrame([candidate.to_dict() for candidate in candidates])
            
            # Load the model
            segmentation = AudienceSegmentation()
            model_loaded = segmentation.load_model()
            
            if not model_loaded:
                return {
                    'success': False,
                    'message': 'Unable to load segmentation model',
                    'task_id': task_id
                }
            
            # Generate visualization
            visualization_path = 'app/static/images/cluster_visualization.png'
            os.makedirs(os.path.dirname(visualization_path), exist_ok=True)
            
            segmentation.visualize_clusters(df, save_path=visualization_path)
            
            # Log completion
            logger.info(f"Visualization generated successfully at {visualization_path}")
            
            # Return result
            return {
                'success': True,
                'message': 'Visualization generated successfully',
                'task_id': task_id,
                'visualization_url': '/static/images/cluster_visualization.png',
                'completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in visualization task: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'Visualization failed: {str(e)}',
                'task_id': task_id
            }