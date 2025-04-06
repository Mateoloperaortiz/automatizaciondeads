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
from ..models import Campaign, MetaInsight
from ..api.meta.insights import get_insights_manager

# Obtener instancia del logger
log = logging.getLogger(__name__)


@celery.task(bind=True, name="tasks.sync_meta_insights_task")
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
    logger.info(
        f"[Tarea {self.request.id}] Iniciando sincronización de insights de Meta para preset: {date_preset}"
    )

    results = {
        "success": False,
        "message": "",
        "campaigns_processed": 0,
        "insights_created": 0,
        "insights_updated": 0,
        "errors": [],
    }

    try:
        # 1. Obtener campañas de Meta
        if campaign_id:
            logger.info(
                f"[Tarea {self.request.id}] Sincronizando insights para campaña específica: {campaign_id}"
            )
            campaigns = Campaign.query.filter_by(id=campaign_id, platform="meta").all()
        else:
            logger.info(
                f"[Tarea {self.request.id}] Sincronizando insights para todas las campañas de Meta"
            )
            campaigns = Campaign.query.filter_by(platform="meta").all()

        if not campaigns:
            msg = "No se encontraron campañas de Meta para sincronizar."
            logger.warning(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        # 2. Procesar cada campaña
        insights_manager = get_insights_manager()
        insights_created = 0
        insights_updated = 0
        campaigns_processed = 0
        errors = []

        for campaign in campaigns:
            try:
                # Verificar que la campaña tenga un ID externo
                if not campaign.external_id:
                    logger.warning(
                        f"[Tarea {self.request.id}] Campaña {campaign.id} no tiene ID externo de Meta. Omitiendo."
                    )
                    errors.append(f"Campaña {campaign.id} no tiene ID externo de Meta")
                    continue

                # Obtener insights para la campaña
                logger.info(
                    f"[Tarea {self.request.id}] Obteniendo insights para campaña {campaign.id} (Meta ID: {campaign.external_id})"
                )
                success, message, insights_data = insights_manager.get_insights(
                    object_id=campaign.external_id,
                    level="campaign",
                    date_preset=date_preset,
                    time_increment=1,  # Datos diarios
                )

                if not success:
                    logger.error(
                        f"[Tarea {self.request.id}] Error al obtener insights para campaña {campaign.id}: {message}"
                    )
                    errors.append(
                        f"Error al obtener insights para campaña {campaign.id}: {message}"
                    )
                    continue

                # Procesar insights
                for insight in insights_data:
                    try:
                        # Extraer datos del insight
                        date_str = insight.get("date_start")
                        if not date_str:
                            continue

                        date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        impressions = int(insight.get("impressions", 0))
                        clicks = int(insight.get("clicks", 0))
                        spend = float(insight.get("spend", 0))
                        reach = int(insight.get("reach", 0))
                        ctr = float(insight.get("ctr", 0))
                        cpc = float(insight.get("cpc", 0))
                        cpm = float(insight.get("cpm", 0))

                        # Buscar si ya existe un insight para esta fecha y campaña
                        existing_insight = MetaInsight.query.filter_by(
                            campaign_id=campaign.id, date=date
                        ).first()

                        if existing_insight:
                            # Actualizar insight existente
                            existing_insight.impressions = impressions
                            existing_insight.clicks = clicks
                            existing_insight.spend = spend
                            existing_insight.reach = reach
                            existing_insight.ctr = ctr
                            existing_insight.cpc = cpc
                            existing_insight.cpm = cpm
                            existing_insight.updated_at = datetime.now()
                            insights_updated += 1
                        else:
                            # Crear nuevo insight
                            new_insight = MetaInsight(
                                campaign_id=campaign.id,
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
                            insights_created += 1

                    except Exception as e:
                        logger.error(
                            f"[Tarea {self.request.id}] Error al procesar insight para campaña {campaign.id}, fecha {date_str}: {e}"
                        )
                        errors.append(
                            f"Error al procesar insight para campaña {campaign.id}, fecha {date_str}: {str(e)}"
                        )
                        continue

                # Confirmar cambios para esta campaña
                db.session.commit()
                campaigns_processed += 1
                logger.info(
                    f"[Tarea {self.request.id}] Procesados {len(insights_data)} insights para campaña {campaign.id}"
                )

            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(
                    f"[Tarea {self.request.id}] Error de base de datos al procesar campaña {campaign.id}: {e}"
                )
                errors.append(f"Error de base de datos al procesar campaña {campaign.id}: {str(e)}")
                continue
            except Exception as e:
                db.session.rollback()
                logger.error(
                    f"[Tarea {self.request.id}] Error inesperado al procesar campaña {campaign.id}: {e}"
                )
                errors.append(f"Error inesperado al procesar campaña {campaign.id}: {str(e)}")
                continue

        # 3. Preparar resultados
        results["success"] = True
        results["message"] = (
            f"Sincronización completada. Procesadas {campaigns_processed} campañas, creados {insights_created} insights, actualizados {insights_updated} insights."
        )
        results["campaigns_processed"] = campaigns_processed
        results["insights_created"] = insights_created
        results["insights_updated"] = insights_updated
        results["errors"] = errors

        logger.info(f"[Tarea {self.request.id}] {results['message']}")
        if errors:
            logger.warning(
                f"[Tarea {self.request.id}] Se encontraron {len(errors)} errores durante la sincronización"
            )

        return results

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"[Tarea {self.request.id}] Error inesperado durante la sincronización de insights: {e}",
            exc_info=True,
        )
        results["message"] = f"Error inesperado: {str(e)}"
        return results
