"""
Generación de datos de candidatos para AdFlux.

Este módulo contiene funciones para generar datos simulados de perfiles de candidatos
utilizando la API de Gemini.
"""

import logging
import random
import time
import re # Added for email generation
from typing import Dict, Any, Optional, List
from faker import Faker  # Local fallback data
fake = Faker("es_CO")
from .utils import generate_with_gemini, setup_gemini_client

# Configurar logging
log = logging.getLogger(__name__)

# Sample data for fallback
SAMPLE_EDUCATION = ["High School", "Technical", "Bachelor's", "Master's", "PhD"]
SAMPLE_AVAILABILITY = ["Immediate", "2 weeks", "1 month", "Negotiable"]
SAMPLE_SKILLS = [
    "Python",
    "SQL",
    "Excel",
    "Comunicación",
    "Trabajo en Equipo",
    "Java",
    "AWS",
    "Marketing",
    "Diseño Gráfico",
    "Project Management",
]

def _create_unique_email(full_name: str, existing_emails: set) -> str:
    """
    Generates a unique email address based on the full name.
    Args:
        full_name: The full name of the candidate.
        existing_emails: A set of email addresses already in use.
    Returns:
        A unique email address.
    """
    if not full_name:
        base_name = "candidate"
    else:
        # Normalize name: lowercase, replace spaces with dots, keep only alphanumeric and dots
        normalized_name = full_name.lower().replace(" ", ".")
        base_name = re.sub(r'[^a-z0-9.]', '', normalized_name)
        # Remove leading/trailing dots and multiple consecutive dots
        base_name = re.sub(r'\.+', '.', base_name).strip('.')
        if not base_name: # Handle cases where name results in empty string after normalization
            base_name = "candidate"

    email_candidate = f"{base_name}@example.com"
    counter = 1
    while email_candidate in existing_emails:
        email_candidate = f"{base_name}{counter}@example.com"
        counter += 1
    return email_candidate



def _generate_local_candidate(candidate_id: int) -> Dict[str, Any]:
    """Generate a candidate profile locally when Gemini fails."""
    name = fake.name()
    location = fake.city()
    years_exp = random.randint(0, 25)
    education_level = random.choice(SAMPLE_EDUCATION)
    skills = random.sample(SAMPLE_SKILLS, k=5)
    primary_skill = random.choice(skills)
    desired_salary = random.randint(1_000_000, 15_000_000)
    desired_position = f"{primary_skill} Specialist"
    summary = f"Profesional con experiencia en {primary_skill} y otras áreas relacionadas."
    availability = random.choice(SAMPLE_AVAILABILITY)
    languages = ["Spanish (Native)", "English (Intermediate)"]

    return {
        "candidate_id": candidate_id,
        "name": name,
        "location": location,
        "years_experience": years_exp,
        "education_level": education_level,
        "skills": skills,
        "primary_skill": primary_skill,
        "desired_salary": desired_salary,
        "desired_position": desired_position,
        "summary": summary,
        "availability": availability,
        "languages": languages,
        "phone": fake.phone_number(),
        "job_id": None,
    }


def generate_candidate_profile(candidate_id: int) -> Optional[Dict[str, Any]]:
    """
    Genera datos simulados para un perfil de candidato utilizando Gemini.

    Args:
        candidate_id: ID único para el candidato.

    Returns:
        Dict o None: Datos del perfil de candidato como diccionario, o None si ocurre un error.
    """
    # Asegurar que el cliente de Gemini esté configurado
    if not setup_gemini_client():
        log.error("No se pudo configurar el cliente de Gemini para generar datos de candidato.")
        return None

    # Prompt para Gemini
    # Nota: El candidate_id en el prompt es más una guía para Gemini, el ID final se asigna localmente.
    prompt = f"""
    Eres un asistente especializado en recursos humanos. Tu tarea es generar datos realistas para un perfil de candidato de trabajo en Colombia.

    Genera un objeto JSON con los siguientes campos OBLIGATORIOS:
    - candidate_id: {candidate_id} (entero, usa este valor exacto)
    - name: nombre completo colombiano realista (string)
    - phone: número de teléfono colombiano ficticio (string)
    - location: ciudad en Colombia (string)
    - years_experience: años de experiencia laboral (entero entre 0 y 25)
    - education_level: nivel educativo (string: "High School", "Technical", "Bachelor's", "Master's", "PhD")
    - skills: lista de habilidades profesionales (array de strings, al menos 5 habilidades, no vacía)
    - primary_skill: habilidad principal, debe ser una de las listadas en skills (string)
    - desired_salary: salario deseado en pesos colombianos (entero entre 1,000,000 y 15,000,000)
    - desired_position: puesto deseado (string)
    - summary: breve resumen profesional (string, al menos 20 palabras)
    - availability: disponibilidad (string: "Immediate", "2 weeks", "1 month", "Negotiable")
    - languages: lista de idiomas y niveles (array de strings, ej: ["Spanish (Native)", "English (Intermediate)"], no vacía)
    - job_id: ID de trabajo al que podría aplicar, puede ser null (entero o null)

    IMPORTANTE: Asegúrate de que el JSON sea válido y contenga TODOS los campos especificados. Usa comillas dobles para todas las claves y valores de texto. Los valores booleanos deben ser true o false (sin comillas). Los valores null deben ser null (sin comillas). Responde SOLO con el objeto JSON, sin texto adicional ni explicaciones. No uses comillas triples ni marcadores de código.
    """

    # Generar datos con Gemini
    generated_data = generate_with_gemini(prompt)
    log.debug(f"Datos crudos recibidos de Gemini para candidate_id {candidate_id}: {generated_data}")

    if generated_data:
        # Verificar que se hayan generado todos los campos requeridos
        required_keys = [
            "candidate_id",
            "name",
            # "email", # Email will be generated and added by the calling function
            # "phone", # Phone is in prompt but not strictly required by current logic, can be added if needed
            "location",
            "years_experience",
            "education_level",
            "skills",
            "primary_skill",
            "desired_salary",
            "desired_position",
            "summary",
            "availability",
            "languages",
        ]

        missing_keys = [key for key in required_keys if key not in generated_data]

        if not missing_keys:
            # Asegurar que candidate_id sea el proporcionado (sobrescribir el de Gemini si es diferente)
            generated_data["candidate_id"] = candidate_id

            # --- Sobrescritura Híbrida: Mantener datos generados por LLM pero aplicar validaciones ---

            # Asegurar que years_experience sea un entero
            try:
                generated_data["years_experience"] = int(generated_data["years_experience"])
            except (ValueError, TypeError):
                log.warning(
                    f"No se pudo convertir years_experience '{generated_data.get('years_experience')}' a int para el candidato {candidate_id}. Usando valor aleatorio."
                )
                generated_data["years_experience"] = random.randint(0, 25)

            # Asegurar que education_level sea uno de los valores permitidos
            valid_education_levels = ["High School", "Technical", "Bachelor's", "Master's", "PhD"]
            if generated_data.get("education_level") not in valid_education_levels:
                log.warning(
                    f"Nivel educativo no válido '{generated_data.get('education_level')}' para el candidato {candidate_id}. Usando valor aleatorio."
                )
                generated_data["education_level"] = random.choice(valid_education_levels)

            # Asegurar que skills sea una lista no vacía y primary_skill esté en ella
            if not isinstance(generated_data.get("skills"), list) or not generated_data.get("skills"):
                log.warning(
                    f"Lista de habilidades vacía o no válida para el candidato {candidate_id}. Usando valores predeterminados."
                )
                generated_data["skills"] = random.sample(SAMPLE_SKILLS, k=random.randint(3,5))
                generated_data["primary_skill"] = random.choice(generated_data["skills"])
            else:
                generated_data["skills"] = [str(skill) for skill in generated_data["skills"] if skill and isinstance(skill, (str, int, float))]
                if not generated_data["skills"]:
                    generated_data["skills"] = random.sample(SAMPLE_SKILLS, k=random.randint(3,5))
                
                current_primary_skill = generated_data.get("primary_skill")
                if not current_primary_skill or str(current_primary_skill) not in generated_data["skills"]:
                    log.warning(
                        f"Habilidad primaria '{current_primary_skill}' no está en la lista de habilidades o es inválida para el candidato {candidate_id}. Usando una habilidad de la lista."
                    )
                    generated_data["primary_skill"] = random.choice(generated_data["skills"])
                else:
                    generated_data["primary_skill"] = str(current_primary_skill)

            # Convertir desired_salary (aún generado por LLM, pero añadir fallback)
            try:
                generated_data["desired_salary"] = int(generated_data["desired_salary"])
            except (ValueError, TypeError):
                fallback_salary = random.randint(1000000, 15000000)  # Fallback COP
                log.warning(
                    f"No se pudo convertir desired_salary '{generated_data.get('desired_salary')}' a int para el candidato {candidate_id}. Usando fallback: {fallback_salary}."
                )
                generated_data["desired_salary"] = fallback_salary
            
            # Validar summary, availability, languages para que no sean vacíos si existen
            for key_to_check in ["summary", "availability", "languages"]:
                if key_to_check in generated_data:
                    if isinstance(generated_data[key_to_check], str) and not generated_data[key_to_check].strip():
                        log.warning(f"Campo '{key_to_check}' estaba vacío para candidato {candidate_id}. Será reemplazado por fallback.")
                        # Deleción para que el fallback local lo genere o se podría poner un default aquí.
                        del generated_data[key_to_check] # Esto hará que se marque como 'missing' y use el fallback
                        if key_to_check not in missing_keys: missing_keys.append(key_to_check)
                    elif isinstance(generated_data[key_to_check], list) and not generated_data[key_to_check]:
                        log.warning(f"Campo lista '{key_to_check}' estaba vacío para candidato {candidate_id}. Será reemplazado por fallback.")
                        del generated_data[key_to_check]
                        if key_to_check not in missing_keys: missing_keys.append(key_to_check)
            
            # Si después de las validaciones, alguna clave requerida se volvió 'missing'
            final_missing_keys = [key for key in required_keys if key not in generated_data or not generated_data[key]]
            if final_missing_keys:
                 log.error(
                    f"Después de validaciones, datos de candidato (candidate_id {candidate_id}) faltan o tienen vacíos en claves requeridas: {final_missing_keys}. "
                    f"Datos (parciales/originales): {generated_data}. Usando datos locales de respaldo."
                )
                 return _generate_local_candidate(candidate_id)

            log.info(f"Datos de candidato generados y validados correctamente para candidate_id {candidate_id}")
            return generated_data
        else:
            log.error(
                f"Datos de candidato generados (candidate_id {candidate_id}) faltan claves requeridas inicialmente: {missing_keys}. "
                f"Datos recibidos: {generated_data}. Usando datos locales de respaldo."
            )
            return _generate_local_candidate(candidate_id)
    else:
        log.error(
            f"Fallo al generar datos de candidato para candidate_id {candidate_id} usando Gemini (retornó None). Usando datos locales de respaldo."
        )
        return _generate_local_candidate(candidate_id)


def generate_multiple_candidates(count: int = 20) -> List[Dict[str, Any]]:
    """
    Genera una lista de perfiles de candidatos simulados usando Gemini.

    Args:
        count: Número de perfiles de candidatos a generar.

    Returns:
        List: Lista de diccionarios, cada uno representando un perfil de candidato.
    """
    candidates = []
    generated_emails = set()  # Para evitar emails duplicados
    generated_candidate_ids = set()  # Para evitar IDs duplicados
    attempts = 0
    max_total_attempts = (
        count * 5
    )  # Aumentar reintentos para asegurar suficientes candidatos únicos
    max_consecutive_failures = 10  # Máximo de fallos consecutivos antes de pausar
    consecutive_failures = 0

    log.info(f"Intentando generar {count} perfiles de candidatos únicos...")

    while len(candidates) < count and attempts < max_total_attempts:
        attempts += 1
        candidate_id = (
            len(candidates) + 1 + (attempts - len(candidates))
        )  # Usar índice progresivo para ID único

        # Evitar IDs duplicados
        while candidate_id in generated_candidate_ids:
            candidate_id += 1

        candidate_data = generate_candidate_profile(candidate_id)

        if candidate_data:
            name = candidate_data.get("name", f"Candidato Anónimo {candidate_id}")
            
            # Generate a unique email locally
            unique_email = _create_unique_email(name, generated_emails)
            candidate_data["email"] = unique_email
            
            generated_emails.add(unique_email)
            generated_candidate_ids.add(candidate_id)
            candidates.append(candidate_data)
            consecutive_failures = 0  # Reset on success
            log.info(f"Candidato único {candidate_id} ('{name}', email: {unique_email}) añadido. Total: {len(candidates)}/{count}")
        else:
            log.warning(f"Fallo al generar perfil para candidato_id {candidate_id}. Intento {attempts}/{max_total_attempts}")
            consecutive_failures += 1

        # Pausar si hay demasiados fallos consecutivos (ahora solo por fallos de generacion de perfil, no de email)
        if consecutive_failures >= max_consecutive_failures:
            log.warning(f"Detectados {consecutive_failures} fallos consecutivos en la generación de perfiles. Pausando por 5 segundos...")
            time.sleep(5)
            consecutive_failures = 0 # Reset after pause

    if len(candidates) < count:
        log.warning(
            f"No se pudieron generar suficientes candidatos únicos. Generados: {len(candidates)} de {count} solicitados."
        )

    return candidates
