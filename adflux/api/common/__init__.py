"""
Utilidades comunes para los clientes de API.

Este módulo proporciona funcionalidades compartidas entre los diferentes
clientes de API, como manejo de errores y logging.
"""

from .excepciones import (
    AdFluxError,
    ErrorBaseDatos,
    ErrorValidacion,
    ErrorAutenticacion,
    ErrorAutorizacion,
    ErrorRecursoNoEncontrado,
    ErrorAPI,
    ErrorTarea
)

# Importar funciones de manejo de errores
from .manejo_errores import (
    registrar_error,
    respuesta_error_api,
    notificar_error_web,
    manejar_excepcion,
    manejar_error_api,
    manejar_error_web,
    handle_meta_api_error,
    handle_google_ads_api_error,
    handle_gemini_api_error
)

# Versión del módulo Common
__version__ = "0.1.0"

__all__ = [
    'AdFluxError',
    'ErrorBaseDatos',
    'ErrorValidacion',
    'ErrorAutenticacion',
    'ErrorAutorizacion',
    'ErrorRecursoNoEncontrado',
    'ErrorAPI',
    'ErrorTarea',
    
    'registrar_error',
    'respuesta_error_api',
    'notificar_error_web',
    'manejar_excepcion',
    'manejar_error_api',
    'manejar_error_web',
    'handle_meta_api_error',
    'handle_google_ads_api_error',
    'handle_gemini_api_error'
]
