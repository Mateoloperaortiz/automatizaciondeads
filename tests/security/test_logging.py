"""
Pruebas para logging de seguridad en AdFlux.

Este módulo contiene pruebas para verificar la funcionalidad de logging
de seguridad implementada en AdFlux.
"""

import pytest
import logging
import json
import os
from unittest.mock import patch, MagicMock, mock_open

from adflux.security.logging import (
    SecurityLogFormatter, setup_security_logging, log_security_event,
    log_authentication_event, log_authorization_event, log_data_access_event,
    log_security_violation
)


@pytest.mark.security
class TestSecurityLogging:
    """Pruebas para logging de seguridad."""
    
    def test_security_log_formatter(self):
        """Prueba el formateador de logs de seguridad."""
        # Crear formateador
        formatter = SecurityLogFormatter('%(levelname)s - %(message)s')
        
        # Crear registro de log
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # Formatear registro
        formatted = formatter.format(record)
        
        # Verificar formato
        assert 'INFO - Test message' in formatted
        
        # Verificar que se añaden atributos adicionales
        assert hasattr(record, 'ip')
        assert hasattr(record, 'method')
        assert hasattr(record, 'path')
        assert hasattr(record, 'user_agent')
        assert hasattr(record, 'user_id')
        assert hasattr(record, 'username')
    
    @patch('adflux.security.logging.logging.handlers.RotatingFileHandler')
    def test_setup_security_logging(self, mock_handler, app, client):
        """Prueba la configuración de logging de seguridad."""
        # Configurar logging de seguridad
        setup_security_logging(app, log_dir='test_logs')
        
        # Verificar que se crearon los manejadores
        assert mock_handler.call_count == 2
        
        # Definir ruta de prueba
        @app.route('/test-logging')
        def test_logging():
            return {'message': 'Test'}
        
        # Hacer solicitud
        response = client.get('/test-logging')
        assert response.status_code == 200
    
    @patch('adflux.security.logging.logging.LogRecord')
    @patch('adflux.security.logging.logging.getLogger')
    def test_log_security_event(self, mock_get_logger, mock_log_record):
        """Prueba la función log_security_event."""
        # Configurar mocks
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_record = MagicMock()
        mock_log_record.return_value = mock_record
        
        # Registrar evento
        log_security_event(
            event_type='test_event',
            message='Test security event',
            data={'key': 'value'},
            level='warning'
        )
        
        # Verificar que se creó el registro
        mock_log_record.assert_called_once()
        
        # Verificar nivel de log
        assert mock_log_record.call_args[1]['level'] == logging.WARNING
        
        # Verificar mensaje
        assert 'Test security event' in mock_log_record.call_args[1]['msg']
        
        # Verificar datos adicionales
        assert hasattr(mock_record, 'data')
        assert mock_record.data == {'key': 'value'}
    
    @patch('adflux.security.logging.log_security_event')
    def test_log_authentication_event(self, mock_log_security_event):
        """Prueba la función log_authentication_event."""
        # Registrar evento de autenticación
        log_authentication_event(
            event='login',
            user_id=1,
            username='testuser',
            success=True,
            details={'ip': '127.0.0.1'}
        )
        
        # Verificar que se llamó a log_security_event
        mock_log_security_event.assert_called_once()
        
        # Verificar argumentos
        args = mock_log_security_event.call_args[1]
        assert args['event_type'] == 'authentication'
        assert 'login' in args['message']
        assert args['data']['user_id'] == 1
        assert args['data']['username'] == 'testuser'
        assert args['data']['success'] is True
        assert args['data']['ip'] == '127.0.0.1'
        assert args['level'] == 'info'
        
        # Registrar evento fallido
        mock_log_security_event.reset_mock()
        log_authentication_event(
            event='login',
            user_id=1,
            username='testuser',
            success=False
        )
        
        # Verificar nivel de log para evento fallido
        assert mock_log_security_event.call_args[1]['level'] == 'warning'
    
    @patch('adflux.security.logging.log_security_event')
    def test_log_authorization_event(self, mock_log_security_event):
        """Prueba la función log_authorization_event."""
        # Registrar evento de autorización
        log_authorization_event(
            event='access_denied',
            user_id=1,
            username='testuser',
            resource='admin_panel',
            action='view',
            success=False
        )
        
        # Verificar que se llamó a log_security_event
        mock_log_security_event.assert_called_once()
        
        # Verificar argumentos
        args = mock_log_security_event.call_args[1]
        assert args['event_type'] == 'authorization'
        assert 'access_denied' in args['message']
        assert args['data']['user_id'] == 1
        assert args['data']['username'] == 'testuser'
        assert args['data']['resource'] == 'admin_panel'
        assert args['data']['action'] == 'view'
        assert args['data']['success'] is False
        assert args['level'] == 'warning'
    
    @patch('adflux.security.logging.log_security_event')
    def test_log_data_access_event(self, mock_log_security_event):
        """Prueba la función log_data_access_event."""
        # Registrar evento de acceso a datos
        log_data_access_event(
            event='read',
            user_id=1,
            username='testuser',
            resource='users',
            resource_id='2',
            action='view'
        )
        
        # Verificar que se llamó a log_security_event
        mock_log_security_event.assert_called_once()
        
        # Verificar argumentos
        args = mock_log_security_event.call_args[1]
        assert args['event_type'] == 'data_access'
        assert 'read' in args['message']
        assert args['data']['user_id'] == 1
        assert args['data']['username'] == 'testuser'
        assert args['data']['resource'] == 'users'
        assert args['data']['resource_id'] == '2'
        assert args['data']['action'] == 'view'
        assert args['level'] == 'info'
    
    @patch('adflux.security.logging.log_security_event')
    def test_log_security_violation(self, mock_log_security_event):
        """Prueba la función log_security_violation."""
        # Registrar violación de seguridad
        log_security_violation(
            event='xss',
            severity='critical',
            details={'payload': '<script>alert("XSS")</script>'}
        )
        
        # Verificar que se llamó a log_security_event
        mock_log_security_event.assert_called_once()
        
        # Verificar argumentos
        args = mock_log_security_event.call_args[1]
        assert args['event_type'] == 'security_violation'
        assert 'xss' in args['message']
        assert args['data']['severity'] == 'critical'
        assert args['data']['payload'] == '<script>alert("XSS")</script>'
        assert args['level'] == 'critical'
