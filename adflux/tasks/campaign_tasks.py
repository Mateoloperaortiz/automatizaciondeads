"""
Tareas generales de campaña para AdFlux.

Este módulo contiene tareas relacionadas con la gestión de campañas publicitarias
que son comunes a todas las plataformas.
"""

import time
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..extensions import db, celery
from ..models import Campaign
from .meta_tasks import async_publish_adflux_campaign_to_meta
from .google_tasks import async_publish_adflux_campaign_to_google

# Obtener instancia del logger
log = logging.getLogger(__name__)


@celery.task(bind=True, name='tasks.async_publish_adflux_campaign')
def async_publish_adflux_campaign(self, campaign_id: int, simulate: bool = False):
    """
    Tarea Celery para publicar asíncronamente una campaña de AdFlux en la plataforma correspondiente.
    Determina la plataforma de la campaña y llama a la tarea específica de esa plataforma.

    Args:
        campaign_id: El ID del objeto Campaign de AdFlux a publicar.
        simulate: Si es True, se ejecuta en modo de simulación.

    Returns:
        dict: Resultados que contienen mensaje e IDs externos (o mensaje de error).
    """
    app = current_app._get_current_object()
    logger = app.logger or log
    logger.info(f"[Tarea {self.request.id}] Iniciando proceso de publicación para Campaña AdFlux ID: {campaign_id} (Simular: {simulate})")

    results = {
        "message": "",
        "success": False,
        "platform": None,
        "task_id": None
    }

    try:
        # 1. Obtener Campaña AdFlux
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            msg = f"Campaña AdFlux ID {campaign_id} no encontrada."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        # 2. Determinar la plataforma
        platform = campaign.platform.lower() if campaign.platform else None
        if not platform:
            msg = f"Campaña AdFlux ID {campaign_id} no tiene plataforma especificada."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        results["platform"] = platform

        # 3. Llamar a la tarea específica de la plataforma
        if platform == 'meta' or platform == 'facebook':
            logger.info(f"[Tarea {self.request.id}] Delegando a tarea de publicación de Meta para campaña {campaign_id}")
            task = async_publish_adflux_campaign_to_meta.delay(campaign_id, simulate)
            results["task_id"] = task.id
            results["success"] = True
            results["message"] = f"Tarea de publicación en Meta iniciada con ID: {task.id}"
        elif platform == 'google':
            logger.info(f"[Tarea {self.request.id}] Delegando a tarea de publicación de Google para campaña {campaign_id}")
            task = async_publish_adflux_campaign_to_google.delay(campaign_id, simulate)
            results["task_id"] = task.id
            results["success"] = True
            results["message"] = f"Tarea de publicación en Google iniciada con ID: {task.id}"
        else:
            msg = f"Plataforma '{platform}' no soportada para la campaña {campaign_id}."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        logger.info(f"[Tarea {self.request.id}] {results['message']}")
        return results

    except Exception as e:
        msg = f"Error inesperado al iniciar tarea de publicación para campaña {campaign_id}: {e}"
        logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)
        results["message"] = msg
        return results
