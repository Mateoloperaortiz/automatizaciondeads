"""
WebSocket Analytics Service

Service for tracking WebSocket connection metrics and performance statistics.
"""

from datetime import datetime, timedelta
import time
import threading
import json
import logging
from collections import defaultdict, deque

logger = logging.getLogger('websocket_analytics')

class WebSocketAnalyticsService:
    """Service for tracking WebSocket connection metrics and performance statistics."""
    
    def __init__(self):
        """Initialize the WebSocket analytics service."""
        # Time series data for metrics
        self.time_series = {
            'active_connections': deque(maxlen=1440),  # 24 hours of minute-by-minute data
            'messages_per_minute': deque(maxlen=1440),
            'bytes_per_minute': deque(maxlen=1440),
            'latency': deque(maxlen=1440),
            'subscription_counts': deque(maxlen=1440),
            'error_counts': deque(maxlen=1440),
            'filter_cache_hits': deque(maxlen=1440),
            'filter_cache_misses': deque(maxlen=1440),
            'filter_eval_time_ms': deque(maxlen=1440)
        }
        
        # Current minute metrics
        self.current_metrics = {
            'message_count': 0,
            'byte_count': 0,
            'latency_sum': 0,
            'latency_count': 0,
            'error_count': 0,
            'connection_count': 0,
            'disconnection_count': 0,
            'subscription_count': 0,
            'unsubscription_count': 0,
            'filter_cache_hits': 0,
            'filter_cache_misses': 0,
            'filter_eval_count': 0,
            'filter_eval_time_ms_sum': 0
        }
        
        # Real-time stats tracking
        self.realtime_stats = defaultdict(int)
        
        # Connection tracking
        self.connections = {}
        self.connection_count = 0
        
        # Subscription tracking by entity type
        self.subscription_counts = defaultdict(int)
        
        # Error tracking
        self.errors = defaultdict(int)
        
        # Peak metrics
        self.peak_metrics = {
            'connections': 0,
            'messages_per_minute': 0,
            'bytes_per_minute': 0,
            'subscriptions': 0,
            'filter_cache_hit_rate': 0
        }
        
        # Protection against data races
        self.lock = threading.Lock()
        
        # Start periodic metrics collection
        self.last_collection_time = time.time()
        
        # Setup complete
        logger.info("WebSocket Analytics Service initialized")
    
    def record_connection(self, session_id, user_id=None):
        """
        Record a new WebSocket connection.
        
        Args:
            session_id (str): WebSocket session ID
            user_id (int, optional): User ID if authenticated
        """
        with self.lock:
            self.connections[session_id] = {
                'connected_at': datetime.utcnow(),
                'user_id': user_id,
                'message_count': 0,
                'byte_count': 0,
                'subscriptions': set(),
                'last_activity': datetime.utcnow()
            }
            self.connection_count += 1
            self.current_metrics['connection_count'] += 1
            
            # Update peak connections if needed
            active_count = len(self.connections)
            if active_count > self.peak_metrics['connections']:
                self.peak_metrics['connections'] = active_count
    
    def record_disconnection(self, session_id):
        """
        Record a WebSocket disconnection.
        
        Args:
            session_id (str): WebSocket session ID
        """
        with self.lock:
            if session_id in self.connections:
                connected_at = self.connections[session_id]['connected_at']
                duration = (datetime.utcnow() - connected_at).total_seconds()
                
                # Log disconnection with session duration
                logger.info(f"WebSocket disconnection: {session_id}, Duration: {duration:.2f}s")
                
                # Remove subscriptions associated with this session
                for subscription in self.connections[session_id]['subscriptions']:
                    entity_type = subscription.split(':')[0]
                    self.subscription_counts[entity_type] -= 1
                
                # Remove the connection
                del self.connections[session_id]
                self.current_metrics['disconnection_count'] += 1
    
    def record_message(self, session_id, message_size, is_incoming=True):
        """
        Record a WebSocket message.
        
        Args:
            session_id (str): WebSocket session ID
            message_size (int): Size of message in bytes
            is_incoming (bool): True if message is from client to server
        """
        with self.lock:
            # Update session metrics
            if session_id in self.connections:
                self.connections[session_id]['message_count'] += 1
                self.connections[session_id]['byte_count'] += message_size
                self.connections[session_id]['last_activity'] = datetime.utcnow()
            
            # Update current minute metrics
            self.current_metrics['message_count'] += 1
            self.current_metrics['byte_count'] += message_size
    
    def record_subscription(self, session_id, entity_type, entity_id=None, filter_expression=None):
        """
        Record a new entity subscription.
        
        Args:
            session_id (str): WebSocket session ID
            entity_type (str): Type of entity
            entity_id (str, optional): ID of entity if direct subscription
            filter_expression (dict, optional): Filter expression if filtered subscription
        """
        with self.lock:
            # Create subscription key
            if entity_id:
                subscription_key = f"{entity_type}:{entity_id}"
            elif filter_expression:
                # For filtered subscriptions, use a special key format
                subscription_key = f"{entity_type}:filter"
            else:
                subscription_key = f"{entity_type}:all"
            
            # Add to session subscriptions
            if session_id in self.connections:
                self.connections[session_id]['subscriptions'].add(subscription_key)
                self.connections[session_id]['last_activity'] = datetime.utcnow()
            
            # Update entity type count
            self.subscription_counts[entity_type] += 1
            
            # Update metrics
            self.current_metrics['subscription_count'] += 1
            
            # Update peak subscriptions if needed
            total_subscriptions = sum(self.subscription_counts.values())
            if total_subscriptions > self.peak_metrics['subscriptions']:
                self.peak_metrics['subscriptions'] = total_subscriptions
    
    def record_unsubscription(self, session_id, entity_type, entity_id=None):
        """
        Record an entity unsubscription.
        
        Args:
            session_id (str): WebSocket session ID
            entity_type (str): Type of entity
            entity_id (str, optional): ID of entity if direct subscription
        """
        with self.lock:
            # Create subscription key
            subscription_key = f"{entity_type}:{entity_id}" if entity_id else f"{entity_type}:filter"
            
            # Remove from session subscriptions
            if session_id in self.connections:
                if subscription_key in self.connections[session_id]['subscriptions']:
                    self.connections[session_id]['subscriptions'].remove(subscription_key)
                    self.connections[session_id]['last_activity'] = datetime.utcnow()
                    
                    # Update entity type count
                    self.subscription_counts[entity_type] -= 1
                    
                    # Update metrics
                    self.current_metrics['unsubscription_count'] += 1
    
    def record_latency(self, session_id, latency_ms):
        """
        Record WebSocket message latency.
        
        Args:
            session_id (str): WebSocket session ID
            latency_ms (float): Round-trip latency in milliseconds
        """
        with self.lock:
            # Update current minute metrics
            self.current_metrics['latency_sum'] += latency_ms
            self.current_metrics['latency_count'] += 1
            
            # Update session last activity
            if session_id in self.connections:
                self.connections[session_id]['last_activity'] = datetime.utcnow()
    
    def record_error(self, session_id, error_type, error_message):
        """
        Record a WebSocket error.
        
        Args:
            session_id (str): WebSocket session ID
            error_type (str): Type of error
            error_message (str): Error message
        """
        with self.lock:
            # Update error counts
            self.errors[error_type] += 1
            
            # Update current minute metrics
            self.current_metrics['error_count'] += 1
            
            # Update session last activity
            if session_id in self.connections:
                self.connections[session_id]['last_activity'] = datetime.utcnow()
            
            # Log the error
            logger.error(f"WebSocket error ({error_type}): {error_message}, Session: {session_id}")
    
    def collect_minute_metrics(self):
        """
        Collect and store metrics for the current minute.
        Should be called every minute.
        """
        with self.lock:
            current_time = time.time()
            time_diff = current_time - self.last_collection_time
            
            # Only collect if at least 30 seconds have passed
            if time_diff < 30:
                return
                
            # Calculate derived metrics
            active_connections = len(self.connections)
            
            # Calculate average latency
            avg_latency = 0
            if self.current_metrics['latency_count'] > 0:
                avg_latency = self.current_metrics['latency_sum'] / self.current_metrics['latency_count']
            
            # Calculate filter cache hit rate
            filter_cache_hit_rate = 0
            total_filter_lookups = self.current_metrics['filter_cache_hits'] + self.current_metrics['filter_cache_misses']
            if total_filter_lookups > 0:
                filter_cache_hit_rate = (self.current_metrics['filter_cache_hits'] / total_filter_lookups) * 100
            
            # Calculate average filter evaluation time
            avg_filter_eval_time = 0
            if self.current_metrics['filter_eval_count'] > 0:
                avg_filter_eval_time = self.current_metrics['filter_eval_time_ms_sum'] / self.current_metrics['filter_eval_count']
            
            # Record time series data
            timestamp = datetime.utcnow().isoformat()
            
            self.time_series['active_connections'].append({
                'timestamp': timestamp,
                'value': active_connections
            })
            
            messages_per_minute = self.current_metrics['message_count'] * (60 / time_diff)
            self.time_series['messages_per_minute'].append({
                'timestamp': timestamp,
                'value': messages_per_minute
            })
            
            bytes_per_minute = self.current_metrics['byte_count'] * (60 / time_diff)
            self.time_series['bytes_per_minute'].append({
                'timestamp': timestamp,
                'value': bytes_per_minute
            })
            
            self.time_series['latency'].append({
                'timestamp': timestamp,
                'value': avg_latency
            })
            
            total_subscriptions = sum(self.subscription_counts.values())
            self.time_series['subscription_counts'].append({
                'timestamp': timestamp,
                'value': total_subscriptions,
                'by_type': dict(self.subscription_counts)
            })
            
            self.time_series['error_counts'].append({
                'timestamp': timestamp,
                'value': self.current_metrics['error_count'],
                'by_type': dict(self.errors)
            })
            
            # Add filter cache metrics
            self.time_series['filter_cache_hits'].append({
                'timestamp': timestamp,
                'value': self.current_metrics['filter_cache_hits'],
                'hit_rate': filter_cache_hit_rate
            })
            
            self.time_series['filter_cache_misses'].append({
                'timestamp': timestamp,
                'value': self.current_metrics['filter_cache_misses']
            })
            
            self.time_series['filter_eval_time_ms'].append({
                'timestamp': timestamp,
                'value': avg_filter_eval_time,
                'total_evals': self.current_metrics['filter_eval_count']
            })
            
            # Update peak metrics
            if messages_per_minute > self.peak_metrics['messages_per_minute']:
                self.peak_metrics['messages_per_minute'] = messages_per_minute
                
            if bytes_per_minute > self.peak_metrics['bytes_per_minute']:
                self.peak_metrics['bytes_per_minute'] = bytes_per_minute
                
            if filter_cache_hit_rate > self.peak_metrics['filter_cache_hit_rate']:
                self.peak_metrics['filter_cache_hit_rate'] = filter_cache_hit_rate
            
            # Reset current metrics
            self.current_metrics = {
                'message_count': 0,
                'byte_count': 0,
                'latency_sum': 0,
                'latency_count': 0,
                'error_count': 0,
                'connection_count': 0,
                'disconnection_count': 0,
                'subscription_count': 0,
                'unsubscription_count': 0,
                'filter_cache_hits': 0,
                'filter_cache_misses': 0,
                'filter_eval_count': 0,
                'filter_eval_time_ms_sum': 0
            }
            
            # Update collection time
            self.last_collection_time = current_time
            
            # Log collection event
            logger.debug(f"Collected minute metrics. Active connections: {active_connections}, " +
                         f"Messages/min: {messages_per_minute:.2f}, " +
                         f"Bytes/min: {bytes_per_minute:.2f}, " +
                         f"Filter cache hit rate: {filter_cache_hit_rate:.1f}%")
    
    def detect_idle_connections(self, idle_threshold_seconds=600):
        """
        Detect idle connections that should be closed.
        
        Args:
            idle_threshold_seconds (int): Threshold in seconds after which a connection
                                          is considered idle
        
        Returns:
            list: List of session IDs that should be closed
        """
        with self.lock:
            idle_sessions = []
            now = datetime.utcnow()
            
            for session_id, connection in list(self.connections.items()):
                last_activity = connection['last_activity']
                idle_time = (now - last_activity).total_seconds()
                
                if idle_time > idle_threshold_seconds:
                    idle_sessions.append(session_id)
                    
            return idle_sessions
    
    def get_analytics_dashboard_data(self):
        """
        Get data for the analytics dashboard.
        
        Returns:
            dict: Dashboard data
        """
        with self.lock:
            active_connections = len(self.connections)
            
            # Calculate connection durations
            now = datetime.utcnow()
            connection_durations = []
            
            for conn in self.connections.values():
                duration = (now - conn['connected_at']).total_seconds()
                connection_durations.append(duration)
            
            # Calculate average duration
            avg_duration = 0
            if connection_durations:
                avg_duration = sum(connection_durations) / len(connection_durations)
            
            # Get filter cache stats if available
            try:
                from app.services.websocket_filter_cache import filter_cache
                cache_stats = filter_cache.get_stats()
            except (ImportError, AttributeError):
                cache_stats = {
                    'size': 0,
                    'max_size': 0,
                    'hits': 0,
                    'misses': 0,
                    'hit_rate': 0
                }
            
            # Get time series data for charts
            # Use only the last 60 data points (1 hour for minute-by-minute data)
            connection_history = list(self.time_series['active_connections'])[-60:]
            message_history = list(self.time_series['messages_per_minute'])[-60:]
            latency_history = list(self.time_series['latency'])[-60:]
            subscription_history = list(self.time_series['subscription_counts'])[-60:]
            error_history = list(self.time_series['error_counts'])[-60:]
            filter_cache_history = {
                'hits': list(self.time_series['filter_cache_hits'])[-60:],
                'misses': list(self.time_series['filter_cache_misses'])[-60:],
                'eval_time': list(self.time_series['filter_eval_time_ms'])[-60:]
            }
            
            # Get real-time stats
            realtime_stats = dict(self.realtime_stats)
            
            return {
                'current': {
                    'active_connections': active_connections,
                    'subscription_count': sum(self.subscription_counts.values()),
                    'subscription_by_type': dict(self.subscription_counts),
                    'average_connection_duration': avg_duration,
                    'error_count': sum(self.errors.values()),
                    'errors_by_type': dict(self.errors)
                },
                'peak': self.peak_metrics,
                'filter_cache': cache_stats,
                'time_series': {
                    'connections': connection_history,
                    'messages': message_history,
                    'latency': latency_history,
                    'subscriptions': subscription_history,
                    'errors': error_history,
                    'filter_cache': filter_cache_history
                },
                'realtime_stats': realtime_stats
            }
    
    def record_stat(self, stat_name, value):
        """
        Record a statistic for tracking.
        
        Args:
            stat_name (str): Name of the statistic
            value (int/float): Value to record
        """
        with self.lock:
            # Update real-time stats
            self.realtime_stats[stat_name] += value
            
            # Update current minute metrics for known stats
            if stat_name == 'filter_cache_hit':
                self.current_metrics['filter_cache_hits'] += value
            elif stat_name == 'filter_cache_miss':
                self.current_metrics['filter_cache_misses'] += value
            elif stat_name == 'filter_eval_time_ms':
                self.current_metrics['filter_eval_time_ms_sum'] += value
                self.current_metrics['filter_eval_count'] += 1
    
    def get_connection_details(self, session_id=None):
        """
        Get details about active connections.
        
        Args:
            session_id (str, optional): Specific session to get details for
                                        If None, returns details for all sessions
        
        Returns:
            dict: Connection details
        """
        with self.lock:
            if session_id:
                if session_id in self.connections:
                    connection = self.connections[session_id]
                    return {
                        'session_id': session_id,
                        'connected_at': connection['connected_at'].isoformat(),
                        'user_id': connection['user_id'],
                        'message_count': connection['message_count'],
                        'byte_count': connection['byte_count'],
                        'subscriptions': list(connection['subscriptions']),
                        'last_activity': connection['last_activity'].isoformat(),
                        'idle_time': (datetime.utcnow() - connection['last_activity']).total_seconds()
                    }
                return None
            else:
                connections = []
                for sid, conn in self.connections.items():
                    connections.append({
                        'session_id': sid,
                        'connected_at': conn['connected_at'].isoformat(),
                        'user_id': conn['user_id'],
                        'message_count': conn['message_count'],
                        'byte_count': conn['byte_count'],
                        'subscription_count': len(conn['subscriptions']),
                        'last_activity': conn['last_activity'].isoformat(),
                        'idle_time': (datetime.utcnow() - conn['last_activity']).total_seconds()
                    })
                return connections

# Create singleton instance
websocket_analytics = WebSocketAnalyticsService()