"""
Configuración CORS para AdFlux.

Este módulo proporciona funciones para configurar CORS (Cross-Origin Resource Sharing)
de manera segura, permitiendo o restringiendo solicitudes de diferentes orígenes.
"""

import logging
import re
from typing import List, Optional, Union, Dict, Any

from flask import Flask, request, Response
from flask_cors import CORS


# Configurar logger
logger = logging.getLogger(__name__)


def setup_cors(app: Flask, allowed_origins: Optional[List[str]] = None) -> None:
    """
    Configura CORS en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
        allowed_origins: Lista de orígenes permitidos (opcional)
    """
    # Usar orígenes por defecto si no se proporcionan
    if allowed_origins is None:
        # En producción, especificar orígenes exactos
        if app.config.get('ENV') == 'production':
            allowed_origins = [
                'https://adflux.example.com',
                'https://api.adflux.example.com'
            ]
        else:
            # En desarrollo, permitir localhost
            allowed_origins = [
                'http://localhost:5000',
                'http://localhost:8080',
                'http://127.0.0.1:5000',
                'http://127.0.0.1:8080'
            ]
    
    # Configurar CORS
    cors_config = {
        'origins': allowed_origins,
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': [
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'X-API-Key',
            'X-CSRF-Token'
        ],
        'expose_headers': [
            'Content-Type',
            'Content-Length',
            'X-Pagination-Total',
            'X-Pagination-Pages',
            'X-Pagination-Page',
            'X-Pagination-Limit'
        ],
        'supports_credentials': True,
        'max_age': 600  # 10 minutos
    }
    
    # Aplicar configuración CORS
    CORS(app, **cors_config)
    
    logger.info(f"CORS configurado con orígenes permitidos: {allowed_origins}")


def validate_origin(origin: str, allowed_origins: List[str]) -> bool:
    """
    Valida si un origen está permitido.
    
    Args:
        origin: Origen a validar
        allowed_origins: Lista de orígenes permitidos
        
    Returns:
        True si el origen está permitido, False en caso contrario
    """
    if not origin:
        return False
    
    # Verificar si el origen está en la lista de permitidos
    if origin in allowed_origins:
        return True
    
    # Verificar patrones con comodines
    for allowed_origin in allowed_origins:
        if '*' in allowed_origin:
            # Convertir patrón a expresión regular
            pattern = allowed_origin.replace('.', '\\.').replace('*', '.*')
            if re.match(f'^{pattern}$', origin):
                return True
    
    return False


def get_cors_headers(origin: Optional[str] = None, allowed_origins: Optional[List[str]] = None,
                    allowed_methods: Optional[List[str]] = None, allowed_headers: Optional[List[str]] = None,
                    expose_headers: Optional[List[str]] = None, max_age: int = 600,
                    allow_credentials: bool = True) -> Dict[str, str]:
    """
    Genera cabeceras CORS para una respuesta.
    
    Args:
        origin: Origen de la solicitud (opcional)
        allowed_origins: Lista de orígenes permitidos (opcional)
        allowed_methods: Lista de métodos permitidos (opcional)
        allowed_headers: Lista de cabeceras permitidas (opcional)
        expose_headers: Lista de cabeceras expuestas (opcional)
        max_age: Tiempo máximo de caché para preflight (en segundos)
        allow_credentials: Si se permiten credenciales
        
    Returns:
        Diccionario con cabeceras CORS
    """
    headers = {}
    
    # Usar valores por defecto si no se proporcionan
    if allowed_origins is None:
        allowed_origins = ['*']
    
    if allowed_methods is None:
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    if allowed_headers is None:
        allowed_headers = ['Content-Type', 'Authorization', 'X-Requested-With']
    
    if expose_headers is None:
        expose_headers = ['Content-Type', 'Content-Length']
    
    # Verificar origen
    if origin:
        if '*' in allowed_origins or validate_origin(origin, allowed_origins):
            headers['Access-Control-Allow-Origin'] = origin
        else:
            # Si el origen no está permitido, no añadir cabeceras CORS
            return {}
    else:
        # Si no hay origen, usar el primer origen permitido
        headers['Access-Control-Allow-Origin'] = allowed_origins[0] if allowed_origins else '*'
    
    # Añadir cabeceras CORS
    headers['Access-Control-Allow-Methods'] = ', '.join(allowed_methods)
    headers['Access-Control-Allow-Headers'] = ', '.join(allowed_headers)
    headers['Access-Control-Expose-Headers'] = ', '.join(expose_headers)
    headers['Access-Control-Max-Age'] = str(max_age)
    
    if allow_credentials:
        headers['Access-Control-Allow-Credentials'] = 'true'
    
    return headers


def add_cors_headers(response: Response, origin: Optional[str] = None,
                    allowed_origins: Optional[List[str]] = None) -> Response:
    """
    Añade cabeceras CORS a una respuesta.
    
    Args:
        response: Respuesta HTTP
        origin: Origen de la solicitud (opcional)
        allowed_origins: Lista de orígenes permitidos (opcional)
        
    Returns:
        Respuesta HTTP con cabeceras CORS
    """
    # Obtener origen de la solicitud si no se proporciona
    if origin is None and request:
        origin = request.headers.get('Origin')
    
    # Generar cabeceras CORS
    cors_headers = get_cors_headers(origin, allowed_origins)
    
    # Añadir cabeceras a la respuesta
    for key, value in cors_headers.items():
        response.headers[key] = value
    
    return response
