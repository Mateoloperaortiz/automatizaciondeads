"""
Script para limpiar la base de datos y llenarla con datos simulados.

Este script elimina todos los datos existentes en la base de datos y la llena
con datos simulados generados usando la API de Gemini.
"""

import os
import logging
import time
import random
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

from adflux.models import (
    db, JobOpening, Candidate, Application, Campaign,
    MetaCampaign, MetaAdSet, MetaAd, MetaInsight, Segment
)
from adflux.simulation.job_data import generate_job_opening
from adflux.simulation.candidate_data import generate_candidate_profile
from adflux.api.gemini.client import get_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("db_reset")


def check_gemini_api() -> bool:
    """
    Verifica que la API de Gemini esté configurada y funcionando.

    Returns:
        bool: True si la API está funcionando, False en caso contrario.
    """
    log.info("Verificando conexión a la API de Gemini...")
    client = get_client()
    success, message, _ = client.test_connection()

    if success:
        log.info(f"Conexión a Gemini exitosa: {message}")
        return True
    else:
        log.error(f"Error de conexión a Gemini: {message}")
        return False


def clear_database(app: Flask) -> bool:
    """
    Elimina todos los datos existentes en la base de datos.

    Args:
        app: Instancia de la aplicación Flask.

    Returns:
        bool: True si la limpieza fue exitosa, False en caso contrario.
    """
    with app.app_context():
        try:
            log.info("Eliminando datos existentes de la base de datos...")

            # Eliminar en orden para respetar las restricciones de clave foránea
            MetaInsight.query.delete()
            MetaAd.query.delete()
            MetaAdSet.query.delete()
            MetaCampaign.query.delete()
            Campaign.query.delete()
            Application.query.delete()
            Candidate.query.delete()
            JobOpening.query.delete()
            Segment.query.delete()

            # Confirmar los cambios
            db.session.commit()
            log.info("Base de datos limpiada exitosamente.")
            return True

        except SQLAlchemyError as e:
            db.session.rollback()
            log.error(f"Error al limpiar la base de datos: {e}")
            return False


def populate_jobs(app: Flask, count: int = 20) -> List[JobOpening]:
    """
    Genera y guarda ofertas de trabajo simuladas en la base de datos.

    Args:
        app: Instancia de la aplicación Flask.
        count: Número de ofertas de trabajo a generar.

    Returns:
        List[JobOpening]: Lista de objetos JobOpening creados.
    """
    with app.app_context():
        try:
            log.info(f"Generando {count} ofertas de trabajo simuladas...")

            # Generar datos simulados usando el formato de data_simulation_example.py
            job_data_list = []
            attempts = 0
            max_attempts = count * 3
            generated_titles = set()
            generated_job_ids = set()

            # Obtener títulos existentes para evitar duplicados
            existing_titles = {job.title.lower() for job in JobOpening.query.all()}

            while len(job_data_list) < count and attempts < max_attempts:
                attempts += 1
                job_id = f"JOB-{len(job_data_list) + 1:04d}"

                # Evitar IDs duplicados
                while job_id in generated_job_ids:
                    job_id_num = int(job_id.split('-')[1]) + 1
                    job_id = f"JOB-{job_id_num:04d}"

                # Generar datos de trabajo
                job_data = generate_job_opening(job_id)

                if job_data:
                    title = job_data.get('title', '').lower()
                    company = job_data.get('company_name', '').lower()

                    # Verificar unicidad del título y compañía combinados
                    title_company_key = f"{title}|{company}" if title and company else None

                    if title_company_key and title_company_key not in generated_titles and title not in existing_titles:
                        generated_titles.add(title_company_key)
                        generated_job_ids.add(job_id)
                        job_data_list.append(job_data)
                        log.debug(f"Trabajo único añadido: {title} en {company} ({len(job_data_list)}/{count})")
                    elif title in existing_titles:
                        log.warning(f"Título de trabajo '{title}' ya existe en la base de datos. Saltando.")
                    elif title_company_key in generated_titles:
                        log.warning(f"Combinación de título y compañía duplicada generada y descartada: '{title}' en '{company}'")
                    else:
                        log.warning(f"Datos de trabajo generados sin título o compañía, descartados.")

            # Crear objetos JobOpening y guardarlos en la base de datos
            job_objects = []

            for job_data in job_data_list:
                # Procesar datos para adaptarlos al modelo JobOpening
                # Extraer valores de salario del rango
                salary_range = job_data.get('salary_range', '')
                salary_min = job_data.get('salary_min')
                salary_max = job_data.get('salary_max')

                # Si no hay salary_min/max pero hay salary_range, intentar extraer valores
                if not salary_min or not salary_max:
                    if salary_range:
                        # Eliminar caracteres no numéricos excepto el separador
                        clean_range = ''.join(c for c in salary_range if c.isdigit() or c in ',-')
                        parts = clean_range.replace('.', '').replace(',', '').split('-')

                        if len(parts) >= 2:
                            try:
                                salary_min = int(parts[0].strip())
                                salary_max = int(parts[1].strip())
                            except (ValueError, IndexError):
                                log.warning(f"No se pudo extraer rango salarial de '{salary_range}'")
                                salary_min = 30000000  # Valores predeterminados en COP
                                salary_max = 80000000
                        elif len(parts) == 1:
                            try:
                                salary_value = int(parts[0].strip())
                                salary_min = salary_value
                                salary_max = salary_value
                            except ValueError:
                                log.warning(f"No se pudo extraer valor salarial de '{salary_range}'")
                                salary_min = 30000000  # Valores predeterminados en COP
                                salary_max = 80000000

                # Procesar fechas
                try:
                    posting_date_str = job_data.get('posting_date', job_data.get('posted_date', datetime.now().isoformat()))
                    if isinstance(posting_date_str, str):
                        posted_date = datetime.fromisoformat(posting_date_str.replace('Z', '+00:00')).date()
                    else:
                        posted_date = datetime.now().date()

                    closing_date_str = job_data.get('closing_date', (datetime.now() + timedelta(days=30)).isoformat())
                    if isinstance(closing_date_str, str):
                        closing_date = datetime.fromisoformat(closing_date_str.replace('Z', '+00:00')).date()
                    else:
                        closing_date = (datetime.now() + timedelta(days=30)).date()
                except (ValueError, TypeError) as e:
                    log.warning(f"Error al procesar fechas: {e}. Usando fechas predeterminadas.")
                    posted_date = datetime.now().date()
                    closing_date = (datetime.now() + timedelta(days=30)).date()

                # Asegurar que los valores de salario sean enteros
                if salary_min is not None and not isinstance(salary_min, int):
                    try:
                        salary_min = int(salary_min)
                    except (ValueError, TypeError):
                        salary_min = 30000000  # Valor predeterminado

                if salary_max is not None and not isinstance(salary_max, int):
                    try:
                        salary_max = int(salary_max)
                    except (ValueError, TypeError):
                        salary_max = 80000000  # Valor predeterminado

                # Procesar remote (asegurar que sea booleano)
                remote_value = job_data.get('remote', False)
                if not isinstance(remote_value, bool):
                    remote_value = str(remote_value).lower() in ['true', 'yes', 'si', '1', 't', 'y']

                # Mapear campos al modelo JobOpening
                job = JobOpening(
                    job_id=job_data.get('job_id', f"JOB-{len(job_objects) + 1:04d}"),
                    title=job_data.get('title', 'Título no disponible'),
                    company_name=job_data.get('company_name', job_data.get('company', 'Empresa no disponible')),
                    location=job_data.get('location', 'Colombia'),
                    description=job_data.get('description', ''),
                    required_skills=job_data.get('requirements', job_data.get('required_skills', [])),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    employment_type=job_data.get('employment_type', 'Full-time'),
                    experience_level=job_data.get('experience_level', 'Mid-level'),
                    education_level=job_data.get('education_level', "Bachelor's"),
                    application_url=job_data.get('application_url', ''),
                    posted_date=posted_date,
                    closing_date=closing_date,
                    status=job_data.get('status', 'open'),
                    department=job_data.get('department', ''),
                    remote=remote_value,
                    benefits=job_data.get('benefits', []),
                    short_description=job_data.get('short_description', '')
                )

                db.session.add(job)
                job_objects.append(job)

            # Confirmar los cambios
            db.session.commit()
            log.info(f"Se guardaron {len(job_objects)} ofertas de trabajo en la base de datos.")
            return job_objects

        except Exception as e:
            db.session.rollback()
            log.error(f"Error al poblar ofertas de trabajo: {e}")
            return []


def populate_candidates(app: Flask, count: int = 50) -> List[Candidate]:
    """
    Genera y guarda perfiles de candidatos simulados en la base de datos.

    Args:
        app: Instancia de la aplicación Flask.
        count: Número de perfiles de candidatos a generar.

    Returns:
        List[Candidate]: Lista de objetos Candidate creados.
    """
    with app.app_context():
        try:
            log.info(f"Generando {count} perfiles de candidatos simulados...")

            # Generar datos simulados usando el formato de data_simulation_example.py
            candidate_data_list = []
            attempts = 0
            max_attempts = count * 3
            generated_emails = set()
            generated_candidate_ids = set()

            # Obtener emails existentes para evitar duplicados
            existing_emails = {candidate.email.lower() for candidate in Candidate.query.all() if candidate.email}

            while len(candidate_data_list) < count and attempts < max_attempts:
                attempts += 1
                candidate_id = f"CAND-{len(candidate_data_list) + 1:05d}"

                # Evitar IDs duplicados
                while candidate_id in generated_candidate_ids:
                    candidate_id_num = int(candidate_id.split('-')[1]) + 1
                    candidate_id = f"CAND-{candidate_id_num:05d}"

                # Generar datos de candidato
                candidate_data = generate_candidate_profile(candidate_id)

                if candidate_data:
                    email = candidate_data.get('email', '').lower()
                    name = candidate_data.get('name', '')

                    if email and email not in generated_emails and email not in existing_emails:
                        generated_emails.add(email)
                        generated_candidate_ids.add(candidate_id)
                        candidate_data_list.append(candidate_data)
                        log.debug(f"Candidato único añadido: {name} ({email}) ({len(candidate_data_list)}/{count})")
                    elif email in existing_emails:
                        log.warning(f"Email de candidato '{email}' ya existe en la base de datos. Saltando.")
                    elif email in generated_emails:
                        log.warning(f"Email de candidato duplicado generado y descartado: '{email}' para {name}")
                    else:
                        log.warning(f"Datos de candidato generados sin email, descartados.")

            # Crear objetos Candidate y guardarlos en la base de datos
            candidate_objects = []

            for candidate_data in candidate_data_list:
                # Procesar years_experience (asegurar que sea entero)
                years_exp = candidate_data.get('years_experience', 0)
                if not isinstance(years_exp, int):
                    try:
                        years_exp = int(years_exp)
                    except (ValueError, TypeError):
                        years_exp = 0  # Valor predeterminado

                # Procesar desired_salary (asegurar que sea entero)
                desired_salary = candidate_data.get('desired_salary', 0)
                if not isinstance(desired_salary, int):
                    try:
                        desired_salary = int(desired_salary)
                    except (ValueError, TypeError):
                        desired_salary = 3000000  # Valor predeterminado

                # Procesar skills (asegurar que sea lista)
                skills = candidate_data.get('skills', [])
                if not isinstance(skills, list):
                    if isinstance(skills, str):
                        # Intentar convertir string a lista si está en formato JSON
                        try:
                            import json
                            skills = json.loads(skills)
                        except json.JSONDecodeError:
                            skills = [skills]  # Convertir a lista de un elemento
                    else:
                        skills = []  # Valor predeterminado

                # Procesar languages (asegurar que sea lista)
                languages = candidate_data.get('languages', ['Spanish (Native)'])
                if not isinstance(languages, list):
                    if isinstance(languages, str):
                        try:
                            import json
                            languages = json.loads(languages)
                        except json.JSONDecodeError:
                            languages = [languages]  # Convertir a lista de un elemento
                    else:
                        languages = ['Spanish (Native)']  # Valor predeterminado

                # Mapear campos al modelo Candidate
                candidate = Candidate(
                    candidate_id=candidate_data.get('candidate_id', f"CAND-{len(candidate_objects) + 1:05d}"),
                    name=candidate_data.get('name', 'Nombre no disponible'),
                    email=candidate_data.get('email', ''),
                    phone=candidate_data.get('phone', ''),
                    location=candidate_data.get('location', 'Colombia'),
                    years_experience=years_exp,
                    education_level=candidate_data.get('education_level', "Bachelor's"),
                    skills=skills,
                    primary_skill=candidate_data.get('primary_skill', ''),
                    desired_salary=desired_salary,
                    desired_position=candidate_data.get('desired_position', ''),
                    summary=candidate_data.get('summary', ''),
                    availability=candidate_data.get('availability', 'Immediate'),
                    languages=languages,
                    segment_id=None  # Se asignará después de la segmentación
                )

                db.session.add(candidate)
                candidate_objects.append(candidate)

            # Confirmar los cambios
            db.session.commit()
            log.info(f"Se guardaron {len(candidate_objects)} perfiles de candidatos en la base de datos.")
            return candidate_objects

        except Exception as e:
            db.session.rollback()
            log.error(f"Error al poblar perfiles de candidatos: {e}")
            return []


def populate_applications(app: Flask, job_count: int = 5, candidate_count: int = 10, count: int = 15) -> List[Application]:
    """
    Genera y guarda aplicaciones simuladas en la base de datos.

    Args:
        app: Instancia de la aplicación Flask.
        job_count: Número de trabajos que se generaron (para log).
        candidate_count: Número de candidatos que se generaron (para log).
        count: Número de aplicaciones a generar.

    Returns:
        List[Application]: Lista de objetos Application creados.
    """
    with app.app_context():
        try:
            # Obtener trabajos y candidatos directamente de la base de datos
            jobs = JobOpening.query.all()
            candidates = Candidate.query.all()

            if not jobs or not candidates:
                log.warning("No hay trabajos o candidatos disponibles para generar aplicaciones.")
                return []

            log.info(f"Generando {count} aplicaciones simuladas...")

            # Filtrar trabajos con estado 'open'
            open_jobs = [job for job in jobs if job.status == 'open']
            if not open_jobs:
                log.warning("No hay trabajos con estado 'open' disponibles para generar aplicaciones.")
                open_jobs = jobs  # Usar todos los trabajos si no hay ninguno con estado 'open'

            # Verificar combinaciones existentes para evitar duplicados
            existing_applications = set()
            for app in Application.query.all():
                existing_applications.add((app.candidate_id, app.job_id))

            # Generar aplicaciones manualmente para tener más control
            application_objects = []
            attempts = 0
            max_attempts = count * 3
            generated_pairs = set()

            # Calcular el máximo teórico de aplicaciones posibles
            max_possible = len(candidates) * len(open_jobs)
            if max_possible < count:
                log.warning(f"Se solicitaron {count} aplicaciones, pero solo son posibles {max_possible} combinaciones únicas.")
                count = max_possible

            while len(application_objects) < count and attempts < max_attempts:
                attempts += 1

                # Seleccionar aleatoriamente un candidato y un trabajo
                candidate = random.choice(candidates)
                job = random.choice(open_jobs)

                candidate_id = candidate.candidate_id
                job_id = job.job_id

                # Verificar si esta combinación ya existe
                if (candidate_id, job_id) in existing_applications or (candidate_id, job_id) in generated_pairs:
                    continue

                # Generar fecha de aplicación realista
                posting_date = job.posted_date or datetime.now().date() - timedelta(days=30)
                closing_date = job.closing_date or datetime.now().date() + timedelta(days=30)
                now = datetime.now().date()
                latest_date = min(closing_date, now)

                # Asegurar que la fecha de aplicación sea posterior a la fecha de publicación
                if latest_date <= posting_date:
                    application_date = posting_date + timedelta(days=1)
                else:
                    # Generar fecha aleatoria entre posting_date y latest_date
                    days_diff = (latest_date - posting_date).days
                    if days_diff > 0:
                        random_days = random.randint(0, days_diff)
                        application_date = posting_date + timedelta(days=random_days)
                    else:
                        application_date = posting_date

                # Crear objeto Application directamente
                application = Application(
                    application_id=len(application_objects) + 1,
                    candidate_id=candidate_id,
                    job_id=job_id,
                    application_date=application_date,
                    status=random.choice(['Pending', 'Reviewed', 'Interviewed', 'Rejected', 'Hired']),
                    source_platform=random.choice(['Meta', 'Google', 'X', 'TikTok', 'LinkedIn', 'Direct'])
                )

                db.session.add(application)
                application_objects.append(application)
                generated_pairs.add((candidate_id, job_id))

                # Hacer commit parcial cada 5 aplicaciones para evitar problemas de memoria
                if len(application_objects) % 5 == 0:
                    db.session.commit()

            # Confirmar los cambios restantes
            db.session.commit()
            log.info(f"Se guardaron {len(application_objects)} aplicaciones en la base de datos.")
            return application_objects

        except Exception as e:
            db.session.rollback()
            log.error(f"Error al poblar aplicaciones: {e}")
            return []


def reset_and_populate_database(app: Flask, job_count: int = 20, candidate_count: int = 50, application_count: int = 100) -> Tuple[bool, Dict[str, int]]:
    """
    Limpia la base de datos y la llena con datos simulados.

    Args:
        app: Instancia de la aplicación Flask.
        job_count: Número de ofertas de trabajo a generar.
        candidate_count: Número de perfiles de candidatos a generar.
        application_count: Número de aplicaciones a generar.

    Returns:
        Tuple[bool, Dict[str, int]]: (éxito, estadísticas de datos generados)
    """
    # Verificar conexión a la API de Gemini
    if not check_gemini_api():
        log.error("No se pudo conectar a la API de Gemini. Abortando.")
        return False, {}

    # Limpiar la base de datos
    if not clear_database(app):
        log.error("No se pudo limpiar la base de datos. Abortando.")
        return False, {}

    # Generar y guardar ofertas de trabajo
    jobs = populate_jobs(app, job_count)
    if not jobs:
        log.error("No se pudieron generar ofertas de trabajo. Abortando.")
        return False, {'jobs': 0, 'candidates': 0, 'applications': 0}

    # Generar y guardar perfiles de candidatos
    candidates = populate_candidates(app, candidate_count)
    if not candidates:
        log.error("No se pudieron generar perfiles de candidatos. Abortando.")
        return False, {'jobs': len(jobs), 'candidates': 0, 'applications': 0}

    # Generar y guardar aplicaciones
    applications = populate_applications(app, len(jobs), len(candidates), application_count)

    # Devolver estadísticas
    stats = {
        'jobs': len(jobs),
        'candidates': len(candidates),
        'applications': len(applications)
    }

    log.info(f"Base de datos poblada exitosamente con {stats['jobs']} trabajos, {stats['candidates']} candidatos y {stats['applications']} aplicaciones.")
    return True, stats


if __name__ == "__main__":
    # Este código se ejecuta solo si se ejecuta el script directamente
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    from adflux import create_app

    # Crear la aplicación Flask
    app = create_app()

    # Definir cantidades predeterminadas
    JOB_COUNT = 20
    CANDIDATE_COUNT = 50
    APPLICATION_COUNT = 100

    # Permitir sobrescribir cantidades desde argumentos de línea de comandos
    if len(sys.argv) > 1:
        try:
            JOB_COUNT = int(sys.argv[1])
        except ValueError:
            pass

    if len(sys.argv) > 2:
        try:
            CANDIDATE_COUNT = int(sys.argv[2])
        except ValueError:
            pass

    if len(sys.argv) > 3:
        try:
            APPLICATION_COUNT = int(sys.argv[3])
        except ValueError:
            pass

    # Ejecutar el reseteo y población de la base de datos
    success, stats = reset_and_populate_database(app, JOB_COUNT, CANDIDATE_COUNT, APPLICATION_COUNT)

    if success:
        print(f"✅ Base de datos poblada exitosamente con:")
        print(f"   - {stats['jobs']} ofertas de trabajo")
        print(f"   - {stats['candidates']} perfiles de candidatos")
        print(f"   - {stats['applications']} aplicaciones")
        sys.exit(0)
    else:
        print("❌ Error al poblar la base de datos. Revise los logs para más detalles.")
        sys.exit(1)
