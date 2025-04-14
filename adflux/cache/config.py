"""
Configuración de caché para AdFlux.

Este módulo proporciona funciones para configurar la caché en la aplicación.
"""

import logging
import os
from typing import Dict, Any, Optional

from flask import Flask

from .redis_cache import RedisCache
from .cache_manager import CacheManager


# Configurar logger
logger = logging.getLogger(__name__)


def init_cache(app: Flask) -> None:
    """
    Inicializa la caché en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
    """
    # Obtener configuración de caché
    cache_config = get_cache_config(app)
    
    # Verificar si la caché está habilitada
    if not cache_config.get('CACHE_ENABLED', True):
        logger.info("Caché deshabilitada")
        return
    
    try:
        # Crear instancia de RedisCache
        redis_cache = RedisCache(
            host=cache_config.get('REDIS_HOST', 'localhost'),
            port=cache_config.get('REDIS_PORT', 6379),
            db=cache_config.get('REDIS_DB', 0),
            password=cache_config.get('REDIS_PASSWORD'),
            prefix=cache_config.get('CACHE_KEY_PREFIX', 'adflux:'),
            default_timeout=cache_config.get('CACHE_DEFAULT_TIMEOUT', 300),
            serializer=cache_config.get('CACHE_SERIALIZER', 'json')
        )
        
        # Crear gestor de caché
        cache_manager = CacheManager(redis_cache)
        
        # Registrar caché en la aplicación
        app.cache = redis_cache
        app.cache_manager = cache_manager
        
        logger.info("Caché inicializada correctamente")
    
    except Exception as e:
        logger.error(f"Error al inicializar caché: {str(e)}")


def get_cache_config(app: Flask) -> Dict[str, Any]:
    """
    Obtiene la configuración de caché.
    
    Args:
        app: Aplicación Flask
        
    Returns:
        Diccionario con configuración de caché
    """
    # Configuración por defecto
    default_config = {
        'CACHE_ENABLED': True,
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': 6379,
        'REDIS_DB': 0,
        'REDIS_PASSWORD': None,
        'CACHE_KEY_PREFIX': 'adflux:',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_SERIALIZER': 'json'
    }
    
    # Obtener configuración de la aplicación
    config = {}
    for key in default_config:
        if key in app.config:
            config[key] = app.config[key]
        elif key in os.environ:
            # Convertir valores de entorno a tipos adecuados
            value = os.environ[key]
            if key == 'REDIS_PORT':
                config[key] = int(value)
            elif key == 'REDIS_DB':
                config[key] = int(value)
            elif key == 'CACHE_DEFAULT_TIMEOUT':
                config[key] = int(value)
            elif key == 'CACHE_ENABLED':
                config[key] = value.lower() in ('true', '1', 't', 'y', 'yes')
            else:
                config[key] = value
        else:
            config[key] = default_config[key]
    
    return config
