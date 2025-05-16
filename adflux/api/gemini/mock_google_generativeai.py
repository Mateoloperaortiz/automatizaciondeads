"""
Módulo mock para google.generativeai.

Este módulo proporciona una implementación simulada del módulo google.generativeai
para pruebas sin necesidad de una clave de API válida.
"""

import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("MockGoogleGenerativeAI")

class MockGenerativeModel:
    """
    Modelo generativo simulado para pruebas.
    """
    
    def __init__(self, model_name=None, generation_config=None):
        """
        Inicializa el modelo generativo simulado.
        
        Args:
            model_name: Nombre del modelo (no utilizado)
            generation_config: Configuración de generación (no utilizado)
        """
        self.model_name = model_name
        self.generation_config = generation_config
        logger.info(f"Modelo generativo mock inicializado: {model_name}")
    
    def generate_content(self, prompt):
        """
        Genera contenido simulado basado en el prompt.
        
        Args:
            prompt: Prompt para la generación
            
        Returns:
            Objeto de respuesta simulado
        """
        logger.info("Generando contenido simulado")
        
        if "Meta (Facebook/Instagram)" in prompt or "META" in prompt:
            return self._generate_meta_content(prompt)
        elif "Google Ads" in prompt or "GOOGLE" in prompt:
            return self._generate_google_content(prompt)
        elif "TikTok" in prompt or "TIKTOK" in prompt:
            return self._generate_tiktok_content(prompt)
        elif "Snapchat" in prompt or "SNAPCHAT" in prompt:
            return self._generate_snapchat_content(prompt)
        elif "variaciones" in prompt:
            return self._generate_variations(prompt)
        else:
            return MockResponse(json.dumps({"error": "No se pudo determinar el tipo de contenido"}))
    
    def _generate_meta_content(self, prompt):
        """Genera contenido simulado para Meta."""
        content = {
            "title": "Únete a nuestro equipo",  # Título más corto para cumplir con la restricción de 40 caracteres
            "description": "Estamos buscando talento como tú para formar parte de nuestra empresa líder en el sector. Grandes beneficios te esperan.",
            "cta": "Aplicar ahora",
            "visual_concept": "Imagen de profesionales colaborando en un ambiente moderno y dinámico",
            "hashtags": ["#Empleo", "#Oportunidad", "#DesarrolloProfesional"],
            "keywords": ["empleo", "trabajo", "carrera", "profesional"],
            "additional_elements": {
                "platform": "meta",
                "format": "imagen_única"
            }
        }
        
        if "carrusel" in prompt:
            content["additional_elements"]["format"] = "carrusel"
            content["slides"] = [
                {"title": "Descripción del puesto", "text": "Como parte de nuestro equipo, serás responsable de..."},
                {"title": "Requisitos", "text": "Buscamos candidatos con experiencia en..."},
                {"title": "Beneficios", "text": "Ofrecemos un salario competitivo y..."}
            ]
        
        return MockResponse(json.dumps(content))
    
    def _generate_google_content(self, prompt):
        """Genera contenido simulado para Google Ads."""
        content = {
            "title": "Empleo de Alto Nivel - Aplica Hoy",
            "description": "Únete a nuestra empresa líder. Grandes beneficios y oportunidades de crecimiento profesional te esperan.",
            "cta": "Ver oferta",
            "visual_concept": "Banner con imagen profesional y texto claro",
            "hashtags": ["#Empleo", "#Oportunidad"],
            "keywords": ["empleo", "trabajo", "carrera", "profesional", "vacante"],
            "additional_elements": {
                "headline1": "Empleo de Alto Nivel",
                "headline2": "Grandes Beneficios",
                "headline3": "Aplica Hoy",
                "description1": "Únete a nuestra empresa líder.",
                "description2": "Oportunidades de crecimiento.",
                "platform": "google",
                "format": "texto"
            }
        }
        
        return MockResponse(json.dumps(content))
    
    def _generate_tiktok_content(self, prompt):
        """Genera contenido simulado para TikTok."""
        content = {
            "title": "¿Buscas trabajo? 👀 ¡Tenemos la oportunidad perfecta para ti!",
            "description": "Swipe up para conocer esta increíble oportunidad laboral con los mejores beneficios del mercado 🔥",
            "cta": "Swipe up",
            "visual_concept": "Video corto mostrando el ambiente laboral con música de tendencia",
            "hashtags": ["#EmpleoIdeal", "#Oportunidad", "#TrabajoDeEnsueño", "#JobTok"],
            "keywords": ["empleo", "trabajo", "oportunidad"],
            "additional_elements": {
                "caption": "¿Buscas trabajo? ¡Tenemos la oportunidad perfecta para ti! #EmpleoIdeal #Oportunidad",
                "text_overlay": "¡Estamos contratando!",
                "music": "Canción viral actual",
                "platform": "tiktok",
                "format": "video"
            }
        }
        
        return MockResponse(json.dumps(content))
    
    def _generate_snapchat_content(self, prompt):
        """Genera contenido simulado para Snapchat."""
        content = {
            "title": "¡Estamos contratando! 👆",
            "description": "Desliza hacia arriba para conocer esta increíble oportunidad laboral 🚀",
            "cta": "Desliza hacia arriba",
            "visual_concept": "Imagen vertical con colores vibrantes y texto llamativo",
            "hashtags": ["#Empleo", "#Oportunidad"],
            "keywords": ["empleo", "trabajo", "oportunidad"],
            "additional_elements": {
                "headline": "¡Estamos contratando!",
                "body_text": "Desliza hacia arriba para conocer esta increíble oportunidad laboral",
                "platform": "snapchat",
                "format": "imagen"
            }
        }
        
        return MockResponse(json.dumps(content))
    
    def _generate_variations(self, prompt):
        """Genera variaciones simuladas de un anuncio."""
        variations = {
            "variations": [
                {
                    "title": "¡Únete a nuestro equipo de profesionales!",
                    "description": "Estamos buscando talento como tú para formar parte de nuestra empresa líder en el sector.",
                    "cta": "Aplicar ahora",
                    "visual_concept": "Imagen de profesionales colaborando",
                    "hashtags": ["#Empleo", "#Oportunidad", "#DesarrolloProfesional"],
                    "keywords": ["empleo", "trabajo", "carrera", "profesional"]
                },
                {
                    "title": "¡Oportunidad única para profesionales!",
                    "description": "Buscamos talento para nuestra empresa en expansión. Grandes beneficios te esperan.",
                    "cta": "Postúlate ya",
                    "visual_concept": "Imagen de oficina moderna",
                    "hashtags": ["#Trabajo", "#Crecimiento", "#Profesionales"],
                    "keywords": ["empleo", "trabajo", "carrera", "profesional"]
                },
                {
                    "title": "¡Desarrolla tu carrera con nosotros!",
                    "description": "Forma parte de un equipo dinámico y en crecimiento. Grandes oportunidades de desarrollo.",
                    "cta": "Conoce más",
                    "visual_concept": "Imagen de equipo diverso trabajando",
                    "hashtags": ["#Carrera", "#Desarrollo", "#Oportunidad"],
                    "keywords": ["empleo", "trabajo", "carrera", "profesional"]
                }
            ]
        }
        
        return MockResponse(json.dumps(variations))


class MockResponse:
    """
    Respuesta simulada de la API de Gemini.
    """
    
    def __init__(self, text):
        """
        Inicializa la respuesta simulada.
        
        Args:
            text: Texto de la respuesta
        """
        self.text = text


configure = lambda api_key=None: logger.info(f"API configurada con clave mock")
GenerativeModel = MockGenerativeModel
