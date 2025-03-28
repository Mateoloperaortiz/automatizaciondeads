"""
Google Cloud Secret Manager integration for MagnetoCursor.

This module provides utilities for securely storing and retrieving
credentials using Google Cloud Secret Manager in production environments.
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Try to import Google Secret Manager, handle gracefully if not available
try:
    from google.cloud import secretmanager
    from google.api_core.exceptions import NotFound, PermissionDenied, FailedPrecondition
    GOOGLE_SECRET_MANAGER_AVAILABLE = True
except ImportError:
    GOOGLE_SECRET_MANAGER_AVAILABLE = False
    logger.warning("Google Cloud Secret Manager not available. Install with: pip install google-cloud-secret-manager")


class GCPSecretManager:
    """
    Google Cloud Secret Manager integration for secure credential storage.
    
    This class provides methods to store, retrieve, and manage credentials
    using Google Cloud Secret Manager for production environments.
    """
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize the GCP Secret Manager client.
        
        Args:
            project_id: Google Cloud project ID (default: from environment)
        """
        self.project_id = project_id or os.environ.get('GCP_PROJECT_ID')
        self.client = None
        self.is_available = GOOGLE_SECRET_MANAGER_AVAILABLE
        
        if self.is_available and self.project_id:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
                logger.info("Google Cloud Secret Manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Secret Manager: {str(e)}")
                self.is_available = False
        elif not self.project_id:
            logger.warning("GCP project ID not set. Set GCP_PROJECT_ID environment variable.")
    
    def get_secret(self, secret_id: str, version: str = "latest") -> Optional[str]:
        """
        Get a secret value from Secret Manager.
        
        Args:
            secret_id: The ID of the secret to retrieve
            version: The version of the secret (default: latest)
            
        Returns:
            The secret value or None if not found/error
        """
        if not self.is_available or not self.client or not self.project_id:
            logger.warning("Secret Manager not available")
            return None
            
        try:
            # Build the resource name of the secret version
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
            
            # Access the secret version
            response = self.client.access_secret_version(name=name)
            
            # Return the decoded payload
            return response.payload.data.decode('UTF-8')
        except NotFound:
            logger.warning(f"Secret {secret_id} not found")
            return None
        except PermissionDenied:
            logger.error(f"Permission denied for secret {secret_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting secret {secret_id}: {str(e)}")
            return None
    
    def create_or_update_secret(self, secret_id: str, value: str) -> bool:
        """
        Create or update a secret in Secret Manager.
        
        Args:
            secret_id: The ID of the secret
            value: The secret value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available or not self.client or not self.project_id:
            logger.warning("Secret Manager not available")
            return False
            
        try:
            # Build the resource name of the parent project
            parent = f"projects/{self.project_id}"
            
            # Check if the secret already exists
            secret_exists = True
            try:
                self.client.get_secret(name=f"{parent}/secrets/{secret_id}")
            except NotFound:
                secret_exists = False
            
            # Create the secret if it doesn't exist
            if not secret_exists:
                logger.info(f"Creating new secret: {secret_id}")
                self.client.create_secret(
                    parent=parent,
                    secret_id=secret_id,
                    secret={"replication": {"automatic": {}}}
                )
            
            # Add a new version of the secret
            secret_value = value.encode('UTF-8')
            response = self.client.add_secret_version(
                parent=f"{parent}/secrets/{secret_id}",
                payload={"data": secret_value}
            )
            
            logger.info(f"Secret {secret_id} created/updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating/updating secret {secret_id}: {str(e)}")
            return False
    
    def delete_secret(self, secret_id: str) -> bool:
        """
        Delete a secret from Secret Manager.
        
        Args:
            secret_id: The ID of the secret to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available or not self.client or not self.project_id:
            logger.warning("Secret Manager not available")
            return False
            
        try:
            # Build the resource name of the secret
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            
            # Delete the secret
            self.client.delete_secret(name=name)
            
            logger.info(f"Secret {secret_id} deleted successfully")
            return True
        except NotFound:
            logger.warning(f"Secret {secret_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting secret {secret_id}: {str(e)}")
            return False
    
    def list_secrets(self) -> List[Dict[str, Any]]:
        """
        List all secrets in the project.
        
        Returns:
            List of secret metadata
        """
        if not self.is_available or not self.client or not self.project_id:
            logger.warning("Secret Manager not available")
            return []
            
        try:
            # Build the resource name of the parent project
            parent = f"projects/{self.project_id}"
            
            # List all secrets
            response = self.client.list_secrets(parent=parent)
            
            # Process the results
            secrets = []
            for secret in response:
                name = secret.name.split('/')[-1]
                create_time = secret.create_time.isoformat() if hasattr(secret, 'create_time') else None
                
                secrets.append({
                    'name': name,
                    'create_time': create_time,
                    'labels': dict(secret.labels) if hasattr(secret, 'labels') else {},
                })
            
            return secrets
        except Exception as e:
            logger.error(f"Error listing secrets: {str(e)}")
            return []
    
    def rotate_secret(self, secret_id: str, new_value: str) -> bool:
        """
        Rotate a secret by adding a new version.
        
        Args:
            secret_id: The ID of the secret to rotate
            new_value: The new secret value
            
        Returns:
            True if successful, False otherwise
        """
        return self.create_or_update_secret(secret_id, new_value)
    
    def export_all_secrets_to_env(self) -> Dict[str, str]:
        """
        Export all secrets to a dictionary for environment variables.
        
        Returns:
            Dictionary of secret_id: value pairs
        """
        if not self.is_available or not self.client or not self.project_id:
            logger.warning("Secret Manager not available")
            return {}
            
        try:
            # Get list of all secrets
            secrets_list = self.list_secrets()
            
            # Get the latest value for each secret
            env_vars = {}
            for secret in secrets_list:
                secret_id = secret['name']
                value = self.get_secret(secret_id)
                if value is not None:
                    env_vars[secret_id] = value
            
            return env_vars
        except Exception as e:
            logger.error(f"Error exporting secrets: {str(e)}")
            return {}
    
    def import_secrets_from_env(self, env_vars: Dict[str, str]) -> bool:
        """
        Import secrets from environment variables.
        
        Args:
            env_vars: Dictionary of secret_id: value pairs
            
        Returns:
            True if all secrets were imported successfully, False otherwise
        """
        if not self.is_available or not self.client or not self.project_id:
            logger.warning("Secret Manager not available")
            return False
            
        try:
            success = True
            for secret_id, value in env_vars.items():
                if not self.create_or_update_secret(secret_id, value):
                    success = False
            
            return success
        except Exception as e:
            logger.error(f"Error importing secrets: {str(e)}")
            return False


# Create a global instance of the Secret Manager
secret_manager = GCPSecretManager()


def is_secret_manager_available() -> bool:
    """
    Check if Google Cloud Secret Manager is available.
    
    Returns:
        True if available, False otherwise
    """
    return secret_manager.is_available


def get_secret(secret_id: str) -> Optional[str]:
    """
    Convenience function to get a secret from Secret Manager.
    
    Args:
        secret_id: The ID of the secret to retrieve
        
    Returns:
        The secret value or None if not found/error
    """
    return secret_manager.get_secret(secret_id)


def store_secret(secret_id: str, value: str) -> bool:
    """
    Convenience function to store a secret in Secret Manager.
    
    Args:
        secret_id: The ID of the secret
        value: The secret value
        
    Returns:
        True if successful, False otherwise
    """
    return secret_manager.create_or_update_secret(secret_id, value)