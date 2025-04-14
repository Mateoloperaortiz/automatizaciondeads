"""
Pruebas para cabeceras de seguridad y CORS en AdFlux.

Este módulo contiene pruebas para verificar la configuración de cabeceras
de seguridad y CORS en AdFlux.
"""

import pytest
from unittest.mock import patch, MagicMock

from adflux.security.headers import setup_security_headers, get_csp_report_uri, setup_csp_reporting
from adflux.security.cors import setup_cors, validate_origin, get_cors_headers, add_cors_headers


@pytest.mark.security
class TestSecurityHeaders:
    """Pruebas para cabeceras de seguridad HTTP."""
    
    def test_security_headers_middleware(self, app, client):
        """Prueba que las cabeceras de seguridad se añaden a las respuestas."""
        # Configurar cabeceras de seguridad
        setup_security_headers(app)
        
        # Definir ruta de prueba
        @app.route('/test-headers')
        def test_headers():
            return {'message': 'Test'}
        
        # Hacer solicitud
        response = client.get('/test-headers')
        
        # Verificar cabeceras de seguridad
        assert 'Content-Security-Policy' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'Referrer-Policy' in response.headers
        assert 'Permissions-Policy' in response.headers
        
        # Verificar valores de cabeceras
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
        assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'
    
    def test_content_security_policy(self, app, client):
        """Prueba la configuración de Content Security Policy."""
        # Configurar cabeceras de seguridad
        setup_security_headers(app)
        
        # Definir ruta de prueba
        @app.route('/test-csp')
        def test_csp():
            return {'message': 'Test'}
        
        # Hacer solicitud
        response = client.get('/test-csp')
        
        # Verificar cabecera CSP
        assert 'Content-Security-Policy' in response.headers
        
        csp = response.headers['Content-Security-Policy']
        
        # Verificar directivas CSP
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "style-src" in csp
        assert "img-src" in csp
        assert "font-src" in csp
        assert "connect-src" in csp
        assert "frame-src" in csp
        assert "object-src 'none'" in csp
        assert "base-uri 'self'" in csp
        assert "form-action 'self'" in csp
        assert "frame-ancestors 'self'" in csp
    
    def test_csp_reporting(self, app, client):
        """Prueba la configuración de reportes CSP."""
        # Configurar reportes CSP
        setup_csp_reporting(app)
        
        # Verificar URI de reportes
        report_uri = get_csp_report_uri()
        assert report_uri == '/api/security/csp-report'
        
        # Hacer solicitud al endpoint de reportes
        report_data = {
            'csp-report': {
                'document-uri': 'https://example.com',
                'violated-directive': 'script-src',
                'blocked-uri': 'https://malicious.com/script.js'
            }
        }
        
        response = client.post('/api/security/csp-report', json=report_data)
        
        # Verificar respuesta
        assert response.status_code == 204


@pytest.mark.security
class TestCORS:
    """Pruebas para configuración CORS."""
    
    def test_cors_configuration(self, app, client):
        """Prueba la configuración de CORS."""
        # Configurar CORS con orígenes específicos
        allowed_origins = ['https://example.com', 'https://test.com']
        setup_cors(app, allowed_origins)
        
        # Definir ruta de prueba
        @app.route('/test-cors')
        def test_cors():
            return {'message': 'Test'}
        
        # Hacer solicitud con origen permitido
        headers = {'Origin': 'https://example.com'}
        response = client.get('/test-cors', headers=headers)
        
        # Verificar cabeceras CORS
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == 'https://example.com'
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
        assert 'Access-Control-Expose-Headers' in response.headers
        
        # Hacer solicitud con origen no permitido
        headers = {'Origin': 'https://malicious.com'}
        response = client.get('/test-cors', headers=headers)
        
        # Verificar que no se añaden cabeceras CORS
        assert 'Access-Control-Allow-Origin' not in response.headers or response.headers['Access-Control-Allow-Origin'] != 'https://malicious.com'
    
    def test_validate_origin(self):
        """Prueba la validación de orígenes."""
        # Orígenes permitidos
        allowed_origins = ['https://example.com', 'https://*.test.com']
        
        # Verificar orígenes válidos
        assert validate_origin('https://example.com', allowed_origins) is True
        
        # Verificar orígenes inválidos
        assert validate_origin('https://malicious.com', allowed_origins) is False
        
        # Verificar orígenes con comodines
        assert validate_origin('https://sub.test.com', allowed_origins) is True
    
    def test_get_cors_headers(self):
        """Prueba la generación de cabeceras CORS."""
        # Generar cabeceras para origen permitido
        headers = get_cors_headers(
            origin='https://example.com',
            allowed_origins=['https://example.com'],
            allowed_methods=['GET', 'POST'],
            allowed_headers=['Content-Type', 'Authorization'],
            expose_headers=['X-Pagination-Total'],
            max_age=3600,
            allow_credentials=True
        )
        
        # Verificar cabeceras
        assert headers['Access-Control-Allow-Origin'] == 'https://example.com'
        assert headers['Access-Control-Allow-Methods'] == 'GET, POST'
        assert headers['Access-Control-Allow-Headers'] == 'Content-Type, Authorization'
        assert headers['Access-Control-Expose-Headers'] == 'X-Pagination-Total'
        assert headers['Access-Control-Max-Age'] == '3600'
        assert headers['Access-Control-Allow-Credentials'] == 'true'
        
        # Generar cabeceras para origen no permitido
        headers = get_cors_headers(
            origin='https://malicious.com',
            allowed_origins=['https://example.com']
        )
        
        # Verificar que no se generan cabeceras
        assert headers == {}
