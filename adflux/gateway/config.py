"""
Configuración del API Gateway.

Este módulo contiene la configuración para el API Gateway de AdFlux.
"""

import os
from datetime import timedelta


class GatewayConfig:
    """Configuración base para el API Gateway."""
    
    # Configuración general
    DEBUG = os.environ.get('GATEWAY_DEBUG', 'False') == 'True'
    SECRET_KEY = os.environ.get('GATEWAY_SECRET_KEY', 'dev-secret-key')
    
    # Configuración de servicios
    SERVICES = {
        'monolith': {
            'url': os.environ.get('MONOLITH_URL', 'http://localhost:5000'),
            'timeout': int(os.environ.get('MONOLITH_TIMEOUT', '30')),
        },
        'auth': {
            'url': os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001'),
            'timeout': int(os.environ.get('AUTH_SERVICE_TIMEOUT', '10')),
        },
        'candidate': {
            'url': os.environ.get('CANDIDATE_SERVICE_URL', 'http://localhost:5002'),
            'timeout': int(os.environ.get('CANDIDATE_SERVICE_TIMEOUT', '20')),
        },
        'job': {
            'url': os.environ.get('JOB_SERVICE_URL', 'http://localhost:5003'),
            'timeout': int(os.environ.get('JOB_SERVICE_TIMEOUT', '20')),
        },
        'campaign': {
            'url': os.environ.get('CAMPAIGN_SERVICE_URL', 'http://localhost:5004'),
            'timeout': int(os.environ.get('CAMPAIGN_SERVICE_TIMEOUT', '30')),
        },
        'ml': {
            'url': os.environ.get('ML_SERVICE_URL', 'http://localhost:5005'),
            'timeout': int(os.environ.get('ML_SERVICE_TIMEOUT', '60')),
        },
        'report': {
            'url': os.environ.get('REPORT_SERVICE_URL', 'http://localhost:5006'),
            'timeout': int(os.environ.get('REPORT_SERVICE_TIMEOUT', '30')),
        },
    }
    
    # Configuración de autenticación
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configuración de rate limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Configuración de caché
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Configuración de circuit breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', '5'))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', '30'))
    
    # Configuración de métricas
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'True') == 'True'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', '9090'))


class DevelopmentConfig(GatewayConfig):
    """Configuración para entorno de desarrollo."""
    
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(GatewayConfig):
    """Configuración para entorno de pruebas."""
    
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(GatewayConfig):
    """Configuración para entorno de producción."""
    
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # En producción, asegurarse de que SECRET_KEY esté configurado
    if os.environ.get('GATEWAY_SECRET_KEY') == 'dev-secret-key':
        raise ValueError('GATEWAY_SECRET_KEY debe ser configurado en producción')
    
    # En producción, asegurarse de que JWT_SECRET_KEY esté configurado
    if os.environ.get('JWT_SECRET_KEY') == 'jwt-secret-key':
        raise ValueError('JWT_SECRET_KEY debe ser configurado en producción')


# Mapeo de configuraciones por entorno
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}


def get_config():
    """
    Obtiene la configuración según el entorno.
    
    Returns:
        Clase de configuración correspondiente al entorno actual
    """
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
