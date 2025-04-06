"""
Generación de contenido con la API de Google Gemini.

Este módulo proporciona funcionalidades para generar contenido creativo
para anuncios utilizando la API de Google Gemini.
"""

from typing import Tuple, Dict, Any, Optional, List

# Intentar importar Google Generative AI SDK, pero no fallar si no está disponible
try:
    import google.generativeai as genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_SDK_AVAILABLE = False

from adflux.api.common.error_handling import handle_gemini_api_error
from adflux.api.common.logging import get_logger
from adflux.api.gemini.client import get_client, GeminiApiClient

# Configurar logger
logger = get_logger("GeminiContent")


class ContentGenerator:
    """
    Generador de contenido utilizando la API de Google Gemini.
    """

    def __init__(self, client: Optional[GeminiApiClient] = None, model_name: Optional[str] = None):
        """
        Inicializa el generador de contenido.

        Args:
            client: Cliente de la API de Google Gemini. Si es None, se usa el cliente por defecto.
            model_name: Nombre del modelo a utilizar. Si es None, se usa 'gemini-1.5-pro'.
        """
        self.client = client or get_client()
        self.model_name = model_name or 'gemini-1.5-pro'

    @handle_gemini_api_error
    def generate_ad_creative(
        self,
        job_title: str,
        job_description: str,
        target_audience: str = "general job seekers",
        temperature: float = 0.7,
        max_output_tokens: int = 800
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera texto creativo para anuncios de trabajo utilizando Gemini.

        Args:
            job_title: Título del trabajo.
            job_description: Descripción del trabajo.
            target_audience: Audiencia objetivo para el anuncio.
            temperature: Temperatura para la generación (0.0 a 1.0).
            max_output_tokens: Número máximo de tokens en la salida.

        Returns:
            Una tupla con: (éxito, mensaje, datos generados).
        """
        if not self.client.ensure_initialized():
            return False, "No se pudo inicializar la API de Google Gemini", {}

        try:
            # Crear el modelo
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                    "top_p": 0.95,
                    "top_k": 40
                }
            )

            # Crear el prompt
            prompt = f"""
            Eres un experto en marketing digital especializado en anuncios para ofertas de trabajo.

            Necesito crear contenido para un anuncio de trabajo con el siguiente título: "{job_title}".

            Descripción del trabajo:
            {job_description}

            Audiencia objetivo: {target_audience}

            Por favor, genera el siguiente contenido para el anuncio:
            1. Un título principal atractivo (máximo 30 caracteres)
            2. Un título secundario que complemente al principal (máximo 30 caracteres)
            3. Una descripción principal que destaque los beneficios del puesto (máximo 90 caracteres)
            4. Una descripción secundaria con más detalles (máximo 90 caracteres)
            5. Un llamado a la acción efectivo (máximo 15 caracteres)

            Formatea tu respuesta como un objeto JSON con las siguientes claves:
            - primary_headline
            - secondary_headline
            - primary_description
            - secondary_description
            - call_to_action

            Asegúrate de que cada texto sea conciso, atractivo y respete los límites de caracteres indicados.
            """

            # Generar respuesta
            response = model.generate_content(prompt)

            # Procesar respuesta
            if hasattr(response, 'text'):
                response_text = response.text

                # Intentar extraer JSON de la respuesta
                import json
                import re

                # Buscar contenido JSON en la respuesta
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text

                # Limpiar el string para asegurar que sea JSON válido
                json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
                json_str = json_str.strip()

                try:
                    creative_data = json.loads(json_str)

                    # Validar que tenga todas las claves necesarias
                    required_keys = ['primary_headline', 'secondary_headline', 'primary_description',
                                    'secondary_description', 'call_to_action']

                    for key in required_keys:
                        if key not in creative_data:
                            creative_data[key] = ""

                    logger.info(f"Se generó contenido creativo para el trabajo '{job_title}'.")
                    return True, "Se generó contenido creativo exitosamente.", creative_data

                except json.JSONDecodeError:
                    # Si no se puede decodificar como JSON, devolver el texto completo
                    logger.warning(f"No se pudo decodificar la respuesta como JSON. Devolviendo texto completo.")
                    return True, "Se generó contenido, pero no en formato JSON.", {
                        "raw_text": response_text,
                        "primary_headline": "",
                        "secondary_headline": "",
                        "primary_description": "",
                        "secondary_description": "",
                        "call_to_action": ""
                    }
            else:
                return False, "La respuesta no contiene texto.", {}

        except Exception as e:
            logger.error(f"Error al generar contenido creativo: {e}", e)
            return False, f"Error al generar contenido creativo: {str(e)}", {}

    @handle_gemini_api_error
    def generate_job_description(
        self,
        job_title: str,
        skills: List[str],
        experience_years: int,
        company_description: str,
        temperature: float = 0.7
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera una descripción de trabajo utilizando Gemini.

        Args:
            job_title: Título del trabajo.
            skills: Lista de habilidades requeridas.
            experience_years: Años de experiencia requeridos.
            company_description: Descripción de la empresa.
            temperature: Temperatura para la generación (0.0 a 1.0).

        Returns:
            Una tupla con: (éxito, mensaje, datos generados).
        """
        if not self.client.ensure_initialized():
            return False, "No se pudo inicializar la API de Google Gemini", {}

        try:
            # Crear el modelo
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 1000,
                    "top_p": 0.95,
                    "top_k": 40
                }
            )

            # Crear el prompt
            skills_text = ", ".join(skills)
            prompt = f"""
            Eres un especialista en recursos humanos con experiencia en redacción de descripciones de trabajo.

            Necesito crear una descripción de trabajo para el puesto de "{job_title}".

            Detalles:
            - Habilidades requeridas: {skills_text}
            - Años de experiencia: {experience_years}
            - Sobre la empresa: {company_description}

            Por favor, genera una descripción de trabajo completa que incluya:
            1. Resumen del puesto
            2. Responsabilidades principales
            3. Requisitos y calificaciones
            4. Beneficios y oportunidades

            Formatea tu respuesta como un objeto JSON con las siguientes claves:
            - summary
            - responsibilities (array de strings)
            - requirements (array de strings)
            - benefits (array de strings)
            """

            # Generar respuesta
            response = model.generate_content(prompt)

            # Procesar respuesta
            if hasattr(response, 'text'):
                response_text = response.text

                # Intentar extraer JSON de la respuesta
                import json
                import re

                # Buscar contenido JSON en la respuesta
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text

                # Limpiar el string para asegurar que sea JSON válido
                json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
                json_str = json_str.strip()

                try:
                    job_data = json.loads(json_str)

                    # Validar que tenga todas las claves necesarias
                    required_keys = ['summary', 'responsibilities', 'requirements', 'benefits']

                    for key in required_keys:
                        if key not in job_data:
                            if key in ['responsibilities', 'requirements', 'benefits']:
                                job_data[key] = []
                            else:
                                job_data[key] = ""

                    logger.info(f"Se generó descripción para el trabajo '{job_title}'.")
                    return True, "Se generó descripción de trabajo exitosamente.", job_data

                except json.JSONDecodeError:
                    # Si no se puede decodificar como JSON, devolver el texto completo
                    logger.warning(f"No se pudo decodificar la respuesta como JSON. Devolviendo texto completo.")
                    return True, "Se generó contenido, pero no en formato JSON.", {
                        "raw_text": response_text,
                        "summary": "",
                        "responsibilities": [],
                        "requirements": [],
                        "benefits": []
                    }
            else:
                return False, "La respuesta no contiene texto.", {}

        except Exception as e:
            logger.error(f"Error al generar descripción de trabajo: {e}", e)
            return False, f"Error al generar descripción de trabajo: {str(e)}", {}


# Crear una instancia del generador por defecto
_default_generator = None


def get_content_generator(client: Optional[GeminiApiClient] = None, model_name: Optional[str] = None) -> ContentGenerator:
    """
    Obtiene una instancia del generador de contenido.

    Args:
        client: Cliente de la API de Google Gemini. Si es None, se usa el cliente por defecto.
        model_name: Nombre del modelo a utilizar. Si es None, se usa 'gemini-1.5-pro'.

    Returns:
        Una instancia de ContentGenerator.
    """
    global _default_generator

    if client or model_name:
        return ContentGenerator(client, model_name)

    if _default_generator is None:
        _default_generator = ContentGenerator()

    return _default_generator
