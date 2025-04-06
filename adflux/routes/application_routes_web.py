"""
Rutas web para aplicaciones en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de aplicaciones.
"""

from flask import Blueprint, render_template, flash
from ..models import Application, JobOpening, Candidate

# Definir el blueprint
application_bp = Blueprint("application", __name__, template_folder="../templates")


@application_bp.route("/")
def list_applications():
    """Renderiza la página de lista de aplicaciones."""
    try:
        # Obtener aplicaciones de la BD, ordenar por fecha de aplicación más reciente
        applications = Application.query.order_by(Application.application_date.desc()).all()

        # Obtener información adicional para cada aplicación
        for app in applications:
            if app.job_id:
                app.job = JobOpening.query.filter_by(job_id=app.job_id).first()
            if app.candidate_id:
                app.candidate = Candidate.query.filter_by(candidate_id=app.candidate_id).first()
    except Exception as e:
        flash(f"Error al obtener aplicaciones: {e}", "error")
        applications = []  # Asegurar que applications sea siempre una lista

    return render_template(
        "applications_list.html", title="Aplicaciones", applications=applications
    )
