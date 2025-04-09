"""
Tareas de Google Ads para AdFlux.

Este módulo contiene tareas relacionadas con la publicación y gestión de campañas
publicitarias en Google Ads.
"""

import os
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..extensions import db, celery
from ..models import Campaign, JobOpening
from ..api.google.campaigns import get_campaign_manager as get_google_campaign_manager

# Obtener instancia del logger
log = logging.getLogger(__name__)

# Helper Exception for parameter errors
class ParameterError(ValueError):
    pass

def _update_google_campaign_status(campaign_id: int, status: str, logger, external_ids: dict = None):
    """Helper to update Google campaign status and optionally external IDs."""
    try:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            campaign.status = status
            if external_ids:
                # Google Ads specific field mapping
                if "campaign_id" in external_ids:
                    campaign.external_id = external_ids["campaign_id"]
                if "ad_group_id" in external_ids:
                    campaign.google_ad_group_id = external_ids["ad_group_id"]
                if "ad_id" in external_ids:
                    campaign.google_ad_id = external_ids["ad_id"]
            db.session.commit()
            logger.info(f"Updated Google Campaign ID {campaign_id} status to '{status}'")
    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Failed to update Google Campaign ID {campaign_id} status to '{status}': {e}", exc_info=True
        )

def _prepare_google_publish_params(campaign: Campaign, job: JobOpening | None, app: object, logger, task_id: str) -> dict:
    """
    Prepares and validates parameters needed for Google Ads API calls.

    Raises:
        ParameterError: If essential parameters are missing or invalid.

    Returns:
        dict: A dictionary containing parameters for Google Ads API interaction.
    """
    params = {}
    api_data = {}

    # --- Customer ID ---
    customer_id = (
        os.getenv("GOOGLE_CUSTOMER_ID")
        or os.getenv("GOOGLE_ADS_TARGET_CUSTOMER_ID")
        or os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        # or campaign.google_customer_id # Add if there's a per-campaign customer_id field
    )
    if not customer_id:
        # Allow missing customer ID in dev/test for simulation
        if os.environ.get("FLASK_ENV", "production") in ["development", "testing"]:
            logger.warning(f"[Tarea {task_id}] Google Ads Customer ID missing. Using mock '1234567890' for dev/test.")
            customer_id = "1234567890"
        else:
            raise ParameterError("Google Ads Customer ID is required and not configured.")
    params["customer_id"] = customer_id

    # --- Campaign Data ---
    api_data["name"] = campaign.name
    try:
        # Assuming budget is stored in the main currency unit (e.g., dollars), convert to micros
        daily_budget_micros = int(float(campaign.daily_budget or 10.0) * 1_000_000)
    except (ValueError, TypeError):
        logger.warning(f"[Tarea {task_id}] Invalid daily_budget '{campaign.daily_budget}'. Using default 10,000,000 micros ($10).", exc_info=True)
        daily_budget_micros = 10_000_000 # Default to $10 in micros
    api_data["daily_budget_micros"] = daily_budget_micros # API expects micros
    api_data["start_date"] = campaign.start_date.strftime("%Y%m%d") if campaign.start_date else None
    api_data["end_date"] = campaign.end_date.strftime("%Y%m%d") if campaign.end_date else None
    api_data["status"] = campaign.initial_status or "PAUSED"
    api_data["landing_page_url"] = campaign.landing_page_url
    api_data["targeting_spec"] = campaign.targeting_spec or {}

    # --- Ad Texts (handle potential legacy fields) ---
    api_data["primary_text"] = getattr(campaign, "primary_text", getattr(campaign, "ad_text", None))
    api_data["headline"] = getattr(campaign, "headline", getattr(campaign, "ad_headline", None))
    api_data["link_description"] = getattr(campaign, "link_description", getattr(campaign, "ad_description", None))

    # --- Ad Image (handle potential legacy fields) ---
    api_data["creative_image_filename"] = getattr(campaign, "creative_image_filename", getattr(campaign, "ad_image_path", None))

    # --- Job Data (if linked) ---
    if job:
        api_data.update({
            "job_title": job.title,
            "job_description": job.description,
            "job_company": job.company_name,
            "job_location": job.location,
            "job_application_url": job.application_url,
        })
        # Default landing page if not set
        if not api_data["landing_page_url"]:
            api_data["landing_page_url"] = job.application_url
        # Default headline if not set
        if not api_data["headline"]:
            api_data["headline"] = f"{job.title} - {job.company_name}"
        # Default description if not set
        if not api_data["link_description"]:
            api_data["link_description"] = job.short_description or f"Aplica ahora para {job.title}"

    # --- Final Validation ---
    if not api_data.get("landing_page_url"):
        default_url = app.config.get("DEFAULT_LANDING_PAGE_URL")
        if default_url:
            api_data["landing_page_url"] = default_url
        else:
            raise ParameterError("Landing page URL is required and could not be determined.")

    if not api_data.get("headline"):
        # Cannot proceed without a headline
        raise ParameterError("Headline is required and could not be determined.")

    params["api_data"] = api_data
    return params

@celery.task(bind=True, name="tasks.async_publish_adflux_campaign_to_google",
             autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def async_publish_adflux_campaign_to_google(self, campaign_id: int, simulate: bool = True):
    app = current_app._get_current_object()
    logger = app.logger or log
    task_id = self.request.id
    logger.info(
        f"[Tarea {task_id}] Iniciando publicación Google Ads para Campaña ID: {campaign_id} (Simular: {simulate})"
    )

    results = {
        "message": "",
        "success": False,
        "external_campaign_id": None,
        "external_ids": None,
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
            return results # Non-retryable error

        if campaign.platform.lower() != "google":
            msg = f"Campaña {campaign_id} no es una campaña de Google Ads (plataforma: {campaign.platform})."
            logger.error(f"[Tarea {task_id}] {msg}")
            results["message"] = msg
            # Non-retryable, but maybe set status? Consider if needed.
            # _update_google_campaign_status(campaign_id, "failed", logger)
            return results # Non-retryable error

        job = campaign.job_opening # Can be None
        logger.info(f"[Tarea {task_id}] Encontrada Campaña Google '{campaign.name}'")

        _update_google_campaign_status(campaign_id, "publishing", logger)

        # 2. Preparar parámetros
        try:
            params = _prepare_google_publish_params(campaign, job, app, logger, task_id)
            customer_id = params["customer_id"]
            api_data = params["api_data"]
            logger.info(f"[Tarea {task_id}] Parámetros preparados para cliente Google {customer_id}")
        except ParameterError as e:
            msg = f"Error de parámetros: {e}"
            logger.error(f"[Tarea {task_id}] {msg}")
            results["message"] = msg
            _update_google_campaign_status(campaign_id, "failed", logger)
            return results # Non-retryable error

        # 3. Llamar a la función cliente de API (simulada por ahora)
        try:
            campaign_manager = get_google_campaign_manager()
            if not campaign_manager or not hasattr(campaign_manager, "publish_campaign"):
                # This indicates a setup issue, likely not recoverable by retry
                msg = "No se pudo inicializar el gestor de campañas de Google Ads"
                logger.error(f"[Tarea {task_id}] {msg}")
                results["message"] = msg
                _update_google_campaign_status(campaign_id, "failed", logger)
                return results # Non-retryable setup error

            if simulate:
                logger.info(
                    f"[Tarea {task_id}] Llamando a función SIMULADA de publicación Google Ads."
                )
                api_result = campaign_manager.publish_campaign(
                    customer_id, campaign.id, api_data
                )
            else:
                # Placeholder para llamada API real
                logger.warning(
                    f"[Tarea {task_id}] Publicación real en Google Ads aún no implementada. Ejecutando simulación en su lugar."
                )
                api_result = campaign_manager.publish_campaign(
                    customer_id, campaign.id, api_data
                )
                # En el futuro:
                # api_result = real_publish_google_campaign_api(customer_id, campaign.id, api_data)
        except Exception as e:
            msg = f"Error al inicializar/usar cliente Google Ads: {e}"
            logger.error(f"[Tarea {task_id}] {msg}", exc_info=True)
            # Raise exception to allow Celery retry for potentially transient errors
            raise Exception(msg) # Trigger retry or mark as failed

        # 4. Procesar resultado
        if not api_result.get("success"):
            # API call failed (simulated or real)
            msg = f"Fallo API Google Ads: {api_result.get('message', 'Error desconocido')}"
            logger.error(f"[Tarea {task_id}] {msg}")
            results["message"] = msg
            # Raise exception to allow Celery retry for API errors
            raise Exception(msg) # Trigger retry or mark as failed

        # Extraer IDs externos
        external_ids = api_result.get("external_ids", {})
        results["external_ids"] = external_ids
        results["external_campaign_id"] = external_ids.get("campaign_id")

        # 5. Actualizar objeto Campaign con IDs externos
        # Use the helper function for final update
        final_status = "published" if not simulate else "published_simulated"
        _update_google_campaign_status(campaign_id, final_status, logger, external_ids=external_ids)
        # Note: _update_google_campaign_status logs success/failure internally

        # 6. Éxito
        results["success"] = True
        results["message"] = api_result.get(
            "message", "Campaña publicada exitosamente en Google Ads"
        )
        logger.info(f"[Tarea {task_id}] {results['message']}")
        return results

    except Exception as e:
        # Catches:
        # - ParameterError (already handled, but catches unexpected issues)
        # - Exceptions raised from Google API calls (after potential retries)
        # - Any other unexpected errors
        db.session.rollback() # Ensure transaction state is clean
        task_id_str = f"[Tarea {task_id}] " if task_id else ""
        msg = f"Error procesando campaña Google {campaign_id}: {e}"
        logger.error(f"{task_id_str}{msg}", exc_info=True)

        # Attempt to mark campaign as failed if it was loaded
        if campaign:
            _update_google_campaign_status(campaign.id, "failed", logger)
        else:
            logger.warning(f"{task_id_str}No se pudo actualizar estado a 'failed' porque la campaña no se cargó.")

        results["message"] = msg
        results["success"] = False
        # Re-raise to ensure Celery marks the task as failed properly after retries.
        raise # Propagate the exception

# TODO: Implement actual Google Ads API call when simulate=False.
# TODO: Consider more granular error handling for specific Google API exceptions if needed.
# TODO: Standardize budget representation (e.g., always micros in DB or always convert in task).
