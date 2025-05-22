"""
Cliente para la API de Google Gemini.

Este módulo proporciona la clase principal para interactuar con la API de Google Gemini,
incluyendo la inicialización y prueba de conexión.
"""

import os
from typing import Tuple, List, Dict, Any, Optional

# Intentar importar Google Generative AI SDK, pero no fallar si no está disponible
try:
    import google.generativeai as genai

    GEMINI_SDK_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_SDK_AVAILABLE = False

from adflux.api.common.error_handling import handle_gemini_api_error
from adflux.api.common.logging import get_logger
from adflux.exceptions.base import AdFluxError
from adflux.exceptions.api import APIError

# Configurar logger
logger = get_logger("GeminiAPI")


class GeminiApiClient:
    """
    Cliente para interactuar con la API de Google Gemini.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el cliente de la API de Google Gemini.

        Args:
            api_key: Clave de API de Google Gemini. Si es None, se usa GEMINI_API_KEY del entorno.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.initialized = False

    def initialize(self) -> bool:
        """
        Inicializa la API de Google Gemini con la clave de API.

        Returns:
            True si la inicialización fue exitosa, False en caso contrario.

        Raises:
            AdFluxError: Si el SDK no está disponible o falta la clave API.
            ErrorAPI: Si la configuración falla.
        """
        if not GEMINI_SDK_AVAILABLE:
            msg = "El SDK de Google Generative AI no está disponible. Instálalo con 'pip install google-generativeai'."
            logger.error(msg)
            raise AdFluxError(message=msg, status_code=500)

        # Check for API key *before* trying to configure
        if not self.api_key:
            print(f"DEBUG: self.api_key inside check: {repr(self.api_key)}") # DEBUG
            logger.error("No se proporcionó una clave de API para Google Gemini.")
            raise AdFluxError(message="No se proporcionó una clave de API para Google Gemini.", status_code=500)

        # Try configuring the API
        try:
            genai.configure(api_key=self.api_key)
            self.initialized = True
            logger.info("API de Google Gemini inicializada correctamente.")
            return True
        except Exception as e:
            msg = f"Error al inicializar la API de Google Gemini: {e}"
            logger.error(msg, exc_info=True)
            # Raise APIError as configuration likely failed due to external API issue
            raise APIError(message=msg, api_name="Gemini", cause=e, status_code=500)

    def ensure_initialized(self):
        """
        Asegura que la API esté inicializada. Lanza excepción si falla.
        """
        if not self.initialized:
            self.initialize()

    @handle_gemini_api_error
    def test_connection(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Prueba la conexión a la API de Google Gemini.

        Returns:
            Una tupla con: (éxito, mensaje, datos adicionales).
        """
        self.ensure_initialized()

        try:
            # Obtener modelos disponibles
            models = genai.list_models()
            gemini_models = [model.name for model in models if "gemini" in model.name.lower()]

            if gemini_models:
                return (
                    True,
                    f"Conexión exitosa. Modelos Gemini disponibles: {len(gemini_models)}",
                    {"models": gemini_models},
                )
            else:
                return (
                    True,
                    "Conexión exitosa, pero no se encontraron modelos Gemini.",
                    {"models": []},
                )

        except Exception as e:
            logger.error(f"Error al probar la conexión a la API de Google Gemini: {e}", e)
            raise

    @handle_gemini_api_error
    def get_available_models(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Obtiene la lista de modelos disponibles en la API de Google Gemini.

        Returns:
            Una tupla con: (éxito, mensaje, lista de modelos).
        """
        self.ensure_initialized()

        try:
            # Obtener modelos disponibles
            models = genai.list_models()

            # Procesar los resultados para un formato más amigable
            models_list = []
            for model in models:
                # Solo incluir modelos de Gemini
                if "gemini" in model.name.lower():
                    model_data = {
                        "name": model.name,
                        "display_name": getattr(model, "display_name", model.name),
                        "description": getattr(model, "description", ""),
                        "input_token_limit": getattr(model, "input_token_limit", 0),
                        "output_token_limit": getattr(model, "output_token_limit", 0),
                        "supported_generation_methods": getattr(
                            model, "supported_generation_methods", []
                        ),
                        "temperature": getattr(model, "temperature", 0.0),
                        "top_p": getattr(model, "top_p", 0.0),
                        "top_k": getattr(model, "top_k", 0),
                        "input_image": "vision" in model.name.lower()
                        or "multimodal" in model.name.lower(),
                    }
                    models_list.append(model_data)

            logger.info(f"Se recuperaron {len(models_list)} modelos de Gemini disponibles.")
            return True, f"Se recuperaron {len(models_list)} modelos de Gemini.", models_list

        except Exception as e:
            logger.error(f"Error al obtener los modelos disponibles: {e}", e)
            raise


# Crear una instancia del cliente por defecto
_default_client = None


def get_client(api_key: Optional[str] = None) -> GeminiApiClient:
    """
    Obtiene una instancia del cliente de la API de Google Gemini.

    Si se proporciona una clave de API, se crea un nuevo cliente con esa clave.
    Si no, se devuelve el cliente por defecto (creándolo si es necesario).

    Args:
        api_key: Clave de API de Google Gemini.

    Returns:
        Una instancia de GeminiApiClient.
    """
    global _default_client

    if api_key:
        return GeminiApiClient(api_key)

    if _default_client is None:
        _default_client = GeminiApiClient()

    return _default_client
