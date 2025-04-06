"""
Configuración de desarrollo para AdFlux.

Este módulo contiene la configuración específica para el entorno de desarrollo.
"""

import os
from .base import BaseConfig, basedir


class DevelopmentConfig(BaseConfig):
    """
    Configuración para el entorno de desarrollo.
    """
    # Habilitar modo de depuración
    DEBUG = True
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'adflux_dev.db')
    
    # Configuración de logging
    LOG_LEVEL = 'DEBUG'
    
    # Configuración de Celery para desarrollo
    CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False').lower() in ('true', '1', 't')
    
    # Configuración adicional para desarrollo
    TEMPLATES_AUTO_RELOAD = True
