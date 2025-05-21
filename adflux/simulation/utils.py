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
from typing import Dict, Any, Optional

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
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        log.error(
            "No se proporcionó clave API para Gemini y no se encontró en variables de entorno."
        )
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
    retry_delay: float = 2.0,
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
            if response_format.lower() == "json":
                generation_config["response_mime_type"] = "application/json"

            # Crear el modelo generativo
            model_instance = genai.GenerativeModel(
                model_name=model, generation_config=generation_config
            )

            # Generar respuesta
            response = model_instance.generate_content(prompt)

            # Verificar si la respuesta es válida
            if not response:
                raise ValueError("Respuesta nula de Gemini.")

            # Manejar el caso donde response.candidates está vacío
            if not hasattr(response, "candidates") or not response.candidates:
                raise ValueError("response.candidates está vacío.")

            # Acceder al texto de manera segura
            response_text = ""
            try:
                # Intentar usar el acceso rápido .text
                if hasattr(response, "text"):
                    response_text = response.text
                # Si no funciona, intentar acceder directamente a candidates y parts
                elif response.candidates and hasattr(response.candidates[0], "content"):
                    content = response.candidates[0].content
                    if hasattr(content, "parts") and content.parts:
                        for part in content.parts:
                            if hasattr(part, "text"):
                                response_text += part.text
                            elif isinstance(part, dict) and "text" in part:
                                response_text += part["text"]
                if not response_text:
                    raise ValueError("No se pudo extraer texto de la respuesta.")
            except Exception as e:
                raise ValueError(f"Error al extraer texto de la respuesta: {e}")

            # Procesar respuesta según el formato solicitado
            if response_format.lower() == "json":
                cleaned_json_text = response_text.strip()

                # More robustly strip markdown code fences
                if cleaned_json_text.startswith("```json"):
                    cleaned_json_text = cleaned_json_text[len("```json"):]
                elif cleaned_json_text.startswith("```"):
                    cleaned_json_text = cleaned_json_text[len("```"):]
                
                if cleaned_json_text.endswith("```"):
                    cleaned_json_text = cleaned_json_text[:-len("```")]
                
                cleaned_json_text = cleaned_json_text.strip()

                # Try to find the outermost JSON object or array
                first_brace = cleaned_json_text.find("{")
                last_brace = cleaned_json_text.rfind("}")
                first_bracket = cleaned_json_text.find("[")
                last_bracket = cleaned_json_text.rfind("]")

                start_idx = -1
                end_idx = -1

                # Check for object-like structure {}
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    start_idx = first_brace
                    end_idx = last_brace
                
                # Check for array-like structure [] and see if it's a better fit or primary
                if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
                    if start_idx == -1 or (first_bracket < start_idx and last_bracket > end_idx):
                        start_idx = first_bracket
                        end_idx = last_bracket
                
                if start_idx != -1 and end_idx != -1:
                    json_to_parse = cleaned_json_text[start_idx : end_idx + 1]
                else:
                    # If no clear delimiters found, fallback to the whole cleaned text
                    json_to_parse = cleaned_json_text
                
                json_to_parse = json_to_parse.strip()

                try:
                    # Attempt 1: Use raw_decode to get the first valid JSON object and its end position
                    decoder = json.JSONDecoder()
                    obj, pos = decoder.raw_decode(json_to_parse)
                    
                    remaining_text = json_to_parse[pos:].strip()
                    if remaining_text:
                        log.warning(f"Reparado: Datos adicionales encontrados después del objeto JSON principal y descartados. Resto (primeros 100 char): '{remaining_text[:100]}'")
                    return obj
                except json.JSONDecodeError as e1:
                    log.warning(f"Primer intento de parseo JSON (raw_decode) falló: {e1}. Texto problemático (primeros 100 char): '{json_to_parse[:100]}'. Intentando reparación manual...")
                    
                    # Attempt 2: Fallback to manual repair for internal syntax issues
                    repaired_text = json_to_parse # Start with the text that raw_decode failed on
                    
                    # Repair common issues like single quotes, Python booleans/None
                    repaired_text = re.sub(r"'([^']*)'\s*:", r'"\1":', repaired_text) # Single-quoted keys
                    repaired_text = re.sub(r":\s*'([^']*)'", r': "\1"', repaired_text) # Single-quoted string values
                    # Handle single-quoted strings in arrays more carefully
                    repaired_text = re.sub(r"\bTrue\b", "true", repaired_text)
                    repaired_text = re.sub(r"\bFalse\b", "false", repaired_text)
                    repaired_text = re.sub(r"\bNone\b", "null", repaired_text)
                    repaired_text = re.sub(r"\bNULL\b", "null", repaired_text) # Just in case

                    try:
                        return json.loads(repaired_text)
                    except json.JSONDecodeError as e2:
                        log.warning(f"Intento {retries+1}/{max_retries+1}: Error al decodificar JSON incluso después de reparación manual: {e2}")
                        log.debug(f"Texto original (después de strip/slice): '{json_to_parse}'")
                        log.debug(f"Texto después de reparación manual: '{repaired_text}'")
                        last_error = e2 # This will be caught by the outer loop for retry
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
