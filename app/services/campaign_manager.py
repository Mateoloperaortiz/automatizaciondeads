"""
Campaign Manager Factory
"""
from typing import Dict, Any, Union, Optional, List, cast
from app.models.candidate import Candidate
from app.models.ad_campaign import AdCampaign
from app import db

# Import API Framework manager when needed (lazy import to avoid circular imports)
# The actual import happens in the get_campaign_manager function

def get_campaign_manager() -> 'APIFrameworkCampaignManager':
    """
    Factory function to get appropriate campaign manager.
    
    Returns:
        APIFrameworkCampaignManager instance
    """
    from app.utils.config import config_manager
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if API Framework is enabled
    if config_manager.is_api_framework_enabled():
        # Check if all platforms are using the framework
        required_platforms = {'meta', 'twitter', 'google'}
        enabled_platforms = set(config_manager.get('API_FRAMEWORK_PLATFORMS', []))
        
        if required_platforms.issubset(enabled_platforms):
            # All required platforms are enabled, use framework manager
            try:
                from flask import current_app
                if hasattr(current_app, 'framework_campaign_manager'):
                    logger.info("Using Framework Campaign Manager from app context")
                    return current_app.framework_campaign_manager
            except RuntimeError:
                # Outside of application context, continue to fallback
                logger.debug("Not in application context, using standalone campaign manager")
                
    # Legacy manager has been removed, use framework manager as fallback
    from app.api_framework import APIFrameworkCampaignManager
    # Create a new instance without logging - to avoid Flask app context issues
    logger.info("Using standalone APIFrameworkCampaignManager instance")
    manager = APIFrameworkCampaignManager()
    
    # Initialize metrics for each client
    for platform, client in manager.platform_clients.items():
        if hasattr(client, 'initialize_metrics') and callable(client.initialize_metrics):
            client.initialize_metrics()
    
    return manager