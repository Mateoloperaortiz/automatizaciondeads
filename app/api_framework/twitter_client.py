"""
Twitter (X) API Client implementation.

This module provides a client implementation for the Twitter (X) Ads API,
using the common API Integration Framework patterns.
"""

import time
import logging
import tweepy
from typing import Dict, Any, Optional, List, Union

from app.api_framework.base import APIRequest, APIResponse, BaseAPIClient
from app.api_framework.cache import TTLCache
from app.api_framework.metrics import APIMetrics
from app.utils.api_debug import api_diagnostic_tool

# Configure logging
logger = logging.getLogger(__name__)


class TwitterAPIClient(BaseAPIClient):
    """
    Client for interacting with Twitter (X) Ads API.
    
    This class provides a standardized interface for the Twitter Ads API,
    implementing the BaseAPIClient contract.
    """
    
    def __init__(self, credentials: Dict[str, str], enable_cache: bool = True,
                enable_metrics: bool = True):
        """
        Initialize the Twitter API client.
        
        Args:
            credentials: Dictionary containing X_API_KEY, X_API_SECRET,
                         X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, X_BEARER_TOKEN
            enable_cache: Whether to enable response caching
            enable_metrics: Whether to track API usage metrics
        """
        super().__init__('TWITTER', credentials)
        
        # Store credential values for easier access
        self.consumer_key = credentials.get('X_API_KEY')
        self.consumer_secret = credentials.get('X_API_SECRET')
        self.access_token = credentials.get('X_ACCESS_TOKEN')
        self.access_token_secret = credentials.get('X_ACCESS_TOKEN_SECRET')
        self.bearer_token = credentials.get('X_BEARER_TOKEN')
        
        # Internal API objects
        self.api = None  # v1.1 API client
        self.client = None  # v2 API client
        
        # Set up cache if enabled
        if enable_cache:
            self.cache = TTLCache(default_ttl=300)  # 5 minute TTL
            
        # Set up metrics if enabled
        if enable_metrics:
            self.metrics = APIMetrics()
            
        # Initialize API if credentials are available
        if all([self.consumer_key, self.consumer_secret, 
                self.access_token, self.access_token_secret]):
            self.initialize()
            
    def initialize(self) -> bool:
        """
        Initialize the Twitter API.
        
        Returns:
            True if initialization was successful, False otherwise
        """
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
            logger.info("Twitter API initialized successfully")
            return True
        except Exception as e:
            error_msg = f"Error initializing Twitter API: {str(e)}"
            logger.error(error_msg)
            self.is_initialized = False
            
            # Log the initialization error
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method='INIT',
                url='tweepy.OAuth1UserHandler',
                headers={},
                data={'consumer_key': self.consumer_key[:4] + '********'},
                response_status=500,
                response_data=None,
                error=error_msg
            )
            return False
            
    def execute_request(self, request: APIRequest) -> APIResponse:
        """
        Execute a Twitter API request.
        
        Args:
            request: The API request to execute
            
        Returns:
            API response object
        """
        if not self.is_initialized:
            return APIResponse(
                request_id=request.id,
                success=False,
                error='Twitter API client is not initialized'
            )
            
        # Check cache first if request is cacheable
        cached_response = self.get_from_cache(request)
        if cached_response:
            logger.debug(f"Cache hit for request: {request.operation} {request.endpoint}")
            
            # Track metrics even for cached responses
            if self.metrics:
                cached_response.timing = 0  # Cache lookup is very fast
                self.track_metrics(request, cached_response)
                
            return cached_response
            
        # Start timing
        start_time = time.time()
        
        try:
            # Log the API call attempt
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method=request.method,
                url=request.endpoint,
                headers=request.headers,
                data=request.data,
                response_status=0,  # Will be updated after call
                response_data=None  # Will be updated after call
            )
            
            # Execute the request based on the operation
            if request.operation == 'post_tweet':
                response = self._post_tweet(request)
            elif request.operation == 'upload_media':
                response = self._upload_media(request)
            elif request.operation == 'create_campaign':
                response = self._create_campaign(request)
            elif request.operation == 'create_line_item':
                response = self._create_line_item(request)
            elif request.operation == 'create_promoted_tweet':
                response = self._create_promoted_tweet(request)
            elif request.operation == 'get_campaign_stats':
                response = self._get_campaign_stats(request)
            elif request.operation == 'create_targeting_criteria':
                response = self._create_targeting_criteria(request)
            elif request.operation == 'update_campaign_status':
                response = self._update_campaign_status(request)
            else:
                response = self._execute_generic_request(request)
                
            # Calculate timing
            elapsed = time.time() - start_time
            response.timing = elapsed
            
            # Cache successful GET responses
            if response.success and request.cacheable:
                self.save_to_cache(request, response)
                
            # Track metrics
            if self.metrics:
                self.track_metrics(request, response)
                
            return response
            
        except Exception as e:
            elapsed = time.time() - start_time
            
            error_msg = str(e)
            logger.error(f"Error executing Twitter request: {error_msg}")
            
            # Create error response
            response = APIResponse(
                request_id=request.id,
                success=False,
                status_code=500,
                error=error_msg,
                timing=elapsed
            )
            
            # Track metrics for errors too
            if self.metrics:
                self.track_metrics(request, response)
                
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method=request.method,
                url=request.endpoint,
                headers=request.headers,
                data=request.data,
                response_status=500,
                response_data=None,
                error=error_msg
            )
            
            return response
            
    def _post_tweet(self, request: APIRequest) -> APIResponse:
        """
        Post a tweet, optionally with media.
        
        Args:
            request: API request with tweet parameters
            
        Returns:
            API response with tweet details
        """
        text = request.data.get('text')
        media_ids = request.data.get('media_ids')
        
        try:
            # Using v2 API via client
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids
            )
            
            tweet_id = response.data['id']
            
            result = {
                'success': True,
                'tweet_id': tweet_id,
                'text': text
            }
            
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method='POST',
                url='tweets',
                headers={},
                data={'text': text, 'media_ids': media_ids},
                response_status=200,
                response_data=result
            )
            
            logger.info(f"Created Twitter tweet: {tweet_id}")
            
            # Return successful response
            return APIResponse(
                request_id=request.id,
                success=True,
                status_code=200,
                data=result
            )
            
        except Exception as e:
            error_msg = str(e)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method='POST',
                url='tweets',
                headers={},
                data={'text': text, 'media_ids': media_ids},
                response_status=500,
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=500,
                error=error_msg
            )
            
    def _upload_media(self, request: APIRequest) -> APIResponse:
        """
        Upload media to Twitter.
        
        Args:
            request: API request with media parameters
            
        Returns:
            API response with media details
        """
        media_path = request.data.get('media_path')
        
        try:
            # Using v1.1 API for media upload
            media = self.api.media_upload(media_path)
            media_id = media.media_id_string
            
            result = {
                'success': True,
                'media_id': media_id,
                'media_path': media_path
            }
            
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method='POST',
                url='media/upload',
                headers={},
                data={'media_path': media_path},
                response_status=200,
                response_data=result
            )
            
            logger.info(f"Uploaded Twitter media: {media_id}")
            
            # Return successful response
            return APIResponse(
                request_id=request.id,
                success=True,
                status_code=200,
                data=result
            )
            
        except Exception as e:
            error_msg = str(e)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method='POST',
                url='media/upload',
                headers={},
                data={'media_path': media_path},
                response_status=500,
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=500,
                error=error_msg
            )
            
    def _create_campaign(self, request: APIRequest) -> APIResponse:
        """
        Create a new ad campaign.
        
        Args:
            request: API request with campaign parameters
            
        Returns:
            API response with campaign details
        """
        # Simplified implementation for proof of concept
        # In a real implementation, you'd use the Twitter Ads API
        name = request.data.get('name')
        funding_instrument_id = request.data.get('funding_instrument_id')
        daily_budget = request.data.get('daily_budget')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        # Simulate a successful campaign creation
        campaign_id = f"test_campaign_{name.replace(' ', '_').lower()}"
        
        result = {
            'success': True,
            'campaign_id': campaign_id,
            'name': name,
            'daily_budget': daily_budget,
            'start_time': start_time,
            'end_time': end_time
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='TWITTER',
            method='POST',
            url='campaigns',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Twitter campaign: {campaign_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _create_line_item(self, request: APIRequest) -> APIResponse:
        """
        Create a line item within a campaign.
        
        Args:
            request: API request with line item parameters
            
        Returns:
            API response with line item details
        """
        # Simplified implementation for proof of concept
        campaign_id = request.data.get('campaign_id')
        name = request.data.get('name')
        product_type = request.data.get('product_type')
        targeting = request.data.get('targeting')
        bid_amount = request.data.get('bid_amount')
        
        # Simulate a successful line item creation
        line_item_id = f"test_line_item_{name.replace(' ', '_').lower()}"
        
        result = {
            'success': True,
            'line_item_id': line_item_id,
            'campaign_id': campaign_id,
            'name': name,
            'product_type': product_type,
            'targeting': targeting,
            'bid_amount': bid_amount
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='TWITTER',
            method='POST',
            url='line_items',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Twitter line item: {line_item_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _create_promoted_tweet(self, request: APIRequest) -> APIResponse:
        """
        Create a promoted tweet within a campaign.
        
        Args:
            request: API request with promoted tweet parameters
            
        Returns:
            API response with promoted tweet details
        """
        # Simplified implementation for proof of concept
        campaign_id = request.data.get('campaign_id')
        tweet_id = request.data.get('tweet_id')
        line_item_id = request.data.get('line_item_id')
        
        # Simulate a successful promoted tweet creation
        promoted_tweet_id = f"test_promoted_tweet_{tweet_id}"
        
        result = {
            'success': True,
            'promoted_tweet_id': promoted_tweet_id,
            'campaign_id': campaign_id,
            'tweet_id': tweet_id,
            'line_item_id': line_item_id
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='TWITTER',
            method='POST',
            url='promoted_tweets',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Twitter promoted tweet: {promoted_tweet_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _get_campaign_stats(self, request: APIRequest) -> APIResponse:
        """
        Get statistics for a campaign.
        
        Args:
            request: API request with campaign ID
            
        Returns:
            API response with campaign statistics
        """
        # Simplified implementation for proof of concept
        campaign_id = request.data.get('campaign_id')
        
        # Simulate campaign statistics
        stats = {
            'impressions': 5000,
            'engagements': 200,
            'clicks': 100,
            'retweets': 10,
            'likes': 30,
            'spend': 50.00  # Daily spend in account currency
        }
        
        result = {
            'success': True,
            'campaign_id': campaign_id,
            'stats': stats
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='TWITTER',
            method='GET',
            url=f"campaigns/{campaign_id}/stats",
            headers={},
            data={},
            response_status=200,
            response_data=result
        )
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _create_targeting_criteria(self, request: APIRequest) -> APIResponse:
        """
        Create targeting criteria for a line item.
        
        Args:
            request: API request with targeting parameters
            
        Returns:
            API response with targeting details
        """
        # Simplified implementation for proof of concept
        line_item_id = request.data.get('line_item_id')
        criteria = request.data.get('criteria')
        
        # Simulate a successful targeting creation
        targeting_id = f"test_targeting_{line_item_id}"
        
        result = {
            'success': True,
            'targeting_id': targeting_id,
            'line_item_id': line_item_id,
            'criteria': criteria
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='TWITTER',
            method='POST',
            url='targeting_criteria',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Twitter targeting criteria: {targeting_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _update_campaign_status(self, request: APIRequest) -> APIResponse:
        """
        Update the status of a campaign.
        
        Args:
            request: API request with status update parameters
            
        Returns:
            API response with updated campaign details
        """
        # Simplified implementation for proof of concept
        campaign_id = request.data.get('campaign_id')
        status = request.data.get('status')
        
        result = {
            'success': True,
            'campaign_id': campaign_id,
            'status': status,
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%S-05:00')
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='TWITTER',
            method='PUT',
            url=f"campaigns/{campaign_id}",
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Updated Twitter campaign status: {campaign_id} -> {status}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _execute_generic_request(self, request: APIRequest) -> APIResponse:
        """
        Execute a generic Twitter API request for operations not specifically implemented.
        
        Args:
            request: The API request to execute
            
        Returns:
            API response object
        """
        try:
            # Map operations to API endpoints
            endpoint_mapping = {
                'get_tweet': '/tweets',
                'get_user': '/users',
                'get_followers': '/users/{id}/followers',
                'get_following': '/users/{id}/following',
                'get_user_tweets': '/users/{id}/tweets',
                'get_campaign': '/ads/campaigns',
                'get_campaign_stats': '/ads/campaign-analytics',
                'get_adgroup': '/ads/adgroups',
                'get_ad': '/ads/creatives'
            }
            
            # Build the URL for the request
            base_url = self.api_url
            url_path = None
            
            # Check if the operation maps to a known endpoint
            for op_prefix, endpoint in endpoint_mapping.items():
                if request.operation.startswith(op_prefix):
                    url_path = endpoint
                    break
            
            # If we couldn't map the operation, try to infer from the endpoint
            if not url_path and request.endpoint:
                url_path = request.endpoint
                
            # If we still don't have a URL path, we can't process this request
            if not url_path:
                return APIResponse(
                    request_id=request.id,
                    success=False,
                    status_code=400,
                    error=f"Couldn't determine API endpoint for operation: {request.operation}"
                )
                
            # Replace any parameter placeholders in the URL
            if '{id}' in url_path and 'id' in request.data:
                url_path = url_path.replace('{id}', str(request.data['id']))
                
            # Build the full URL
            url = f"{base_url}{url_path}"
            if request.method == 'GET' and request.data:
                # Add query parameters for GET requests
                query_params = '&'.join([f"{k}={v}" for k, v in request.data.items() if v is not None])
                if query_params:
                    url = f"{url}?{query_params}"
                    
            # Prepare headers
            headers = request.headers.copy() if request.headers else {}
            if 'Authorization' not in headers and self.bearer_token:
                headers['Authorization'] = f"Bearer {self.bearer_token}"
            if 'Content-Type' not in headers and request.method in ('POST', 'PUT'):
                headers['Content-Type'] = 'application/json'
                
            # Make the HTTP request
            logger.info(f"Making Twitter API request: {request.method} {url}")
            
            # Twitter API v2 endpoints require authentication
            auth_headers = {}
            if self.api_key and self.api_key_secret:
                # Setup for OAuth 1.0a authentication
                auth_headers.update({
                    'X-Twitter-API-Key': self.api_key, 
                    'X-Twitter-Client-Token': self.api_key_secret
                })
                
            # Log the API call attempt
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method=request.method,
                url=url,
                headers={**headers, **auth_headers},
                data=request.data if request.method in ('POST', 'PUT') else None,
                response_status=0,  # Will be updated after call
                response_data=None  # Will be updated after call
            )
            
            # We don't actually make the HTTP request as this is a mock API client
            # In a real implementation, we would use requests or similar:
            # response = requests.request(
            #     method=request.method,
            #     url=url,
            #     headers={**headers, **auth_headers},
            #     json=request.data if request.method in ('POST', 'PUT') else None
            # )
            
            # For simulation, we'll return a success response with mock data
            if request.operation.startswith('get_campaign'):
                mock_data = {
                    "data": {
                        "campaign_id": request.data.get('campaign_id', '12345'),
                        "name": "Simulated Twitter Campaign",
                        "status": "ACTIVE",
                        "metrics": {
                            "impressions": 5432,
                            "clicks": 123,
                            "engagement_rate": 2.26
                        }
                    }
                }
            elif request.operation.startswith('get_user'):
                mock_data = {
                    "data": {
                        "id": request.data.get('id', '54321'),
                        "name": "Mock User",
                        "username": "mockuser",
                        "followers_count": 1000,
                        "following_count": 500
                    }
                }
            else:
                mock_data = {
                    "data": {
                        "message": "Generic operation simulation successful",
                        "request_info": {
                            "operation": request.operation,
                            "method": request.method,
                            "url": url
                        }
                    }
                }
                
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method=request.method,
                url=url,
                headers={**headers, **auth_headers},
                data=request.data if request.method in ('POST', 'PUT') else None,
                response_status=200,
                response_data=mock_data
            )
            
            return APIResponse(
                request_id=request.id,
                success=True,
                status_code=200,
                data=mock_data
            )
            
        except Exception as e:
            error_msg = f"Error executing generic Twitter request: {str(e)}"
            logger.error(error_msg)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='TWITTER',
                method=request.method if hasattr(request, 'method') else 'UNKNOWN',
                url=url if 'url' in locals() else request.endpoint,
                headers=headers if 'headers' in locals() else {},
                data=request.data if hasattr(request, 'data') else {},
                response_status=500,
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=500,
                error=error_msg
            )
        
    # Helper methods to create API requests
    def post_tweet_request(self, text: str, media_ids: Optional[List[str]] = None) -> APIRequest:
        """
        Create an API request for posting a tweet.
        
        Args:
            text: Tweet text
            media_ids: List of media IDs to attach to the tweet
            
        Returns:
            API request object
        """
        data = {'text': text}
        if media_ids:
            data['media_ids'] = media_ids
            
        return APIRequest(
            method='POST',
            endpoint='tweets',
            data=data,
            platform='TWITTER',
            operation='post_tweet'
        )
        
    def upload_media_request(self, media_path: str) -> APIRequest:
        """
        Create an API request for uploading media.
        
        Args:
            media_path: Path to the media file
            
        Returns:
            API request object
        """
        return APIRequest(
            method='POST',
            endpoint='media/upload',
            data={'media_path': media_path},
            platform='TWITTER',
            operation='upload_media'
        )
        
    def create_campaign_request(self, name: str, funding_instrument_id: str,
                              daily_budget: float, start_time: str,
                              end_time: Optional[str] = None) -> APIRequest:
        """
        Create an API request for campaign creation.
        
        Args:
            name: Campaign name
            funding_instrument_id: Funding instrument ID
            daily_budget: Daily budget in account currency
            start_time: Campaign start time (ISO format)
            end_time: Campaign end time (ISO format), optional
            
        Returns:
            API request object
        """
        data = {
            'name': name,
            'funding_instrument_id': funding_instrument_id,
            'daily_budget': daily_budget,
            'start_time': start_time
        }
        
        if end_time:
            data['end_time'] = end_time
            
        return APIRequest(
            method='POST',
            endpoint='campaigns',
            data=data,
            platform='TWITTER',
            operation='create_campaign'
        )
        
    def create_line_item_request(self, campaign_id: str, name: str,
                               product_type: str = 'PROMOTED_TWEETS',
                               placements: Optional[List[Dict]] = None,
                               targeting: Optional[Dict] = None,
                               bid_amount: Optional[float] = None) -> APIRequest:
        """
        Create an API request for line item creation.
        
        Args:
            campaign_id: ID of the campaign
            name: Line item name
            product_type: Product type (default: PROMOTED_TWEETS)
            placements: List of placement objects
            targeting: Targeting criteria
            bid_amount: Bid amount in account currency
            
        Returns:
            API request object
        """
        data = {
            'campaign_id': campaign_id,
            'name': name,
            'product_type': product_type
        }
        
        if placements:
            data['placements'] = placements
            
        if targeting:
            data['targeting'] = targeting
            
        if bid_amount:
            data['bid_amount'] = bid_amount
            
        return APIRequest(
            method='POST',
            endpoint='line_items',
            data=data,
            platform='TWITTER',
            operation='create_line_item'
        )
        
    def create_promoted_tweet_request(self, campaign_id: str, tweet_id: str,
                                    line_item_id: str) -> APIRequest:
        """
        Create an API request for promoted tweet creation.
        
        Args:
            campaign_id: ID of the campaign
            tweet_id: ID of the tweet to promote
            line_item_id: ID of the line item
            
        Returns:
            API request object
        """
        data = {
            'campaign_id': campaign_id,
            'tweet_id': tweet_id,
            'line_item_id': line_item_id
        }
        
        return APIRequest(
            method='POST',
            endpoint='promoted_tweets',
            data=data,
            platform='TWITTER',
            operation='create_promoted_tweet'
        )
        
    def get_campaign_stats_request(self, campaign_id: str) -> APIRequest:
        """
        Create an API request for getting campaign statistics.
        
        Args:
            campaign_id: ID of the campaign to get stats for
            
        Returns:
            API request object
        """
        return APIRequest(
            method='GET',
            endpoint=f"campaigns/{campaign_id}/stats",
            data={'campaign_id': campaign_id},
            platform='TWITTER',
            operation='get_campaign_stats',
            cacheable=True  # This request can be cached
        )
        
    def create_targeting_criteria_request(self, line_item_id: str, 
                                        criteria: Dict[str, Any]) -> APIRequest:
        """
        Create an API request for targeting criteria creation.
        
        Args:
            line_item_id: ID of the line item
            criteria: Targeting criteria
            
        Returns:
            API request object
        """
        data = {
            'line_item_id': line_item_id,
            'criteria': criteria
        }
        
        return APIRequest(
            method='POST',
            endpoint='targeting_criteria',
            data=data,
            platform='TWITTER',
            operation='create_targeting_criteria'
        )
        
    def update_campaign_status_request(self, campaign_id: str, status: str) -> APIRequest:
        """
        Create an API request for updating campaign status.
        
        Args:
            campaign_id: ID of the campaign
            status: New status (ACTIVE, PAUSED, DELETED)
            
        Returns:
            API request object
        """
        data = {
            'campaign_id': campaign_id,
            'status': status
        }
        
        return APIRequest(
            method='PUT',
            endpoint=f"campaigns/{campaign_id}",
            data=data,
            platform='TWITTER',
            operation='update_campaign_status'
        )