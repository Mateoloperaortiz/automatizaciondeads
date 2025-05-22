"""
Generación de datos de trabajos para AdFlux.

Este módulo contiene funciones para generar datos simulados de ofertas de trabajo
utilizando la API de Gemini.
"""

import logging
import random
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .utils import generate_with_gemini, setup_gemini_client
from faker import Faker  # Ensure faker is in requirements
fake = Faker("es_CO")

# Configurar logging
log = logging.getLogger(__name__)

SAMPLE_TITLES = [
    "Analista de Datos",
    "Desarrollador Backend",
    "Diseñador UX/UI",
    "Gerente de Proyecto",
    "Especialista en Marketing",
    "Ingeniero de Software",
    "Administrador de Sistemas",
    "Asesor Comercial",
    "Contador Público",
]

SAMPLE_COMPANIES = [
    "Bancolombia",
    "Ecopetrol",
    "Grupo Nutresa",
    "Rappi",
    "Falabella",
    "Grupo Éxito",
    "Avianca",
    "Davivienda",
]

SAMPLE_LOCATIONS = [
    "Bogotá",
    "Medellín",
    "Cali",
    "Barranquilla",
    "Cartagena",
    "Bucaramanga",
    "Pereira",
]

SAMPLE_DEPARTMENTS = [
    "Tecnología",
    "Finanzas",
    "Recursos Humanos",
    "Marketing",
    "Ventas",
    "Operaciones",
]

SAMPLE_SKILLS = [
    "Python",
    "SQL",
    "Excel Avanzado",
    "Comunicación",
    "Gestión de Proyectos",
    "JavaScript",
    "AWS",
    "Diseño Gráfico",
    "Negociación",
]

SAMPLE_BENEFITS = [
    "Seguro médico",
    "Bono de alimentación",
    "Trabajo remoto",
    "Programa de bienestar",
    "Capacitación",
]

SAMPLE_SALARY_RANGES = [
    "$3.000.000 - $4.500.000",
    "$4.500.000 - $6.000.000",
    "$6.000.000 - $8.000.000",
    "$8.000.000 - $10.000.000",
]

VALID_STATUSES = ["open", "closed", "draft"]
EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract", "Temporary", "Internship"]
EXPERIENCE_LEVELS = ["Entry-level", "Mid-level", "Senior", "Executive"]
EDUCATION_LEVELS = ["High School", "Technical", "Bachelor's", "Master's", "PhD"]


def _create_unique_job_title_for_company(original_title: str, company_name: str, existing_title_company_keys: set) -> str:
    """
    Ensures a unique title for a given company by appending a counter if needed.
    Args:
        original_title: The initial job title.
        company_name: The company name.
        existing_title_company_keys: A set of 'title|company' keys already in use.
    Returns:
        A title string that is unique for the given company in the context of existing keys.
    """
    if not original_title or not company_name:
        # Should not happen if LLM provides data, but handle defensively
        return original_title or "Default Job Title"

    current_title = original_title
    title_company_key = f"{current_title}|{company_name}".lower()
    counter = 1
    while title_company_key in existing_title_company_keys:
        current_title = f"{original_title} ({counter})"
        title_company_key = f"{current_title}|{company_name}".lower()
        counter += 1
    return current_title


def _generate_local_job(job_id: int) -> Dict[str, Any]:
    """Generate a fallback job dictionary using local random data."""
    title = random.choice(SAMPLE_TITLES)
    company = random.choice(SAMPLE_COMPANIES)
    location = random.choice(SAMPLE_LOCATIONS)
    posted_date = datetime.now() - timedelta(days=random.randint(0, 30))
    closing_date = posted_date + timedelta(days=random.randint(15, 60))

    skills_sample = random.sample(SAMPLE_SKILLS, k=min(5, len(SAMPLE_SKILLS)))

    job_data = {
        "job_id": job_id,
        "title": title,
        "company_name": company,
        "location": location,
        "description": f"Estamos buscando un {title} para unirse a nuestro equipo en {company}.",
        "requirements": skills_sample,
        "salary_range": random.choice(SAMPLE_SALARY_RANGES),
        "employment_type": random.choice(EMPLOYMENT_TYPES),
        "experience_level": random.choice(EXPERIENCE_LEVELS),
        "education_level": random.choice(EDUCATION_LEVELS),
        "application_url": f"https://example.com/jobs/{job_id}",
        "posted_date": posted_date.isoformat(),
        "closing_date": closing_date.isoformat(),
        "status": random.choice(VALID_STATUSES),
        "department": random.choice(SAMPLE_DEPARTMENTS),
        "remote": random.choice([True, False]),
        "skills": skills_sample,
        "benefits": random.sample(SAMPLE_BENEFITS, k=min(3, len(SAMPLE_BENEFITS))),
        "short_description": f"{title} en {company} ({location}).",
    }
    log.info(f"Datos de trabajo locales generados para job_id {job_id}")
    return job_data


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
    prompt = """
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
    - posted_date: fecha de publicación en formato ISO (string, dentro de los últimos 30 días)
    - closing_date: fecha de cierre en formato ISO (string, entre 15 y 60 días después de posted_date)
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
        required_keys = [
            "job_id",
            "title",
            "company_name",
            "location",
            "description",
            "requirements",
            "salary_range",
            "employment_type",
            "experience_level",
            "education_level",
            "application_url",
            "posted_date",
            "closing_date",
            "status",
            "department",
            "remote",
            "skills",
            "benefits",
            "short_description",
        ]

        if all(key in generated_data for key in required_keys):
            # Asegurar que job_id sea el proporcionado
            generated_data["job_id"] = job_id

            # Asegurar que las fechas estén en formato ISO
            try:
                # Validar posted_date
                posted_date = datetime.fromisoformat(
                    generated_data["posted_date"].replace("Z", "+00:00")
                )

                # Validar closing_date
                closing_date = datetime.fromisoformat(
                    generated_data["closing_date"].replace("Z", "+00:00")
                )

                # Verificar que closing_date sea posterior a posted_date
                if closing_date <= posted_date:
                    # Ajustar closing_date si es necesario
                    closing_date = posted_date + timedelta(days=random.randint(15, 60))
                    generated_data["closing_date"] = closing_date.isoformat()
            except (ValueError, TypeError):
                # Si hay error en las fechas, generar nuevas
                now = datetime.now()
                posted_date = now - timedelta(days=random.randint(0, 30))
                closing_date = posted_date + timedelta(days=random.randint(15, 60))
                generated_data["posted_date"] = posted_date.isoformat()
                generated_data["closing_date"] = closing_date.isoformat()

            # Asegurar que status sea uno de los valores permitidos
            valid_statuses = ["open", "closed", "draft"]
            if generated_data["status"] not in valid_statuses:
                generated_data["status"] = random.choice(valid_statuses)

            # Asegurar que remote sea booleano
            if not isinstance(generated_data["remote"], bool):
                generated_data["remote"] = str(generated_data["remote"]).lower() in [
                    "true",
                    "yes",
                    "si",
                    "1",
                ]

            log.info(f"Datos de trabajo generados correctamente para job_id {job_id}")
            return generated_data
        else:
            missing_keys = [key for key in required_keys if key not in generated_data]
            log.error(f"Datos de trabajo generados faltan claves requeridas: {missing_keys}. Usando datos locales de respaldo.")
            return _generate_local_job(job_id)
    else:
        log.error(f"Fallo al generar datos de trabajo para job_id {job_id} usando Gemini. Usando datos locales de respaldo.")
        return _generate_local_job(job_id)


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
            original_title = job_data.get("title")
            company_name = job_data.get("company_name")

            if original_title and company_name:
                # Ensure the title is unique for the company
                unique_title = _create_unique_job_title_for_company(original_title, company_name, generated_titles)
                
                # Update job_data with the potentially modified unique title
                job_data["title"] = unique_title
                
                title_company_key = f"{unique_title}|{company_name}".lower()
                
                generated_titles.add(title_company_key)
                generated_job_ids.add(job_id)
                jobs.append(job_data)
                log.info(f"Trabajo único ('{unique_title}' en '{company_name}') añadido. ID: {job_id}. Total: {len(jobs)}/{count}")
                consecutive_failures = 0  # Reset on success
            else:
                log.warning(f"Datos de trabajo generados sin título o compañía para job_id {job_id}. Descartando.")
                consecutive_failures += 1
        else:
            log.warning(f"Fallo al generar datos de trabajo para job_id {job_id}. Intento {attempts}/{max_total_attempts}")
            consecutive_failures += 1

        # Pausa si hay demasiados fallos consecutivos (posible límite de API)
        if consecutive_failures >= max_consecutive_failures:
            log.warning(
                f"Detectados {consecutive_failures} fallos consecutivos. Pausando por 5 segundos..."
            )
            time.sleep(5)
            consecutive_failures = 0

    log.info(
        f"Generación de trabajos completada: {len(jobs)}/{count} trabajos generados en {attempts} intentos."
    )
    return jobs
