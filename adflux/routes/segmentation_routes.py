"""
Rutas de segmentación para AdFlux.

Este módulo contiene las rutas relacionadas con la segmentación de candidatos.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from sqlalchemy import func
from ..models import db, Candidate, Segment, Campaign
from ..forms import SegmentForm
from ..tasks import run_candidate_segmentation_task
from ..ml import analyze_segments_from_db
from ..extensions import csrf
from flask_wtf.csrf import generate_csrf
from ..constants import SEGMENT_MAP, SEGMENT_COLORS, DEFAULT_SEGMENT_NAME, DEFAULT_SEGMENT_COLOR

# Definir el blueprint
segmentation_bp = Blueprint('segmentation', __name__, template_folder='../templates')


@segmentation_bp.route('/')
def segmentation_analysis():
    """Renderiza la página de análisis de segmentación."""
    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()

    try:
        # Obtener todos los segmentos de la tabla Segment
        all_segments = Segment.query.all()

        # Obtener análisis de segmentos
        analysis_results = analyze_segments_from_db()

        if 'error' in analysis_results:
            flash(f"Error al analizar segmentos: {analysis_results['error']}", 'error')
            chart_data = None
            segment_summary = []
            summary_stats = {}
        else:
            # Preparar datos para gráfico de distribución de segmentos
            chart_labels = []
            chart_data_values = []
            segment_summary = []

            # Inicializar estadísticas resumidas
            total_candidates = analysis_results.get('total_candidates', 0)

            # Contar segmentos activos (los que tienen candidatos asignados)
            segments_data = analysis_results.get('segments', {})
            active_segments = len(segments_data)

            # Contar todos los segmentos disponibles
            total_segments = len(all_segments)

            summary_stats = {
                'total_candidates': total_candidates,
                'segmented_candidates': sum(segment_data.get('size', 0) for segment_data in segments_data.values()),
                'active_segments': active_segments,
                'total_segments': total_segments
            }

            # Procesar cada segmento de la tabla Segment
            for segment_obj in all_segments:
                segment_id = segment_obj.id
                segment_name = segment_obj.name
                segment_description = segment_obj.description or ""

                # Verificar si este segmento tiene datos de análisis
                segment_data = segments_data.get(str(segment_id), {})

                # Añadir datos al gráfico
                chart_labels.append(segment_name)

                # Si hay datos de análisis para este segmento, usar el tamaño; de lo contrario, contar candidatos manualmente
                if segment_data:
                    segment_size = segment_data.get('size', 0)
                else:
                    # Contar candidatos asignados a este segmento
                    segment_size = Candidate.query.filter_by(segment_id=segment_id).count()

                chart_data_values.append(segment_size)

                # Obtener campañas asociadas a este segmento
                associated_campaigns = []
                try:
                    campaigns = Campaign.query.filter(Campaign.target_segment_ids.contains([int(segment_id)])).all()
                    associated_campaigns = [{
                        'id': c.id,
                        'name': c.name,
                        'platform': c.platform,
                        'status': c.status,
                        'url': url_for('campaign.view_campaign_details', campaign_id=c.id)
                    } for c in campaigns]
                except Exception as e:
                    current_app.logger.error(f"Error al obtener campañas para segmento {segment_id}: {e}", exc_info=True)

                # Preparar resumen del segmento
                segment_summary.append({
                    'id': int(segment_id),
                    'name': segment_name,
                    'description': segment_description,
                    'count': segment_size,
                    'view_url': url_for('candidate.list_candidates', segment=segment_id),
                    'edit_url': url_for('segmentation.edit_segment', segment_id=segment_id),
                    'avg_experience': segment_data.get('avg_experience'),
                    'top_skills': segment_data.get('top_primary_skills', []),
                    'top_locations': segment_data.get('locations', []),
                    'education_distribution': segment_data.get('education_levels', []),
                    'associated_campaigns': associated_campaigns,
                    'total_campaign_count': len(associated_campaigns),
                    'charts': {
                        'skills': segment_data.get('primary_skills_chart'),
                        'experience': segment_data.get('experience_chart'),
                        'education': segment_data.get('education_chart')
                    },
                    'is_active': bool(segment_data)  # Marcar si el segmento tiene candidatos asignados
                })

            # Ordenar segmentos: primero los activos, luego por tamaño (descendente)
            segment_summary.sort(key=lambda x: (not x['is_active'], -x['count']))

            # Añadir segmento "Sin segmentar" si hay candidatos sin segmento
            try:
                unsegmented_count = Candidate.query.filter(Candidate.segment_id.is_(None)).count()
                if unsegmented_count > 0:
                    segment_name = "Sin segmentar"
                    chart_labels.append(segment_name)
                    chart_data_values.append(unsegmented_count)
                    summary_stats['total_candidates'] += unsegmented_count
                    segment_summary.append({
                        'id': None,
                        'name': segment_name,
                        'description': 'Candidatos no asignados a ningún segmento.',
                        'count': unsegmented_count,
                        'view_url': url_for('candidate.list_candidates', segment='none'),
                        'avg_experience': None,
                        'top_skills': [],
                        'top_locations': [],
                        'education_distribution': {},
                        'associated_campaigns': [],
                        'total_campaign_count': 0
                    })
            except Exception as e:
                current_app.logger.error(f"Error al contar candidatos sin segmento: {e}", exc_info=True)

            # Ya hemos establecido las estadísticas de resumen anteriormente

            chart_data = {
                'labels': chart_labels,
                'data': chart_data_values
            } if chart_labels else None

    except Exception as e:
        current_app.logger.error(f"Error durante el análisis de segmentos: {e}", exc_info=True)
        flash("Error al generar el análisis de segmentación.", "error")
        chart_data = None
        segment_summary = []
        summary_stats = {}
        csrf_token_value = generate_csrf() # Regenerar en caso de error si es necesario

    return render_template('segmentation.html',
                           title="Análisis de Segmentación de Candidatos",
                           chart_data=chart_data,
                           segment_summary=segment_summary,
                           summary_stats=summary_stats,
                           csrf_token_value=csrf_token_value,
                           segment_map=SEGMENT_MAP,
                           segment_colors=SEGMENT_COLORS,
                           default_segment_name=DEFAULT_SEGMENT_NAME,
                           default_segment_color=DEFAULT_SEGMENT_COLOR)


@segmentation_bp.route('/run', methods=['POST'])
def run_segmentation_task():
    """Dispara la tarea de segmentación ML."""
    try:
        # Usar la tarea Celery en lugar de la función directa
        task = run_candidate_segmentation_task.delay()
        flash(f"Tarea de segmentación iniciada. Los resultados se actualizarán en breve.", 'success')
    except Exception as e:
        current_app.logger.error(f"Error al disparar la tarea de segmentación: {e}", exc_info=True)
        flash("Ocurrió un error inesperado al intentar iniciar la tarea de segmentación.", 'error')

    return redirect(url_for('segmentation.segmentation_analysis'))


@segmentation_bp.route('/segments/<int:segment_id>/edit', methods=['GET', 'POST'])
def edit_segment(segment_id):
    """Edita un segmento existente."""
    segment = Segment.query.get_or_404(segment_id)
    form = SegmentForm(obj=segment)

    if form.validate_on_submit():
        try:
            segment.name = form.name.data
            segment.description = form.description.data
            db.session.commit()
            flash(f"Segmento '{segment.name}' actualizado con éxito.", 'success')
            return redirect(url_for('segmentation.segmentation_analysis'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el segmento: {e}", 'error')
            current_app.logger.error(f"Error al actualizar el segmento {segment_id}: {e}", exc_info=True)

    return render_template('segment_edit.html',
                           title=f"Editar Segmento: {segment.name}",
                           form=form,
                           segment=segment)


@segmentation_bp.route('/segmentation/trigger', methods=['POST'])
def trigger_segmentation():
    """Dispara la tarea en segundo plano para re-ejecutar la segmentación de candidatos."""
    try:
        task = run_candidate_segmentation_task.delay()
        flash(f"Tarea de segmentación de candidatos iniciada (ID de Tarea: {task.id}). Los resultados se actualizarán en breve.", 'info')
    except Exception as e:
        flash(f"Error al iniciar la tarea de segmentación: {e}", 'error')
        current_app.logger.error(f"Error al despachar la tarea de segmentación: {e}", exc_info=True)

    return redirect(url_for('segmentation.segmentation_analysis'))
