"""
Rate limiting para AdFlux.

Este módulo proporciona funciones para limitar la tasa de solicitudes,
previniendo ataques de fuerza bruta, DDoS, etc.
"""

import time
import logging
import functools
from typing import Callable, Dict, Any, Optional, Union, TypeVar, cast

from flask import Flask, request, jsonify, current_app, g
from redis import Redis


# Configurar logger
logger = logging.getLogger(__name__)


# Tipo para funciones
F = TypeVar('F', bound=Callable[..., Any])


class RateLimiter:
    """
    Limitador de tasa utilizando Redis.
    
    Implementa el algoritmo de token bucket para limitar la tasa de solicitudes.
    """
    
    def __init__(self, redis_client: Redis, key_prefix: str = 'rate_limit:'):
        """
        Inicializa el limitador de tasa.
        
        Args:
            redis_client: Cliente Redis
            key_prefix: Prefijo para las claves en Redis
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
    
    def is_allowed(self, key: str, limit: int, period: int) -> bool:
        """
        Verifica si una solicitud está permitida según el límite de tasa.
        
        Args:
            key: Clave única para identificar al cliente
            limit: Número máximo de solicitudes permitidas en el período
            period: Período de tiempo en segundos
            
        Returns:
            True si la solicitud está permitida, False en caso contrario
        """
        # Construir clave completa
        redis_key = f"{self.key_prefix}{key}"
        
        # Obtener contador actual y tiempo de expiración
        current_count = self.redis.get(redis_key)
        
        if current_count is None:
            # Primera solicitud, establecer contador a 1
            self.redis.set(redis_key, 1, ex=period)
            return True
        
        # Incrementar contador
        current_count = int(current_count)
        
        if current_count >= limit:
            # Límite excedido
            return False
        
        # Incrementar contador
        self.redis.incr(redis_key)
        
        return True
    
    def get_remaining(self, key: str, limit: int) -> int:
        """
        Obtiene el número de solicitudes restantes.
        
        Args:
            key: Clave única para identificar al cliente
            limit: Número máximo de solicitudes permitidas
            
        Returns:
            Número de solicitudes restantes
        """
        # Construir clave completa
        redis_key = f"{self.key_prefix}{key}"
        
        # Obtener contador actual
        current_count = self.redis.get(redis_key)
        
        if current_count is None:
            return limit
        
        # Calcular solicitudes restantes
        remaining = max(0, limit - int(current_count))
        
        return remaining
    
    def get_reset_time(self, key: str) -> int:
        """
        Obtiene el tiempo restante hasta que se restablezca el límite.
        
        Args:
            key: Clave única para identificar al cliente
            
        Returns:
            Tiempo restante en segundos
        """
        # Construir clave completa
        redis_key = f"{self.key_prefix}{key}"
        
        # Obtener tiempo de expiración
        ttl = self.redis.ttl(redis_key)
        
        if ttl < 0:
            return 0
        
        return ttl


def setup_rate_limiting(app: Flask) -> None:
    """
    Configura rate limiting en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
    """
    # Verificar si hay cliente Redis disponible
    if not hasattr(app, 'redis'):
        logger.warning("No se encontró cliente Redis, rate limiting no estará disponible")
        return
    
    # Crear limitador de tasa
    app.rate_limiter = RateLimiter(app.redis)
    
    # Configurar middleware para rate limiting global
    @app.before_request
    def check_rate_limit():
        """
        Verifica el límite de tasa antes de procesar una solicitud.
        """
        # Ignorar solicitudes a rutas estáticas
        if request.path.startswith('/static'):
            return None
        
        # Obtener dirección IP del cliente
        client_ip = request.remote_addr
        
        # Obtener límites de tasa
        global_limit = app.config.get('RATE_LIMIT_GLOBAL', 1000)
        global_period = app.config.get('RATE_LIMIT_PERIOD', 3600)  # 1 hora
        
        # Verificar límite global
        if not app.rate_limiter.is_allowed(f"global:{client_ip}", global_limit, global_period):
            logger.warning(f"Rate limit global excedido para IP {client_ip}")
            
            # Obtener tiempo de restablecimiento
            reset_time = app.rate_limiter.get_reset_time(f"global:{client_ip}")
            
            # Establecer cabeceras de rate limiting
            response = jsonify({
                'error': 'Rate limit excedido',
                'message': 'Has excedido el límite de solicitudes permitidas'
            })
            response.status_code = 429
            response.headers['Retry-After'] = str(reset_time)
            response.headers['X-RateLimit-Limit'] = str(global_limit)
            response.headers['X-RateLimit-Remaining'] = '0'
            response.headers['X-RateLimit-Reset'] = str(int(time.time()) + reset_time)
            
            return response
        
        # Almacenar información de rate limiting en g
        g.rate_limit = {
            'global_limit': global_limit,
            'global_remaining': app.rate_limiter.get_remaining(f"global:{client_ip}", global_limit),
            'global_reset': app.rate_limiter.get_reset_time(f"global:{client_ip}")
        }
        
        return None
    
    # Añadir cabeceras de rate limiting a las respuestas
    @app.after_request
    def add_rate_limit_headers(response):
        """
        Añade cabeceras de rate limiting a las respuestas.
        
        Args:
            response: Respuesta HTTP
            
        Returns:
            Respuesta HTTP con cabeceras de rate limiting
        """
        if hasattr(g, 'rate_limit'):
            response.headers['X-RateLimit-Limit'] = str(g.rate_limit['global_limit'])
            response.headers['X-RateLimit-Remaining'] = str(g.rate_limit['global_remaining'])
            response.headers['X-RateLimit-Reset'] = str(int(time.time()) + g.rate_limit['global_reset'])
        
        return response
    
    logger.info("Rate limiting configurado")


def rate_limit(limit: int, period: int = 60, key_func: Optional[Callable[..., str]] = None) -> Callable[[F], F]:
    """
    Decorador para aplicar rate limiting a una ruta específica.
    
    Args:
        limit: Número máximo de solicitudes permitidas en el período
        period: Período de tiempo en segundos
        key_func: Función para generar la clave de rate limiting (opcional)
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verificar si hay limitador de tasa disponible
            if not hasattr(current_app, 'rate_limiter'):
                return func(*args, **kwargs)
            
            # Obtener dirección IP del cliente
            client_ip = request.remote_addr
            
            # Generar clave de rate limiting
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Usar endpoint y dirección IP como clave por defecto
                endpoint = request.endpoint or 'unknown'
                key = f"{endpoint}:{client_ip}"
            
            # Verificar límite de tasa
            if not current_app.rate_limiter.is_allowed(key, limit, period):
                logger.warning(f"Rate limit excedido para {key}")
                
                # Obtener tiempo de restablecimiento
                reset_time = current_app.rate_limiter.get_reset_time(key)
                
                # Establecer cabeceras de rate limiting
                response = jsonify({
                    'error': 'Rate limit excedido',
                    'message': 'Has excedido el límite de solicitudes permitidas'
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(reset_time)
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(int(time.time()) + reset_time)
                
                return response
            
            # Almacenar información de rate limiting en g
            if not hasattr(g, 'rate_limit_routes'):
                g.rate_limit_routes = {}
            
            g.rate_limit_routes[key] = {
                'limit': limit,
                'remaining': current_app.rate_limiter.get_remaining(key, limit),
                'reset': current_app.rate_limiter.get_reset_time(key)
            }
            
            # Ejecutar función
            return func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator
