"""
Publishing API routes using the new API Framework.

This module provides routes for publishing job ads to social media platforms
using the new API Framework.
"""

from flask import Blueprint, jsonify, request, current_app
from app.models.job_opening import JobOpening
from app.models.segment import Segment
from app.models.ad_campaign import AdCampaign
from app import db
import logging
from app.services.campaign_manager import get_campaign_manager
from app.utils.error_handling import (
    handle_api_errors, ValidationError, ResourceNotFoundError, APIError
)

logger = logging.getLogger(__name__)

publish_api_framework_bp = Blueprint('publish_api_framework', __name__, url_prefix='/api')

@publish_api_framework_bp.route('/v2/publish/job/<int:job_id>', methods=['POST'])
@handle_api_errors
def publish_job_ad(job_id):
    """
    Publish a job opening ad to social media platforms using the new API Framework.
    
    Request JSON format:
    {
        "platforms": ["meta", "twitter", "google"],
        "segment_id": 1,  # Optional
        "budget": 1000,   # Optional, in cents
        "status": "PAUSED"  # Optional
    }
    """
    # Validate request data
    data = request.json or {}
    
    # Validate platforms
    platforms = data.get('platforms')
    if not platforms:
        raise ValidationError("Platforms list is required")
        
    # Validate platforms format
    if not isinstance(platforms, list):
        raise ValidationError("Platforms must be a list")
        
    # Validate budget
    budget = data.get('budget', 1000)  # Default $10.00
    try:
        budget = float(budget)
        if budget <= 0:
            raise ValidationError("Budget must be greater than zero")
    except ValueError:
        raise ValidationError("Budget must be a number")
        
    # Validate status
    status = data.get('status', 'PAUSED')  # Default to paused for safety
    if status not in ['ACTIVE', 'PAUSED']:
        raise ValidationError("Status must be 'ACTIVE' or 'PAUSED'")
    
    # Verify job opening exists
    job_opening = db.session.get(JobOpening, job_id)
    if not job_opening:
        raise ResourceNotFoundError(f"Job opening with ID {job_id} not found", "job_opening")
    
    # Verify segment exists if specified
    segment_id = data.get('segment_id')
    if segment_id is not None:
        segment = db.session.get(Segment, segment_id)
        if not segment:
            raise ResourceNotFoundError(f"Segment with ID {segment_id} not found", "segment")
    
    # Get campaign manager (will return the appropriate implementation based on config)
    campaign_manager = get_campaign_manager()
    
    # Create campaign using the manager
    result = campaign_manager.create_campaign(
        job_opening_id=job_id,
        platforms=platforms,
        segment_id=segment_id,
        budget=budget,
        status=status
    )
    
    # Return result
    status_code = 201 if result.get('success', False) else 500
    return jsonify(result), status_code
        
@publish_api_framework_bp.route('/v2/publish/campaigns/<int:campaign_id>/pause', methods=['POST'])
@handle_api_errors
def pause_campaign(campaign_id):
    """
    Pause an active campaign.
    """
    # Verify campaign exists
    campaign = db.session.get(AdCampaign, campaign_id)
    if not campaign:
        raise ResourceNotFoundError(f"Campaign with ID {campaign_id} not found", "campaign")
    
    # Get campaign manager
    campaign_manager = get_campaign_manager()
    
    # Pause campaign
    result = campaign_manager.pause_campaign(campaign_id)
    
    # Return result
    return jsonify(result), 200
        
@publish_api_framework_bp.route('/v2/publish/campaigns/<int:campaign_id>/resume', methods=['POST'])
@handle_api_errors
def resume_campaign(campaign_id):
    """
    Resume a paused campaign.
    """
    # Verify campaign exists
    campaign = db.session.get(AdCampaign, campaign_id)
    if not campaign:
        raise ResourceNotFoundError(f"Campaign with ID {campaign_id} not found", "campaign")
    
    # Get campaign manager
    campaign_manager = get_campaign_manager()
    
    # Resume campaign
    result = campaign_manager.resume_campaign(campaign_id)
    
    # Return result
    return jsonify(result), 200
        
@publish_api_framework_bp.route('/v2/publish/campaigns/<int:campaign_id>/stats', methods=['GET'])
@handle_api_errors
def get_campaign_stats(campaign_id):
    """
    Get metrics for a campaign.
    """
    # Verify campaign exists
    campaign = db.session.get(AdCampaign, campaign_id)
    if not campaign:
        raise ResourceNotFoundError(f"Campaign with ID {campaign_id} not found", "campaign")
        
    # This will be implemented in the future when we have the CampaignManager.get_campaign_stats method
    raise APIError("This endpoint is not yet implemented", 501)
    
@publish_api_framework_bp.route('/publish', methods=['POST'])
@handle_api_errors
def publish_ad():
    """
    Backward compatible endpoint for the old /api/publish route.
    This allows existing clients to continue working while we migrate to the new API framework.
    
    Request JSON format:
    {
        "job_opening_id": 1,
        "platforms": ["meta", "twitter", "google"],
        "target_segment_id": 1,  # Optional
        "budget": 1000,   # Optional, in cents
        "ad_content": "Apply now for our exciting job opening!"
    }
    """
    data = request.json or {}
    
    if 'job_opening_id' not in data:
        raise ValidationError("job_opening_id is required")
        
    job_id = data.get('job_opening_id')
    
    # Verify job opening exists
    job_opening = db.session.get(JobOpening, job_id)
    if not job_opening:
        raise ResourceNotFoundError(f"Job opening with ID {job_id} not found", "job_opening")
    
    # Get other parameters with validation
    platforms = data.get('platforms', ['meta'])
    if not isinstance(platforms, list):
        raise ValidationError("platforms must be a list")
        
    segment_id = data.get('target_segment_id')
    if segment_id is not None:
        segment = db.session.get(Segment, segment_id)
        if not segment:
            raise ResourceNotFoundError(f"Segment with ID {segment_id} not found", "segment")
    
    budget = data.get('budget', 1000)
    try:
        budget = float(budget)
        if budget <= 0:
            raise ValidationError("Budget must be greater than zero")
    except ValueError:
        raise ValidationError("Budget must be a number")
        
    status = 'PAUSED'  # Always start paused for safety
    
    # Get campaign manager through the factory
    campaign_manager = get_campaign_manager()
    
    # Create campaign using the manager
    result = campaign_manager.create_campaign(
        job_opening_id=job_id,
        platforms=platforms,
        segment_id=segment_id,
        budget=budget,
        status=status,
        ad_content=data.get('ad_content', '')
    )
    
    return jsonify(result), 201