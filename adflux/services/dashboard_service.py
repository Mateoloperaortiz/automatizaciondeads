"""
Servicio para la lógica de negocio relacionada con el Dashboard.
"""

from flask import current_app
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from ..models import db, JobOpening, Candidate, Campaign, MetaInsight
from ..constants import CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLORS, SEGMENT_MAP, DEFAULT_SEGMENT_NAME

class DashboardService:
    """Contiene la lógica de negocio para obtener datos del dashboard."""

    def get_dashboard_data(self, start_date, end_date):
        """Recopila y procesa todos los datos necesarios para el dashboard."""

        stats = {
            # Placeholders for all stats
            "total_jobs": 0,
            "total_campaigns": 0,
            "total_candidates": 0,
            "status_counts": {},
            "status_chart_data": {"labels": [], "data": []},
            "job_status_chart_data": {"labels": [], "data": []},
            "segment_chart_data": {"labels": [], "data": []},
            "total_spend": 0.0,
            "total_impressions": 0,
            "total_clicks": 0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
            "spend_over_time_chart": {"labels": [], "data": []},
            "top_campaigns": [],
            "errors": [] # To collect non-critical errors
        }

        # --- Estadísticas Generales (Sin filtro de fecha) ---
        try:
            stats["total_jobs"] = db.session.query(func.count(JobOpening.job_id)).scalar() or 0
            stats["total_campaigns"] = db.session.query(func.count(Campaign.id)).scalar() or 0
            stats["total_candidates"] = db.session.query(func.count(Candidate.candidate_id)).scalar() or 0
        except SQLAlchemyError as e:
            error_msg = f"Error al obtener estadísticas generales: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            stats["errors"].append(error_msg)

        # --- Estado y Gráfico de Campañas (Sin filtro de fecha) ---
        try:
            campaigns_by_status_query = (
                db.session.query(Campaign.status, func.count(Campaign.id))
                .group_by(Campaign.status)
                .all()
            )
            standardized_status_counts = {}
            for status, count in campaigns_by_status_query:
                if status is not None:
                    standardized_status = CAMPAIGN_STATUS.get(status.upper(), status.title())
                    standardized_status_counts[standardized_status] = standardized_status_counts.get(standardized_status, 0) + count

            stats["status_counts"] = standardized_status_counts
            if standardized_status_counts:
                stats["status_chart_data"] = {
                    "labels": list(standardized_status_counts.keys()),
                    "data": list(standardized_status_counts.values())
                }
        except SQLAlchemyError as e:
            error_msg = f"Error al obtener estadísticas de estado de campañas: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            stats["errors"].append(error_msg)

        # --- Gráfico de Estado de Puestos (Sin filtro de fecha) ---
        try:
            job_status_counts = (
                db.session.query(JobOpening.status, func.count(JobOpening.job_id))
                .group_by(JobOpening.status)
                .all()
            )
            valid_job_statuses = {str(status).title(): count for status, count in job_status_counts if status is not None}
            if valid_job_statuses:
                stats["job_status_chart_data"] = {
                    "labels": list(valid_job_statuses.keys()),
                    "data": list(valid_job_statuses.values())
                    }
        except SQLAlchemyError as e:
            error_msg = f"Error al obtener estadísticas de estado de trabajos: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            stats["errors"].append(error_msg)

        # --- Gráfico de Segmentos de Candidatos (Sin filtro de fecha) ---
        try:
            segment_counts = (
                db.session.query(Candidate.segment_id, func.count(Candidate.candidate_id))
                .group_by(Candidate.segment_id)
                .order_by(Candidate.segment_id)
                .all()
            )
            seg_labels = []
            seg_data = []
            for s_id, count in segment_counts:
                 seg_labels.append(SEGMENT_MAP.get(s_id, DEFAULT_SEGMENT_NAME) if s_id is not None else "Sin segmentar")
                 seg_data.append(count)

            if seg_labels:
                 stats["segment_chart_data"] = {"labels": seg_labels, "data": seg_data}

        except SQLAlchemyError as e:
            error_msg = f"Error al obtener estadísticas de segmentos de candidatos: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            stats["errors"].append(error_msg)

        # --- Métricas de Rendimiento (Rango de Fechas) ---
        try:
            insights_base_query = MetaInsight.query.filter(
                MetaInsight.date_start >= start_date, MetaInsight.date_stop <= end_date
            )

            performance_totals = insights_base_query.with_entities(
                func.sum(MetaInsight.spend),
                func.sum(MetaInsight.impressions),
                func.sum(MetaInsight.clicks),
            ).first()

            total_spend = float(performance_totals[0] or 0.0)
            total_impressions = int(performance_totals[1] or 0)
            total_clicks = int(performance_totals[2] or 0)

            stats["total_spend"] = total_spend
            stats["total_impressions"] = total_impressions
            stats["total_clicks"] = total_clicks
            stats["ctr"] = (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0
            stats["cpc"] = total_spend / total_clicks if total_clicks > 0 else 0.0
            stats["cpm"] = (total_spend / total_impressions) * 1000.0 if total_impressions > 0 else 0.0

            # Gasto a lo largo del tiempo
            spend_over_time = (
                insights_base_query.with_entities(
                    MetaInsight.date_start, func.sum(MetaInsight.spend)
                )
                .group_by(MetaInsight.date_start)
                .order_by(MetaInsight.date_start)
                .all()
            )
            valid_spend_data = [(date.strftime("%Y-%m-%d"), float(spend or 0.0)) for date, spend in spend_over_time]
            if valid_spend_data:
                stats["spend_over_time_chart"] = {
                    "labels": [item[0] for item in valid_spend_data],
                    "data": [item[1] for item in valid_spend_data]
                }

            # Campañas de mayor rendimiento (por clics)
            top_campaigns_query = (
                db.session.query(
                    Campaign.id.label("campaign_id"),
                    Campaign.name.label("campaign_name"),
                    func.sum(MetaInsight.spend).label("total_spend"),
                    func.sum(MetaInsight.impressions).label("total_impressions"),
                    func.sum(MetaInsight.clicks).label("total_clicks"),
                )
                .select_from(MetaInsight)
                .join(Campaign, Campaign.external_campaign_id == MetaInsight.meta_campaign_id)
                .filter(
                    MetaInsight.date_start >= start_date,
                    MetaInsight.date_stop <= end_date
                )
                .group_by(Campaign.id, Campaign.name)
                .having(func.sum(MetaInsight.clicks) > 0) # Solo campañas con clics
                .order_by(func.sum(MetaInsight.clicks).desc())
                .limit(5)
            )

            top_campaign_results = top_campaigns_query.all()
            top_campaign_data = []
            for row in top_campaign_results:
                spend = float(row.total_spend or 0.0)
                impressions = int(row.total_impressions or 0)
                clicks = int(row.total_clicks or 0)
                ctr = (clicks / impressions) * 100.0 if impressions > 0 else 0.0
                top_campaign_data.append({
                           "id": row.campaign_id,
                           "name": row.campaign_name,
                           "spend": round(spend, 2),
                           "impressions": impressions,
                           "clicks": clicks,
                           "ctr": round(ctr, 2),
                        })
            stats["top_campaigns"] = top_campaign_data

        except SQLAlchemyError as e:
             error_msg = f"Error al obtener métricas de rendimiento: {str(e)}"
             current_app.logger.error(error_msg, exc_info=True)
             stats["errors"].append(error_msg)
             # Reset performance stats to default if DB error occurs
             stats["total_spend"] = 0.0
             stats["total_impressions"] = 0
             stats["total_clicks"] = 0
             stats["ctr"] = 0.0
             stats["cpc"] = 0.0
             stats["cpm"] = 0.0
             stats["spend_over_time_chart"] = {"labels": [], "data": []}
             stats["top_campaigns"] = []
        except Exception as e:
             # Catch other potential errors during processing
             error_msg = f"Error inesperado al procesar métricas de rendimiento: {str(e)}"
             current_app.logger.error(error_msg, exc_info=True)
             stats["errors"].append(error_msg)

        return stats 