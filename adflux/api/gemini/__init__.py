"""
Cliente de API para Google Gemini.

Este módulo proporciona funcionalidades para interactuar con la API de Google Gemini,
incluyendo la generación de contenido para anuncios.
"""

# Importar cliente de Gemini
from adflux.api.gemini.client import get_client, GeminiApiClient

# Importar generador de contenido
from adflux.api.gemini.content_generation import ContentGenerator, get_content_generator

# Versión del módulo Gemini API
__version__ = '0.1.0'
