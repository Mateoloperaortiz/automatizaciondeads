"""
Rutas de segmentación para AdFlux (Refactorizado para usar SegmentationService).

Este módulo contiene las rutas relacionadas con la segmentación de candidatos.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from ..forms import SegmentForm
from flask_wtf.csrf import generate_csrf
from ..constants import SEGMENT_MAP, SEGMENT_COLORS, DEFAULT_SEGMENT_NAME, DEFAULT_SEGMENT_COLOR

# Importar servicio
from ..services.segmentation_service import SegmentationService

# Instanciar servicio
segmentation_service = SegmentationService()

# Definir el blueprint
segmentation_bp = Blueprint("segmentation", __name__, template_folder="../templates")


@segmentation_bp.route("/")
def segmentation_analysis():
    """Renderiza la página de análisis de segmentación usando SegmentationService."""
    csrf_token_value = generate_csrf()
    analysis_data = segmentation_service.get_segmentation_analysis_data()

    if analysis_data.get("error"):
        flash(analysis_data["error"], "error")
        # Pasar datos vacíos/predeterminados a la plantilla en caso de error grave
        analysis_data = {
            "chart_data": None,
            "segment_summary": [],
            "summary_stats": {},
        }

    return render_template(
        "segmentation.html",
        title="Análisis de Segmentación de Candidatos",
        chart_data=analysis_data.get("chart_data"),
        segment_summary=analysis_data.get("segment_summary", []),
        summary_stats=analysis_data.get("summary_stats", {}),
        csrf_token_value=csrf_token_value,
        # Pasar constantes si la plantilla las necesita directamente
        segment_map=SEGMENT_MAP,
        segment_colors=SEGMENT_COLORS,
        default_segment_name=DEFAULT_SEGMENT_NAME,
        default_segment_color=DEFAULT_SEGMENT_COLOR,
    )


# Ruta consolidada para disparar la tarea
@segmentation_bp.route("/trigger", methods=["POST"])
def trigger_segmentation_task():
    """Dispara la tarea de segmentación ML usando SegmentationService."""
    from flask import request
    strategy = request.form.get('strategy', 'kmeans')
    success, message = segmentation_service.trigger_segmentation_with_strategy(strategy)
    flash(message, "success" if success else "error")
    return redirect(url_for("segmentation.segmentation_analysis"))


@segmentation_bp.route("/segments/<int:segment_id>/edit", methods=["GET", "POST"])
def edit_segment(segment_id):
    """Edita un segmento existente usando SegmentationService."""
    try:
        # Obtener segmento via servicio (maneja 404)
        segment = segmentation_service.get_segment_by_id(segment_id)
    except Exception as e:
        # Capturar 404 u otros errores al obtener el segmento
        flash(f"Error al cargar segmento: {e}", "error")
        current_app.logger.error(f"Error al obtener segmento {segment_id} para editar: {e}", exc_info=True)
        return redirect(url_for("segmentation.segmentation_analysis"))

    form = SegmentForm(obj=segment)

    if form.validate_on_submit():
        # Llamar al servicio para actualizar
        data = {"name": form.name.data, "description": form.description.data}
        success, message = segmentation_service.update_segment(segment_id, data)
        flash(message, "success" if success else "error")
        if success:
            return redirect(url_for("segmentation.segmentation_analysis"))
        # Si falla, se renderiza de nuevo el formulario con el error flash

    return render_template(
        "segment_edit.html", title=f"Editar Segmento: {segment.name}", form=form, segment=segment
    )


# Eliminar rutas duplicadas o lógica movida
# @segmentation_bp.route("/run", methods=["POST"])
# def run_segmentation_task(): ...
# @segmentation_bp.route("/segmentation/trigger", methods=["POST"])
# def trigger_segmentation(): ...
# Eliminar imports no usados (db, Candidate, Campaign, Segment, run_candidate_segmentation_task, analyze_segments_from_db)
