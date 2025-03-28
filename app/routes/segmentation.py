"""
Routes for audience segmentation functionality.

This module provides API endpoints for managing audience segments,
including segment creation, retrieval, and assignment.
"""

from flask import Blueprint, jsonify, request, current_app
from app.services.campaign_manager import get_campaign_manager
from app.models.segment import Segment
from app.models.candidate import Candidate
from app import db
import os
import sys

# Create blueprint
segmentation_bp = Blueprint('segmentation', __name__, url_prefix='/api/segmentation')

# Initialize campaign manager for segment operations
campaign_manager = get_campaign_manager()

@segmentation_bp.route('/segments', methods=['GET'])
def get_segments():
    """Get all audience segments."""
    try:
        segments = Segment.query.all()
        
        return jsonify({
            'success': True,
            'segments': [{
                'id': segment.id,
                'name': segment.name,
                'description': segment.description,
                'segment_code': segment.segment_code,
                'size': len(segment.candidate_ids) if segment.candidate_ids else 0,
            } for segment in segments]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving segments: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve segments'
        }), 500

@segmentation_bp.route('/segments/<int:segment_id>', methods=['GET'])
def get_segment(segment_id):
    """Get details for a specific audience segment."""
    try:
        result = campaign_manager.get_segment_details(segment_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving segment {segment_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve segment {segment_id}'
        }), 500

@segmentation_bp.route('/segments/create', methods=['POST'])
def create_segments():
    """Create or update audience segments using machine learning clustering."""
    try:
        # This is a long-running operation
        result = campaign_manager.create_audience_segments()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        current_app.logger.error(f"Error creating segments: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create segments'
        }), 500

@segmentation_bp.route('/candidate/<int:candidate_id>/segment', methods=['GET'])
def assign_segment(candidate_id):
    """Determine the segment for a specific candidate."""
    try:
        # Check if candidate exists
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return jsonify({
                'success': False,
                'error': f'Candidate {candidate_id} not found'
            }), 404
        
        # Assign segment
        result = campaign_manager.assign_segment_to_candidate(candidate_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        current_app.logger.error(f"Error assigning segment to candidate {candidate_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to assign segment to candidate {candidate_id}'
        }), 500

@segmentation_bp.route('/segments/<int:segment_id>/candidates', methods=['GET'])
def get_segment_candidates(segment_id):
    """Get candidates in a specific segment."""
    try:
        segment = Segment.query.get(segment_id)
        if not segment:
            return jsonify({
                'success': False,
                'error': f'Segment {segment_id} not found'
            }), 404
        
        candidates = []
        if segment.candidate_ids:
            # Limit to first 50 candidates for performance
            candidate_limit = min(50, len(segment.candidate_ids))
            candidate_objs = Candidate.query.filter(
                Candidate.id.in_(segment.candidate_ids[:candidate_limit])
            ).all()
            
            for candidate in candidate_objs:
                candidates.append({
                    'id': candidate.id,
                    'name': candidate.name,
                    'location': candidate.location,
                    'education_level': candidate.education_level,
                    'years_experience': candidate.years_experience,
                    'skills': candidate.skills
                })
        
        return jsonify({
            'success': True,
            'segment_id': segment_id,
            'segment_name': segment.name,
            'total_candidates': len(segment.candidate_ids) if segment.candidate_ids else 0,
            'candidates': candidates
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving candidates for segment {segment_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve candidates for segment {segment_id}'
        }), 500

@segmentation_bp.route('/train', methods=['POST'])
def train_model():
    """Train or retrain the audience segmentation model."""
    try:
        # Add project root to path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        if project_root not in sys.path:
            sys.path.append(project_root)
        
        # Run training script
        from ml.train_model import main as train_model_main
        train_model_main()
        
        return jsonify({
            'success': True,
            'message': 'Segmentation model trained successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error training segmentation model: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to train segmentation model: {str(e)}'
        }), 500
