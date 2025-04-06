"""
Rutas web para aplicaciones en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de aplicaciones.
"""

from flask import Blueprint, render_template, flash, request
from sqlalchemy.exc import SQLAlchemyError
from ..services.application_service import ApplicationService
from ..api.common.excepciones import AdFluxError, ErrorRecursoNoEncontrado, ErrorValidacion, ErrorBaseDatos
from ..api.common.error_handling import manejar_error_web, notificar_error_web

# Definir el blueprint
application_bp = Blueprint("application", __name__, template_folder="../templates")


@application_bp.route("/")
@manejar_error_web
def list_applications():
    """Renderiza la página de lista de aplicaciones."""
    try:
        page = request.args.get("page", 1, type=int)
        if page < 1:
            raise ErrorValidacion(mensaje="El número de página debe ser mayor o igual a 1")
            
        per_page = request.args.get("per_page", 10, type=int)
        if per_page < 1 or per_page > 100:
            raise ErrorValidacion(mensaje="El número de elementos por página debe estar entre 1 y 100")
            
        status = request.args.get("status")
        
        valid_statuses = ["pending", "approved", "rejected", "withdrawn"]
        if status and status not in valid_statuses:
            notificar_error_web(
                f"Estado '{status}' no válido. Estados válidos: {', '.join(valid_statuses)}. Mostrando todas las aplicaciones.", 
                "warning"
            )
            status = None
        
        try:
            applications, pagination = ApplicationService.get_applications(
                page=page,
                per_page=per_page,
                status=status,
                sort_by="application_date",
                sort_order="desc"
            )
        except SQLAlchemyError as e:
            raise ErrorBaseDatos(
                mensaje=f"Error de base de datos al obtener aplicaciones: {str(e)}"
            )
    except Exception as e:
        if not isinstance(e, AdFluxError):
            raise AdFluxError(
                mensaje=f"Error inesperado al listar aplicaciones: {str(e)}",
                codigo=500
            )
        raise

    return render_template(
        "applications_list.html", 
        title="Aplicaciones", 
        applications=applications,
        pagination=pagination
    )
