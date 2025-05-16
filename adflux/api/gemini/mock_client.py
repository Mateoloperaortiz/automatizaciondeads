"""
Cliente mock para la API de Google Gemini.

Este módulo proporciona una implementación simulada del cliente de Gemini
para pruebas sin necesidad de una clave de API válida.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import json
import random

from adflux.api.common.logging import get_logger

logger = get_logger("MockGeminiAPI")

class MockGeminiApiClient:
    """
    Cliente simulado para la API de Google Gemini.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el cliente simulado.
        
        Args:
            api_key: No se utiliza, pero se mantiene para compatibilidad.
        """
        self.initialized = True
        logger.info("Cliente mock de Gemini inicializado")
    
    def initialize(self) -> bool:
        """
        Simula la inicialización de la API.
        
        Returns:
            True siempre, indicando éxito.
        """
        self.initialized = True
        logger.info("Cliente mock de Gemini inicializado")
        return True
    
    def ensure_initialized(self):
        """
        No hace nada, ya que el cliente mock siempre está inicializado.
        """
        pass
    
    def test_connection(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Simula una prueba de conexión exitosa.
        
        Returns:
            Tupla simulando una conexión exitosa.
        """
        models = [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-ultra"
        ]
        
        return (
            True,
            f"Conexión simulada exitosa. Modelos disponibles: {len(models)}",
            {"models": models}
        )
    
    def get_available_models(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Simula la obtención de modelos disponibles.
        
        Returns:
            Tupla con modelos simulados.
        """
        models = [
            {
                "name": "gemini-pro",
                "display_name": "Gemini Pro",
                "description": "Modelo de lenguaje de propósito general",
                "input_token_limit": 30720,
                "output_token_limit": 2048,
                "supported_generation_methods": ["generateContent", "countTokens"],
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 40,
                "input_image": False
            },
            {
                "name": "gemini-pro-vision",
                "display_name": "Gemini Pro Vision",
                "description": "Modelo multimodal para texto e imágenes",
                "input_token_limit": 12288,
                "output_token_limit": 4096,
                "supported_generation_methods": ["generateContent", "countTokens"],
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 32,
                "input_image": True
            }
        ]
        
        return True, f"Se recuperaron {len(models)} modelos simulados de Gemini.", models


class MockContentGenerator:
    """
    Generador de contenido simulado para anuncios.
    """
    
    def __init__(self, client=None):
        """
        Inicializa el generador de contenido simulado.
        
        Args:
            client: No se utiliza, pero se mantiene para compatibilidad.
        """
        self.client = client or MockGeminiApiClient()
        logger.info("Generador de contenido mock inicializado")
    
    def generate_ad_content(
        self,
        job_data: Dict[str, Any],
        platform: str,
        segment_data: Optional[Dict[str, Any]] = None,
        format_type: Optional[str] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera contenido simulado para un anuncio.
        
        Args:
            job_data: Datos de la oferta de trabajo
            platform: Plataforma (meta, google, tiktok, snapchat)
            segment_data: Datos del segmento objetivo (opcional)
            format_type: Tipo de formato (imagen_única, carrusel, video, etc.)
            
        Returns:
            Tupla con contenido simulado.
        """
        logger.info(f"Generando contenido simulado para plataforma {platform}, formato {format_type}")
        
        job_title = job_data.get("title", "Oferta de trabajo")
        company = job_data.get("company", "Empresa")
        location = job_data.get("location", "Ubicación")
        
        if platform == "meta":
            return self._generate_meta_content(job_title, company, location, format_type)
        elif platform == "google":
            return self._generate_google_content(job_title, company, location, format_type)
        elif platform == "tiktok":
            return self._generate_tiktok_content(job_title, company, location, format_type)
        elif platform == "snapchat":
            return self._generate_snapchat_content(job_title, company, location, format_type)
        else:
            return False, f"Plataforma no soportada: {platform}", {}
    
    def generate_ad_variations(
        self,
        base_content: Dict[str, Any],
        platform: str,
        num_variations: int = 3,
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Genera variaciones simuladas de un anuncio base.
        
        Args:
            base_content: Contenido base del anuncio
            platform: Plataforma para la que se generan las variaciones
            num_variations: Número de variaciones a generar
            
        Returns:
            Tupla con variaciones simuladas.
        """
        logger.info(f"Generando {num_variations} variaciones simuladas para plataforma {platform}")
        
        variations = []
        for i in range(num_variations):
            variation = base_content.copy()
            
            if "headline" in variation:
                variation["headline"] = f"Variación {i+1}: {variation['headline']}"
            
            if "description" in variation:
                variation["description"] = f"{variation['description']} (Variante {i+1})"
            
            variations.append(variation)
        
        return True, f"Se generaron {num_variations} variaciones simuladas.", variations
    
    def _generate_meta_content(self, job_title, company, location, format_type):
        """Genera contenido simulado para Meta (Facebook/Instagram)."""
        content = {
            "headline": f"¡Únete a nuestro equipo como {job_title}!",
            "description": f"Estamos buscando un/a {job_title} para unirse a nuestro equipo en {company}. Ubicación: {location}.",
            "cta": "Aplicar ahora",
            "platform": "meta",
            "format": format_type or "imagen_única",
        }
        
        if format_type == "carrusel":
            content["slides"] = [
                {"title": "Descripción del puesto", "text": f"Como {job_title}, serás responsable de..."},
                {"title": "Requisitos", "text": "Buscamos candidatos con experiencia en..."},
                {"title": "Beneficios", "text": "Ofrecemos un salario competitivo y..."}
            ]
        
        return True, "Contenido simulado generado exitosamente para Meta", content
    
    def _generate_google_content(self, job_title, company, location, format_type):
        """Genera contenido simulado para Google Ads."""
        content = {
            "headline1": f"{job_title} - {company}",
            "headline2": f"Trabaja en {location}",
            "headline3": "Aplica hoy",
            "description1": f"Únete a nuestro equipo como {job_title}.",
            "description2": f"Grandes oportunidades en {company}.",
            "platform": "google",
            "format": format_type or "texto",
        }
        
        return True, "Contenido simulado generado exitosamente para Google", content
    
    def _generate_tiktok_content(self, job_title, company, location, format_type):
        """Genera contenido simulado para TikTok."""
        content = {
            "caption": f"¿Buscas trabajo como {job_title}? ¡{company} está contratando! #empleo #trabajo #{job_title.replace(' ', '')}",
            "text_overlay": f"¡{company} está contratando!",
            "cta": "Aplicar",
            "platform": "tiktok",
            "format": format_type or "video",
        }
        
        return True, "Contenido simulado generado exitosamente para TikTok", content
    
    def _generate_snapchat_content(self, job_title, company, location, format_type):
        """Genera contenido simulado para Snapchat."""
        content = {
            "headline": f"¡{company} está contratando!",
            "body_text": f"Buscamos {job_title} en {location}. ¡Desliza hacia arriba para aplicar!",
            "cta": "Aplicar ahora",
            "platform": "snapchat",
            "format": format_type or "imagen",
        }
        
        return True, "Contenido simulado generado exitosamente para Snapchat", content


def get_mock_content_generator() -> MockContentGenerator:
    """
    Obtiene una instancia del generador de contenido mock.
    
    Returns:
        Una instancia de MockContentGenerator.
    """
    return MockContentGenerator()
