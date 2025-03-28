"""
Configuration management system for MagnetoCursor.

Handles application configuration based on environment, with secure loading
of sensitive credentials through CredentialManager.
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .credentials import credential_manager, is_configured

# Configure logging
logger = logging.getLogger(__name__)

# Environment constants
ENV_DEV = 'development'
ENV_TEST = 'testing'
ENV_STAGE = 'staging'
ENV_PROD = 'production'

# Default configuration values
DEFAULT_CONFIG = {
    'SECRET_KEY': 'dev-key-for-development',
    'DEBUG': True,
    'TESTING': False,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///ad_automation.sqlite',
    # API rate limiting
    'META_API_RATE_LIMIT': 200,  # requests per hour
    'TWITTER_API_RATE_LIMIT': 450,  # requests per 15-min window
    'GOOGLE_API_RATE_LIMIT': 100,  # requests per 100 seconds
    # Job settings
    'MAX_CONCURRENT_JOBS': 5,
    'JOB_TIMEOUT_SECONDS': 300,
    # Cache settings
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,
    # Security settings
    'SESSION_COOKIE_SECURE': False,
    'SESSION_COOKIE_HTTPONLY': True,
    # API Framework feature flags
    'USE_API_FRAMEWORK': False,
    'API_FRAMEWORK_PLATFORMS': [],  # Empty list = none enabled
    'COLLECT_API_METRICS': True,
    'API_CACHE_TTL': 300,  # 5 minutes default cache TTL
}

# Environment-specific configuration
ENV_CONFIG = {
    ENV_DEV: {
        'DEBUG': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////Users/mateo/Documents/GitHub/PoCs/MagnetoCursor/instance/ad_automation.sqlite',
        'META_API_SIMULATE': False,
        'TWITTER_API_SIMULATE': False,
        'GOOGLE_API_SIMULATE': False,
    },
    ENV_TEST: {
        'DEBUG': True,
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///instance/test_db.sqlite',
        'META_API_SIMULATE': True,
        'TWITTER_API_SIMULATE': True,
        'GOOGLE_API_SIMULATE': True,
        'USE_API_FRAMEWORK': True,
        'API_FRAMEWORK_PLATFORMS': ['meta', 'twitter', 'google'],
    },
    ENV_STAGE: {
        'DEBUG': False,
        'SQLALCHEMY_DATABASE_URI': os.getenv('SQLALCHEMY_DATABASE_URI', 
                                           'postgresql+psycopg2://postgres:postgres@localhost:5432/ad_automation_staging'),
        'SESSION_COOKIE_SECURE': True,
        'META_API_SIMULATE': False,
        'TWITTER_API_SIMULATE': False,
        'GOOGLE_API_SIMULATE': False,
    },
    ENV_PROD: {
        'DEBUG': False,
        'SQLALCHEMY_DATABASE_URI': os.getenv('SQLALCHEMY_DATABASE_URI', 
                                           'postgresql+psycopg2://postgres:postgres@localhost:5432/ad_automation'),
        'SESSION_COOKIE_SECURE': True,
        'META_API_SIMULATE': False,
        'TWITTER_API_SIMULATE': False,
        'GOOGLE_API_SIMULATE': False,
    }
}


class ConfigurationManager:
    """
    Configuration management system for environment-specific settings.
    
    This class provides a centralized way to access application configuration
    with proper handling of environment-specific overrides and sensitive credentials.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure one configuration manager instance."""
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, env_file: str = '.env'):
        """
        Initialize the configuration manager.
        
        Args:
            env_file: Path to the .env file
        """
        if self._initialized:
            return
            
        # Load environment variables
        load_dotenv(env_file)
        
        # Determine current environment
        self.environment = os.environ.get('FLASK_ENV', ENV_DEV)
        if self.environment not in ENV_CONFIG:
            logger.warning(f"Unknown environment: {self.environment}, defaulting to {ENV_DEV}")
            self.environment = ENV_DEV
        
        # Configure logging environment
        self._configure_logging()
        
        # Initialize configuration with defaults and environment overrides
        self.config = self._initialize_config()
        
        # Merge API credentials
        self._merge_credentials()
        
        # Ensure credentials are validated with credential manager
        if not is_configured('META') and not self.config.get('META_API_SIMULATE', False):
            logger.warning("Meta API credentials are not properly configured.")
        
        if not is_configured('GOOGLE') and not self.config.get('GOOGLE_API_SIMULATE', False):
            logger.warning("Google Ads API credentials are not properly configured.")
        
        if not is_configured('TWITTER') and not self.config.get('TWITTER_API_SIMULATE', False):
            logger.warning("Twitter API credentials are not properly configured.")
        
        self._initialized = True
    
    def _configure_logging(self):
        """Configure logging based on the current environment."""
        log_level = logging.DEBUG if self.environment in [ENV_DEV, ENV_TEST] else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _initialize_config(self) -> Dict[str, Any]:
        """
        Initialize configuration with defaults and environment overrides.
        
        Returns:
            Complete configuration dictionary
        """
        # Start with default configuration
        config = DEFAULT_CONFIG.copy()
        
        # Override with environment-specific values
        env_specific = ENV_CONFIG.get(self.environment, {})
        config.update(env_specific)
        
        # Override with environment variables
        for key in config:
            env_value = os.environ.get(key)
            if env_value is not None:
                # Convert boolean strings
                if env_value.lower() in ['true', 'yes', '1']:
                    config[key] = True
                elif env_value.lower() in ['false', 'no', '0']:
                    config[key] = False
                else:
                    config[key] = env_value
        
        # Add environment setting for templates
        config['ENVIRONMENT'] = self.environment
        config['IS_DEVELOPMENT'] = self.environment == ENV_DEV
        config['IS_TESTING'] = self.environment == ENV_TEST
        config['IS_STAGING'] = self.environment == ENV_STAGE
        config['IS_PRODUCTION'] = self.environment == ENV_PROD
        
        return config
    
    def _merge_credentials(self):
        """Merge API credentials from CredentialManager into the configuration."""
        # Meta credentials
        meta_creds = credential_manager.get_credentials('META')
        for key, value in meta_creds.items():
            self.config[key] = value
        
        # Google credentials
        google_creds = credential_manager.get_credentials('GOOGLE')
        for key, value in google_creds.items():
            self.config[key] = value
        
        # Twitter credentials
        twitter_creds = credential_manager.get_credentials('TWITTER')
        for key, value in twitter_creds.items():
            self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def update(self, key: str, value: Any):
        """
        Update a configuration value.
        
        Args:
            key: Configuration key
            value: New value
        """
        self.config[key] = value
        
    def set(self, key: str, value: Any):
        """
        Set a configuration value and persist it to environment.
        
        Args:
            key: Configuration key
            value: New value
        """
        self.config[key] = value
        # In a real implementation, this would persist the setting
        # to a database or configuration file
        logger.info(f"Updated configuration: {key}={value}")
        
    def set_default(self, key: str, value: Any):
        """
        Set a default configuration value if not already set.
        
        Args:
            key: Configuration key
            value: Default value
        """
        if key not in self.config:
            self.config[key] = value
    
    def is_api_simulated(self, platform: str) -> bool:
        """
        Check if API should be simulated for a platform.
        
        Args:
            platform: Platform name (META, GOOGLE, TWITTER)
            
        Returns:
            True if API simulation is enabled, False otherwise
        """
        key = f"{platform}_API_SIMULATE"
        return self.config.get(key, False)
        
    def is_api_framework_enabled(self) -> bool:
        """
        Check if the API framework is enabled.
        
        Returns:
            True if the API framework is enabled, False otherwise
        """
        return self.config.get('USE_API_FRAMEWORK', False)
        
    def is_platform_using_framework(self, platform: str) -> bool:
        """
        Check if a specific platform is using the API framework.
        
        Args:
            platform: Platform name (meta, twitter, google)
            
        Returns:
            True if the platform is using the framework, False otherwise
        """
        if not self.is_api_framework_enabled():
            return False
            
        platforms = self.config.get('API_FRAMEWORK_PLATFORMS', [])
        return platform.lower() in platforms
        
    def enable_api_framework(self, platforms: Optional[list[str]] = None):
        """
        Enable the API framework for specified platforms.
        
        Args:
            platforms: List of platform names to enable (meta, twitter, google)
                      If None, doesn't change the platform list
        """
        self.set('USE_API_FRAMEWORK', True)
        
        if platforms is not None:
            self.set('API_FRAMEWORK_PLATFORMS', [p.lower() for p in platforms])
            
        logger.info(f"API Framework enabled for platforms: {self.config.get('API_FRAMEWORK_PLATFORMS')}")
        
    def disable_api_framework(self):
        """
        Disable the API framework.
        """
        self.set('USE_API_FRAMEWORK', False)
        logger.info("API Framework disabled")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the application configuration.
        
        Returns:
            Dictionary with configuration health status
        """
        status = {
            'environment': self.environment,
            'database': {
                'uri': credential_manager.mask_value(self.config.get('SQLALCHEMY_DATABASE_URI', '')),
                'track_modifications': self.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
            },
            'api_simulation': {
                'meta': self.config.get('META_API_SIMULATE', False),
                'google': self.config.get('GOOGLE_API_SIMULATE', False),
                'twitter': self.config.get('TWITTER_API_SIMULATE', False)
            },
            'api_framework': {
                'enabled': self.is_api_framework_enabled(),
                'platforms': self.config.get('API_FRAMEWORK_PLATFORMS', []),
                'collect_metrics': self.config.get('COLLECT_API_METRICS', True),
                'cache_ttl': self.config.get('API_CACHE_TTL', 300)
            },
            'security': {
                'debug': self.config.get('DEBUG', False),
                'testing': self.config.get('TESTING', False),
                'secure_cookies': self.config.get('SESSION_COOKIE_SECURE', False),
                'httponly_cookies': self.config.get('SESSION_COOKIE_HTTPONLY', True)
            },
            'credentials': credential_manager.get_health_status()
        }
        
        return status
    
    def init_app(self, app):
        """
        Initialize a Flask app with the configuration.
        
        Args:
            app: Flask application instance
        """
        # Update app configuration
        app.config.update(self.config)
        
        # Register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['config_manager'] = self


# Create a global instance of the configuration manager
config_manager = ConfigurationManager()


def get_config(key: str, default: Any = None) -> Any:
    """
    Convenience function to get a configuration value.
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    return config_manager.get(key, default)