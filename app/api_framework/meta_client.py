"""
Meta (Facebook) API Client implementation.

This module provides a client implementation for the Meta (Facebook) Ads API,
using the common API Integration Framework patterns.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union, Type, TypeVar

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.exceptions import FacebookRequestError

from app.api_framework.base import APIRequest, APIResponse, BaseAPIClient
from app.api_framework.cache import TTLCache
from app.api_framework.metrics import APIMetrics
from app.utils.api_debug import api_diagnostic_tool

# Configure logging
logger = logging.getLogger(__name__)


class MetaAPIClient(BaseAPIClient):
    """
    Client for interacting with Meta (Facebook) Ads API.
    
    This class provides a standardized interface for the Meta Ads API,
    implementing the BaseAPIClient contract.
    """
    
    def __init__(self, credentials: Dict[str, str], enable_cache: bool = True,
                enable_metrics: bool = True):
        """
        Initialize the Meta API client.
        
        Args:
            credentials: Dictionary containing META_APP_ID, META_APP_SECRET,
                         META_ACCESS_TOKEN, and META_AD_ACCOUNT_ID
            enable_cache: Whether to enable response caching
            enable_metrics: Whether to track API usage metrics
        """
        super().__init__('META', credentials)
        
        # Store credential values for easier access
        self.app_id = credentials.get('META_APP_ID')
        self.app_secret = credentials.get('META_APP_SECRET')
        self.access_token = credentials.get('META_ACCESS_TOKEN')
        self.ad_account_id = credentials.get('META_AD_ACCOUNT_ID')
        
        # Set up cache if enabled
        if enable_cache:
            self.cache = TTLCache(default_ttl=300)  # 5 minute TTL
            
        # Set up metrics if enabled
        if enable_metrics:
            self.metrics = APIMetrics()
            
        # Initialize API if credentials are available
        if all([self.app_id, self.app_secret, self.access_token, self.ad_account_id]):
            self.initialize()
            
    def initialize(self) -> bool:
        """
        Initialize the Facebook Ads API.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.is_initialized = True
            logger.info("Meta API initialized successfully")
            return True
        except Exception as e:
            error_msg = f"Error initializing Meta API: {str(e)}"
            logger.error(error_msg)
            self.is_initialized = False
            
            # Log the initialization error
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='INIT',
                url='facebook_business.api.FacebookAdsApi.init',
                headers={},
                data={'app_id': self.app_id[:4] + '********'},
                response_status=500,
                response_data=None,
                error=error_msg
            )
            return False
            
    def execute_request(self, request: APIRequest) -> APIResponse:
        """
        Execute a Meta API request.
        
        Args:
            request: The API request to execute
            
        Returns:
            API response object
        """
        if not self.is_initialized:
            return APIResponse(
                request_id=request.id,
                success=False,
                error='Meta API client is not initialized'
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
                platform='META',
                method=request.method,
                url=request.endpoint,
                headers=request.headers,
                data=request.data,
                response_status=0,  # Will be updated after call
                response_data=None  # Will be updated after call
            )
            
            # Execute the request based on the operation
            if request.operation == 'create_campaign':
                response = self._create_campaign(request)
            elif request.operation == 'create_ad_set':
                response = self._create_ad_set(request)
            elif request.operation == 'create_ad':
                response = self._create_ad(request)
            elif request.operation == 'get_campaign_stats':
                response = self._get_campaign_stats(request)
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
            logger.error(f"Error executing Meta request: {error_msg}")
            
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
                platform='META',
                method=request.method,
                url=request.endpoint,
                headers=request.headers,
                data=request.data,
                response_status=500,
                response_data=None,
                error=error_msg
            )
            
            return response
            
    def _create_campaign(self, request: APIRequest) -> APIResponse:
        """
        Create a new Meta ad campaign.
        
        Args:
            request: API request with campaign parameters
            
        Returns:
            API response with campaign details
        """
        params = request.data
        account = AdAccount(self.ad_account_id)
        
        # Set default special ad category for job ads
        if 'special_ad_category' not in params:
            params['special_ad_category'] = 'EMPLOYMENT'
            
        try:
            # Make the API call
            campaign = account.create_campaign(
                params=params,
                fields=['id', 'name', 'objective', 'status']
            )
            
            result = {
                'success': True,
                'campaign_id': campaign['id'],
                'name': campaign['name'],
                'status': campaign['status']
            }
            
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='POST',
                url=f"{self.ad_account_id}/campaigns",
                headers={},
                data=params,
                response_status=200,
                response_data=result
            )
            
            logger.info(f"Created Meta campaign: {campaign['id']}")
            
            # Return successful response
            return APIResponse(
                request_id=request.id,
                success=True,
                status_code=200,
                data=result
            )
            
        except FacebookRequestError as e:
            # Handle Facebook-specific error response
            error_msg = str(e)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='POST',
                url=f"{self.ad_account_id}/campaigns",
                headers={},
                data=params,
                response_status=e.http_status(),
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=e.http_status(),
                error=error_msg
            )
            
    def _create_ad_set(self, request: APIRequest) -> APIResponse:
        """
        Create a new ad set within a campaign.
        
        Args:
            request: API request with ad set parameters
            
        Returns:
            API response with ad set details
        """
        params = request.data
        account = AdAccount(self.ad_account_id)
        
        # Ensure budget is in cents
        if 'daily_budget' in params and isinstance(params['daily_budget'], (int, float)):
            params['daily_budget'] = int(params['daily_budget'] * 100)
            
        try:
            # Make the API call
            ad_set = account.create_ad_set(
                params=params,
                fields=['id', 'name', 'status', 'daily_budget']
            )
            
            result = {
                'success': True,
                'ad_set_id': ad_set['id'],
                'name': ad_set['name'],
                'status': ad_set['status'],
                'daily_budget': ad_set['daily_budget']
            }
            
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='POST',
                url=f"{self.ad_account_id}/adsets",
                headers={},
                data=params,
                response_status=200,
                response_data=result
            )
            
            logger.info(f"Created Meta ad set: {ad_set['id']}")
            
            # Return successful response
            return APIResponse(
                request_id=request.id,
                success=True,
                status_code=200,
                data=result
            )
            
        except FacebookRequestError as e:
            # Handle Facebook-specific error response
            error_msg = str(e)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='POST',
                url=f"{self.ad_account_id}/adsets",
                headers={},
                data=params,
                response_status=e.http_status(),
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=e.http_status(),
                error=error_msg
            )
            
    def _create_ad(self, request: APIRequest) -> APIResponse:
        """
        Create a new ad within an ad set.
        
        Args:
            request: API request with ad parameters
            
        Returns:
            API response with ad details
        """
        params = request.data
        account = AdAccount(self.ad_account_id)
        
        try:
            # Make the API call
            ad = account.create_ad(
                params=params,
                fields=['id', 'name', 'status']
            )
            
            result = {
                'success': True,
                'ad_id': ad['id'],
                'name': ad['name'],
                'status': ad['status']
            }
            
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='POST',
                url=f"{self.ad_account_id}/ads",
                headers={},
                data=params,
                response_status=200,
                response_data=result
            )
            
            logger.info(f"Created Meta ad: {ad['id']}")
            
            # Return successful response
            return APIResponse(
                request_id=request.id,
                success=True,
                status_code=200,
                data=result
            )
            
        except FacebookRequestError as e:
            # Handle Facebook-specific error response
            error_msg = str(e)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='POST',
                url=f"{self.ad_account_id}/ads",
                headers={},
                data=params,
                response_status=e.http_status(),
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=e.http_status(),
                error=error_msg
            )
            
    def _get_campaign_stats(self, request: APIRequest) -> APIResponse:
        """
        Get statistics for a campaign.
        
        Args:
            request: API request with campaign ID
            
        Returns:
            API response with campaign statistics
        """
        campaign_id = request.data.get('campaign_id')
        if not campaign_id:
            return APIResponse(
                request_id=request.id,
                success=False,
                error='Missing campaign_id parameter'
            )
            
        try:
            campaign = Campaign(campaign_id)
            
            # Make the API call
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
                result = {
                    'success': True,
                    'campaign_id': campaign_id,
                    'stats': insights[0]
                }
            else:
                result = {
                    'success': True,
                    'campaign_id': campaign_id,
                    'stats': {}
                }
                
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='GET',
                url=f"{campaign_id}/insights",
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
            
        except FacebookRequestError as e:
            # Handle Facebook-specific error response
            error_msg = str(e)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='META',
                method='GET',
                url=f"{campaign_id}/insights",
                headers={},
                data={},
                response_status=e.http_status(),
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=e.http_status(),
                error=error_msg
            )
            
    def _execute_generic_request(self, request: APIRequest) -> APIResponse:
        """
        Execute a generic Meta API request for operations not specifically implemented.
        
        Args:
            request: The API request to execute
            
        Returns:
            API response object
        """
        # Map API endpoints to their corresponding Facebook objects
        endpoint_mapping = {
            'campaign': Campaign,
            'adset': AdSet,
            'ad': Ad,
            'adaccount': AdAccount
        }
        
        try:
            # Parse the endpoint to determine the object type
            endpoint_parts = request.endpoint.strip('/').split('/')
            
            # Extract object type and ID
            object_id = None
            object_type = None
            
            # Check if endpoint has ID structure
            if len(endpoint_parts) > 0 and any(part in endpoint_parts[-1] for part in endpoint_mapping.keys()):
                for key in endpoint_mapping.keys():
                    if key in endpoint_parts[-1]:
                        object_type = key
                        object_id = endpoint_parts[-1]
                        break
            
            # If we couldn't determine the object type but have an ID-like string
            if not object_type and len(endpoint_parts) > 0 and endpoint_parts[-1].isalnum():
                object_id = endpoint_parts[-1]
                
                # Try to infer object type from operation
                if 'campaign' in request.operation:
                    object_type = 'campaign'
                elif 'adset' in request.operation or 'ad_set' in request.operation:
                    object_type = 'adset'
                elif 'ad' in request.operation and 'adset' not in request.operation:
                    object_type = 'ad'
                elif 'account' in request.operation:
                    object_type = 'adaccount'
            
            # Use account as fallback
            if not object_id:
                object_type = 'adaccount'
                object_id = self.ad_account_id
            
            # Create the appropriate object
            if object_type and object_type in endpoint_mapping:
                fb_object = endpoint_mapping[object_type](object_id)
                
                # Execute the appropriate method based on the HTTP method
                if request.method == 'GET':
                    # For GET requests, use get_<field> or get_<connection> pattern
                    if '.' in request.operation:
                        # Handle dot notation (e.g., 'campaign.get_insights')
                        operation_parts = request.operation.split('.')
                        if len(operation_parts) > 1 and hasattr(fb_object, operation_parts[1]):
                            method = getattr(fb_object, operation_parts[1])
                            result = method(params=request.data)
                            return APIResponse(
                                request_id=request.id,
                                success=True,
                                status_code=200,
                                data=result
                            )
                    else:
                        # Try to infer the method from operation
                        method_name = None
                        if 'get_' in request.operation:
                            method_name = request.operation
                        elif 'insights' in request.endpoint or 'statistics' in request.endpoint:
                            method_name = 'get_insights'
                        
                        if method_name and hasattr(fb_object, method_name):
                            method = getattr(fb_object, method_name)
                            result = method(params=request.data)
                            return APIResponse(
                                request_id=request.id,
                                success=True,
                                status_code=200,
                                data=result
                            )
                elif request.method == 'POST':
                    # For POST requests, use create_<object> pattern
                    if '.' in request.operation:
                        # Handle dot notation
                        operation_parts = request.operation.split('.')
                        if len(operation_parts) > 1 and hasattr(fb_object, operation_parts[1]):
                            method = getattr(fb_object, operation_parts[1])
                            result = method(params=request.data)
                            return APIResponse(
                                request_id=request.id,
                                success=True,
                                status_code=200,
                                data=result
                            )
                elif request.method == 'DELETE':
                    # For DELETE, use the delete method
                    result = fb_object.api_delete()
                    return APIResponse(
                        request_id=request.id,
                        success=True,
                        status_code=200,
                        data={"deleted": True, "id": object_id}
                    )
            
            # If we reach here, we couldn't handle the request
            logger.warning(f"Unsupported Meta API operation: {request.operation} on {request.endpoint}")
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=400,
                error=f"Operation '{request.operation}' on endpoint '{request.endpoint}' not supported"
            )
            
        except FacebookRequestError as e:
            # Handle Facebook-specific error response
            error_msg = str(e)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='META',
                method=request.method,
                url=request.endpoint,
                headers=request.headers,
                data=request.data,
                response_status=e.http_status(),
                response_data=None,
                error=error_msg
            )
            
            return APIResponse(
                request_id=request.id,
                success=False,
                status_code=e.http_status(),
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Error executing generic Meta request: {str(e)}"
            logger.error(error_msg)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='META',
                method=request.method,
                url=request.endpoint,
                headers=request.headers,
                data=request.data,
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
        
    def create_campaign_request(self, name: str, objective: str = 'REACH',
                              status: str = 'PAUSED',
                              special_ad_categories: Optional[List[str]] = None) -> APIRequest:
        """
        Create an API request object for campaign creation.
        
        Args:
            name: Campaign name
            objective: Campaign objective (e.g., 'REACH', 'BRAND_AWARENESS')
            status: Campaign status ('ACTIVE', 'PAUSED')
            special_ad_categories: Special ad categories if applicable
            
        Returns:
            API request object ready to be executed
        """
        params = {
            'name': name,
            'objective': objective,
            'status': status,
        }
        
        if special_ad_categories:
            params['special_ad_categories'] = special_ad_categories
            
        return APIRequest(
            method='POST',
            endpoint=f"{self.ad_account_id}/campaigns",
            data=params,
            platform='META',
            operation='create_campaign'
        )
        
    def create_ad_set_request(self, campaign_id: str, name: str, targeting: Dict[str, Any],
                            budget: float, bid_amount: int,
                            billing_event: str = 'IMPRESSIONS',
                            status: str = 'PAUSED') -> APIRequest:
        """
        Create an API request object for ad set creation.
        
        Args:
            campaign_id: ID of the campaign to add the ad set to
            name: Ad set name
            targeting: Targeting specifications
            budget: Daily budget in account currency
            bid_amount: Bid amount in cents
            billing_event: Billing event type ('IMPRESSIONS', 'LINK_CLICKS')
            status: Ad set status ('ACTIVE', 'PAUSED')
            
        Returns:
            API request object ready to be executed
        """
        params = {
            'name': name,
            'campaign_id': campaign_id,
            'daily_budget': budget,  # Will be converted to cents in execution
            'billing_event': billing_event,
            'optimization_goal': 'REACH',
            'bid_amount': bid_amount,
            'targeting': targeting,
            'status': status
        }
        
        return APIRequest(
            method='POST',
            endpoint=f"{self.ad_account_id}/adsets",
            data=params,
            platform='META',
            operation='create_ad_set'
        )
        
    def create_ad_request(self, ad_set_id: str, name: str, creative_id: str,
                        status: str = 'PAUSED') -> APIRequest:
        """
        Create an API request object for ad creation.
        
        Args:
            ad_set_id: ID of the ad set to add the ad to
            name: Ad name
            creative_id: ID of the creative to use for the ad
            status: Ad status ('ACTIVE', 'PAUSED')
            
        Returns:
            API request object ready to be executed
        """
        params = {
            'name': name,
            'adset_id': ad_set_id,
            'creative': {'creative_id': creative_id},
            'status': status
        }
        
        return APIRequest(
            method='POST',
            endpoint=f"{self.ad_account_id}/ads",
            data=params,
            platform='META',
            operation='create_ad'
        )
        
    def create_status_update_request(self, campaign_id: str, status: str = 'PAUSED') -> APIRequest:
        """
        Create an API request object for updating campaign status.
        
        Args:
            campaign_id: ID of the campaign to update
            status: New campaign status ('ACTIVE', 'PAUSED')
            
        Returns:
            API request object ready to be executed
        """
        params = {
            'status': status
        }
        
        return APIRequest(
            method='POST',
            endpoint=f"{campaign_id}",
            data=params,
            platform='META',
            operation='update_status'
        )
        
    def create_ad_creative_request(self, name: str, body: str, object_story_spec: Dict[str, Any]) -> APIRequest:
        """
        Create an API request object for ad creative creation.
        
        Args:
            name: Creative name
            body: Ad body text
            object_story_spec: Specification for the creative (page, post, link details)
            
        Returns:
            API request object ready to be executed
        """
        params = {
            'name': name,
            'body': body,
            'object_story_spec': object_story_spec
        }
        
        return APIRequest(
            method='POST',
            endpoint=f"{self.ad_account_id}/adcreatives",
            data=params,
            platform='META',
            operation='create_ad_creative'
        )
        
    def get_campaign_stats_request(self, campaign_id: str) -> APIRequest:
        """
        Create an API request object for getting campaign statistics.
        
        Args:
            campaign_id: ID of the campaign to get stats for
            
        Returns:
            API request object ready to be executed
        """
        return APIRequest(
            method='GET',
            endpoint=f"{campaign_id}/insights",
            data={'campaign_id': campaign_id},
            platform='META',
            operation='get_campaign_stats',
            cacheable=True  # This request can be cached
        )