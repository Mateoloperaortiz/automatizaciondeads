"""
Pruebas para el sistema de auditoría de AdFlux.

Este módulo contiene pruebas para verificar la funcionalidad del sistema
de auditoría implementado en AdFlux.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from flask import g, request

from adflux.auth.audit import AuditLog, log_activity, setup_audit_hooks


@pytest.mark.security
class TestAudit:
    """Pruebas para el sistema de auditoría."""
    
    def test_create_audit_log(self, db, admin_user):
        """Prueba la creación de un log de auditoría."""
        # Crear log de auditoría
        audit_log = AuditLog(
            user_id=admin_user.id,
            action='test_action',
            resource_type='test_resource',
            resource_id='123',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            endpoint='/test',
            method='GET',
            status_code=200,
            details={'key': 'value'}
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        # Verificar que el log se creó correctamente
        saved_log = AuditLog.query.filter_by(action='test_action').first()
        assert saved_log is not None
        assert saved_log.user_id == admin_user.id
        assert saved_log.resource_type == 'test_resource'
        assert saved_log.resource_id == '123'
        assert saved_log.ip_address == '127.0.0.1'
        assert saved_log.user_agent == 'Test User Agent'
        assert saved_log.endpoint == '/test'
        assert saved_log.method == 'GET'
        assert saved_log.status_code == 200
        assert saved_log.details == {'key': 'value'}
    
    def test_audit_log_create_method(self, db, admin_user):
        """Prueba el método create de AuditLog."""
        # Crear log de auditoría con el método create
        with patch('adflux.auth.audit.request') as mock_request:
            # Configurar mock de request
            mock_request.remote_addr = '127.0.0.1'
            mock_request.user_agent.string = 'Test User Agent'
            mock_request.path = '/test'
            mock_request.method = 'GET'
            
            # Crear log
            audit_log = AuditLog.create(
                action='create_method',
                user_id=admin_user.id,
                resource_type='test_resource',
                resource_id='123',
                details={'key': 'value'},
                status_code=200
            )
        
        # Verificar que el log se creó correctamente
        assert audit_log.id is not None
        assert audit_log.user_id == admin_user.id
        assert audit_log.action == 'create_method'
        assert audit_log.resource_type == 'test_resource'
        assert audit_log.resource_id == '123'
        assert audit_log.ip_address == '127.0.0.1'
        assert audit_log.user_agent == 'Test User Agent'
        assert audit_log.endpoint == '/test'
        assert audit_log.method == 'GET'
        assert audit_log.status_code == 200
        assert audit_log.details == {'key': 'value'}
        
        # Verificar que se guardó en la base de datos
        saved_log = AuditLog.query.filter_by(action='create_method').first()
        assert saved_log is not None
        assert saved_log.id == audit_log.id
    
    def test_audit_log_search(self, db, admin_user):
        """Prueba el método search de AuditLog."""
        # Crear varios logs de auditoría
        for i in range(5):
            AuditLog.create(
                action=f'search_test_{i}',
                user_id=admin_user.id,
                resource_type='test_resource',
                resource_id=str(i),
                status_code=200
            )
        
        # Buscar logs por usuario
        logs = AuditLog.search(user_id=admin_user.id)
        assert len(logs) == 5
        
        # Buscar logs por acción
        logs = AuditLog.search(action='search_test_2')
        assert len(logs) == 1
        assert logs[0].action == 'search_test_2'
        
        # Buscar logs por tipo de recurso
        logs = AuditLog.search(resource_type='test_resource')
        assert len(logs) == 5
        
        # Buscar logs por ID de recurso
        logs = AuditLog.search(resource_id='3')
        assert len(logs) == 1
        assert logs[0].resource_id == '3'
        
        # Buscar logs por fecha
        start_date = datetime.utcnow() - timedelta(hours=1)
        end_date = datetime.utcnow() + timedelta(hours=1)
        logs = AuditLog.search(start_date=start_date, end_date=end_date)
        assert len(logs) == 5
        
        # Buscar logs con límite
        logs = AuditLog.search(limit=2)
        assert len(logs) == 2
        
        # Buscar logs con desplazamiento
        logs = AuditLog.search(offset=2, limit=2)
        assert len(logs) == 2
        assert logs[0].resource_id != '0'  # Los primeros dos están omitidos
    
    def test_get_user_activity(self, db, admin_user, regular_user):
        """Prueba el método get_user_activity de AuditLog."""
        # Crear logs para diferentes usuarios
        for i in range(3):
            AuditLog.create(
                action=f'admin_activity_{i}',
                user_id=admin_user.id,
                resource_type='test_resource',
                resource_id=str(i),
                status_code=200
            )
        
        for i in range(2):
            AuditLog.create(
                action=f'user_activity_{i}',
                user_id=regular_user.id,
                resource_type='test_resource',
                resource_id=str(i),
                status_code=200
            )
        
        # Obtener actividad del administrador
        admin_logs = AuditLog.get_user_activity(admin_user.id)
        assert len(admin_logs) == 3
        for log in admin_logs:
            assert log.user_id == admin_user.id
            assert log.action.startswith('admin_activity')
        
        # Obtener actividad del usuario regular
        user_logs = AuditLog.get_user_activity(regular_user.id)
        assert len(user_logs) == 2
        for log in user_logs:
            assert log.user_id == regular_user.id
            assert log.action.startswith('user_activity')
    
    def test_get_resource_activity(self, db, admin_user):
        """Prueba el método get_resource_activity de AuditLog."""
        # Crear logs para diferentes recursos
        for i in range(3):
            AuditLog.create(
                action=f'resource1_activity_{i}',
                user_id=admin_user.id,
                resource_type='resource1',
                resource_id='123',
                status_code=200
            )
        
        for i in range(2):
            AuditLog.create(
                action=f'resource2_activity_{i}',
                user_id=admin_user.id,
                resource_type='resource2',
                resource_id='456',
                status_code=200
            )
        
        # Obtener actividad del recurso 1
        resource1_logs = AuditLog.get_resource_activity('resource1', '123')
        assert len(resource1_logs) == 3
        for log in resource1_logs:
            assert log.resource_type == 'resource1'
            assert log.resource_id == '123'
            assert log.action.startswith('resource1_activity')
        
        # Obtener actividad del recurso 2
        resource2_logs = AuditLog.get_resource_activity('resource2', '456')
        assert len(resource2_logs) == 2
        for log in resource2_logs:
            assert log.resource_type == 'resource2'
            assert log.resource_id == '456'
            assert log.action.startswith('resource2_activity')
    
    def test_get_suspicious_activity(self, db, admin_user):
        """Prueba el método get_suspicious_activity de AuditLog."""
        # Crear logs normales
        for i in range(3):
            AuditLog.create(
                action=f'normal_activity_{i}',
                user_id=admin_user.id,
                resource_type='test_resource',
                resource_id=str(i),
                status_code=200
            )
        
        # Crear logs sospechosos
        AuditLog.create(
            action='login',
            user_id=admin_user.id,
            resource_type='auth',
            resource_id='1',
            status_code=401
        )
        
        AuditLog.create(
            action='change_permissions',
            user_id=admin_user.id,
            resource_type='user',
            resource_id='2',
            status_code=200
        )
        
        AuditLog.create(
            action='reset_password',
            user_id=admin_user.id,
            resource_type='user',
            resource_id='3',
            status_code=200
        )
        
        # Obtener actividad sospechosa
        suspicious_logs = AuditLog.get_suspicious_activity()
        assert len(suspicious_logs) == 3
        
        # Verificar que solo se obtienen los logs sospechosos
        actions = [log.action for log in suspicious_logs]
        assert 'login' in actions
        assert 'change_permissions' in actions
        assert 'reset_password' in actions
        
        for action in actions:
            assert not action.startswith('normal_activity')
    
    @patch('adflux.auth.audit.get_jwt_identity')
    def test_log_activity(self, mock_get_jwt_identity, db, admin_user):
        """Prueba la función log_activity."""
        # Configurar mock
        mock_get_jwt_identity.return_value = admin_user.id
        
        # Registrar actividad
        with patch('adflux.auth.audit.request') as mock_request:
            # Configurar mock de request
            mock_request.remote_addr = '127.0.0.1'
            mock_request.user_agent.string = 'Test User Agent'
            mock_request.path = '/test'
            mock_request.method = 'GET'
            
            # Registrar actividad
            log = log_activity(
                action='test_log_activity',
                resource_type='test_resource',
                resource_id='123',
                details={'key': 'value'},
                status_code=200
            )
        
        # Verificar que se creó el log
        assert log.id is not None
        assert log.user_id == admin_user.id
        assert log.action == 'test_log_activity'
        assert log.resource_type == 'test_resource'
        assert log.resource_id == '123'
        assert log.details == {'key': 'value'}
        assert log.status_code == 200
        
        # Verificar que se guardó en la base de datos
        saved_log = AuditLog.query.filter_by(action='test_log_activity').first()
        assert saved_log is not None
        assert saved_log.id == log.id
    
    def test_setup_audit_hooks(self, app, client, db):
        """Prueba la configuración de hooks para auditoría automática."""
        # Configurar hooks de auditoría
        setup_audit_hooks(app)
        
        # Definir ruta de prueba
        @app.route('/test-audit')
        def test_audit():
            return {'message': 'Test'}
        
        # Hacer solicitud
        response = client.get('/test-audit')
        assert response.status_code == 200
        
        # Verificar que se crearon logs de auditoría
        logs = AuditLog.query.all()
        assert len(logs) > 0
        
        # Verificar que hay un log para la solicitud
        request_log = AuditLog.query.filter_by(endpoint='/test-audit').first()
        assert request_log is not None
        assert request_log.method == 'GET'
