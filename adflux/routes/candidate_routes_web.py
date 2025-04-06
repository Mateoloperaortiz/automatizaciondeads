"""
Rutas web para candidatos en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de candidatos.
"""

from flask import Blueprint, render_template, url_for, flash, request, redirect
from ..models import Segment
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, EmailField
from wtforms.validators import DataRequired, Optional, Email
from flask_wtf.csrf import generate_csrf
from ..constants import SEGMENT_MAP, SEGMENT_COLORS, DEFAULT_SEGMENT_NAME, DEFAULT_SEGMENT_COLOR
from ..services.candidate_service import CandidateService

# Definir el blueprint
candidate_bp = Blueprint("candidate", __name__, template_folder="../templates")


class CandidateForm(FlaskForm):
    """Formulario para crear y editar candidatos."""
    name = StringField('Nombre Completo', validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[Optional(), Email()])
    phone = StringField('Teléfono', validators=[Optional()])
    location = StringField('Ubicación', validators=[Optional()])
    years_experience = IntegerField('Años de Experiencia', validators=[Optional()])
    education_level = SelectField('Nivel de Educación', choices=[
        ('', 'Seleccionar...'),
        ('high-school', 'Bachillerato'),
        ('associate', 'Técnico/Tecnólogo'),
        ('bachelor', 'Pregrado'),
        ('master', 'Maestría'),
        ('doctorate', 'Doctorado')
    ], validators=[Optional()])
    primary_skill = StringField('Habilidad Principal', validators=[Optional()])
    desired_salary = IntegerField('Salario Deseado', validators=[Optional()])
    desired_position = StringField('Cargo Deseado', validators=[Optional()])
    summary = TextAreaField('Resumen Profesional', validators=[Optional()])
    availability = SelectField('Disponibilidad', choices=[
        ('', 'Seleccionar...'),
        ('immediate', 'Inmediata'),
        ('two_weeks', '2 Semanas'),
        ('one_month', '1 Mes'),
        ('negotiable', 'Negociable')
    ], validators=[Optional()])
    skills = TextAreaField('Habilidades', validators=[Optional()])
    languages = TextAreaField('Idiomas', validators=[Optional()])


@candidate_bp.route("/")
def list_candidates():
    """Renderiza la página de lista de candidatos."""
    page = request.args.get("page", 1, type=int)
    query = request.args.get("query", "")
    sort_by = request.args.get("sort_by", "name")
    sort_order = request.args.get("sort_order", "asc")
    segment_filter = request.args.get("segment")  # Obtener filtro de segmento

    candidates, pagination = CandidateService.get_candidates(
        page=page,
        per_page=10,
        query=query,
        sort_by=sort_by,
        sort_order=sort_order,
        segment_filter=segment_filter
    )

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


@candidate_bp.route("/<string:candidate_id>")
def candidate_details(candidate_id):
    """Renderiza la página de detalles para un candidato específico."""
    candidate = CandidateService.get_candidate_by_id(candidate_id)
    
    if not candidate:
        flash(f"Candidato con ID {candidate_id} no encontrado.", "error")
        return redirect(url_for('candidate.list_candidates'))

    # Obtener nombre del segmento si existe
    segment_name = None
    if candidate.segment_id:
        segment = Segment.query.get(candidate.segment_id)
        if segment:
            segment_name = segment.name

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
def create_candidate():
    """Renderiza y procesa el formulario para crear un nuevo candidato."""
    form = CandidateForm()
    
    if form.validate_on_submit():
        try:
            candidate_data = {
                'name': form.name.data,
                'email': form.email.data,
                'phone': form.phone.data,
                'location': form.location.data,
                'years_experience': form.years_experience.data,
                'education_level': form.education_level.data,
                'primary_skill': form.primary_skill.data,
                'desired_salary': form.desired_salary.data,
                'desired_position': form.desired_position.data,
                'summary': form.summary.data,
                'availability': form.availability.data,
                'skills': form.skills.data,  # El servicio procesará esto como string
                'languages': form.languages.data  # El servicio procesará esto como string
            }
            
            candidate, message, status_code = CandidateService.create_candidate(candidate_data)
            
            if status_code == 201:
                flash(message, "success")
                return redirect(url_for('candidate.candidate_details', candidate_id=candidate.candidate_id))
            else:
                flash(message, "error")
            
        except Exception as e:
            flash(f"Error al crear candidato: {e}", "error")
    
    return render_template("candidate_form.html", title="Crear Candidato", form=form, candidate=None)


@candidate_bp.route("/<string:candidate_id>/edit", methods=["GET", "POST"])
def update_candidate(candidate_id):
    """Renderiza y procesa el formulario para editar un candidato existente."""
    candidate = CandidateService.get_candidate_by_id(candidate_id)
    
    if not candidate:
        flash(f"Candidato con ID {candidate_id} no encontrado.", "error")
        return redirect(url_for('candidate.list_candidates'))
        
    form = CandidateForm(obj=candidate)
    
    if request.method == "GET":
        form.skills.data = ', '.join(candidate.skills) if candidate.skills else ''
        form.languages.data = ', '.join(candidate.languages) if candidate.languages else ''
    
    if form.validate_on_submit():
        try:
            candidate_data = {
                'name': form.name.data,
                'email': form.email.data,
                'phone': form.phone.data,
                'location': form.location.data,
                'years_experience': form.years_experience.data,
                'education_level': form.education_level.data,
                'primary_skill': form.primary_skill.data,
                'desired_salary': form.desired_salary.data,
                'desired_position': form.desired_position.data,
                'summary': form.summary.data,
                'availability': form.availability.data,
                'skills': form.skills.data,  # El servicio procesará esto como string
                'languages': form.languages.data  # El servicio procesará esto como string
            }
            
            updated_candidate, message, status_code = CandidateService.update_candidate(candidate_id, candidate_data)
            
            if status_code == 200:
                flash(message, "success")
                return redirect(url_for('candidate.candidate_details', candidate_id=updated_candidate.candidate_id))
            else:
                flash(message, "error")
            
        except Exception as e:
            flash(f"Error al actualizar candidato: {e}", "error")
    
    return render_template("candidate_form.html", title="Editar Candidato", form=form, candidate=candidate)
