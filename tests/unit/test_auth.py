"""
Pruebas unitarias para autenticación y autorización de AdFlux.

Este módulo contiene pruebas unitarias para los componentes de autenticación
y autorización de AdFlux.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from flask import url_for
from flask_jwt_extended import create_access_token, decode_token

from adflux.auth.jwt_auth import revoke_token, RevokedToken
from adflux.auth.two_factor import generate_totp_secret, verify_totp, get_totp_uri
from adflux.auth.rbac import assign_role_to_user, remove_role_from_user
from adflux.auth.decorators import role_required, permission_required
from adflux.models import User, Role, Permission


@pytest.mark.unit
@pytest.mark.auth
class TestJWTAuth:
    """Pruebas para autenticación JWT."""
    
    def test_create_access_token(self, app, admin_user):
        """Prueba la creación de un token de acceso."""
        with app.app_context():
            # Crear token
            token = create_access_token(identity=admin_user.id)
            
            # Verificar que el token es válido
            assert token is not None
            
            # Decodificar token
            decoded = decode_token(token)
            
            # Verificar contenido
            assert decoded['sub'] == admin_user.id
            assert 'exp' in decoded
            assert 'iat' in decoded
            assert 'jti' in decoded
    
    def test_revoke_token(self, app, admin_user):
        """Prueba la revocación de un token."""
        with app.app_context():
            # Crear token
            token = create_access_token(identity=admin_user.id)
            
            # Decodificar token
            decoded = decode_token(token)
            
            # Revocar token
            revoke_token(decoded, admin_user.id)
            
            # Verificar que el token está revocado
            revoked = RevokedToken.query.filter_by(jti=decoded['jti']).first()
            assert revoked is not None
            assert revoked.user_id == admin_user.id
            assert revoked.token_type == decoded['type']
    
    def test_jwt_required_decorator(self, app, client, admin_token):
        """Prueba el decorador jwt_required."""
        # Definir ruta protegida
        @app.route('/protected')
        @jwt_required()
        def protected():
            return {'message': 'Success'}
        
        # Intentar acceder sin token
        response = client.get('/protected')
        assert response.status_code == 401
        
        # Acceder con token
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get('/protected', headers=headers)
        assert response.status_code == 200
        assert response.json['message'] == 'Success'


@pytest.mark.unit
@pytest.mark.auth
class TestTwoFactor:
    """Pruebas para autenticación de dos factores."""
    
    def test_generate_totp_secret(self):
        """Prueba la generación de un secreto TOTP."""
        # Generar secreto
        secret = generate_totp_secret()
        
        # Verificar que el secreto es válido
        assert secret is not None
        assert len(secret) > 0
    
    def test_get_totp_uri(self):
        """Prueba la generación de un URI para código QR."""
        # Generar secreto
        secret = generate_totp_secret()
        
        # Generar URI
        uri = get_totp_uri(secret, 'test@example.com')
        
        # Verificar que el URI es válido
        assert uri is not None
        assert 'otpauth://totp/' in uri
        assert 'test@example.com' in uri
        assert secret in uri
    
    def test_verify_totp(self):
        """Prueba la verificación de un código TOTP."""
        # Esta prueba es complicada porque los códigos TOTP cambian con el tiempo
        # Usamos un mock para simular la verificación
        with patch('adflux.auth.two_factor.pyotp.TOTP') as mock_totp:
            # Configurar mock
            mock_totp_instance = MagicMock()
            mock_totp_instance.verify.return_value = True
            mock_totp.return_value = mock_totp_instance
            
            # Verificar código
            result = verify_totp('secret', '123456')
            
            # Verificar resultado
            assert result is True
            mock_totp_instance.verify.assert_called_once_with('123456')


@pytest.mark.unit
@pytest.mark.auth
class TestRBAC:
    """Pruebas para control de acceso basado en roles."""
    
    def test_assign_role_to_user(self, db, regular_user):
        """Prueba la asignación de un rol a un usuario."""
        # Obtener rol
        admin_role = Role.query.filter_by(name='admin').first()
        
        # Verificar que el usuario no tiene el rol
        assert admin_role not in regular_user.roles
        
        # Asignar rol
        result = assign_role_to_user(regular_user.id, 'admin')
        
        # Verificar resultado
        assert result is True
        
        # Verificar que el usuario tiene el rol
        db.session.refresh(regular_user)
        assert admin_role in regular_user.roles
    
    def test_remove_role_from_user(self, db, admin_user):
        """Prueba la eliminación de un rol de un usuario."""
        # Obtener rol
        admin_role = Role.query.filter_by(name='admin').first()
        
        # Verificar que el usuario tiene el rol
        assert admin_role in admin_user.roles
        
        # Eliminar rol
        result = remove_role_from_user(admin_user.id, 'admin')
        
        # Verificar resultado
        assert result is True
        
        # Verificar que el usuario no tiene el rol
        db.session.refresh(admin_user)
        assert admin_role not in admin_user.roles
    
    def test_role_required_decorator(self, app, client, admin_token, user_token):
        """Prueba el decorador role_required."""
        # Definir ruta protegida
        @app.route('/admin-only')
        @role_required('admin')
        def admin_only():
            return {'message': 'Admin access'}
        
        # Intentar acceder sin token
        response = client.get('/admin-only')
        assert response.status_code == 401
        
        # Acceder con token de usuario regular
        headers = {'Authorization': f'Bearer {user_token}'}
        response = client.get('/admin-only', headers=headers)
        assert response.status_code == 403
        
        # Acceder con token de administrador
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get('/admin-only', headers=headers)
        assert response.status_code == 200
        assert response.json['message'] == 'Admin access'
    
    def test_permission_required_decorator(self, app, client, admin_token, user_token):
        """Prueba el decorador permission_required."""
        # Definir ruta protegida
        @app.route('/edit-settings')
        @permission_required('edit_settings')
        def edit_settings():
            return {'message': 'Settings access'}
        
        # Intentar acceder sin token
        response = client.get('/edit-settings')
        assert response.status_code == 401
        
        # Acceder con token de usuario regular
        headers = {'Authorization': f'Bearer {user_token}'}
        response = client.get('/edit-settings', headers=headers)
        assert response.status_code == 403
        
        # Acceder con token de administrador
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get('/edit-settings', headers=headers)
        assert response.status_code == 200
        assert response.json['message'] == 'Settings access'
