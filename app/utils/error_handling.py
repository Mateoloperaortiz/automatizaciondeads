"""
Standardized error handling for the MagnetoCursor application.

This module provides consistent error handling patterns, custom exceptions,
and decorators for standardizing error responses across the application.
"""

import logging
import functools
import traceback
from typing import Dict, Any, Optional, List, Callable, Type, Union
from flask import jsonify, Response

logger = logging.getLogger(__name__)

# Base Exception Classes
class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 500, 
               platform: str = None, details: Any = None):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            platform: Platform that raised the error
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.platform = platform
        self.details = details
        super().__init__(self.message)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        error_dict = {
            'success': False,
            'error': self.message,
            'status_code': self.status_code
        }
        
        if self.platform:
            error_dict['platform'] = self.platform
            
        if self.details:
            error_dict['details'] = self.details
            
        return error_dict
        
    def to_response(self) -> Response:
        """Convert error to a Flask response."""
        return jsonify(self.to_dict()), self.status_code

# Specific API Exceptions
class ValidationError(APIError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Any = None):
        """Initialize validation error."""
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(APIError):
    """Exception for authentication errors."""
    
    def __init__(self, message: str, platform: str = None):
        """Initialize authentication error."""
        super().__init__(message, status_code=401, platform=platform)

class AuthorizationError(APIError):
    """Exception for authorization errors."""
    
    def __init__(self, message: str, platform: str = None):
        """Initialize authorization error."""
        super().__init__(message, status_code=403, platform=platform)

class ResourceNotFoundError(APIError):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str, resource_type: str = None):
        """Initialize resource not found error."""
        details = {'resource_type': resource_type} if resource_type else None
        super().__init__(message, status_code=404, details=details)

class RateLimitError(APIError):
    """Exception for rate limit errors."""
    
    def __init__(self, message: str, platform: str = None, retry_after: int = None):
        """Initialize rate limit error."""
        details = {'retry_after': retry_after} if retry_after else None
        super().__init__(message, status_code=429, platform=platform, details=details)

class ConfigurationError(APIError):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, component: str = None):
        """Initialize configuration error."""
        details = {'component': component} if component else None
        super().__init__(message, status_code=500, details=details)

class ServiceUnavailableError(APIError):
    """Exception for service unavailable errors."""
    
    def __init__(self, message: str, platform: str = None):
        """Initialize service unavailable error."""
        super().__init__(message, status_code=503, platform=platform)

class APIClientError(APIError):
    """Exception for API client errors."""
    
    def __init__(self, message: str, platform: str, original_error: Exception = None):
        """Initialize API client error."""
        details = {'original_error': str(original_error)} if original_error else None
        super().__init__(message, status_code=500, platform=platform, details=details)

# Decorators
def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle API errors consistently.
    
    This decorator catches exceptions and converts them to standardized
    API responses. For use with Flask routes.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            # Log API errors
            logger.error(f"API Error ({e.__class__.__name__}): {e.message}")
            return e.to_response()
        except Exception as e:
            # Log unexpected errors
            logger.exception(f"Unexpected error: {str(e)}")
            error = APIError("An unexpected error occurred", 500, details=str(e))
            return error.to_response()
    
    return wrapper

def handle_exceptions(func: Callable) -> Callable:
    """
    General purpose exception handler for WebSocket and background tasks.
    
    This decorator catches all exceptions and logs them, but doesn't
    convert them to responses like handle_api_errors.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the exception
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            # Re-raise the exception for proper error handling
            raise
    
    return wrapper

def with_error_handling(func: Callable) -> Callable:
    """
    Decorator to handle errors for services and non-Flask functions.
    
    This decorator catches exceptions and converts them to standard dicts 
    with success/error fields.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If result is already a dict with success/error keys, leave it
            if isinstance(result, dict) and 'success' in result:
                return result
                
            # Otherwise, wrap the result in a success dict
            return {
                'success': True,
                'data': result
            }
        except APIError as e:
            # Log API errors
            logger.error(f"API Error ({e.__class__.__name__}): {e.message}")
            return e.to_dict()
        except Exception as e:
            # Log unexpected errors
            logger.exception(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }
    
    return wrapper

# Utility Functions
def format_exception(e: Exception) -> Dict[str, Any]:
    """
    Format an exception into a standardized dictionary.
    
    Args:
        e: The exception to format
        
    Returns:
        A dictionary with error details
    """
    if isinstance(e, APIError):
        return e.to_dict()
    
    return {
        'success': False,
        'error': str(e),
        'status_code': 500,
        'error_type': e.__class__.__name__
    }
    
def log_and_raise(error_message: str, 
                exception_class: Type[APIError] = APIError, 
                log_level: str = 'error',
                **kwargs):
    """
    Log an error and raise an exception.
    
    Args:
        error_message: Message to log and include in exception
        exception_class: Exception class to raise
        log_level: Logging level ('debug', 'info', 'warning', 'error', 'critical')
        **kwargs: Additional arguments to pass to the exception
        
    Raises:
        The specified exception class
    """
    # Log the error
    log_func = getattr(logger, log_level)
    log_func(error_message)
    
    # Raise the exception
    raise exception_class(error_message, **kwargs)

# Factory function to convert various error types to API errors
def convert_to_api_error(e: Exception, platform: str = None) -> APIError:
    """
    Convert various exceptions to appropriate APIError subclasses.
    
    Args:
        e: Exception to convert
        platform: API platform name
        
    Returns:
        An appropriate APIError subclass
    """
    # Already an APIError
    if isinstance(e, APIError):
        return e
        
    # Map common exception types to appropriate API errors
    error_text = str(e)
    error_name = e.__class__.__name__
    
    if error_name == 'ValidationError' or 'validation' in error_text.lower():
        return ValidationError(error_text)
    elif 'not found' in error_text.lower() or 'no such' in error_text.lower():
        return ResourceNotFoundError(error_text)
    elif 'permission' in error_text.lower() or 'not allowed' in error_text.lower():
        return AuthorizationError(error_text, platform)
    elif 'authenticate' in error_text.lower() or 'unauthorized' in error_text.lower():
        return AuthenticationError(error_text, platform)
    elif 'rate limit' in error_text.lower() or 'too many requests' in error_text.lower():
        return RateLimitError(error_text, platform)
    elif 'unavailable' in error_text.lower() or 'temporarily' in error_text.lower():
        return ServiceUnavailableError(error_text, platform)
    else:
        # Default to generic API error
        return APIError(error_text, platform=platform)