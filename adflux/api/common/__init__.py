"""
Utilidades comunes para los clientes de API.

Este módulo proporciona funcionalidades compartidas entre los diferentes
clientes de API, como manejo de errores y logging.
"""

# Importar funciones de manejo de errores
from adflux.api.common.error_handling import (
    handle_meta_api_error,
    handle_google_ads_api_error,
    handle_gemini_api_error
)

# Importar funciones de logging
from adflux.api.common.logging import (
    log_info,
    log_warning,
    log_error,
    get_logger,
    ApiLogger
)

# Versión del módulo Common
__version__ = '0.1.0'
