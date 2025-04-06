"""
Paquete de configuración de Swagger UI para AdFlux.

Este paquete contiene la configuración de Swagger UI para la API de AdFlux,
organizada en módulos específicos según su funcionalidad.
"""

from flask import Blueprint, jsonify

# Importar configuración de Swagger
from .config import SWAGGER_SPEC
from .ui import swagger_ui_html

# Crear un blueprint para Swagger UI
swagger_bp = Blueprint('swagger', __name__, url_prefix='/api')

# Ruta para redirigir a la UI de Swagger
@swagger_bp.route('/')
def api_root():
    """Redirigir a la UI de Swagger"""
    return {
        "name": "AdFlux API",
        "version": "1.0",
        "description": "API for managing job openings and candidates",
        "documentation": "/api/docs"
    }

# Ruta para servir la especificación de Swagger
@swagger_bp.route('/swagger.json')
def swagger_json():
    """Servir la especificación de Swagger como JSON"""
    return jsonify(SWAGGER_SPEC)

# Ruta para servir la UI de Swagger
@swagger_bp.route('/docs')
def swagger_ui():
    """Servir la UI de Swagger"""
    return swagger_ui_html

# Para mantener compatibilidad con el código existente
__all__ = ['swagger_bp']
