"""
Utilidades para el manejo de errores en AdFlux.

Este módulo proporciona decoradores y funciones para manejar errores
de manera consistente en toda la aplicación.

NOTA: Este módulo ahora utiliza las excepciones definidas en adflux.exceptions
y proporciona adaptadores para mantener compatibilidad con el código existente.
"""

import functools
import traceback
from typing import Callable, Any, Tuple, Dict, Optional, List, Union

try:
    from flask import current_app, flash, jsonify, request
except ImportError:
    current_app = None
    flash = None
    jsonify = None
    request = None

try:
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    SQLAlchemyError = Exception

try:
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    FacebookRequestError = Exception

from ...exceptions.base import AdFluxError
from ...exceptions.api import APIError

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


def manejar_error_api(func: Callable) -> Callable:
    """
    Decorador para manejar errores en rutas de API.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de API.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            prefijo = f"Error en {func.__name__}"
            return manejar_excepcion(e, prefijo, es_api=True)

    return wrapper


def manejar_error_web(func: Callable) -> Callable:
    """
    Decorador para manejar errores en rutas web.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores web.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            prefijo = f"Error en {func.__name__}"
            manejar_excepcion(e, prefijo, es_api=False)
            if request and hasattr(request, "referrer") and request.referrer:
                from flask import redirect
                return redirect(request.referrer)
            else:
                from flask import render_template
                return render_template("error.html", error=str(e))

    return wrapper


def handle_meta_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Meta de manera consistente.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Meta.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FacebookRequestError as e:
            # Handle Facebook errors specifically
            mensaje_api_error = ""
            # Use lambda to safely attempt calling api_error_message()
            get_api_error = lambda obj: obj.api_error_message() if hasattr(obj, 'api_error_message') and callable(getattr(obj, 'api_error_message', None)) else str(obj)
            # Directly call the lambda, let other exceptions propagate if needed
            mensaje_api_error = get_api_error(e)
            raise APIError(
                message=f"Error de API Meta: {mensaje_api_error}",
                api_name="Meta",
                cause=e,
                status_code=500
            )
        except ImportError as e:
            raise AdFluxError(
                message=f"Error de importación del SDK de Meta: {e}",
                status_code=500
            )
        except Exception as e:
            # Wrap other exceptions
            raise APIError(
                message=f"Error inesperado interactuando con API Meta: {e}",
                api_name="Meta",
                cause=e,
                status_code=500
            )

    return wrapper


def handle_google_ads_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Google Ads de manera consistente.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Google Ads.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise APIError(
                message=f"Error de API Google Ads: {str(e)}",
                api_name="Google Ads",
                cause=e,
                status_code=500
            )

    return wrapper


def handle_gemini_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Google Gemini de manera consistente.
    Mantiene compatibilidad con el código existente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Google Gemini.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Raise standardized APIError
            raise APIError(
                message=f"Error de API Gemini: {str(e)}",
                api_name="Gemini",
                cause=e,
                status_code=500
            )

    return wrapper
