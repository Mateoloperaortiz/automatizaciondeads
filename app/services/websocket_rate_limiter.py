"""
WebSocket Rate Limiter Service

Service for rate limiting WebSocket connections and subscriptions.
"""

import time
import threading
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger('websocket_rate_limiter')

class TokenBucket:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, rate, capacity):
        """
        Initialize the token bucket.
        
        Args:
            rate (float): Tokens per second
            capacity (int): Maximum bucket capacity
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
        
    def consume(self, tokens=1):
        """
        Consume tokens from the bucket.
        
        Args:
            tokens (int): Number of tokens to consume
            
        Returns:
            bool: True if tokens were consumed, False if not enough tokens
        """
        with self.lock:
            # Refill tokens based on elapsed time
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now
            
            # Check if enough tokens
            if tokens <= self.tokens:
                self.tokens -= tokens
                return True
            else:
                return False

class SlidingWindowCounter:
    """Sliding window counter for rate limiting."""
    
    def __init__(self, window_size, max_requests):
        """
        Initialize the sliding window counter.
        
        Args:
            window_size (int): Window size in seconds
            max_requests (int): Maximum requests in window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self.lock = threading.Lock()
        
    def check_and_add(self):
        """
        Check if request can be processed and add it.
        
        Returns:
            bool: True if request can be processed, False otherwise
        """
        with self.lock:
            now = time.time()
            
            # Remove expired entries
            cutoff = now - self.window_size
            while self.requests and self.requests[0] <= cutoff:
                self.requests.popleft()
                
            # Check if limit exceeded
            if len(self.requests) >= self.max_requests:
                return False
                
            # Add new request
            self.requests.append(now)
            return True
            
    def get_retry_after(self):
        """
        Get retry after time in seconds.
        
        Returns:
            float: Seconds until the next request can be made
        """
        with self.lock:
            if not self.requests or len(self.requests) < self.max_requests:
                return 0
                
            oldest = self.requests[0]
            return oldest + self.window_size - time.time()

class WebSocketRateLimiterService:
    """Service for rate limiting WebSocket operations."""
    
    def __init__(self):
        """Initialize the WebSocket rate limiter service."""
        # Default rate limits
        self.default_limits = {
            'connection': {'window': 60, 'max_requests': 10},     # 10 connections per minute
            'subscription': {'window': 60, 'max_requests': 50},    # 50 subscriptions per minute
            'message': {'window': 60, 'max_requests': 100}        # 100 messages per minute
        }
        
        # Per-user rate limiters (sliding window)
        self.user_limiters = defaultdict(lambda: {
            'connection': SlidingWindowCounter(
                self.default_limits['connection']['window'],
                self.default_limits['connection']['max_requests']
            ),
            'subscription': SlidingWindowCounter(
                self.default_limits['subscription']['window'],
                self.default_limits['subscription']['max_requests']
            ),
            'message': SlidingWindowCounter(
                self.default_limits['message']['window'],
                self.default_limits['message']['max_requests']
            )
        })
        
        # Per-IP rate limiters (more strict token bucket for unauthenticated users)
        self.ip_limiters = defaultdict(lambda: {
            'connection': TokenBucket(0.2, 5),      # 0.2 tokens/sec, max 5 
            'subscription': TokenBucket(1, 10),     # 1 token/sec, max 10
            'message': TokenBucket(2, 20)           # 2 tokens/sec, max 20
        })
        
        # Track blocked requests for analytics
        self.blocked_stats = defaultdict(int)
        
        # Cleanup thread for inactive limiters
        self.cleanup_thread = threading.Thread(target=self._cleanup_limiters, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("WebSocket Rate Limiter Service initialized")
        
    def check_rate_limit(self, operation, user_id=None, ip=None):
        """
        Check if an operation is rate limited.
        
        Args:
            operation (str): Operation type (connection, subscription, message)
            user_id (int, optional): User ID if authenticated
            ip (str, optional): IP address for unauthenticated users
            
        Returns:
            tuple: (allowed, retry_after) - allowed is boolean, retry_after in seconds
        """
        # Validate operation
        if operation not in self.default_limits:
            # Unknown operation, default to allow
            return True, 0
            
        # If authenticated, use user-based limiting
        if user_id is not None:
            limiter = self.user_limiters[user_id][operation]
            allowed = limiter.check_and_add()
            
            if not allowed:
                retry_after = limiter.get_retry_after()
                # Log and track blocked request
                self._track_blocked_request(operation, user_id=user_id)
                return False, retry_after
                
            return True, 0
            
        # If unauthenticated but we have IP, use IP-based limiting
        elif ip is not None:
            limiter = self.ip_limiters[ip][operation]
            allowed = limiter.consume()
            
            if not allowed:
                # For token bucket, suggest retry after 1 second 
                # (could be more sophisticated)
                retry_after = 1.0
                # Log and track blocked request
                self._track_blocked_request(operation, ip=ip)
                return False, retry_after
                
            return True, 0
            
        # No user_id or IP, default to allow
        return True, 0
        
    def _track_blocked_request(self, operation, user_id=None, ip=None):
        """
        Track a blocked request for analytics.
        
        Args:
            operation (str): Operation type
            user_id (int, optional): User ID
            ip (str, optional): IP address
        """
        key = f"{operation}:user:{user_id}" if user_id else f"{operation}:ip:{ip}"
        self.blocked_stats[key] += 1
        
        # Log the blocked request
        if user_id:
            logger.warning(f"Rate limited {operation} for user {user_id}")
        else:
            logger.warning(f"Rate limited {operation} for IP {ip}")
            
    def _cleanup_limiters(self):
        """Periodically clean up inactive limiters."""
        while True:
            # Sleep for 5 minutes
            time.sleep(300)
            
            # Remove old IP limiters to prevent memory leaks
            # In a real production app, consider using a TTL cache
            self.ip_limiters.clear()
            
            # Could also clean up user limiters for inactive users
            # For now, just log cleanup
            logger.debug("Rate limiter cleanup completed")
            
    def get_rate_limit_stats(self):
        """
        Get rate limiting statistics.
        
        Returns:
            dict: Rate limiting statistics
        """
        return {
            'blocked_requests': dict(self.blocked_stats),
            'active_user_limiters': len(self.user_limiters),
            'active_ip_limiters': len(self.ip_limiters)
        }

# Create singleton instance
websocket_rate_limiter = WebSocketRateLimiterService()