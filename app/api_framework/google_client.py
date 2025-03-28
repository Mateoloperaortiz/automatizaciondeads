"""
Google Ads API Client implementation.

This module provides a client implementation for the Google Ads API,
using the common API Integration Framework patterns.
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List, Union

# Import Google libraries conditionally to handle cases where they might not be available
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GOOGLE_LIBRARIES_AVAILABLE = True
except ImportError:
    GOOGLE_LIBRARIES_AVAILABLE = False

from app.api_framework.base import APIRequest, APIResponse, BaseAPIClient
from app.api_framework.cache import TTLCache
from app.api_framework.metrics import APIMetrics
from app.utils.api_debug import api_diagnostic_tool

# Configure logging
logger = logging.getLogger(__name__)


class GoogleAPIClient(BaseAPIClient):
    """
    Client for interacting with Google Ads API.
    
    This class provides a standardized interface for the Google Ads API,
    implementing the BaseAPIClient contract.
    """
    
    def __init__(self, credentials: Dict[str, str], enable_cache: bool = True,
                enable_metrics: bool = True):
        """
        Initialize the Google Ads API client.
        
        Args:
            credentials: Dictionary containing GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
                         GOOGLE_REFRESH_TOKEN, GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CUSTOMER_ID
            enable_cache: Whether to enable response caching
            enable_metrics: Whether to track API usage metrics
        """
        super().__init__('GOOGLE', credentials)
        
        # Check if required libraries are available
        if not GOOGLE_LIBRARIES_AVAILABLE:
            logger.error("Google API libraries not available. Install required packages.")
            self.is_initialized = False
            return
            
        # Store credential values for easier access
        self.client_id = credentials.get('GOOGLE_CLIENT_ID')
        self.client_secret = credentials.get('GOOGLE_CLIENT_SECRET')
        self.developer_token = credentials.get('GOOGLE_ADS_DEVELOPER_TOKEN')
        self.customer_id = credentials.get('GOOGLE_ADS_CUSTOMER_ID')
        self.refresh_token = credentials.get('GOOGLE_REFRESH_TOKEN')
        
        # Define paths for OAuth flow
        self.credentials_path = 'credentials.json'
        self.token_path = 'token.json'
        self.scopes = ['https://www.googleapis.com/auth/adwords']
        
        # Google API objects
        self.api_version = 'v12'
        self.service = None
        self.credentials = None
        
        # Set up cache if enabled
        if enable_cache:
            self.cache = TTLCache(default_ttl=300)  # 5 minute TTL
            
        # Set up metrics if enabled
        if enable_metrics:
            self.metrics = APIMetrics()
            
        # Initialize API if credentials are available
        if all([self.client_id, self.client_secret, self.developer_token, self.customer_id]):
            self.initialize()
            
    def initialize(self) -> bool:
        """
        Initialize the Google Ads API.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # If we're in testing mode, use simulation instead of real API
        from app.utils.config import config_manager
        if config_manager.get('TESTING', False) or config_manager.get('GOOGLE_API_SIMULATE', False):
            logger.info("Using simulation mode for Google Ads API (TESTING=True)")
            self.is_initialized = True
            # We're successfully initialized, but in simulation mode
            return True
            
        try:
            # Check if we have a token.json file
            creds = None
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as token:
                    token_data = json.load(token)
                    creds = Credentials.from_authorized_user_info(token_data, self.scopes)
            
            # If there are no valid credentials, use refresh token or prompt the user to log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if self.refresh_token:
                        # Use provided refresh token
                        token_data = {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "refresh_token": self.refresh_token,
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "scopes": self.scopes
                        }
                        creds = Credentials.from_authorized_user_info(token_data, self.scopes)
                    else:
                        # Create credentials.json file if it doesn't exist
                        if not os.path.exists(self.credentials_path):
                            with open(self.credentials_path, 'w') as f:
                                json.dump({
                                    "installed": {
                                        "client_id": self.client_id,
                                        "client_secret": self.client_secret,
                                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                        "token_uri": "https://oauth2.googleapis.com/token",
                                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost:8000"]
                                    }
                                }, f)
                                
                        # This would typically launch a browser for OAuth flow
                        # In a server environment, this needs to be handled differently
                        # Use simulation mode in testing to avoid this
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.scopes)
                        creds = flow.run_local_server(port=8000)
                    
                    # Save the credentials for the next run
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
            
            self.credentials = creds
            
            # Create a connection to the API for AdWords
            # Note: This is a simplified version as the real Google Ads API is more complex
            # In a real implementation, you'd use the google-ads-python library
            self.service = build('adwords', self.api_version, credentials=creds)
            self.is_initialized = True
            logger.info("Google Ads API initialized successfully")
            
            return True
            
        except Exception as e:
            error_msg = f"Error initializing Google Ads API: {str(e)}"
            logger.error(error_msg)
            self.is_initialized = False
            
            # Log the initialization error
            api_diagnostic_tool.log_api_call(
                platform='GOOGLE',
                method='INIT',
                url='google.oauth2.credentials.Credentials',
                headers={},
                data={'client_id': self.client_id[:4] + '********' if self.client_id else None},
                response_status=500,
                response_data=None,
                error=error_msg
            )
            
            # For testing, we'll set initialized to true anyway but keep track of the error
            # This allows tests to run without real credentials
            from app.utils.config import config_manager
            if config_manager.get('TESTING', False):
                logger.warning("Using simulation mode for Google Ads API due to initialization error in testing mode")
                self.is_initialized = True
                return True
                
            return False
            
    def execute_request(self, request: APIRequest) -> APIResponse:
        """
        Execute a Google Ads API request.
        
        Args:
            request: The API request to execute
            
        Returns:
            API response object
        """
        if not self.is_initialized:
            return APIResponse(
                request_id=request.id,
                success=False,
                error='Google Ads API client is not initialized'
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
                platform='GOOGLE',
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
            elif request.operation == 'create_ad_group':
                response = self._create_ad_group(request)
            elif request.operation == 'create_responsive_search_ad':
                response = self._create_responsive_search_ad(request)
            elif request.operation == 'get_campaign_stats':
                response = self._get_campaign_stats(request)
            elif request.operation == 'create_location_targeting':
                response = self._create_location_targeting(request)
            elif request.operation == 'create_demographic_targeting':
                response = self._create_demographic_targeting(request)
            elif request.operation == 'create_keyword_targeting':
                response = self._create_keyword_targeting(request)
            elif request.operation == 'update_campaign_status':
                response = self._update_campaign_status(request)
            elif request.operation == 'update_budget':
                response = self._update_budget(request)
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
            logger.error(f"Error executing Google request: {error_msg}")
            
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
                platform='GOOGLE',
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
        Create a new ad campaign.
        
        Args:
            request: API request with campaign parameters
            
        Returns:
            API response with campaign details
        """
        # Simplified implementation for proof of concept
        # In a real implementation, you'd use the Google Ads API client library
        name = request.data.get('name')
        budget = request.data.get('budget')
        status = request.data.get('status', 'PAUSED')
        
        # Simulate a successful campaign creation
        campaign_id = f"test_campaign_{name.replace(' ', '_').lower()}"
        
        result = {
            'success': True,
            'campaign_id': campaign_id,
            'name': name,
            'status': status,
            'budget': budget
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
            method='POST',
            url='campaigns',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Google campaign: {campaign_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _create_ad_group(self, request: APIRequest) -> APIResponse:
        """
        Create a new ad group within a campaign.
        
        Args:
            request: API request with ad group parameters
            
        Returns:
            API response with ad group details
        """
        # Simplified implementation for proof of concept
        campaign_id = request.data.get('campaign_id')
        name = request.data.get('name')
        status = request.data.get('status', 'PAUSED')
        
        # Simulate a successful ad group creation
        ad_group_id = f"test_adgroup_{name.replace(' ', '_').lower()}"
        
        result = {
            'success': True,
            'ad_group_id': ad_group_id,
            'campaign_id': campaign_id,
            'name': name,
            'status': status
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
            method='POST',
            url='ad_groups',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Google ad group: {ad_group_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _create_responsive_search_ad(self, request: APIRequest) -> APIResponse:
        """
        Create a new responsive search ad within an ad group.
        
        Args:
            request: API request with ad parameters
            
        Returns:
            API response with ad details
        """
        # Extract parameters
        ad_group_id = request.data.get('ad_group_id')
        headlines = request.data.get('headlines', [])
        descriptions = request.data.get('descriptions', [])
        final_url = request.data.get('final_url')
        status = request.data.get('status', 'PAUSED')
        
        # Validate inputs
        if len(headlines) < 3 or len(headlines) > 15:
            return APIResponse(
                request_id=request.id,
                success=False,
                error='Must provide 3-15 headlines'
            )
        
        if len(descriptions) < 2 or len(descriptions) > 4:
            return APIResponse(
                request_id=request.id,
                success=False,
                error='Must provide 2-4 descriptions'
            )
        
        # Simulate a successful ad creation
        ad_id = f"test_ad_{ad_group_id}"
        
        result = {
            'success': True,
            'ad_id': ad_id,
            'ad_group_id': ad_group_id,
            'status': status,
            'headlines_count': len(headlines),
            'descriptions_count': len(descriptions),
            'final_url': final_url
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
            method='POST',
            url='responsive_search_ads',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Google responsive search ad: {ad_id}")
        
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
            'impressions': 1000,
            'clicks': 50,
            'cost': 25.0,
            'conversions': 2,
            'ctr': 0.05,
            'average_cpc': 0.5
        }
        
        result = {
            'success': True,
            'campaign_id': campaign_id,
            'stats': stats
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
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
            
    def _create_location_targeting(self, request: APIRequest) -> APIResponse:
        """
        Add location targeting to a campaign.
        
        Args:
            request: API request with location targeting parameters
            
        Returns:
            API response with location targeting details
        """
        # Simplified implementation for proof of concept
        campaign_id = request.data.get('campaign_id')
        locations = request.data.get('locations', [])
        
        # Simulate a successful location targeting creation
        targeting_id = f"test_location_{campaign_id}"
        
        result = {
            'success': True,
            'targeting_id': targeting_id,
            'campaign_id': campaign_id,
            'locations': locations
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
            method='POST',
            url='campaign_location_targets',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Google location targeting: {targeting_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _create_demographic_targeting(self, request: APIRequest) -> APIResponse:
        """
        Add demographic targeting to an ad group.
        
        Args:
            request: API request with demographic targeting parameters
            
        Returns:
            API response with demographic targeting details
        """
        # Simplified implementation for proof of concept
        ad_group_id = request.data.get('ad_group_id')
        criteria = request.data.get('criteria', {})
        
        # Simulate a successful demographic targeting creation
        targeting_id = f"test_demographic_{ad_group_id}"
        
        result = {
            'success': True,
            'targeting_id': targeting_id,
            'ad_group_id': ad_group_id,
            'criteria': criteria
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
            method='POST',
            url='ad_group_demographic_targets',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Google demographic targeting: {targeting_id}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _create_keyword_targeting(self, request: APIRequest) -> APIResponse:
        """
        Add keyword targeting to an ad group.
        
        Args:
            request: API request with keyword targeting parameters
            
        Returns:
            API response with keyword targeting details
        """
        # Simplified implementation for proof of concept
        ad_group_id = request.data.get('ad_group_id')
        keywords = request.data.get('keywords', [])
        match_type = request.data.get('match_type', 'BROAD')
        
        # Simulate a successful keyword targeting creation
        targeting_id = f"test_keyword_{ad_group_id}"
        
        result = {
            'success': True,
            'targeting_id': targeting_id,
            'ad_group_id': ad_group_id,
            'keywords': keywords,
            'match_type': match_type
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
            method='POST',
            url='ad_group_keywords',
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Created Google keyword targeting: {targeting_id}")
        
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
            platform='GOOGLE',
            method='PUT',
            url=f"campaigns/{campaign_id}",
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Updated Google campaign status: {campaign_id} -> {status}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _update_budget(self, request: APIRequest) -> APIResponse:
        """
        Update the budget of a campaign.
        
        Args:
            request: API request with budget update parameters
            
        Returns:
            API response with updated campaign details
        """
        # Simplified implementation for proof of concept
        campaign_id = request.data.get('campaign_id')
        budget = request.data.get('budget')
        
        result = {
            'success': True,
            'campaign_id': campaign_id,
            'budget': budget,
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%S-05:00')
        }
        
        # Update the API call log with success
        api_diagnostic_tool.log_api_call(
            platform='GOOGLE',
            method='PUT',
            url=f"campaigns/{campaign_id}/budget",
            headers={},
            data=request.data,
            response_status=200,
            response_data=result
        )
        
        logger.info(f"Updated Google campaign budget: {campaign_id} -> {budget}")
        
        # Return successful response
        return APIResponse(
            request_id=request.id,
            success=True,
            status_code=200,
            data=result
        )
            
    def _execute_generic_request(self, request: APIRequest) -> APIResponse:
        """
        Execute a generic Google Ads API request for operations not specifically implemented.
        
        Args:
            request: The API request to execute
            
        Returns:
            API response object
        """
        try:
            # Map operations to service names
            service_mapping = {
                'campaign': 'CampaignService',
                'ad_group': 'AdGroupService',
                'ad': 'AdService',
                'keyword': 'KeywordPlanService',
                'creative': 'AdCreativeService',
                'report': 'ReportingService',
                'audience': 'AudienceService',
                'targeting': 'TargetingIdeaService'
            }
            
            # Extract service name and method from operation
            service_name = None
            method_name = None
            
            # Parse operation to determine service and method
            if '.' in request.operation:
                parts = request.operation.split('.')
                if len(parts) >= 2:
                    # Format is likely 'service.method'
                    service_prefix = parts[0].lower()
                    method_name = parts[1]
                    
                    # Find matching service
                    for key, service in service_mapping.items():
                        if service_prefix.startswith(key):
                            service_name = service
                            break
            else:
                # Try to infer from operation name
                for key, service in service_mapping.items():
                    if key in request.operation.lower():
                        service_name = service
                        
                        # Try to infer method
                        if request.method == 'GET':
                            if 'get' in request.operation.lower() or 'list' in request.operation.lower():
                                method_name = 'Get' if 'get' in request.operation.lower() else 'List'
                            else:
                                method_name = 'Get'  # Default for GET
                        elif request.method == 'POST':
                            if 'create' in request.operation.lower():
                                method_name = 'Create'
                            elif 'update' in request.operation.lower():
                                method_name = 'Update'
                            else:
                                method_name = 'Mutate'  # Default for POST
                        elif request.method == 'DELETE':
                            method_name = 'Remove'
                        break
                        
            # If we couldn't determine service or method, we can't process this request
            if not service_name or not method_name:
                return APIResponse(
                    request_id=request.id,
                    success=False,
                    status_code=400,
                    error=f"Couldn't determine Google Ads service and method for operation: {request.operation}"
                )
                
            # In a real implementation, we would get the appropriate service client
            # and call the method, e.g.:
            # service_client = self.client.get_service(service_name)
            # method = getattr(service_client, method_name)
            # response = method(request.data)
            
            # Log the API call attempt
            api_diagnostic_tool.log_api_call(
                platform='GOOGLE',
                method=request.method,
                url=f"GoogleAdsService.{service_name}.{method_name}",
                headers=request.headers or {},
                data=request.data,
                response_status=0,  # Will be updated after call
                response_data=None  # Will be updated after call
            )
            
            # For demonstration, we'll return a mock response
            if 'campaign' in service_name.lower():
                if 'get' in method_name.lower() or 'list' in method_name.lower():
                    mock_data = {
                        "campaigns": [
                            {
                                "resourceName": f"customers/{self.customer_id}/campaigns/{request.data.get('campaign_id', '1234')}",
                                "id": request.data.get('campaign_id', '1234'),
                                "name": "Simulated Google Ads Campaign",
                                "status": "ENABLED",
                                "advertisingChannelType": "SEARCH",
                                "servingStatus": "SERVING"
                            }
                        ]
                    }
                else:
                    mock_data = {
                        "results": [
                            {
                                "resourceName": f"customers/{self.customer_id}/campaigns/{request.data.get('campaign_id', '1234')}",
                                "campaignId": request.data.get('campaign_id', '1234'),
                                "status": "ENABLED"
                            }
                        ]
                    }
            elif 'report' in service_name.lower():
                mock_data = {
                    "reports": [
                        {
                            "campaignId": request.data.get('campaign_id', '1234'),
                            "metrics": {
                                "impressions": 12345,
                                "clicks": 678,
                                "conversions": 45,
                                "costMicros": 9876000  # In micro-units (millionths)
                            }
                        }
                    ]
                }
            else:
                mock_data = {
                    "results": [
                        {
                            "resourceName": f"customers/{self.customer_id}/{service_name.lower()}/{request.data.get('id', '5678')}",
                            "id": request.data.get('id', '5678'),
                            "status": "ENABLED"
                        }
                    ]
                }
                
            # Update the API call log with success
            api_diagnostic_tool.log_api_call(
                platform='GOOGLE',
                method=request.method,
                url=f"GoogleAdsService.{service_name}.{method_name}",
                headers=request.headers or {},
                data=request.data,
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
            error_msg = f"Error executing generic Google Ads request: {str(e)}"
            logger.error(error_msg)
            
            # Update the API call log with error
            api_diagnostic_tool.log_api_call(
                platform='GOOGLE',
                method=request.method if hasattr(request, 'method') else 'UNKNOWN',
                url=f"GoogleAdsService.{service_name}.{method_name}" if 'service_name' in locals() and 'method_name' in locals() else 'unknown',
                headers=request.headers or {},
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
    def create_campaign_request(self, name: str, budget: float, 
                              status: str = 'PAUSED') -> APIRequest:
        """
        Create an API request for campaign creation.
        
        Args:
            name: Campaign name
            budget: Daily budget in account currency
            status: Campaign status ('ENABLED', 'PAUSED')
            
        Returns:
            API request object
        """
        data = {
            'name': name,
            'budget': budget,
            'status': status
        }
        
        return APIRequest(
            method='POST',
            endpoint='campaigns',
            data=data,
            platform='GOOGLE',
            operation='create_campaign'
        )
        
    def create_ad_group_request(self, campaign_id: str, name: str,
                              status: str = 'PAUSED') -> APIRequest:
        """
        Create an API request for ad group creation.
        
        Args:
            campaign_id: ID of the campaign to add the ad group to
            name: Ad group name
            status: Ad group status ('ENABLED', 'PAUSED')
            
        Returns:
            API request object
        """
        data = {
            'campaign_id': campaign_id,
            'name': name,
            'status': status
        }
        
        return APIRequest(
            method='POST',
            endpoint='ad_groups',
            data=data,
            platform='GOOGLE',
            operation='create_ad_group'
        )
        
    def create_responsive_search_ad_request(self, ad_group_id: str, headlines: List[str],
                                          descriptions: List[str], final_url: str,
                                          status: str = 'PAUSED') -> APIRequest:
        """
        Create an API request for responsive search ad creation.
        
        Args:
            ad_group_id: ID of the ad group to add the ad to
            headlines: List of headlines (3-15 required)
            descriptions: List of descriptions (2-4 required)
            final_url: Landing page URL
            status: Ad status ('ENABLED', 'PAUSED')
            
        Returns:
            API request object
        """
        data = {
            'ad_group_id': ad_group_id,
            'headlines': headlines,
            'descriptions': descriptions,
            'final_url': final_url,
            'status': status
        }
        
        return APIRequest(
            method='POST',
            endpoint='responsive_search_ads',
            data=data,
            platform='GOOGLE',
            operation='create_responsive_search_ad'
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
            platform='GOOGLE',
            operation='get_campaign_stats',
            cacheable=True  # This request can be cached
        )
        
    def create_location_targeting_request(self, campaign_id: str, 
                                        locations: List[str]) -> APIRequest:
        """
        Create an API request for location targeting creation.
        
        Args:
            campaign_id: ID of the campaign
            locations: List of location criteria (country codes, cities, etc.)
            
        Returns:
            API request object
        """
        data = {
            'campaign_id': campaign_id,
            'locations': locations
        }
        
        return APIRequest(
            method='POST',
            endpoint='campaign_location_targets',
            data=data,
            platform='GOOGLE',
            operation='create_location_targeting'
        )
        
    def create_demographic_targeting_request(self, ad_group_id: str,
                                           criteria: Dict[str, Any]) -> APIRequest:
        """
        Create an API request for demographic targeting creation.
        
        Args:
            ad_group_id: ID of the ad group
            criteria: Demographic criteria
            
        Returns:
            API request object
        """
        data = {
            'ad_group_id': ad_group_id,
            'criteria': criteria
        }
        
        return APIRequest(
            method='POST',
            endpoint='ad_group_demographic_targets',
            data=data,
            platform='GOOGLE',
            operation='create_demographic_targeting'
        )
        
    def create_keyword_targeting_request(self, ad_group_id: str, keywords: List[str],
                                       match_type: str = 'BROAD') -> APIRequest:
        """
        Create an API request for keyword targeting creation.
        
        Args:
            ad_group_id: ID of the ad group
            keywords: List of keywords to target
            match_type: Keyword match type ('BROAD', 'PHRASE', 'EXACT')
            
        Returns:
            API request object
        """
        data = {
            'ad_group_id': ad_group_id,
            'keywords': keywords,
            'match_type': match_type
        }
        
        return APIRequest(
            method='POST',
            endpoint='ad_group_keywords',
            data=data,
            platform='GOOGLE',
            operation='create_keyword_targeting'
        )
        
    def update_campaign_status_request(self, campaign_id: str, status: str) -> APIRequest:
        """
        Create an API request for updating campaign status.
        
        Args:
            campaign_id: ID of the campaign
            status: New status ('ENABLED', 'PAUSED', 'REMOVED')
            
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
            platform='GOOGLE',
            operation='update_campaign_status'
        )
        
    def update_budget_request(self, campaign_id: str, budget: float) -> APIRequest:
        """
        Create an API request for updating campaign budget.
        
        Args:
            campaign_id: ID of the campaign
            budget: New daily budget in account currency
            
        Returns:
            API request object
        """
        data = {
            'campaign_id': campaign_id,
            'budget': budget
        }
        
        return APIRequest(
            method='PUT',
            endpoint=f"campaigns/{campaign_id}/budget",
            data=data,
            platform='GOOGLE',
            operation='update_budget'
        )