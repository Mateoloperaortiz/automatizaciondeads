"""
API debugging and diagnostics utilities.

This module provides tools for debugging API issues, diagnosing
credential problems, and assisting with API integration.
"""
import json
import logging
import platform
import requests
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from .credentials import credential_manager
from .secure_storage import get_secure_storage

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEBUG_STORAGE_KEY = 'api_debug_logs'
MAX_DEBUG_LOGS = 100
MAX_LOG_AGE_DAYS = 7

# Create temporary secure storage for debug logs
debug_storage = get_secure_storage(storage_type='temp', use_encryption=True)


class APIDiagnosticTool:
    """
    Tool for diagnosing API integration issues.
    
    This class provides utilities for testing API connections,
    validating credentials, and logging API calls for debugging.
    """
    
    def __init__(self):
        """Initialize the API diagnostic tool."""
        self.session = requests.Session()
        self.init_session()
    
    def init_session(self):
        """Initialize the HTTP session with appropriate headers."""
        app_version = '1.0.0'
        user_agent = f"MagnetoCursor/{app_version} ({platform.system()}; {platform.release()}; Python/{platform.python_version()})"
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'X-Diagnostic-Tool': 'true'
        })
    
    def log_api_call(self, platform: str, method: str, url: str, 
                     headers: Dict[str, str], data: Any, 
                     response_status: int, response_data: Any,
                     error: Optional[str] = None):
        """
        Log an API call for diagnostic purposes.
        
        Args:
            platform: API platform (META, GOOGLE, TWITTER)
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            headers: Request headers (sensitive values masked)
            data: Request data
            response_status: HTTP status code
            response_data: Response data
            error: Error message if any
        """
        # Mask sensitive values in headers
        masked_headers = self._mask_sensitive_headers(headers)
        
        # Create log entry
        log_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'platform': platform,
            'method': method,
            'url': url,
            'headers': masked_headers,
            'data': self._mask_sensitive_data(data),
            'response': {
                'status': response_status,
                'data': response_data
            },
            'error': error
        }
        
        # Get existing logs or create new
        logs = debug_storage.get(DEBUG_STORAGE_KEY, [])
        
        # Add new log
        logs.append(log_entry)
        
        # Limit number of logs
        if len(logs) > MAX_DEBUG_LOGS:
            logs = logs[-MAX_DEBUG_LOGS:]
        
        # Store updated logs
        debug_storage.set(DEBUG_STORAGE_KEY, logs)
        
        # Log to main logger too
        logger.debug(f"API Call [{platform}] {method} {url} - Status: {response_status}")
        if error:
            logger.error(f"API Error [{platform}]: {error}")
    
    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Mask sensitive values in headers.
        
        Args:
            headers: Request headers
            
        Returns:
            Headers with sensitive values masked
        """
        sensitive_headers = ['authorization', 'x-access-token', 'api-key']
        masked_headers = {}
        
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                masked_headers[key] = '********'
            else:
                masked_headers[key] = value
        
        return masked_headers
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """
        Mask sensitive values in request data.
        
        Args:
            data: Request data
            
        Returns:
            Data with sensitive values masked
        """
        if not data:
            return data
        
        if isinstance(data, dict):
            masked_data = {}
            sensitive_keys = ['access_token', 'token', 'secret', 'password', 'key']
            
            for key, value in data.items():
                if any(s in key.lower() for s in sensitive_keys):
                    masked_data[key] = '********'
                elif isinstance(value, (dict, list)):
                    masked_data[key] = self._mask_sensitive_data(value)
                else:
                    masked_data[key] = value
            
            return masked_data
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        else:
            return data
    
    def get_logs(self, platform: Optional[str] = None, 
                limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get diagnostic logs for review.
        
        Args:
            platform: Filter logs by platform (optional)
            limit: Maximum number of logs to return
            
        Returns:
            List of diagnostic logs
        """
        logs = debug_storage.get(DEBUG_STORAGE_KEY, [])
        
        # Filter by platform if specified
        if platform:
            logs = [log for log in logs if log['platform'] == platform]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit number of logs
        return logs[:limit]
    
    def clear_logs(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear diagnostic logs.
        
        Args:
            platform: Clear logs only for this platform (optional)
            
        Returns:
            Result of the operation
        """
        if platform:
            logs = debug_storage.get(DEBUG_STORAGE_KEY, [])
            filtered_logs = [log for log in logs if log['platform'] != platform]
            debug_storage.set(DEBUG_STORAGE_KEY, filtered_logs)
            return {
                'success': True,
                'platform': platform,
                'cleared': len(logs) - len(filtered_logs)
            }
        else:
            debug_storage.set(DEBUG_STORAGE_KEY, [])
            return {
                'success': True,
                'cleared': 'all'
            }
    
    def test_meta_api_connection(self) -> Dict[str, Any]:
        """
        Test connection to Meta Graph API.
        
        Returns:
            Test result
        """
        meta_credentials = credential_manager.get_credentials('META')
        token = meta_credentials.get('META_ACCESS_TOKEN')
        
        if not token:
            return {
                'success': False,
                'error': 'Missing Meta access token'
            }
        
        try:
            # Prepare request
            url = 'https://graph.facebook.com/v16.0/me'
            headers = {
                'Accept': 'application/json'
            }
            params = {
                'access_token': token,
                'fields': 'id,name'
            }
            
            # Make request
            # Note: In real implementation, make the actual request
            # response = self.session.get(url, headers=headers, params=params)
            
            # For this PoC, simulate response
            simulated_response = {
                'status_code': 200,
                'json': lambda: {'id': '12345', 'name': 'Test User'}
            }
            response = simulated_response
            
            # Log the API call
            self.log_api_call(
                platform='META',
                method='GET',
                url=url,
                headers=headers,
                data=params,
                response_status=response['status_code'],
                response_data=response['json']()
            )
            
            # Parse response
            if response['status_code'] == 200:
                return {
                    'success': True,
                    'user': response['json']()
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned {response['status_code']}",
                    'details': response['json']()
                }
        except Exception as e:
            self.log_api_call(
                platform='META',
                method='GET',
                url=url,
                headers=headers,
                data=params,
                response_status=0,
                response_data=None,
                error=str(e)
            )
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_twitter_api_connection(self) -> Dict[str, Any]:
        """
        Test connection to Twitter API.
        
        Returns:
            Test result
        """
        twitter_credentials = credential_manager.get_credentials('TWITTER')
        bearer_token = twitter_credentials.get('X_BEARER_TOKEN')
        
        if not bearer_token:
            return {
                'success': False,
                'error': 'Missing Twitter bearer token'
            }
        
        try:
            # Prepare request
            url = 'https://api.twitter.com/2/users/me'
            headers = {
                'Authorization': f"Bearer {bearer_token}",
                'Accept': 'application/json'
            }
            
            # Make request
            # Note: In real implementation, make the actual request
            # response = self.session.get(url, headers=headers)
            
            # For this PoC, simulate response
            simulated_response = {
                'status_code': 200,
                'json': lambda: {'data': {'id': '12345', 'name': 'Test User'}}
            }
            response = simulated_response
            
            # Log the API call
            self.log_api_call(
                platform='TWITTER',
                method='GET',
                url=url,
                headers=headers,
                data=None,
                response_status=response['status_code'],
                response_data=response['json']()
            )
            
            # Parse response
            if response['status_code'] == 200:
                return {
                    'success': True,
                    'user': response['json']()['data']
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned {response['status_code']}",
                    'details': response['json']()
                }
        except Exception as e:
            self.log_api_call(
                platform='TWITTER',
                method='GET',
                url=url,
                headers=headers,
                data=None,
                response_status=0,
                response_data=None,
                error=str(e)
            )
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_google_api_connection(self) -> Dict[str, Any]:
        """
        Test connection to Google API.
        
        Returns:
            Test result
        """
        # Google API authentication is more complex and requires OAuth
        # This is a simplified simulation for the PoC
        google_credentials = credential_manager.get_credentials('GOOGLE')
        refresh_token = google_credentials.get('GOOGLE_REFRESH_TOKEN')
        
        if not refresh_token:
            return {
                'success': False,
                'error': 'Missing Google refresh token'
            }
        
        try:
            # Simulate a successful response
            return {
                'success': True,
                'user': {
                    'email': 'test@example.com',
                    'verified': True
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_all_connections(self) -> Dict[str, Any]:
        """
        Test connections to all APIs.
        
        Returns:
            Test results for all platforms
        """
        return {
            'META': self.test_meta_api_connection(),
            'TWITTER': self.test_twitter_api_connection(),
            'GOOGLE': self.test_google_api_connection()
        }
    
    def get_api_diagnostics(self) -> Dict[str, Any]:
        """
        Get comprehensive API diagnostics.
        
        Returns:
            Diagnostic information for all platforms
        """
        return {
            'credentials': {
                'META': {
                    'configured': credential_manager.is_configured('META'),
                    'credentials': {
                        key: credential_manager.mask_value(value)
                        for key, value in credential_manager.get_credentials('META').items()
                    }
                },
                'TWITTER': {
                    'configured': credential_manager.is_configured('TWITTER'),
                    'credentials': {
                        key: credential_manager.mask_value(value)
                        for key, value in credential_manager.get_credentials('TWITTER').items()
                    }
                },
                'GOOGLE': {
                    'configured': credential_manager.is_configured('GOOGLE'),
                    'credentials': {
                        key: credential_manager.mask_value(value)
                        for key, value in credential_manager.get_credentials('GOOGLE').items()
                    }
                }
            },
            'connection_tests': self.test_all_connections(),
            'recent_logs': {
                'META': self.get_logs(platform='META', limit=5),
                'TWITTER': self.get_logs(platform='TWITTER', limit=5),
                'GOOGLE': self.get_logs(platform='GOOGLE', limit=5)
            }
        }


# Create a global instance of the API diagnostic tool
api_diagnostic_tool = APIDiagnosticTool()


def test_api_connections() -> Dict[str, Any]:
    """
    Convenience function to test all API connections.
    
    Returns:
        Test results for all platforms
    """
    return api_diagnostic_tool.test_all_connections()


def get_api_logs(platform: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Convenience function to get API diagnostic logs.
    
    Args:
        platform: Filter logs by platform (optional)
        limit: Maximum number of logs to return
        
    Returns:
        List of diagnostic logs
    """
    return api_diagnostic_tool.get_logs(platform, limit)