"""
API Gateway para AdFlux.

Este módulo implementa un API Gateway que actúa como punto de entrada
único para todas las solicitudes a los servicios de AdFlux.
"""

from flask import Flask
from flask_cors import CORS

from .config import GatewayConfig
from .routes import register_routes
from .middleware import register_middleware
from .auth import register_auth_handlers
from .logging import configure_logging


def create_gateway_app(config=None):
    """
    Crea y configura la aplicación Flask para el API Gateway.
    
    Args:
        config: Configuración personalizada (opcional)
        
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(GatewayConfig)
    if config:
        app.config.update(config)
    
    # Configurar CORS
    CORS(app)
    
    # Configurar logging
    configure_logging(app)
    
    # Registrar middleware
    register_middleware(app)
    
    # Registrar manejadores de autenticación
    register_auth_handlers(app)
    
    # Registrar rutas
    register_routes(app)
    
    return app
