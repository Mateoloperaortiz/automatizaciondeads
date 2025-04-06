"""
Tareas de Google Ads para AdFlux.

Este módulo contiene tareas relacionadas con la publicación y gestión de campañas
publicitarias en Google Ads.
"""

import time
import os
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..extensions import db, celery
from ..models import Campaign
from ..api.google.client import get_client as get_google_client
from ..api.google.campaigns import get_campaign_manager as get_google_campaign_manager

# Obtener instancia del logger
log = logging.getLogger(__name__)


@celery.task(bind=True, name='tasks.async_publish_adflux_campaign_to_google')
def async_publish_adflux_campaign_to_google(self, campaign_id: int, simulate: bool = True):
    """
    Tarea Celery para publicar asíncronamente una campaña de AdFlux en Google Ads.
    Obtiene detalles de la campaña, determina parámetros y llama a funciones de la API de Google Ads.
    Actualmente se ejecuta en modo de simulación por defecto.

    Args:
        campaign_id: El ID del objeto Campaign de AdFlux a publicar.
        simulate: Si es True (predeterminado), usa la llamada API simulada. Si es False, intentaría una llamada API real (aún no implementado).

    Returns:
        dict: Resultados que contienen mensaje e IDs externos (o mensaje de error).
    """
    app = current_app._get_current_object()
    logger = app.logger or log
    logger.info(f"[Tarea {self.request.id}] Iniciando proceso de publicación en Google Ads para Campaña AdFlux ID: {campaign_id} (Simular: {simulate})")

    results = {
        "message": "",
        "success": False,
        "external_campaign_id": None,
        "external_ids": None  # Diccionario para IDs de Google
    }

    try:
        # 1. Obtener Campaña AdFlux y Trabajo vinculado
        campaign = Campaign.query.options(db.joinedload(Campaign.job_opening)) \
            .filter_by(id=campaign_id).first()

        if not campaign:
            msg = f"[Tarea {self.request.id}] Campaña AdFlux ID {campaign_id} no encontrada."
            logger.error(msg)
            results["message"] = msg
            return results

        if campaign.platform.lower() != 'google':
            msg = f"[Tarea {self.request.id}] Campaña {campaign_id} no es una campaña de Google Ads (plataforma: {campaign.platform}). Abortando."
            logger.error(msg)
            results["message"] = msg
            return results

        logger.info(f"[Tarea {self.request.id}] Encontrada Campaña Google '{campaign.name}'")

        # Actualizar estado a 'publicando'
        campaign.status = 'publishing'
        db.session.commit()

        # 2. Preparar datos para la llamada API
        # Extraer campos relevantes del modelo de campaña AdFlux
        campaign_data_for_api = {
            'name': campaign.name,
            'daily_budget': campaign.daily_budget or 1000,  # en centavos
            'start_date': campaign.start_date.strftime('%Y%m%d') if campaign.start_date else None,
            'end_date': campaign.end_date.strftime('%Y%m%d') if campaign.end_date else None,
            'status': campaign.initial_status or 'PAUSED',
            'landing_page_url': campaign.landing_page_url,
            'targeting_spec': campaign.targeting_spec or {}
        }

        # Manejar atributos que pueden no existir en el modelo Campaign
        try:
            campaign_data_for_api['primary_text'] = campaign.primary_text
        except AttributeError:
            try:
                campaign_data_for_api['ad_text'] = campaign.ad_text
            except AttributeError:
                pass

        try:
            campaign_data_for_api['headline'] = campaign.headline
        except AttributeError:
            try:
                campaign_data_for_api['ad_headline'] = campaign.ad_headline
            except AttributeError:
                pass

        try:
            campaign_data_for_api['link_description'] = campaign.link_description
        except AttributeError:
            try:
                campaign_data_for_api['ad_description'] = campaign.ad_description
            except AttributeError:
                pass

        try:
            campaign_data_for_api['creative_image_filename'] = campaign.creative_image_filename
        except AttributeError:
            try:
                campaign_data_for_api['ad_image_path'] = campaign.ad_image_path
            except AttributeError:
                pass

        # Obtener datos del trabajo vinculado
        job = campaign.job_opening
        if job:
            campaign_data_for_api.update({
                'job_title': job.title,
                'job_description': job.description,
                'job_company': job.company_name,
                'job_location': job.location,
                'job_application_url': job.application_url
            })

        # Añadir valores predeterminados si faltan campos obligatorios
        if not campaign_data_for_api.get('landing_page_url') and job and job.application_url:
            campaign_data_for_api['landing_page_url'] = job.application_url
        elif not campaign_data_for_api.get('landing_page_url'):
            campaign_data_for_api['landing_page_url'] = app.config.get('DEFAULT_LANDING_PAGE_URL', 'https://example.com')

        # Asegurarse de que tenemos un headline
        if not campaign_data_for_api.get('headline') and not campaign_data_for_api.get('ad_headline') and job:
            campaign_data_for_api['headline'] = f"{job.title} - {job.company_name}"

        # Asegurarse de que tenemos una descripción
        if not campaign_data_for_api.get('link_description') and not campaign_data_for_api.get('ad_description') and job:
            campaign_data_for_api['link_description'] = job.short_description or f"Aplica ahora para {job.title}"

        # 3. Llamar a la función cliente de API (simulada por ahora)
        # Obtener el ID del cliente de Google Ads del entorno o de los datos de la campaña
        # Intentar obtener el ID del cliente de varias fuentes posibles
        customer_id = (os.getenv('GOOGLE_CUSTOMER_ID') or
                      os.getenv('GOOGLE_ADS_TARGET_CUSTOMER_ID') or
                      os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID') or
                      campaign_data_for_api.get('customer_id'))

        # Si no se encuentra un ID de cliente, usar un valor simulado para desarrollo
        if not customer_id and os.environ.get('FLASK_ENV', 'development') in ['development', 'testing']:
            logger.warning(f"[Tarea {self.request.id}] No se encontró un ID de cliente de Google Ads. Usando valor simulado para desarrollo.")
            customer_id = '1234567890'  # Valor simulado para desarrollo
        elif not customer_id:
            logger.error(f"[Tarea {self.request.id}] No se proporcionó un ID de cliente de Google Ads")
            return False, "No se proporcionó un ID de cliente de Google Ads"

        # Obtener el gestor de campañas de Google
        try:
            campaign_manager = get_google_campaign_manager()

            # Verificar si el gestor de campañas se inició correctamente
            if not campaign_manager or not hasattr(campaign_manager, 'publish_campaign'):
                logger.error(f"[Tarea {self.request.id}] No se pudo inicializar el gestor de campañas de Google Ads")
                return {
                    'success': False,
                    'message': "No se pudo inicializar el cliente de Google Ads",
                    'external_campaign_id': None,
                    'external_ids': None
                }

            if simulate:
                logger.info(f"[Tarea {self.request.id}] Llamando a función SIMULADA de publicación de Google Ads.")
                api_result = campaign_manager.publish_campaign(customer_id, campaign.id, campaign_data_for_api)
            else:
                # Placeholder para llamada API real
                logger.warning(f"[Tarea {self.request.id}] Publicación real en Google Ads aún no implementada. Ejecutando simulación en su lugar.")
                api_result = campaign_manager.publish_campaign(customer_id, campaign.id, campaign_data_for_api)
                # En el futuro:
                # api_result = real_publish_google_campaign_api(campaign.id, campaign_data_for_api)
        except Exception as e:
            logger.error(f"[Tarea {self.request.id}] Error al inicializar o usar el cliente de Google Ads: {str(e)}")
            return {
                'success': False,
                'message': f"Error al publicar en Google Ads: {str(e)}",
                'external_campaign_id': None,
                'external_ids': None
            }

        # 4. Procesar resultado
        if not api_result.get('success'):
            msg = f"Error al publicar en Google Ads: {api_result.get('message', 'Error desconocido')}"
            logger.error(f"[Tarea {self.request.id}] {msg}")
            campaign.status = 'failed'
            db.session.commit()
            results["message"] = msg
            return results

        # Extraer IDs externos
        external_ids = api_result.get('external_ids', {})
        results["external_ids"] = external_ids
        results["external_campaign_id"] = external_ids.get('campaign_id')

        # 5. Actualizar objeto Campaign con IDs externos
        try:
            campaign.external_id = external_ids.get('campaign_id')
            campaign.google_ad_group_id = external_ids.get('ad_group_id')
            campaign.google_ad_id = external_ids.get('ad_id')
            campaign.status = 'published'  # o 'active' dependiendo de la lógica de negocio
            db.session.commit()
            logger.info(f"[Tarea {self.request.id}] Actualizada Campaña AdFlux {campaign_id} con IDs externos de Google")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"[Tarea {self.request.id}] Error al actualizar Campaña AdFlux {campaign_id} con IDs externos: {e}")
            # Continuar a pesar del error de BD - la campaña se creó en Google pero no se actualizaron los IDs en AdFlux

        # 6. Éxito
        results["success"] = True
        results["message"] = api_result.get('message', "Campaña publicada exitosamente en Google Ads")
        logger.info(f"[Tarea {self.request.id}] {results['message']}")
        return results

    except Exception as e:
        db.session.rollback()  # Revertir por si acaso
        msg = f"Error inesperado durante tarea de creación de campaña Google para campaña {campaign_id}: {e}"
        logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)

        # Actualizar estado de la campaña a 'failed'
        try:
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                campaign.status = 'failed'
                db.session.commit()
        except:
            db.session.rollback()
            logger.error(f"[Tarea {self.request.id}] No se pudo actualizar el estado de la campaña a 'failed'")

        results["message"] = msg
        results["success"] = False
        return results  # Devolver detalles del error
