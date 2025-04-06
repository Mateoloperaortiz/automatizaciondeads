"""
Cliente de API para Meta (Facebook/Instagram) Ads.

Este módulo proporciona funcionalidades para interactuar con la API de Meta Ads,
incluyendo la gestión de campañas, conjuntos de anuncios, anuncios e insights.
"""

# Importar cliente principal
from adflux.api.meta.client import get_client, MetaApiClient

# Importar gestor de campañas
from adflux.api.meta.campaigns import CampaignManager, get_campaign_manager

# Importar gestor de conjuntos de anuncios
from adflux.api.meta.ad_sets import AdSetManager, get_ad_set_manager

# Importar gestor de anuncios
from adflux.api.meta.ads import AdManager, get_ad_manager

# Importar gestor de insights
from adflux.api.meta.insights import InsightsManager, get_insights_manager

# Importar utilidades
from adflux.api.meta.utils import MetaUtils, get_meta_utils

# Versión del módulo Meta API
__version__ = '0.1.0'
