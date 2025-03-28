"""
Caching mechanisms for the API Integration Framework.

This module provides caching functionality for API requests and responses,
including a TTL (time-to-live) based cache implementation.
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, TypeVar, Generic, Callable

from app.api_framework.base import APIRequest, APIResponse

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar('T')


class APICache:
    """
    Abstract base class for API caching implementations.
    
    This class defines the interface that all cache implementations must support.
    """
    
    def get(self, key: str) -> Optional[APIResponse]:
        """
        Get a response from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response if available and valid, None otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
        
    def set(self, key: str, response: APIResponse) -> None:
        """
        Store a response in the cache.
        
        Args:
            key: Cache key
            response: API response to cache
        """
        raise NotImplementedError("Subclasses must implement this method")
        
    def delete(self, key: str) -> None:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key to delete
        """
        raise NotImplementedError("Subclasses must implement this method")
        
    def clear(self) -> None:
        """Clear all items from the cache."""
        raise NotImplementedError("Subclasses must implement this method")


class TTLCache(APICache):
    """
    Time-to-live (TTL) based cache implementation.
    
    This cache automatically expires entries after a specified duration.
    """
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000,
                 cleanup_interval: int = 60):
        """
        Initialize the TTL cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
            max_size: Maximum number of items to store
            cleanup_interval: Interval between cleanup runs in seconds
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
    def get(self, key: str) -> Optional[APIResponse]:
        """
        Get a response from the cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response if available and valid, None otherwise
        """
        with self.lock:
            if key not in self.cache:
                return None
                
            entry = self.cache[key]
            
            # Check if entry has expired
            if time.time() > entry['expires_at']:
                del self.cache[key]
                return None
                
            response_dict = entry['value']
            return APIResponse.from_dict(response_dict)
        
    def set(self, key: str, response: APIResponse, ttl: Optional[int] = None) -> None:
        """
        Store a response in the cache with an expiration time.
        
        Args:
            key: Cache key
            response: API response to cache
            ttl: Time-to-live in seconds (default: self.default_ttl)
        """
        if ttl is None:
            ttl = self.default_ttl
            
        expires_at = time.time() + ttl
        
        with self.lock:
            # Ensure we're not exceeding max size
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_oldest()
                
            self.cache[key] = {
                'value': response.to_dict(),
                'created_at': time.time(),
                'expires_at': expires_at
            }
            
    def delete(self, key: str) -> None:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key to delete
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self.lock:
            self.cache.clear()
            
    def _evict_oldest(self) -> None:
        """Evict the oldest item from the cache."""
        oldest_key = None
        oldest_time = float('inf')
        
        # Find the oldest entry
        for key, entry in self.cache.items():
            if entry['created_at'] < oldest_time:
                oldest_time = entry['created_at']
                oldest_key = key
                
        # Remove it
        if oldest_key:
            del self.cache[oldest_key]
            
    def _cleanup_expired(self) -> None:
        """Remove expired entries from the cache."""
        now = time.time()
        
        with self.lock:
            # Get keys to delete (to avoid modifying dict during iteration)
            keys_to_delete = [
                key for key, entry in self.cache.items()
                if now > entry['expires_at']
            ]
            
            # Delete expired entries
            for key in keys_to_delete:
                del self.cache[key]
                
    def _start_cleanup_thread(self) -> None:
        """Start a background thread to periodically clean up expired entries."""
        def cleanup_worker():
            while True:
                time.sleep(self.cleanup_interval)
                try:
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Error in cache cleanup: {str(e)}")
                    
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()


class MemoryCache(Generic[T]):
    """
    Simple in-memory cache with optional TTL.
    
    This is a more generic cache implementation that can be used
    for purposes other than caching API responses.
    """
    
    def __init__(self, default_ttl: Optional[int] = None):
        """
        Initialize memory cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (None for no expiration)
        """
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """
        Get an item from the cache.
        
        Args:
            key: Cache key
            default: Value to return if key is not found
            
        Returns:
            Cached value if available and valid, default otherwise
        """
        if key not in self.cache:
            return default
            
        entry = self.cache[key]
        
        # Check if entry has TTL and has expired
        if 'expires_at' in entry and time.time() > entry['expires_at']:
            del self.cache[key]
            return default
            
        return entry['value']
        
    def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """
        Store an item in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None uses default, 0 means never expire)
        """
        entry = {'value': value}
        
        # Calculate expiration if TTL is set
        if ttl is not None or self.default_ttl is not None:
            # Use provided TTL or fall back to default
            effective_ttl = ttl if ttl is not None else self.default_ttl
            if effective_ttl > 0:  # Only set expires_at if TTL is positive
                entry['expires_at'] = time.time() + effective_ttl
                
        self.cache[key] = entry
        
    def delete(self, key: str) -> None:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key to delete
        """
        if key in self.cache:
            del self.cache[key]
            
    def clear(self) -> None:
        """Clear all items from the cache."""
        self.cache.clear()
        
    def get_or_set(self, key: str, default_factory: Callable[[], T], 
                   ttl: Optional[int] = None) -> T:
        """
        Get an item from the cache, or set it using a factory function.
        
        Args:
            key: Cache key
            default_factory: Function to call to create the value if not in cache
            ttl: Time-to-live in seconds
            
        Returns:
            Cached or newly created value
        """
        value = self.get(key)
        if value is None:
            value = default_factory()
            self.set(key, value, ttl)
        return value