"""
Meta API integration for publishing job ads on Facebook and Instagram.
"""
import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights

class MetaAPIService:
    """Service for interacting with Meta (Facebook) Ads API."""
    
    def __init__(self):
        """Initialize the Meta API service."""
        self.app_id = os.environ.get('META_APP_ID')
        self.app_secret = os.environ.get('META_APP_SECRET')
        self.access_token = os.environ.get('META_ACCESS_TOKEN')
        self.ad_account_id = os.environ.get('META_AD_ACCOUNT_ID')
        self.is_initialized = False
        
        # Initialize the API if credentials are available
        if self.app_id and self.app_secret and self.access_token:
            self._init_api()
    
    def _init_api(self):
        """Initialize the Facebook Ads API."""
        try:
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.is_initialized = True
        except Exception as e:
            print(f"Error initializing Meta API: {str(e)}")
            self.is_initialized = False
    
    def create_campaign(self, name, objective='REACH', status='PAUSED', special_ad_categories=None):
        """
        Create a new ad campaign.
        
        Args:
            name (str): Campaign name.
            objective (str): Campaign objective (e.g., 'REACH', 'BRAND_AWARENESS').
            status (str): Campaign status ('ACTIVE', 'PAUSED').
            special_ad_categories (list): Special ad categories if applicable.
            
        Returns:
            dict: Campaign details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            account = AdAccount(self.ad_account_id)
            
            params = {
                'name': name,
                'objective': objective,
                'status': status,
            }
            
            if special_ad_categories:
                params['special_ad_categories'] = special_ad_categories
            
            # Create the campaign in test mode
            params['special_ad_category'] = 'EMPLOYMENT'
            
            campaign = account.create_campaign(
                params=params,
                fields=['id', 'name', 'objective', 'status']
            )
            
            return {
                'success': True,
                'campaign_id': campaign['id'],
                'name': campaign['name'],
                'status': campaign['status']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_ad_set(self, campaign_id, name, targeting, budget, bid_amount, billing_event='IMPRESSIONS', status='PAUSED'):
        """
        Create a new ad set within a campaign.
        
        Args:
            campaign_id (str): ID of the campaign to add the ad set to.
            name (str): Ad set name.
            targeting (dict): Targeting specifications.
            budget (float): Daily budget in account currency.
            bid_amount (int): Bid amount in cents.
            billing_event (str): Billing event type ('IMPRESSIONS', 'LINK_CLICKS').
            status (str): Ad set status ('ACTIVE', 'PAUSED').
            
        Returns:
            dict: Ad set details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            account = AdAccount(self.ad_account_id)
            
            params = {
                'name': name,
                'campaign_id': campaign_id,
                'daily_budget': int(budget * 100),  # Convert to cents
                'billing_event': billing_event,
                'optimization_goal': 'REACH',
                'bid_amount': bid_amount,
                'targeting': targeting,
                'status': status
            }
            
            ad_set = account.create_ad_set(
                params=params,
                fields=['id', 'name', 'status', 'daily_budget']
            )
            
            return {
                'success': True,
                'ad_set_id': ad_set['id'],
                'name': ad_set['name'],
                'status': ad_set['status'],
                'daily_budget': ad_set['daily_budget']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_ad(self, ad_set_id, name, creative_id, status='PAUSED'):
        """
        Create a new ad within an ad set.
        
        Args:
            ad_set_id (str): ID of the ad set to add the ad to.
            name (str): Ad name.
            creative_id (str): ID of the creative to use for the ad.
            status (str): Ad status ('ACTIVE', 'PAUSED').
            
        Returns:
            dict: Ad details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            account = AdAccount(self.ad_account_id)
            
            params = {
                'name': name,
                'adset_id': ad_set_id,
                'creative': {'creative_id': creative_id},
                'status': status
            }
            
            ad = account.create_ad(
                params=params,
                fields=['id', 'name', 'status']
            )
            
            return {
                'success': True,
                'ad_id': ad['id'],
                'name': ad['name'],
                'status': ad['status']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_campaign_stats(self, campaign_id):
        """
        Get statistics for a campaign.
        
        Args:
            campaign_id (str): ID of the campaign to get stats for.
            
        Returns:
            dict: Campaign statistics.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            campaign = Campaign(campaign_id)
            insights = campaign.get_insights(
                fields=[
                    'impressions',
                    'clicks',
                    'spend',
                    'reach',
                    'cpc',
                    'cpm'
                ]
            )
            
            if insights:
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'stats': insights[0]
                }
            else:
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'stats': {}
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)} 