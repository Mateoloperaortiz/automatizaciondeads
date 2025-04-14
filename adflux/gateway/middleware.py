"""
Middleware para el API Gateway.

Este módulo define el middleware utilizado por el API Gateway
para procesar solicitudes y respuestas.
"""

import time
import uuid
from flask import request, g, current_app
from werkzeug.exceptions import TooManyRequests


def register_middleware(app):
    """
    Registra todo el middleware para el API Gateway.
    
    Args:
        app: Aplicación Flask
    """
    # Middleware de request ID
    @app.before_request
    def add_request_id():
        """Añade un ID único a cada solicitud."""
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.start_time = time.time()
    
    # Middleware de logging
    @app.before_request
    def log_request():
        """Registra información sobre la solicitud entrante."""
        current_app.logger.info(
            f"Request {g.request_id}: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
    
    @app.after_request
    def log_response(response):
        """Registra información sobre la respuesta saliente."""
        duration = time.time() - g.start_time
        current_app.logger.info(
            f"Response {g.request_id}: {response.status_code} "
            f"in {duration:.3f}s"
        )
        response.headers['X-Request-ID'] = g.request_id
        return response
    
    # Middleware de rate limiting
    @app.before_request
    def check_rate_limit():
        """
        Verifica si la solicitud excede los límites de tasa.
        
        Este es un ejemplo simple. En producción, se recomienda usar
        una biblioteca como Flask-Limiter.
        """
        # Implementación básica de rate limiting
        # En producción, usar Redis u otra solución distribuida
        if hasattr(app, 'rate_limiter'):
            client_ip = request.remote_addr
            if not app.rate_limiter.is_allowed(client_ip):
                current_app.logger.warning(f"Rate limit exceeded for {client_ip}")
                raise TooManyRequests("Demasiadas solicitudes. Intente más tarde.")
    
    # Middleware de métricas
    @app.before_request
    def start_timer():
        """Inicia el temporizador para medir la duración de la solicitud."""
        g.start_time = time.time()
    
    @app.after_request
    def record_metrics(response):
        """Registra métricas sobre la solicitud y respuesta."""
        if current_app.config.get('ENABLE_METRICS', False):
            duration = time.time() - g.start_time
            # Aquí se registrarían métricas en un sistema como Prometheus
            # Por ejemplo:
            # request_duration.observe(duration)
            # request_count.inc()
            # if 400 <= response.status_code < 500:
            #     client_error_count.inc()
            # elif 500 <= response.status_code < 600:
            #     server_error_count.inc()
        return response
    
    # Middleware de CORS
    @app.after_request
    def add_cors_headers(response):
        """Añade cabeceras CORS a la respuesta."""
        # Esto es redundante si se usa Flask-CORS, pero se incluye como ejemplo
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    # Middleware de manejo de errores
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Maneja excepciones no capturadas."""
        current_app.logger.error(f"Error no capturado: {str(e)}", exc_info=True)
        
        # Determinar código de estado
        status_code = 500
        if hasattr(e, 'code'):
            status_code = e.code
        
        # Crear respuesta de error
        response = {
            'error': True,
            'message': str(e),
            'status_code': status_code,
            'request_id': getattr(g, 'request_id', 'unknown')
        }
        
        return response, status_code
