"""
Generación de datos de aplicaciones para AdFlux.

Este módulo contiene funciones para generar datos simulados de aplicaciones
de candidatos a ofertas de trabajo.
"""

import logging
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Configurar logging
log = logging.getLogger(__name__)


def generate_simulated_applications(
    jobs: List[Dict[str, Any]], candidates: List[Dict[str, Any]], num_applications: int = 30
) -> List[Dict[str, Any]]:
    """
    Genera aplicaciones simuladas entre candidatos y ofertas de trabajo.

    Args:
        jobs: Lista de diccionarios de ofertas de trabajo generadas.
        candidates: Lista de diccionarios de perfiles de candidatos generados.
        num_applications: El número deseado de aplicaciones a simular.

    Returns:
        List: Una lista de diccionarios, cada uno representando una aplicación simulada.
              Cada diccionario contiene: 'application_id', 'candidate_id', 'job_id',
              'application_date', 'source_platform'.
              Retorna una lista vacía si no hay trabajos o candidatos disponibles.
    """
    if not jobs or not candidates:
        log.warning("No se pueden simular aplicaciones sin trabajos o candidatos.")
        return []

    applications = []
    applied_pairs = set()  # Para evitar aplicaciones duplicadas (candidate_id, job_id)
    application_ids = set()  # Para evitar IDs de aplicación duplicados
    platforms = [
        "Meta",
        "Google",
        "X",
        "TikTok",
        "LinkedIn",
        "Direct",
    ]  # Plataformas de origen simuladas

    # Filtrar trabajos abiertos para que las aplicaciones sean más realistas
    open_jobs = [job for job in jobs if job.get("status") == "open"]
    if not open_jobs:
        log.warning("No hay trabajos abiertos ('open') disponibles para simular aplicaciones.")
        # Podríamos decidir simular con trabajos no abiertos, pero esto es más realista
        return []

    # Calcular el máximo teórico de aplicaciones posibles (candidatos x trabajos)
    max_possible = len(candidates) * len(open_jobs)
    if max_possible < num_applications:
        log.warning(
            f"Se solicitaron {num_applications} aplicaciones, pero solo son posibles {max_possible} combinaciones únicas."
        )
        num_applications = max_possible

    max_attempts = num_applications * 5  # Intentar un poco más para alcanzar el número deseado
    max_consecutive_failures = 20  # Máximo de fallos consecutivos antes de terminar
    consecutive_failures = 0

    log.info(f"Intentando generar {num_applications} aplicaciones simuladas únicas...")

    app_id_counter = 1
    attempts = 0
    while (
        len(applications) < num_applications
        and attempts < max_attempts
        and consecutive_failures < max_consecutive_failures
    ):
        attempts += 1

        # Seleccionar aleatoriamente un candidato y un trabajo abierto
        candidate = random.choice(candidates)
        job = random.choice(open_jobs)

        candidate_id = candidate.get("candidate_id")
        job_id = job.get("job_id")

        # Saltar si este par ya aplicó
        if (candidate_id, job_id) in applied_pairs:
            consecutive_failures += 1
            continue

        # Saltar si no se pudieron obtener IDs (poco probable pero seguro)
        if not candidate_id or not job_id:
            log.debug("Se saltó la generación de aplicación debido a IDs faltantes.")
            consecutive_failures += 1
            continue

        # Asegurar que el ID de aplicación sea único
        while app_id_counter in application_ids:
            app_id_counter += 1

        # Simular una fecha de aplicación realista
        job_posting_date = job.get("posted_date")
        job_closing_date = job.get("closing_date")

        try:
            # Convertir fechas de string a datetime
            posted_date = (
                datetime.fromisoformat(job_posting_date.replace("Z", "+00:00"))
                if job_posting_date
                else datetime.now() - timedelta(days=30)
            )
            closing_date = (
                datetime.fromisoformat(job_closing_date.replace("Z", "+00:00"))
                if job_closing_date
                else datetime.now() + timedelta(days=30)
            )

            # Generar fecha de aplicación entre la fecha de publicación y ahora (o fecha de cierre si es en el pasado)
            now = datetime.now()
            latest_date = min(closing_date, now)

            # Asegurar que la fecha de aplicación sea posterior a la fecha de publicación
            if latest_date <= posted_date:
                log.debug(f"Fechas inválidas para el trabajo {job_id}, ajustando.")
                latest_date = posted_date + timedelta(days=1)

            # Generar fecha aleatoria entre posted_date y latest_date
            application_date = posted_date + timedelta(
                seconds=random.randint(0, int((latest_date - posted_date).total_seconds()))
            )

            # Formatear como string ISO
            application_date_str = application_date.isoformat()
        except (ValueError, TypeError, AttributeError):
            # Fallback si hay problemas con las fechas
            log.debug(
                f"Error al procesar fechas para el trabajo {job_id}, usando fechas aleatorias."
            )
            days_ago = random.randint(1, 30)
            application_date_str = (datetime.now() - timedelta(days=days_ago)).isoformat()

        # Crear objeto de aplicación
        application = {
            "application_id": app_id_counter,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "application_date": application_date_str,
            "source_platform": random.choice(platforms),
        }

        # Añadir a la lista de aplicaciones
        applications.append(application)
        applied_pairs.add((candidate_id, job_id))
        application_ids.add(app_id_counter)
        app_id_counter += 1
        consecutive_failures = 0  # Reiniciar contador de fallos

        log.debug(f"Aplicación simulada: Candidato {candidate_id} -> Trabajo {job_id}")

    if consecutive_failures >= max_consecutive_failures:
        log.warning(
            f"Se alcanzó el límite de fallos consecutivos ({max_consecutive_failures}). Posiblemente no hay más combinaciones únicas disponibles."
        )

    log.info(
        f"Generación de aplicaciones completada: {len(applications)}/{num_applications} aplicaciones generadas en {attempts} intentos."
    )
    return applications
