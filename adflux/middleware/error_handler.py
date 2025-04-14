"""
Middleware para manejo de errores en AdFlux.

Este módulo proporciona un middleware para manejar errores de manera centralizada.
"""

import traceback
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

from flask import Flask, request, jsonify, Response, current_app
from werkzeug.exceptions import HTTPException

from ..exceptions import (
    AdFluxError, APIError, DatabaseError, ValidationError,
    BusinessError, AuthenticationError, AuthorizationError
)


# Configurar logger
logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """
    Registra manejadores de errores en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
    """
    # Manejar excepciones HTTP de Werkzeug
    app.register_error_handler(HTTPException, handle_http_exception)
    
    # Manejar excepciones personalizadas de AdFlux
    app.register_error_handler(AdFluxError, handle_adflux_error)
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(DatabaseError, handle_database_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(BusinessError, handle_business_error)
    app.register_error_handler(AuthenticationError, handle_authentication_error)
    app.register_error_handler(AuthorizationError, handle_authorization_error)
    
    # Manejar excepciones no manejadas
    app.register_error_handler(Exception, handle_unhandled_exception)


def handle_http_exception(e: HTTPException) -> Response:
    """
    Maneja excepciones HTTP de Werkzeug.
    
    Args:
        e: Excepción HTTP
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.warning(f"Error HTTP {e.code}: {e.description}")
    
    response = {
        "error": e.name,
        "message": e.description
    }
    
    return jsonify(response), e.code


def handle_adflux_error(e: AdFluxError) -> Response:
    """
    Maneja excepciones personalizadas de AdFlux.
    
    Args:
        e: Excepción de AdFlux
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.error(f"Error de AdFlux: {str(e)}")
    
    if e.cause:
        logger.error(f"Causa: {str(e.cause)}")
    
    return jsonify(e.to_dict()), e.status_code


def handle_api_error(e: APIError) -> Response:
    """
    Maneja excepciones de API.
    
    Args:
        e: Excepción de API
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.error(f"Error de API: {str(e)}")
    
    if e.api_name:
        logger.error(f"API: {e.api_name}")
    
    if e.request_id:
        logger.error(f"Request ID: {e.request_id}")
    
    if e.response:
        logger.error(f"Respuesta: {e.response}")
    
    return jsonify(e.to_dict()), e.status_code


def handle_database_error(e: DatabaseError) -> Response:
    """
    Maneja excepciones de base de datos.
    
    Args:
        e: Excepción de base de datos
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.error(f"Error de base de datos: {str(e)}")
    
    # En producción, no exponer detalles de errores de base de datos
    if current_app.config.get("ENV") == "production":
        response = {
            "error": "DatabaseError",
            "message": "Se produjo un error en la base de datos"
        }
    else:
        response = e.to_dict()
    
    return jsonify(response), e.status_code


def handle_validation_error(e: ValidationError) -> Response:
    """
    Maneja excepciones de validación.
    
    Args:
        e: Excepción de validación
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.warning(f"Error de validación: {str(e)}")
    
    return jsonify(e.to_dict()), e.status_code


def handle_business_error(e: BusinessError) -> Response:
    """
    Maneja excepciones de lógica de negocio.
    
    Args:
        e: Excepción de lógica de negocio
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.warning(f"Error de negocio: {str(e)}")
    
    return jsonify(e.to_dict()), e.status_code


def handle_authentication_error(e: AuthenticationError) -> Response:
    """
    Maneja excepciones de autenticación.
    
    Args:
        e: Excepción de autenticación
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.warning(f"Error de autenticación: {str(e)}")
    
    return jsonify(e.to_dict()), e.status_code


def handle_authorization_error(e: AuthorizationError) -> Response:
    """
    Maneja excepciones de autorización.
    
    Args:
        e: Excepción de autorización
        
    Returns:
        Respuesta JSON con información del error
    """
    logger.warning(f"Error de autorización: {str(e)}")
    
    return jsonify(e.to_dict()), e.status_code


def handle_unhandled_exception(e: Exception) -> Response:
    """
    Maneja excepciones no manejadas.
    
    Args:
        e: Excepción no manejada
        
    Returns:
        Respuesta JSON con información del error
    """
    # Registrar excepción con traceback
    logger.exception(f"Error no manejado: {str(e)}")
    
    # En producción, no exponer detalles de errores no manejados
    if current_app.config.get("ENV") == "production":
        response = {
            "error": "InternalServerError",
            "message": "Se produjo un error interno en el servidor"
        }
    else:
        response = {
            "error": e.__class__.__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    
    return jsonify(response), 500


def error_handling_middleware() -> Callable:
    """
    Middleware para manejo de errores.
    
    Returns:
        Función middleware
    """
    def middleware(next_handler: Callable) -> Callable:
        def handler(*args: Any, **kwargs: Any) -> Any:
            try:
                return next_handler(*args, **kwargs)
            except Exception as e:
                # Convertir excepciones no manejadas a respuestas JSON
                if isinstance(e, HTTPException):
                    return handle_http_exception(e)
                elif isinstance(e, AdFluxError):
                    return handle_adflux_error(e)
                else:
                    return handle_unhandled_exception(e)
        
        return handler
    
    return middleware
