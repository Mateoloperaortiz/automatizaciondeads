"""
Tareas de sincronización para AdFlux.

Este módulo contiene tareas relacionadas con la sincronización de datos entre AdFlux
y las plataformas de anuncios (Meta, Google, etc.).
"""

from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..extensions import db, celery
from ..models import Campaign, MetaInsight, JobOpening
from ..api.meta.insights import get_insights_manager

# Obtener instancia del logger
log = logging.getLogger(__name__)


def _process_and_save_insights(campaign_id: int, insights_data: list, logger, task_id: str) -> tuple[int, int, list]:
    """Processes and saves insights for a single campaign."""
    created_count = 0
    updated_count = 0
    processing_errors = []

    if not insights_data:
        return 0, 0, []

    for insight in insights_data:
        try:
            date_str = insight.get("date_start")
            if not date_str:
                logger.warning(f"[Tarea {task_id}] Insight para Campaña {campaign_id} sin 'date_start'. Omitiendo.")
                continue

            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            impressions = int(insight.get("impressions", 0))
            clicks = int(insight.get("clicks", 0))
            spend = float(insight.get("spend", 0))
            reach = int(insight.get("reach", 0))
            ctr = float(insight.get("ctr", 0))
            cpc = float(insight.get("cpc", 0))
            cpm = float(insight.get("cpm", 0))

            # Upsert logic
            existing_insight = MetaInsight.query.filter_by(campaign_id=campaign_id, date=date).first()

            if existing_insight:
                existing_insight.impressions = impressions
                existing_insight.clicks = clicks
                existing_insight.spend = spend
                existing_insight.reach = reach
                existing_insight.ctr = ctr
                existing_insight.cpc = cpc
                existing_insight.cpm = cpm
                existing_insight.updated_at = datetime.now()
                updated_count += 1
            else:
                new_insight = MetaInsight(
                    campaign_id=campaign_id,
                    date=date,
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    reach=reach,
                    ctr=ctr,
                    cpc=cpc,
                    cpm=cpm,
                )
                db.session.add(new_insight)
                created_count += 1

        except (ValueError, TypeError, KeyError) as e:
            err_msg = f"Error procesando insight para Campaña {campaign_id}, fecha {date_str}: {e}"
            logger.error(f"[Tarea {task_id}] {err_msg}", exc_info=True)
            processing_errors.append(err_msg)
            # Continue with the next insight
            continue

    # Commit changes for this campaign's insights
    try:
        db.session.commit()
        logger.debug(f"[Tarea {task_id}] Commit exitoso para insights de Campaña {campaign_id}")
    except SQLAlchemyError as e:
        db.session.rollback()
        err_msg = f"Error DB guardando insights para Campaña {campaign_id}: {e}"
        logger.error(f"[Tarea {task_id}] {err_msg}", exc_info=True)
        # Return counts as 0 and add this as a critical error for this campaign
        return 0, 0, processing_errors + [err_msg]

    return created_count, updated_count, processing_errors


@celery.task(bind=True, name="tasks.sync_meta_insights_task",
             autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def sync_meta_insights_task(self, campaign_id=None, date_preset="last_30d"):
    """
    Tarea Celery para sincronizar insights de Meta Ads.
    Si se proporciona un ID de campaña, solo se sincronizan los insights de esa campaña.
    De lo contrario, se sincronizan los insights de todas las campañas de Meta.

    Args:
        campaign_id: ID opcional de la campaña para sincronizar.
        date_preset: Preset de fecha para los insights ('today', 'yesterday', 'last_7d', 'last_30d', etc.).

    Returns:
        dict: Resultados de la sincronización.
    """
    app = current_app._get_current_object()
    logger = app.logger or log
    task_id = self.request.id
    log_prefix = f"[Tarea {task_id}]"
    logger.info(f"{log_prefix} Iniciando sincronización insights Meta (Preset: {date_preset}, Campaña: {campaign_id or 'Todas'}) ")

    results = {
        "success": False,
        "message": "Iniciando sincronización...",
        "total_campaigns_found": 0,
        "campaigns_processed": 0,
        "campaigns_skipped": 0,
        "insights_created": 0,
        "insights_updated": 0,
        "aggregated_errors": [],
    }

    try:
        # 1. Obtener campañas de Meta
        if campaign_id:
            logger.debug(f"{log_prefix} Filtrando por campaña específica: {campaign_id}")
            campaigns = Campaign.query.filter_by(id=campaign_id, platform="meta").all()
        else:
            logger.debug(f"{log_prefix} Obteniendo todas las campañas de Meta activas o pausadas con ID externo")
            campaigns = Campaign.query.filter_by(platform="meta").all()

        results["total_campaigns_found"] = len(campaigns)
        if not campaigns:
            msg = "No se encontraron campañas de Meta para sincronizar."
            logger.warning(f"{log_prefix} {msg}")
            results["message"] = msg
            results["success"] = True # Not an error if no campaigns exist
            return results

        # 2. Procesar cada campaña
        insights_manager = get_insights_manager()
        total_created = 0
        total_updated = 0
        total_processed = 0
        total_skipped = 0
        aggregated_errors = []

        for campaign in campaigns:
            campaign_log_prefix = f"{log_prefix} Campaña {campaign.id}"
            try:
                if not campaign.external_id:
                    logger.warning(f"{campaign_log_prefix}: Sin ID externo de Meta. Omitiendo.")
                    aggregated_errors.append(f"Campaña {campaign.id}: Sin ID externo.")
                    total_skipped += 1
                    continue

                logger.debug(f"{campaign_log_prefix}: Obteniendo insights (Meta ID: {campaign.external_id}) para preset {date_preset}")
                success, message, insights_data = insights_manager.get_insights(
                    object_id=campaign.external_id,
                    level="campaign",
                    date_preset=date_preset,
                    time_increment=1,  # Datos diarios
                )

                if not success:
                    err_msg = f"Error API obteniendo insights: {message}"
                    logger.error(f"{campaign_log_prefix}: {err_msg}")
                    aggregated_errors.append(f"Campaña {campaign.id}: {err_msg}")
                    # Consider if API error for one campaign should stop the whole task or just skip
                    # For now, skip this campaign
                    total_skipped += 1
                    continue

                # Procesar y guardar insights para esta campaña
                logger.debug(f"{campaign_log_prefix}: Procesando {len(insights_data)} insights obtenidos.")
                created, updated, processing_errors = _process_and_save_insights(
                    campaign.id, insights_data, logger, task_id
                )

                total_created += created
                total_updated += updated
                aggregated_errors.extend(processing_errors)

                # Only count as processed if insights were processed without DB error
                if not any(f"Error DB guardando insights para Campaña {campaign.id}" in err for err in processing_errors):
                    total_processed += 1
                    logger.info(f"{campaign_log_prefix}: Procesados {len(insights_data)} insights ({created} creados, {updated} actualizados).")
                else:
                    total_skipped +=1 # Count as skipped if DB error occurred during save

            except Exception as e:
                db.session.rollback()
                err_msg = f"Error inesperado procesando: {e}"
                logger.error(f"{campaign_log_prefix}: {err_msg}", exc_info=True)
                aggregated_errors.append(f"Campaña {campaign.id}: {err_msg}")
                total_skipped += 1
                continue

        # 3. Preparar resultados
        results["success"] = not aggregated_errors # Consider success=False if any errors occurred
        results["message"] = (
            f"Sincronización completada. Encontradas={results['total_campaigns_found']}, "
            f"Procesadas={total_processed}, Omitidas={total_skipped}, "
            f"Insights Creados={total_created}, Actualizados={total_updated}."
        )
        results["campaigns_processed"] = total_processed
        results["campaigns_skipped"] = total_skipped
        results["insights_created"] = total_created
        results["insights_updated"] = total_updated
        results["aggregated_errors"] = aggregated_errors

        logger.info(f"{log_prefix} {results['message']}")
        if aggregated_errors:
            logger.warning(
                f"{log_prefix} Se encontraron {len(aggregated_errors)} errores durante la sincronización. Ver 'aggregated_errors' en resultado."
            )

        return results

    except Exception as e:
        db.session.rollback()
        # Catch top-level errors (e.g., DB connection, insight manager init)
        # These might be caught by Celery retry first
        final_msg = f"Error CRÍTICO durante sincronización insights: {e}"
        logger.error(f"{log_prefix} {final_msg}", exc_info=True)
        results["message"] = final_msg
        results["success"] = False
        # Re-raise the exception to ensure Celery handles retry/failure state correctly
        raise
