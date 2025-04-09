"""
Rutas del panel de control para AdFlux (Refactorizado para usar DashboardService).

Este módulo contiene las rutas relacionadas con el panel de control principal de AdFlux.
"""

from flask import Blueprint, render_template, redirect, request, current_app, flash
from datetime import datetime, timedelta
from flask_wtf.csrf import generate_csrf
from ..constants import CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLORS
from ..services.dashboard_service import DashboardService

# Instanciar el servicio
dashboard_service = DashboardService()

# Definir el blueprint
dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")

# Helper para parsear y validar fechas (similar al de report_routes)
def _parse_date_range(start_date_str, end_date_str):
    today = datetime.utcnow().date()
    default_end_date = today
    default_start_date = default_end_date - timedelta(days=30)

    if not end_date_str:
        end_date = default_end_date
    else:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Formato de fecha de fin inválido, usando predeterminado.", "warning")
            end_date = default_end_date

    if not start_date_str:
        start_date = default_start_date
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Formato de fecha de inicio inválido, usando predeterminado.", "warning")
            start_date = default_start_date

    if start_date > end_date:
        flash(
            "La fecha de inicio no puede ser posterior a la fecha de fin, usando rango predeterminado.",
            "warning",
        )
        start_date = default_start_date
        end_date = default_end_date

    return start_date, end_date

@dashboard_bp.route("/")
def index():
    """Renderiza la página principal del panel de control usando DashboardService."""
    try:
        # --- Manejo del Rango de Fechas ---
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        start_date, end_date = _parse_date_range(start_date_str, end_date_str)
        # --------------------------

        csrf_token_value = generate_csrf()

        # Obtener datos del servicio
        stats = dashboard_service.get_dashboard_data(start_date, end_date)

        # Mostrar errores no críticos recopilados por el servicio
        if stats.get("errors"):
            for error_msg in stats["errors"]:
                flash(f"Advertencia al cargar datos: {error_msg}", "warning")

    except Exception as e:
        # Error inesperado grave al procesar la solicitud o llamar al servicio
        current_app.logger.error(f"Error grave en dashboard: {e}", exc_info=True)
        flash("Ocurrió un error inesperado al cargar el panel de control.", "error")
        # Devolver datos vacíos o una plantilla de error
        stats = {}

    return render_template(
        "dashboard.html",
        title="Panel de Control",
        stats=stats,
        start_date=start_date.isoformat() if 'start_date' in locals() else (datetime.utcnow().date() - timedelta(days=30)).isoformat(),
        end_date=end_date.isoformat() if 'end_date' in locals() else datetime.utcnow().date().isoformat(),
        csrf_token_value=csrf_token_value,
        campaign_status=CAMPAIGN_STATUS,
        campaign_status_colors=CAMPAIGN_STATUS_COLORS,
    )


@dashboard_bp.route("/api-docs")
def api_docs():
    """Redirige a la documentación de la API"""
    return redirect("/api/docs/")
