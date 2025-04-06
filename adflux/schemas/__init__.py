"""
Paquete de esquemas para AdFlux.

Este paquete contiene todos los esquemas de Marshmallow utilizados por AdFlux,
organizados en módulos específicos según su funcionalidad.
"""

# Importar esquemas de Meta
from .meta import (
    meta_campaign_schema, meta_campaigns_schema,
    meta_ad_set_schema, meta_ad_sets_schema,
    meta_ad_schema, meta_ads_schema,
    meta_insight_schema, meta_insights_schema
)

# Importar esquemas de Trabajo
from .job import job_schema, jobs_schema

# Importar esquemas de Candidato
from .candidate import candidate_schema, candidates_schema

# Importar esquemas de Aplicación
from .application import application_schema, applications_schema

# Importar esquemas de Campaña
from .campaign import campaign_schema, campaigns_schema

# Para mantener compatibilidad con el código existente
__all__ = [
    # Esquemas de Meta
    'meta_campaign_schema', 'meta_campaigns_schema',
    'meta_ad_set_schema', 'meta_ad_sets_schema',
    'meta_ad_schema', 'meta_ads_schema',
    'meta_insight_schema', 'meta_insights_schema',
    
    # Esquemas de Trabajo
    'job_schema', 'jobs_schema',
    
    # Esquemas de Candidato
    'candidate_schema', 'candidates_schema',
    
    # Esquemas de Aplicación
    'application_schema', 'applications_schema',
    
    # Esquemas de Campaña
    'campaign_schema', 'campaigns_schema'
]
