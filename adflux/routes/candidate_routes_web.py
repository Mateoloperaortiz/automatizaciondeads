"""
Rutas web para candidatos en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de candidatos.
"""

from flask import Blueprint, render_template, url_for, flash, request, redirect
from ..models import Segment
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, EmailField
from wtforms.validators import DataRequired, Optional, Email, ValidationError
from flask_wtf.csrf import generate_csrf
from ..constants import SEGMENT_MAP, SEGMENT_COLORS, DEFAULT_SEGMENT_NAME, DEFAULT_SEGMENT_COLOR
from ..services.candidate_service import CandidateService
from sqlalchemy.exc import SQLAlchemyError
from ..api.common.excepciones import (
    AdFluxError,
    ErrorRecursoNoEncontrado,
    ErrorValidacion,
    ErrorBaseDatos,
)
from ..api.common.error_handling import manejar_error_web, notificar_error_web

# Definir el blueprint
candidate_bp = Blueprint("candidate", __name__, template_folder="../templates")


class CandidateForm(FlaskForm):
    """Formulario para crear y editar candidatos."""

    name = StringField("Nombre Completo", validators=[DataRequired()])
    email = EmailField("Correo Electrónico", validators=[Optional(), Email()])
    phone = StringField("Teléfono", validators=[Optional()])
    location = StringField("Ubicación", validators=[Optional()])
    years_experience = IntegerField("Años de Experiencia", validators=[Optional()])
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
    primary_skill = StringField("Habilidad Principal", validators=[Optional()])
    desired_salary = IntegerField("Salario Deseado", validators=[Optional()])
    desired_position = StringField("Cargo Deseado", validators=[Optional()])
    summary = TextAreaField("Resumen Profesional", validators=[Optional()])
    availability = SelectField(
        "Disponibilidad",
        choices=[
            ("", "Seleccionar..."),
            ("immediate", "Inmediata"),
            ("two_weeks", "2 Semanas"),
            ("one_month", "1 Mes"),
            ("negotiable", "Negociable"),
        ],
        validators=[Optional()],
    )
    skills = TextAreaField("Habilidades (separadas por coma)", validators=[Optional()])
    languages = TextAreaField("Idiomas (separados por coma)", validators=[Optional()])

    # Validador personalizado para email (si se proporciona, no debe estar vacío)
    def validate_email(self, field):
        if field.data and not field.data.strip():
            raise ValidationError("El correo electrónico no puede consistir solo en espacios en blanco.")

    # Validador personalizado para años de experiencia
    def validate_years_experience(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError("Los años de experiencia no pueden ser negativos.")


@candidate_bp.route("/")
@manejar_error_web
def list_candidates():
    """Renderiza la página de lista de candidatos."""
    try:
        page = request.args.get("page", 1, type=int)
        if page < 1:
            raise ErrorValidacion(mensaje="El número de página debe ser mayor o igual a 1")

        query = request.args.get("query", "")
        sort_by = request.args.get("sort_by", "name")
        sort_order = request.args.get("sort_order", "asc")

        if sort_order not in ["asc", "desc"]:
            sort_order = "asc"
            notificar_error_web(
                f"Orden de clasificación '{sort_order}' no válido. Usando 'asc'.", "warning"
            )

        segment_filter = request.args.get("segment")  # Obtener filtro de segmento

        try:
            candidates, pagination = CandidateService.get_candidates(
                page=page,
                per_page=10,
                query=query,
                sort_by=sort_by,
                sort_order=sort_order,
                segment_filter=segment_filter,
            )
        except SQLAlchemyError as e:
            raise ErrorBaseDatos(mensaje=f"Error de base de datos al obtener candidatos: {str(e)}")

        # Generar enlaces de ordenación para encabezados de tabla
        sort_links = {}
        for col in ["name", "primary_skill", "years_experience", "segment"]:
            # Invertir orden si ya está ordenado por esta columna
            current_order = "asc" if sort_by != col or sort_order == "desc" else "desc"
            sort_links[col] = url_for(
                "candidate.list_candidates",
                page=page,
                query=query,
                sort_by=col,
                sort_order=current_order,
                segment=segment_filter,
            )

        # Obtener nombres de segmentos para mostrar en lugar de IDs
        segment_names = CandidateService.get_segment_names(candidates)

        # Generar token CSRF para formularios
        csrf_token_value = generate_csrf()

        return render_template(
            "candidates_list.html",
            title="Candidatos",
            candidates=candidates,
            pagination=pagination,
            sort_links=sort_links,
            segment_names=segment_names,
            segment_map=SEGMENT_MAP,
            segment_colors=SEGMENT_COLORS,
            default_segment_name=DEFAULT_SEGMENT_NAME,
            default_segment_color=DEFAULT_SEGMENT_COLOR,
            query=query,
            csrf_token_value=csrf_token_value,
        )
    except Exception as e:
        if not isinstance(e, AdFluxError):
            raise AdFluxError(
                mensaje=f"Error inesperado al listar candidatos: {str(e)}", codigo=500
            )
        raise


@candidate_bp.route("/<string:candidate_id>")
def candidate_details(candidate_id):
    """Renderiza la página de detalles para un candidato específico."""
    # Usar el nuevo método del servicio para obtener candidato y nombre de segmento
    candidate, segment_name = CandidateService.get_candidate_details(candidate_id)

    if not candidate:
        flash(f"Candidato con ID {candidate_id} no encontrado.", "error")
        return redirect(url_for("candidate.list_candidates"))

    return render_template(
        "candidate_detail.html",
        title=f"Candidato: {candidate.name}",
        candidate=candidate,
        segment_name=segment_name,
        segment_map=SEGMENT_MAP,
        segment_colors=SEGMENT_COLORS,
        default_segment_name=DEFAULT_SEGMENT_NAME,
        default_segment_color=DEFAULT_SEGMENT_COLOR,
    )


@candidate_bp.route("/create", methods=["GET", "POST"])
@manejar_error_web
def create_candidate():
    """Renderiza y procesa el formulario para crear un nuevo candidato."""
    form = CandidateForm()

    if form.validate_on_submit():
        # Validaciones de email y años de experiencia ahora en el formulario
        # if form.email.data and not form.email.data.strip(): ...
        # if form.years_experience.data is not None and form.years_experience.data < 0: ...

        # Asumiendo que el servicio espera skills y languages como strings separados por comas
        # (o si no, procesar aquí como en job_routes_web)
        candidate_data = {
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "location": form.location.data,
            "years_experience": form.years_experience.data,
            "education_level": form.education_level.data,
            "primary_skill": form.primary_skill.data,
            "desired_salary": form.desired_salary.data,
            "desired_position": form.desired_position.data,
            "summary": form.summary.data,
            "availability": form.availability.data,
            "skills": form.skills.data,  # Pasar el string directamente
            "languages": form.languages.data,  # Pasar el string directamente
        }

        try:
            candidate, message, status_code = CandidateService.create_candidate(candidate_data)

            if status_code == 201:
                flash(message, "success")
                if candidate and hasattr(candidate, "candidate_id"):
                    return redirect(
                        url_for("candidate.candidate_details", candidate_id=candidate.candidate_id)
                    )
                else:
                    flash("Candidato creado pero no se pudo obtener su ID", "warning")
                    return redirect(url_for("candidate.list_candidates"))
            else:
                # Mostrar error del servicio
                flash(f"Error al crear candidato: {message}", "error")
                # raise AdFluxError(mensaje=message, codigo=status_code)

        except (SQLAlchemyError, ErrorBaseDatos) as e: # Capturar errores de BD
            db_error_msg = f"Error de base de datos al crear candidato: {str(e)}"
            current_app.logger.error(db_error_msg, exc_info=True)
            flash(db_error_msg, "error") # Mostrar error de BD
        except Exception as e:
             if not isinstance(e, AdFluxError):
                 current_app.logger.error(f"Error inesperado al crear candidato: {e}", exc_info=True)
                 flash("Ocurrió un error inesperado al crear el candidato.", "error")

    return render_template(
        "candidate_form.html", title="Crear Candidato", form=form, candidate=None
    )


@candidate_bp.route("/<string:candidate_id>/edit", methods=["GET", "POST"])
@manejar_error_web
def update_candidate(candidate_id):
    """Renderiza y procesa el formulario para editar un candidato existente."""
    candidate = CandidateService.get_candidate_by_id(candidate_id)

    if not candidate:
        raise ErrorRecursoNoEncontrado(
            mensaje=f"Candidato con ID {candidate_id} no encontrado.",
            recurso="Candidato",
            identificador=candidate_id,
        )

    form = CandidateForm(obj=candidate)

    if request.method == "GET":
        # Asumiendo que skills/languages en el modelo son listas y las unimos para el form
        form.skills.data = ", ".join(candidate.skills) if isinstance(candidate.skills, list) else candidate.skills or ""
        form.languages.data = ", ".join(candidate.languages) if isinstance(candidate.languages, list) else candidate.languages or ""

    if form.validate_on_submit():
        # Validaciones ahora en el formulario
        # if form.email.data and not form.email.data.strip(): ...
        # if form.years_experience.data is not None and form.years_experience.data < 0: ...

        # Asumiendo que el servicio espera skills y languages como strings separados por comas
        candidate_data = {
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "location": form.location.data,
            "years_experience": form.years_experience.data,
            "education_level": form.education_level.data,
            "primary_skill": form.primary_skill.data,
            "desired_salary": form.desired_salary.data,
            "desired_position": form.desired_position.data,
            "summary": form.summary.data,
            "availability": form.availability.data,
            "skills": form.skills.data, # Pasar string
            "languages": form.languages.data, # Pasar string
        }

        try:
            updated_candidate, message, status_code = CandidateService.update_candidate(
                candidate_id, candidate_data
            )

            if status_code == 200:
                flash(message, "success")
                if updated_candidate and hasattr(updated_candidate, "candidate_id"):
                    return redirect(
                        url_for(
                            "candidate.candidate_details",
                            candidate_id=updated_candidate.candidate_id,
                        )
                    )
                else:
                    flash("Candidato actualizado pero no se pudo obtener su ID", "warning")
                    return redirect(url_for("candidate.list_candidates"))
            else:
                 # Mostrar error del servicio
                 flash(f"Error al actualizar candidato: {message}", "error")
                # raise AdFluxError(mensaje=message, codigo=status_code)

        except (SQLAlchemyError, ErrorBaseDatos) as e:
            db_error_msg = f"Error de base de datos al actualizar candidato: {str(e)}"
            current_app.logger.error(db_error_msg, exc_info=True)
            flash(db_error_msg, "error")
        except Exception as e:
            if not isinstance(e, AdFluxError):
                 current_app.logger.error(f"Error inesperado al actualizar candidato: {e}", exc_info=True)
                 flash("Ocurrió un error inesperado al actualizar el candidato.", "error")

    return render_template(
        "candidate_form.html", title="Editar Candidato", form=form, candidate=candidate
    )
