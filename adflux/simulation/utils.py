"""
Utilidades para la simulación de datos en AdFlux.

Este módulo contiene funciones auxiliares para la simulación de datos,
incluyendo la configuración del cliente de Gemini y funciones para
generar datos con la API de Gemini.
"""

import os
import json
import logging
import time
import re
import google.generativeai as genai
from typing import Dict, Any, Optional, List, Union

# Configurar logging
log = logging.getLogger(__name__)

# Constantes
DEFAULT_MODEL = "models/gemini-2.0-flash"  # Modelo más estable de Gemini
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_OUTPUT_TOKENS = 8192
DEFAULT_TOP_P = 0.95  # Parámetro top_p para muestreo de núcleos


def setup_gemini_client(api_key: Optional[str] = None) -> bool:
    """
    Configura el cliente de Gemini con la clave API proporcionada o desde variables de entorno.

    Args:
        api_key: Clave API de Gemini. Si es None, se intenta obtener de la variable de entorno GEMINI_API_KEY.

    Returns:
        bool: True si la configuración fue exitosa, False en caso contrario.
    """
    # Intentar obtener la clave API de la variable de entorno si no se proporciona
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        log.error("No se proporcionó clave API para Gemini y no se encontró en variables de entorno.")
        return False

    try:
        # Configurar la API de Gemini
        genai.configure(api_key=api_key)
        log.info("Cliente de Gemini configurado exitosamente.")
        return True
    except Exception as e:
        log.error(f"Error al configurar cliente de Gemini: {e}")
        return False


def generate_with_gemini(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    top_p: float = DEFAULT_TOP_P,
    response_format: str = "json",
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> Optional[Dict[str, Any]]:
    """
    Genera datos utilizando la API de Gemini con reintentos automáticos.

    Args:
        prompt: Prompt para la generación.
        model: Modelo de Gemini a utilizar.
        temperature: Temperatura para la generación (0.0 - 1.0).
        max_output_tokens: Número máximo de tokens a generar.
        top_p: Parámetro de muestreo de núcleos (0.0 - 1.0).
        response_format: Formato de respuesta esperado ('json' o 'text').
        max_retries: Número máximo de reintentos en caso de error.
        retry_delay: Tiempo de espera entre reintentos en segundos.

    Returns:
        Dict o None: Datos generados como diccionario si response_format es 'json',
                    o el texto generado si response_format es 'text'.
                    None si ocurre un error después de todos los reintentos.
    """
    retries = 0
    last_error = None

    while retries <= max_retries:
        try:
            # Crear modelo generativo con configuración específica para JSON
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "top_p": top_p,  # Parámetro de muestreo de núcleos
            }

            # Si queremos JSON, configurar el modelo para responder en formato JSON
            if response_format.lower() == 'json':
                generation_config["response_mime_type"] = "application/json"

            # Crear el modelo generativo
            model_instance = genai.GenerativeModel(model_name=model, generation_config=generation_config)

            # Generar respuesta
            response = model_instance.generate_content(prompt)

            # Verificar si la respuesta es válida
            if not response:
                raise ValueError("Respuesta nula de Gemini.")

            # Manejar el caso donde response.candidates está vacío
            if not hasattr(response, 'candidates') or not response.candidates:
                raise ValueError("response.candidates está vacío.")

            # Acceder al texto de manera segura
            response_text = ""
            try:
                # Intentar usar el acceso rápido .text
                if hasattr(response, 'text'):
                    response_text = response.text
                # Si no funciona, intentar acceder directamente a candidates y parts
                elif response.candidates and hasattr(response.candidates[0], 'content'):
                    content = response.candidates[0].content
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'text'):
                                response_text += part.text
                            elif isinstance(part, dict) and 'text' in part:
                                response_text += part['text']
                if not response_text:
                    raise ValueError("No se pudo extraer texto de la respuesta.")
            except Exception as e:
                raise ValueError(f"Error al extraer texto de la respuesta: {e}")

            # Procesar respuesta según el formato solicitado
            if response_format.lower() == 'json':
                try:
                    # Intentar parsear como JSON
                    json_text = response_text.strip()

                    # Eliminar comillas de código si están presentes
                    if json_text.startswith('```json'):
                        json_text = json_text.replace('```json', '', 1)
                    elif json_text.startswith('```'):
                        json_text = json_text.replace('```', '', 1)
                    if json_text.endswith('```'):
                        json_text = json_text.replace('```', '', 1)

                    # Eliminar cualquier texto antes o después del JSON
                    # Buscar el primer '{' y el último '}'
                    start_idx = json_text.find('{')
                    end_idx = json_text.rfind('}')

                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_text = json_text[start_idx:end_idx+1]

                    json_text = json_text.strip()

                    # Intentar cargar el JSON
                    try:
                        return json.loads(json_text)
                    except json.JSONDecodeError as e1:
                        # Si falla, intentar reparar problemas comunes de formato
                        log.warning(f"Primer intento de parseo JSON falló: {e1}. Intentando reparar...")

                        # Reemplazar comillas simples por comillas dobles en claves y valores
                        # Reemplazar comillas simples en claves
                        json_text = re.sub(r"'([^']+)'\s*:", r'"\1":', json_text)
                        # Reemplazar comillas simples en valores string
                        json_text = re.sub(r":\s*'([^']*)'([,}])", r':"\1"\2', json_text)

                        # Asegurar que los valores booleanos estén en minúsculas
                        json_text = json_text.replace('True', 'true').replace('False', 'false')

                        # Asegurar que null esté en minúsculas
                        json_text = json_text.replace('None', 'null').replace('NULL', 'null')

                        # Intentar cargar el JSON reparado
                        return json.loads(json_text)
                except json.JSONDecodeError as e:
                    log.warning(f"Intento {retries+1}/{max_retries+1}: Error al decodificar JSON: {e}")
                    log.debug(f"Texto recibido: {response_text}")
                    last_error = e
            else:
                # Devolver texto sin procesar
                return response_text

        except Exception as e:
            log.warning(f"Intento {retries+1}/{max_retries+1}: Error al generar con Gemini: {e}")
            last_error = e

        # Incrementar contador de reintentos
        retries += 1

        # Si aún tenemos reintentos disponibles, esperar antes de reintentar
        if retries <= max_retries:
            log.info(f"Esperando {retry_delay} segundos antes de reintentar...")
            time.sleep(retry_delay)
            # Aumentar ligeramente la temperatura en cada reintento para variar la salida
            temperature = min(temperature + 0.1, 1.0)

    # Si llegamos aquí, todos los intentos fallaron
    log.error(f"Todos los intentos fallaron. Último error: {last_error}")
    return None
