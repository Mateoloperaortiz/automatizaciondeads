from flask import Blueprint, current_app, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user, login_required
import json
import logging
import zlib
import base64
import time
import copy
from collections import defaultdict
from threading import Lock
from datetime import datetime
from app.utils.error_handling import handle_exceptions
from app.models.notification import NotificationCategory
from app.services.websocket_analytics_service import websocket_analytics
from app.services.websocket_auth import websocket_auth
from app.services.websocket_permissions import websocket_permissions
from app.services.websocket_rate_limiter import websocket_rate_limiter

# Initialize SocketIO with the app later
socketio = SocketIO()

# Create blueprint for HTTP API endpoints related to WebSocket
websocket_bp = Blueprint('websocket', __name__, url_prefix='/api/websocket')

# Dictionary to store active subscribers by entity
# Format: {entity_type: {entity_id: set(session_ids)}}
entity_subscribers = {}

# Dictionary to store session info
# Format: {session_id: {user_id: id, subscriptions: set(entity_keys)}}
session_info = {}

# Message batching system
# Format: {session_id: [message1, message2, ...]}
message_batches = defaultdict(list)
message_batch_lock = Lock()
message_batch_timer = None

# Default batch interval: 100ms
DEFAULT_BATCH_INTERVAL = 0.1

# Entity type-specific batch intervals (in seconds)
BATCH_INTERVALS = {
    'analytics': 0.25,      # 250ms for analytics (high frequency, lower priority)
    'notification': 0.05,   # 50ms for notifications (important, deliver quickly)
    'task': 0.2,            # 200ms for tasks (high frequency, lower priority)
    'campaign': 0.1,        # 100ms for campaigns (medium frequency)
    'segment': 0.1,         # 100ms for segments (medium frequency)
    'job_opening': 0.05,    # 50ms for job openings (low frequency, deliver quickly)
    'default': DEFAULT_BATCH_INTERVAL
}

# Adaptive batching settings
MIN_BATCH_INTERVAL = 0.02   # 20ms minimum
MAX_BATCH_INTERVAL = 0.5    # 500ms maximum
BATCH_LOAD_THRESHOLD = 100  # Messages per second threshold for adaptive batching

# Compression settings
# Don't compress payloads smaller than 1KB
MIN_COMPRESSION_SIZE = 1024
# Use zlib compression level 6 (balance between speed and compression ratio)
COMPRESSION_LEVEL = 6

# Performance monitoring
message_stats = {
    'total_messages_sent': 0,
    'compressed_messages': 0,
    'batched_messages': 0,
    'total_bytes_sent': 0,
    'total_bytes_saved': 0,
    'last_reset': time.time()
}

# Logger for WebSocket events
logger = logging.getLogger('websocket')

@socketio.on('connect')
def handle_connect():
    """Handle client connection with authentication and rate limiting."""
    session_id = request.sid
    
    # Get client IP for rate limiting
    client_ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')
    
    # Check rate limit for connections
    allowed, retry_after = websocket_rate_limiter.check_rate_limit('connection', ip=client_ip)
    if not allowed:
        logger.warning(f"Connection rate limited for IP {client_ip}")
        websocket_analytics.record_stat('rate_limited_connections', 1)
        return False  # Reject connection
    
    # Authenticate using token
    user_data = websocket_auth.authenticate_socket(request)
    
    # Fallback to session authentication if token is not provided
    user_id = None
    permissions = []
    token_exp = None
    
    if user_data:
        # Token authentication successful
        user_id = user_data['user_id']
        permissions = user_data.get('permissions', [])
        token_exp = user_data.get('exp')
        websocket_analytics.record_stat('token_auth_connections', 1)
    elif not current_user.is_anonymous:
        # Fallback to session authentication
        user_id = current_user.id
        permissions = websocket_permissions._get_user_permissions(user_id)
        websocket_analytics.record_stat('session_auth_connections', 1)
    else:
        # Anonymous user
        websocket_analytics.record_stat('anonymous_connections', 1)
    
    # Store session info with auth details
    session_info[session_id] = {
        'user_id': user_id,
        'permissions': permissions,
        'token_exp': token_exp,
        'subscriptions': set(),
        'ip_address': client_ip,
        'connection_time': datetime.utcnow(),
        'last_activity': datetime.utcnow()
    }
    
    # Join user room if authenticated
    if user_id:
        join_room(f'user_{user_id}')
    
    # Join the global room
    join_room('global')
    
    logger.info(f"Client connected: {session_id}, User: {user_id}, IP: {client_ip}")
    
    # Record in analytics service
    websocket_analytics.record_connection(session_id, user_id)
    
    # Send connection confirmation with auth status
    emit('connection_status', {
        'status': 'connected',
        'session_id': session_id,
        'authenticated': user_id is not None,
        'token_authenticated': user_data is not None,
        'token_expiry': token_exp,
        'permissions': permissions
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    session_id = request.sid
    
    # Get user info before cleaning up
    user_info = session_info.get(session_id, {})
    user_id = user_info.get('user_id')
    
    logger.info(f"Client disconnected: {session_id}, User: {user_id}")
    
    # Record in analytics service
    websocket_analytics.record_disconnection(session_id)
    
    # Remove from all subscriptions
    subscriptions = user_info.get('subscriptions', set()).copy()
    for entity_key in subscriptions:
        try:
            entity_type, entity_id = entity_key.split(':')
            _remove_subscriber(entity_type, entity_id, session_id)
        except Exception as e:
            logger.error(f"Error removing subscription on disconnect: {str(e)}")
    
    # Remove session info
    if session_id in session_info:
        del session_info[session_id]

@socketio.on('subscribe')
def handle_subscribe(data):
    """
    Handle entity subscription requests with optional filtering.
    
    Basic subscription format:
    {
        "entity_type": "campaign",
        "entity_id": 123
    }
    
    Enhanced subscription with filtering:
    {
        "entity_type": "campaign", 
        "filter": {
            "operator": "AND",
            "conditions": [
                {"field": "status", "op": "eq", "value": "active"},
                {"field": "budget", "op": "gt", "value": 1000}
            ]
        }
    }
    
    Multi-entity subscription:
    {
        "multi_entity": true,
        "entity_types": ["campaign", "segment"],
        "filter": {...}
    }
    """
    session_id = request.sid
    
    # Get session information
    session_data = session_info.get(session_id, {})
    user_id = session_data.get('user_id')
    client_ip = session_data.get('ip_address')
    
    # Update last activity timestamp
    if session_id in session_info:
        session_info[session_id]['last_activity'] = datetime.utcnow()
    
    # Check rate limits for subscriptions
    allowed, retry_after = websocket_rate_limiter.check_rate_limit(
        'subscription', user_id=user_id, ip=client_ip
    )
    
    if not allowed:
        websocket_analytics.record_stat('rate_limited_subscriptions', 1)
        emit('error', {
            'code': 429,
            'message': 'Rate limit exceeded',
            'details': f'Too many subscription requests. Please try again in {retry_after:.1f} seconds'
        })
        return
    
    # Check for multi-entity subscription
    if data.get('multi_entity'):
        return _handle_multi_entity_subscription(data, session_id)
    
    # Regular entity subscription
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    filter_expr = data.get('filter')
    
    # Validate basic requirements
    if not entity_type:
        emit('error', {
            'code': 400,
            'message': 'Invalid subscription request',
            'details': 'entity_type is required'
        })
        return
    
    # Check permission for this subscription
    has_permission = websocket_permissions.has_permission(
        user_id, 'subscribe', entity_type, entity_id, filter_expr
    )
    
    if not has_permission:
        websocket_analytics.record_stat('permission_denied_subscriptions', 1)
        emit('error', {
            'code': 403,
            'message': 'Permission denied',
            'details': f'You do not have permission to subscribe to {entity_type}'
        })
        logger.warning(f"Permission denied for subscription: user {user_id} -> {entity_type}:{entity_id}")
        return
    
    # For entity-type only subscriptions (with filter)
    if not entity_id and filter_expr:
        success = _add_filtered_subscriber(entity_type, filter_expr, session_id)
        
        if success:
            # Join room for this filtered subscription
            room_name = f"{entity_type}_filtered_{session_id}"
            join_room(room_name)
            
            # Record in analytics service
            websocket_analytics.record_subscription(session_id, entity_type, filter_expression=filter_expr)
            
            emit('subscription_status', {
                'status': 'subscribed',
                'entity_type': entity_type,
                'filter': filter_expr,
                'subscription_id': room_name
            })
            
            logger.info(f"Client {session_id} subscribed to {entity_type} with filter: {filter_expr}")
        else:
            emit('error', {
                'code': 400,
                'message': 'Filtered subscription failed',
                'details': 'Invalid filter expression or entity type'
            })
        return
    
    # Regular entity subscription
    if not entity_id:
        emit('error', {
            'code': 400,
            'message': 'Invalid subscription request',
            'details': 'entity_id is required for direct entity subscriptions'
        })
        return
    
    # Add subscriber to entity
    success = _add_subscriber(entity_type, entity_id, session_id, filter_expr)
    
    if success:
        # Join room for this entity
        room_name = f"{entity_type}_{entity_id}"
        join_room(room_name)
        
        # Record in analytics service
        websocket_analytics.record_subscription(session_id, entity_type, entity_id, filter_expr)
        
        # Response data
        response_data = {
            'status': 'subscribed',
            'entity_type': entity_type,
            'entity_id': entity_id
        }
        
        # Include filter if provided
        if filter_expr:
            response_data['filter'] = filter_expr
        
        # Add subscription count
        entity_subscription_count = 0
        if entity_type in entity_subscribers and entity_id in entity_subscribers[entity_type]:
            if isinstance(entity_subscribers[entity_type][entity_id], dict):
                entity_subscription_count = len(entity_subscribers[entity_type][entity_id].get('sessions', set()))
            else:
                entity_subscription_count = len(entity_subscribers[entity_type][entity_id])
                
        response_data['subscriber_count'] = entity_subscription_count
        
        emit('subscription_status', response_data)
        
        logger.info(f"Client {session_id} subscribed to {entity_type}:{entity_id}" + 
                   (f" with filter: {filter_expr}" if filter_expr else ""))
    else:
        emit('error', {
            'code': 500,
            'message': 'Subscription failed',
            'details': 'Unable to register subscription'
        })

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """
    Handle entity unsubscription requests.
    
    Basic unsubscription format:
    {
        "entity_type": "campaign",
        "entity_id": 123
    }
    
    Filtered unsubscription format:
    {
        "entity_type": "campaign",
        "filter_hash": "md5hash"
    }
    
    Multi-entity unsubscription format:
    {
        "multi_entity": true,
        "subscription_id": "multi_abc123"
    }
    """
    session_id = request.sid
    
    # Handle multi-entity unsubscription
    if data.get('multi_entity') and data.get('subscription_id'):
        room_name = data.get('subscription_id')
        success = _remove_multi_entity_subscriber(room_name, session_id)
        
        if success:
            # Leave room
            leave_room(room_name)
            
            emit('subscription_status', {
                'status': 'unsubscribed',
                'multi_entity': True,
                'subscription_id': room_name
            })
            
            logger.info(f"Client {session_id} unsubscribed from multi-entity subscription: {room_name}")
        else:
            emit('error', {
                'message': 'Multi-entity unsubscription failed',
                'details': 'No active subscription found'
            })
        return
    
    # Handle filtered subscription unsubscription
    entity_type = data.get('entity_type')
    if entity_type and data.get('filter_hash'):
        filter_hash = data.get('filter_hash')
        success = _remove_filtered_subscriber(entity_type, filter_hash, session_id)
        
        if success:
            # Leave room
            room_name = f"{entity_type}_filter_{filter_hash}"
            leave_room(room_name)
            
            emit('subscription_status', {
                'status': 'unsubscribed',
                'entity_type': entity_type,
                'filter_hash': filter_hash
            })
            
            logger.info(f"Client {session_id} unsubscribed from filtered {entity_type} subscription: {filter_hash}")
        else:
            emit('error', {
                'message': 'Filtered unsubscription failed',
                'details': 'No active subscription found'
            })
        return
    
    # Handle standard entity unsubscription
    entity_id = data.get('entity_id')
    
    if not entity_type or not entity_id:
        emit('error', {
            'message': 'Invalid unsubscription request',
            'details': 'entity_type and entity_id are required for direct entity unsubscription'
        })
        return
    
    # Remove subscriber from entity
    success = _remove_subscriber(entity_type, entity_id, session_id)
    
    if success:
        # Leave room for this entity
        room_name = f"{entity_type}_{entity_id}"
        leave_room(room_name)
        
        # Record in analytics service
        websocket_analytics.record_unsubscription(session_id, entity_type, entity_id)
        
        emit('subscription_status', {
            'status': 'unsubscribed',
            'entity_type': entity_type,
            'entity_id': entity_id
        })
        
        logger.info(f"Client {session_id} unsubscribed from {entity_type}:{entity_id}")
    else:
        emit('error', {
            'message': 'Unsubscription failed',
            'details': 'No active subscription found'
        })

@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    """Handle request to unsubscribe from all entities and all subscription types."""
    session_id = request.sid
    
    # Track total unsubscribed count
    unsubscribed_count = 0
    
    # 1. Unsubscribe from direct entity subscriptions
    entity_subscriptions = session_info.get(session_id, {}).get('subscriptions', set()).copy()
    
    for entity_key in entity_subscriptions:
        try:
            entity_type, entity_id = entity_key.split(':')
            if _remove_subscriber(entity_type, entity_id, session_id):
                # Leave room for this entity
                room_name = f"{entity_type}_{entity_id}"
                leave_room(room_name)
                unsubscribed_count += 1
        except Exception as e:
            logger.error(f"Error during unsubscribe_all (direct entity): {str(e)}")
    
    # 2. Unsubscribe from filtered subscriptions
    filter_subscriptions = session_info.get(session_id, {}).get('filter_subscriptions', set()).copy()
    
    for filter_key in filter_subscriptions:
        try:
            # Format is entity_type:filter:hash
            parts = filter_key.split(':')
            if len(parts) == 3:
                entity_type = parts[0]
                filter_hash = parts[2]
                
                if _remove_filtered_subscriber(entity_type, filter_hash, session_id):
                    # Leave room for this filtered subscription
                    room_name = f"{entity_type}_filter_{filter_hash}"
                    leave_room(room_name)
                    unsubscribed_count += 1
        except Exception as e:
            logger.error(f"Error during unsubscribe_all (filtered): {str(e)}")
    
    # 3. Unsubscribe from multi-entity subscriptions
    multi_subscriptions = {}
    if 'multi_subscriptions' in session_info.get(session_id, {}):
        multi_subscriptions = session_info[session_id]['multi_subscriptions'].copy()
    
    for room_name in multi_subscriptions:
        try:
            if _remove_multi_entity_subscriber(room_name, session_id):
                # Leave room for this multi-entity subscription
                leave_room(room_name)
                unsubscribed_count += 1
        except Exception as e:
            logger.error(f"Error during unsubscribe_all (multi-entity): {str(e)}")
    
    emit('subscription_status', {
        'status': 'unsubscribed_all',
        'count': unsubscribed_count
    })
    
    logger.info(f"Client {session_id} unsubscribed from all subscriptions ({unsubscribed_count})")

@socketio.on('ping')
def handle_ping(data):
    """Handle ping messages from clients."""
    session_id = request.sid
    client_timestamp = data.get('timestamp')
    current_time = import_time_module().time()
    
    # Calculate round-trip latency if client timestamp is provided
    if client_timestamp:
        latency_ms = (current_time - float(client_timestamp)) * 1000
        # Record latency in analytics service
        websocket_analytics.record_latency(session_id, latency_ms)
    
    emit('pong', {
        'timestamp': client_timestamp,
        'server_time': current_time
    })
    
@socketio.on('error')
def handle_client_error(data):
    """Handle error reports from clients."""
    session_id = request.sid
    error_type = data.get('type', 'client_error')
    error_message = data.get('message', 'Unknown client error')
    
    # Record error in analytics service
    websocket_analytics.record_error(session_id, error_type, error_message)
    
    # Log the error
    logger.error(f"Client error from {session_id}: {error_type} - {error_message}")
    
    # Acknowledge receipt of error
    emit('error_received', {
        'status': 'recorded',
        'timestamp': import_time_module().time()
    })

@socketio.on('client_stats')
def handle_client_stats(data):
    """Handle performance statistics reported from clients."""
    session_id = request.sid
    
    # Extract client-side statistics
    message_count = data.get('message_count', 0)
    processing_time = data.get('processing_time_ms', 0)
    render_time = data.get('render_time_ms', 0)
    batch_size = data.get('batch_size', 0)
    compressed_msgs = data.get('compressed_messages', 0)
    decompression_time = data.get('decompression_time_ms', 0)
    
    # Log client performance data
    logger.info(f"Client stats from {session_id}: processed {message_count} messages, " +
                f"processing: {processing_time}ms, rendering: {render_time}ms")
    
    # Record client stats in analytics
    websocket_analytics.record_stat('client_processing_time_ms', processing_time)
    websocket_analytics.record_stat('client_render_time_ms', render_time or 0)
    websocket_analytics.record_stat('client_batch_size', batch_size)
    websocket_analytics.record_stat('client_decompression_time_ms', decompression_time)
    
    # Acknowledge receipt
    emit('stats_received', {
        'status': 'recorded',
        'timestamp': import_time_module().time()
    })

@socketio.on('acknowledge')
def handle_acknowledgment(data):
    """Handle message acknowledgment from client."""
    session_id = request.sid
    ack_id = data.get('id')
    
    if ack_id is None:
        return
    
    # Record acknowledgment in analytics
    websocket_analytics.record_stat('message_acknowledgments', 1)
    
    # Update client last activity time
    if session_id in session_info:
        session_info[session_id]['last_activity'] = datetime.utcnow()
        
    # Log at debug level
    logger.debug(f"Received acknowledgment from {session_id} for message {ack_id}")

def import_time_module():
    """Import time module to avoid circular imports."""
    import time
    return time

def _handle_multi_entity_subscription(data, session_id):
    """
    Handle subscription to multiple entity types.
    
    Args:
        data (dict): Subscription data with entity_types and optional filter
        session_id (str): WebSocket session ID
        
    Returns:
        None
    """
    entity_types = data.get('entity_types', [])
    filter_expr = data.get('filter')
    
    # Get user ID for permission checking
    user_id = session_info.get(session_id, {}).get('user_id')
    
    if not entity_types or not isinstance(entity_types, list):
        emit('error', {
            'code': 400,
            'message': 'Invalid multi-entity subscription',
            'details': 'entity_types must be a non-empty list'
        })
        return
    
    # Limit the number of entity types in a single subscription
    max_entity_types = 10
    if len(entity_types) > max_entity_types:
        emit('error', {
            'code': 400,
            'message': 'Too many entity types',
            'details': f'Maximum {max_entity_types} entity types allowed in a multi-entity subscription'
        })
        return
        
    # Check permissions for each entity type
    denied_types = []
    for entity_type in entity_types:
        if not websocket_permissions.has_permission(user_id, 'subscribe', entity_type, None, filter_expr):
            denied_types.append(entity_type)
    
    if denied_types:
        websocket_analytics.record_stat('permission_denied_subscriptions', 1)
        emit('error', {
            'code': 403,
            'message': 'Permission denied',
            'details': f'You do not have permission to subscribe to: {", ".join(denied_types)}'
        })
        return
    
    # Create a unique room for this multi-entity subscription
    import hashlib
    subscription_hash = hashlib.md5(f"{session_id}_{','.join(entity_types)}_{str(filter_expr)}".encode()).hexdigest()
    room_name = f"multi_{subscription_hash}"
    
    # Store this multi-entity subscription
    if 'multi_subscriptions' not in session_info.setdefault(session_id, {}):
        session_info[session_id]['multi_subscriptions'] = {}
    
    # Add subscription details
    session_info[session_id]['multi_subscriptions'][room_name] = {
        'entity_types': entity_types,
        'filter': filter_expr,
        'created_at': datetime.utcnow()
    }
    
    # Join the room
    join_room(room_name)
    
    # Track subscription for each entity type
    for entity_type in entity_types:
        # Create entity_type dictionary if it doesn't exist
        if 'multi_entity_subscribers' not in globals():
            globals()['multi_entity_subscribers'] = {}
            
        if entity_type not in globals()['multi_entity_subscribers']:
            globals()['multi_entity_subscribers'][entity_type] = {}
            
        if room_name not in globals()['multi_entity_subscribers'][entity_type]:
            globals()['multi_entity_subscribers'][entity_type][room_name] = {
                'filter': filter_expr,
                'sessions': set()
            }
            
        globals()['multi_entity_subscribers'][entity_type][room_name]['sessions'].add(session_id)
        
        # Record in analytics service (per entity type)
        websocket_analytics.record_subscription(
            session_id, 
            entity_type, 
            entity_id=None, 
            filter_expression=filter_expr
        )
    
    emit('subscription_status', {
        'status': 'subscribed',
        'multi_entity': True,
        'entity_types': entity_types,
        'filter': filter_expr,
        'subscription_id': room_name
    })
    
    # Record multi-entity subscription in analytics
    websocket_analytics.record_stat('multi_entity_subscriptions', 1)
    websocket_analytics.record_stat('multi_entity_subscription_types', len(entity_types))
    
    logger.info(f"Client {session_id} subscribed to multiple entity types: {entity_types}" +
               (f" with filter: {filter_expr}" if filter_expr else ""))

def _add_filtered_subscriber(entity_type, filter_expr, session_id):
    """
    Add a subscriber to an entity type with filter.
    
    Args:
        entity_type (str): Type of entity to subscribe to
        filter_expr (dict): Filter expression
        session_id (str): WebSocket session ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate filter expression
        if not _validate_filter_expression(filter_expr):
            return False
            
        # Create filtered_subscribers dictionary if it doesn't exist
        if 'filtered_subscribers' not in globals():
            globals()['filtered_subscribers'] = {}
            
        # Create entity_type dictionary if it doesn't exist
        if entity_type not in globals()['filtered_subscribers']:
            globals()['filtered_subscribers'][entity_type] = {}
            
        # Create unique key for this filter
        import hashlib
        filter_hash = hashlib.md5(str(filter_expr).encode()).hexdigest()
        filter_key = f"{entity_type}_filter_{filter_hash}"
        
        # Create filter entry if it doesn't exist
        if filter_key not in globals()['filtered_subscribers'][entity_type]:
            globals()['filtered_subscribers'][entity_type][filter_key] = {
                'filter': filter_expr,
                'sessions': set()
            }
            
        # Add session to filtered subscribers
        globals()['filtered_subscribers'][entity_type][filter_key]['sessions'].add(session_id)
        
        # Add to session subscriptions
        subscription_key = f"{entity_type}:filter:{filter_hash}"
        session_info.setdefault(session_id, {}).setdefault('filter_subscriptions', set()).add(subscription_key)
        
        return True
    except Exception as e:
        logger.error(f"Error adding filtered subscriber: {str(e)}")
        return False

def _add_subscriber(entity_type, entity_id, session_id, filter_expr=None):
    """
    Add a subscriber to an entity.
    
    Args:
        entity_type (str): Type of entity to subscribe to
        entity_id (str/int): ID of entity to subscribe to
        session_id (str): WebSocket session ID
        filter_expr (dict, optional): Filter expression for conditional updates
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate filter if provided
        if filter_expr and not _validate_filter_expression(filter_expr):
            return False
            
        # Convert entity_id to string for consistency
        entity_id = str(entity_id)
        
        # Create entity_type dictionary if it doesn't exist
        if entity_type not in entity_subscribers:
            entity_subscribers[entity_type] = {}
            
        # Create entity_id set if it doesn't exist
        if entity_id not in entity_subscribers[entity_type]:
            entity_subscribers[entity_type][entity_id] = {}
            
        # If we're transitioning from old format, convert to new
        if isinstance(entity_subscribers[entity_type][entity_id], set):
            old_subscribers = entity_subscribers[entity_type][entity_id]
            entity_subscribers[entity_type][entity_id] = {
                'sessions': old_subscribers,
                'filters': {}  # Maps session_id to its filter
            }
            
        # Add session_id to subscribers
        entity_subscribers[entity_type][entity_id].setdefault('sessions', set()).add(session_id)
        
        # Add filter if provided
        if filter_expr:
            entity_subscribers[entity_type][entity_id].setdefault('filters', {})[session_id] = filter_expr
            
        # Add to session subscriptions
        subscription_key = f"{entity_type}:{entity_id}"
        session_info.setdefault(session_id, {}).setdefault('subscriptions', set()).add(subscription_key)
        
        return True
    except Exception as e:
        logger.error(f"Error adding subscriber: {str(e)}")
        return False
        
def _validate_filter_expression(filter_expr):
    """
    Validate a filter expression.
    
    Args:
        filter_expr (dict): Filter expression to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Basic structure validation
        if not isinstance(filter_expr, dict):
            return False
            
        # Check for simple condition
        if all(k in filter_expr for k in ['field', 'op', 'value']):
            return filter_expr['op'] in ['eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'contains', 'startswith', 'endswith']
            
        # Check for complex condition with operator and conditions
        if 'operator' in filter_expr and 'conditions' in filter_expr:
            if filter_expr['operator'] not in ['AND', 'OR']:
                return False
                
            if not isinstance(filter_expr['conditions'], list) or not filter_expr['conditions']:
                return False
                
            # Recursively validate each condition
            return all(_validate_filter_expression(cond) for cond in filter_expr['conditions'])
            
        return False
    except Exception as e:
        logger.error(f"Error validating filter expression: {str(e)}")
        return False

def _remove_subscriber(entity_type, entity_id, session_id):
    """
    Remove a subscriber from an entity.
    
    Args:
        entity_type (str): Type of entity
        entity_id (str/int): ID of entity
        session_id (str): WebSocket session ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert entity_id to string for consistency
        entity_id = str(entity_id)
        
        # Check if entity type exists
        if entity_type not in entity_subscribers:
            return False
            
        # Check if entity ID exists
        if entity_id not in entity_subscribers[entity_type]:
            return False
        
        # Handle new subscriber structure with filters
        if isinstance(entity_subscribers[entity_type][entity_id], dict):
            # Check if session is subscribed
            if session_id not in entity_subscribers[entity_type][entity_id].get('sessions', set()):
                return False
                
            # Remove session from subscribers
            entity_subscribers[entity_type][entity_id]['sessions'].remove(session_id)
            
            # Remove any filter for this session
            if 'filters' in entity_subscribers[entity_type][entity_id] and session_id in entity_subscribers[entity_type][entity_id]['filters']:
                del entity_subscribers[entity_type][entity_id]['filters'][session_id]
        else:
            # Legacy format (direct set)
            # Check if session is subscribed
            if session_id not in entity_subscribers[entity_type][entity_id]:
                return False
                
            # Remove session from subscribers
            entity_subscribers[entity_type][entity_id].remove(session_id)
        
        # Remove from session subscriptions
        subscription_key = f"{entity_type}:{entity_id}"
        if session_id in session_info and 'subscriptions' in session_info[session_id]:
            session_info[session_id]['subscriptions'].discard(subscription_key)
        
        # Clean up empty structures
        if isinstance(entity_subscribers[entity_type][entity_id], dict) and not entity_subscribers[entity_type][entity_id].get('sessions', set()):
            del entity_subscribers[entity_type][entity_id]
        elif isinstance(entity_subscribers[entity_type][entity_id], set) and not entity_subscribers[entity_type][entity_id]:
            del entity_subscribers[entity_type][entity_id]
            
        # Clean up empty entity type
        if entity_type in entity_subscribers and not entity_subscribers[entity_type]:
            del entity_subscribers[entity_type]
        
        return True
    except Exception as e:
        logger.error(f"Error removing subscriber: {str(e)}")
        return False
        
def _remove_filtered_subscriber(entity_type, filter_hash, session_id):
    """
    Remove a filtered subscriber.
    
    Args:
        entity_type (str): Type of entity
        filter_hash (str): Hash of the filter expression
        session_id (str): WebSocket session ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if filtered subscribers exist
        if 'filtered_subscribers' not in globals():
            return False
            
        # Check if entity type exists
        if entity_type not in globals()['filtered_subscribers']:
            return False
            
        filter_key = f"{entity_type}_filter_{filter_hash}"
        
        # Check if filter exists
        if filter_key not in globals()['filtered_subscribers'][entity_type]:
            return False
            
        # Check if session is subscribed
        if session_id not in globals()['filtered_subscribers'][entity_type][filter_key]['sessions']:
            return False
            
        # Remove session from subscribers
        globals()['filtered_subscribers'][entity_type][filter_key]['sessions'].remove(session_id)
        
        # Remove from session filter subscriptions
        subscription_key = f"{entity_type}:filter:{filter_hash}"
        if session_id in session_info and 'filter_subscriptions' in session_info[session_id]:
            session_info[session_id]['filter_subscriptions'].discard(subscription_key)
        
        # Clean up empty sets
        if not globals()['filtered_subscribers'][entity_type][filter_key]['sessions']:
            del globals()['filtered_subscribers'][entity_type][filter_key]
            
            if not globals()['filtered_subscribers'][entity_type]:
                del globals()['filtered_subscribers'][entity_type]
        
        return True
    except Exception as e:
        logger.error(f"Error removing filtered subscriber: {str(e)}")
        return False
        
def _remove_multi_entity_subscriber(room_name, session_id):
    """
    Remove a multi-entity subscriber.
    
    Args:
        room_name (str): Room name for the multi-entity subscription
        session_id (str): WebSocket session ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if session and multi-subscriptions exist
        if session_id not in session_info or 'multi_subscriptions' not in session_info[session_id]:
            return False
            
        # Check if this subscription exists
        if room_name not in session_info[session_id]['multi_subscriptions']:
            return False
            
        # Get entity types for this subscription
        entity_types = session_info[session_id]['multi_subscriptions'][room_name]['entity_types']
        
        # Remove from multi_entity_subscribers
        if 'multi_entity_subscribers' in globals():
            for entity_type in entity_types:
                if entity_type in globals()['multi_entity_subscribers'] and room_name in globals()['multi_entity_subscribers'][entity_type]:
                    # Remove session from room
                    globals()['multi_entity_subscribers'][entity_type][room_name]['sessions'].discard(session_id)
                    
                    # Clean up empty rooms
                    if not globals()['multi_entity_subscribers'][entity_type][room_name]['sessions']:
                        del globals()['multi_entity_subscribers'][entity_type][room_name]
                        
                    # Clean up empty entity types
                    if not globals()['multi_entity_subscribers'][entity_type]:
                        del globals()['multi_entity_subscribers'][entity_type]
        
        # Remove from session multi-subscriptions
        del session_info[session_id]['multi_subscriptions'][room_name]
        
        # Clean up if no more multi-subscriptions
        if not session_info[session_id]['multi_subscriptions']:
            del session_info[session_id]['multi_subscriptions']
        
        return True
    except Exception as e:
        logger.error(f"Error removing multi-entity subscriber: {str(e)}")
        return False

@websocket_bp.route('/token', methods=['POST'])
@login_required
def generate_websocket_token():
    """Generate a WebSocket authentication token for the current user."""
    try:
        user_id = current_user.id
        
        # Get permissions for this user
        permissions = websocket_permissions._get_user_permissions(user_id)
        
        # Default token expiry (1 hour)
        token_expiry = current_app.config.get('WEBSOCKET_TOKEN_EXPIRY', 3600)
        
        # Generate token with permissions
        token = websocket_auth.generate_token(user_id, permissions)
        
        # Return token to client
        return jsonify({
            'status': 'success',
            'token': token,
            'expires_in': token_expiry,
            'permissions': permissions
        })
    except Exception as e:
        logger.error(f"Error generating WebSocket token: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate token',
            'details': str(e)
        }), 500

@websocket_bp.route('/message-stats')
def websocket_message_stats():
    """API endpoint to get WebSocket message statistics."""
    try:
        # Calculate derived stats
        stats_copy = message_stats.copy()
        
        # Calculate time since last reset
        stats_copy['uptime_seconds'] = time.time() - stats_copy['last_reset']
        
        # Calculate messages per second
        if stats_copy['uptime_seconds'] > 0:
            stats_copy['messages_per_second'] = stats_copy['total_messages_sent'] / stats_copy['uptime_seconds']
        else:
            stats_copy['messages_per_second'] = 0
            
        # Calculate compression ratio
        if stats_copy['total_bytes_sent'] > 0:
            bytes_before_compression = stats_copy['total_bytes_sent'] + stats_copy['total_bytes_saved']
            stats_copy['compression_ratio'] = bytes_before_compression / stats_copy['total_bytes_sent']
        else:
            stats_copy['compression_ratio'] = 0
            
        # Calculate batching efficiency
        if stats_copy['batched_messages'] > 0:
            stats_copy['batching_efficiency'] = stats_copy['batched_messages'] / stats_copy['total_messages_sent']
        else:
            stats_copy['batching_efficiency'] = 0
            
        # Get analytics data for a more comprehensive view
        analytics_data = websocket_analytics.get_analytics_dashboard_data()
            
        return jsonify({
            'status': 'active',
            'message_stats': stats_copy,
            'analytics': analytics_data
        })
    except Exception as e:
        logger.error(f"Error getting message stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@websocket_bp.route('/connections')
def websocket_connections():
    """API endpoint to get details about active WebSocket connections."""
    try:
        connections = websocket_analytics.get_connection_details()
        return jsonify({
            'status': 'success',
            'connection_count': len(connections),
            'connections': connections
        })
    except Exception as e:
        logger.error(f"Error getting WebSocket connections: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@websocket_bp.route('/connection/<session_id>')
def websocket_connection_detail(session_id):
    """API endpoint to get details about a specific WebSocket connection."""
    try:
        connection = websocket_analytics.get_connection_details(session_id)
        if connection:
            return jsonify({
                'status': 'success',
                'connection': connection
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f"No active connection found with ID: {session_id}"
            }), 404
    except Exception as e:
        logger.error(f"Error getting WebSocket connection details: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@websocket_bp.route('/security-stats')
@login_required
def websocket_security_stats():
    """API endpoint to get WebSocket security statistics."""
    try:
        # Get rate limiter stats
        rate_limit_stats = websocket_rate_limiter.get_rate_limit_stats()
        
        # Get real-time security metrics from analytics service
        realtime_stats = {}
        for stat_name in [
            'rate_limited_connections', 'rate_limited_subscriptions',
            'permission_denied_subscriptions', 'token_auth_connections',
            'session_auth_connections', 'anonymous_connections',
            'ack_requests', 'message_acknowledgments'
        ]:
            realtime_stats[stat_name] = websocket_analytics.realtime_stats.get(stat_name, 0)
        
        # Active connections by authentication type
        auth_types = {'token': 0, 'session': 0, 'anonymous': 0}
        for session_data in session_info.values():
            if session_data.get('token_exp'):
                auth_types['token'] += 1
            elif session_data.get('user_id'):
                auth_types['session'] += 1
            else:
                auth_types['anonymous'] += 1
        
        return jsonify({
            'status': 'success',
            'rate_limiting': rate_limit_stats,
            'security_metrics': realtime_stats,
            'authentication': {
                'active_connections_by_type': auth_types,
                'total_active_connections': len(session_info)
            }
        })
    except Exception as e:
        logger.error(f"Error getting security stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@websocket_bp.route('/status')
def websocket_status():
    """API endpoint to get WebSocket status and statistics for all subscription types."""
    try:
        # Count active sessions
        active_sessions = len(session_info)
        
        # Calculate statistics for each subscription type
        stats = {}
        
        # 1. Direct entity subscriptions
        entity_counts = {}
        direct_subscription_count = 0
        
        for entity_type, entities in entity_subscribers.items():
            type_count = 0
            for entity_id, subscribers in entities.items():
                if isinstance(subscribers, dict):
                    # New format with filters
                    session_count = len(subscribers.get('sessions', set()))
                else:
                    # Legacy format
                    session_count = len(subscribers)
                    
                type_count += session_count
            
            entity_counts[entity_type] = type_count
            direct_subscription_count += type_count
            
        stats['direct_subscriptions'] = {
            'count': direct_subscription_count,
            'by_entity_type': entity_counts
        }
        
        # 2. Filtered subscriptions
        filtered_counts = {}
        filtered_subscription_count = 0
        
        if 'filtered_subscribers' in globals():
            for entity_type, filters in globals()['filtered_subscribers'].items():
                type_count = 0
                for filter_key, filter_data in filters.items():
                    session_count = len(filter_data.get('sessions', set()))
                    type_count += session_count
                
                filtered_counts[entity_type] = type_count
                filtered_subscription_count += type_count
                
        stats['filtered_subscriptions'] = {
            'count': filtered_subscription_count,
            'by_entity_type': filtered_counts
        }
        
        # 3. Multi-entity subscriptions
        multi_entity_count = 0
        multi_entity_details = {}
        
        if 'multi_entity_subscribers' in globals():
            for entity_type, rooms in globals()['multi_entity_subscribers'].items():
                entity_room_count = len(rooms)
                session_count = sum(len(room_data.get('sessions', set())) for room_data in rooms.values())
                
                multi_entity_details[entity_type] = {
                    'room_count': entity_room_count,
                    'session_count': session_count
                }
                
                multi_entity_count += session_count
                
        stats['multi_entity_subscriptions'] = {
            'count': multi_entity_count,
            'details': multi_entity_details
        }
        
        # 4. Calculate memory usage (estimated)
        import sys
        memory_usage = {
            'session_info': sys.getsizeof(str(session_info)),
            'entity_subscribers': sys.getsizeof(str(entity_subscribers))
        }
        
        if 'filtered_subscribers' in globals():
            memory_usage['filtered_subscribers'] = sys.getsizeof(str(globals()['filtered_subscribers']))
            
        if 'multi_entity_subscribers' in globals():
            memory_usage['multi_entity_subscribers'] = sys.getsizeof(str(globals()['multi_entity_subscribers']))
            
        memory_usage['total'] = sum(memory_usage.values())
        
        # Get analytics data from the websocket analytics service
        analytics_data = websocket_analytics.get_analytics_dashboard_data()
        
        # Full response
        return jsonify({
            'status': 'active',
            'active_sessions': active_sessions,
            'total_subscriptions': direct_subscription_count + filtered_subscription_count + multi_entity_count,
            'subscription_stats': stats,
            'memory_usage': memory_usage,
            'analytics': analytics_data
        })
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def emit_to_entity_subscribers(entity_type, entity_id, event_name, data, request_acknowledgment=False):
    """
    Emit an event to all subscribers of an entity.
    
    Args:
        entity_type (str): Type of entity
        entity_id (str/int): ID of entity
        event_name (str): Event name to emit
        data (dict): Event data to emit
        request_acknowledgment (bool): Whether to request acknowledgment
        
    Returns:
        int: Number of clients the event was sent to
    """
    try:
        # Convert entity_id to string for consistency
        entity_id = str(entity_id)
        
        # Create room name
        room_name = f"{entity_type}_{entity_id}"
        
        # Get subscriber count
        subscriber_count = 0
        if entity_type in entity_subscribers and entity_id in entity_subscribers[entity_type]:
            if isinstance(entity_subscribers[entity_type][entity_id], dict):
                subscriber_count = len(entity_subscribers[entity_type][entity_id].get('sessions', set()))
            else:
                subscriber_count = len(entity_subscribers[entity_type][entity_id])
        
        # If too many subscribers or high frequency updates, use batching
        use_batching = subscriber_count > 5  # Batch for more than 5 subscribers
        
        # Check if this entity type should always use batching
        high_freq_types = ['analytics', 'task']
        if entity_type in high_freq_types:
            use_batching = True
        
        # Some critical messages should not be batched to ensure delivery
        if request_acknowledgment and subscriber_count <= 20:
            use_batching = False
        
        # Message size for tracking
        message_size = len(json.dumps(data))
        
        # Add acknowledgment request ID to critical messages for tracking
        if request_acknowledgment:
            # Create a unique acknowledgment ID
            ack_id = f"{entity_type}_{entity_id}_{time.time()}_{hash(str(data))}"[-32:]
            
            # Add acknowledgment request to data
            if isinstance(data, dict):
                data['_ack'] = {
                    'id': ack_id,
                    'timestamp': time.time()
                }
            
            # Record pending acknowledgment in analytics
            websocket_analytics.record_stat('ack_requests', 1)
            
            logger.debug(f"Requesting acknowledgment {ack_id} for {entity_type}:{entity_id} message")
        
        # Use batch emitting if appropriate
        if use_batching:
            batch_emit(event_name, data, room=room_name)
        else:
            # For smaller rooms, emit directly for lower latency
            socketio.emit(event_name, data, room=room_name)
        
        # Update stats
        with message_batch_lock:
            if not use_batching:
                message_stats['total_messages_sent'] += 1
                message_stats['total_bytes_sent'] += message_size
        
        # Track message in analytics for each subscriber
        if entity_type in entity_subscribers and entity_id in entity_subscribers[entity_type]:
            if isinstance(entity_subscribers[entity_type][entity_id], dict):
                sessions = entity_subscribers[entity_type][entity_id].get('sessions', set())
            else:
                sessions = entity_subscribers[entity_type][entity_id]
                
            for session_id in sessions:
                websocket_analytics.record_message(session_id, message_size, is_incoming=False)
        
        return subscriber_count
    except Exception as e:
        logger.error(f"Error emitting to entity subscribers: {str(e)}")
        return 0

def emit_entity_update(entity_type, entity_id, update_type, entity_data, request_acknowledgment=False):
    """
    Emit an entity update event to subscribers.
    
    Args:
        entity_type (str): Type of entity that was updated
        entity_id (str/int): ID of entity that was updated
        update_type (str): Type of update (created, updated, deleted, etc.)
        entity_data (dict): Updated entity data
        request_acknowledgment (bool): Whether to request acknowledgment for this update
        
    Returns:
        int: Number of clients notified
    """
    # Add entity type and ID to entity data for filtering
    if entity_data and isinstance(entity_data, dict):
        entity_data['entity_type'] = entity_type
        if 'id' not in entity_data and 'entity_id' not in entity_data:
            entity_data['id'] = entity_id
    
    # Generate message data
    data = {
        'type': 'entity_update',
        'entity_type': entity_type,
        'entity_id': entity_id,
        'update_type': update_type,
        'entity': entity_data,
        'timestamp': import_time_module().time()
    }
    
    # Determine if this is a critical update that needs acknowledgment
    is_critical = False
    if request_acknowledgment or update_type in ['deleted', 'error', 'critical_status']:
        is_critical = True
        
    # Invalidate filter cache for this entity when it changes
    try:
        from app.services.websocket_filter_cache import filter_cache
        if update_type in ['created', 'updated', 'deleted', 'status_change']:
            filter_cache.invalidate_entity(entity_type, entity_id)
            
            # For significant changes, invalidate the entire entity type
            if update_type in ['created', 'deleted']:
                filter_cache.invalidate_entity_type(entity_type)
                
            # Record cache invalidation in analytics
            websocket_analytics.record_stat('filter_cache_invalidations', 1)
    except ImportError:
        pass
    
    # Track total notified clients
    notified_count = 0
    
    # 1. Direct entity subscribers
    notified_count += emit_to_entity_subscribers(entity_type, entity_id, 'message', data, is_critical)
    
    # 2. Filtered subscribers for this entity type
    notified_count += emit_to_filtered_subscribers(entity_type, entity_data, 'message', data, is_critical)
    
    # 3. Multi-entity subscribers that include this entity type
    notified_count += emit_to_multi_entity_subscribers(entity_type, entity_data, 'message', data, is_critical)
    
    # Record entity update metrics in analytics
    websocket_analytics.record_stat(f'entity_update_{entity_type}', 1)
    websocket_analytics.record_stat(f'update_type_{update_type}', 1)
    if is_critical:
        websocket_analytics.record_stat('critical_updates', 1)
    
    return notified_count

def emit_to_filtered_subscribers(entity_type, entity_data, event_name, data, request_acknowledgment=False):
    """
    Emit an event to filtered subscribers of an entity type.
    
    Args:
        entity_type (str): Type of entity
        entity_data (dict): Entity data to evaluate against filters
        event_name (str): Event name to emit
        data (dict): Event data to emit
        request_acknowledgment (bool): Whether to request acknowledgment
        
    Returns:
        int: Number of clients the event was sent to
    """
    notified_count = 0
    
    # Check if filtered_subscribers exists
    if 'filtered_subscribers' not in globals():
        return 0
        
    # Check if entity type exists in filtered subscribers
    if entity_type not in globals()['filtered_subscribers']:
        return 0
        
    # Add acknowledgment request ID to critical messages for tracking
    original_data = data
    if request_acknowledgment:
        # We'll need to create separate acknowledgment IDs for each filter group
        data = copy.deepcopy(data)
    
    # For each filter, check if entity matches
    for filter_key, filter_data in globals()['filtered_subscribers'][entity_type].items():
        filter_expr = filter_data.get('filter')
        
        # Skip if no filter or filter is invalid
        if not filter_expr or not isinstance(filter_expr, dict):
            continue
            
        # Check if entity matches filter
        if evaluate_filter(filter_expr, entity_data):
            # For critical messages with acknowledgments, create a unique ID for this filter group
            if request_acknowledgment:
                # Deep copy data to avoid modifying the original
                message_data = copy.deepcopy(data)
                
                # Create unique acknowledgment ID for this filter group
                filter_hash = filter_key.split('_')[-1] if '_' in filter_key else 'default'
                ack_id = f"{entity_type}_filter_{filter_hash}_{time.time()}_{hash(str(message_data))}"[-32:]
                
                # Add acknowledgment request to data
                if isinstance(message_data, dict):
                    message_data['_ack'] = {
                        'id': ack_id,
                        'timestamp': time.time()
                    }
                
                # Record pending acknowledgment in analytics
                websocket_analytics.record_stat('ack_requests', 1)
                websocket_analytics.record_stat('filtered_ack_requests', 1)
                
                logger.debug(f"Requesting filtered acknowledgment {ack_id} for {entity_type} message")
                
                # Emit message with acknowledgment
                socketio.emit(event_name, message_data, room=filter_key)
            else:
                # Normal emit without acknowledgment
                socketio.emit(event_name, original_data, room=filter_key)
            
            # Count subscribers
            subscriber_count = len(filter_data.get('sessions', set()))
            notified_count += subscriber_count
            
            # Track message in analytics for each subscriber
            message_size = len(json.dumps(data))
            for session_id in filter_data.get('sessions', set()):
                websocket_analytics.record_message(session_id, message_size, is_incoming=False)
            
    return notified_count

def emit_to_multi_entity_subscribers(entity_type, entity_data, event_name, data, request_acknowledgment=False):
    """
    Emit an event to multi-entity subscribers that include this entity type.
    
    Args:
        entity_type (str): Type of entity
        entity_data (dict): Entity data to evaluate against filters
        event_name (str): Event name to emit
        data (dict): Event data to emit
        request_acknowledgment (bool): Whether to request acknowledgment
        
    Returns:
        int: Number of clients the event was sent to
    """
    notified_count = 0
    
    # Check if multi_entity_subscribers exists
    if 'multi_entity_subscribers' not in globals():
        return 0
        
    # Check if entity type exists in multi-entity subscribers
    if entity_type not in globals()['multi_entity_subscribers']:
        return 0
        
    # Add acknowledgment request ID to critical messages for tracking
    original_data = data
    if request_acknowledgment:
        # We'll need to create separate acknowledgment IDs for each multi-entity group
        data = copy.deepcopy(data)
    
    # For each multi-entity subscription room, check if entity matches filter
    for room_name, room_data in globals()['multi_entity_subscribers'][entity_type].items():
        filter_expr = room_data.get('filter')
        
        # If no filter or filter matches
        if not filter_expr or evaluate_filter(filter_expr, entity_data):
            # For critical messages with acknowledgments, create a unique ID for this multi-entity group
            if request_acknowledgment:
                # Deep copy data to avoid modifying the original
                message_data = copy.deepcopy(data)
                
                # Create unique acknowledgment ID for this multi-entity group
                room_hash = room_name.split('_')[-1] if '_' in room_name else 'default'
                ack_id = f"{entity_type}_multi_{room_hash}_{time.time()}_{hash(str(message_data))}"[-32:]
                
                # Add acknowledgment request to data
                if isinstance(message_data, dict):
                    message_data['_ack'] = {
                        'id': ack_id,
                        'timestamp': time.time()
                    }
                
                # Record pending acknowledgment in analytics
                websocket_analytics.record_stat('ack_requests', 1)
                websocket_analytics.record_stat('multi_entity_ack_requests', 1)
                
                logger.debug(f"Requesting multi-entity acknowledgment {ack_id} for {entity_type} message")
                
                # Emit message with acknowledgment
                socketio.emit(event_name, message_data, room=room_name)
            else:
                # Normal emit without acknowledgment
                socketio.emit(event_name, original_data, room=room_name)
            
            # Count subscribers
            subscriber_count = len(room_data.get('sessions', set()))
            notified_count += subscriber_count
            
            # Track message in analytics for each subscriber
            message_size = len(json.dumps(data))
            for session_id in room_data.get('sessions', set()):
                websocket_analytics.record_message(session_id, message_size, is_incoming=False)
            
    return notified_count

def evaluate_filter(filter_expr, entity_data):
    """
    Evaluate if entity data matches a filter expression.
    
    Args:
        filter_expr (dict): Filter expression
        entity_data (dict): Entity data
        
    Returns:
        bool: True if entity matches filter, False otherwise
    """
    from app.services.websocket_filter_cache import filter_cache
    from app.services.websocket_analytics_service import websocket_analytics
    
    # Skip empty filters
    if not filter_expr:
        return True
    
    try:
        # Get entity type and ID
        entity_type = entity_data.get('entity_type')
        entity_id = entity_data.get('id') or entity_data.get('entity_id')
        
        # Only use cache if we have entity type and ID
        if entity_type and entity_id:
            # Check cache for previously computed result
            cached_result = filter_cache.get_cached_result(entity_type, entity_id, filter_expr)
            if cached_result is not None:
                websocket_analytics.record_stat('filter_cache_hit', 1)
                return cached_result
            
            # No cache hit, track miss
            websocket_analytics.record_stat('filter_cache_miss', 1)
        
        # Start evaluation timer for analytics
        start_time = time.time()
        
        # Evaluate filter expression
        result = _evaluate_filter_internal(filter_expr, entity_data)
        
        # Track filter evaluation time
        eval_time_ms = (time.time() - start_time) * 1000
        websocket_analytics.record_stat('filter_eval_time_ms', eval_time_ms)
        
        # Cache result if we have entity type and ID
        if entity_type and entity_id:
            filter_cache.cache_result(entity_type, entity_id, filter_expr, result)
        
        return result
    except Exception as e:
        logger.error(f"Error evaluating filter: {str(e)}")
        return False

def _evaluate_filter_internal(filter_expr, entity_data):
    """
    Internal filter evaluation logic.
    
    Args:
        filter_expr (dict): Filter expression
        entity_data (dict): Entity data
        
    Returns:
        bool: True if entity matches filter, False otherwise
    """
    # Simple condition
    if all(k in filter_expr for k in ['field', 'op', 'value']):
        field = filter_expr['field']
        op = filter_expr['op']
        value = filter_expr['value']
        
        # Check if field exists in entity data
        if field not in entity_data:
            return False
            
        # Get field value
        field_value = entity_data[field]
        
        # Evaluate condition
        if op == 'eq':
            return field_value == value
        elif op == 'neq':
            return field_value != value
        elif op == 'gt':
            return field_value > value
        elif op == 'gte':
            return field_value >= value
        elif op == 'lt':
            return field_value < value
        elif op == 'lte':
            return field_value <= value
        elif op == 'contains':
            return value in field_value if isinstance(field_value, (str, list, dict)) else False
        elif op == 'startswith':
            return field_value.startswith(value) if isinstance(field_value, str) else False
        elif op == 'endswith':
            return field_value.endswith(value) if isinstance(field_value, str) else False
            
        # Unknown operator
        return False
        
    # Complex condition with operator and conditions
    if 'operator' in filter_expr and 'conditions' in filter_expr:
        operator = filter_expr['operator']
        conditions = filter_expr['conditions']
        
        # Apply predicate pushdown optimization
        if operator == 'AND':
            # For AND, evaluate inexpensive conditions first
            conditions_sorted = sorted(conditions, key=_get_condition_cost)
            
            # Short-circuit evaluation - return False on first False
            for cond in conditions_sorted:
                if not _evaluate_filter_internal(cond, entity_data):
                    return False
            return True
            
        elif operator == 'OR':
            # For OR, also evaluate inexpensive conditions first
            conditions_sorted = sorted(conditions, key=_get_condition_cost)
            
            # Short-circuit evaluation - return True on first True
            for cond in conditions_sorted:
                if _evaluate_filter_internal(cond, entity_data):
                    return True
            return False
            
        # Unknown operator
        return False
        
    # Invalid filter
    return False

def _get_condition_cost(condition):
    """
    Estimate computational cost of a filter condition.
    Lower values are evaluated first.
    
    Args:
        condition (dict): Filter condition
        
    Returns:
        int: Estimated cost (0-100)
    """
    # Simple conditions
    if all(k in condition for k in ['field', 'op', 'value']):
        op = condition['op']
        
        # Equality checks are very fast
        if op == 'eq' or op == 'neq':
            return 10
            
        # Comparison operations are also fast
        elif op in ['gt', 'gte', 'lt', 'lte']:
            return 20
            
        # String operations are more expensive
        elif op == 'startswith' or op == 'endswith':
            return 30
            
        # Contains is most expensive
        elif op == 'contains':
            return 40
            
        return 50
        
    # Complex conditions are most expensive
    elif 'operator' in condition and 'conditions' in condition:
        # Recursive cost calculation
        if len(condition['conditions']) == 0:
            return 0
            
        # Base cost plus average cost of subconditions
        subcondition_cost = sum(_get_condition_cost(c) for c in condition['conditions'])
        avg_cost = subcondition_cost / len(condition['conditions'])
        
        # AND is slightly cheaper than OR due to short-circuiting
        if condition['operator'] == 'AND':
            return 60 + avg_cost
        else:
            return 70 + avg_cost
            
    # Unknown conditions are most expensive
    return 100

def compress_payload(payload):
    """
    Compress a payload using zlib if it's large enough.
    
    Args:
        payload (dict): The payload to compress
        
    Returns:
        dict: The compressed payload or original payload if too small
    """
    # Convert payload to JSON
    json_payload = json.dumps(payload)
    payload_size = len(json_payload)
    
    # Skip compression for small payloads
    if payload_size < MIN_COMPRESSION_SIZE:
        return {
            'compressed': False,
            'data': payload,
            'original_size': payload_size
        }
    
    # Compress the payload
    try:
        compressed_data = zlib.compress(json_payload.encode('utf-8'), COMPRESSION_LEVEL)
        b64_data = base64.b64encode(compressed_data).decode('utf-8')
        
        compressed_size = len(b64_data)
        bytes_saved = payload_size - compressed_size
        
        # Update compression stats
        with message_batch_lock:
            message_stats['compressed_messages'] += 1
            message_stats['total_bytes_saved'] += bytes_saved
        
        return {
            'compressed': True,
            'data': b64_data,
            'original_size': payload_size,
            'compressed_size': compressed_size
        }
    except Exception as e:
        logger.error(f"Compression failed: {str(e)}")
        return {
            'compressed': False,
            'data': payload,
            'original_size': payload_size
        }

def get_batch_interval(entity_type=None, message_count=0):
    """
    Get the appropriate batch interval based on entity type and system load.
    
    Args:
        entity_type (str, optional): Type of entity being updated
        message_count (int, optional): Number of messages in current batch
        
    Returns:
        float: Batch interval in seconds
    """
    # Start with entity type-specific interval or default
    interval = BATCH_INTERVALS.get(entity_type, BATCH_INTERVALS['default'])
    
    # Apply adaptive batching based on message count
    if message_count > BATCH_LOAD_THRESHOLD:
        # Calculate load factor (1.0 = threshold, 2.0 = 2x threshold)
        load_factor = message_count / BATCH_LOAD_THRESHOLD
        
        # Adjust interval between MIN and MAX based on load
        interval = min(MAX_BATCH_INTERVAL, 
                     max(MIN_BATCH_INTERVAL, 
                         interval * load_factor))
    
    return interval

def batch_emit(event_name, data, room=None):
    """
    Add a message to the batch queue for a room or session.
    
    Args:
        event_name (str): Event name to emit
        data (dict): Event data to emit
        room (str, optional): Room name to emit to
        
    Returns:
        bool: True if message was batched, False if sent immediately
    """
    global message_batch_timer
    
    # If no room is specified, skip batching
    if room is None:
        socketio.emit(event_name, data)
        return False
    
    # Get sessions for this room
    sessions = []
    if room.startswith('user_') or room.startswith('team_') or room.startswith('global'):
        # These are broadcast rooms, don't batch for efficiency
        socketio.emit(event_name, data, room=room)
        return False
    
    # Calculate message size for analytics
    message_size = len(json.dumps(data))
    
    # Determine message priority
    is_high_priority = False
    entity_type = None
    
    # Check if this is an entity update and extract entity type
    if isinstance(data, dict) and data.get('type') == 'entity_update':
        entity_type = data.get('entity_type')
        update_type = data.get('update_type')
        
        # Some update types are high priority (created, deleted, status_change)
        if update_type in ['created', 'deleted', 'status_change', 'error']:
            is_high_priority = True
    
    # Add message to batch for each session in the room
    with message_batch_lock:
        # For entity rooms, find the actual sessions
        if room in socketio.server.rooms:
            for sid in socketio.server.rooms[room]:
                sessions.append(sid)
            
            # Add message to each session's batch
            for sid in sessions:
                # Add message with metadata
                message_batches[sid].append({
                    'event': event_name,
                    'data': data,
                    'entity_type': entity_type,
                    'is_high_priority': is_high_priority,
                    'timestamp': time.time()
                })
                message_stats['batched_messages'] += 1
                
                # Record message in analytics
                websocket_analytics.record_message(sid, message_size, is_incoming=False)
        else:
            # Direct to a specific session
            message_batches[room].append({
                'event': event_name,
                'data': data,
                'entity_type': entity_type,
                'is_high_priority': is_high_priority,
                'timestamp': time.time()
            })
            message_stats['batched_messages'] += 1
            
            # Record message in analytics
            websocket_analytics.record_message(room, message_size, is_incoming=False)
        
        # Start timer if not already running - use adaptive interval
        if message_batch_timer is None:
            # Get total message count for load-based adaptation
            total_message_count = sum(len(batch) for batch in message_batches.values())
            
            # Get appropriate batch interval
            batch_interval = get_batch_interval(entity_type, total_message_count)
            
            # Start the background task
            message_batch_timer = socketio.start_background_task(
                process_message_batches, batch_interval)
            
    return True

def process_message_batches(batch_interval=None):
    """
    Process all pending message batches and send them to clients.
    
    Args:
        batch_interval (float, optional): Override for batch interval
    """
    global message_batch_timer
    
    # Use provided interval or default
    if batch_interval is None:
        batch_interval = DEFAULT_BATCH_INTERVAL
    
    # Sleep for batch interval to collect messages
    socketio.sleep(batch_interval)
    
    with message_batch_lock:
        # Copy and clear the current batches
        current_batches = message_batches.copy()
        message_batches.clear()
        
        # Reset the timer
        message_batch_timer = None
    
    # Track batch stats for analytics
    batch_sizes = []
    batch_entity_types = defaultdict(int)
    high_priority_msgs = 0
    batch_processing_start = time.time()
    
    # Process each batch
    for sid, messages in current_batches.items():
        if not messages:
            continue
            
        # Skip if only one message, just send directly
        if len(messages) == 1:
            socketio.emit(messages[0]['event'], messages[0]['data'], room=sid)
            
            # Update stats
            direct_message_size = len(json.dumps(messages[0]['data']))
            message_stats['total_messages_sent'] += 1
            message_stats['total_bytes_sent'] += direct_message_size
            
            continue
        
        # Group messages by entity type for more efficient processing
        messages_by_entity = defaultdict(list)
        high_priority = []
        
        # Check for high priority messages that should be sent immediately
        for msg in messages:
            if msg.get('is_high_priority', False):
                high_priority.append(msg)
                high_priority_msgs += 1
            else:
                entity_type = msg.get('entity_type') or 'unknown'
                messages_by_entity[entity_type].append(msg)
                batch_entity_types[entity_type] += 1
        
        # Send high priority messages first, individually
        for msg in high_priority:
            socketio.emit(msg['event'], msg['data'], room=sid)
            message_stats['total_messages_sent'] += 1
            
            # Update stats for analytics
            direct_message_size = len(json.dumps(msg['data']))
            message_stats['total_bytes_sent'] += direct_message_size
        
        # Process each entity type batch
        for entity_type, entity_messages in messages_by_entity.items():
            if not entity_messages:
                continue
                
            batch_sizes.append(len(entity_messages))
            
            # Prepare batch message
            batch_data = {
                'type': 'batch',
                'messages': entity_messages,
                'count': len(entity_messages),
                'entity_type': entity_type,
                'timestamp': time.time()
            }
            
            # Compress the batch if it's large enough
            payload_json = json.dumps(batch_data)
            original_size = len(payload_json)
            bytes_saved = 0
            
            message_stats['total_messages_sent'] += 1
            
            # Track batch effectiveness in analytics 
            # (difference between sum of individual messages and batch size)
            individual_message_sizes = sum(len(json.dumps(msg['data'])) for msg in entity_messages)
            batch_overhead = original_size - individual_message_sizes
            
            # Record batch metrics
            websocket_analytics.record_stat('batch_overhead_bytes', batch_overhead)
            websocket_analytics.record_stat('batch_size', len(entity_messages))
            websocket_analytics.record_stat(f'batch_entity_{entity_type}', len(entity_messages))
            
            if original_size >= MIN_COMPRESSION_SIZE:
                # Use compression
                compressed_result = compress_payload(batch_data)
                bytes_saved = original_size - compressed_result['compressed_size']
                message_stats['total_bytes_sent'] += compressed_result['compressed_size']
                
                # Record combined batch+compression savings in analytics
                websocket_analytics.record_message(sid, compressed_result['compressed_size'], is_incoming=False)
                websocket_analytics.record_stat('compression_bytes_saved', bytes_saved)
                
                socketio.emit('batch', compressed_result, room=sid)
            else:
                # Send uncompressed batch
                message_stats['total_bytes_sent'] += original_size
                socketio.emit('batch', batch_data, room=sid)
    
    # Record batch processing stats
    batch_processing_time = (time.time() - batch_processing_start) * 1000  # ms
    websocket_analytics.record_stat('batch_processing_time_ms', batch_processing_time)
    
    # Log batch processing summary if any batches were processed
    if batch_sizes:
        avg_batch_size = sum(batch_sizes) / len(batch_sizes)
        logger.debug(f"Processed {len(batch_sizes)} batches, avg size: {avg_batch_size:.1f}, " +
                    f"high priority: {high_priority_msgs}, processing time: {batch_processing_time:.2f}ms")

def reset_message_stats():
    """Reset the message statistics."""
    with message_batch_lock:
        for key in message_stats:
            if key != 'last_reset':
                message_stats[key] = 0
        message_stats['last_reset'] = time.time()

def initialize_socketio(app):
    """
    Initialize SocketIO with the Flask app.
    
    Args:
        app: Flask application
    """
    # Enable Flask-SocketIO's message queue support if Redis is available
    message_queue = None
    if app.config.get('REDIS_URL'):
        message_queue = app.config.get('REDIS_URL')
    
    # Initialize SocketIO
    socketio.init_app(
        app,
        cors_allowed_origins="*",  # Adjust for production
        message_queue=message_queue,
        async_mode='eventlet',  # Use eventlet for best performance
        # Enable websocket compression in the transport layer
        compression_options={'threshold': MIN_COMPRESSION_SIZE}
    )
    
    # Add compression and batching configuration to the app config
    app.config['WEBSOCKET_COMPRESSION_ENABLED'] = True
    app.config['WEBSOCKET_BATCH_INTERVAL'] = BATCH_INTERVAL
    
    # Set up periodic stat reset task
    socketio.start_background_task(periodic_stats_reset)
    
    # Set up periodic analytics collection task
    socketio.start_background_task(periodic_analytics_collection)
    
    # Set up periodic idle connection cleanup task
    socketio.start_background_task(periodic_idle_connection_cleanup)
    
    logger.info("WebSocket server initialized with batching, compression, and analytics")
    
    return socketio
    
def periodic_analytics_collection():
    """Collect analytics metrics every minute."""
    while True:
        socketio.sleep(60)  # 1 minute
        websocket_analytics.collect_minute_metrics()
        
def periodic_idle_connection_cleanup():
    """Check for and close idle connections every 5 minutes."""
    while True:
        socketio.sleep(300)  # 5 minutes
        idle_sessions = websocket_analytics.detect_idle_connections(idle_threshold_seconds=600)
        
        # Close idle connections
        for session_id in idle_sessions:
            try:
                logger.info(f"Closing idle connection: {session_id}")
                socketio.server.disconnect(session_id)
            except Exception as e:
                logger.error(f"Error closing idle connection {session_id}: {str(e)}")
    
def periodic_stats_reset():
    """Reset message stats every hour."""
    while True:
        socketio.sleep(3600)  # 1 hour
        reset_message_stats()
        logger.info("WebSocket message stats reset")