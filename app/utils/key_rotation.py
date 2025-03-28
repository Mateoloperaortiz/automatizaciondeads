"""
API key rotation utility for MagnetoCursor.

This module provides functionality for managing API key rotation and
monitoring expiration dates to ensure continuous service.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from .credentials import credential_manager
from .secure_storage import get_secure_storage

# Configure logging
logger = logging.getLogger(__name__)

# Constants
META_GRAPH_API_URL = 'https://graph.facebook.com/v16.0'
META_TOKEN_VALIDITY_DAYS = 60  # Meta long-lived tokens typically last 60 days

# Storage for rotation history
rotation_storage = get_secure_storage(storage_type='temp', use_encryption=True)


class KeyRotationManager:
    """
    Manages API key rotation and expiration monitoring.
    
    This class provides functionality to check key validity, schedule
    rotations, and perform automatic rotation where supported.
    """
    
    def __init__(self):
        """Initialize the key rotation manager."""
        self.expiring_keys = {}  # Keys that will expire soon
        
    def check_meta_token_validity(self) -> Dict[str, Any]:
        """
        Check the validity of Meta access token.
        
        Returns:
            Dictionary with token validity information
        """
        meta_credentials = credential_manager.get_credentials('META')
        token = meta_credentials.get('META_ACCESS_TOKEN')
        app_id = meta_credentials.get('META_APP_ID')
        app_secret = meta_credentials.get('META_APP_SECRET')
        
        if not token or not app_id or not app_secret:
            return {
                'valid': False,
                'error': 'Missing required Meta credentials',
                'expiration': None,
                'days_remaining': None
            }
        
        try:
            # Use the debug_token endpoint to get token info
            # This is a simplified implementation - in production, use the Facebook SDK
            url = f"{META_GRAPH_API_URL}/debug_token"
            params = {
                'input_token': token,
                'access_token': f"{app_id}|{app_secret}"  # App access token
            }
            
            # In a real implementation, make the actual API call:
            # response = requests.get(url, params=params)
            # data = response.json()
            
            # For this PoC, we'll simulate the response
            # In production, use the debug_token API
            simulated_response = {
                'data': {
                    'app_id': app_id,
                    'is_valid': True,
                    'expires_at': int((datetime.now() + timedelta(days=45)).timestamp())
                }
            }
            
            # Parse the response
            data = simulated_response
            
            if not data.get('data', {}).get('is_valid', False):
                return {
                    'valid': False,
                    'error': 'Invalid token',
                    'expiration': None,
                    'days_remaining': None
                }
            
            # Calculate expiration
            if 'expires_at' in data['data']:
                expire_timestamp = data['data']['expires_at']
                expire_date = datetime.fromtimestamp(expire_timestamp)
                days_remaining = (expire_date - datetime.now()).days
                
                # Store the expiry if it's less than 30 days away
                if days_remaining < 30:
                    self.expiring_keys['META_ACCESS_TOKEN'] = {
                        'expiry_date': expire_date,
                        'days_remaining': days_remaining
                    }
                
                return {
                    'valid': True,
                    'expiration': expire_date.isoformat(),
                    'days_remaining': days_remaining
                }
            else:
                # If no expiration, assume it lasts 60 days from now
                expire_date = datetime.now() + timedelta(days=META_TOKEN_VALIDITY_DAYS)
                return {
                    'valid': True,
                    'expiration': expire_date.isoformat(),
                    'days_remaining': META_TOKEN_VALIDITY_DAYS
                }
        except Exception as e:
            logger.error(f"Error checking Meta token validity: {str(e)}")
            return {
                'valid': False,
                'error': str(e),
                'expiration': None,
                'days_remaining': None
            }
    
    def rotate_meta_token(self) -> Dict[str, Any]:
        """
        Rotate Meta access token.
        
        Returns:
            Dictionary with rotation result
        """
        meta_credentials = credential_manager.get_credentials('META')
        token = meta_credentials.get('META_ACCESS_TOKEN')
        app_id = meta_credentials.get('META_APP_ID')
        app_secret = meta_credentials.get('META_APP_SECRET')
        
        if not token or not app_id or not app_secret:
            return {
                'success': False,
                'error': 'Missing required Meta credentials'
            }
        
        try:
            # Use the OAuth endpoint to get a new long-lived token
            # This is a simplified implementation - in production, use the Facebook SDK
            # Note: In a real implementation, this would be a proper token exchange
            url = f"{META_GRAPH_API_URL}/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': app_id,
                'client_secret': app_secret,
                'fb_exchange_token': token
            }
            
            # In a real implementation, make the actual API call:
            # response = requests.get(url, params=params)
            # data = response.json()
            
            # For this PoC, we'll simulate the response
            simulated_response = {
                'access_token': f"EAAT{token[5:30]}NEW{token[35:]}",
                'token_type': 'bearer',
                'expires_in': 5184000  # 60 days in seconds
            }
            
            # Parse the response
            data = simulated_response
            
            if 'access_token' not in data:
                return {
                    'success': False,
                    'error': 'Failed to get new access token'
                }
            
            # Store the old token for recovery if needed
            self._store_rotation_history('META_ACCESS_TOKEN', token, data['access_token'])
            
            # Update the credential
            new_token = data['access_token']
            credential_manager.rotate_credential('META_ACCESS_TOKEN', new_token)
            
            # Remove from expiring keys if present
            if 'META_ACCESS_TOKEN' in self.expiring_keys:
                del self.expiring_keys['META_ACCESS_TOKEN']
            
            return {
                'success': True,
                'expires_in': data.get('expires_in', 5184000),  # 60 days in seconds
                'token_type': data.get('token_type', 'bearer')
            }
        except Exception as e:
            logger.error(f"Error rotating Meta token: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_twitter_token_validity(self) -> Dict[str, Any]:
        """
        Check the validity of Twitter access token.
        
        Returns:
            Dictionary with token validity information
        """
        # This is a simplified implementation - Twitter's API doesn't have
        # a direct way to check token validity, so we assume they're valid.
        # In production, you'd make a simple API call to verify.
        twitter_credentials = credential_manager.get_credentials('TWITTER')
        
        if not all(twitter_credentials.get(key) for key in ['X_API_KEY', 'X_API_SECRET', 
                                                           'X_ACCESS_TOKEN', 'X_ACCESS_TOKEN_SECRET']):
            return {
                'valid': False,
                'error': 'Missing required Twitter credentials',
                'expiration': None,
                'days_remaining': None
            }
        
        # Twitter tokens don't expire unless revoked, so we'll mark them as valid
        return {
            'valid': True,
            'expiration': None,  # No expiration for Twitter tokens
            'days_remaining': None
        }
    
    def check_google_token_validity(self) -> Dict[str, Any]:
        """
        Check the validity of Google refresh token and related credentials.
        
        Returns:
            Dictionary with token validity information
        """
        google_credentials = credential_manager.get_credentials('GOOGLE')
        refresh_token = google_credentials.get('GOOGLE_REFRESH_TOKEN')
        client_id = google_credentials.get('GOOGLE_CLIENT_ID')
        client_secret = google_credentials.get('GOOGLE_CLIENT_SECRET')
        
        if not refresh_token or not client_id or not client_secret:
            return {
                'valid': False,
                'error': 'Missing required Google credentials',
                'expiration': None,
                'days_remaining': None
            }
        
        # Google refresh tokens don't expire unless unused for 6 months
        # or explicitly revoked. For production, you'd verify by attempting
        # to use it to get a new access token.
        return {
            'valid': True,
            'expiration': None,  # No predictable expiration for Google refresh tokens
            'days_remaining': None
        }
    
    def check_all_credentials(self) -> Dict[str, Any]:
        """
        Check validity of all API credentials.
        
        Returns:
            Dictionary with validity information for all platforms
        """
        return {
            'META': self.check_meta_token_validity(),
            'TWITTER': self.check_twitter_token_validity(),
            'GOOGLE': self.check_google_token_validity(),
            'expiring_keys': self.expiring_keys
        }
    
    def _store_rotation_history(self, key: str, old_value: str, new_value: str):
        """
        Store key rotation history for recovery if needed.
        
        Args:
            key: Credential key
            old_value: Old credential value
            new_value: New credential value
        """
        now = datetime.now()
        rotation_key = f"{key}_{now.strftime('%Y%m%d%H%M%S')}"
        
        # Get existing history or create new
        history = rotation_storage.get('rotation_history', {})
        
        # Add this rotation
        history[rotation_key] = {
            'key': key,
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': now.isoformat(),
            'platform': self._get_platform_for_key(key)
        }
        
        # Store updated history
        rotation_storage.set('rotation_history', history)
    
    def _get_platform_for_key(self, key: str) -> str:
        """
        Get the platform name for a credential key.
        
        Args:
            key: Credential key
            
        Returns:
            Platform name (META, GOOGLE, TWITTER)
        """
        if key.startswith('META_'):
            return 'META'
        elif key.startswith('GOOGLE_'):
            return 'GOOGLE'
        elif key.startswith('X_'):
            return 'TWITTER'
        return 'UNKNOWN'
    
    def get_rotation_history(self) -> List[Dict[str, Any]]:
        """
        Get history of key rotations.
        
        Returns:
            List of rotation records
        """
        history = rotation_storage.get('rotation_history', {})
        
        # Convert to list and sort by timestamp (newest first)
        history_list = [
            {
                'key': key,
                'platform': data['platform'],
                'timestamp': data['timestamp'],
                # Mask the actual values
                'old_value': credential_manager.mask_value(data['old_value']),
                'new_value': credential_manager.mask_value(data['new_value'])
            }
            for key, data in history.items()
        ]
        
        # Sort by timestamp (newest first)
        history_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return history_list
    
    def revert_rotation(self, rotation_key: str) -> Dict[str, Any]:
        """
        Revert a key rotation.
        
        Args:
            rotation_key: Key of the rotation record
            
        Returns:
            Result of the reversion
        """
        history = rotation_storage.get('rotation_history', {})
        
        if rotation_key not in history:
            return {
                'success': False,
                'error': 'Rotation record not found'
            }
        
        record = history[rotation_key]
        key = record['key']
        old_value = record['old_value']
        
        try:
            # Update the credential with the old value
            credential_manager.rotate_credential(key, old_value)
            
            # Add a new rotation record for this reversion
            self._store_rotation_history(key, record['new_value'], old_value)
            
            return {
                'success': True,
                'key': key,
                'platform': record['platform']
            }
        except Exception as e:
            logger.error(f"Error reverting rotation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Create a global instance of the key rotation manager
key_rotation_manager = KeyRotationManager()


def check_credentials_validity() -> Dict[str, Any]:
    """
    Convenience function to check validity of all API credentials.
    
    Returns:
        Dictionary with validity information for all platforms
    """
    return key_rotation_manager.check_all_credentials()


def rotate_meta_token() -> Dict[str, Any]:
    """
    Convenience function to rotate Meta access token.
    
    Returns:
        Dictionary with rotation result
    """
    return key_rotation_manager.rotate_meta_token()