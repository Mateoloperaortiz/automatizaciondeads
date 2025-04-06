"""
Utilidades para el manejo de errores en las APIs.

Este módulo proporciona decoradores y funciones para manejar errores
de manera consistente en todas las llamadas a APIs externas.
"""

import functools
from typing import Callable, Any, Tuple, Dict

# Intentar importar Flask, pero no fallar si no está disponible
try:
    from flask import current_app
except ImportError:
    current_app = None

# Importaciones específicas para cada API
from facebook_business.exceptions import FacebookRequestError

# Estas importaciones se habilitarán cuando se implementen los módulos correspondientes
# from google.ads.googleads.errors import GoogleAdsException


def handle_meta_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Meta de manera consistente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Meta.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[bool, str, Any]:
        try:
            return func(*args, **kwargs)
        except FacebookRequestError as e:
            mensaje_error = f"Error de API Meta en {func.__name__}: {e}"
            if current_app:
                current_app.logger.error(mensaje_error)
            else:
                print(mensaje_error)
            return False, f"Error de API: {e.api_error_message()}", None
        except ImportError as e:
            mensaje_error = f"Error de importación en {func.__name__}: {e}"
            if current_app:
                current_app.logger.error(mensaje_error)
            else:
                print(mensaje_error)
            return False, f"Error de importación del SDK: {e}", None
        except Exception as e:
            mensaje_error = f"Error inesperado en {func.__name__}: {e}"
            if current_app:
                current_app.logger.error(mensaje_error, exc_info=True)
            else:
                print(mensaje_error)
            return False, f"Error inesperado: {e}", None

    return wrapper


def handle_google_ads_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Google Ads de manera consistente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Google Ads.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return func(*args, **kwargs)
        except Exception as e:  # Reemplazar con GoogleAdsException cuando se implemente
            mensaje_error = f"Error de API Google Ads en {func.__name__}: {e}"
            if current_app:
                current_app.logger.error(mensaje_error, exc_info=True)
            else:
                print(mensaje_error)
            return {
                "success": False,
                "message": f"Error de API Google Ads: {str(e)}",
                "external_ids": None,
            }

    return wrapper


def handle_gemini_api_error(func: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de Google Gemini de manera consistente.

    Args:
        func: La función a decorar.

    Returns:
        La función decorada que maneja los errores de la API de Google Gemini.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[bool, str, Dict[str, Any]]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            mensaje_error = f"Error de API Gemini en {func.__name__}: {e}"
            if current_app:
                current_app.logger.error(mensaje_error, exc_info=True)
            else:
                print(mensaje_error)
            return False, f"Error de API Gemini: {str(e)}", {}

    return wrapper
