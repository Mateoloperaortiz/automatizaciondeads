"""
WebSocket Permissions Service

Service for checking and enforcing WebSocket subscription permissions.
"""

from flask import current_app
import re
import logging
import hashlib
import time
from collections import defaultdict

logger = logging.getLogger('websocket_permissions')

class WebSocketPermissionService:
    """Service for WebSocket permission checking."""
    
    def __init__(self):
        """Initialize the WebSocket permission service."""
        # Permission cache for faster lookups
        self.permission_cache = {}
        # Cache expiry (5 minutes)
        self.cache_ttl = 300
        # Cache last access times
        self.cache_last_access = {}
        logger.info("WebSocket Permission Service initialized")
        
    def has_permission(self, user_id, action, entity_type, entity_id=None, filter_expr=None):
        """
        Check if user has permission for an action on an entity.
        
        Args:
            user_id (int): User ID
            action (str): Action (subscribe, publish)
            entity_type (str): Type of entity
            entity_id (str/int, optional): ID of entity
            filter_expr (dict, optional): Filter expression
            
        Returns:
            bool: True if permitted, False otherwise
        """
        # Skip permissions for admin users
        if self._is_admin(user_id):
            return True
            
        # Anonymous users have very limited permissions
        if user_id is None:
            return self._check_anonymous_permission(action, entity_type)
            
        # Generate cache key
        filter_hash = None
        if filter_expr:
            filter_hash = hashlib.md5(str(filter_expr).encode()).hexdigest()
            
        cache_key = f"{user_id}:{action}:{entity_type}:{entity_id}:{filter_hash}"
        
        # Check cache first (for fast lookups)
        if cache_key in self.permission_cache:
            cache_time = self.cache_last_access.get(cache_key, 0)
            if time.time() - cache_time < self.cache_ttl:
                # Update last access time
                self.cache_last_access[cache_key] = time.time()
                return self.permission_cache[cache_key]
            
        try:
            # First check for wildcard permission
            if self._check_user_permission(user_id, f"{action}:*"):
                result = True
                self.permission_cache[cache_key] = result
                self.cache_last_access[cache_key] = time.time()
                return result
                
            # Check entity type permission
            if not self._check_user_permission(user_id, f"{action}:{entity_type}"):
                result = False
                self.permission_cache[cache_key] = result
                self.cache_last_access[cache_key] = time.time()
                return result
                
            # If no entity_id specified, we're done
            if entity_id is None:
                # For filtered subscriptions, check filter permissions
                if filter_expr:
                    result = self._check_filter_permissions(user_id, entity_type, filter_expr)
                    self.permission_cache[cache_key] = result
                    self.cache_last_access[cache_key] = time.time()
                    return result
                    
                result = True
                self.permission_cache[cache_key] = result
                self.cache_last_access[cache_key] = time.time()
                return result
                
            # Check entity instance permission
            result = self._check_entity_instance_permission(user_id, action, entity_type, entity_id)
            
            # Cache result
            self.permission_cache[cache_key] = result
            self.cache_last_access[cache_key] = time.time()
            
            return result
        except Exception as e:
            logger.error(f"Error checking permissions: {str(e)}")
            # Default to deny on error
            return False
            
    def _check_anonymous_permission(self, action, entity_type):
        """
        Check permissions for anonymous users.
        
        Args:
            action (str): Action (subscribe, publish)
            entity_type (str): Type of entity
            
        Returns:
            bool: True if permitted, False otherwise
        """
        # Only allow subscription to public entity types
        if action != 'subscribe':
            return False
            
        # List of entity types that anonymous users can subscribe to
        public_entities = ['campaign', 'job_opening', 'notification']
        
        return entity_type in public_entities
            
    def _check_user_permission(self, user_id, permission):
        """
        Check if user has a specific permission string.
        
        Args:
            user_id (int): User ID
            permission (str): Permission string
            
        Returns:
            bool: True if permitted, False otherwise
        """
        # Implement admin check
        if self._is_admin(user_id):
            return True
            
        # Get user permissions
        user_permissions = self._get_user_permissions(user_id)
        
        # Check direct permission
        if permission in user_permissions:
            return True
            
        # Check wildcard permissions (e.g., "subscribe:*")
        for user_perm in user_permissions:
            if self._match_permission_pattern(user_perm, permission):
                return True
                
        return False
        
    def _match_permission_pattern(self, pattern, permission):
        """
        Check if a permission pattern matches a permission string.
        
        Args:
            pattern (str): Permission pattern (may include wildcards)
            permission (str): Permission string to check
            
        Returns:
            bool: True if pattern matches, False otherwise
        """
        # Convert pattern to regex
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(f"^{regex_pattern}$", permission))
        
    def _is_admin(self, user_id):
        """
        Check if user is an admin.
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if admin, False otherwise
        """
        # In a real app, check admin status from DB
        # For now, hardcode admin users
        admin_users = current_app.config.get('ADMIN_USERS', [1])  # User ID 1 is admin by default
        return user_id in admin_users
        
    def _get_user_permissions(self, user_id):
        """
        Get permissions for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of permission strings
        """
        # In a real app, fetch from database
        # For now, use hardcoded permissions
        
        # Default permissions for authenticated users
        default_permissions = [
            "subscribe:campaign",
            "subscribe:segment",
            "subscribe:notification",
            "subscribe:job_opening"
        ]
        
        # Role-based permissions
        user_permissions = {
            1: ["*:*"],  # Admin - all permissions
            2: ["subscribe:*", "publish:notification"],  # Manager
            3: ["subscribe:campaign", "subscribe:segment"]  # Regular user
        }
        
        return user_permissions.get(user_id, default_permissions)
        
    def _check_entity_instance_permission(self, user_id, action, entity_type, entity_id):
        """
        Check if user has permission for a specific entity instance.
        
        Args:
            user_id (int): User ID
            action (str): Action (subscribe, publish)
            entity_type (str): Type of entity
            entity_id (str/int): ID of entity
            
        Returns:
            bool: True if permitted, False otherwise
        """
        # In a real app, this would check the database
        # For example, check ownership or explicit permissions
        
        # If user has permission for the entity type, assume they have
        # permission for all instances (simplification)
        if self._check_user_permission(user_id, f"{action}:{entity_type}"):
            return True
            
        # Check specific instance permission
        specific_permission = f"{action}:{entity_type}:{entity_id}"
        return self._check_user_permission(user_id, specific_permission)
        
    def _check_filter_permissions(self, user_id, entity_type, filter_expr):
        """
        Check if user has permission to use a filter expression.
        Prevents users from crafting filters to access unauthorized data.
        
        Args:
            user_id (int): User ID
            entity_type (str): Type of entity
            filter_expr (dict): Filter expression
            
        Returns:
            bool: True if permitted, False otherwise
        """
        # For simplicity, allow all valid filters if user can access the entity type
        # In a real app, you'd validate fields used in filter are accessible to the user
        
        # Basic sanity check
        if not isinstance(filter_expr, dict):
            return False
            
        # Check for restricted fields in filter expressions
        restricted_fields = {
            'campaign': ['internal_budget', 'cost_per_acquisition'],
            'segment': ['scoring_algorithm', 'targeting_data'],
            'candidate': ['salary', 'notes', 'internal_rating']
        }
        
        # Extract all fields used in the filter
        def extract_fields(expr):
            fields = []
            
            if isinstance(expr, dict):
                # Simple condition with field, op, value
                if 'field' in expr and 'op' in expr and 'value' in expr:
                    fields.append(expr['field'])
                    
                # Complex condition with operator and conditions
                elif 'operator' in expr and 'conditions' in expr:
                    for condition in expr['conditions']:
                        fields.extend(extract_fields(condition))
            
            return fields
            
        fields = extract_fields(filter_expr)
        
        # Check if any restricted fields are used
        entity_restricted_fields = restricted_fields.get(entity_type, [])
        for field in fields:
            if field in entity_restricted_fields:
                logger.warning(f"User {user_id} attempted to use restricted field {field} in filter for {entity_type}")
                return False
                
        return True
        
    def clear_cache_for_user(self, user_id):
        """
        Clear permission cache for a user.
        
        Args:
            user_id (int): User ID
        """
        keys_to_delete = [k for k in self.permission_cache if k.startswith(f"{user_id}:")]
        for key in keys_to_delete:
            if key in self.permission_cache:
                del self.permission_cache[key]
                if key in self.cache_last_access:
                    del self.cache_last_access[key]
                    
        logger.debug(f"Cleared permission cache for user {user_id}")
        
    def clear_cache(self):
        """Clear the entire permission cache."""
        self.permission_cache.clear()
        self.cache_last_access.clear()
        logger.debug("Cleared entire permission cache")

# Create singleton instance
websocket_permissions = WebSocketPermissionService()