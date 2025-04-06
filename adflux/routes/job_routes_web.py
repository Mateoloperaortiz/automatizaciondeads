"""
Rutas web para trabajos en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de trabajos.
"""

from flask import Blueprint, render_template, flash
from ..models import JobOpening

# Definir el blueprint
job_bp = Blueprint("job", __name__, template_folder="../templates")


@job_bp.route("/")
def list_jobs():
    """Renderiza la página de lista de empleos."""
    try:
        # Obtener empleos de la BD, ordenar por fecha de publicación más reciente
        jobs = JobOpening.query.order_by(JobOpening.posted_date.desc()).all()
    except Exception as e:
        flash(f"Error al obtener empleos: {e}", "error")
        jobs = []  # Asegurar que jobs sea siempre una lista
    return render_template("jobs_list.html", title="Ofertas de Empleo", jobs=jobs)


@job_bp.route("/<string:job_id>")
def job_details(job_id):
    """Renderiza la página de detalles para una oferta de empleo específica."""
    job = JobOpening.query.filter_by(job_id=job_id).first_or_404()
    return render_template("job_detail.html", title=f"Empleo: {job.title}", job=job)
