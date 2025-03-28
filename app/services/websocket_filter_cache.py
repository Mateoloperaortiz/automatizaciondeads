"""
WebSocket Filter Cache Service

Provides caching for WebSocket filter evaluations to improve performance.
"""

import time
import hashlib
import threading
import logging
from collections import OrderedDict
from datetime import datetime, timedelta

logger = logging.getLogger('websocket_filter_cache')

class LRUCache:
    """
    LRU Cache implementation with TTL (time-to-live) support.
    """
    
    def __init__(self, max_size=1000, ttl_seconds=300):
        """
        Initialize the LRU cache.
        
        Args:
            max_size (int): Maximum number of items in cache
            ttl_seconds (int): Default TTL in seconds
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.expirations = 0
    
    def get(self, key):
        """
        Get a value from the cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            any: Cached value or None if not found or expired
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            value, timestamp = self.cache[key]
            
            # Check TTL
            if timestamp + self.ttl_seconds < time.time():
                # Expired
                del self.cache[key]
                self.expirations += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            
            return value
    
    def put(self, key, value, ttl_seconds=None):
        """
        Add a value to the cache.
        
        Args:
            key (str): Cache key
            value (any): Value to cache
            ttl_seconds (int, optional): TTL override for this item
        """
        with self.lock:
            # If key exists, just update it and move to end
            if key in self.cache:
                self.cache.move_to_end(key)
            
            # Add new item
            self.cache[key] = (value, time.time())
            
            # Evict oldest item if over capacity
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def invalidate(self, key_prefix):
        """
        Invalidate all cache entries with keys starting with key_prefix.
        
        Args:
            key_prefix (str): Prefix for keys to invalidate
            
        Returns:
            int: Number of invalidated entries
        """
        with self.lock:
            to_delete = [k for k in self.cache.keys() if k.startswith(key_prefix)]
            
            for key in to_delete:
                del self.cache[key]
            
            return len(to_delete)
    
    def clear(self):
        """Clear the entire cache."""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self):
        """
        Get cache statistics.
        
        Returns:
            dict: Cache statistics
        """
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'expirations': self.expirations,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }

class FilterEvaluationCache:
    """
    Cache for filter evaluation results to improve WebSocket message delivery performance.
    """
    
    def __init__(self, max_size=5000, default_ttl=300):
        """
        Initialize the filter evaluation cache.
        
        Args:
            max_size (int): Maximum cache size
            default_ttl (int): Default TTL in seconds
        """
        self.cache = LRUCache(max_size=max_size, ttl_seconds=default_ttl)
        self.default_ttl = default_ttl
        self.entity_versions = {}  # {entity_type: {entity_id: version}}
        self.lock = threading.Lock()
        
        # TTL settings for different entity types (customizable)
        self.ttl_settings = {
            'campaign': 600,      # 10 minutes for campaigns
            'segment': 900,       # 15 minutes for segments
            'analytics': 60,      # 1 minute for analytics (frequently changing)
            'job_opening': 1800,  # 30 minutes for job openings (stable)
            'candidate': 1800,    # 30 minutes for candidates (stable)
            'notification': 120,  # 2 minutes for notifications
            'task': 60,           # 1 minute for tasks
            'default': default_ttl
        }
        
        logger.info(f"Filter Evaluation Cache initialized with max_size={max_size}")
    
    def get_entity_version(self, entity_type, entity_id):
        """
        Get the current version for an entity.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str/int): ID of entity
            
        Returns:
            int: Entity version
        """
        with self.lock:
            # Convert entity_id to string for consistency
            entity_id = str(entity_id)
            
            # Initialize entity type dict if not exists
            if entity_type not in self.entity_versions:
                self.entity_versions[entity_type] = {}
            
            # Initialize entity version if not exists
            if entity_id not in self.entity_versions[entity_type]:
                self.entity_versions[entity_type][entity_id] = 1
            
            return self.entity_versions[entity_type][entity_id]
    
    def increment_entity_version(self, entity_type, entity_id):
        """
        Increment version for an entity when it changes.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str/int): ID of entity
            
        Returns:
            int: New entity version
        """
        with self.lock:
            # Convert entity_id to string for consistency
            entity_id = str(entity_id)
            
            # Initialize entity type dict if not exists
            if entity_type not in self.entity_versions:
                self.entity_versions[entity_type] = {}
            
            # Initialize entity version if not exists
            if entity_id not in self.entity_versions[entity_type]:
                self.entity_versions[entity_type][entity_id] = 1
            else:
                self.entity_versions[entity_type][entity_id] += 1
            
            # Invalidate all cache entries for this entity
            cache_prefix = f"{entity_type}:{entity_id}:"
            invalidated = self.cache.invalidate(cache_prefix)
            
            logger.debug(f"Incremented version for {entity_type}:{entity_id} to " +
                         f"{self.entity_versions[entity_type][entity_id]}, invalidated {invalidated} cache entries")
            
            return self.entity_versions[entity_type][entity_id]
    
    def get_cache_key(self, entity_type, entity_id, filter_hash):
        """
        Generate a cache key for filter evaluation.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str/int): ID of entity
            filter_hash (str): Hash of filter expression
            
        Returns:
            str: Cache key
        """
        # Convert entity_id to string for consistency
        entity_id = str(entity_id)
        
        # Get entity version for cache invalidation
        version = self.get_entity_version(entity_type, entity_id)
        
        return f"{entity_type}:{entity_id}:{filter_hash}:{version}"
    
    def get_filter_hash(self, filter_expr):
        """
        Generate a hash for a filter expression.
        
        Args:
            filter_expr (dict): Filter expression
            
        Returns:
            str: Hash of filter expression
        """
        if not filter_expr:
            return "none"
            
        # Convert filter to string and hash
        filter_str = str(filter_expr)
        return hashlib.md5(filter_str.encode()).hexdigest()
    
    def get_cached_result(self, entity_type, entity_id, filter_expr):
        """
        Get cached filter evaluation result.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str/int): ID of entity
            filter_expr (dict): Filter expression
            
        Returns:
            bool or None: Cached result or None if not found
        """
        if not filter_expr:
            return None
            
        filter_hash = self.get_filter_hash(filter_expr)
        cache_key = self.get_cache_key(entity_type, entity_id, filter_hash)
        
        return self.cache.get(cache_key)
    
    def cache_result(self, entity_type, entity_id, filter_expr, result):
        """
        Cache filter evaluation result.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str/int): ID of entity
            filter_expr (dict): Filter expression
            result (bool): Evaluation result
        """
        if not filter_expr:
            return
            
        filter_hash = self.get_filter_hash(filter_expr)
        cache_key = self.get_cache_key(entity_type, entity_id, filter_hash)
        
        # Get TTL for this entity type
        ttl = self.ttl_settings.get(entity_type, self.default_ttl)
        
        self.cache.put(cache_key, result, ttl_seconds=ttl)
    
    def invalidate_entity(self, entity_type, entity_id):
        """
        Invalidate all cache entries for an entity.
        
        Args:
            entity_type (str): Type of entity
            entity_id (str/int): ID of entity
            
        Returns:
            int: New entity version
        """
        return self.increment_entity_version(entity_type, entity_id)
    
    def invalidate_entity_type(self, entity_type):
        """
        Invalidate all cache entries for an entity type.
        
        Args:
            entity_type (str): Type of entity
            
        Returns:
            int: Number of entities invalidated
        """
        with self.lock:
            if entity_type not in self.entity_versions:
                return 0
                
            # Increment version for all entities of this type
            for entity_id in self.entity_versions[entity_type]:
                self.entity_versions[entity_type][entity_id] += 1
                
                # Invalidate all cache entries for this entity
                cache_prefix = f"{entity_type}:{entity_id}:"
                self.cache.invalidate(cache_prefix)
            
            return len(self.entity_versions[entity_type])
    
    def get_stats(self):
        """
        Get cache statistics.
        
        Returns:
            dict: Cache statistics
        """
        stats = self.cache.get_stats()
        
        # Add entity version stats
        entity_type_counts = {}
        total_entities = 0
        
        with self.lock:
            for entity_type, entities in self.entity_versions.items():
                entity_type_counts[entity_type] = len(entities)
                total_entities += len(entities)
        
        stats.update({
            'total_entity_types': len(self.entity_versions),
            'total_entities': total_entities,
            'entity_type_counts': entity_type_counts
        })
        
        return stats

# Create singleton instance
filter_cache = FilterEvaluationCache()