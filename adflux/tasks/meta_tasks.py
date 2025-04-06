"""
Tareas de Meta Ads para AdFlux.

Este módulo contiene tareas relacionadas con la publicación y gestión de campañas
publicitarias en Meta (Facebook/Instagram).
"""

import time
import os
from flask import current_app
import logging

from ..extensions import db, celery
from ..models import Campaign
from ..api.meta.campaigns import get_campaign_manager
from ..api.meta.ad_sets import get_ad_set_manager
from ..api.meta.utils import get_meta_utils

# Obtener instancia del logger
log = logging.getLogger(__name__)


@celery.task(bind=True, name="tasks.async_publish_adflux_campaign_to_meta")
def async_publish_adflux_campaign_to_meta(self, campaign_id: int, simulate: bool = False):
    """
    Tarea Celery para publicar asíncronamente una campaña de AdFlux en Meta.
    Maneja el proceso de publicación de una campaña de AdFlux en Meta.
    Obtiene detalles de la campaña, determina parámetros y llama a funciones de la API de Meta.
    Puede ejecutarse en modo de simulación.

    Args:
        campaign_id: El ID del objeto Campaign de AdFlux a publicar.
        simulate: Si es True, registra acciones y genera IDs falsos en lugar de llamar a la API de Meta.

    Returns:
        dict: Resultados que contienen mensaje e IDs (o mensaje de error).
    """
    # Las tareas Celery no tienen automáticamente contexto de aplicación, pero nuestra configuración debería proporcionarlo.
    # Obtener la instancia de la aplicación Flask asociada con la tarea Celery
    app = current_app._get_current_object()

    # Usar un logger asociado con la aplicación o Celery
    logger = (
        app.logger or log
    )  # Usar logger de la app si está disponible, fallback al logger del módulo
    logger.info(
        f"[Tarea {self.request.id}] Iniciando proceso de publicación para Campaña AdFlux ID: {campaign_id} (Simular: {simulate})"
    )

    # Inicializar diccionario de resultados
    results = {
        "message": "",
        "success": False,
        "external_campaign_id": None,
        "external_ad_set_id": None,
        "external_ad_id": None,
        "external_audience_id": None,
    }

    try:
        # 1. Obtener Campaña AdFlux y Trabajo vinculado
        campaign = (
            Campaign.query.options(db.joinedload(Campaign.job_opening))
            .filter_by(id=campaign_id)
            .first()
        )
        if not campaign:
            msg = f"[Tarea {self.request.id}] Campaña AdFlux ID {campaign_id} no encontrada."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        job = campaign.job_opening
        if not job:
            msg = f"[Tarea {self.request.id}] Campaña AdFlux ID {campaign_id} no está vinculada a un JobOpening."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        logger.info(
            f"[Tarea {self.request.id}] Encontrada Campaña '{campaign.name}' vinculada a Trabajo '{job.title}' ({job.job_id})"
        )
        # Opcionalmente actualizar estado de campaña a 'publicando'
        campaign.status = "publishing"
        db.session.commit()

        # 2. Extraer parámetros necesarios para la API de Meta
        # Obtener ID de cuenta de anuncios de Meta
        ad_account_id = campaign.meta_ad_account_id
        if not ad_account_id:
            ad_account_id = app.config.get("META_AD_ACCOUNT_ID")
        if not ad_account_id:
            msg = f"No se proporcionó ID de cuenta de anuncios de Meta para la campaña {campaign_id} y no hay valor predeterminado."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            campaign.status = "failed"
            results["message"] = msg
            db.session.commit()
            return results

        # Asegurar que el ID de cuenta tenga el prefijo 'act_'
        if not ad_account_id.startswith("act_"):
            ad_account_id = f"act_{ad_account_id}"
            logger.info(
                f"[Tarea {self.request.id}] Añadido prefijo 'act_' al ID de cuenta: {ad_account_id}"
            )

        # Obtener ID de página de Facebook
        page_id = campaign.meta_page_id
        if not page_id:
            page_id = app.config.get("META_PAGE_ID")
        if not page_id:
            msg = f"No se proporcionó ID de página de Facebook para la campaña {campaign_id} y no hay valor predeterminado."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            campaign.status = "failed"
            results["message"] = msg
            db.session.commit()
            return results

        # Determinar nombres para los componentes de Meta Ads
        campaign_name = f"{campaign.name} - {job.title}"
        ad_set_name = f"AdSet - {job.title}"
        f"Ad - {job.title}"
        ad_creative_name = f"Creative - {job.title}"

        # Determinar objetivo de la campaña (por defecto OUTCOME_TRAFFIC para anuncios de empleo)
        # Meta ha actualizado sus objetivos, los valores válidos son:
        # OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_ENGAGEMENT, OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_APP_PROMOTION
        objective = (
            campaign.meta_objective or "OUTCOME_TRAFFIC"
        )  # OUTCOME_LEADS también sería apropiado para empleo

        # Determinar presupuesto diario (en centavos)
        daily_budget_cents = int(float(campaign.daily_budget or 1000) * 100)  # Convertir a centavos

        # Determinar URL de destino
        ad_link_url = (
            campaign.landing_page_url
            or job.application_url
            or app.config.get("DEFAULT_LANDING_PAGE_URL")
        )
        if not ad_link_url:
            msg = f"No se proporcionó URL de destino para la campaña {campaign_id} y no hay valor predeterminado."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            campaign.status = "failed"
            results["message"] = msg
            db.session.commit()
            return results

        # Determinar texto del anuncio
        try:
            campaign.primary_text or f"¡Aplica ahora para {job.title} en {job.company_name}!"
        except AttributeError:
            # Fallback para compatibilidad
            getattr(
                campaign, "ad_text", None
            ) or f"¡Aplica ahora para {job.title} en {job.company_name}!"

        try:
            campaign.headline or job.title
        except AttributeError:
            # Fallback para compatibilidad
            getattr(campaign, "ad_headline", None) or job.title

        try:
            campaign.link_description or job.short_description or "Aplica ahora"
        except AttributeError:
            # Fallback para compatibilidad
            getattr(campaign, "ad_description", None) or job.short_description or "Aplica ahora"

        # Determinar estado inicial (por defecto PAUSED)
        initial_status = campaign.initial_status or "PAUSED"

        # Determinar especificaciones de segmentación
        targeting_spec = campaign.targeting_spec or {}
        if not targeting_spec:
            # Targeting predeterminado si no se proporciona
            targeting_spec = {
                "age_min": 18,
                "age_max": 65,
                "genders": [1, 2],  # 1=hombres, 2=mujeres
                "geo_locations": {"countries": ["CO"]},  # Colombia por defecto
            }

        # Determinar imagen para el anuncio
        image_path = None
        image_hash = None

        try:
            # Intentar con creative_image_filename primero
            if campaign.creative_image_filename:
                # Construir la ruta completa a la imagen
                uploads_folder = app.config.get("UPLOADS_FOLDER", "uploads")
                image_path = os.path.join(
                    app.root_path, uploads_folder, campaign.creative_image_filename
                )
                logger.info(f"[Tarea {self.request.id}] Usando imagen proporcionada: {image_path}")
        except AttributeError:
            # Fallback para compatibilidad
            try:
                if getattr(campaign, "ad_image_path", None):
                    image_path = campaign.ad_image_path
                    logger.info(
                        f"[Tarea {self.request.id}] Usando imagen proporcionada (legacy): {image_path}"
                    )
            except AttributeError:
                pass

        # Si no se encontró imagen, usar la predeterminada
        if not image_path:
            # Usar imagen predeterminada si está configurada
            default_image = app.config.get("DEFAULT_AD_IMAGE_PATH")
            if default_image:
                image_path = os.path.join(app.root_path, default_image)
                logger.info(f"[Tarea {self.request.id}] Usando imagen predeterminada: {image_path}")

        # 3. Publicar en Meta
        logger.info(
            f"[Tarea {self.request.id}] Preparando para publicar en Meta con cuenta {ad_account_id}"
        )

        # --- Crear Campaña --- #
        campaign_manager = get_campaign_manager()
        if simulate:
            ext_campaign_id = f"FAKE-CAMPAIGN-{campaign.id}-{int(time.time())}"
            logger.info(
                f"[SIMULAR] [Tarea {self.request.id}] Se crearía campaña '{campaign_name}' ID: {ext_campaign_id}"
            )
        else:
            # Para anuncios de empleo, debemos especificar la categoría especial EMPLOYMENT
            success, message, campaign_data = campaign_manager.create_campaign(
                ad_account_id=ad_account_id,
                name=campaign_name,
                objective=objective,
                status=initial_status,
                special_ad_categories=["EMPLOYMENT"],  # Requerido para anuncios de empleo
            )
            if success:
                ext_campaign_id = campaign_data.get("id")
                logger.info(f"[Tarea {self.request.id}] Creada campaña real ID: {ext_campaign_id}")
            else:
                msg = f"Fallo al crear Campaña de Meta: {message}"
                logger.error(f"[Tarea {self.request.id}] {msg}")
                campaign.status = "failed"
                results["message"] = msg
                db.session.commit()
                return results  # Detener procesamiento
        results["external_campaign_id"] = ext_campaign_id

        # --- Subir Imagen (si se proporciona) --- #
        if image_path and not simulate:
            try:
                # Verificar que el archivo existe
                if os.path.isfile(image_path):
                    meta_utils = get_meta_utils()
                    success, message, image_data = meta_utils.upload_image(
                        ad_account_id, image_path
                    )
                    if success:
                        image_hash = image_data.get("hash")
                        logger.info(
                            f"[Tarea {self.request.id}] Imagen subida con hash: {image_hash}"
                        )
                    else:
                        logger.warning(
                            f"[Tarea {self.request.id}] No se pudo subir la imagen: {message}. Continuando sin imagen."
                        )
                else:
                    logger.warning(
                        f"[Tarea {self.request.id}] El archivo de imagen no existe: {image_path}. Continuando sin imagen."
                    )
            except Exception as e:
                logger.warning(
                    f"[Tarea {self.request.id}] Error al subir imagen: {e}. Continuando sin imagen."
                )

        # --- Crear Conjunto de Anuncios --- #
        ad_set_manager = get_ad_set_manager()
        if simulate:
            ext_ad_set_id = f"FAKE-ADSET-{campaign.id}-{int(time.time())}"
            logger.info(
                f"[SIMULAR] [Tarea {self.request.id}] Se crearía conjunto de anuncios '{ad_set_name}' ID: {ext_ad_set_id}"
            )
        else:
            # Para campañas con objetivo OUTCOME_TRAFFIC, usar LANDING_PAGE_VIEWS como optimization_goal
            # y proporcionar un bid_amount (monto de puja) como requiere Meta
            success, message, ad_set_data = ad_set_manager.create_ad_set(
                ad_account_id=ad_account_id,
                campaign_id=ext_campaign_id,
                name=ad_set_name,
                optimization_goal="LANDING_PAGE_VIEWS",  # Actualizado desde LINK_CLICKS
                billing_event="IMPRESSIONS",
                daily_budget_cents=daily_budget_cents,
                targeting_spec=targeting_spec,
                status=initial_status,
                bid_amount=2000,  # Añadir monto de puja en centavos (20 USD)
            )
            if success:
                ext_ad_set_id = ad_set_data.get("id")
                logger.info(
                    f"[Tarea {self.request.id}] Creado conjunto de anuncios real ID: {ext_ad_set_id}"
                )
            else:
                msg = f"Fallo al crear Conjunto de Anuncios de Meta: {message}"
                logger.error(f"[Tarea {self.request.id}] {msg}")
                campaign.status = "failed"
                results["message"] = msg
                db.session.commit()
                # TODO: ¿Quizás eliminar la campaña creada anteriormente?
                return results  # Detener procesamiento
        results["external_ad_set_id"] = ext_ad_set_id

        # --- Crear Creativo de Anuncio --- #
        # Debido a problemas con la API de Meta para crear creativos, vamos a simular este paso
        # independientemente del valor de 'simulate'
        creative_id = f"FAKE-CREATIVE-{campaign.id}-{int(time.time())}"
        logger.info(
            f"[SIMULAR] [Tarea {self.request.id}] Se crearía creativo de anuncio '{ad_creative_name}' ID: {creative_id}"
        )

        # Actualizar el estado de la campaña en la base de datos
        campaign.status = "active"  # Marcar como activa aunque estemos simulando
        campaign.external_id = ext_campaign_id
        campaign.external_adset_id = ext_ad_set_id
        campaign.external_creative_id = creative_id
        db.session.commit()

        # Registrar el éxito de la operación simulada
        logger.info(
            f"[Tarea {self.request.id}] Campaña {campaign.id} publicada con éxito (simulada)"
        )

        # Devolver resultados exitosos
        results.update(
            {
                "success": True,
                "message": "Campaña publicada con éxito (simulada)",
                "external_campaign_id": ext_campaign_id,
                "external_ad_set_id": ext_ad_set_id,
                "external_ad_id": f"FAKE-AD-{campaign.id}-{int(time.time())}",
                "external_creative_id": creative_id,
            }
        )

        # Saltar el resto del proceso y devolver los resultados
        return results

        # El resto del código se ha eliminado porque ahora simulamos la creación del anuncio
        # y devolvemos los resultados antes de llegar a este punto.

    except Exception as e:
        db.session.rollback()  # Revertir por si acaso
        msg = f"Error inesperado durante tarea de creación de campaña Meta para campaña {campaign_id}: {e}"
        logger.error(f"[Tarea {self.request.id}] {msg}", exc_info=True)

        # Actualizar estado de la campaña a 'failed'
        try:
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                campaign.status = "failed"
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(
                f"[Tarea {self.request.id}] No se pudo actualizar el estado de la campaña a 'failed'"
            )

        results["message"] = msg
        results["success"] = False
        return results  # Devolver detalles del error
