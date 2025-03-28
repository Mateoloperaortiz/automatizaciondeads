"""
API Integration Framework for MagnetoCursor.

This package provides a unified framework for integrating with various social media APIs.
It includes standardized request/response objects, caching, metrics tracking, and
platform-specific client implementations.
"""

from app.api_framework.base import APIRequest, APIResponse, BaseAPIClient
from app.api_framework.meta_client import MetaAPIClient
from app.api_framework.twitter_client import TwitterAPIClient
from app.api_framework.google_client import GoogleAPIClient
from app.api_framework.cache import APICache, TTLCache
from app.api_framework.metrics import APIMetrics
from app.api_framework.campaign_manager import APIFrameworkCampaignManager

# Version
__version__ = '0.1.0'