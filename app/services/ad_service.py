"""
Ad service for managing ads across different social media platforms.

This module has been updated to use the new API Framework instead of the
legacy API service implementations which have been removed.
"""
from app.models.ad_campaign import AdCampaign, SocialMediaPlatform
from app.models.job_opening import JobOpening
from app.models.candidate import Candidate
from app import db
from app.services.campaign_manager import get_campaign_manager
from app.utils.error_handling import (
    with_error_handling, ValidationError, ResourceNotFoundError
)

class AdService:
    """
    Service for managing ads across different social media platforms.
    
    This service delegates to the APIFrameworkCampaignManager for all
    API operations, ensuring consistent implementation across platforms.
    """
    
    def __init__(self):
        """Initialize the ad service using the API Framework."""
        # Get the campaign manager from the factory
        self.campaign_manager = get_campaign_manager()
    
    @with_error_handling
    def create_campaign(self, campaign_data):
        """
        Create a new ad campaign in the database and on the social media platform.
        
        Args:
            campaign_data (dict): Campaign data including job_opening_id, platform_id, etc.
            
        Returns:
            dict: Campaign details including ID and status.
            
        Raises:
            ValidationError: If the campaign data is invalid
            ResourceNotFoundError: If the platform or job opening is not found
        """
        # Validate campaign data
        if not campaign_data.get('title'):
            raise ValidationError("Campaign title is required")
            
        if not campaign_data.get('job_opening_id'):
            raise ValidationError("Job opening ID is required")
            
        if not campaign_data.get('platform_id'):
            raise ValidationError("Platform ID is required")
        
        # Verify job opening exists
        job_opening_id = campaign_data.get('job_opening_id')
        job_opening = db.session.get(JobOpening, job_opening_id)
        if not job_opening:
            raise ResourceNotFoundError(f"Job opening with ID {job_opening_id} not found", "job_opening")
            
        # Create campaign in database
        new_campaign = AdCampaign(
            title=campaign_data.get('title'),
            description=campaign_data.get('description'),
            platform_id=campaign_data.get('platform_id'),
            job_opening_id=job_opening_id,
            segment_id=campaign_data.get('segment_id'),
            budget=campaign_data.get('budget'),
            status='draft',
            ad_content=campaign_data.get('ad_content')
        )
        
        db.session.add(new_campaign)
        db.session.commit()
        
        # Get the platform
        platform = db.session.get(SocialMediaPlatform, campaign_data.get('platform_id'))
        if not platform:
            return {
                'success': True,
                'campaign_id': new_campaign.id,
                'message': 'Campaign created in database, but platform not found for API creation'
            }
            
        # Use the campaign manager to create the campaign on the platform via API Framework
        campaign_manager = get_campaign_manager()
        
        # Prepare the campaign data
        platforms = [platform.name.lower()]
        segment_id = campaign_data.get('segment_id')
        budget = float(campaign_data.get('budget', 1000.0))
        status = campaign_data.get('status', 'PAUSED')
        
        # Create campaign via API framework
        api_result = campaign_manager.create_campaign(
            job_opening_id=new_campaign.job_opening_id,
            platforms=platforms,
            segment_id=segment_id,
            budget=budget,
            status=status,
            ad_content=new_campaign.ad_content or ''
        )
        
        # Update the database record with platform-specific IDs if successful
        platform_result = api_result.get('platforms', {}).get(platform.name.lower(), {})
        if api_result.get('success') and platform_result.get('success'):
            new_campaign.platform_campaign_id = platform_result.get('campaign_id')
            new_campaign.status = status
            db.session.commit()
            
            return {
                'success': True,
                'campaign_id': new_campaign.id,
                'platform_campaign_id': new_campaign.platform_campaign_id,
                'message': 'Campaign created successfully and published to platform'
            }
        
        return {
            'success': True,
            'campaign_id': new_campaign.id,
            'message': 'Campaign created successfully in database'
        }
    
    @with_error_handling
    def publish_campaign(self, campaign_id):
        """
        Publish an ad campaign to the respective social media platform.
        
        Args:
            campaign_id (int): ID of the campaign to publish.
            
        Returns:
            dict: Publication details including status.
            
        Raises:
            ResourceNotFoundError: If campaign, job opening, or platform not found
        """
        # Get campaign from database
        campaign = db.session.get(AdCampaign, campaign_id)
        if not campaign:
            raise ResourceNotFoundError(f"Campaign with ID {campaign_id} not found", "campaign")
        
        # Get job opening
        job_opening = db.session.get(JobOpening, campaign.job_opening_id)
        if not job_opening:
            raise ResourceNotFoundError(f"Job opening with ID {campaign.job_opening_id} not found", "job_opening")
        
        # Get platform
        platform = db.session.get(SocialMediaPlatform, campaign.platform_id)
        if not platform:
            raise ResourceNotFoundError(f"Platform with ID {campaign.platform_id} not found", "platform")
        
        # Create ad content if not provided
        if not campaign.ad_content:
            campaign.ad_content = self._generate_ad_content(job_opening)
        
        # Use the campaign manager to publish the campaign
        # This now uses the new API Framework through the campaign manager
        result = self.campaign_manager.publish_campaign(
            campaign_id=campaign_id,
            platform=platform.name.lower(),
            ad_content=campaign.ad_content
        )
        
        if result.get('success', False):
            # Update campaign status and platform ID
            # Note: Status will be updated to 'active' by the campaign manager
            # but we use lowercase here for consistency with our model
            campaign.status = 'active'  
            campaign.platform_ad_id = result.get('platform_ad_id', '')
            db.session.commit()
        
        return result
    
    # Legacy platform-specific publishing methods have been removed
    # as part of the API Framework migration
    
    # These were replaced by the unified API Framework approach
    # that handles all platforms consistently through the campaign_manager
    
    # The following helper methods are kept because they generate content
    # independent of the API implementation
    
    def _generate_ad_content(self, job_opening):
        """Generate ad content based on the job opening."""
        return f"""
        {job_opening.title} at {job_opening.company}
        
        {job_opening.description[:200]}...
        
        Location: {job_opening.location}
        Type: {job_opening.job_type}
        Experience: {job_opening.experience_level}
        
        Apply now on Magneto365!
        """
    
    def _generate_tweet_text(self, job_opening):
        """Generate a tweet text for the job opening."""
        return f"📢 Job Alert! {job_opening.title} at {job_opening.company} in {job_opening.location}. {job_opening.job_type} position. Apply now: https://www.magneto365.com/job/{job_opening.id} #JobOpening #Hiring #{job_opening.job_type.replace(' ', '')}"
    
    @with_error_handling
    def get_campaign_status(self, campaign_id):
        """
        Get the status of a campaign across all platforms.
        
        Args:
            campaign_id (int): ID of the campaign to check.
            
        Returns:
            dict: Campaign status details.
            
        Raises:
            ResourceNotFoundError: If campaign or platform not found
        """
        # Get campaign from database
        campaign = db.session.get(AdCampaign, campaign_id)
        if not campaign:
            raise ResourceNotFoundError(f"Campaign with ID {campaign_id} not found", "campaign")
        
        # Get platform
        platform = db.session.get(SocialMediaPlatform, campaign.platform_id)
        if not platform:
            raise ResourceNotFoundError(f"Platform with ID {campaign.platform_id} not found", "platform")
        
        # Use the campaign manager to get the campaign status
        if campaign.platform_campaign_id or campaign.platform_ad_id:
            # Delegate to the campaign manager for API calls
            platform_id = campaign.platform_campaign_id or campaign.platform_ad_id
            return self.campaign_manager.get_campaign_stats(
                campaign_id=campaign_id,
                platform=platform.name.lower(),
                platform_campaign_id=platform_id
            )
        
        # If there's no platform ID yet, just return the database status
        return {
            'success': True,
            'platform': platform.name,
            'campaign_title': campaign.title,
            'campaign_status': campaign.status,
            'stats': {}
        }