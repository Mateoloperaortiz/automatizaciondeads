#!/usr/bin/env python
"""Punto de entrada principal para ejecutar la aplicación Flask.

Este script crea la instancia de la aplicación Flask, inicia el planificador,
y ejecuta el servidor de desarrollo.
"""

import os
import logging
from adflux.utils.env_loader import load_env_files

# Cargar variables de entorno primero
load_env_files(os.path.dirname(__file__))

from adflux.core import create_app, run_meta_sync_for_all_accounts
# Import celery instance from extensions
from adflux.extensions import celery

# Create the Flask app instance globally
app = create_app()

# --- Configurar Logging ---
# Configuración básica de logging (personalizar según sea necesario)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# --- Ejecución Principal --- #
# Este bloque permite ejecutar el servidor de desarrollo directamente vía `python run.py`
# Sin embargo, generalmente se prefiere usar `flask run` vía CLI para desarrollo.
if __name__ == '__main__':
    # Para desarrollo, debug=True habilita la recarga automática y errores detallados
    # El puerto 5003 es diferente para evitar conflictos
    app.run(debug=True, host='0.0.0.0', port=5003)
