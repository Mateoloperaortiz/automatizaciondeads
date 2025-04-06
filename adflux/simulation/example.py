"""
Script de ejemplo para probar las funciones de simulación de datos de AdFlux.

Este script muestra cómo utilizar las funciones de simulación para generar
datos de trabajos, candidatos y aplicaciones.
"""

import json
import logging

from .job_data import generate_multiple_jobs
from .candidate_data import generate_multiple_candidates
from .application_data import generate_simulated_applications

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def run_simulation_example():
    """
    Ejecuta un ejemplo de simulación de datos.
    """
    NUM_JOBS_TO_GENERATE = 5
    NUM_CANDIDATES_TO_GENERATE = 20
    NUM_APPLICATIONS_TO_SIMULATE = 15

    print("--- Generando Ofertas de Trabajo (Usando Gemini) ---")
    sample_jobs = generate_multiple_jobs(NUM_JOBS_TO_GENERATE)
    if sample_jobs:
        print(f"Se generaron {len(sample_jobs)} trabajos.")
        print(json.dumps(sample_jobs[0], indent=2))  # Mostrar solo el primero
    else:
        print("Fallo al generar trabajos de muestra.")

    print("--- Generando Perfiles de Candidato (Usando Gemini) ---")
    sample_candidates = generate_multiple_candidates(NUM_CANDIDATES_TO_GENERATE)
    if sample_candidates:
        print(f"Se generaron {len(sample_candidates)} candidatos.")
        print(json.dumps(sample_candidates[0], indent=2))  # Mostrar solo el primero
    else:
        print("Fallo al generar candidatos de muestra.")

    print("--- Simulando Aplicaciones de Trabajo ---")
    if sample_jobs and sample_candidates:
        simulated_applications = generate_simulated_applications(
            sample_jobs, sample_candidates, NUM_APPLICATIONS_TO_SIMULATE
        )
        if simulated_applications:
            print(f"Se simularon {len(simulated_applications)} aplicaciones.")
            print("Ejemplos de aplicaciones simuladas:")
            for app in simulated_applications[:3]:  # Mostrar las primeras 3
                print(json.dumps(app, indent=2))
        else:
            print("Fallo al simular aplicaciones (o no había trabajos/candidatos adecuados).")
    else:
        print("No se pueden simular aplicaciones porque faltan trabajos o candidatos.")


if __name__ == "__main__":
    run_simulation_example()
