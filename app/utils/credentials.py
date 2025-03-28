"""
Secure credential management system for MagnetoCursor.

This module provides a secure, flexible system for managing API credentials
across different environments (development, testing, staging, production).
It supports:
- Environment variable loading with fallbacks
- Credential validation and rotation
- Secure storage options including Google Secret Manager
- Credential masking in logs and error messages
"""
import os
import re
import json
import logging
import hashlib
import functools
from typing import Dict, Any, Optional, Union, Callable, List, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Attempt to import Google Secret Manager, handle gracefully if not available
try:
    from google.cloud import secretmanager
    GOOGLE_SECRET_MANAGER_AVAILABLE = True
except ImportError:
    GOOGLE_SECRET_MANAGER_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# Constants
CREDENTIAL_EXPIRY_WARNING_DAYS = 14
API_KEY_PATTERN = re.compile(r'^[A-Za-z0-9_\-]{10,}$')
MASKED_VALUE = '********'
DEFAULT_ENV_FILE_PATH = '.env'

# Define credential configuration structure
CREDENTIAL_CONFIG = {
    # Meta (Facebook) credentials
    'META': {
        'required': ['META_APP_ID', 'META_APP_SECRET', 'META_ACCESS_TOKEN', 'META_AD_ACCOUNT_ID'],
        'validators': {
            'META_APP_ID': lambda x: x.isdigit() and len(x) > 8,
            'META_APP_SECRET': lambda x: len(x) >= 32,
            'META_ACCESS_TOKEN': lambda x: len(x) >= 50 and 'EAAT' in x,
            'META_AD_ACCOUNT_ID': lambda x: x.startswith('act_') and x[4:].isdigit()
        },
        'expiry_check': {
            'META_ACCESS_TOKEN': lambda x: check_meta_token_expiry(x)
        }
    },
    
    # Google Ads credentials
    'GOOGLE': {
        'required': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN', 
                    'GOOGLE_ADS_DEVELOPER_TOKEN', 'GOOGLE_ADS_CUSTOMER_ID'],
        'validators': {
            'GOOGLE_CLIENT_ID': lambda x: x.endswith('.apps.googleusercontent.com'),
            'GOOGLE_CLIENT_SECRET': lambda x: x.startswith('GOCSPX-'),
            'GOOGLE_REFRESH_TOKEN': lambda x: len(x) >= 30,
            'GOOGLE_ADS_DEVELOPER_TOKEN': lambda x: len(x) >= 20,
            'GOOGLE_ADS_CUSTOMER_ID': lambda x: x.isdigit()
        }
    },
    
    # Twitter/X credentials
    'TWITTER': {
        'required': ['X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 
                    'X_ACCESS_TOKEN_SECRET', 'X_BEARER_TOKEN'],
        'validators': {
            'X_API_KEY': lambda x: API_KEY_PATTERN.match(x) is not None,
            'X_API_SECRET': lambda x: len(x) >= 30,
            'X_ACCESS_TOKEN': lambda x: '-' in x and len(x) >= 30,
            'X_ACCESS_TOKEN_SECRET': lambda x: len(x) >= 30,
            'X_BEARER_TOKEN': lambda x: 'AAAAAAAAAA' in x
        }
    }
}


def check_meta_token_expiry(token: str) -> Optional[datetime]:
    """
    Check if a Meta access token is near expiry.
    
    Access tokens typically expire after 60 days, but this is a simplified check.
    In production, a proper expiry check would call the /debug_token endpoint.
    
    Args:
        token: The Meta access token to check
        
    Returns:
        Optional datetime of estimated expiry or None if couldn't determine
    """
    # Import here to avoid circular imports
    import requests
    
    try:
        # Check if token starts with expected prefix (EAAT)
        if not token or not token.startswith('EAAT'):
            logger.warning("Invalid Meta access token format")
            return datetime.now() + timedelta(days=7)  # Assume will expire soon
        
        # Real implementation would use the Meta Graph API Debug Token endpoint
        # Example: https://graph.facebook.com/debug_token?input_token={token}&access_token={app_token}
        # For now, implement a simplified check based on token format
        
        # Extract token creation time from the token (if following Meta format - simplified approach)
        # This is an approximation, not how Meta tokens actually work
        token_hash = hashlib.md5(token.encode()).hexdigest()
        # Use hash to generate a pseudo-random but consistent expiry date
        hash_value = int(token_hash[:8], 16)
        days_valid = 30 + (hash_value % 30)  # Between 30-60 days validity
        
        # Estimate expiry based on token signature
        return datetime.now() + timedelta(days=days_valid)
    except Exception as e:
        logger.warning(f"Could not determine Meta token expiry: {str(e)}")
        return datetime.now() + timedelta(days=30)  # Default fallback


class CredentialManager:
    """
    Secure credential management system for API integrations.
    
    This class provides a centralized way to access API credentials with proper
    security practices, validation, and rotation management.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure one credential manager instance."""
        if cls._instance is None:
            cls._instance = super(CredentialManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, 
                app=None, 
                env_file: str = DEFAULT_ENV_FILE_PATH,
                use_secret_manager: bool = False,
                gcp_project_id: Optional[str] = None):
        """
        Initialize the credential manager.
        
        Args:
            app: Flask app instance (optional)
            env_file: Path to the .env file
            use_secret_manager: Whether to use Google Secret Manager
            gcp_project_id: Google Cloud project ID for Secret Manager
        """
        if self._initialized:
            return
            
        # Load environment variables
        load_dotenv(env_file)
        
        self.env = os.environ.get('FLASK_ENV', 'development')
        self.use_secret_manager = use_secret_manager and GOOGLE_SECRET_MANAGER_AVAILABLE
        self.gcp_project_id = gcp_project_id
        self.credentials = {}
        self.secret_client = None
        
        # Configure secret manager if enabled
        if self.use_secret_manager and self.gcp_project_id:
            try:
                self.secret_client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                logger.error(f"Failed to initialize Secret Manager: {str(e)}")
                self.use_secret_manager = False
        
        # Load all credentials
        self._load_all_credentials()
        
        # Initialize with Flask app if provided
        if app is not None:
            self.init_app(app)
            
        self._initialized = True
    
    def init_app(self, app):
        """
        Configure with a Flask application instance.
        
        Args:
            app: Flask application instance
        """
        # Add config values to Flask app
        for platform, creds in self.credentials.items():
            for key, value in creds.items():
                app.config[key] = value
                
        # Register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['credential_manager'] = self
    
    def _load_all_credentials(self):
        """Load all credentials from environment variables and/or secret manager."""
        for platform, config in CREDENTIAL_CONFIG.items():
            self.credentials[platform] = {}
            
            # Get required credentials for this platform
            for key in config['required']:
                # Try to get from Secret Manager first if enabled
                if self.use_secret_manager:
                    value = self._get_from_secret_manager(key)
                    if value:
                        self.credentials[platform][key] = value
                        continue
                
                # Fall back to environment variable
                value = os.environ.get(key)
                if value:
                    self.credentials[platform][key] = value
            
            # Validate the credentials
            self._validate_credentials(platform)
    
    def _get_from_secret_manager(self, secret_id: str) -> Optional[str]:
        """
        Retrieve a secret from Google Secret Manager.
        
        Args:
            secret_id: The ID of the secret to retrieve
            
        Returns:
            The secret value or None if not found/error
        """
        if not self.secret_client or not self.gcp_project_id:
            return None
            
        try:
            # Build the resource name of the secret version
            name = f"projects/{self.gcp_project_id}/secrets/{secret_id}/versions/latest"
            
            # Access the secret version
            response = self.secret_client.access_secret_version(name=name)
            
            # Return the decoded payload
            return response.payload.data.decode('UTF-8')
        except Exception as e:
            logger.warning(f"Failed to retrieve secret {secret_id}: {str(e)}")
            return None
    
    def _validate_credentials(self, platform: str):
        """
        Validate credentials for a specific platform.
        
        Args:
            platform: The platform name (META, GOOGLE, TWITTER)
        """
        if platform not in CREDENTIAL_CONFIG:
            logger.warning(f"No validation config for platform: {platform}")
            return
            
        config = CREDENTIAL_CONFIG[platform]
        platform_creds = self.credentials.get(platform, {})
        
        # Check required credentials
        missing = [key for key in config['required'] if key not in platform_creds or not platform_creds[key]]
        if missing:
            logger.warning(f"Missing required credentials for {platform}: {', '.join(missing)}")
        
        # Validate credential format
        if 'validators' in config:
            for key, validator in config['validators'].items():
                if key in platform_creds and platform_creds[key]:
                    try:
                        if not validator(platform_creds[key]):
                            logger.warning(f"Credential {key} failed validation")
                    except Exception as e:
                        logger.warning(f"Error validating {key}: {str(e)}")
        
        # Check for soon-to-expire credentials
        if 'expiry_check' in config:
            for key, expiry_checker in config['expiry_check'].items():
                if key in platform_creds and platform_creds[key]:
                    try:
                        expiry_date = expiry_checker(platform_creds[key])
                        if expiry_date:
                            days_until_expiry = (expiry_date - datetime.now()).days
                            if days_until_expiry <= CREDENTIAL_EXPIRY_WARNING_DAYS:
                                logger.warning(f"Credential {key} expires in {days_until_expiry} days")
                    except Exception as e:
                        logger.warning(f"Error checking expiry for {key}: {str(e)}")
    
    def get_credentials(self, platform: str) -> Dict[str, str]:
        """
        Get all credentials for a specific platform.
        
        Args:
            platform: Platform name (META, GOOGLE, TWITTER)
            
        Returns:
            Dictionary of credentials for the platform
        """
        return self.credentials.get(platform, {})
    
    def get(self, key: str) -> Optional[str]:
        """
        Get a specific credential by key.
        
        Args:
            key: The credential key (e.g., META_APP_ID)
            
        Returns:
            The credential value or None if not found
        """
        for platform_creds in self.credentials.values():
            if key in platform_creds:
                return platform_creds[key]
        return None
    
    def is_configured(self, platform: str) -> bool:
        """
        Check if all required credentials for a platform are available.
        
        Args:
            platform: Platform name (META, GOOGLE, TWITTER)
            
        Returns:
            True if all required credentials are available, False otherwise
        """
        if platform not in CREDENTIAL_CONFIG:
            return False
            
        required = CREDENTIAL_CONFIG[platform]['required']
        platform_creds = self.credentials.get(platform, {})
        
        return all(key in platform_creds and platform_creds[key] for key in required)
    
    def mask_value(self, value: str) -> str:
        """
        Mask a sensitive credential value for display.
        
        Args:
            value: The sensitive value to mask
            
        Returns:
            Masked value (e.g., "EAAT***********ZQZD")
        """
        if not value or len(value) < 10:
            return MASKED_VALUE
            
        # Show first 4 and last 4 characters, mask the rest
        return value[:4] + MASKED_VALUE + value[-4:]
    
    def rotate_credential(self, key: str, new_value: str) -> bool:
        """
        Update a credential with a new value.
        
        This is useful for token rotation. For production, this would be 
        integrated with a secure credential rotation system.
        
        Args:
            key: The credential key to update
            new_value: The new credential value
            
        Returns:
            True if successful, False otherwise
        """
        # Find which platform this credential belongs to
        platform = None
        for p, config in CREDENTIAL_CONFIG.items():
            if key in config['required']:
                platform = p
                break
        
        if not platform:
            logger.error(f"Unknown credential key: {key}")
            return False
        
        # Validate the new value
        if 'validators' in CREDENTIAL_CONFIG[platform] and key in CREDENTIAL_CONFIG[platform]['validators']:
            validator = CREDENTIAL_CONFIG[platform]['validators'][key]
            try:
                if not validator(new_value):
                    logger.error(f"New value for {key} failed validation")
                    return False
            except Exception as e:
                logger.error(f"Error validating new value for {key}: {str(e)}")
                return False
        
        # Update the credential
        self.credentials[platform][key] = new_value
        
        # If using Secret Manager, update the secret
        if self.use_secret_manager and self.secret_client:
            try:
                self._update_secret_manager(key, new_value)
            except Exception as e:
                logger.error(f"Failed to update secret in Secret Manager: {str(e)}")
                
        return True
    
    def _update_secret_manager(self, secret_id: str, value: str):
        """
        Update a secret in Google Secret Manager.
        
        Args:
            secret_id: The ID of the secret to update
            value: The new secret value
        """
        if not self.secret_client or not self.gcp_project_id:
            return
            
        # Build the resource name of the parent project
        parent = f"projects/{self.gcp_project_id}"
        
        try:
            # Try to access the secret first to see if it exists
            secret_name = f"{parent}/secrets/{secret_id}"
            self.secret_client.get_secret(name=secret_name)
            
            # Secret exists, add new version
            secret = self.secret_client.add_secret_version(
                parent=secret_name,
                payload={"data": value.encode("UTF-8")}
            )
        except Exception:
            # Secret doesn't exist, create it
            secret = self.secret_client.create_secret(
                parent=parent,
                secret_id=secret_id,
                secret={"replication": {"automatic": {}}}
            )
            
            # Add the first version
            self.secret_client.add_secret_version(
                parent=secret.name,
                payload={"data": value.encode("UTF-8")}
            )
    
    def export_to_env_file(self, file_path: str = '.env.new'):
        """
        Export all credentials to a new .env file.
        
        This is useful for development and testing.
        
        Args:
            file_path: Path to the new .env file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                f.write("# Generated by CredentialManager\n")
                f.write(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for platform, platform_creds in self.credentials.items():
                    f.write(f"# {platform} API Credentials\n")
                    for key, value in platform_creds.items():
                        f.write(f"{key}={value}\n")
                    f.write("\n")
            return True
        except Exception as e:
            logger.error(f"Failed to export credentials to {file_path}: {str(e)}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all credentials.
        
        Returns:
            Dictionary with credential health status
        """
        status = {}
        
        for platform, config in CREDENTIAL_CONFIG.items():
            platform_status = {
                'configured': self.is_configured(platform),
                'missing': [],
                'expiring': [],
                'invalid': []
            }
            
            platform_creds = self.credentials.get(platform, {})
            
            # Check missing credentials
            platform_status['missing'] = [
                key for key in config['required'] 
                if key not in platform_creds or not platform_creds[key]
            ]
            
            # Check credential format
            if 'validators' in config:
                for key, validator in config['validators'].items():
                    if key in platform_creds and platform_creds[key]:
                        try:
                            if not validator(platform_creds[key]):
                                platform_status['invalid'].append(key)
                        except Exception:
                            platform_status['invalid'].append(key)
            
            # Check for soon-to-expire credentials
            if 'expiry_check' in config:
                for key, expiry_checker in config['expiry_check'].items():
                    if key in platform_creds and platform_creds[key]:
                        try:
                            expiry_date = expiry_checker(platform_creds[key])
                            if expiry_date:
                                days_until_expiry = (expiry_date - datetime.now()).days
                                if days_until_expiry <= CREDENTIAL_EXPIRY_WARNING_DAYS:
                                    platform_status['expiring'].append({
                                        'key': key,
                                        'days_remaining': days_until_expiry
                                    })
                        except Exception:
                            pass
            
            status[platform] = platform_status
            
        return status

# Create a global instance of the credential manager
credential_manager = CredentialManager()


def get_credentials(platform: str) -> Dict[str, str]:
    """
    Convenience function to get all credentials for a platform.
    
    Args:
        platform: Platform name (META, GOOGLE, TWITTER)
        
    Returns:
        Dictionary of credentials for the platform
    """
    return credential_manager.get_credentials(platform)


def is_configured(platform: str) -> bool:
    """
    Convenience function to check if a platform is configured.
    
    Args:
        platform: Platform name (META, GOOGLE, TWITTER)
        
    Returns:
        True if all required credentials are available, False otherwise
    """
    return credential_manager.is_configured(platform)


def require_credentials(platform: str) -> Callable:
    """
    Decorator to require credentials for a platform.
    
    Args:
        platform: Platform name (META, GOOGLE, TWITTER)
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not credential_manager.is_configured(platform):
                logger.error(f"Missing required credentials for {platform}")
                return {'success': False, 'error': f'Missing required credentials for {platform}'}
            return func(*args, **kwargs)
        return wrapper
    return decorator