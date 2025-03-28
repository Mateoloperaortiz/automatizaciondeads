"""
Base classes for the API Integration Framework.

This module defines the core abstractions used throughout the framework:
- APIRequest: A standardized request object
- APIResponse: A standardized response object
- BaseAPIClient: An abstract base class for API clients
"""

import abc
import time
import uuid
import logging
from typing import Dict, Any, Optional, List, Union, Type, TypeVar
from app.utils.error_handling import APIError, APIClientError

# Configure logging
logger = logging.getLogger(__name__)

# Type variables for generic typing
T = TypeVar('T')
RequestParams = Dict[str, Any]


class APIRequest:
    """
    Standardized API request object.
    
    This class encapsulates all information needed to make an API request,
    providing a consistent interface across different API implementations.
    """
    
    def __init__(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        platform: Optional[str] = None,
        operation: Optional[str] = None,
        cacheable: bool = False
    ):
        """
        Initialize a new API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint or path
            params: Query parameters
            data: Request body data
            headers: Request headers
            timeout: Request timeout in seconds
            platform: API platform identifier (e.g., META, TWITTER)
            operation: Operation name (e.g., create_campaign)
            cacheable: Whether this request can be cached
        """
        self.id = str(uuid.uuid4())
        self.method = method.upper()
        self.endpoint = endpoint
        self.params = params or {}
        self.data = data or {}
        self.headers = headers or {}
        self.timeout = timeout
        self.platform = platform
        self.operation = operation
        self.cacheable = cacheable
        self.created_at = time.time()
        
    def get_cache_key(self) -> str:
        """
        Generate a cache key for this request.
        
        The cache key is based on the method, endpoint, and serialized parameters.
        Only applicable for GET requests by default.
        
        Returns:
            A unique string to use as a cache key
        """
        if not self.cacheable or self.method != 'GET':
            return ""
            
        # Create a deterministic representation of the parameters
        param_str = "&".join(f"{k}={v}" for k, v in sorted(self.params.items()))
        return f"{self.platform}:{self.endpoint}:{param_str}"
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the request to a dictionary.
        
        Returns:
            Dictionary representation of the request
        """
        return {
            'id': self.id,
            'method': self.method,
            'endpoint': self.endpoint,
            'params': self.params,
            'data': self.data,
            'headers': self.headers,
            'timeout': self.timeout,
            'platform': self.platform,
            'operation': self.operation,
            'cacheable': self.cacheable,
            'created_at': self.created_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIRequest':
        """
        Create a request from a dictionary.
        
        Args:
            data: Dictionary containing request data
            
        Returns:
            New APIRequest instance
        """
        instance = cls(
            method=data['method'],
            endpoint=data['endpoint'],
            params=data.get('params'),
            data=data.get('data'),
            headers=data.get('headers'),
            timeout=data.get('timeout', 30),
            platform=data.get('platform'),
            operation=data.get('operation'),
            cacheable=data.get('cacheable', False)
        )
        
        instance.id = data.get('id', instance.id)
        instance.created_at = data.get('created_at', instance.created_at)
        
        return instance


class APIResponse:
    """
    Standardized API response object.
    
    This class encapsulates all information returned from an API request,
    providing a consistent interface across different API implementations.
    """
    
    def __init__(
        self,
        request_id: str,
        success: bool,
        status_code: Optional[int] = None,
        data: Any = None,
        error: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timing: Optional[float] = None
    ):
        """
        Initialize a new API response.
        
        Args:
            request_id: ID of the associated request
            success: Whether the request was successful
            status_code: HTTP status code, if applicable
            data: Response data
            error: Error message, if any
            headers: Response headers
            timing: Request-response time in seconds
        """
        self.request_id = request_id
        self.success = success
        self.status_code = status_code
        self.data = data
        self.error = error
        self.headers = headers or {}
        self.timing = timing
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response to a dictionary.
        
        Returns:
            Dictionary representation of the response
        """
        return {
            'request_id': self.request_id,
            'success': self.success,
            'status_code': self.status_code,
            'data': self.data,
            'error': self.error,
            'headers': self.headers,
            'timing': self.timing,
            'timestamp': self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIResponse':
        """
        Create a response from a dictionary.
        
        Args:
            data: Dictionary containing response data
            
        Returns:
            New APIResponse instance
        """
        instance = cls(
            request_id=data['request_id'],
            success=data['success'],
            status_code=data.get('status_code'),
            data=data.get('data'),
            error=data.get('error'),
            headers=data.get('headers'),
            timing=data.get('timing')
        )
        
        instance.timestamp = data.get('timestamp', instance.timestamp)
        
        return instance


class BaseAPIClient(abc.ABC):
    """
    Abstract base class for API clients.
    
    This class defines the interface that all API clients must implement,
    ensuring consistent behavior across different platform integrations.
    """
    
    def __init__(self, platform_name: str, credentials: Dict[str, str]):
        """
        Initialize the API client.
        
        Args:
            platform_name: Name of the platform (e.g., META, TWITTER)
            credentials: Dictionary of credentials for the platform
        """
        self.platform_name = platform_name
        self.credentials = credentials
        self.cache = None  # Will be set by implementations if caching is used
        self.metrics = None  # Will be set by implementations if metrics tracking is used
        self.is_initialized = False
        
    @abc.abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the API client with credentials.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
        
    @abc.abstractmethod
    def execute_request(self, request: APIRequest) -> APIResponse:
        """
        Execute an API request.
        
        Args:
            request: The API request to execute
            
        Returns:
            API response object
        """
        pass
        
    def execute_requests(self, requests: List[APIRequest]) -> List[APIResponse]:
        """
        Execute multiple API requests, potentially in parallel.
        
        Implementations may override this to provide batch processing or
        parallel execution optimizations.
        
        Args:
            requests: List of API requests to execute
            
        Returns:
            List of API responses
        """
        # Default implementation: process sequentially
        return [self.execute_request(request) for request in requests]
        
    def get_from_cache(self, request: APIRequest) -> Optional[APIResponse]:
        """
        Try to get a response from the cache.
        
        Args:
            request: The API request
            
        Returns:
            Cached response if available, None otherwise
        """
        if not self.cache or not request.cacheable:
            return None
            
        cache_key = request.get_cache_key()
        if not cache_key:
            return None
            
        return self.cache.get(cache_key)
        
    def save_to_cache(self, request: APIRequest, response: APIResponse) -> None:
        """
        Save a response to the cache.
        
        Args:
            request: The API request
            response: The API response to cache
        """
        if not self.cache or not request.cacheable or not response.success:
            return
            
        cache_key = request.get_cache_key()
        if not cache_key:
            return
            
        self.cache.set(cache_key, response)
        
    def track_metrics(self, request: APIRequest, response: APIResponse) -> None:
        """
        Track metrics for a request-response pair.
        
        Args:
            request: The API request
            response: The API response
        """
        if not self.metrics:
            return
            
        self.metrics.record(request, response)
        
    def clear_cache(self) -> None:
        """Clear the cache for this client."""
        if self.cache:
            self.cache.clear()
            
    def validate_request(self, request: APIRequest) -> Optional[str]:
        """
        Validate an API request.
        
        Args:
            request: The API request to validate
            
        Returns:
            Error message if validation fails, None otherwise
        """
        if request.platform and request.platform != self.platform_name:
            return f"Platform mismatch: {request.platform} vs {self.platform_name}"
            
        if not request.endpoint:
            return "Missing endpoint"
            
        return None