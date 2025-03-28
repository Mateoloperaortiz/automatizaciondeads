from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetaAPI:
    """Class for interacting with Meta (Facebook) Ads API."""
    
    def __init__(self):
        """Initialize Meta API with credentials."""
        self.app_id = os.environ.get('FACEBOOK_APP_ID')
        self.app_secret = os.environ.get('FACEBOOK_APP_SECRET')
        self.access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
        self.ad_account_id = os.environ.get('FACEBOOK_AD_ACCOUNT_ID')
        
        # Initialize the API
        if all([self.app_id, self.app_secret, self.access_token]):
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.ad_account = AdAccount(f'act_{self.ad_account_id}')
            self.initialized = True
        else:
            logger.error("Meta API credentials missing")
            self.initialized = False
    
    def create_campaign(self, name, objective='LEAD_GENERATION', status='PAUSED', daily_budget=1000):
        """Create a new campaign.
        
        Args:
            name (str): Campaign name
            objective (str): Campaign objective (LINK_CLICKS, LEAD_GENERATION, etc.)
            status (str): Campaign status (ACTIVE, PAUSED)
            daily_budget (int): Daily budget in cents (1000 = $10.00)
        
        Returns:
            dict: Campaign details
        """
        if not self.initialized:
            logger.error("Meta API not initialized")
            return None
        
        try:
            fields = [
                'id',
                'name',
                'objective',
                'status',
                'created_time'
            ]
            
            params = {
                'name': name,
                'objective': objective,
                'status': status,
                'special_ad_categories': [],
                'daily_budget': daily_budget
            }
            
            campaign = self.ad_account.create_campaign(
                fields=fields,
                params=params,
            )
            
            return {
                'id': campaign['id'],
                'name': campaign['name'],
                'objective': campaign['objective'],
                'status': campaign['status'],
                'created_time': campaign['created_time'],
                'platform': 'meta'
            }
        
        except Exception as e:
            logger.error(f"Error creating Meta campaign: {str(e)}")
            return None
    
    def create_ad_set(self, campaign_id, name, targeting, bid_amount=500, status='PAUSED'):
        """Create a new ad set.
        
        Args:
            campaign_id (str): Campaign ID
            name (str): Ad set name
            targeting (dict): Targeting specifications
            bid_amount (int): Bid amount in cents
            status (str): Ad set status (ACTIVE, PAUSED)
        
        Returns:
            dict: Ad set details
        """
        if not self.initialized:
            logger.error("Meta API not initialized")
            return None
        
        try:
            fields = [
                'id',
                'name',
                'campaign_id',
                'status',
                'targeting',
                'created_time'
            ]
            
            start_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
            
            params = {
                'name': name,
                'campaign_id': campaign_id,
                'status': status,
                'bid_amount': bid_amount,
                'billing_event': 'IMPRESSIONS',
                'optimization_goal': 'LINK_CLICKS',
                'targeting': targeting,
                'start_time': start_time
            }
            
            ad_set = self.ad_account.create_ad_set(
                fields=fields,
                params=params,
            )
            
            return {
                'id': ad_set['id'],
                'name': ad_set['name'],
                'campaign_id': ad_set['campaign_id'],
                'status': ad_set['status'],
                'targeting': ad_set['targeting'],
                'created_time': ad_set['created_time'],
                'platform': 'meta'
            }
        
        except Exception as e:
            logger.error(f"Error creating Meta ad set: {str(e)}")
            return None
    
    def create_ad(self, ad_set_id, name, creative, status='PAUSED'):
        """Create a new ad.
        
        Args:
            ad_set_id (str): Ad set ID
            name (str): Ad name
            creative (dict): Creative specifications
            status (str): Ad status (ACTIVE, PAUSED)
        
        Returns:
            dict: Ad details
        """
        if not self.initialized:
            logger.error("Meta API not initialized")
            return None
        
        try:
            fields = [
                'id',
                'name',
                'adset_id',
                'status',
                'created_time'
            ]
            
            params = {
                'name': name,
                'adset_id': ad_set_id,
                'status': status,
                'creative': creative
            }
            
            ad = self.ad_account.create_ad(
                fields=fields,
                params=params,
            )
            
            return {
                'id': ad['id'],
                'name': ad['name'],
                'adset_id': ad['adset_id'],
                'status': ad['status'],
                'created_time': ad['created_time'],
                'platform': 'meta'
            }
        
        except Exception as e:
            logger.error(f"Error creating Meta ad: {str(e)}")
            return None
    
    def get_campaign(self, campaign_id):
        """Get campaign details.
        
        Args:
            campaign_id (str): Campaign ID
        
        Returns:
            dict: Campaign details
        """
        if not self.initialized:
            logger.error("Meta API not initialized")
            return None
        
        try:
            fields = [
                'id',
                'name',
                'objective',
                'status',
                'created_time'
            ]
            
            campaign = Campaign(campaign_id).api_get(
                fields=fields
            )
            
            return {
                'id': campaign['id'],
                'name': campaign['name'],
                'objective': campaign['objective'],
                'status': campaign['status'],
                'created_time': campaign['created_time'],
                'platform': 'meta'
            }
        
        except Exception as e:
            logger.error(f"Error getting Meta campaign: {str(e)}")
            return None
    
    def get_ad_insights(self, ad_id):
        """Get ad insights.
        
        Args:
            ad_id (str): Ad ID
        
        Returns:
            dict: Ad insights
        """
        if not self.initialized:
            logger.error("Meta API not initialized")
            return None
        
        try:
            fields = [
                'impressions',
                'clicks',
                'spend',
                'cpc',
                'ctr',
                'reach',
                'frequency'
            ]
            
            params = {
                'date_preset': 'last_30_days'
            }
            
            insights = Ad(ad_id).get_insights(
                fields=fields,
                params=params
            )
            
            if insights:
                return insights[0]
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting Meta ad insights: {str(e)}")
            return None
    
    def publish_job_ad(self, job_opening, segment=None, budget=1000, status='PAUSED'):
        """Publish a job opening ad.
        
        Args:
            job_opening (JobOpening): Job opening model instance
            segment (Segment, optional): Target segment. Defaults to None.
            budget (int, optional): Daily budget in cents. Defaults to 1000.
            status (str, optional): Campaign status. Defaults to 'PAUSED'.
        
        Returns:
            dict: Published ad details
        """
        if not self.initialized:
            logger.error("Meta API not initialized")
            return None
        
        try:
            # Create campaign
            campaign_name = f"Job: {job_opening.title} at {job_opening.company}"
            campaign = self.create_campaign(
                name=campaign_name,
                objective='LEAD_GENERATION',
                status=status,
                daily_budget=budget
            )
            
            if not campaign:
                logger.error(f"Failed to create Meta campaign for job {job_opening.id}")
                return None
            
            # Define targeting based on segment or default
            targeting = {
                'geo_locations': {
                    'countries': ['CO'],  # Colombia
                    'cities': [
                        {'key': '2257835', 'name': 'Bogotá', 'region': 'Bogota D.C.', 'country': 'CO'}
                    ]
                },
                'age_min': 18,
                'age_max': 65,
                'facebook_positions': ['feed', 'instagram_feed'],
                'device_platforms': ['mobile', 'desktop']
            }
            
            if segment:
                # Add segment specific targeting
                if segment.criteria and 'age_range' in segment.criteria:
                    targeting['age_min'] = segment.criteria['age_range']['min']
                    targeting['age_max'] = segment.criteria['age_range']['max']
            
            # Create ad set
            ad_set_name = f"AdSet: {job_opening.title}"
            ad_set = self.create_ad_set(
                campaign_id=campaign['id'],
                name=ad_set_name,
                targeting=targeting,
                status=status
            )
            
            if not ad_set:
                logger.error(f"Failed to create Meta ad set for job {job_opening.id}")
                return None
            
            # Create ad creative
            creative = {
                'title': job_opening.title,
                'body': f"Join {job_opening.company} as a {job_opening.title} in {job_opening.location}. {job_opening.description[:100]}...",
                'link_url': f"https://www.magneto365.com/job/{job_opening.id}",
                'image_url': 'https://www.magneto365.com/static/images/logo.png'  # Default image
            }
            
            # Create ad
            ad_name = f"Ad: {job_opening.title}"
            ad = self.create_ad(
                ad_set_id=ad_set['id'],
                name=ad_name,
                creative=creative,
                status=status
            )
            
            if not ad:
                logger.error(f"Failed to create Meta ad for job {job_opening.id}")
                return None
            
            return {
                'platform': 'meta',
                'campaign': campaign,
                'ad_set': ad_set,
                'ad': ad,
                'job_opening_id': job_opening.id
            }
        
        except Exception as e:
            logger.error(f"Error publishing Meta job ad: {str(e)}")
            return None 