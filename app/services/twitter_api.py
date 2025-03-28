"""
Twitter (X) API integration for publishing job ads on X platform.
"""
import os
import tweepy

class TwitterAPIService:
    """Service for interacting with Twitter (X) API for ads."""
    
    def __init__(self):
        """Initialize the Twitter API service."""
        self.consumer_key = os.environ.get('X_API_KEY')
        self.consumer_secret = os.environ.get('X_API_SECRET')
        self.access_token = os.environ.get('X_ACCESS_TOKEN')
        self.access_token_secret = os.environ.get('X_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.environ.get('X_BEARER_TOKEN')
        self.api = None
        self.client = None
        self.is_initialized = False
        
        # Initialize the API if credentials are available
        if self.consumer_key and self.consumer_secret and self.access_token and self.access_token_secret:
            self._init_api()
    
    def _init_api(self):
        """Initialize the Twitter API."""
        try:
            # Set up auth & api handlers for the v1.1 API used by the Ads features
            auth = tweepy.OAuth1UserHandler(
                self.consumer_key, 
                self.consumer_secret,
                self.access_token, 
                self.access_token_secret
            )
            self.api = tweepy.API(auth)
            
            # Set up v2 API client for newer features
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            
            self.is_initialized = True
        except Exception as e:
            print(f"Error initializing Twitter API: {str(e)}")
            self.is_initialized = False
    
    def post_tweet(self, text, media_ids=None):
        """
        Post a tweet, optionally with media.
        
        Args:
            text (str): Tweet text.
            media_ids (list): List of media IDs to attach to the tweet.
            
        Returns:
            dict: Tweet details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            # Using v2 API via client
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids
            )
            
            tweet_id = response.data['id']
            
            return {
                'success': True,
                'tweet_id': tweet_id,
                'text': text
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_media(self, media_path, media_type=None):
        """
        Upload media to Twitter.
        
        Args:
            media_path (str): Path to the media file.
            media_type (str): Media type (IMAGE, VIDEO, GIF).
            
        Returns:
            dict: Media details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            # Using v1.1 API for media upload
            media = self.api.media_upload(media_path)
            media_id = media.media_id_string
            
            return {
                'success': True,
                'media_id': media_id,
                'media_path': media_path
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_campaign(self, name, funding_instrument_id, daily_budget, start_time, end_time=None):
        """
        Create a new ad campaign.
        
        Args:
            name (str): Campaign name.
            funding_instrument_id (str): Funding instrument ID.
            daily_budget (float): Daily budget in account currency.
            start_time (str): Campaign start time (ISO format).
            end_time (str): Campaign end time (ISO format), optional.
            
        Returns:
            dict: Campaign details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            # Simplified implementation for proof of concept
            # In a real implementation, you'd use the Twitter Ads API
            
            # Simulate a successful campaign creation
            campaign_id = f"test_campaign_{name.replace(' ', '_').lower()}"
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'name': name,
                'daily_budget': daily_budget,
                'start_time': start_time,
                'end_time': end_time
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_promoted_tweet(self, campaign_id, tweet_id, line_item_id):
        """
        Create a promoted tweet within a campaign.
        
        Args:
            campaign_id (str): ID of the campaign.
            tweet_id (str): ID of the tweet to promote.
            line_item_id (str): ID of the line item.
            
        Returns:
            dict: Promoted tweet details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            # Simplified implementation for proof of concept
            
            # Simulate a successful promoted tweet creation
            promoted_tweet_id = f"test_promoted_tweet_{tweet_id}"
            
            return {
                'success': True,
                'promoted_tweet_id': promoted_tweet_id,
                'campaign_id': campaign_id,
                'tweet_id': tweet_id,
                'line_item_id': line_item_id
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
            # Simplified implementation for proof of concept
            
            # Simulate campaign statistics
            stats = {
                'impressions': 5000,
                'engagements': 200,
                'clicks': 100,
                'retweets': 10,
                'likes': 30,
                'spend': 50.00  # Daily spend in account currency
            }
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'stats': stats
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_line_item(self, campaign_id, name, product_type='PROMOTED_TWEETS',
                        placements=None, targeting=None, bid_amount=None):
        """
        Create a line item within a campaign.
        
        Args:
            campaign_id (str): ID of the campaign.
            name (str): Line item name.
            product_type (str): Product type (default: PROMOTED_TWEETS).
            placements (list): List of placement objects.
            targeting (dict): Targeting criteria.
            bid_amount (float): Bid amount in account currency.
            
        Returns:
            dict: Line item details including ID.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            # Simplified implementation for proof of concept
            line_item_id = f"test_line_item_{name.replace(' ', '_').lower()}"
            
            return {
                'success': True,
                'line_item_id': line_item_id,
                'campaign_id': campaign_id,
                'name': name,
                'product_type': product_type,
                'targeting': targeting,
                'bid_amount': bid_amount
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_targeting_criteria(self, line_item_id, criteria):
        """
        Create targeting criteria for a line item.
        
        Args:
            line_item_id (str): ID of the line item.
            criteria (dict): Targeting criteria including:
                - locations
                - interests
                - keywords
                - demographics
                - devices
                
        Returns:
            dict: Targeting criteria details.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            # Simplified implementation for proof of concept
            targeting_id = f"test_targeting_{line_item_id}"
            
            return {
                'success': True,
                'targeting_id': targeting_id,
                'line_item_id': line_item_id,
                'criteria': criteria
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_campaign_status(self, campaign_id, status):
        """
        Update the status of a campaign.
        
        Args:
            campaign_id (str): ID of the campaign.
            status (str): New status (ACTIVE, PAUSED, DELETED).
            
        Returns:
            dict: Updated campaign details.
        """
        if not self.is_initialized:
            return {'success': False, 'error': 'API not initialized'}
        
        try:
            # Simplified implementation for proof of concept
            return {
                'success': True,
                'campaign_id': campaign_id,
                'status': status,
                'updated_at': '2025-03-25T10:27:54-05:00'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}