"""
Utility functions for standardizing API responses.

This module provides helper functions to ensure consistent response format
across all API endpoints in the application.
"""
from flask import jsonify
from typing import Any, Dict, List, Optional, Union


def api_success(data: Any = None, message: Optional[str] = None, status_code: int = 200) -> tuple:
    """
    Create a standardized success response.
    
    Args:
        data: The data to include in the response
        message: Optional success message
        status_code: HTTP status code (default: 200)
        
    Returns:
        tuple: (jsonified response, status code)
    """
    response = {
        'success': True
    }
    
    if data is not None:
        response['data'] = data
        
    if message:
        response['message'] = message
        
    return jsonify(response), status_code


def api_error(message: str, errors: Optional[List[Dict[str, Any]]] = None, status_code: int = 400) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        errors: Optional list of specific errors
        status_code: HTTP status code (default: 400)
        
    Returns:
        tuple: (jsonified response, status code)
    """
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
        
    return jsonify(response), status_code


def paginated_response(
    data: List[Any], 
    total: int, 
    page: int, 
    per_page: int, 
    message: Optional[str] = None
) -> tuple:
    """
    Create a standardized paginated response.
    
    Args:
        data: The data for the current page
        total: Total number of items
        page: Current page number
        per_page: Number of items per page
        message: Optional success message
        
    Returns:
        tuple: (jsonified response, status code)
    """
    response = {
        'success': True,
        'data': data,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page  # Ceiling division
        }
    }
    
    if message:
        response['message'] = message
        
    return jsonify(response), 200