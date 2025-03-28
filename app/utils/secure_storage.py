"""
Secure storage utility for handling sensitive data.

Provides encryption and secure storage capabilities for sensitive data,
with support for in-memory, file-based, and cloud-based storage.
"""
import os
import json
import base64
import logging
import tempfile
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta

# For crypto operations
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_ENCRYPTION_KEY_ENV = 'SECURE_STORAGE_KEY'
DEFAULT_SALT_ENV = 'SECURE_STORAGE_SALT'
TEMP_STORAGE_PREFIX = 'magnetocursor_'


class SecureStorage:
    """
    Secure storage for sensitive data with encryption.
    
    This class provides a secure way to store sensitive data with encryption,
    supporting both in-memory and file-based storage.
    """
    
    def __init__(self, 
                encryption_key: Optional[str] = None,
                use_encryption: bool = True,
                storage_type: str = 'memory'):
        """
        Initialize the secure storage.
        
        Args:
            encryption_key: Encryption key for data protection
            use_encryption: Whether to encrypt data
            storage_type: Storage type ('memory', 'file', 'temp')
        """
        self.use_encryption = use_encryption and CRYPTOGRAPHY_AVAILABLE
        self.storage_type = storage_type
        self.storage = {}
        self.file_path = None
        self.cipher_suite = None
        
        # Set up encryption
        if self.use_encryption:
            # Get encryption key
            self.encryption_key = encryption_key or os.environ.get(DEFAULT_ENCRYPTION_KEY_ENV)
            
            # If no key provided, generate one and warn
            if not self.encryption_key:
                self.encryption_key = self._generate_key()
                logger.warning("No encryption key provided. Generated a temporary key.")
                logger.warning("For production, set the SECURE_STORAGE_KEY environment variable.")
            
            # Initialize cipher suite
            self._init_encryption(self.encryption_key)
        
        # Set up storage
        if storage_type == 'file':
            self.file_path = os.environ.get('SECURE_STORAGE_PATH')
            if not self.file_path:
                logger.warning("No storage path provided. Using in-memory storage.")
                self.storage_type = 'memory'
            else:
                self._load_from_file()
        elif storage_type == 'temp':
            self._init_temp_storage()
    
    def _generate_key(self) -> str:
        """
        Generate a new encryption key.
        
        Returns:
            Base64-encoded encryption key
        """
        if CRYPTOGRAPHY_AVAILABLE:
            # Generate a key using cryptography
            key = Fernet.generate_key()
            return key.decode('utf-8')
        else:
            # Fallback to a less secure method
            import random
            import string
            chars = string.ascii_letters + string.digits
            return ''.join(random.choice(chars) for _ in range(32))
    
    def _init_encryption(self, key: str):
        """
        Initialize encryption with the provided key.
        
        Args:
            key: Encryption key (base64-encoded)
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography package not available. Encryption disabled.")
            self.use_encryption = False
            return
        
        try:
            # If key is not a valid Fernet key, derive one using PBKDF2
            try:
                key_bytes = key.encode('utf-8')
                if not len(base64.b64decode(key_bytes)) == 32:
                    raise ValueError("Not a valid Fernet key")
                self.cipher_suite = Fernet(key_bytes)
            except Exception:
                # Get salt from environment or use a random salt
                salt = os.environ.get(DEFAULT_SALT_ENV)
                if salt:
                    salt = salt.encode('utf-8')
                else:
                    # Generate a random salt if not provided in environment
                    salt = os.urandom(16)
                    logger.warning("No salt provided in environment. Generated a random salt.")
                    logger.warning("For production, set the SECURE_STORAGE_SALT environment variable.")
                
                # Derive a key using PBKDF2
                password = key.encode('utf-8')
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                derived_key = base64.urlsafe_b64encode(kdf.derive(password))
                self.cipher_suite = Fernet(derived_key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {str(e)}")
            self.use_encryption = False
    
    def _init_temp_storage(self):
        """Initialize temporary file storage."""
        try:
            temp_dir = tempfile.gettempdir()
            temp_name = f"{TEMP_STORAGE_PREFIX}{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            self.file_path = os.path.join(temp_dir, temp_name)
            # Create empty file
            with open(self.file_path, 'w') as f:
                f.write('{}')
        except Exception as e:
            logger.error(f"Failed to initialize temp storage: {str(e)}")
            self.storage_type = 'memory'
    
    def _load_from_file(self):
        """Load data from file storage."""
        if not self.file_path:
            return
        
        try:
            if not os.path.exists(self.file_path):
                # Create directory if needed
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                # Create empty file
                with open(self.file_path, 'w') as f:
                    f.write('{}')
                return
            
            with open(self.file_path, 'r') as f:
                data = f.read()
                if not data:
                    self.storage = {}
                    return
                
                if self.use_encryption and self.cipher_suite:
                    try:
                        # Decrypt data
                        decrypted = self.cipher_suite.decrypt(data.encode('utf-8')).decode('utf-8')
                        self.storage = json.loads(decrypted)
                    except Exception as e:
                        logger.error(f"Failed to decrypt data: {str(e)}")
                        self.storage = {}
                else:
                    # Load unencrypted data
                    self.storage = json.loads(data)
        except Exception as e:
            logger.error(f"Failed to load data from file: {str(e)}")
            self.storage = {}
    
    def _save_to_file(self):
        """Save data to file storage."""
        if not self.file_path or self.storage_type == 'memory':
            return
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            if self.use_encryption and self.cipher_suite:
                # Encrypt data
                data_str = json.dumps(self.storage)
                encrypted = self.cipher_suite.encrypt(data_str.encode('utf-8')).decode('utf-8')
                with open(self.file_path, 'w') as f:
                    f.write(encrypted)
            else:
                # Save unencrypted data
                with open(self.file_path, 'w') as f:
                    json.dump(self.storage, f)
        except Exception as e:
            logger.error(f"Failed to save data to file: {str(e)}")
    
    def set(self, key: str, value: Any, expiry: Optional[int] = None):
        """
        Store a value securely.
        
        Args:
            key: Storage key
            value: Value to store
            expiry: Expiry time in seconds (None for no expiry)
        """
        # Create data object with optional expiry
        data = {
            'value': value,
            'created_at': datetime.now().isoformat(),
        }
        
        if expiry is not None:
            expiry_time = datetime.now() + timedelta(seconds=expiry)
            data['expires_at'] = expiry_time.isoformat()
        
        # Store the data
        self.storage[key] = data
        
        # Save to file if using file storage
        if self.storage_type in ['file', 'temp']:
            self._save_to_file()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value securely.
        
        Args:
            key: Storage key
            default: Default value if key not found or expired
            
        Returns:
            The stored value or default
        """
        data = self.storage.get(key)
        if not data:
            return default
        
        # Check expiry
        if 'expires_at' in data:
            try:
                expiry_time = datetime.fromisoformat(data['expires_at'])
                if datetime.now() > expiry_time:
                    # Value has expired
                    self.delete(key)
                    return default
            except Exception:
                pass
        
        return data.get('value', default)
    
    def delete(self, key: str):
        """
        Delete a stored value.
        
        Args:
            key: Storage key
        """
        if key in self.storage:
            del self.storage[key]
            
            # Save to file if using file storage
            if self.storage_type in ['file', 'temp']:
                self._save_to_file()
    
    def clear(self):
        """Clear all stored values."""
        self.storage = {}
        
        # Save to file if using file storage
        if self.storage_type in ['file', 'temp']:
            self._save_to_file()
    
    def get_all_keys(self) -> list:
        """
        Get all storage keys.
        
        Returns:
            List of all storage keys
        """
        return list(self.storage.keys())
    
    def get_creation_time(self, key: str) -> Optional[datetime]:
        """
        Get the creation time of a stored value.
        
        Args:
            key: Storage key
            
        Returns:
            Creation time or None if key not found
        """
        data = self.storage.get(key)
        if not data or 'created_at' not in data:
            return None
        
        try:
            return datetime.fromisoformat(data['created_at'])
        except Exception:
            return None
    
    def get_expiry_time(self, key: str) -> Optional[datetime]:
        """
        Get the expiry time of a stored value.
        
        Args:
            key: Storage key
            
        Returns:
            Expiry time or None if key not found or no expiry
        """
        data = self.storage.get(key)
        if not data or 'expires_at' not in data:
            return None
        
        try:
            return datetime.fromisoformat(data['expires_at'])
        except Exception:
            return None
    
    def cleanup_expired(self):
        """Remove all expired values."""
        now = datetime.now()
        expired_keys = []
        
        for key, data in self.storage.items():
            if 'expires_at' in data:
                try:
                    expiry_time = datetime.fromisoformat(data['expires_at'])
                    if now > expiry_time:
                        expired_keys.append(key)
                except Exception:
                    pass
        
        for key in expired_keys:
            self.delete(key)
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """
        Get status of the encryption.
        
        Returns:
            Dictionary with encryption status
        """
        return {
            'enabled': self.use_encryption,
            'library_available': CRYPTOGRAPHY_AVAILABLE,
            'storage_type': self.storage_type,
            'file_path': self.file_path,
            'key_configured': bool(self.encryption_key)
        }


# Create an instance with default settings (in-memory storage without encryption)
default_storage = SecureStorage(use_encryption=False)


def get_secure_storage(storage_type: str = 'memory', use_encryption: bool = True) -> SecureStorage:
    """
    Get a secure storage instance.
    
    Args:
        storage_type: Storage type ('memory', 'file', 'temp')
        use_encryption: Whether to encrypt data
        
    Returns:
        SecureStorage instance
    """
    return SecureStorage(
        storage_type=storage_type,
        use_encryption=use_encryption
    )