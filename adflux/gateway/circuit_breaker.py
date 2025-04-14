"""
Circuit Breaker para el API Gateway.

Este módulo implementa el patrón Circuit Breaker para prevenir
cascadas de fallos cuando un servicio no está disponible.
"""

import time
import functools
from enum import Enum
from flask import current_app
from werkzeug.exceptions import ServiceUnavailable


class CircuitState(Enum):
    """Estados posibles del circuit breaker."""
    CLOSED = 'closed'  # Funcionamiento normal
    OPEN = 'open'      # Circuito abierto, no se permiten solicitudes
    HALF_OPEN = 'half_open'  # Permitir algunas solicitudes para probar recuperación


class CircuitBreaker:
    """
    Implementación del patrón Circuit Breaker.
    
    Monitorea fallos en las llamadas a servicios y abre el circuito
    cuando se alcanza un umbral de fallos, previniendo más llamadas
    hasta que el servicio se recupere.
    """
    
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        """
        Inicializa el circuit breaker.
        
        Args:
            failure_threshold: Número de fallos consecutivos para abrir el circuito
            recovery_timeout: Tiempo en segundos antes de intentar recuperación
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.services = {}
    
    def get_breaker(self, service_name):
        """
        Obtiene o crea un circuit breaker para un servicio específico.
        
        Args:
            service_name: Nombre del servicio
            
        Returns:
            Circuit breaker para el servicio
        """
        if service_name not in self.services:
            self.services[service_name] = {
                'state': CircuitState.CLOSED,
                'failure_count': 0,
                'last_failure_time': 0
            }
        return self.services[service_name]
    
    def execute(self, service_name, func, *args, **kwargs):
        """
        Ejecuta una función con protección de circuit breaker.
        
        Args:
            service_name: Nombre del servicio
            func: Función a ejecutar
            *args: Argumentos posicionales para la función
            **kwargs: Argumentos de palabra clave para la función
            
        Returns:
            Resultado de la función
            
        Raises:
            ServiceUnavailable: Si el circuito está abierto
        """
        breaker = self.get_breaker(service_name)
        
        # Verificar si el circuito está abierto
        if breaker['state'] == CircuitState.OPEN:
            # Verificar si ha pasado el tiempo de recuperación
            if time.time() - breaker['last_failure_time'] > self.recovery_timeout:
                current_app.logger.info(f"Circuit breaker para {service_name} cambiando a HALF_OPEN")
                breaker['state'] = CircuitState.HALF_OPEN
            else:
                current_app.logger.warning(f"Circuit breaker para {service_name} está OPEN, rechazando solicitud")
                raise ServiceUnavailable(f"Servicio {service_name} no disponible temporalmente")
        
        try:
            # Ejecutar la función
            result = func(*args, **kwargs)
            
            # Si el circuito estaba medio abierto y la llamada tuvo éxito, cerrarlo
            if breaker['state'] == CircuitState.HALF_OPEN:
                current_app.logger.info(f"Circuit breaker para {service_name} cambiando a CLOSED")
                breaker['state'] = CircuitState.CLOSED
                breaker['failure_count'] = 0
            
            return result
            
        except Exception as e:
            # Registrar el fallo
            breaker['failure_count'] += 1
            breaker['last_failure_time'] = time.time()
            
            # Si se alcanza el umbral de fallos, abrir el circuito
            if breaker['failure_count'] >= self.failure_threshold:
                if breaker['state'] != CircuitState.OPEN:
                    current_app.logger.warning(
                        f"Circuit breaker para {service_name} cambiando a OPEN "
                        f"después de {breaker['failure_count']} fallos"
                    )
                    breaker['state'] = CircuitState.OPEN
            
            # Re-lanzar la excepción
            raise


# Instancia global del circuit breaker
_circuit_breaker = None


def get_circuit_breaker():
    """
    Obtiene la instancia global del circuit breaker.
    
    Returns:
        Instancia del circuit breaker
    """
    global _circuit_breaker
    if _circuit_breaker is None:
        failure_threshold = current_app.config.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5)
        recovery_timeout = current_app.config.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 30)
        _circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
    return _circuit_breaker


def circuit_breaker(func):
    """
    Decorador que aplica el patrón Circuit Breaker a una función.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @functools.wraps(func)
    def wrapper(service_name, *args, **kwargs):
        breaker = get_circuit_breaker()
        return breaker.execute(service_name, func, service_name, *args, **kwargs)
    return wrapper
