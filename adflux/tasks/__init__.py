"""
Paquete de tareas para AdFlux.

Este paquete contiene todas las tareas asíncronas y programadas utilizadas por AdFlux,
organizadas en módulos específicos según su funcionalidad.
"""

# Importar tareas de machine learning
from .ml_tasks import (
    scheduled_train_and_predict,
    trigger_train_and_predict,
    run_candidate_segmentation_task,
)

# Importar tareas de Meta Ads
from .meta_tasks import async_publish_adflux_campaign_to_meta

# Importar tareas de Google Ads
from .google_tasks import async_publish_adflux_campaign_to_google

# Importar tareas de sincronización
from .sync_tasks import sync_meta_insights_task

# Importar tareas generales de campaña
from .campaign_tasks import async_publish_adflux_campaign

# Para mantener compatibilidad con el código existente
__all__ = [
    # ML Tasks
    "scheduled_train_and_predict",
    "trigger_train_and_predict",
    "run_candidate_segmentation_task",
    # Meta Tasks
    "async_publish_adflux_campaign_to_meta",
    # Google Tasks
    "async_publish_adflux_campaign_to_google",
    # Sync Tasks
    "sync_meta_insights_task",
    # Campaign Tasks
    "async_publish_adflux_campaign",
]
