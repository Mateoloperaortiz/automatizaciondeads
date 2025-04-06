"""
Configuración para la aplicación AdFlux.

Este módulo contiene la configuración para la aplicación AdFlux.
"""

import os


class Config:
    """Configuración base para AdFlux."""
    
    # Configuración de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_insecure')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///adflux.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de archivos
    UPLOADS_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Configuración de anuncios
    DEFAULT_AD_IMAGE_PATH = 'static/images/default_ad.jpg'
    
    # Configuración de Meta Ads
    META_APP_ID = os.environ.get('META_APP_ID', '')
    META_APP_SECRET = os.environ.get('META_APP_SECRET', '')
    META_ACCESS_TOKEN = os.environ.get('META_ACCESS_TOKEN', '')
    META_ACCOUNT_ID = os.environ.get('META_ACCOUNT_ID', '')
    META_PAGE_ID = os.environ.get('META_PAGE_ID', '')
    
    # Configuración de Google Ads
    GOOGLE_ADS_CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID', '')
    GOOGLE_ADS_CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', '')
    GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
    GOOGLE_ADS_REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', '')
    GOOGLE_ADS_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_CUSTOMER_ID', '')
    
    # Configuración de Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-pro')
    
    # Configuración de Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Configuración de APScheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'UTC'
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.environ.get('LOG_FILE', 'adflux.log')
    LOG_TO_CONSOLE = True
    LOG_TO_FILE = False


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    
    DEBUG = True
    TESTING = False
    
    # Configuración de logging
    LOG_LEVEL = 'DEBUG'
    LOG_TO_CONSOLE = True
    LOG_TO_FILE = False


class TestingConfig(Config):
    """Configuración para pruebas."""
    
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Configuración de logging
    LOG_LEVEL = 'DEBUG'
    LOG_TO_CONSOLE = True
    LOG_TO_FILE = False


class ProductionConfig(Config):
    """Configuración para producción."""
    
    DEBUG = False
    TESTING = False
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
    LOG_TO_CONSOLE = True
    LOG_TO_FILE = True


# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
