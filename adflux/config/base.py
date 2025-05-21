"""
Configuración base para AdFlux.

Este módulo contiene la configuración base común a todos los entornos.
"""

import os
from adflux.utils.env_loader import load_env_files

# Obtener la ruta base del proyecto
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Cargar variables de entorno desde los archivos .env y .envrc
load_env_files(basedir)


class BaseConfig:
    """
    Configuración base común a todos los entornos.
    """

    # Configuración de seguridad
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    # Configuración de la base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de paginación
    ITEMS_PER_PAGE = 10

    # Configuración de machine learning
    ML_N_CLUSTERS = 5

    # Configuración de archivos
    UPLOAD_FOLDER = "adflux/static/uploads"

    # Configuración CSRF
    WTF_CSRF_ENABLED = True

    # Configuración de Celery
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND") or "redis://localhost:6379/0"

    # Credenciales API Meta
    META_APP_ID = os.environ.get("META_APP_ID")
    META_APP_SECRET = os.environ.get("META_APP_SECRET")
    META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
    META_ACCOUNT_ID = os.environ.get("META_ACCOUNT_ID")
    META_PAGE_ID = os.environ.get("META_PAGE_ID")
    META_AD_ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID")

    # Credenciales API Gemini
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL")

    # Credenciales API Google Ads
    GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
    GOOGLE_ADS_CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    GOOGLE_ADS_CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
    GOOGLE_ADS_REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
    GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    GOOGLE_ADS_USE_PROTO_PLUS = os.environ.get("GOOGLE_ADS_USE_PROTO_PLUS", "True").lower() in (
        "true",
        "1",
        "t",
    )
    GOOGLE_ADS_TARGET_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_TARGET_CUSTOMER_ID")
