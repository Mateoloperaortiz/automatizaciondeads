"""
Rutas del panel de control para AdFlux.

Este módulo contiene las rutas relacionadas con el panel de control principal de AdFlux.
"""

from flask import Blueprint, render_template, redirect, request, current_app
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models import db, JobOpening, Candidate, Campaign, MetaInsight
from flask_wtf.csrf import generate_csrf
from ..constants import CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLORS, SEGMENT_MAP, DEFAULT_SEGMENT_NAME

# Definir el blueprint
dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")


@dashboard_bp.route("/")
def index():
    """Renderiza la página principal del panel de control."""
    # --- Manejo del Rango de Fechas ---
    default_end_date_dt = datetime.utcnow().date()
    default_start_date_dt = default_end_date_dt - timedelta(days=30)
    start_date_str = request.args.get("start_date", default_start_date_dt.isoformat())
    end_date_str = request.args.get("end_date", default_end_date_dt.isoformat())
    try:
        start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        start_date_dt = default_start_date_dt
        start_date_str = start_date_dt.isoformat()
    try:
        end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        end_date_dt = default_end_date_dt
        end_date_str = end_date_dt.isoformat()
    if start_date_dt > end_date_dt:
        start_date_dt = default_start_date_dt
        end_date_dt = default_end_date_dt
        start_date_str = start_date_dt.isoformat()
        end_date_str = end_date_dt.isoformat()
    # --------------------------

    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()

    # Inicializar diccionario de estadísticas
    stats = {}

    try:
        # --- Estadísticas Generales (Sin filtro de fecha) ---
        stats["total_jobs"] = db.session.query(func.count(JobOpening.job_id)).scalar() or 0
        stats["total_campaigns"] = db.session.query(func.count(Campaign.id)).scalar() or 0
        stats["total_candidates"] = (
            db.session.query(func.count(Candidate.candidate_id)).scalar() or 0
        )

        # --- Estado y Gráfico de Campañas (Sin filtro de fecha) ---
        campaigns_by_status_query = (
            db.session.query(Campaign.status, func.count(Campaign.id))
            .group_by(Campaign.status)
            .all()
        )

        # Estandarizar los estados de las campañas
        standardized_status_counts = {}
        for status, count in campaigns_by_status_query:
            if status is not None:
                # Convertir el estado a mayúsculas para buscar en el diccionario
                standardized_status = CAMPAIGN_STATUS.get(status.upper(), status.title())
                if standardized_status in standardized_status_counts:
                    standardized_status_counts[standardized_status] += count
                else:
                    standardized_status_counts[standardized_status] = count

        stats["status_counts"] = standardized_status_counts

        if standardized_status_counts:
            status_labels = list(standardized_status_counts.keys())
            status_data = list(standardized_status_counts.values())
            stats["status_chart_data"] = {"labels": status_labels, "data": status_data}

        # --- Gráfico de Estado de Puestos (Sin filtro de fecha) ---
        job_status_counts = (
            db.session.query(JobOpening.status, func.count(JobOpening.job_id))
            .group_by(JobOpening.status)
            .all()
        )
        if job_status_counts:
            job_labels = [
                str(status).title() for status, count in job_status_counts if status is not None
            ]
            job_data = [count for status, count in job_status_counts if status is not None]
            stats["job_status_chart_data"] = {"labels": job_labels, "data": job_data}

        # --- Gráfico de Segmentos de Candidatos (Sin filtro de fecha) ---
        segment_counts = (
            db.session.query(Candidate.segment_id, func.count(Candidate.candidate_id))
            .group_by(Candidate.segment_id)
            .order_by(Candidate.segment_id)
            .all()
        )
        if segment_counts:
            # Usar el mapa de segmentos estandarizado para las etiquetas
            seg_labels = [
                SEGMENT_MAP.get(s, DEFAULT_SEGMENT_NAME) if s is not None else "Sin segmentar"
                for s, count in segment_counts
            ]
            seg_data = [count for s, count in segment_counts]
            stats["segment_chart_data"] = {"labels": seg_labels, "data": seg_data}

        # --- Consulta Base para Insights en Rango de Fechas ---
        insights_base_query = MetaInsight.query.filter(
            MetaInsight.date_start >= start_date_dt, MetaInsight.date_stop <= end_date_dt
        )

        # --- Totales de Métricas de Rendimiento ---
        performance_totals = insights_base_query.with_entities(
            func.sum(MetaInsight.spend),
            func.sum(MetaInsight.impressions),
            func.sum(MetaInsight.clicks),
        ).first()

        total_spend = 0.0
        total_impressions = 0
        total_clicks = 0
        if performance_totals:
            total_spend = float(performance_totals[0]) if performance_totals[0] is not None else 0.0
            total_impressions = (
                int(performance_totals[1]) if performance_totals[1] is not None else 0
            )
            total_clicks = int(performance_totals[2]) if performance_totals[2] is not None else 0

        stats["total_spend"] = total_spend
        stats["total_impressions"] = total_impressions
        stats["total_clicks"] = total_clicks

        # --- Calcular Métricas Derivadas ---
        stats["ctr"] = (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0
        stats["cpc"] = total_spend / total_clicks if total_clicks > 0 else 0.0
        stats["cpm"] = (total_spend / total_impressions) * 1000.0 if total_impressions > 0 else 0.0

        # --- Gráfico de Gasto a lo Largo del Tiempo ---
        spend_over_time = (
            insights_base_query.with_entities(MetaInsight.date_start, func.sum(MetaInsight.spend))
            .group_by(MetaInsight.date_start)
            .order_by(MetaInsight.date_start)
            .all()
        )

        if spend_over_time:
            spend_dates = [date.strftime("%Y-%m-%d") for date, _ in spend_over_time]
            spend_values = [float(spend) for _, spend in spend_over_time]
            stats["spend_over_time_chart"] = {"labels": spend_dates, "data": spend_values}

        # --- Campañas de Mayor Rendimiento ---
        top_campaigns = (
            insights_base_query.with_entities(
                MetaInsight.meta_campaign_id,
                func.sum(MetaInsight.spend).label("total_spend"),
                func.sum(MetaInsight.impressions).label("total_impressions"),
                func.sum(MetaInsight.clicks).label("total_clicks"),
            )
            .group_by(MetaInsight.meta_campaign_id)
            .order_by(func.sum(MetaInsight.clicks).desc())
            .limit(5)
            .all()
        )

        stats["top_campaigns"] = []
        for campaign_id, spend, impressions, clicks in top_campaigns:
            campaign = Campaign.query.filter_by(external_campaign_id=campaign_id).first()
            if campaign:
                ctr = (clicks / impressions) * 100.0 if impressions > 0 else 0.0
                stats["top_campaigns"].append(
                    {
                        "id": campaign.id,
                        "name": campaign.name,
                        "spend": spend,
                        "impressions": impressions,
                        "clicks": clicks,
                        "ctr": ctr,
                    }
                )

    except Exception as e:
        current_app.logger.error(f"Error al generar estadísticas del panel: {e}", exc_info=True)
        stats = {
            "total_jobs": 0,
            "total_campaigns": 0,
            "total_candidates": 0,
            "total_spend": 0.0,
            "total_impressions": 0,
            "total_clicks": 0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
        }

    return render_template(
        "dashboard.html",
        title="Panel de Control",
        stats=stats,
        start_date=start_date_str,
        end_date=end_date_str,
        csrf_token_value=csrf_token_value,
        campaign_status=CAMPAIGN_STATUS,
        campaign_status_colors=CAMPAIGN_STATUS_COLORS,
    )


@dashboard_bp.route("/api-docs")
def api_docs():
    """Redirige a la documentación de la API"""
    return redirect("/api/docs")
