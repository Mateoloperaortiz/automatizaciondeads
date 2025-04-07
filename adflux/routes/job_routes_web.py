"""
Rutas web para trabajos en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de trabajos.
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, Optional
from sqlalchemy.exc import SQLAlchemyError

from ..models import JobOpening
from ..services.job_service import JobService
from ..api.common.excepciones import (
    AdFluxError,
    ErrorRecursoNoEncontrado,
    ErrorValidacion,
    ErrorBaseDatos,
)
from ..api.common.error_handling import manejar_error_web, notificar_error_web

# Definir el blueprint
job_bp = Blueprint("job", __name__, template_folder="../templates")


class JobForm(FlaskForm):
    """Formulario para crear y editar trabajos."""

    title = StringField("Título", validators=[DataRequired()])
    short_description = StringField("Descripción Corta", validators=[Optional()])
    description = TextAreaField("Descripción Completa", validators=[Optional()])
    company_name = StringField("Empresa", validators=[Optional()])
    location = StringField("Ubicación", validators=[Optional()])
    department = StringField("Departamento", validators=[Optional()])
    salary_min = IntegerField("Salario Mínimo", validators=[Optional()])
    salary_max = IntegerField("Salario Máximo", validators=[Optional()])
    employment_type = SelectField(
        "Tipo de Empleo",
        choices=[
            ("", "Seleccionar..."),
            ("full-time", "Tiempo Completo"),
            ("part-time", "Medio Tiempo"),
            ("contract", "Contrato"),
            ("temporary", "Temporal"),
            ("internship", "Pasantía"),
        ],
        validators=[Optional()],
    )
    experience_level = SelectField(
        "Nivel de Experiencia",
        choices=[
            ("", "Seleccionar..."),
            ("entry-level", "Nivel de Entrada"),
            ("mid-level", "Nivel Medio"),
            ("senior", "Senior"),
            ("executive", "Ejecutivo"),
        ],
        validators=[Optional()],
    )
    education_level = SelectField(
        "Nivel de Educación",
        choices=[
            ("", "Seleccionar..."),
            ("high-school", "Bachillerato"),
            ("associate", "Técnico/Tecnólogo"),
            ("bachelor", "Pregrado"),
            ("master", "Maestría"),
            ("doctorate", "Doctorado"),
        ],
        validators=[Optional()],
    )
    posted_date = DateField("Fecha de Publicación", format="%Y-%m-%d", validators=[Optional()])
    closing_date = DateField("Fecha de Cierre", format="%Y-%m-%d", validators=[Optional()])
    status = SelectField(
        "Estado",
        choices=[("open", "Abierto"), ("closed", "Cerrado"), ("draft", "Borrador")],
        default="open",
    )
    remote = BooleanField("Trabajo Remoto", default=False)
    required_skills = TextAreaField("Habilidades Requeridas", validators=[Optional()])
    benefits = TextAreaField("Beneficios", validators=[Optional()])


@job_bp.route("/")
@manejar_error_web
def list_jobs():
    """Renderiza la página de lista de empleos."""
    try:
        page = request.args.get("page", 1, type=int)
        if page < 1:
            raise ErrorValidacion(mensaje="El número de página debe ser mayor o igual a 1")

        per_page = request.args.get("per_page", 10, type=int)
        if per_page < 1 or per_page > 100:
            raise ErrorValidacion(
                mensaje="El número de elementos por página debe estar entre 1 y 100"
            )

        query = request.args.get("query", "")
        status = request.args.get("status")

        if status and status not in ["open", "closed", "draft"]:
            notificar_error_web(
                f"Estado '{status}' no válido. Mostrando todos los estados.", "warning"
            )
            status = None

        try:
            jobs, pagination = JobService.get_jobs(
                page=page,
                per_page=per_page,
                query=query,
                status=status,
                sort_by="posted_date",
                sort_order="desc",
            )
        except SQLAlchemyError as e:
            raise ErrorBaseDatos(mensaje=f"Error de base de datos al obtener trabajos: {str(e)}")
    except Exception as e:
        if not isinstance(e, AdFluxError):
            raise AdFluxError(mensaje=f"Error inesperado al listar trabajos: {str(e)}", codigo=500)
        raise

    return render_template(
        "jobs_list.html", title="Ofertas de Empleo", jobs=jobs, pagination=pagination, query=query
    )


@job_bp.route("/<string:job_id>")
def job_details(job_id):
    """Renderiza la página de detalles para una oferta de empleo específica."""
    job = JobService.get_job_by_id(job_id)
    if not job:
        flash(f"Trabajo con ID {job_id} no encontrado.", "error")
        return redirect(url_for("job.list_jobs"))
    return render_template("job_detail.html", title=f"Empleo: {job.title}", job=job)


@job_bp.route("/create", methods=["GET", "POST"])
@manejar_error_web
def create_job():
    """Renderiza y procesa el formulario para crear un nuevo trabajo."""
    form = JobForm()

    if form.validate_on_submit():
        if form.salary_min.data is not None and form.salary_max.data is not None:
            if form.salary_min.data > form.salary_max.data:
                raise ErrorValidacion(
                    mensaje="El salario mínimo no puede ser mayor que el salario máximo"
                )

        if form.posted_date.data and form.closing_date.data:
            if form.posted_date.data > form.closing_date.data:
                raise ErrorValidacion(
                    mensaje="La fecha de publicación no puede ser posterior a la fecha de cierre"
                )

        job_data = {
            "title": form.title.data,
            "short_description": form.short_description.data,
            "description": form.description.data,
            "company_name": form.company_name.data,
            "location": form.location.data,
            "department": form.department.data,
            "salary_min": form.salary_min.data,
            "salary_max": form.salary_max.data,
            "employment_type": form.employment_type.data,
            "experience_level": form.experience_level.data,
            "education_level": form.education_level.data,
            "posted_date": form.posted_date.data,
            "closing_date": form.closing_date.data,
            "status": form.status.data,
            "remote": form.remote.data,
            "required_skills": form.required_skills.data,  # El servicio procesará esto
            "benefits": form.benefits.data,  # El servicio procesará esto
        }

        try:
            job, message, status_code = JobService.create_job(job_data)

            if status_code == 201:
                flash(message, "success")
                if job and hasattr(job, "job_id"):
                    return redirect(url_for("job.job_details", job_id=job.job_id))
                else:
                    flash("Trabajo creado pero no se pudo obtener su ID", "warning")
                    return redirect(url_for("job.list_jobs"))
            else:
                raise AdFluxError(mensaje=message, codigo=status_code)

        except SQLAlchemyError as e:
            raise ErrorBaseDatos(mensaje=f"Error de base de datos al crear trabajo: {str(e)}")

    return render_template("job_form.html", title="Crear Trabajo", form=form, job=None)


@job_bp.route("/<string:job_id>/edit", methods=["GET", "POST"])
@manejar_error_web
def update_job(job_id):
    """Renderiza y procesa el formulario para editar un trabajo existente."""
    job = JobService.get_job_by_id(job_id)

    if not job:
        raise ErrorRecursoNoEncontrado(
            mensaje=f"Trabajo con ID {job_id} no encontrado.",
            recurso="Trabajo",
            identificador=job_id,
        )

    form = JobForm(obj=job)

    if request.method == "GET":
        form.required_skills.data = ", ".join(job.required_skills) if job.required_skills else ""
        form.benefits.data = ", ".join(job.benefits) if job.benefits else ""

    if form.validate_on_submit():
        if form.salary_min.data is not None and form.salary_max.data is not None:
            if form.salary_min.data > form.salary_max.data:
                raise ErrorValidacion(
                    mensaje="El salario mínimo no puede ser mayor que el salario máximo"
                )

        if form.posted_date.data and form.closing_date.data:
            if form.posted_date.data > form.closing_date.data:
                raise ErrorValidacion(
                    mensaje="La fecha de publicación no puede ser posterior a la fecha de cierre"
                )

        job_data = {
            "title": form.title.data,
            "short_description": form.short_description.data,
            "description": form.description.data,
            "company_name": form.company_name.data,
            "location": form.location.data,
            "department": form.department.data,
            "salary_min": form.salary_min.data,
            "salary_max": form.salary_max.data,
            "employment_type": form.employment_type.data,
            "experience_level": form.experience_level.data,
            "education_level": form.education_level.data,
            "posted_date": form.posted_date.data,
            "closing_date": form.closing_date.data,
            "status": form.status.data,
            "remote": form.remote.data,
            "required_skills": form.required_skills.data,  # El servicio procesará esto
            "benefits": form.benefits.data,  # El servicio procesará esto
        }

        try:
            updated_job, message, status_code = JobService.update_job(job_id, job_data)

            if status_code == 200:
                flash(message, "success")
                if updated_job and hasattr(updated_job, "job_id"):
                    return redirect(url_for("job.job_details", job_id=updated_job.job_id))
                else:
                    flash("Trabajo actualizado pero no se pudo obtener su ID", "warning")
                    return redirect(url_for("job.list_jobs"))
            else:
                raise AdFluxError(mensaje=message, codigo=status_code)

        except SQLAlchemyError as e:
            raise ErrorBaseDatos(mensaje=f"Error de base de datos al actualizar trabajo: {str(e)}")

    return render_template("job_form.html", title="Editar Trabajo", form=form, job=job)
