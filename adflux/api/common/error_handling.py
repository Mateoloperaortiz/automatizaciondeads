"""
Utilidades para el manejo de errores en AdFlux.

Este módulo proporciona decoradores, funciones y middleware para manejar errores
de manera consistente en toda la aplicación. Incluye:

- Decoradores para manejar errores en rutas de API y web
- Funciones para registrar errores y generar respuestas estandarizadas
- Middleware para manejar errores de manera centralizada
- Manejadores específicos para diferentes tipos de excepciones

NOTA: Este módulo ahora utiliza las excepciones definidas en adflux.exceptions
y proporciona adaptadores para mantener compatibilidad con el código existente.
"""

import functools
import traceback
import logging
from typing import Callable, Any, Tuple, Dict, Optional, List, Union, Type

try:
    from flask import current_app, flash, jsonify, request, Flask, Response
except ImportError:
    current_app = None
    flash = None
    jsonify = None
    request = None
    Flask = None
    Response = None

try:
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    SQLAlchemyError = Exception

try:
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    FacebookRequestError = Exception

try:
    from werkzeug.exceptions import HTTPException
except ImportError:
    HTTPException = Exception

from ...exceptions.base import AdFluxError, AdFluxWarning
from ...exceptions.api import (
    APIError, APIConnectionError, APITimeoutError, APIRateLimitError,
    APIAuthenticationError, APIPermissionError, APIResourceError,
    APIValidationError, APINotFoundError, APIServerError
)
from ...exceptions.database import (
    DatabaseError, DatabaseConnectionError, DatabaseQueryError,
    DatabaseIntegrityError, DatabaseTimeoutError, DatabaseNotFoundError
)
from ...exceptions.validation import (
    ValidationError, InvalidInputError, MissingRequiredFieldError,
    InvalidFormatError, InvalidValueError, InvalidTypeError
)
from ...exceptions.business import (
    BusinessError, ResourceNotFoundError, ResourceAlreadyExistsError,
    ResourceInUseError, OperationNotAllowedError, LimitExceededError
)
from ...exceptions.auth import (
    AuthenticationError, AuthorizationError, TokenExpiredError,
    InvalidTokenError, InvalidCredentialsError, AccountLockedError
)
from ...exceptions.file import (
    FileError, FileNotFoundError, FilePermissionError, FileFormatError,
    FileSizeError, FileUploadError, FileDownloadError
)

from .excepciones import (
    ErrorBaseDatos,
    ErrorValidacion,
    ErrorAutenticacion,
    ErrorAutorizacion,
    ErrorRecursoNoEncontrado,
    ErrorAPI,
    ErrorTarea,
)


def registrar_error(
    mensaje: str,
    excepcion: Optional[Exception] = None,
    nivel: str = "error",
    exc_info: bool = True,
    extra: Optional[Dict[str, Any]] = None,
    contexto: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Registra un error en el sistema de logging.

    Args:
        mensaje: Mensaje descriptivo del error.
        excepcion: Excepción que causó el error.
        nivel: Nivel de logging (error, warning, info, etc.).
        exc_info: Si se debe incluir información detallada de la excepción.
        extra: Información adicional para el registro.
        contexto: Información contextual sobre dónde ocurrió el error.
    """
    if not current_app:
        print(f"{nivel.upper()}: {mensaje}")
        if contexto:
            print(f"Contexto: {contexto}")
        if excepcion and exc_info:
            print(f"Excepción: {excepcion}")
            traceback.print_exc()
        return

    logger = current_app.logger
    log_method = getattr(logger, nivel, logger.error)

    if not extra:
        extra = {}
    
    if contexto:
        extra.update({"contexto": contexto})

    if excepcion and isinstance(excepcion, AdFluxError) and hasattr(excepcion, 'detalles'):
        extra.update(getattr(excepcion, 'detalles', {}))

    if excepcion and exc_info:
        log_method(mensaje, exc_info=True, extra=extra)
    else:
        log_method(mensaje, extra=extra)


def respuesta_error_api(
    mensaje: str,
    codigo: int = 400,
    errores: Optional[Union[Dict[str, List[str]], str]] = None,
    detalles: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], int]:
    """
    Genera una respuesta de error estandarizada para APIs.

    Args:
        mensaje: Mensaje descriptivo del error.
        codigo: Código HTTP de estado.
        errores: Errores de validación por campo o mensaje de error.
        detalles: Información adicional sobre el error.

    Returns:
        Tupla con la respuesta JSON y el código de estado HTTP.
    """
    respuesta = {"success": False, "message": mensaje}

    if errores:
        if isinstance(errores, dict):
            respuesta["errors"] = errores
        else:
            respuesta["error_details"] = errores

    if detalles:
        for clave, valor in detalles.items():
            if clave not in respuesta:
                respuesta[clave] = valor

    return respuesta, codigo


def notificar_error_web(
    mensaje: str,
    categoria: str = "error",
    detalles: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Notifica un error al usuario en la interfaz web.

    Args:
        mensaje: Mensaje descriptivo del error.
        categoria: Categoría del mensaje (error, warning, info, etc.).
        detalles: Información adicional sobre el error.
    """
    if flash:
        flash(mensaje, categoria)

    nivel_log = "error" if categoria == "error" else "info"
    registrar_error(mensaje, nivel=nivel_log, exc_info=False, extra=detalles)


def manejar_excepcion(
    excepcion: Exception,
    prefijo_mensaje: str = "Error en la operación",
    es_api: bool = False,
) -> Union[Tuple[Dict[str, Any], int], str]:
    """
    Maneja una excepción y genera la respuesta apropiada.

    Args:
        excepcion: Excepción a manejar.
        prefijo_mensaje: Prefijo para el mensaje de error.
        es_api: Si la respuesta es para una API o para la web.

    Returns:
        Respuesta de error para API o mensaje para web.
    """
    if isinstance(excepcion, ErrorBaseDatos):
        mensaje = f"{prefijo_mensaje}: Error de base de datos - {getattr(excepcion, 'mensaje', str(excepcion))}"
        registrar_error(mensaje, excepcion, exc_info=True)
        if es_api:
            return respuesta_error_api(
                mensaje, 
                getattr(excepcion, 'codigo', 500), 
                detalles=getattr(excepcion, 'detalles', {})
            )
        else:
            notificar_error_web(mensaje)
            return mensaje

    elif isinstance(excepcion, ErrorValidacion):
        mensaje = f"{prefijo_mensaje}: Error de validación - {getattr(excepcion, 'mensaje', str(excepcion))}"
        registrar_error(mensaje, excepcion, nivel="warning")
        if es_api:
            return respuesta_error_api(
                mensaje, 
                getattr(excepcion, 'codigo', 400), 
                errores=getattr(excepcion, 'errores', None), 
                detalles=getattr(excepcion, 'detalles', {})
            )
        else:
            notificar_error_web(mensaje)
            return mensaje

    elif isinstance(excepcion, ErrorRecursoNoEncontrado):
        mensaje = f"{prefijo_mensaje}: {getattr(excepcion, 'mensaje', str(excepcion))}"
        registrar_error(mensaje, excepcion, nivel="warning")
        if es_api:
            return respuesta_error_api(
                mensaje, 
                getattr(excepcion, 'codigo', 404), 
                detalles=getattr(excepcion, 'detalles', {})
            )
        else:
            notificar_error_web(mensaje)
            return mensaje

    elif isinstance(excepcion, (ErrorAutenticacion, ErrorAutorizacion)):
        mensaje = f"{prefijo_mensaje}: {getattr(excepcion, 'mensaje', str(excepcion))}"
        registrar_error(mensaje, excepcion, nivel="warning")
        if es_api:
            return respuesta_error_api(
                mensaje, 
                getattr(excepcion, 'codigo', 401), 
                detalles=getattr(excepcion, 'detalles', {})
            )
        else:
            notificar_error_web(mensaje)
            return mensaje

    elif isinstance(excepcion, ErrorAPI):
        mensaje = f"{prefijo_mensaje}: Error en API {getattr(excepcion, 'api', 'desconocida')} - {getattr(excepcion, 'mensaje', str(excepcion))}"
        registrar_error(mensaje, excepcion, exc_info=True)
        if es_api:
            return respuesta_error_api(
                mensaje, 
                getattr(excepcion, 'codigo', 500), 
                detalles=getattr(excepcion, 'detalles', {})
            )
        else:
            notificar_error_web(mensaje)
            return mensaje

    elif isinstance(excepcion, ErrorTarea):
        mensaje = f"{prefijo_mensaje}: Error en tarea {getattr(excepcion, 'tarea_id', '') or ''} - {getattr(excepcion, 'mensaje', str(excepcion))}"
        registrar_error(mensaje, excepcion, exc_info=True)
        if es_api:
            return respuesta_error_api(
                mensaje, 
                getattr(excepcion, 'codigo', 500), 
                detalles=getattr(excepcion, 'detalles', {})
            )
        else:
            notificar_error_web(mensaje)
            return mensaje

    elif isinstance(excepcion, SQLAlchemyError):
        mensaje = f"{prefijo_mensaje}: Error de base de datos - {str(excepcion)}"
        registrar_error(mensaje, excepcion, exc_info=True)
        if es_api:
            return respuesta_error_api(mensaje, 500)
        else:
            notificar_error_web(mensaje)
            return mensaje

    elif isinstance(excepcion, FacebookRequestError):
        mensaje_api_error = ""
        get_api_error = lambda obj: obj.api_error_message() if hasattr(obj, 'api_error_message') and callable(getattr(obj, 'api_error_message', None)) else str(obj)
        # Directly call the lambda, let other exceptions propagate if needed
        mensaje_api_error = get_api_error(excepcion)
        mensaje = f"{prefijo_mensaje}: Error de API Meta - {mensaje_api_error}"
        registrar_error(mensaje, excepcion, exc_info=True)
        if es_api:
            return respuesta_error_api(mensaje, 500, detalles={"api": "Meta"})
        else:
            notificar_error_web(mensaje)
            return mensaje

    else:
        mensaje = f"{prefijo_mensaje}: {str(excepcion)}"
        registrar_error(mensaje, excepcion, exc_info=True)
        if es_api:
            return respuesta_error_api(mensaje, 500)
        else:
            notificar_error_web(mensaje)
            return mensaje


def handle_error(
    api_name: Optional[str] = None,
    es_api: bool = True,
    status_code: int = 500,
    redirect_on_error: bool = False,
    error_template: str = "error.html",
    specific_exceptions: Optional[Dict[Type[Exception], Callable[[Exception], Exception]]] = None
) -> Callable:
    """
    Decorador genérico para manejar errores de manera consistente.
    
    Args:
        api_name: Nombre de la API (si aplica).
        es_api: Si la respuesta es para una API o para la web.
        status_code: Código de estado HTTP por defecto para errores.
        redirect_on_error: Si se debe redirigir a la página anterior en caso de error (solo para web).
        error_template: Plantilla a usar para mostrar errores (solo para web).
        specific_exceptions: Diccionario de excepciones específicas y funciones para manejarlas.
        
    Returns:
        Decorador configurado para manejar errores.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                prefijo = f"Error en {func.__name__}"
                
                if specific_exceptions and any(isinstance(e, exc_type) for exc_type in specific_exceptions):
                    for exc_type, handler in specific_exceptions.items():
                        if isinstance(e, exc_type):
                            raise handler(e)
                
                if api_name:
                    if isinstance(e, FacebookRequestError) and api_name == "Meta":
                        mensaje_api_error = ""
                        get_api_error = lambda obj: obj.api_error_message() if hasattr(obj, 'api_error_message') and callable(getattr(obj, 'api_error_message', None)) else str(obj)
                        mensaje_api_error = get_api_error(e)
                        raise APIError(
                            message=f"Error de API {api_name}: {mensaje_api_error}",
                            api_name=api_name,
                            cause=e,
                            status_code=status_code
                        )
                    else:
                        raise APIError(
                            message=f"Error de API {api_name}: {str(e)}",
                            api_name=api_name,
                            cause=e,
                            status_code=status_code
                        )
                
                if es_api:
                    return manejar_excepcion(e, prefijo, es_api=True)
                else:
                    manejar_excepcion(e, prefijo, es_api=False)
                    if redirect_on_error and request and hasattr(request, "referrer") and request.referrer:
                        from flask import redirect
                        return redirect(request.referrer)
                    else:
                        from flask import render_template
                        return render_template(error_template, error=str(e))
                        
        return wrapper
    return decorator


def manejar_error_api(func: Callable) -> Callable:
    """
    Decorador para manejar errores en rutas de API.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de API.
    """
    return handle_error(es_api=True)(func)


def manejar_error_web(func: Callable) -> Callable:
    """
    Decorador para manejar errores en rutas web.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores web.
    """
    return handle_error(es_api=False, redirect_on_error=True)(func)


def handle_meta_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Meta de manera consistente.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Meta.
    """
    specific_exceptions = {
        ImportError: lambda e: AdFluxError(
            message=f"Error de importación del SDK de Meta: {e}",
            status_code=500
        )
    }
    
    return handle_error(
        api_name="Meta",
        es_api=True,
        status_code=500,
        specific_exceptions=specific_exceptions
    )(func)


def handle_google_ads_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Google Ads de manera consistente.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Google Ads.
    """
    return handle_error(api_name="Google Ads", es_api=True, status_code=500)(func)


def handle_gemini_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Google Gemini de manera consistente.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Google Gemini.
    """
    return handle_error(api_name="Gemini", es_api=True, status_code=500)(func)


logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """
    Registra manejadores de errores en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
    """
    if not app:
        return
        
    app.register_error_handler(HTTPException, handle_http_exception)
    
    app.register_error_handler(AdFluxError, handle_adflux_error)
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(DatabaseError, handle_database_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(BusinessError, handle_business_error)
    app.register_error_handler(AuthenticationError, handle_authentication_error)
    app.register_error_handler(AuthorizationError, handle_authorization_error)
    
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
    
    if current_app and current_app.config.get("ENV") == "production":
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
    
    if current_app and current_app.config.get("ENV") == "production":
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
                if isinstance(e, HTTPException):
                    return handle_http_exception(e)
                elif isinstance(e, AdFluxError):
                    return handle_adflux_error(e)
                else:
                    return handle_unhandled_exception(e)
        
        return handler
    
    return middleware
