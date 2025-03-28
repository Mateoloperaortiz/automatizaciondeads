"""
Refactored campaign manager using the API Integration Framework.

This module provides a unified interface for managing ad campaigns across different
social media platforms, leveraging the new API framework's standardized approach.
"""

import time
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, cast

from app.api_framework.base import APIRequest, APIResponse
from app.api_framework.meta_client import MetaAPIClient
from app.api_framework.twitter_client import TwitterAPIClient
from app.api_framework.google_client import GoogleAPIClient
from app.models.ad_campaign import AdCampaign
from app.models.job_opening import JobOpening
from app.models.segment import Segment
from app.models.candidate import Candidate
from app.utils.credentials import credential_manager
from app.utils.error_handling import (
    APIError, ValidationError, ResourceNotFoundError, 
    with_error_handling, log_and_raise
)
from app import db

# Configure logging
logger = logging.getLogger(__name__)


class APIFrameworkCampaignManager:
    """
    Campaign manager that uses the API Integration Framework.
    
    This class provides a unified interface for creating and managing ad campaigns
    across multiple social media platforms, leveraging the standardized API framework.
    """
    
    def __init__(self):
        """Initialize platform-specific API clients."""
        # Initialize clients with credentials from credential manager
        self.meta_client = MetaAPIClient(credential_manager.get_credentials('META'))
        self.twitter_client = TwitterAPIClient(credential_manager.get_credentials('TWITTER'))
        self.google_client = GoogleAPIClient(credential_manager.get_credentials('GOOGLE'))
        
        # Map platform names to clients
        self.platform_clients = {
            'meta': self.meta_client,
            'facebook': self.meta_client,  # Alias
            'instagram': self.meta_client,  # Alias
            'google': self.google_client,
            'twitter': self.twitter_client,
            'x': self.twitter_client  # Alias
        }
        
    @with_error_handling
    def create_campaign(self, job_opening_id: int, platforms: List[str], 
                       segment_id: Optional[int] = None, budget: float = 1000.0,
                       status: str = 'PAUSED', ad_content: str = '') -> Dict[str, Union[bool, Dict]]:
        """
        Create an ad campaign across multiple platforms.
        
        Args:
            job_opening_id: ID of the job opening to advertise
            platforms: List of platform names to create campaigns on
            segment_id: ID of the audience segment to target
            budget: Daily budget per platform in account currency
            status: Initial campaign status ('ACTIVE', 'PAUSED')
            ad_content: Optional ad content
            
        Returns:
            Dictionary with results for each platform
            
        Raises:
            ValidationError: If parameters are invalid
            ResourceNotFoundError: If job opening or segment not found
            APIError: For other API errors
        """
        # Validate inputs
        if not platforms:
            raise ValidationError("At least one platform must be specified")
            
        if budget <= 0:
            raise ValidationError("Budget must be greater than zero")
            
        if status not in ['ACTIVE', 'PAUSED']:
            raise ValidationError("Status must be 'ACTIVE' or 'PAUSED'")
        
        # Get job opening
        job_opening = db.session.get(JobOpening, job_opening_id)
        if not job_opening:
            raise ResourceNotFoundError(f"Job opening with ID {job_opening_id} not found", "job_opening")
        
        # Get segment if specified
        segment = None
        if segment_id:
            segment = db.session.get(Segment, segment_id)
            if not segment:
                raise ResourceNotFoundError(f"Segment with ID {segment_id} not found", "segment")
        
        results: Dict[str, Union[bool, Dict[str, Any]]] = {
            'success': False,
            'platforms': {}
        }
        
        for platform in platforms:
            try:
                client = self.platform_clients.get(platform.lower())
                if not client:
                    results['platforms'][platform] = cast(Dict[str, Union[bool, str]], {
                        'success': False,
                        'error': f'Platform {platform} not supported'
                    })
                    continue
                
                if not client.is_initialized:
                    results['platforms'][platform] = cast(Dict[str, Union[bool, str]], {
                        'success': False,
                        'error': f'Client for {platform} is not initialized'
                    })
                    continue
                
                # Create campaign request for the platform
                if platform.lower() in ['meta', 'facebook', 'instagram']:
                    result = self._create_meta_campaign(client, job_opening, segment, budget, status)
                elif platform.lower() == 'google':
                    result = self._create_google_campaign(client, job_opening, segment, budget, status)
                else:  # Twitter/X
                    result = self._create_twitter_campaign(client, job_opening, segment, budget, status)
                
                if result.success:
                    # Create campaign record in database
                    campaign = AdCampaign(
                        job_opening_id=job_opening_id,
                        platform=platform.lower(),
                        platform_campaign_id=result.data['campaign_id'],
                        name=f"{job_opening.title} - {platform}",
                        status=status,
                        daily_budget=budget,
                        segment_id=segment_id if segment else None,
                        ad_content=ad_content
                    )
                    db.session.add(campaign)
                    db.session.commit()
                    
                    # Update result with database ID
                    result_dict: Dict[str, Any] = {
                        'success': True,
                        'campaign_id': result.data['campaign_id'],
                        'campaign_db_id': campaign.id
                    }
                    
                    # Add additional platform-specific details
                    result_dict.update({
                        k: v for k, v in result.data.items() 
                        if k not in ['success', 'campaign_id']
                    })
                    
                    results['platforms'][platform] = result_dict
                    
                    # Set overall success if at least one platform succeeds
                    results['success'] = True
                    
                    # Create notification for successful campaign creation
                    from app.services.notification_service import NotificationService
                    from app.models.notification import NotificationType, NotificationCategory
                    
                    NotificationService.create_notification(
                        title="Campaign Created",
                        message=f"Campaign for {job_opening.title} has been created on {platform.title()}.",
                        type=NotificationType.SUCCESS,
                        category=NotificationCategory.CAMPAIGN,
                        related_entity_type="campaign",
                        related_entity_id=campaign.id,
                        extra_data={
                            'platform': platform,
                            'job_title': job_opening.title,
                            'job_id': job_opening.id,
                            'status': status,
                            'segment_id': segment_id
                        }
                    )
                    
                else:
                    # Copy error from API Response
                    results['platforms'][platform] = cast(Dict[str, Union[bool, str]], {
                        'success': False,
                        'error': result.error
                    })
                    
                    # Create notification for failed campaign creation
                    from app.services.notification_service import NotificationService
                    from app.models.notification import NotificationType, NotificationCategory
                    
                    NotificationService.create_notification(
                        title="Campaign Creation Failed",
                        message=f"Failed to create campaign for '{job_opening.title}' on {platform.title()}.",
                        type=NotificationType.ERROR,
                        category=NotificationCategory.CAMPAIGN,
                        related_entity_type="job_opening",
                        related_entity_id=job_opening.id,
                        extra_data={
                            'platform': platform,
                            'error': result.error,
                            'segment_id': segment_id
                        }
                    )
                
            except Exception as e:
                logger.exception(f"Error creating campaign for platform {platform}")
                results['platforms'][platform] = cast(Dict[str, Union[bool, str]], {
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _create_meta_campaign(self, client: MetaAPIClient, job_opening: JobOpening, 
                            segment: Optional[Segment], budget: float, 
                            status: str) -> APIResponse:
        """
        Create a campaign on Meta platforms.
        
        Args:
            client: Meta API client
            job_opening: Job opening to advertise
            segment: Audience segment to target (optional)
            budget: Daily budget in account currency
            status: Campaign status ('ACTIVE', 'PAUSED')
            
        Returns:
            API response with campaign details
        """
        # Create campaign request
        campaign_request = client.create_campaign_request(
            name=f"{job_opening.title} - Meta",
            objective='REACH',
            status=status
        )
        
        # Execute campaign creation request
        campaign_response = client.execute_request(campaign_request)
        
        if not campaign_response.success:
            return campaign_response
        
        # Create targeting based on segment
        targeting = {
            'age_min': 18,
            'age_max': 65,
            'genders': [1, 2],  # Both men and women
            'geo_locations': {'countries': ['US']},
            'interests': [{'id': '6003139266461', 'name': 'Job hunting'}]
        }
        
        if segment:
            # Adjust targeting based on segment data
            targeting.update(self._get_meta_targeting_from_segment(segment))
        
        # Create ad set request
        ad_set_request = client.create_ad_set_request(
            campaign_id=campaign_response.data['campaign_id'],
            name=f"AdSet for {job_opening.title}",
            targeting=targeting,
            budget=budget,
            bid_amount=500  # $5.00 bid
        )
        
        # Execute ad set creation request
        ad_set_response = client.execute_request(ad_set_request)
        
        if not ad_set_response.success:
            return ad_set_response
        
        # Combine the results
        return APIResponse(
            request_id=campaign_response.request_id,
            success=True,
            status_code=200,
            data={
                'success': True,
                'campaign_id': campaign_response.data['campaign_id'],
                'ad_set_id': ad_set_response.data['ad_set_id'],
                'name': campaign_response.data['name'],
                'status': campaign_response.data['status']
            }
        )
    
    def _create_google_campaign(self, client: GoogleAPIClient, job_opening: JobOpening,
                              segment: Optional[Segment], budget: float,
                              status: str) -> APIResponse:
        """
        Create a campaign on Google Ads.
        
        Args:
            client: Google API client
            job_opening: Job opening to advertise
            segment: Audience segment to target (optional)
            budget: Daily budget in account currency
            status: Campaign status ('ACTIVE', 'PAUSED')
            
        Returns:
            API response with campaign details
        """
        # Create campaign request
        campaign_request = client.create_campaign_request(
            name=f"{job_opening.title} - Google",
            budget=budget,
            status=status
        )
        
        # Execute campaign creation request
        campaign_response = client.execute_request(campaign_request)
        
        if not campaign_response.success:
            return campaign_response
        
        # Create ad group request
        ad_group_request = client.create_ad_group_request(
            campaign_id=campaign_response.data['campaign_id'],
            name=f"AdGroup for {job_opening.title}",
            status=status
        )
        
        # Execute ad group creation request
        ad_group_response = client.execute_request(ad_group_request)
        
        if not ad_group_response.success:
            return ad_group_response
        
        # Create location targeting
        locations = ['US']  # Default to US
        if segment:
            # Get locations from segment
            locations = self._get_google_locations_from_segment(segment)
        
        location_request = client.create_location_targeting_request(
            campaign_id=campaign_response.data['campaign_id'],
            locations=locations
        )
        
        location_response = client.execute_request(location_request)
        
        # Create demographic targeting if segment exists
        if segment:
            demographic_request = client.create_demographic_targeting_request(
                ad_group_id=ad_group_response.data['ad_group_id'],
                criteria=self._get_google_demographics_from_segment(segment)
            )
            
            demographic_response = client.execute_request(demographic_request)
        
        # Create responsive search ad
        ad_request = client.create_responsive_search_ad_request(
            ad_group_id=ad_group_response.data['ad_group_id'],
            headlines=[
                job_opening.title,
                f"Join {job_opening.company}",
                "Apply Now",
                "Career Opportunity",
                "Job Opening"
            ],
            descriptions=[
                job_opening.description[:90] if job_opening.description else "Great career opportunity",
                f"Work at {job_opening.company}",
                "Apply today and start your new career"
            ],
            final_url=job_opening.application_url,
            status=status
        )
        
        ad_response = client.execute_request(ad_request)
        
        # Combine the results
        return APIResponse(
            request_id=campaign_response.request_id,
            success=True,
            status_code=200,
            data={
                'success': True,
                'campaign_id': campaign_response.data['campaign_id'],
                'ad_group_id': ad_group_response.data['ad_group_id'],
                'ad_id': ad_response.data['ad_id'] if ad_response.success else None,
                'name': campaign_response.data['name'],
                'status': campaign_response.data['status']
            }
        )
    
    def _create_twitter_campaign(self, client: TwitterAPIClient, job_opening: JobOpening,
                               segment: Optional[Segment], budget: float,
                               status: str) -> APIResponse:
        """
        Create a campaign on Twitter/X.
        
        Args:
            client: Twitter API client
            job_opening: Job opening to advertise
            segment: Audience segment to target (optional)
            budget: Daily budget in account currency
            status: Campaign status ('ACTIVE', 'PAUSED')
            
        Returns:
            API response with campaign details
        """
        # Create initial tweet
        tweet_text = f"🚀 New Job Opening: {job_opening.title}\n\n" \
                    f"Join {job_opening.company} - {job_opening.location}\n\n" \
                    f"Apply now: {job_opening.application_url}"
        
        tweet_request = client.post_tweet_request(tweet_text)
        tweet_response = client.execute_request(tweet_request)
        
        if not tweet_response.success:
            return tweet_response
        
        # Create campaign
        campaign_request = client.create_campaign_request(
            name=f"{job_opening.title} - X",
            funding_instrument_id="test_funding",  # Would be real in production
            daily_budget=budget,
            start_time=time.strftime('%Y-%m-%dT%H:%M:%S-05:00')  # Current time
        )
        
        campaign_response = client.execute_request(campaign_request)
        
        if not campaign_response.success:
            return campaign_response
        
        # Create line item with targeting
        line_item_request = client.create_line_item_request(
            campaign_id=campaign_response.data['campaign_id'],
            name=f"LineItem for {job_opening.title}",
            targeting=self._get_twitter_targeting_from_segment(segment) if segment else None,
            bid_amount=500  # $5.00 bid
        )
        
        line_item_response = client.execute_request(line_item_request)
        
        if not line_item_response.success:
            return line_item_response
        
        # Create promoted tweet
        promoted_request = client.create_promoted_tweet_request(
            campaign_id=campaign_response.data['campaign_id'],
            tweet_id=tweet_response.data['tweet_id'],
            line_item_id=line_item_response.data['line_item_id']
        )
        
        promoted_response = client.execute_request(promoted_request)
        
        # Combine the results
        return APIResponse(
            request_id=campaign_response.request_id,
            success=True,
            status_code=200,
            data={
                'success': True,
                'campaign_id': campaign_response.data['campaign_id'],
                'tweet_id': tweet_response.data['tweet_id'],
                'line_item_id': line_item_response.data['line_item_id'],
                'name': campaign_response.data['name'],
                'status': 'PAUSED'  # Twitter doesn't return status in simulation
            }
        )
    
    def _get_meta_targeting_from_segment(self, segment: Segment) -> Dict[str, Any]:
        """
        Convert segment data to Meta targeting format.
        
        Args:
            segment: Audience segment with targeting criteria
            
        Returns:
            Dictionary with Meta targeting parameters
        """
        targeting = {}
        if segment.criteria:
            if 'age_range' in segment.criteria:
                targeting['age_min'] = max(18, segment.criteria['age_range'][0])
                targeting['age_max'] = min(65, segment.criteria['age_range'][1])
            
            if 'location' in segment.criteria:
                targeting['geo_locations'] = {
                    'cities': [{'key': loc} for loc in segment.criteria['location'][:5]]
                }
            
            if 'interests' in segment.criteria:
                targeting['interests'] = [
                    {'id': f"interest_{i}", 'name': interest}
                    for i, interest in enumerate(segment.criteria['interests'][:10])
                ]
        
        return targeting
    
    def _get_google_locations_from_segment(self, segment: Segment) -> List[str]:
        """
        Convert segment location data to Google Ads format.
        
        Args:
            segment: Audience segment with targeting criteria
            
        Returns:
            List of location strings for Google Ads
        """
        locations = ['US']  # Default
        if segment.criteria and 'location' in segment.criteria:
            locations = segment.criteria['location'][:5]  # Limit to 5 locations
        return locations
    
    def _get_google_demographics_from_segment(self, segment: Segment) -> Dict[str, Any]:
        """
        Convert segment data to Google Ads demographic targeting.
        
        Args:
            segment: Audience segment with targeting criteria
            
        Returns:
            Dictionary with Google demographic targeting parameters
        """
        demographics = {
            'age_ranges': ['18-24', '25-34', '35-44', '45-54', '55-64'],
            'genders': ['MALE', 'FEMALE']
        }
        
        if segment.criteria:
            if 'age_range' in segment.criteria:
                min_age, max_age = segment.criteria['age_range']
                demographics['age_ranges'] = [
                    range_str for range_str in demographics['age_ranges']
                    if any(age in range(min_age, max_age + 1) 
                          for age in map(int, range_str.replace('+', '-').split('-')))
                ]
        
        return demographics
    
    def _get_twitter_targeting_from_segment(self, segment: Segment) -> Dict[str, Any]:
        """
        Convert segment data to Twitter targeting criteria.
        
        Args:
            segment: Audience segment with targeting criteria
            
        Returns:
            Dictionary with Twitter targeting parameters
        """
        targeting = {
            'locations': ['US'],
            'age_ranges': ['18-24', '25-34', '35-44', '45-54', '55-64'],
            'gender': ['male', 'female']
        }
        
        if segment and segment.criteria:
            if 'location' in segment.criteria:
                targeting['locations'] = segment.criteria['location'][:5]
            
            if 'age_range' in segment.criteria:
                min_age, max_age = segment.criteria['age_range']
                targeting['age_ranges'] = [
                    range_str for range_str in targeting['age_ranges']
                    if any(age in range(min_age, max_age + 1) 
                          for age in map(int, range_str.replace('+', '-').split('-')))
                ]
            
            if 'interests' in segment.criteria:
                targeting['interests'] = segment.criteria['interests'][:10]
            
            if 'keywords' in segment.criteria:
                targeting['keywords'] = segment.criteria['keywords'][:20]
        
        return targeting
    
    def update_campaign_status(self, campaign_id: int, status: str) -> Dict[str, Union[bool, str, int, Any]]:
        """
        Update a campaign's status.
        
        Args:
            campaign_id: Database ID of the campaign
            status: New status ('ACTIVE', 'PAUSED')
            
        Returns:
            Dictionary with operation result
        """
        # Get campaign from database
        campaign = AdCampaign.query.get(campaign_id)
        if not campaign:
            return {'success': False, 'error': 'Campaign not found'}
        
        # Get client for platform
        platform_name = getattr(campaign, 'platform', None)
        if isinstance(platform_name, str):
            client = self.platform_clients.get(platform_name.lower())
        else:
            # Handle case where platform is a relationship to SocialMediaPlatform object
            platform_obj = getattr(campaign, 'platform', None)
            if platform_obj and hasattr(platform_obj, 'name'):
                client = self.platform_clients.get(platform_obj.name.lower())
            else:
                client = None
                
        if not client:
            platform_display = getattr(campaign, 'platform', 'Unknown')
            if not isinstance(platform_display, str):
                platform_display = getattr(platform_display, 'name', 'Unknown')
            return {'success': False, 'error': f'Platform {platform_display} not supported'}
        
        # Store original status for notification
        original_status = campaign.status
        
        # Create status update request based on platform
        platform_name = getattr(campaign, 'platform', None)
        if isinstance(platform_name, str):
            platform_str = platform_name.lower()
        else:
            # Handle case where platform is a relationship to SocialMediaPlatform object
            platform_obj = getattr(campaign, 'platform', None)
            platform_str = platform_obj.name.lower() if platform_obj and hasattr(platform_obj, 'name') else ''
            
        if platform_str in ['meta', 'facebook', 'instagram']:
            request = self.meta_client.create_status_update_request(
                campaign_id=campaign.platform_campaign_id,
                status=status
            )
        elif platform_str == 'google':
            request = self.google_client.update_campaign_status_request(
                campaign_id=campaign.platform_campaign_id,
                status=status
            )
        else:  # Twitter/X
            request = self.twitter_client.update_campaign_status_request(
                campaign_id=campaign.platform_campaign_id,
                status=status
            )
        
        # Execute the request
        response = client.execute_request(request)
        
        if response.success:
            # Update database record
            campaign.status = status
            db.session.commit()
            
            # Create notification for status change
            from app.services.notification_service import NotificationService
            from app.models.notification import NotificationType, NotificationCategory
            
            # Get job opening for notification
            job_opening = None
            if campaign.job_opening_id:
                from app.models.job_opening import JobOpening
                job_opening = JobOpening.query.get(campaign.job_opening_id)
            
            # Get platform display string
            platform_display = platform_str.title()
            
            # Create different notifications based on status change
            if status == 'ACTIVE':
                NotificationService.create_notification(
                    title="Campaign Activated",
                    message=f"Campaign '{campaign.title}' is now active on {platform_display}.",
                    type=NotificationType.SUCCESS,
                    category=NotificationCategory.CAMPAIGN,
                    related_entity_type="campaign",
                    related_entity_id=campaign.id,
                    extra_data={
                        'platform': platform_str,
                        'job_title': job_opening.title if job_opening else None,
                        'previous_status': original_status
                    }
                )
            elif status == 'PAUSED':
                NotificationService.create_notification(
                    title="Campaign Paused",
                    message=f"Campaign '{campaign.title}' has been paused on {platform_display}.",
                    type=NotificationType.INFO,
                    category=NotificationCategory.CAMPAIGN,
                    related_entity_type="campaign",
                    related_entity_id=campaign.id,
                    extra_data={
                        'platform': platform_str,
                        'job_title': job_opening.title if job_opening else None,
                        'previous_status': original_status
                    }
                )
            
            return cast(Dict[str, Union[bool, str, int, Any]], {
                'success': True,
                'campaign_id': campaign_id,
                'status': status,
                'platform': platform_str
            })
        else:
            # Create error notification
            from app.services.notification_service import NotificationService
            from app.models.notification import NotificationType, NotificationCategory
            
            # Get platform display string
            platform_display = platform_str.title()
            
            NotificationService.create_notification(
                title="Campaign Status Update Failed",
                message=f"Failed to update status for campaign '{campaign.title}' on {platform_display}.",
                type=NotificationType.ERROR,
                category=NotificationCategory.CAMPAIGN,
                related_entity_type="campaign",
                related_entity_id=campaign.id,
                extra_data={
                    'platform': platform_str,
                    'error': response.error,
                    'requested_status': status,
                    'current_status': original_status
                }
            )
            
            return cast(Dict[str, Union[bool, str, int, Any]], {
                'success': False,
                'error': response.error,
                'campaign_id': campaign_id,
                'platform': platform_str
            })
    
    def pause_campaign(self, campaign_id: int) -> Dict[str, Union[bool, str, int, Any]]:
        """
        Pause an active campaign.
        
        Args:
            campaign_id: Database ID of the campaign
            
        Returns:
            Dictionary with operation result
        """
        return self.update_campaign_status(campaign_id, 'PAUSED')
        
    def resume_campaign(self, campaign_id: int) -> Dict[str, Union[bool, str, int, Any]]:
        """
        Resume a paused campaign.
        
        Args:
            campaign_id: Database ID of the campaign
            
        Returns:
            Dictionary with operation result
        """
        return self.update_campaign_status(campaign_id, 'ACTIVE')
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all platforms.
        
        Returns:
            Dictionary with metrics for each platform
        """
        metrics: Dict[str, Dict[str, Any]] = {}
        
        # Get metrics from each client's metrics tracking
        for platform, client in self.platform_clients.items():
            if client.metrics and platform not in metrics:  # Avoid duplicates
                metrics[platform] = client.metrics.get_summary()
        
        return metrics
    
    def publish_campaign(self, campaign_id: int, platform: str, ad_content: str) -> Dict[str, Union[bool, str, int, Dict[str, Any]]]:
        """
        Publish an existing campaign to social media platform.
        
        This method takes a campaign that exists in the database and publishes it to
        the specified social media platform using the appropriate API client.
        
        Args:
            campaign_id: Database ID of the campaign to publish
            platform: Name of the platform to publish to
            ad_content: Text content for the ad
            
        Returns:
            Dictionary with publication results
        """
        # Get campaign from database
        from app.models.ad_campaign import AdCampaign
        from app.models.job_opening import JobOpening
        
        campaign = AdCampaign.query.get(campaign_id)
        if not campaign:
            return cast(Dict[str, Union[bool, str]], {
                'success': False,
                'error': f'Campaign with ID {campaign_id} not found'
            })
            
        # Get job opening for the campaign
        job_opening = JobOpening.query.get(campaign.job_opening_id)
        if not job_opening:
            return cast(Dict[str, Union[bool, str]], {
                'success': False,
                'error': f'Job opening with ID {campaign.job_opening_id} not found'
            })
            
        # Get client for platform
        client = self.platform_clients.get(platform.lower())
        if not client:
            return cast(Dict[str, Union[bool, str]], {
                'success': False,
                'error': f'Platform {platform} not supported'
            })
            
        # Check if client is initialized
        if not client.is_initialized:
            return cast(Dict[str, Union[bool, str]], {
                'success': False,
                'error': f'Client for {platform} is not initialized'
            })
            
        try:
            # Different implementation depending on platform
            if platform.lower() in ['meta', 'facebook', 'instagram']:
                result = self._publish_to_meta(client, campaign, job_opening, ad_content)
            elif platform.lower() == 'google':
                result = self._publish_to_google(client, campaign, job_opening, ad_content)
            else:  # Twitter/X
                result = self._publish_to_twitter(client, campaign, job_opening, ad_content)
                
            # Update campaign status in the database if successful
            if result.success:
                campaign.status = 'ACTIVE'
                campaign.platform_campaign_id = result.data.get('campaign_id', '')
                campaign.platform_ad_id = result.data.get('ad_id', '')
                db.session.commit()
                
                return cast(Dict[str, Union[bool, str, int]], {
                    'success': True,
                    'campaign_id': campaign_id,
                    'platform_campaign_id': campaign.platform_campaign_id,
                    'platform_ad_id': campaign.platform_ad_id,
                    'platform': platform,
                    'status': 'active'
                })
            else:
                return cast(Dict[str, Union[bool, str, int]], {
                    'success': False,
                    'error': result.error,
                    'campaign_id': campaign_id,
                    'platform': platform
                })
                
        except Exception as e:
            return cast(Dict[str, Union[bool, str, int]], {
                'success': False,
                'error': str(e),
                'campaign_id': campaign_id,
                'platform': platform
            })
    
    def _publish_to_meta(self, client, campaign, job_opening, ad_content) -> APIResponse:
        """
        Publish a campaign to Meta platforms.
        
        Args:
            client: Meta API client
            campaign: Campaign database object
            job_opening: Job opening database object
            ad_content: Ad content text
            
        Returns:
            API response with publication details
        """
        # Create a creative for the ad
        creative_request = client.create_ad_creative_request(
            name=f"Creative for {job_opening.title}",
            body=ad_content,
            object_story_spec={
                'page_id': client.page_id,
                'link_data': {
                    'message': ad_content,
                    'link': job_opening.application_url,
                    'name': job_opening.title,
                    'description': job_opening.description[:200] if job_opening.description else ''
                }
            }
        )
        creative_response = client.execute_request(creative_request)
        
        if not creative_response.success:
            return creative_response
            
        # Create ad using the creative
        ad_request = client.create_ad_request(
            ad_set_id=campaign.platform_campaign_id,  # This typically would be the ad set ID
            name=f"Ad for {job_opening.title}",
            creative_id=creative_response.data['creative_id'],
            status='ACTIVE'
        )
        ad_response = client.execute_request(ad_request)
        
        # Return combined result
        if ad_response.success:
            return APIResponse(
                request_id=ad_response.request_id,
                success=True,
                status_code=200,
                data={
                    'campaign_id': campaign.platform_campaign_id,
                    'creative_id': creative_response.data['creative_id'],
                    'ad_id': ad_response.data['ad_id']
                }
            )
        else:
            return ad_response
            
    def _publish_to_google(self, client, campaign, job_opening, ad_content) -> APIResponse:
        """
        Publish a campaign to Google Ads.
        
        Args:
            client: Google API client
            campaign: Campaign database object
            job_opening: Job opening database object
            ad_content: Ad content text
            
        Returns:
            API response with publication details
        """
        # Create ad group if not already present
        ad_group_request = client.create_ad_group_request(
            campaign_id=campaign.platform_campaign_id,
            name=f"Ad Group for {job_opening.title}",
            status='ENABLED'
        )
        ad_group_response = client.execute_request(ad_group_request)
        
        if not ad_group_response.success:
            return ad_group_response
            
        # Split ad content into headlines and descriptions
        lines = ad_content.strip().split('\n')
        headlines = lines[:3]  # First 3 lines as headlines
        
        # Ensure we have enough headlines
        while len(headlines) < 3:
            headlines.append(job_opening.title)
            
        descriptions = lines[3:5] if len(lines) > 3 else [job_opening.description[:90] if job_opening.description else '']
        
        # Create responsive search ad
        ad_request = client.create_responsive_search_ad_request(
            ad_group_id=ad_group_response.data['ad_group_id'],
            headlines=headlines,
            descriptions=descriptions,
            final_url=job_opening.application_url,
            status='ENABLED'
        )
        ad_response = client.execute_request(ad_request)
        
        # Return combined result
        if ad_response.success:
            return APIResponse(
                request_id=ad_response.request_id,
                success=True,
                status_code=200,
                data={
                    'campaign_id': campaign.platform_campaign_id,
                    'ad_group_id': ad_group_response.data['ad_group_id'],
                    'ad_id': ad_response.data['ad_id']
                }
            )
        else:
            return ad_response
            
    def _publish_to_twitter(self, client, campaign, job_opening, ad_content) -> APIResponse:
        """
        Publish a campaign to Twitter/X.
        
        Args:
            client: Twitter API client
            campaign: Campaign database object
            job_opening: Job opening database object
            ad_content: Ad content text
            
        Returns:
            API response with publication details
        """
        # Format the tweet text
        tweet_text = f"🚀 {job_opening.title} at {job_opening.company} - {job_opening.location}\n\n"
        
        # Add shortened version of ad content
        ad_lines = ad_content.strip().split('\n')
        if ad_lines:
            tweet_text += f"{ad_lines[0]}\n\n" if ad_lines[0] else ""
            
        # Add application URL
        tweet_text += f"Apply now: {job_opening.application_url}"
        
        # Ensure tweet doesn't exceed 280 characters
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
            
        # Post the tweet
        tweet_request = client.post_tweet_request(tweet_text)
        tweet_response = client.execute_request(tweet_request)
        
        if not tweet_response.success:
            return tweet_response
            
        # Promote the tweet
        promote_request = client.create_promoted_tweet_request(
            campaign_id=campaign.platform_campaign_id,
            tweet_id=tweet_response.data['tweet_id'],
            line_item_id=campaign.platform_ad_id if campaign.platform_ad_id else None
        )
        promote_response = client.execute_request(promote_request)
        
        # Return combined result
        if promote_response.success:
            return APIResponse(
                request_id=promote_response.request_id,
                success=True,
                status_code=200,
                data={
                    'campaign_id': campaign.platform_campaign_id,
                    'tweet_id': tweet_response.data['tweet_id'],
                    'ad_id': tweet_response.data['tweet_id']  # Use tweet ID as ad ID
                }
            )
        else:
            return promote_response
    
    def get_campaign_stats(self, campaign_id: int, platform: str = None, platform_campaign_id: str = None) -> Dict[str, Union[bool, str, int, Dict[str, Any]]]:
        """
        Get statistics for a campaign.
        
        Args:
            campaign_id: Database ID of the campaign
            platform: Optional platform name (if already known)
            platform_campaign_id: Optional platform-specific campaign ID
            
        Returns:
            Dictionary with campaign statistics
        """
        # Get campaign from database
        campaign = AdCampaign.query.get(campaign_id)
        if not campaign:
            return {'success': False, 'error': 'Campaign not found'}
        
        # Get platform name
        platform_name = getattr(campaign, 'platform', None)
        if isinstance(platform_name, str):
            platform_str = platform_name.lower()
        else:
            # Handle case where platform is a relationship to SocialMediaPlatform object
            platform_obj = getattr(campaign, 'platform', None)
            platform_str = platform_obj.name.lower() if platform_obj and hasattr(platform_obj, 'name') else ''
            
        # Get client for platform
        client = self.platform_clients.get(platform_str)
        if not client:
            return {'success': False, 'error': f'Platform {platform_str} not supported'}
        
        # Create stats request based on platform
        if platform_str in ['meta', 'facebook', 'instagram']:
            request = self.meta_client.get_campaign_stats_request(
                campaign_id=campaign.platform_campaign_id
            )
        elif platform_str == 'google':
            request = self.google_client.get_campaign_stats_request(
                campaign_id=campaign.platform_campaign_id
            )
        else:  # Twitter/X
            request = self.twitter_client.get_campaign_stats_request(
                campaign_id=campaign.platform_campaign_id
            )
        
        # Execute the request
        response = client.execute_request(request)
        
        if response.success:
            return cast(Dict[str, Union[bool, str, int, Dict[str, Any]]], {
                'success': True,
                'campaign_id': campaign_id,
                'platform': platform_str,
                'stats': response.data['stats']
            })
        else:
            return cast(Dict[str, Union[bool, str, int, Dict[str, Any]]], {
                'success': False,
                'error': response.error,
                'campaign_id': campaign_id,
                'platform': platform_str
            })
    
    def clear_caches(self) -> Dict[str, Union[bool, str]]:
        """
        Clear all caches for all clients.
        
        Returns:
            Status message
        """
        for platform, client in self.platform_clients.items():
            if client.cache:
                client.clear_cache()
                
        return cast(Dict[str, Union[bool, str]], {
            'success': True,
            'message': 'All API caches cleared'
        })