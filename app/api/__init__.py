"""
API integrations for social media platforms.

This package contains modules for interacting with various social media platform APIs
for publishing job opening ads and managing ad campaigns.
"""

from app.api.meta import MetaAPI
# Import other API modules as they are created
# from app.api.twitter import TwitterAPI
# from app.api.google import GoogleAdsAPI

# Factory method to get API instance by platform name
def get_api(platform):
    """Get API instance by platform name.
    
    Args:
        platform (str): Platform name (meta, twitter, google, etc.)
        
    Returns:
        object: API instance for the specified platform
    """
    if platform.lower() == 'meta':
        return MetaAPI()
    # elif platform.lower() == 'twitter':
    #     return TwitterAPI()
    # elif platform.lower() == 'google':
    #     return GoogleAdsAPI()
    else:
        raise ValueError(f"Unsupported platform: {platform}") 