"""
Decoradores de utilidad para AdFlux.

Este módulo proporciona decoradores que pueden ser utilizados para
añadir funcionalidad a funciones y métodos en diferentes partes de la aplicación.
"""

import time
import functools
import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast
from datetime import datetime, timedelta

from flask import current_app, g, request, jsonify
from werkzeug.exceptions import HTTPException

# Configurar logger
logger = logging.getLogger(__name__)

# Tipo para funciones
F = TypeVar('F', bound=Callable[..., Any])


def log_execution_time(func: F) -> F:
    """
    Decorador que registra el tiempo de ejecución de una función.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Calcular tiempo de ejecución
        execution_time = end_time - start_time
        
        # Registrar tiempo de ejecución
        logger.debug(
            f"Función {func.__name__} ejecutada en {execution_time:.4f} segundos"
        )
        
        return result
    
    return cast(F, wrapper)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception
) -> Callable[[F], F]:
    """
    Decorador que reintenta una función en caso de error.
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Tiempo de espera inicial entre intentos (en segundos)
        backoff: Factor de incremento del tiempo de espera
        exceptions: Excepciones que deben ser capturadas
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Convertir excepciones a tupla si es una sola excepción
            if isinstance(exceptions, list):
                exception_types = tuple(exceptions)
            else:
                exception_types = (exceptions,)
            
            # Inicializar variables
            attempts = 0
            current_delay = delay
            
            # Intentar ejecutar la función
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exception_types as e:
                    attempts += 1
                    
                    # Si es el último intento, relanzar la excepción
                    if attempts == max_attempts:
                        logger.error(
                            f"Función {func.__name__} falló después de {max_attempts} intentos. "
                            f"Último error: {str(e)}"
                        )
                        raise
                    
                    # Registrar error y esperar
                    logger.warning(
                        f"Intento {attempts}/{max_attempts} de {func.__name__} falló. "
                        f"Error: {str(e)}. Reintentando en {current_delay:.2f} segundos..."
                    )
                    
                    # Esperar antes de reintentar
                    time.sleep(current_delay)
                    
                    # Incrementar tiempo de espera
                    current_delay *= backoff
        
        return cast(F, wrapper)
    
    return decorator


def cache_result(
    ttl: int = 300,
    key_prefix: str = "",
    key_func: Optional[Callable[..., str]] = None
) -> Callable[[F], F]:
    """
    Decorador que cachea el resultado de una función.
    
    Args:
        ttl: Tiempo de vida de la caché en segundos
        key_prefix: Prefijo para la clave de caché
        key_func: Función para generar la clave de caché
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verificar si hay caché disponible
            if not hasattr(current_app, 'cache'):
                # Si no hay caché, ejecutar la función normalmente
                return func(*args, **kwargs)
            
            # Generar clave de caché
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Generar clave basada en la función y sus argumentos
                arg_str = ','.join(str(arg) for arg in args)
                kwarg_str = ','.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{func.__module__}.{func.__name__}:{arg_str}:{kwarg_str}"
            
            # Intentar obtener resultado de la caché
            cached_result = current_app.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Resultado obtenido de la caché para {func.__name__}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            current_app.cache.set(cache_key, result, timeout=ttl)
            
            return result
        
        return cast(F, wrapper)
    
    return decorator


def validate_args(**validators: Callable[[Any], Any]) -> Callable[[F], F]:
    """
    Decorador que valida los argumentos de una función.
    
    Args:
        validators: Diccionario de validadores para cada argumento
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Obtener nombres de argumentos
            arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
            
            # Crear diccionario de argumentos
            all_args = {}
            for i, arg in enumerate(args):
                if i < len(arg_names):
                    all_args[arg_names[i]] = arg
            all_args.update(kwargs)
            
            # Validar argumentos
            for arg_name, validator in validators.items():
                if arg_name in all_args:
                    try:
                        # Aplicar validador
                        all_args[arg_name] = validator(all_args[arg_name])
                    except Exception as e:
                        # Lanzar excepción con mensaje descriptivo
                        raise ValueError(f"Argumento inválido '{arg_name}': {str(e)}")
            
            # Reconstruir argumentos
            new_args = []
            for i, arg_name in enumerate(arg_names):
                if i < len(args):
                    new_args.append(all_args.get(arg_name, args[i]))
            
            new_kwargs = {k: v for k, v in all_args.items() if k not in arg_names[:len(args)]}
            
            # Ejecutar función con argumentos validados
            return func(*new_args, **new_kwargs)
        
        return cast(F, wrapper)
    
    return decorator


def require_auth(roles: Optional[List[str]] = None) -> Callable[[F], F]:
    """
    Decorador que requiere autenticación para acceder a una función.
    
    Args:
        roles: Lista de roles permitidos
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verificar si el usuario está autenticado
            if not hasattr(g, 'user') or not g.user:
                return jsonify({
                    "error": "No autorizado",
                    "message": "Debe iniciar sesión para acceder a este recurso"
                }), 401
            
            # Verificar roles si se especifican
            if roles and not any(role in g.user.roles for role in roles):
                return jsonify({
                    "error": "Prohibido",
                    "message": "No tiene permisos para acceder a este recurso"
                }), 403
            
            # Ejecutar función
            return func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator


def rate_limit(
    limit: int = 100,
    period: int = 60,
    key_func: Optional[Callable[..., str]] = None
) -> Callable[[F], F]:
    """
    Decorador que limita la tasa de llamadas a una función.
    
    Args:
        limit: Número máximo de llamadas permitidas en el período
        period: Período de tiempo en segundos
        key_func: Función para generar la clave de limitación
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verificar si hay caché disponible
            if not hasattr(current_app, 'cache'):
                # Si no hay caché, ejecutar la función normalmente
                return func(*args, **kwargs)
            
            # Generar clave de limitación
            if key_func:
                rate_key = key_func(*args, **kwargs)
            else:
                # Usar IP del cliente como clave por defecto
                client_ip = request.remote_addr or 'unknown'
                rate_key = f"rate_limit:{func.__module__}.{func.__name__}:{client_ip}"
            
            # Obtener contador actual
            counter = current_app.cache.get(rate_key) or 0
            
            # Verificar límite
            if counter >= limit:
                return jsonify({
                    "error": "Demasiadas solicitudes",
                    "message": f"Ha excedido el límite de {limit} solicitudes por {period} segundos"
                }), 429
            
            # Incrementar contador
            current_app.cache.set(rate_key, counter + 1, timeout=period)
            
            # Ejecutar función
            return func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator


def handle_exceptions(
    default_status_code: int = 500,
    default_message: str = "Se produjo un error interno",
    log_traceback: bool = True,
    exceptions: Dict[Type[Exception], int] = None
) -> Callable[[F], F]:
    """
    Decorador que maneja excepciones y devuelve respuestas JSON apropiadas.
    
    Args:
        default_status_code: Código de estado HTTP por defecto
        default_message: Mensaje de error por defecto
        log_traceback: Si se debe registrar el traceback completo
        exceptions: Diccionario de excepciones y códigos de estado
        
    Returns:
        Decorador
    """
    if exceptions is None:
        exceptions = {}
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except HTTPException as e:
                # Manejar excepciones HTTP de Werkzeug
                logger.warning(f"Error HTTP {e.code}: {e.description}")
                return jsonify({
                    "error": e.name,
                    "message": e.description
                }), e.code
            except Exception as e:
                # Determinar código de estado
                status_code = default_status_code
                for exc_type, code in exceptions.items():
                    if isinstance(e, exc_type):
                        status_code = code
                        break
                
                # Registrar error
                if log_traceback:
                    logger.exception(f"Error no manejado en {func.__name__}: {str(e)}")
                else:
                    logger.error(f"Error en {func.__name__}: {str(e)}")
                
                # Devolver respuesta JSON
                return jsonify({
                    "error": e.__class__.__name__,
                    "message": str(e) or default_message
                }), status_code
        
        return cast(F, wrapper)
    
    return decorator
