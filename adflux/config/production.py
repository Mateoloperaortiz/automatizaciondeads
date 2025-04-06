"""
Configuración de producción para AdFlux.

Este módulo contiene la configuración específica para el entorno de producción.
"""

import os
from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """
    Configuración para el entorno de producción.
    """

    # Deshabilitar modo de depuración
    DEBUG = False

    # Configuración de seguridad
    SECRET_KEY = os.environ.get("SECRET_KEY")  # Debe estar definido en producción
    if not SECRET_KEY:
        raise ValueError("La variable de entorno SECRET_KEY debe estar definida en producción")

    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("La variable de entorno DATABASE_URL debe estar definida en producción")

    # Configuración de logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR")

    # Configuración de seguridad adicional
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
