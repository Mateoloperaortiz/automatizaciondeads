"""
Rutas web para aplicaciones en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de aplicaciones.
"""

from flask import Blueprint, render_template, request, flash
from sqlalchemy.exc import SQLAlchemyError
from ..services.application_service import ApplicationService
from ..api.common.excepciones import AdFluxError, ErrorValidacion, ErrorBaseDatos
from ..api.common.error_handling import manejar_error_web, notificar_error_web

# Definir el blueprint
application_bp = Blueprint("application", __name__, template_folder="../templates")

# Estados válidos para filtro (podría venir de constantes)
VALID_APP_STATUSES = ["pending", "approved", "rejected", "withdrawn"]

@application_bp.route("/")
@manejar_error_web
def list_applications():
    """Renderiza la página de lista de aplicaciones."""
    applications = []
    pagination = None
    status_filter = None # Inicializar

    try:
        # Obtener y validar parámetros de paginación y filtro
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        status_filter = request.args.get("status")

        if page < 1:
            page = 1
            notificar_error_web("Número de página inválido. Mostrando página 1.", "warning")
            # O lanzar ErrorValidacion si se prefiere detener
            # raise ErrorValidacion(mensaje="El número de página debe ser mayor o igual a 1")
        if per_page < 1 or per_page > 100:
            per_page = 10
            notificar_error_web("Elementos por página inválido (1-100). Usando 10.", "warning")
            # raise ErrorValidacion(mensaje="El número de elementos por página debe estar entre 1 y 100")
        if status_filter and status_filter not in VALID_APP_STATUSES:
            notificar_error_web(
                f"Estado '{status_filter}' no válido. Mostrando todas las aplicaciones.",
                "warning",
            )
            status_filter = None # Ignorar filtro inválido

        # Llamar al servicio para obtener las aplicaciones
        applications, pagination = ApplicationService.get_applications(
            page=page,
            per_page=per_page,
            status=status_filter,
            sort_by="application_date", # O el campo que corresponda
            sort_order="desc",
        )

    except SQLAlchemyError as e:
         # Error específico de BD al llamar al servicio
         # El decorador @manejar_error_web debería capturar esto si lanza ErrorBaseDatos
         raise ErrorBaseDatos(mensaje=f"Error de base de datos al obtener aplicaciones: {str(e)}")
    except AdFluxError as e:
         # Capturar otros errores conocidos de AdFlux lanzados desde el servicio o validación
         # El decorador ya debería manejar esto
         raise e
    except Exception as e:
         # Capturar cualquier otro error inesperado
         # El decorador debería capturar esto y convertirlo en AdFluxError(codigo=500)
         raise AdFluxError(mensaje=f"Error inesperado al listar aplicaciones: {str(e)}", codigo=500)

    return render_template(
        "applications_list.html",
        title="Aplicaciones",
        applications=applications,
        pagination=pagination,
        current_status=status_filter # Pasar el filtro actual a la plantilla
    )
