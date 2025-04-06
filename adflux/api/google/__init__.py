"""
Cliente de API para Google Ads.

Este módulo proporciona funcionalidades para interactuar con la API de Google Ads,
incluyendo la gestión de campañas, grupos de anuncios y anuncios.
"""

# Importar cliente de Google Ads
from adflux.api.google.client import get_client, GoogleAdsApiClient

# Importar gestor de campañas
from adflux.api.google.campaigns import CampaignManager, get_campaign_manager

# Importar gestor de grupos de anuncios
from adflux.api.google.ad_groups import AdGroupManager, get_ad_group_manager

# Importar gestor de anuncios
from adflux.api.google.ads import AdManager, get_ad_manager

# Importar gestor de palabras clave
from adflux.api.google.keywords import KeywordManager, get_keyword_manager

# Importar gestor de targeting
from adflux.api.google.targeting import TargetingManager, get_targeting_manager

# Versión del módulo Google API
__version__ = '0.1.0'
