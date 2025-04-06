"""
Generación de datos de trabajos para AdFlux.

Este módulo contiene funciones para generar datos simulados de ofertas de trabajo
utilizando la API de Gemini.
"""

import logging
import random
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .utils import generate_with_gemini, setup_gemini_client

# Configurar logging
log = logging.getLogger(__name__)


def generate_job_opening(job_id: int) -> Optional[Dict[str, Any]]:
    """
    Genera datos simulados para una oferta de trabajo utilizando Gemini.

    Args:
        job_id: ID único para la oferta de trabajo.

    Returns:
        Dict o None: Datos de la oferta de trabajo como diccionario, o None si ocurre un error.
    """
    # Asegurar que el cliente de Gemini esté configurado
    if not setup_gemini_client():
        log.error("No se pudo configurar el cliente de Gemini para generar datos de trabajo.")
        return None

    # Prompt para Gemini
    prompt = f"""
    Eres un asistente especializado en recursos humanos. Tu tarea es generar datos realistas para una oferta de trabajo en Colombia.

    Genera un objeto JSON con los siguientes campos:
    - job_id: {job_id} (entero)
    - title: título del puesto (string)
    - company_name: nombre de una empresa colombiana real (string)
    - location: ciudad en Colombia (string)
    - description: descripción detallada del puesto (string)
    - requirements: lista de requisitos (array de strings)
    - salary_range: rango salarial en pesos colombianos (string)
    - employment_type: tipo de empleo (string: "Full-time", "Part-time", "Contract", "Temporary", "Internship")
    - experience_level: nivel de experiencia requerido (string: "Entry-level", "Mid-level", "Senior", "Executive")
    - education_level: nivel educativo requerido (string: "High School", "Technical", "Bachelor's", "Master's", "PhD")
    - application_url: URL ficticia para aplicar (string)
    - posting_date: fecha de publicación en formato ISO (string, dentro de los últimos 30 días)
    - closing_date: fecha de cierre en formato ISO (string, entre 15 y 60 días después de posting_date)
    - status: estado de la oferta (string: "open", "closed", "draft")
    - department: departamento de la empresa (string)
    - remote: si es trabajo remoto (boolean)
    - skills: lista de habilidades requeridas (array de strings)
    - benefits: lista de beneficios (array de strings)
    - short_description: descripción corta para anuncios (string, máximo 150 caracteres)

    IMPORTANTE: Asegúrate de que el JSON sea válido. Usa comillas dobles para todas las claves y valores de texto. Los valores booleanos deben ser true o false (sin comillas). Responde SOLO con el objeto JSON, sin texto adicional ni explicaciones. No uses comillas triples ni marcadores de código.
    """

    # Generar datos con Gemini
    generated_data = generate_with_gemini(prompt)

    if generated_data:
        # Verificar que se hayan generado todos los campos requeridos
        required_keys = ['job_id', 'title', 'company_name', 'location', 'description', 'requirements',
                         'salary_range', 'employment_type', 'experience_level', 'education_level',
                         'application_url', 'posting_date', 'closing_date', 'status', 'department',
                         'remote', 'skills', 'benefits', 'short_description']

        if all(key in generated_data for key in required_keys):
            # Asegurar que job_id sea el proporcionado
            generated_data['job_id'] = job_id

            # Asegurar que las fechas estén en formato ISO
            try:
                # Validar posting_date
                posting_date = datetime.fromisoformat(generated_data['posting_date'].replace('Z', '+00:00'))

                # Validar closing_date
                closing_date = datetime.fromisoformat(generated_data['closing_date'].replace('Z', '+00:00'))

                # Verificar que closing_date sea posterior a posting_date
                if closing_date <= posting_date:
                    # Ajustar closing_date si es necesario
                    closing_date = posting_date + timedelta(days=random.randint(15, 60))
                    generated_data['closing_date'] = closing_date.isoformat()
            except (ValueError, TypeError):
                # Si hay error en las fechas, generar nuevas
                now = datetime.now()
                posting_date = now - timedelta(days=random.randint(0, 30))
                closing_date = posting_date + timedelta(days=random.randint(15, 60))
                generated_data['posting_date'] = posting_date.isoformat()
                generated_data['closing_date'] = closing_date.isoformat()

            # Asegurar que status sea uno de los valores permitidos
            valid_statuses = ['open', 'closed', 'draft']
            if generated_data['status'] not in valid_statuses:
                generated_data['status'] = random.choice(valid_statuses)

            # Asegurar que remote sea booleano
            if not isinstance(generated_data['remote'], bool):
                generated_data['remote'] = str(generated_data['remote']).lower() in ['true', 'yes', 'si', '1']

            log.info(f"Datos de trabajo generados correctamente para job_id {job_id}")
            return generated_data
        else:
            missing_keys = [key for key in required_keys if key not in generated_data]
            log.error(f"Datos de trabajo generados faltan claves requeridas: {missing_keys}")
            return None
    else:
        log.error(f"Fallo al generar datos de trabajo para job_id {job_id} usando Gemini.")
        return None


def generate_multiple_jobs(count: int = 10) -> List[Dict[str, Any]]:
    """
    Genera una lista de ofertas de trabajo simuladas usando Gemini, asegurando títulos únicos.

    Args:
        count: Número de ofertas de trabajo a generar.

    Returns:
        List: Lista de diccionarios, cada uno representando una oferta de trabajo.
    """
    jobs = []
    generated_titles = set()
    generated_job_ids = set()
    attempts = 0
    max_total_attempts = count * 5  # Aumentar reintentos para asegurar suficientes trabajos únicos
    max_consecutive_failures = 10  # Máximo de fallos consecutivos antes de pausar
    consecutive_failures = 0

    log.info(f"Intentando generar {count} ofertas de trabajo únicas...")

    while len(jobs) < count and attempts < max_total_attempts:
        attempts += 1
        job_id = len(jobs) + 1 + (attempts - len(jobs))  # Usar índice progresivo para ID único

        # Evitar IDs duplicados
        while job_id in generated_job_ids:
            job_id += 1

        job_data = generate_job_opening(job_id)

        if job_data:
            title = job_data.get('title')
            company = job_data.get('company_name')

            # Verificar unicidad del título y compañía combinados
            title_company_key = f"{title}|{company}".lower() if title and company else None

            if title_company_key and title_company_key not in generated_titles:
                generated_titles.add(title_company_key)
                generated_job_ids.add(job_id)
                jobs.append(job_data)
                log.debug(f"Trabajo único añadido: {title} en {company} ({len(jobs)}/{count})")
                consecutive_failures = 0  # Reiniciar contador de fallos
            elif title_company_key:
                log.warning(f"Combinación de título y compañía duplicada generada y descartada: '{title}' en '{company}'")
                consecutive_failures += 1
            else:
                log.warning(f"Datos de trabajo generados sin título o compañía, descartados.")
                consecutive_failures += 1
        else:
            log.warning(f"Fallo la generación de trabajo en el intento {attempts}.")
            consecutive_failures += 1

        # Pausa si hay demasiados fallos consecutivos (posible límite de API)
        if consecutive_failures >= max_consecutive_failures:
            log.warning(f"Detectados {consecutive_failures} fallos consecutivos. Pausando por 5 segundos...")
            time.sleep(5)
            consecutive_failures = 0

    log.info(f"Generación de trabajos completada: {len(jobs)}/{count} trabajos generados en {attempts} intentos.")
    return jobs
