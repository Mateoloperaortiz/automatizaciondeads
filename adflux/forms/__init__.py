"""
Paquete de formularios para AdFlux.

Este paquete contiene todos los formularios utilizados por AdFlux,
organizados en módulos específicos según su funcionalidad.
"""

# Importar funciones auxiliares
from .utils import get_job_openings, get_segment_choices

# Importar formularios de campaña
from .campaign_forms import CampaignForm

# Importar formularios de segmento
from .segment_forms import SegmentForm

# Importar formularios de configuración de API
from .api_settings_forms import MetaApiSettingsForm, GoogleAdsSettingsForm, GeminiSettingsForm

# Para mantener compatibilidad con el código existente
__all__ = [
    # Funciones auxiliares
    'get_job_openings',
    'get_segment_choices',

    # Formularios de campaña
    'CampaignForm',

    # Formularios de segmento
    'SegmentForm',

    # Formularios de configuración de API
    'MetaApiSettingsForm',
    'GoogleAdsSettingsForm',
    'GeminiSettingsForm'
]
