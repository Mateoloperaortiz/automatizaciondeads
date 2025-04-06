#!/usr/bin/env python
"""
Script para limpiar y poblar la base de datos de AdFlux.

Este script elimina todos los datos existentes en la base de datos y la llena
con datos simulados generados usando la API de Gemini.

Uso:
    python reset_db.py [num_jobs] [num_candidates] [num_applications]

Argumentos:
    num_jobs: Número de ofertas de trabajo a generar (predeterminado: 20).
    num_candidates: Número de perfiles de candidatos a generar (predeterminado: 50).
    num_applications: Número de aplicaciones a generar (predeterminado: 100).

Ejemplo:
    python reset_db.py 30 80 150
"""

import os
import sys
import logging
from adflux.core import create_app
from adflux.simulation.db_reset import reset_and_populate_database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("reset_db")

# Definir cantidades predeterminadas
JOB_COUNT = 20
CANDIDATE_COUNT = 50
APPLICATION_COUNT = 100

def main():
    """Función principal del script."""
    # Permitir sobrescribir cantidades desde argumentos de línea de comandos
    global JOB_COUNT, CANDIDATE_COUNT, APPLICATION_COUNT

    if len(sys.argv) > 1:
        try:
            JOB_COUNT = int(sys.argv[1])
        except ValueError:
            log.warning(f"Valor inválido para num_jobs: {sys.argv[1]}. Usando valor predeterminado: {JOB_COUNT}")

    if len(sys.argv) > 2:
        try:
            CANDIDATE_COUNT = int(sys.argv[2])
        except ValueError:
            log.warning(f"Valor inválido para num_candidates: {sys.argv[2]}. Usando valor predeterminado: {CANDIDATE_COUNT}")

    if len(sys.argv) > 3:
        try:
            APPLICATION_COUNT = int(sys.argv[3])
        except ValueError:
            log.warning(f"Valor inválido para num_applications: {sys.argv[3]}. Usando valor predeterminado: {APPLICATION_COUNT}")

    log.info(f"Iniciando reseteo de base de datos con {JOB_COUNT} trabajos, {CANDIDATE_COUNT} candidatos y {APPLICATION_COUNT} aplicaciones...")

    # Crear la aplicación Flask
    app = create_app()

    # Ejecutar el reseteo y población de la base de datos
    success, stats = reset_and_populate_database(app, JOB_COUNT, CANDIDATE_COUNT, APPLICATION_COUNT)

    if success:
        print("\n" + "="*50)
        print("✅ Base de datos poblada exitosamente con:")
        print(f"   - {stats['jobs']} ofertas de trabajo")
        print(f"   - {stats['candidates']} perfiles de candidatos")
        print(f"   - {stats['applications']} aplicaciones")
        print("="*50 + "\n")
        return 0
    else:
        print("\n" + "="*50)
        print("❌ Error al poblar la base de datos. Revise los logs para más detalles.")
        print("="*50 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
