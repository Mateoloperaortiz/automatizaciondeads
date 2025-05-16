"""
Generador de contenido para anuncios utilizando Google Gemini.

Este módulo proporciona funcionalidades para generar contenido creativo
para anuncios en diferentes plataformas utilizando la API de Google Gemini.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple

from .client import GeminiApiClient, get_client
from adflux.api.common.error_handling import handle_gemini_api_error
from adflux.api.common.excepciones import AdFluxError

logger = logging.getLogger("GeminiContentGenerator")

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 2048
DEFAULT_TOP_P = 0.95

PLATFORM_TEMPLATES = {
    "meta": {
        "max_title_length": 40,
        "max_description_length": 125,
        "formats": ["imagen_única", "carrusel", "video"],
        "aspect_ratios": ["1:1", "4:5", "16:9"],
    },
    "google": {
        "max_title_length": 30,
        "max_description_length": 90,
        "formats": ["texto", "responsive", "imagen"],
        "aspect_ratios": ["1:1", "4:3", "16:9"],
    },
    "tiktok": {
        "max_title_length": 100,
        "max_description_length": 100,
        "formats": ["video", "imagen"],
        "aspect_ratios": ["9:16", "1:1"],
    },
    "snapchat": {
        "max_title_length": 34,
        "max_description_length": 150,
        "formats": ["video", "imagen", "colección"],
        "aspect_ratios": ["9:16", "1:1"],
    }
}


class ContentGenerator:
    """
    Generador de contenido para anuncios utilizando Google Gemini.
    """

    def __init__(self, client: Optional[GeminiApiClient] = None):
        """
        Inicializa el generador de contenido.

        Args:
            client: Cliente de la API de Google Gemini. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()
        self.model = "models/gemini-2.5-pro-exp-03-25"  # Modelo por defecto

    def ensure_client_initialized(self):
        """
        Asegura que el cliente de la API esté inicializado.
        """
        if not hasattr(self.client, "ensure_initialized"):
            raise AdFluxError("Cliente de Gemini no válido", codigo=500)
        self.client.ensure_initialized()

    @handle_gemini_api_error
    def generate_ad_content(
        self,
        job_data: Dict[str, Any],
        platform: str,
        segment_data: Optional[Dict[str, Any]] = None,
        format_type: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera contenido para anuncios basado en datos de trabajo y segmento.

        Args:
            job_data: Datos de la oferta de trabajo
            platform: Plataforma para la que se genera el contenido (meta, google, tiktok, snapchat)
            segment_data: Datos del segmento objetivo (opcional)
            format_type: Tipo de formato (imagen_única, carrusel, video, etc.)
            temperature: Temperatura para la generación (0.0 - 1.0)

        Returns:
            Tupla con (éxito, mensaje, contenido generado)
        """
        self.ensure_client_initialized()

        platform = platform.lower()

        if platform not in PLATFORM_TEMPLATES:
            return False, f"Plataforma '{platform}' no soportada", {}

        platform_config = PLATFORM_TEMPLATES[platform]

        if not format_type:
            format_type = platform_config["formats"][0]
        elif format_type not in platform_config["formats"]:
            return False, f"Formato '{format_type}' no soportado para la plataforma '{platform}'", {}

        prompt = self._build_ad_content_prompt(job_data, platform, segment_data, format_type)

        try:
            try:
                import os
                if os.getenv("USE_MOCK_CLIENT", "False").lower() in ("true", "1", "yes"):
                    import adflux.api.gemini.mock_google_generativeai as genai
                    logger.info("Usando módulo mock de google.generativeai")
                else:
                    import google.generativeai as genai
            except ImportError:
                import adflux.api.gemini.mock_google_generativeai as genai
                logger.info("Usando módulo mock de google.generativeai (fallback)")
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": DEFAULT_MAX_OUTPUT_TOKENS,
                "top_p": DEFAULT_TOP_P,
                "response_mime_type": "application/json",
            }
            
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=generation_config
            )
            
            response = model.generate_content(prompt)
            
            if not response or not hasattr(response, "text"):
                return False, "No se pudo generar contenido", {}
            
            try:
                content = json.loads(response.text)
                
                if not isinstance(content, dict):
                    return False, "Formato de respuesta inválido", {}
                
                if self._validate_ad_content(content, platform, format_type):
                    return True, "Contenido generado exitosamente", content
                else:
                    return False, "Contenido generado no cumple con los requisitos de la plataforma", content
                
            except json.JSONDecodeError:
                return False, "No se pudo parsear la respuesta como JSON", {"raw_text": response.text}
                
        except Exception as e:
            logger.error(f"Error al generar contenido: {e}")
            return False, f"Error al generar contenido: {str(e)}", {}

    def _build_ad_content_prompt(
        self,
        job_data: Dict[str, Any],
        platform: str,
        segment_data: Optional[Dict[str, Any]] = None,
        format_type: Optional[str] = None,
    ) -> str:
        """
        Construye el prompt para generar contenido de anuncios.

        Args:
            job_data: Datos de la oferta de trabajo
            platform: Plataforma para la que se genera el contenido
            segment_data: Datos del segmento objetivo (opcional)
            format_type: Tipo de formato

        Returns:
            Prompt para Gemini
        """
        platform_config = PLATFORM_TEMPLATES[platform]
        
        job_title = job_data.get("title", "")
        job_description = job_data.get("description", "")
        job_requirements = job_data.get("requirements", "")
        job_location = job_data.get("location", "")
        job_salary = job_data.get("salary", "")
        job_company = job_data.get("company", "")
        
        segment_info = ""
        if segment_data:
            segment_info = f"""
            Información del segmento objetivo:
            - ID del segmento: {segment_data.get('segment_id', 'No disponible')}
            - Tamaño del segmento: {segment_data.get('count', 'No disponible')} candidatos
            - Años de experiencia promedio: {segment_data.get('avg_experience', 'No disponible')}
            - Nivel educativo predominante: {segment_data.get('education_level', 'No disponible')}
            - Habilidades principales: {', '.join(segment_data.get('skills', ['No disponible']))}
            - Rango salarial deseado: {segment_data.get('salary_range', 'No disponible')}
            """
        
        prompt = f"""
        Eres un experto en marketing digital y creación de anuncios para la plataforma {platform.upper()}.
        
        Necesito que generes contenido creativo para un anuncio de empleo con las siguientes características:
        
        INFORMACIÓN DEL EMPLEO:
        - Título: {job_title}
        - Empresa: {job_company}
        - Ubicación: {job_location}
        - Salario: {job_salary}
        - Descripción: {job_description}
        - Requisitos: {job_requirements}
        
        {segment_info}
        
        ESPECIFICACIONES DE LA PLATAFORMA {platform.upper()}:
        - Formato del anuncio: {format_type}
        - Longitud máxima del título: {platform_config['max_title_length']} caracteres
        - Longitud máxima de la descripción: {platform_config['max_description_length']} caracteres
        - Relaciones de aspecto disponibles: {', '.join(platform_config['aspect_ratios'])}
        
        INSTRUCCIONES ESPECÍFICAS:
        """
        
        if platform == "meta":
            prompt += """
            - Crea un título atractivo que genere interés inmediato
            - La descripción debe ser concisa y destacar los beneficios principales
            - Incluye un llamado a la acción claro y directo
            - Sugiere una imagen o video que complemente el mensaje
            - Incluye 3-5 hashtags relevantes para aumentar el alcance
            """
        elif platform == "google":
            prompt += """
            - El título debe incluir palabras clave relevantes para SEO
            - La descripción debe ser directa y enfocada en los beneficios
            - Incluye al menos 2 llamados a la acción diferentes
            - Sugiere palabras clave adicionales para la campaña
            """
        elif platform == "tiktok":
            prompt += """
            - Crea un título llamativo y juvenil que capte la atención
            - La descripción debe ser informal y usar lenguaje actual
            - Sugiere un concepto de video breve y dinámico
            - Incluye 3-5 hashtags de tendencia relevantes
            - Propón una música o sonido que podría acompañar el anuncio
            """
        elif platform == "snapchat":
            prompt += """
            - El título debe ser ultra conciso y llamativo
            - La descripción debe ser juvenil y usar emojis estratégicamente
            - Sugiere un concepto visual interactivo
            - Incluye un llamado a la acción que genere interacción
            """
        
        prompt += f"""
        
        FORMATO DE RESPUESTA:
        Devuelve tu respuesta en formato JSON con la siguiente estructura:
        
        {{
            "title": "Título del anuncio (máximo {platform_config['max_title_length']} caracteres)",
            "description": "Descripción del anuncio (máximo {platform_config['max_description_length']} caracteres)",
            "cta": "Llamado a la acción principal",
            "visual_concept": "Descripción detallada del concepto visual para el anuncio",
            "hashtags": ["hashtag1", "hashtag2", ...],
            "keywords": ["keyword1", "keyword2", ...],
            "additional_elements": {{
                // Elementos adicionales específicos de la plataforma
            }}
        }}
        
        Asegúrate de que el contenido sea original, atractivo y optimizado para la plataforma {platform.upper()}.
        """
        
        return prompt

    def _validate_ad_content(
        self, content: Dict[str, Any], platform: str, format_type: Optional[str] = None
    ) -> bool:
        """
        Valida que el contenido generado cumpla con los requisitos de la plataforma.

        Args:
            content: Contenido generado
            platform: Plataforma para la que se generó el contenido
            format_type: Tipo de formato (opcional)

        Returns:
            True si el contenido es válido, False en caso contrario
        """
        platform_config = PLATFORM_TEMPLATES[platform]
        
        required_fields = ["title", "description", "cta"]
        for field in required_fields:
            if field not in content:
                logger.warning(f"Campo requerido '{field}' no presente en el contenido generado")
                return False
        
        if len(content.get("title", "")) > platform_config["max_title_length"]:
            logger.warning(f"Título excede la longitud máxima para {platform}")
            return False
            
        if len(content.get("description", "")) > platform_config["max_description_length"]:
            logger.warning(f"Descripción excede la longitud máxima para {platform}")
            return False
        
        if platform == "meta" and "hashtags" not in content:
            logger.warning("Faltan hashtags para anuncio de Meta")
            return False
            
        if platform == "google" and "keywords" not in content:
            logger.warning("Faltan keywords para anuncio de Google")
            return False
        
        return True

    @handle_gemini_api_error
    def generate_ad_variations(
        self,
        base_content: Dict[str, Any],
        platform: str,
        num_variations: int = 3,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Genera variaciones de un anuncio base.

        Args:
            base_content: Contenido base del anuncio
            platform: Plataforma para la que se generan las variaciones
            num_variations: Número de variaciones a generar
            temperature: Temperatura para la generación (0.0 - 1.0)

        Returns:
            Tupla con (éxito, mensaje, lista de variaciones)
        """
        self.ensure_client_initialized()
        
        platform = platform.lower()
        
        if platform not in PLATFORM_TEMPLATES:
            return False, f"Plataforma '{platform}' no soportada", []
        
        prompt = self._build_variations_prompt(base_content, platform, num_variations)
        
        try:
            try:
                import os
                if os.getenv("USE_MOCK_CLIENT", "False").lower() in ("true", "1", "yes"):
                    import adflux.api.gemini.mock_google_generativeai as genai
                    logger.info("Usando módulo mock de google.generativeai para variaciones")
                else:
                    import google.generativeai as genai
            except ImportError:
                import adflux.api.gemini.mock_google_generativeai as genai
                logger.info("Usando módulo mock de google.generativeai para variaciones (fallback)")
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": DEFAULT_MAX_OUTPUT_TOKENS * 2,  # Mayor para múltiples variaciones
                "top_p": DEFAULT_TOP_P,
                "response_mime_type": "application/json",
            }
            
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=generation_config
            )
            
            response = model.generate_content(prompt)
            
            if not response or not hasattr(response, "text"):
                return False, "No se pudo generar variaciones", []
            
            try:
                variations_data = json.loads(response.text)
                
                if not isinstance(variations_data, dict) or "variations" not in variations_data:
                    return False, "Formato de respuesta inválido", []
                
                variations = variations_data.get("variations", [])
                
                valid_variations = []
                for variation in variations:
                    if self._validate_ad_content(variation, platform, base_content.get("format_type", "")):
                        valid_variations.append(variation)
                
                if not valid_variations:
                    return False, "Ninguna variación generada cumple con los requisitos", []
                
                return True, f"Se generaron {len(valid_variations)} variaciones válidas", valid_variations
                
            except json.JSONDecodeError:
                return False, "No se pudo parsear la respuesta como JSON", []
                
        except Exception as e:
            logger.error(f"Error al generar variaciones: {e}")
            return False, f"Error al generar variaciones: {str(e)}", []

    def _build_variations_prompt(
        self, base_content: Dict[str, Any], platform: str, num_variations: int
    ) -> str:
        """
        Construye el prompt para generar variaciones de anuncios.

        Args:
            base_content: Contenido base del anuncio
            platform: Plataforma para la que se generan las variaciones
            num_variations: Número de variaciones a generar

        Returns:
            Prompt para Gemini
        """
        platform_config = PLATFORM_TEMPLATES[platform]
        
        title = base_content.get("title", "")
        description = base_content.get("description", "")
        cta = base_content.get("cta", "")
        
        prompt = f"""
        Eres un experto en marketing digital y creación de anuncios para la plataforma {platform.upper()}.
        
        Necesito que generes {num_variations} variaciones del siguiente anuncio base:
        
        ANUNCIO BASE:
        - Título: {title}
        - Descripción: {description}
        - Llamado a la acción: {cta}
        
        ESPECIFICACIONES DE LA PLATAFORMA {platform.upper()}:
        - Longitud máxima del título: {platform_config['max_title_length']} caracteres
        - Longitud máxima de la descripción: {platform_config['max_description_length']} caracteres
        
        INSTRUCCIONES:
        - Genera {num_variations} variaciones diferentes del anuncio
        - Cada variación debe mantener el mismo mensaje central pero con enfoque diferente
        - Experimenta con diferentes tonos, estilos y llamados a la acción
        - Asegúrate de que cada variación cumpla con las restricciones de longitud
        - Mantén la esencia del anuncio original pero hazlo único
        
        FORMATO DE RESPUESTA:
        Devuelve tu respuesta en formato JSON con la siguiente estructura:
        
        {{
            "variations": [
                {{
                    "title": "Título de la variación 1",
                    "description": "Descripción de la variación 1",
                    "cta": "Llamado a la acción de la variación 1",
                    "visual_concept": "Concepto visual para la variación 1",
                    "hashtags": ["hashtag1", "hashtag2", ...],
                    "keywords": ["keyword1", "keyword2", ...],
                    "additional_elements": {{
                        // Elementos adicionales específicos de la plataforma
                    }}
                }},
                // Repetir para cada variación
            ]
        }}
        
        Asegúrate de que cada variación sea única, atractiva y optimizada para la plataforma {platform.upper()}.
        """
        
        return prompt


_default_generator = None


def get_content_generator(client: Optional[GeminiApiClient] = None) -> ContentGenerator:
    """
    Obtiene una instancia del generador de contenido.

    Si se proporciona un cliente, se crea un nuevo generador con ese cliente.
    Si no, se devuelve el generador por defecto (creándolo si es necesario).

    Args:
        client: Cliente de la API de Google Gemini.

    Returns:
        Una instancia de ContentGenerator.
    """
    global _default_generator

    if client:
        return ContentGenerator(client)

    if _default_generator is None:
        _default_generator = ContentGenerator()

    return _default_generator
