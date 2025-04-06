"""
Configuración de pruebas para AdFlux.

Este módulo contiene la configuración específica para el entorno de pruebas.
"""

import os
from .base import BaseConfig, basedir


class TestingConfig(BaseConfig):
    """
    Configuración para el entorno de pruebas.
    """
    # Habilitar modo de pruebas
    TESTING = True
    
    # Deshabilitar CSRF para pruebas
    WTF_CSRF_ENABLED = False
    
    # Configuración de la base de datos para pruebas
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'adflux_test.db')
    
    # Configuración de Celery para pruebas
    CELERY_TASK_ALWAYS_EAGER = True  # Ejecutar tareas de forma síncrona
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
