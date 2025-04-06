"""
Módulo API de AdFlux.

Este módulo proporciona acceso a las diferentes APIs utilizadas por AdFlux:
- Meta (Facebook/Instagram) Ads API
- Google Ads API
- Google Gemini API

Este archivo sirve como punto de entrada principal para todas las funcionalidades
de API, proporcionando una interfaz unificada para el resto de la aplicación.
"""

# Importar clientes para facilitar el acceso

# Meta API
from adflux.api.meta import get_client as get_meta_client
from adflux.api.meta import CampaignManager as MetaCampaignManager
from adflux.api.meta import AdSetManager as MetaAdSetManager
from adflux.api.meta import AdManager as MetaAdManager
from adflux.api.meta import InsightsManager as MetaInsightsManager
from adflux.api.meta import MetaUtils, get_meta_utils

# Google Ads API
from adflux.api.google import get_client as get_google_client
from adflux.api.google import CampaignManager as GoogleCampaignManager
from adflux.api.google import AdGroupManager as GoogleAdGroupManager
from adflux.api.google import AdManager as GoogleAdManager
from adflux.api.google import KeywordManager as GoogleKeywordManager
from adflux.api.google import TargetingManager as GoogleTargetingManager

# Gemini API
from adflux.api.gemini import get_client as get_gemini_client
from adflux.api.gemini import ContentGenerator, get_content_generator

# Versión del módulo API
__version__ = '0.1.0'
