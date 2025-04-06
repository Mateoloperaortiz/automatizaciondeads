"""
Rutas web para candidatos en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de candidatos.
"""

from flask import Blueprint, render_template, url_for, flash, request, redirect
from sqlalchemy import or_
from ..models import Candidate, Segment, db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, EmailField
from wtforms.validators import DataRequired, Optional, Email
from flask_wtf.csrf import generate_csrf
from ..constants import SEGMENT_MAP, SEGMENT_COLORS, DEFAULT_SEGMENT_NAME, DEFAULT_SEGMENT_COLOR
import uuid

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

    # Consulta base
    candidate_query = Candidate.query

    # Filtrado por segmento
    if segment_filter is not None:
        if segment_filter.lower() == "none":  # Manejar valor especial 'none' para no segmentados
            # Usar segment_id
            candidate_query = candidate_query.filter(Candidate.segment_id.is_(None))
        else:
            try:
                segment_id = int(segment_filter)
                # Usar segment_id
                candidate_query = candidate_query.filter(Candidate.segment_id == segment_id)
            except ValueError:
                flash(f"Valor de filtro de segmento inválido: {segment_filter}", "warning")
                # Opcionalmente ignorar filtro o redirigir

    # Funcionalidad de búsqueda (ejemplo simple en nombre y habilidad principal)
    if query:
        search_term = f"%{query}%"
        candidate_query = candidate_query.filter(
            or_(Candidate.name.ilike(search_term), Candidate.primary_skill.ilike(search_term))
        )

    # Lógica de ordenación
    # Usar segment_id para clave de ordenación
    sort_column = getattr(
        Candidate, sort_by if sort_by != "segment" else "segment_id", Candidate.name
    )
    if sort_order == "desc":
        sort_column = sort_column.desc()

    # Paginación
    per_page = 10
    pagination = candidate_query.order_by(sort_column).paginate(
        page=page, per_page=per_page, error_out=False
    )
    candidates = pagination.items

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
    segment_names = {}
    if candidates:
        # Recopilar todos los segment_ids únicos
        segment_ids = set(c.segment_id for c in candidates if c.segment_id is not None)
        if segment_ids:
            segments = Segment.query.filter(Segment.id.in_(segment_ids)).all()
            segment_names = {s.id: s.name for s in segments}

    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()

    # Usar el mapa de segmentos de las constantes globales

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
    candidate = Candidate.query.filter_by(candidate_id=candidate_id).first_or_404()

    # Obtener nombre del segmento si existe
    segment_name = None
    if candidate.segment_id:
        segment = Segment.query.get(candidate.segment_id)
        if segment:
            segment_name = segment.name

    # Usar el mapa de segmentos de las constantes globales

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
            candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
            
            skills = [skill.strip() for skill in form.skills.data.split(',')] if form.skills.data else []
            languages = [language.strip() for language in form.languages.data.split(',')] if form.languages.data else []
            
            new_candidate = Candidate(
                candidate_id=candidate_id,
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                location=form.location.data,
                years_experience=form.years_experience.data,
                education_level=form.education_level.data,
                primary_skill=form.primary_skill.data,
                desired_salary=form.desired_salary.data,
                desired_position=form.desired_position.data,
                summary=form.summary.data,
                availability=form.availability.data,
                skills=skills,
                languages=languages
            )
            
            db.session.add(new_candidate)
            db.session.commit()
            
            flash(f"Candidato '{new_candidate.name}' creado exitosamente.", "success")
            return redirect(url_for('candidate.candidate_details', candidate_id=new_candidate.candidate_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear candidato: {e}", "error")
    
    return render_template("candidate_form.html", title="Crear Candidato", form=form, candidate=None)


@candidate_bp.route("/<string:candidate_id>/edit", methods=["GET", "POST"])
def update_candidate(candidate_id):
    """Renderiza y procesa el formulario para editar un candidato existente."""
    candidate = Candidate.query.filter_by(candidate_id=candidate_id).first_or_404()
    form = CandidateForm(obj=candidate)
    
    if request.method == "GET":
        form.skills.data = ', '.join(candidate.skills) if candidate.skills else ''
        form.languages.data = ', '.join(candidate.languages) if candidate.languages else ''
    
    if form.validate_on_submit():
        try:
            candidate.name = form.name.data
            candidate.email = form.email.data
            candidate.phone = form.phone.data
            candidate.location = form.location.data
            candidate.years_experience = form.years_experience.data
            candidate.education_level = form.education_level.data
            candidate.primary_skill = form.primary_skill.data
            candidate.desired_salary = form.desired_salary.data
            candidate.desired_position = form.desired_position.data
            candidate.summary = form.summary.data
            candidate.availability = form.availability.data
            
            candidate.skills = [skill.strip() for skill in form.skills.data.split(',')] if form.skills.data else []
            candidate.languages = [language.strip() for language in form.languages.data.split(',')] if form.languages.data else []
            
            db.session.commit()
            
            flash(f"Candidato '{candidate.name}' actualizado exitosamente.", "success")
            return redirect(url_for('candidate.candidate_details', candidate_id=candidate.candidate_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar candidato: {e}", "error")
    
    return render_template("candidate_form.html", title="Editar Candidato", form=form, candidate=candidate)
