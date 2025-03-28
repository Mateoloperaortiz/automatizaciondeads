"""
Utility modules for the MagnetoCursor application.

This package provides various utility functions and helpers used throughout the application.
"""

# Allow importing API response utilities directly from utils package
try:
    from app.utils.api_responses import api_success, api_error, paginated_response
    __all__ = ['api_success', 'api_error', 'paginated_response']
except ImportError:
    # Handle the case where api_responses might not be imported yet
    __all__ = []