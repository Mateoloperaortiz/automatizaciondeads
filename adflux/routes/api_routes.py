"""
Rutas de API para AdFlux.

Este módulo contiene las rutas de API para AdFlux.
"""

from flask import Blueprint, request, jsonify
from adflux.api.gemini.content_generation import get_content_generator
from adflux.services import RecommendationService

# Crear blueprint para rutas de API
api_bp = Blueprint("api", __name__, url_prefix="/api")

recommendation_service = RecommendationService()


@api_bp.route("/generate-ad-creative", methods=["POST"])
def generate_ad_creative():
    """
    Genera contenido creativo para anuncios de trabajo utilizando la API de Gemini.

    Espera un JSON con:
    - job_title: Título del trabajo
    - job_description: Descripción del trabajo
    - target_audience: (Opcional) Audiencia objetivo

    Retorna un JSON con:
    - success: True/False
    - message: Mensaje de éxito o error
    - content: Contenido generado (si success=True)
    """
    try:
        # Obtener datos del request
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No se proporcionaron datos JSON"}), 400

        # Validar campos requeridos
        job_title = data.get("job_title")
        job_description = data.get("job_description")
        target_audience = data.get("target_audience", "general job seekers")

        if not job_title:
            return jsonify({"success": False, "message": "El título del trabajo es requerido"}), 400

        if not job_description:
            return (
                jsonify({"success": False, "message": "La descripción del trabajo es requerida"}),
                400,
            )

        # Obtener generador de contenido
        content_generator = get_content_generator()

        # Generar contenido creativo
        success, message, content = content_generator.generate_ad_creative(
            job_title=job_title, job_description=job_description, target_audience=target_audience
        )

        # Adaptar el formato de respuesta para el frontend
        adapted_content = {
            "primary_text": content.get("primary_description", "")
            + "\n\n"
            + content.get("secondary_description", ""),
            "headline": content.get("primary_headline", ""),
            "link_description": content.get("call_to_action", ""),
        }

        # Retornar respuesta
        return jsonify({"success": success, "message": message, "content": adapted_content})

    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Error al generar contenido creativo: {str(e)}"}
            ),
            500,
        )


@api_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    """
    Endpoint para obtener recomendaciones de campañas publicitarias.
    
    Espera un JSON con:
    - job_id: ID de la oferta de trabajo
    
    Retorna un JSON con:
    - success: True/False
    - message: Mensaje de éxito o error
    - recommendations: Datos de recomendación (si success=True)
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        # Validar datos
        if not data or "job_id" not in data:
            return jsonify({"success": False, "message": "job_id es requerido"}), 400
        
        # Obtener recomendaciones
        success, message, recommendations = recommendation_service.get_job_recommendations(data["job_id"])
        
        # Devolver respuesta
        return jsonify({
            "success": success,
            "message": message,
            "recommendations": recommendations
        })
        
    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Error al generar recomendaciones: {str(e)}"}
            ),
            500,
        )
