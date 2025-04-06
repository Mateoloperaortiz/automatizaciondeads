"""
Rutas web para candidatos en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de candidatos.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from sqlalchemy import or_, func
from ..models import db, Candidate, Segment
from ..extensions import csrf
from flask_wtf.csrf import generate_csrf
from ..constants import SEGMENT_MAP, SEGMENT_COLORS, DEFAULT_SEGMENT_NAME, DEFAULT_SEGMENT_COLOR

# Definir el blueprint
candidate_bp = Blueprint('candidate', __name__, template_folder='../templates')


@candidate_bp.route('/')
def list_candidates():
    """Renderiza la página de lista de candidatos."""
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    segment_filter = request.args.get('segment') # Obtener filtro de segmento

    # Consulta base
    candidate_query = Candidate.query

    # Filtrado por segmento
    if segment_filter is not None:
        if segment_filter.lower() == 'none': # Manejar valor especial 'none' para no segmentados
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
    sort_column = getattr(Candidate, sort_by if sort_by != 'segment' else 'segment_id', Candidate.name)
    if sort_order == 'desc':
        sort_column = sort_column.desc()

    # Paginación
    per_page = 10
    pagination = candidate_query.order_by(sort_column).paginate(page=page, per_page=per_page, error_out=False)
    candidates = pagination.items

    # Generar enlaces de ordenación para encabezados de tabla
    sort_links = {}
    for col in ['name', 'primary_skill', 'years_experience', 'segment']:
        # Invertir orden si ya está ordenado por esta columna
        current_order = 'asc' if sort_by != col or sort_order == 'desc' else 'desc'
        sort_links[col] = url_for('candidate.list_candidates', page=page, query=query, sort_by=col, sort_order=current_order, segment=segment_filter)

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

    return render_template('candidates_list.html',
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
                           csrf_token_value=csrf_token_value)


@candidate_bp.route('/<string:candidate_id>')
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

    return render_template('candidate_detail.html',
                           title=f"Candidato: {candidate.name}",
                           candidate=candidate,
                           segment_name=segment_name,
                           segment_map=SEGMENT_MAP,
                           segment_colors=SEGMENT_COLORS,
                           default_segment_name=DEFAULT_SEGMENT_NAME,
                           default_segment_color=DEFAULT_SEGMENT_COLOR)
