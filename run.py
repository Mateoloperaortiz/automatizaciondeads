#!/usr/bin/env python
"""Punto de entrada principal para ejecutar la aplicación Flask.

Este script crea la instancia de la aplicación Flask, inicia el planificador,
y ejecuta el servidor de desarrollo.
"""

import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno primero
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from adflux.app import create_app
from adflux.extensions import celery # Importar la instancia de celery

# Crear la instancia de la aplicación Flask
# Esta llamada es crucial ya que inicializa y configura todo, incluyendo Celery
app = create_app()

# --- Configurar Logging --- 
# Configuración básica de logging (personalizar según sea necesario)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# --- Ejecución Principal --- #
# Este bloque permite ejecutar el servidor de desarrollo directamente vía `python run.py`
# Sin embargo, generalmente se prefiere usar `flask run` vía CLI para desarrollo.
if __name__ == '__main__':
    # Nota: El modo debug idealmente debería ser controlado por la configuración de Flask (DevelopmentConfig)
    # o la variable de entorno FLASK_DEBUG, no codificado directamente aquí.
    app.run(host='0.0.0.0', port=5000) # Usar 0.0.0.0 para ser accesible externamente si es necesario
