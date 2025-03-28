"""
Real-time utilities for WebSocket integration
"""

import functools
import logging
from flask import g, request, current_app
from app.tasks.notification_tasks import send_entity_update_notification

logger = logging.getLogger('realtime')

def broadcast_entity_change(entity_type, get_entity_id=None, get_entity_data=None):
    """
    Decorator to broadcast entity changes via WebSocket after API operations.
    
    Args:
        entity_type (str): Type of entity (campaign, segment, etc.)
        get_entity_id (callable, optional): Function to extract entity ID from response
        get_entity_data (callable, optional): Function to extract entity data from response
    
    Returns:
        function: Decorated function
    
    Usage:
        @broadcast_entity_change('campaign', 
            get_entity_id=lambda resp: resp.get('id'),
            get_entity_data=lambda resp: resp)
        def create_campaign():
            # Your function implementation
            return {'id': 123, 'name': 'New Campaign'}
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Call original function
            response = func(*args, **kwargs)
            
            try:
                # Determine update type based on HTTP method
                method = request.method.upper()
                if method == 'POST':
                    update_type = 'created'
                elif method == 'PUT' or method == 'PATCH':
                    update_type = 'updated'
                elif method == 'DELETE':
                    update_type = 'deleted'
                else:
                    # Don't broadcast for GET requests
                    return response
                
                # Get entity ID from response using provided function or fallback methods
                entity_id = None
                
                if get_entity_id:
                    # Use provided function to extract ID
                    entity_id = get_entity_id(response)
                elif isinstance(response, dict):
                    # Try common keys
                    for key in ['id', 'entity_id', f'{entity_type}_id']:
                        if key in response:
                            entity_id = response[key]
                            break
                
                # If we couldn't determine entity ID, try to get from URL
                if entity_id is None:
                    # Check if URL contains ID
                    path_parts = request.path.strip('/').split('/')
                    for i, part in enumerate(path_parts):
                        if part == entity_type or part == f'{entity_type}s':
                            if i + 1 < len(path_parts) and path_parts[i + 1].isdigit():
                                entity_id = int(path_parts[i + 1])
                                break
                
                # If we still can't determine entity ID, don't broadcast
                if entity_id is None:
                    logger.warning(f"Could not determine entity ID for {entity_type} broadcast")
                    return response
                
                # Get entity data from response using provided function or fallback
                entity_data = None
                
                if get_entity_data:
                    # Use provided function to extract data
                    entity_data = get_entity_data(response)
                elif isinstance(response, dict):
                    # Use the entire response as entity data
                    entity_data = response
                else:
                    # Create minimal entity data
                    entity_data = {'id': entity_id}
                
                # Get user ID from session if available
                user_id = None
                if hasattr(g, 'user') and hasattr(g.user, 'id'):
                    user_id = g.user.id
                
                # Queue the notification task
                send_entity_update_notification.delay(
                    entity_type=entity_type, 
                    entity_id=entity_id,
                    update_type=update_type,
                    entity_data=entity_data,
                    user_id=user_id
                )
                
                logger.info(f"Queued {entity_type} {update_type} notification for entity {entity_id}")
                
            except Exception as e:
                # Log error but don't affect the API response
                logger.error(f"Error broadcasting entity change: {str(e)}")
            
            # Return original response regardless of broadcasting success
            return response
        
        return wrapper
    
    return decorator

def entity_changed(entity_type, entity_id, update_type, entity_data=None):
    """
    Manually trigger an entity change broadcast.
    
    Args:
        entity_type (str): Type of entity (campaign, segment, etc.)
        entity_id (int): ID of the entity
        update_type (str): Type of update (created, updated, deleted, etc.)
        entity_data (dict, optional): Entity data to broadcast
        
    Returns:
        bool: True if broadcast was queued successfully
    """
    try:
        # Default entity data if not provided
        if entity_data is None:
            entity_data = {'id': entity_id}
        
        # Get user ID from session if available
        user_id = None
        if hasattr(g, 'user') and hasattr(g.user, 'id'):
            user_id = g.user.id
        
        # Queue the notification task
        send_entity_update_notification.delay(
            entity_type=entity_type,
            entity_id=entity_id,
            update_type=update_type,
            entity_data=entity_data,
            user_id=user_id
        )
        
        logger.info(f"Manually triggered {entity_type} {update_type} notification for entity {entity_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error manually triggering entity change: {str(e)}")
        return False