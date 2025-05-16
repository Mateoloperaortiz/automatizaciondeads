"""
Rutas para la generación de creatividades para anuncios.

Este módulo define las rutas para la generación de contenido creativo
para anuncios en diferentes plataformas utilizando la API de Google Gemini.
"""

import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_wtf.csrf import generate_csrf
from ..services.creative_service import CreativeService
from ..services.job_service import JobService
from ..services.segmentation_service import SegmentationService

logger = logging.getLogger(__name__)

creative_bp = Blueprint("creative", __name__, url_prefix="/creative")

creative_service = CreativeService()
job_service = JobService()
segmentation_service = SegmentationService()


@creative_bp.route("/", methods=["GET", "POST"])
def creative_dashboard():
    """Muestra el dashboard de generación de creatividades."""
    try:
        selected_platform = ''
        selected_formats = []
        
        if request.method == "POST" and 'select_platform' in request.form:
            selected_platform = request.form.get('platform', '')
            logger.info(f"POST: Plataforma seleccionada: '{selected_platform}'")
        else:
            selected_platform = request.args.get('platform', '')
            logger.info(f"GET: Plataforma seleccionada desde URL: '{selected_platform}'")
        
        jobs = job_service.get_active_jobs()
        
        analysis_data = segmentation_service.get_segmentation_analysis_data()
        segments = analysis_data.get("segment_summary", [])
        
        platforms = creative_service.get_supported_platforms()
        
        platform_formats = {}
        for platform in platforms:
            platform_formats[platform['id']] = platform.get('formats', [])
        
        if selected_platform:
            selected_formats = platform_formats.get(selected_platform, [])
            logger.info(f"Formatos para plataforma '{selected_platform}': {selected_formats}")
        
        csrf_token_value = generate_csrf()
        
        return render_template(
            "creative/dashboard.html",
            title="Generación de Creatividades",
            jobs=jobs,
            segments=segments,
            platforms=platforms,
            platform_formats=platform_formats,
            selected_platform=selected_platform,
            selected_formats=selected_formats,
            csrf_token_value=csrf_token_value,
        )
    except Exception as e:
        logger.exception(f"Error al cargar el dashboard de creatividades: {e}")
        flash(f"Error al cargar el dashboard de creatividades: {str(e)}", "error")
        return redirect(url_for("dashboard.index"))


@creative_bp.route("/generate", methods=["POST"])
def generate_creative():
    """Genera contenido creativo para un anuncio."""
    try:
        job_id = request.form.get("job_id")
        platform = request.form.get("platform")
        segment_id = request.form.get("segment_id")
        format_type = request.form.get("format_type")
        
        if not job_id or not platform:
            flash("Se requiere seleccionar una oferta de trabajo y una plataforma", "error")
            return redirect(url_for("creative.creative_dashboard"))
        
        segment_id = int(segment_id) if segment_id else None
        
        success, message, content = creative_service.generate_ad_creative(
            job_id=job_id,
            platform=platform,
            segment_id=segment_id,
            format_type=format_type,
        )
        
        if not success:
            flash(message, "error")
            return redirect(url_for("creative.creative_dashboard"))
        
        from flask import session
        session["creative_content"] = content
        session["creative_platform"] = platform
        session["creative_job_id"] = job_id
        session["creative_segment_id"] = segment_id
        session["creative_format_type"] = format_type
        
        return redirect(url_for("creative.show_creative"))
    except Exception as e:
        logger.exception(f"Error al generar creatividad: {e}")
        flash(f"Error al generar creatividad: {str(e)}", "error")
        return redirect(url_for("creative.creative_dashboard"))


@creative_bp.route("/show", methods=["GET"])
def show_creative():
    """Muestra el resultado de la generación de creatividad."""
    try:
        from flask import session
        content = session.get("creative_content")
        platform = session.get("creative_platform")
        job_id = session.get("creative_job_id")
        segment_id = session.get("creative_segment_id")
        
        if not content or not platform or not job_id:
            flash("No hay creatividad generada para mostrar", "error")
            return redirect(url_for("creative.creative_dashboard"))
        
        job = job_service.get_job_by_id(job_id)
        
        segment = None
        if segment_id:
            segment = segmentation_service.get_segment_by_id(segment_id)
        
        platforms = creative_service.get_supported_platforms()
        platform_info = next((p for p in platforms if p["id"] == platform), None)
        
        csrf_token_value = generate_csrf()
        
        return render_template(
            "creative/result.html",
            title="Resultado de Creatividad",
            content=content,
            platform=platform,
            platform_info=platform_info,
            job=job,
            segment=segment,
            csrf_token_value=csrf_token_value,
        )
    except Exception as e:
        logger.exception(f"Error al mostrar creatividad: {e}")
        flash(f"Error al mostrar creatividad: {str(e)}", "error")
        return redirect(url_for("creative.creative_dashboard"))


@creative_bp.route("/variations", methods=["POST"])
def generate_variations():
    """Genera variaciones de un anuncio base."""
    try:
        from flask import session
        base_content = session.get("creative_content")
        platform = session.get("creative_platform")
        num_variations = int(request.form.get("num_variations", 3))
        
        if not base_content or not platform:
            flash("No hay creatividad base para generar variaciones", "error")
            return redirect(url_for("creative.creative_dashboard"))
        
        success, message, variations = creative_service.generate_ad_variations(
            base_content=base_content,
            platform=platform,
            num_variations=num_variations,
        )
        
        if not success:
            flash(message, "error")
            return redirect(url_for("creative.show_creative"))
        
        session["creative_variations"] = variations
        
        return redirect(url_for("creative.show_variations"))
    except Exception as e:
        logger.exception(f"Error al generar variaciones: {e}")
        flash(f"Error al generar variaciones: {str(e)}", "error")
        return redirect(url_for("creative.show_creative"))


@creative_bp.route("/variations/show", methods=["GET"])
def show_variations():
    """Muestra las variaciones generadas."""
    try:
        from flask import session
        variations = session.get("creative_variations")
        base_content = session.get("creative_content")
        platform = session.get("creative_platform")
        job_id = session.get("creative_job_id")
        
        if not variations or not base_content or not platform or not job_id:
            flash("No hay variaciones para mostrar", "error")
            return redirect(url_for("creative.creative_dashboard"))
        
        job = job_service.get_job_by_id(job_id)
        
        platforms = creative_service.get_supported_platforms()
        platform_info = next((p for p in platforms if p["id"] == platform), None)
        
        csrf_token_value = generate_csrf()
        
        return render_template(
            "creative/variations.html",
            title="Variaciones de Creatividad",
            variations=variations,
            base_content=base_content,
            platform=platform,
            platform_info=platform_info,
            job=job,
            csrf_token_value=csrf_token_value,
        )
    except Exception as e:
        logger.exception(f"Error al mostrar variaciones: {e}")
        flash(f"Error al mostrar variaciones: {str(e)}", "error")
        return redirect(url_for("creative.creative_dashboard"))


@creative_bp.route("/api/platforms", methods=["GET"])
def api_get_platforms():
    """API para obtener las plataformas soportadas."""
    try:
        platforms = creative_service.get_supported_platforms()
        return jsonify({"success": True, "platforms": platforms})
    except Exception as e:
        logger.exception(f"Error al obtener plataformas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@creative_bp.route("/api/formats/<platform>", methods=["GET"])
def api_get_formats(platform):
    """API para obtener los formatos disponibles para una plataforma."""
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept', '').find('application/json') != -1:
            platforms = creative_service.get_supported_platforms()
            platform_info = next((p for p in platforms if p["id"] == platform), None)
            
            if not platform_info:
                return jsonify({"success": False, "error": f"Plataforma '{platform}' no soportada"}), 404
            
            formats = platform_info.get("formats", [])
            
            response = jsonify({"success": True, "formats": formats})
            response.headers['Content-Type'] = 'application/json'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            return jsonify({"success": False, "error": "Se requiere una solicitud AJAX"}), 400
    except Exception as e:
        logger.exception(f"Error al obtener formatos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
