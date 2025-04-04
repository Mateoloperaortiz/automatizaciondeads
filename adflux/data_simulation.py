# Funciones para generar datos simulados usando LLM (Gemini)

# from faker import Faker # Ya no se usa Faker
import google.generativeai as genai
import os
import json
import logging
import time # Para posibles reintentos
import datetime # Mantener para formateo de fechas
import random # <--- Importación añadida para módulo random

# Configurar logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Inicializar cliente Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    log.warning("GEMINI_API_KEY no encontrado en variables de entorno. La generación de datos fallará.")
    # Opcionalmente lanzar un error o proporcionar un generador ficticio
    gemini_model = None
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Usando gemini-1.5-flash para generación potencialmente más rápida/barata
        # Usar gemini-1.5-pro para mayor calidad si es necesario
        gemini_model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        log.info("API Gemini configurada correctamente usando gemini-2.5-pro-exp-03-25.")
    except Exception as e:
        log.error(f"Fallo al configurar la API Gemini: {e}")
        gemini_model = None

# Función auxiliar para llamar a la API Gemini y analizar JSON
def generate_with_gemini(prompt, retries=3, delay=5, temperature=0.9):
    if not gemini_model:
        log.error("Modelo Gemini no inicializado. No se pueden generar datos.")
        return None

    for attempt in range(retries):
        try:
            log.debug(f"Enviando prompt a Gemini (intento {attempt + 1}):\n{prompt}")
            # Asegurar que el formato de respuesta sea JSON y establecer temperatura
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=temperature # Usar el parámetro temperature
            )
            response = gemini_model.generate_content(prompt, generation_config=generation_config)
            
            log.debug(f"Texto de respuesta crudo de Gemini:\n{response.text}")
            
            # El texto de respuesta debería ser directamente el string JSON
            json_data = json.loads(response.text)
            return json_data
        
        except json.JSONDecodeError as e:
            log.error(f"La respuesta de Gemini no fue JSON válido (intento {attempt + 1}/{retries}): {e}")
            log.error(f"Texto de respuesta que falló al analizar: {response.text if 'response' in locals() else 'N/A'}")
            # Opcionalmente reintentar o modificar prompt si el JSON es consistentemente malo
        except Exception as e:
            # Capturar otros errores potenciales de API (límites de tasa, problemas de conexión, etc.)
            log.error(f"Error llamando a la API Gemini (intento {attempt + 1}/{retries}): {e}")
        
        if attempt < retries - 1:
            log.info(f"Reintentando llamada a la API Gemini en {delay} segundos...")
            time.sleep(delay)
        else:
            log.error("Se alcanzó el máximo de reintentos para la llamada a la API Gemini.")
            return None

# --- Nuevas Funciones de Generación usando Gemini ---

def generate_job_opening(job_id):
    """Genera un diccionario que representa una única oferta de trabajo simulada usando Gemini."""
    
    prompt = f"""
    Genera un objeto JSON realista que represente una oferta de trabajo para un rol técnico o de negocios.
    El objeto JSON debe adherirse estrictamente a la siguiente estructura y tipos de datos:
    {{
        "job_id": "JOB-{job_id:04d}", // Usa este formato exacto de ID de trabajo
        "title": "string", // Título del trabajo (ej., Ingeniero de Software, Gerente de Producto)
        "description": "string", // Un párrafo de 3-5 frases describiendo el rol y responsabilidades.
        "location": "string", // Ciudad, ST o Ciudad, País o "Remoto"
        "company": "string", // Nombre de empresa que suene realista
        "required_skills": ["string", "string", ...], // Lista de 3-7 habilidades técnicas o blandas relevantes
        "salary_min": integer, // Salario anual mínimo plausible (ej., 40000 a 90000)
        "salary_max": integer, // Salario anual máximo plausible (ej., 90000 a 180000), debe ser > salary_min
        "posted_date": "YYYY-MM-DD", // Una fecha plausible dentro del último año
        "status": "string" // Debe ser uno de: "open", "pending", "closed" (principalmente "open")
    }}
    
    Asegúrate de que la salida sea ÚNICAMENTE el objeto JSON válido, comenzando con {{ y terminando con }}, sin ningún otro texto antes o después.
    Haz que los datos sean realistas y variados.
    """

    generated_data = generate_with_gemini(prompt)
    
    if generated_data:
        # Validación básica (se podría añadir más)
        required_keys = ['job_id', 'title', 'description', 'location', 'company', 'required_skills', 'salary_min', 'salary_max', 'posted_date', 'status']
        if all(key in generated_data for key in required_keys):
             # Asegurar formato correcto de job_id (LLM podría alucinar)
             generated_data['job_id'] = f'JOB-{job_id:04d}' 
             # Convertir string de fecha a objeto date si es necesario (o manejar en sembrado)
             # Opcional: Convertir strings de salario a int si LLM devuelve strings
             try:
                generated_data['salary_min'] = int(generated_data['salary_min'])
                generated_data['salary_max'] = int(generated_data['salary_max'])
             except (ValueError, TypeError):
                 log.warning(f"No se pudieron convertir los salarios a int para el trabajo {generated_data.get('job_id')}. Usando marcadores de posición.")
                 generated_data['salary_min'] = 50000
                 generated_data['salary_max'] = 100000
             
             log.info(f"Datos de trabajo generados correctamente para {generated_data['job_id']}")
             return generated_data
        else:
            log.error("Datos de trabajo generados faltan claves requeridas.")
            return None # Indicar fallo
    else:
        log.error(f"Fallo al generar datos de trabajo para el índice {job_id} usando Gemini.")
        return None # Indicar fallo

def generate_candidate_profile(candidate_id):
    """Genera un diccionario que representa un único perfil de candidato simulado usando Gemini."""
    
    # Ejemplos Few-shot
    example_1 = {
        "candidate_id": "CAND-00000", # Marcador de posición, será sobrescrito
        "name": "Alice Chen",
        "location": "New York, NY",
        "years_experience": 3,
        "education_level": "Bachelor Degree",
        "skills": ["JavaScript", "React", "Node.js", "HTML", "CSS", "REST APIs", "Git"],
        "primary_skill": "React",
        "desired_salary": 85000
    }
    example_2 = {
        "candidate_id": "CAND-00000", # Marcador de posición, será sobrescrito
        "name": "Bob Garcia", 
        "location": "Remote",
        "years_experience": 12,
        "education_level": "Master Degree",
        "skills": ["AWS", "Terraform", "Kubernetes", "Docker", "CI/CD", "Python", "Bash", "Security Best Practices"],
        "primary_skill": "AWS",
        "desired_salary": 150000
    }
    
    prompt = f"""
    Genera un objeto JSON realista que represente un perfil de candidato para un rol técnico o de negocios.
    
    Aquí hay un par de ejemplos que demuestran el formato y la variedad deseados:
    Ejemplo 1: {json.dumps(example_1)}
    Ejemplo 2: {json.dumps(example_2)}
    
    Ahora, genera un NUEVO objeto JSON realista para un candidato diferente. Debe adherirse estrictamente a la siguiente estructura y tipos de datos:
    {{
        "candidate_id": "CAND-{candidate_id:05d}", // Usa este formato exacto de ID de candidato
        "name": "string", // Nombre completo del candidato
        "location": "string", // Ciudad, ST o Ciudad, País o "Remoto"
        "years_experience": integer, // Años plausibles de experiencia profesional. Asegúrate de que este valor varíe realisticamente entre 0 y 25.
        "education_level": "string", // Debe ser uno de: "High School", "Associate Degree", "Bachelor Degree", "Master Degree", "PhD"
        "skills": ["string", "string", ...], // Lista de 5-15 habilidades técnicas o blandas relevantes
        "primary_skill": "string", // Una de las habilidades de la lista anterior. Genera diversas habilidades principales relevantes para diferentes roles técnicos/de negocios (ej., Python, Java, React, AWS, Azure, Análisis de Datos, Marketing Digital, Ventas, Diseño UI/UX, Gestión de Producto, etc.).
        "desired_salary": integer // Salario anual deseado plausible (ej., 40000 a 200000)
    }}
    
    Asegúrate de que la salida sea ÚNICAMENTE el objeto JSON válido para el nuevo candidato, comenzando con {{ y terminando con }}, sin ningún otro texto antes o después.
    Haz que los datos sean realistas y variados. Genera habilidades relevantes para roles técnicos/de negocios comunes. Asegúrate de que 'primary_skill' esté presente en la lista 'skills'.
    Genera una variedad significativa en ubicación, años_experiencia y habilidad_principal entre diferentes candidatos. NO copies simplemente los ejemplos.
    """

    generated_data = generate_with_gemini(prompt) # Temperatura pasada implícitamente vía valor por defecto

    if generated_data:
        # Validación básica para claves principales necesarias antes de sobrescribir
        required_keys = ['candidate_id', 'name', 'location', 'education_level', 'skills', 'desired_salary'] # Eliminado experiencia/principal de la comprobación inicial
        if all(key in generated_data for key in required_keys):
            # Asegurar formato de ID correcto
            generated_data['candidate_id'] = f'CAND-{candidate_id:05d}'
            
            # --- Inicio Sobrescritura Híbrida --- 
            # Sobrescribir years_experience con un valor aleatorio
            generated_data['years_experience'] = random.randint(0, 25) 
            log.debug(f"Se sobrescribió years_experience a {generated_data['years_experience']} para el candidato {generated_data.get('candidate_id')}")

            # Asegurar que skills sea una lista y sobrescribir primary_skill
            skills_list = generated_data.get('skills')
            if not isinstance(skills_list, list) or not skills_list:
                log.warning(f"Datos de habilidades inválidos o vacíos para el candidato {generated_data.get('candidate_id')}. Estableciendo habilidades de marcador de posición.")
                generated_data['skills'] = ['Comunicación', 'Resolución de Problemas', 'Trabajo en Equipo'] # Añadir algunos valores por defecto
                generated_data['primary_skill'] = random.choice(generated_data['skills'])
            else:
                # Asegurar que los elementos de la lista de habilidades sean strings (a veces los LLM pueden anidar cosas)
                generated_data['skills'] = [str(skill) for skill in skills_list if isinstance(skill, (str, int, float))]
                # Sobrescribir primary_skill eligiendo aleatoriamente de la lista de habilidades generada/limpiada
                if generated_data['skills']: # Comprobar de nuevo en caso de que la limpieza resulte en lista vacía
                    generated_data['primary_skill'] = random.choice(generated_data['skills'])
                    log.debug(f"Se sobrescribió primary_skill a '{generated_data['primary_skill']}' para el candidato {generated_data.get('candidate_id')}")
                else:
                    log.warning(f"La lista de habilidades quedó vacía después de la limpieza para el candidato {generated_data.get('candidate_id')}. Estableciendo habilidad principal de marcador de posición.")
                    generated_data['skills'] = ['Comunicación', 'Resolución de Problemas', 'Trabajo en Equipo'] # Re-añadir valores por defecto
                    generated_data['primary_skill'] = random.choice(generated_data['skills'])

            # Convertir desired_salary (aún generado por LLM, pero añadir fallback)
            try:
                generated_data['desired_salary'] = int(generated_data['desired_salary'])
            except (ValueError, TypeError):
                fallback_salary = random.randint(40000, 180000)
                log.warning(f"No se pudo convertir desired_salary '{generated_data.get('desired_salary')}' a int para el candidato {generated_data.get('candidate_id')}. Usando fallback: {fallback_salary}.")
                generated_data['desired_salary'] = fallback_salary
                
            # --- Fin Sobrescritura Híbrida --- 

            log.info(f"Datos de candidato generados/modificados correctamente para {generated_data['candidate_id']}")
            return generated_data
        else:
            missing_keys = [key for key in required_keys if key not in generated_data]
            log.error(f"Datos de candidato generados faltan claves requeridas: {missing_keys}")
            return None
    else:
        log.error(f"Fallo al generar datos de candidato para el índice {candidate_id} usando Gemini.")
        return None

def generate_multiple_jobs(count=10):
    """Genera una lista de ofertas de trabajo simuladas usando Gemini."""
    jobs = []
    for i in range(count):
        job_data = generate_job_opening(i + 1) # Usar índice comenzando desde 1
        if job_data: # Añadir solo si la generación fue exitosa
            jobs.append(job_data)
        else:
            log.warning(f"Saltando índice de trabajo {i+1} debido a fallo de generación.")
    return jobs

def generate_multiple_candidates(count=100):
    """Genera una lista de perfiles de candidatos simulados usando Gemini."""
    candidates = []
    for i in range(count):
        candidate_data = generate_candidate_profile(i + 1)
        if candidate_data: # Añadir solo si la generación fue exitosa
            candidates.append(candidate_data)
        else:
            log.warning(f"Saltando índice de candidato {i+1} debido a fallo de generación.")
    return candidates

# Ejemplo de uso (puede eliminarse o moverse a un comando CLI más tarde)
if __name__ == '__main__':
    print("--- Muestra de Ofertas de Trabajo (Generadas por Gemini) ---")
    sample_jobs = generate_multiple_jobs(2) # Generar menos para pruebas
    if sample_jobs:
        for job in sample_jobs:
            print(json.dumps(job, indent=2))
    else:
        print("Fallo al generar trabajos de muestra.")

    # print("\n--- Muestra de Perfiles de Candidato ---")
    # sample_candidates = generate_multiple_candidates(5)
    # for candidate in sample_candidates:
    #     print(candidate)
