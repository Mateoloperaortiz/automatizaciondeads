from flask import Blueprint, jsonify, request, current_app
from app.models.job_opening import JobOpening
from app.models.segment import Segment
from app.models.ad_campaign import AdCampaign
from app import db
from app.api import get_api
import logging

logger = logging.getLogger(__name__)

publish_bp = Blueprint('publish', __name__, url_prefix='/api/publish')

@publish_bp.route('/job/<int:job_id>', methods=['POST'])
def publish_job_ad(job_id):
    """Publish a job opening ad to social media platforms.
    
    Request JSON format:
    {
        "platforms": ["meta", "twitter", "google"],
        "segment_id": 1,  # Optional
        "budget": 1000,   # Optional, in cents
        "status": "PAUSED"  # Optional
    }
    """
    # Get job opening
    job_opening = JobOpening.query.get_or_404(job_id)
    
    # Get request data
    data = request.json or {}
    platforms = data.get('platforms', ['meta'])  # Default to Meta
    segment_id = data.get('segment_id')
    budget = data.get('budget', 1000)  # Default $10.00
    status = data.get('status', 'PAUSED')  # Default to paused for safety
    
    # Get segment if specified
    segment = None
    if segment_id:
        segment = Segment.query.get(segment_id)
    
    # Initialize results
    results = {
        'job_opening_id': job_id,
        'platforms': {},
        'success': False
    }
    
    # Publish to each platform
    for platform in platforms:
        try:
            # Get API for platform
            api = get_api(platform)
            
            # Publish ad
            result = api.publish_job_ad(
                job_opening=job_opening,
                segment=segment,
                budget=budget,
                status=status
            )
            
            if result:
                # Create ad campaign record
                campaign = AdCampaign(
                    job_opening_id=job_id,
                    platform=platform,
                    platform_campaign_id=result['campaign']['id'],
                    name=result['campaign']['name'],
                    status=status,
                    daily_budget=budget,
                    targeting=result['ad_set'].get('targeting') if 'ad_set' in result else None
                )
                
                db.session.add(campaign)
                db.session.commit()
                
                # Update results
                results['platforms'][platform] = {
                    'success': True,
                    'campaign_id': campaign.id,
                    'platform_campaign_id': result['campaign']['id']
                }
                results['success'] = True
            else:
                results['platforms'][platform] = {
                    'success': False,
                    'error': f"Failed to publish ad on {platform}"
                }
        
        except Exception as e:
            logger.error(f"Error publishing to {platform}: {str(e)}")
            results['platforms'][platform] = {
                'success': False,
                'error': str(e)
            }
    
    # Return results
    if results['success']:
        return jsonify(results), 200
    else:
        return jsonify(results), 500

@publish_bp.route('/status/<int:campaign_id>', methods=['GET'])
def get_campaign_status(campaign_id):
    """Get the status of a campaign."""
    # Get campaign
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    try:
        # Get API for platform
        api = get_api(campaign.platform)
        
        # Get campaign status
        result = api.get_campaign(campaign.platform_campaign_id)
        
        if result:
            # Update campaign status
            campaign.status = result['status']
            db.session.commit()
            
            return jsonify({
                'campaign_id': campaign.id,
                'platform': campaign.platform,
                'status': campaign.status,
                'details': result
            }), 200
        else:
            return jsonify({
                'error': f"Failed to get campaign status from {campaign.platform}"
            }), 500
    
    except Exception as e:
        logger.error(f"Error getting campaign status: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@publish_bp.route('/update/<int:campaign_id>', methods=['PUT'])
def update_campaign_status(campaign_id):
    """Update the status of a campaign.
    
    Request JSON format:
    {
        "status": "ACTIVE"  # or "PAUSED"
    }
    """
    # Get campaign
    campaign = AdCampaign.query.get_or_404(campaign_id)
    
    # Get request data
    data = request.json or {}
    status = data.get('status')
    
    if not status:
        return jsonify({
            'error': 'Missing status parameter'
        }), 400
    
    try:
        # Get API for platform
        api = get_api(campaign.platform)
        
        # Update campaign status
        # This is a simplified version - actual implementation would depend on the platform's API
        # For now, we just update the database record
        campaign.status = status
        db.session.commit()
        
        return jsonify({
            'campaign_id': campaign.id,
            'platform': campaign.platform,
            'status': campaign.status
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating campaign status: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500 