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
from ..models import Campaign, JobOpening
from ..api.meta.campaigns import get_campaign_manager
from ..api.meta.ad_sets import get_ad_set_manager
from ..api.meta.utils import get_meta_utils

# Obtener instancia del logger
log = logging.getLogger(__name__)


# Helper Exception for parameter errors
class ParameterError(ValueError):
    pass


def _update_campaign_status(campaign_id: int, status: str, logger, external_ids: dict = None):
    """Helper to update campaign status and optionally external IDs."""
    try:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            campaign.status = status
            if external_ids:
                if "campaign" in external_ids:
                    campaign.external_id = external_ids["campaign"]
                if "adset" in external_ids:
                    campaign.external_adset_id = external_ids["adset"]
                if "creative" in external_ids: # Assuming simulation still uses this
                    campaign.external_creative_id = external_ids["creative"]
            db.session.commit()
            logger.info(f"Updated Campaign ID {campaign_id} status to '{status}'")
    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Failed to update Campaign ID {campaign_id} status to '{status}': {e}", exc_info=True
        )


def _prepare_meta_publish_params(campaign: Campaign, job: JobOpening, app: object, logger) -> dict:
    """
    Prepares and validates parameters needed for Meta API calls.

    Raises:
        ParameterError: If essential parameters are missing or invalid.

    Returns:
        dict: A dictionary containing parameters for Meta API interaction.
    """
    params = {}

    # --- Ad Account ID ---
    ad_account_id = campaign.meta_ad_account_id or app.config.get("META_AD_ACCOUNT_ID")
    if not ad_account_id:
        raise ParameterError("Meta Ad Account ID not provided and no default configured.")
    if not ad_account_id.startswith("act_"):
        ad_account_id = f"act_{ad_account_id}"
        logger.info(f"Added prefix 'act_' to Ad Account ID: {ad_account_id}")
    params["ad_account_id"] = ad_account_id

    # --- Page ID ---
    page_id = campaign.meta_page_id or app.config.get("META_PAGE_ID")
    if not page_id:
        raise ParameterError("Meta Page ID not provided and no default configured.")
    params["page_id"] = page_id

    # --- Naming ---
    params["campaign_name"] = f"{campaign.name} - {job.title}"
    params["ad_set_name"] = f"AdSet - {job.title}"
    # params["ad_name"] = f"Ad - {job.title}" # Currently unused due to simulation
    params["ad_creative_name"] = f"Creative - {job.title}"

    # --- Objective ---
    # Meta objectives: OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_ENGAGEMENT, OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_APP_PROMOTION
    params["objective"] = campaign.meta_objective or "OUTCOME_TRAFFIC"

    # --- Budget ---
    try:
        daily_budget_cents = int(float(campaign.daily_budget or 1000) * 100) # Default to 1000 units (e.g., $10.00 if currency is USD)
    except (ValueError, TypeError):
         logger.warning(f"Invalid daily_budget value '{campaign.daily_budget}'. Using default 100000 cents ($10).")
         daily_budget_cents = 100000 # Default to 1000 * 100 cents
    params["daily_budget_cents"] = daily_budget_cents


    # --- Ad Link URL ---
    ad_link_url = (
        campaign.landing_page_url
        or job.application_url
        or app.config.get("DEFAULT_LANDING_PAGE_URL")
    )
    if not ad_link_url:
        raise ParameterError("Ad destination URL not provided and no default configured.")
    params["ad_link_url"] = ad_link_url

    # --- Ad Creatives (Text) ---
    # Using getattr for potential backward compatibility if fields were renamed
    params["primary_text"] = getattr(campaign, "primary_text", None) or f"¡Aplica ahora para {job.title} en {job.company_name}!"
    params["headline"] = getattr(campaign, "headline", None) or job.title
    params["link_description"] = getattr(campaign, "link_description", None) or job.short_description or "Aplica ahora"

    # --- Initial Status ---
    params["initial_status"] = campaign.initial_status or "PAUSED"

    # --- Targeting ---
    targeting_spec = campaign.targeting_spec or {}
    if not targeting_spec:
        targeting_spec = {
            "age_min": 18,
            "age_max": 65,
            "genders": [1, 2],
            "geo_locations": {"countries": ["CO"]}, # Default: Colombia
        }
    params["targeting_spec"] = targeting_spec

    # --- Image ---
    image_path = None
    # Using getattr for potential backward compatibility
    image_filename = getattr(campaign, "creative_image_filename", None)
    if image_filename:
        uploads_folder = app.config.get("UPLOADS_FOLDER", "uploads")
        image_path = os.path.join(app.root_path, uploads_folder, image_filename)
        logger.info(f"Using provided image path: {image_path}")
    else: # Fallback to legacy or default
        legacy_image_path = getattr(campaign, "ad_image_path", None)
        if legacy_image_path:
             image_path = legacy_image_path
             logger.info(f"Using provided image path (legacy): {image_path}")
        else:
            default_image = app.config.get("DEFAULT_AD_IMAGE_PATH")
            if default_image:
                image_path = os.path.join(app.root_path, default_image)
                logger.info(f"Using default image path: {image_path}")

    params["image_path"] = image_path # Can be None

    return params


@celery.task(bind=True, name="tasks.async_publish_adflux_campaign_to_meta",
             autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
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
    task_id = self.request.id
    logger.info(
        f"[Tarea {task_id}] Iniciando publicación para Campaña AdFlux ID: {campaign_id} (Simular: {simulate})"
    )

    # Inicializar diccionario de resultados
    results = {
        "message": "",
        "success": False,
        "external_campaign_id": None,
        "external_ad_set_id": None,
        "external_ad_id": None,
        "external_creative_id": None,
        "image_hash": None,
    }

    campaign = None # Initialize campaign to None

    try:
        # 1. Obtener Campaña AdFlux y Trabajo vinculado
        campaign = (
            Campaign.query.options(db.joinedload(Campaign.job_opening))
            .filter_by(id=campaign_id)
            .first()
        )
        if not campaign:
            msg = f"Campaña AdFlux ID {campaign_id} no encontrada."
            logger.error(f"[Tarea {task_id}] {msg}")
            results["message"] = msg
            # No need to update status if campaign not found
            return results # Non-retryable error

        job = campaign.job_opening
        if not job:
            msg = f"Campaña AdFlux ID {campaign_id} no está vinculada a un JobOpening."
            logger.error(f"[Tarea {task_id}] {msg}")
            results["message"] = msg
            _update_campaign_status(campaign_id, "failed", logger)
            return results # Non-retryable error

        logger.info(
            f"[Tarea {task_id}] Encontrada Campaña '{campaign.name}' vinculada a Trabajo '{job.title}' ({job.job_id})"
        )

        # Update status to 'publishing' before potentially long operations
        _update_campaign_status(campaign_id, "publishing", logger)

        # 2. Preparar parámetros
        try:
            params = _prepare_meta_publish_params(campaign, job, app, logger)
            ad_account_id = params["ad_account_id"] # Needed separately
            logger.info(f"[Tarea {task_id}] Parámetros preparados para cuenta {ad_account_id}")
        except ParameterError as e:
            msg = f"Error de parámetros: {e}"
            logger.error(f"[Tarea {task_id}] {msg}")
            results["message"] = msg
            _update_campaign_status(campaign_id, "failed", logger)
            return results # Non-retryable error

        # 3. Publicar en Meta
        logger.info(f"[Tarea {task_id}] Iniciando publicación en Meta...")

        ext_campaign_id = None
        ext_ad_set_id = None
        ext_creative_id = None # Used in simulation
        image_hash = None

        # --- Crear Campaña ---
        if simulate:
            ext_campaign_id = f"FAKE-CAMPAIGN-{campaign.id}-{int(time.time())}"
            logger.info(
                f"[SIMULAR] [Tarea {task_id}] Se crearía campaña '{params['campaign_name']}' ID: {ext_campaign_id}"
            )
        else:
            campaign_manager = get_campaign_manager()
            success, message, campaign_data = campaign_manager.create_campaign(
                ad_account_id=ad_account_id,
                name=params["campaign_name"],
                objective=params["objective"],
                status=params["initial_status"],
                special_ad_categories=["EMPLOYMENT"],
            )
            if success:
                ext_campaign_id = campaign_data.get("id")
                logger.info(f"[Tarea {task_id}] Creada campaña real ID: {ext_campaign_id}")
            else:
                msg = f"Fallo al crear Campaña de Meta: {message}"
                logger.error(f"[Tarea {task_id}] {msg}")
                # Let Celery retry for transient errors, otherwise fail
                raise Exception(msg) # Raise exception to trigger retry or mark as failed

        # --- Subir Imagen (si aplica y no simula) ---
        if params.get("image_path") and not simulate:
            image_path = params["image_path"]
            try:
                if os.path.isfile(image_path):
                    meta_utils = get_meta_utils()
                    success, message, image_data = meta_utils.upload_image(
                        ad_account_id, image_path
                    )
                    if success:
                        image_hash = image_data.get("hash")
                        logger.info(
                            f"[Tarea {task_id}] Imagen subida con hash: {image_hash}"
                        )
                    else:
                        logger.warning(
                            f"[Tarea {task_id}] No se pudo subir la imagen ({image_path}): {message}. Continuando sin imagen."
                        )
                else:
                    logger.warning(
                        f"[Tarea {task_id}] El archivo de imagen no existe: {image_path}. Continuando sin imagen."
                    )
            except Exception as e:
                logger.warning(
                    f"[Tarea {task_id}] Error al subir imagen '{image_path}': {e}. Continuando sin imagen.", exc_info=True
                )
                # Decide if image upload failure is critical. Here we continue.

        # --- Crear Conjunto de Anuncios ---
        if simulate:
            ext_ad_set_id = f"FAKE-ADSET-{campaign.id}-{int(time.time())}"
            logger.info(
                f"[SIMULAR] [Tarea {task_id}] Se crearía conjunto de anuncios '{params['ad_set_name']}' ID: {ext_ad_set_id}"
            )
        else:
            if not ext_campaign_id:
                 # Should not happen if previous step succeeded, but defensive check
                 raise Exception("External campaign ID is missing before creating Ad Set.")

            ad_set_manager = get_ad_set_manager()
            success, message, ad_set_data = ad_set_manager.create_ad_set(
                ad_account_id=ad_account_id,
                campaign_id=ext_campaign_id,
                name=params["ad_set_name"],
                optimization_goal="LANDING_PAGE_VIEWS",
                billing_event="IMPRESSIONS",
                daily_budget_cents=params["daily_budget_cents"],
                targeting_spec=params["targeting_spec"],
                status=params["initial_status"],
                bid_amount=2000, # Example bid amount, consider making configurable
            )
            if success:
                ext_ad_set_id = ad_set_data.get("id")
                logger.info(
                    f"[Tarea {task_id}] Creado conjunto de anuncios real ID: {ext_ad_set_id}"
                )
            else:
                msg = f"Fallo al crear Conjunto de Anuncios de Meta: {message}"
                logger.error(f"[Tarea {task_id}] {msg}")
                # TODO: Consider cleanup? (e.g., delete the created campaign)
                # Let Celery retry for transient errors, otherwise fail
                raise Exception(msg) # Raise exception to trigger retry or mark as failed

        # --- Crear Creativo de Anuncio (Simulado) ---
        # !! Manteniendo la lógica de simulación existente !!
        ext_creative_id = f"FAKE-CREATIVE-{campaign.id}-{int(time.time())}"
        logger.info(
            f"[SIMULAR] [Tarea {task_id}] Se crearía creativo '{params['ad_creative_name']}' ID: {ext_creative_id}"
        )
        # Si se implementara la creación real:
        # if simulate: ...
        # else:
        #   ad_creative_manager = get_ad_creative_manager()
        #   success, message, creative_data = ad_creative_manager.create_ad_creative(...)
        #   if success: ext_creative_id = ...
        #   else: raise Exception(...)

        # 4. Actualizar DB y finalizar
        final_status = "active" if not simulate else "active_simulated" # Use a distinct status for simulated success
        external_ids_map = {
            "campaign": ext_campaign_id,
            "adset": ext_ad_set_id,
            "creative": ext_creative_id,
        }
        _update_campaign_status(campaign_id, final_status, logger, external_ids=external_ids_map)

        logger.info(
            f"[Tarea {task_id}] Campaña {campaign.id} procesada con éxito ({'simulada' if simulate else 'real'})."
        )

        results.update(
            {
                "success": True,
                "message": f"Campaña procesada con éxito ({'simulada' if simulate else 'real'}).",
                "external_campaign_id": ext_campaign_id,
                "external_ad_set_id": ext_ad_set_id,
                # "external_ad_id": ..., # No Ad created in this flow
                "external_creative_id": ext_creative_id, # From simulation
                "image_hash": image_hash,
            }
        )
        return results

    except Exception as e:
        # This block catches:
        # - ParameterError during preparation (already handled, but catches unexpected issues)
        # - Exceptions raised from Meta API calls (after potential retries)
        # - Any other unexpected errors during the process
        db.session.rollback() # Ensure transaction state is clean
        task_id_str = f"[Tarea {task_id}] " if task_id else ""
        msg = f"Error procesando campaña Meta {campaign_id}: {e}"
        logger.error(f"{task_id_str}{msg}", exc_info=True)

        # Attempt to mark campaign as failed if it was loaded
        if campaign:
            _update_campaign_status(campaign.id, "failed", logger)
        else:
             logger.warning(f"{task_id_str}No se pudo actualizar estado a 'failed' porque la campaña no se cargó.")


        results["message"] = msg
        results["success"] = False

        # Propagate the exception if it's a retryable one, Celery handles it
        # If it's the final attempt or a non-retryable error caught here,
        # the task state will be FAILURE.
        # We re-raise to ensure Celery marks the task as failed properly after retries.
        raise # Reraise the exception caught

# Note: The simulation logic for Ad Creative creation remains as per the original code's comment.
# If real creative creation is needed, the relevant API calls should be added.
# Consider making bid_amount configurable.
# Consider more specific exception handling for Meta API errors if needed for cleanup logic.
