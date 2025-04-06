"""
Rutas web para aplicaciones en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de aplicaciones.
"""

from flask import Blueprint, render_template, flash, request
from ..services.application_service import ApplicationService

# Definir el blueprint
application_bp = Blueprint("application", __name__, template_folder="../templates")


@application_bp.route("/")
def list_applications():
    """Renderiza la página de lista de aplicaciones."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        status = request.args.get("status")
        
        applications, pagination = ApplicationService.get_applications(
            page=page,
            per_page=per_page,
            status=status,
            sort_by="application_date",
            sort_order="desc"
        )
        
    except Exception as e:
        flash(f"Error al obtener aplicaciones: {e}", "error")
        applications = []
        pagination = None

    return render_template(
        "applications_list.html", 
        title="Aplicaciones", 
        applications=applications,
        pagination=pagination
    )
