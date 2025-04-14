"""
Pruebas para rate limiting en AdFlux.

Este módulo contiene pruebas para verificar la funcionalidad de rate limiting
implementada en AdFlux.
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from flask import g

from adflux.security.rate_limiting import RateLimiter, setup_rate_limiting, rate_limit


@pytest.mark.security
class TestRateLimiting:
    """Pruebas para rate limiting."""
    
    def test_rate_limiter(self, mock_redis):
        """Prueba la clase RateLimiter."""
        # Crear limitador de tasa
        limiter = RateLimiter(mock_redis)
        
        # Verificar solicitud permitida
        assert limiter.is_allowed('test_key', 5, 60) is True
        
        # Verificar contador
        assert mock_redis.get('rate_limit:test_key') == 1
        
        # Verificar solicitudes adicionales
        for i in range(2, 6):
            assert limiter.is_allowed('test_key', 5, 60) is True
            assert mock_redis.get('rate_limit:test_key') == i
        
        # Verificar límite excedido
        assert limiter.is_allowed('test_key', 5, 60) is False
        assert mock_redis.get('rate_limit:test_key') == 5
    
    def test_get_remaining(self, mock_redis):
        """Prueba el método get_remaining de RateLimiter."""
        # Crear limitador de tasa
        limiter = RateLimiter(mock_redis)
        
        # Verificar solicitudes restantes para clave nueva
        assert limiter.get_remaining('new_key', 10) == 10
        
        # Establecer contador
        mock_redis.set('rate_limit:new_key', 3)
        
        # Verificar solicitudes restantes
        assert limiter.get_remaining('new_key', 10) == 7
        
        # Establecer contador mayor que el límite
        mock_redis.set('rate_limit:new_key', 15)
        
        # Verificar solicitudes restantes
        assert limiter.get_remaining('new_key', 10) == 0
    
    def test_get_reset_time(self, mock_redis):
        """Prueba el método get_reset_time de RateLimiter."""
        # Crear limitador de tasa
        limiter = RateLimiter(mock_redis)
        
        # Establecer clave con tiempo de expiración
        mock_redis.set('rate_limit:expire_key', 1, ex=60)
        
        # Verificar tiempo de restablecimiento
        assert limiter.get_reset_time('expire_key') <= 60
        assert limiter.get_reset_time('expire_key') > 0
        
        # Verificar clave inexistente
        assert limiter.get_reset_time('nonexistent_key') == 0
    
    def test_setup_rate_limiting(self, app, client, mock_redis):
        """Prueba la configuración de rate limiting en la aplicación."""
        # Configurar aplicación con Redis
        app.redis = mock_redis
        
        # Configurar rate limiting
        setup_rate_limiting(app)
        
        # Verificar que se creó el limitador de tasa
        assert hasattr(app, 'rate_limiter')
        
        # Definir ruta de prueba
        @app.route('/test-rate-limit')
        def test_rate_limit():
            return {'message': 'Test'}
        
        # Hacer solicitudes
        for i in range(5):
            response = client.get('/test-rate-limit')
            assert response.status_code == 200
            
            # Verificar cabeceras de rate limiting
            assert 'X-RateLimit-Limit' in response.headers
            assert 'X-RateLimit-Remaining' in response.headers
            assert 'X-RateLimit-Reset' in response.headers
    
    def test_rate_limit_decorator(self, app, client, mock_redis):
        """Prueba el decorador rate_limit."""
        # Configurar aplicación con Redis
        app.redis = mock_redis
        
        # Configurar rate limiting
        setup_rate_limiting(app)
        
        # Definir ruta con rate limiting
        @app.route('/limited')
        @rate_limit(limit=3, period=60)
        def limited():
            return {'message': 'Limited'}
        
        # Hacer solicitudes permitidas
        for i in range(3):
            response = client.get('/limited')
            assert response.status_code == 200
            assert response.json['message'] == 'Limited'
        
        # Hacer solicitud que excede el límite
        response = client.get('/limited')
        assert response.status_code == 429
        assert 'error' in response.json
        assert 'Rate limit excedido' in response.json['error']
        
        # Verificar cabeceras
        assert 'Retry-After' in response.headers
        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-RateLimit-Remaining' in response.headers
        assert 'X-RateLimit-Reset' in response.headers
        assert response.headers['X-RateLimit-Remaining'] == '0'
    
    def test_rate_limit_with_custom_key(self, app, client, mock_redis):
        """Prueba el decorador rate_limit con función de clave personalizada."""
        # Configurar aplicación con Redis
        app.redis = mock_redis
        
        # Configurar rate limiting
        setup_rate_limiting(app)
        
        # Función de clave personalizada
        def custom_key_func(*args, **kwargs):
            return f"custom:{kwargs.get('user_id', 'anonymous')}"
        
        # Definir ruta con rate limiting y clave personalizada
        @app.route('/user-limited/<user_id>')
        @rate_limit(limit=2, period=60, key_func=custom_key_func)
        def user_limited(user_id):
            return {'message': f'Limited for user {user_id}'}
        
        # Hacer solicitudes para usuario 1
        for i in range(2):
            response = client.get('/user-limited/1')
            assert response.status_code == 200
        
        # Verificar límite excedido para usuario 1
        response = client.get('/user-limited/1')
        assert response.status_code == 429
        
        # Verificar que usuario 2 no está afectado
        response = client.get('/user-limited/2')
        assert response.status_code == 200
