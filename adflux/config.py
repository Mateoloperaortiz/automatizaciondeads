import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env')) # Cargar .env desde la raíz del proyecto

class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Añadir otras configuraciones por defecto
    ITEMS_PER_PAGE = 10 # Elementos de paginación por defecto
    ML_N_CLUSTERS = 5 # Número de segmentos por defecto para K-means
    UPLOAD_FOLDER = 'adflux/static/uploads' # Definir ruta de la carpeta de subidas

    # Configuración de la base de datos (usar DATABASE_URL desde .env)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'adflux.db')

    # Configuración de Celery (Ejemplo - ajustar según sea necesario)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

    # Credenciales API Meta (Cargadas vía load_dotenv)
    META_APP_ID = os.environ.get('META_APP_ID')
    META_APP_SECRET = os.environ.get('META_APP_SECRET')
    META_ACCESS_TOKEN = os.environ.get('META_ACCESS_TOKEN')
    META_ACCOUNT_ID = os.environ.get('META_ACCOUNT_ID')
    META_PAGE_ID = os.environ.get('META_PAGE_ID')
    META_AD_ACCOUNT_ID = os.environ.get('META_AD_ACCOUNT_ID')

    # Credenciales API Gemini
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL')

    # Credenciales API Google Ads
    GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN')
    GOOGLE_ADS_CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID')
    GOOGLE_ADS_CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
    GOOGLE_ADS_REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN')
    GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
    # Convertir string 'True'/'False' de var env a booleano
    GOOGLE_ADS_USE_PROTO_PLUS = os.environ.get('GOOGLE_ADS_USE_PROTO_PLUS', 'True').lower() in ('true', '1', 't')
    # Añadir el ID de cliente objetivo
    GOOGLE_ADS_TARGET_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_TARGET_CUSTOMER_ID')


class DevelopmentConfig(Config):
    """Configuración de desarrollo."""
    DEBUG = True
    SQLALCHEMY_ECHO = False # Establecer a True para registrar consultas SQL

class TestingConfig(Config):
    """Configuración de pruebas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Usar DB en memoria para pruebas
    WTF_CSRF_ENABLED = False # Deshabilitar validación de formularios CSRF en pruebas

class ProductionConfig(Config):
    """Configuración de producción."""
    DEBUG = False
    TESTING = False
    # Añadir configuraciones específicas de producción como logging, cabeceras de seguridad, etc.

# Diccionario para acceder a las clases de configuración por nombre
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
