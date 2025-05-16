"""
Cliente de API para Google Gemini.

Este módulo proporciona funcionalidades para interactuar con la API de Google Gemini,
incluyendo la generación de contenido para anuncios.
"""

import os
import logging

# Importar cliente de Gemini
from .client import GeminiApiClient, get_client

# Importar generador de contenido
from .content_generator import ContentGenerator, get_content_generator

# Versión del módulo Gemini API
__version__ = "0.1.0"

logger = logging.getLogger(__name__)

USE_MOCK_CLIENT = os.getenv("USE_MOCK_CLIENT", "False").lower() in ("true", "1", "yes")

if USE_MOCK_CLIENT or not os.getenv("GEMINI_API_KEY"):
    try:
        from .mock_client import MockGeminiApiClient, MockContentGenerator, get_mock_content_generator
        
        _original_get_client = get_client
        _original_get_content_generator = get_content_generator
        
        def get_client(api_key=None):
            """Versión mock de get_client que devuelve un cliente simulado."""
            logger.info("Usando cliente mock de Gemini API")
            return MockGeminiApiClient(api_key)
        
        def get_content_generator():
            """Versión mock de get_content_generator que devuelve un generador simulado."""
            logger.info("Usando generador de contenido mock de Gemini")
            return get_mock_content_generator()
        
        logger.warning("Usando implementación mock de Gemini API. No se realizarán llamadas reales a la API.")
    except ImportError as e:
        logger.error(f"No se pudo importar el cliente mock: {e}")

__all__ = [
    "GeminiApiClient",
    "get_client",
    "ContentGenerator",
    "get_content_generator",
]
