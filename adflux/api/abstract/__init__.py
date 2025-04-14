"""
Módulo de interfaces abstractas para APIs externas.

Este módulo contiene las interfaces abstractas para las APIs externas
utilizadas por AdFlux, como Meta Ads API, Google Ads API, etc.
"""

from .ad_api import AdAPI, AdCampaign, AdSet, Ad, AdCreative, AdInsight
from .api_factory import AdAPIFactory

__all__ = [
    'AdAPI',
    'AdCampaign',
    'AdSet',
    'Ad',
    'AdCreative',
    'AdInsight',
    'AdAPIFactory',
]
