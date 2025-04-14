"""
Decoradores para caché.

Este módulo proporciona decoradores para facilitar el uso de caché.
"""

import hashlib
import inspect
import json
import logging
import functools
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, TypeVar, cast

from flask import current_app, request


# Configurar logger
logger = logging.getLogger(__name__)


# Tipo para funciones
F = TypeVar('F', bound=Callable[..., Any])


def cache_key(*args, **kwargs) -> str:
    """
    Genera una clave de caché a partir de argumentos.
    
    Args:
        *args: Argumentos posicionales
        **kwargs: Argumentos con nombre
        
    Returns:
        Clave de caché
    """
    # Convertir argumentos a cadenas
    args_str = ','.join(str(arg) for arg in args)
    kwargs_str = ','.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    # Combinar argumentos
    key_str = f"{args_str}:{kwargs_str}"
    
    # Generar hash para claves largas
    if len(key_str) > 100:
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    return key_str


def cached(
    timeout: int = 300,
    key_prefix: str = "",
    unless: Optional[Callable[..., bool]] = None,
    cache_type: str = 'data'
) -> Callable[[F], F]:
    """
    Decorador que cachea el resultado de una función.
    
    Args:
        timeout: Tiempo de vida de la caché en segundos
        key_prefix: Prefijo para la clave de caché
        unless: Función que determina si no se debe cachear el resultado
        cache_type: Tipo de caché a utilizar ('api', 'view', 'data', 'fragment')
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verificar si hay caché disponible
            if not hasattr(current_app, 'cache_manager'):
                # Si no hay caché, ejecutar la función normalmente
                return func(*args, **kwargs)
            
            # Verificar si no se debe cachear
            if unless and unless(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Generar clave de caché
            func_name = f"{func.__module__}.{func.__name__}"
            cache_args = cache_key(*args, **kwargs)
            cache_key_str = f"{key_prefix}:{func_name}:{cache_args}"
            
            # Obtener gestor de caché
            cache_manager = current_app.cache_manager
            
            # Intentar obtener resultado de la caché
            if cache_type == 'api':
                cached_result = cache_manager.get_api_cache(cache_key_str)
            elif cache_type == 'view':
                cached_result = cache_manager.get_view_cache(cache_key_str)
            elif cache_type == 'fragment':
                cached_result = cache_manager.get_fragment_cache(cache_key_str)
            else:  # data
                cached_result = cache_manager.get_data_cache(cache_key_str)
            
            if cached_result is not None:
                logger.debug(f"Resultado obtenido de la caché para {func_name}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            
            # Almacenar resultado en caché
            if cache_type == 'api':
                cache_manager.set_api_cache(cache_key_str, result, timeout)
            elif cache_type == 'view':
                cache_manager.set_view_cache(cache_key_str, result, timeout)
            elif cache_type == 'fragment':
                cache_manager.set_fragment_cache(cache_key_str, result, timeout)
            else:  # data
                cache_manager.set_data_cache(cache_key_str, result, timeout)
            
            return result
        
        return cast(F, wrapper)
    
    return decorator


def invalidate_cache(
    key_pattern: str,
    cache_type: str = 'data'
) -> Callable[[F], F]:
    """
    Decorador que invalida la caché después de ejecutar una función.
    
    Args:
        key_pattern: Patrón de claves a invalidar
        cache_type: Tipo de caché a invalidar ('api', 'view', 'data', 'fragment')
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Verificar si hay caché disponible
            if not hasattr(current_app, 'cache_manager'):
                return result
            
            # Obtener gestor de caché
            cache_manager = current_app.cache_manager
            
            # Invalidar caché
            if cache_type == 'api':
                cache_manager.redis_cache.flush(f"api:{key_pattern}")
            elif cache_type == 'view':
                cache_manager.redis_cache.flush(f"view:{key_pattern}")
            elif cache_type == 'fragment':
                cache_manager.redis_cache.flush(f"fragment:{key_pattern}")
            else:  # data
                cache_manager.redis_cache.flush(f"data:{key_pattern}")
            
            logger.debug(f"Caché invalidada para patrón {key_pattern}")
            
            return result
        
        return cast(F, wrapper)
    
    return decorator
