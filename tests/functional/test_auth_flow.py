"""
Pruebas funcionales para el flujo de autenticación en AdFlux.

Este módulo contiene pruebas para verificar el flujo completo de autenticación,
autorización y gestión de usuarios en AdFlux.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from flask import url_for
from flask_jwt_extended import decode_token

from adflux.models import db, User, Role
from adflux.auth.jwt_auth import RevokedToken
from adflux.auth.rbac import assign_role_to_user, remove_role_from_user


@pytest.mark.functional
class TestAuthFlow:
    """Pruebas para el flujo completo de autenticación."""
    
    def test_register_login_flow(self, app, client, db):
        """Prueba el flujo de registro y login de un usuario."""
        # Definir rutas de autenticación
        @app.route('/auth/register', methods=['POST'])
        def register():
            data = json.loads(client.get_data(as_text=True))
            
            # Verificar que el usuario no existe
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return {'error': 'User already exists'}, 400
            
            # Crear usuario
            user = User(
                username=data['username'],
                email=data['email'],
                name=data['name'],
                password_hash='$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash',  # 'password'
                active=True
            )
            
            # Asignar rol de editor
            editor_role = Role.query.filter_by(name='editor').first()
            user.roles.append(editor_role)
            
            db.session.add(user)
            db.session.commit()
            
            return {'message': 'User registered successfully'}, 201
        
        @app.route('/auth/login', methods=['POST'])
        def login():
            from flask_jwt_extended import create_access_token, create_refresh_token
            
            data = json.loads(client.get_data(as_text=True))
            
            # Buscar usuario
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return {'error': 'Invalid credentials'}, 401
            
            # En una aplicación real, verificaríamos la contraseña aquí
            # Para la prueba, asumimos que es correcta
            
            # Crear tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'name': user.name
                }
            }, 200
        
        # Registrar usuario
        register_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'password123'
        }
        
        response = client.post('/auth/register', json=register_data)
        assert response.status_code == 201
        assert response.json['message'] == 'User registered successfully'
        
        # Verificar que el usuario se creó en la base de datos
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.username == 'testuser'
        assert user.name == 'Test User'
        
        # Verificar que se asignó el rol de editor
        assert len(user.roles) == 1
        assert user.roles[0].name == 'editor'
        
        # Iniciar sesión
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        response = client.post('/auth/login', json=login_data)
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
        assert 'user' in response.json
        assert response.json['user']['email'] == 'test@example.com'
        
        # Verificar tokens
        access_token = response.json['access_token']
        with app.app_context():
            decoded = decode_token(access_token)
            assert decoded['sub'] == user.id
    
    def test_refresh_token_flow(self, app, client, db, regular_user):
        """Prueba el flujo de renovación de token."""
        # Definir rutas de autenticación
        @app.route('/auth/refresh', methods=['POST'])
        def refresh():
            from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
            
            # Verificar token de refresco
            try:
                jwt_required(refresh=True)
                user_id = get_jwt_identity()
                
                # Crear nuevo token de acceso
                access_token = create_access_token(identity=user_id)
                
                return {'access_token': access_token}, 200
            
            except Exception as e:
                return {'error': str(e)}, 401
        
        # Crear token de refresco
        with app.app_context():
            from flask_jwt_extended import create_refresh_token
            refresh_token = create_refresh_token(identity=regular_user.id)
        
        # Renovar token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/auth/refresh', headers=headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        assert 'access_token' in response.json
        
        # Verificar nuevo token
        access_token = response.json['access_token']
        with app.app_context():
            decoded = decode_token(access_token)
            assert decoded['sub'] == regular_user.id
    
    def test_logout_flow(self, app, client, db, admin_user):
        """Prueba el flujo de cierre de sesión."""
        # Definir rutas de autenticación
        @app.route('/auth/logout', methods=['POST'])
        def logout():
            from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
            
            # Verificar token
            try:
                jwt_required()
                token = get_jwt()
                user_id = get_jwt_identity()
                
                # Revocar token
                jti = token['jti']
                token_type = token['type']
                exp = datetime.fromtimestamp(token['exp'])
                
                revoked_token = RevokedToken(
                    jti=jti,
                    token_type=token_type,
                    user_id=user_id,
                    expires_at=exp
                )
                
                db.session.add(revoked_token)
                db.session.commit()
                
                return {'message': 'Successfully logged out'}, 200
            
            except Exception as e:
                return {'error': str(e)}, 401
        
        # Crear token de acceso
        with app.app_context():
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=admin_user.id)
        
        # Cerrar sesión
        headers = {'Authorization': f'Bearer {access_token}'}
        response = client.post('/auth/logout', headers=headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json['message'] == 'Successfully logged out'
        
        # Verificar que el token se revocó
        with app.app_context():
            decoded = decode_token(access_token)
            jti = decoded['jti']
            
            revoked = RevokedToken.query.filter_by(jti=jti).first()
            assert revoked is not None
            assert revoked.user_id == admin_user.id
    
    def test_role_management_flow(self, app, client, db, regular_user):
        """Prueba el flujo de gestión de roles."""
        # Definir rutas de gestión de roles
        @app.route('/admin/users/<int:user_id>/roles', methods=['POST'])
        def add_role(user_id):
            data = json.loads(client.get_data(as_text=True))
            role_name = data['role']
            
            # Asignar rol
            success = assign_role_to_user(user_id, role_name)
            
            if success:
                return {'message': f'Role {role_name} assigned to user {user_id}'}, 200
            else:
                return {'error': 'Failed to assign role'}, 400
        
        @app.route('/admin/users/<int:user_id>/roles/<role_name>', methods=['DELETE'])
        def remove_role(user_id, role_name):
            # Eliminar rol
            success = remove_role_from_user(user_id, role_name)
            
            if success:
                return {'message': f'Role {role_name} removed from user {user_id}'}, 200
            else:
                return {'error': 'Failed to remove role'}, 400
        
        # Verificar roles iniciales
        assert len(regular_user.roles) == 1
        assert regular_user.roles[0].name == 'editor'
        
        # Asignar rol de administrador
        response = client.post(f'/admin/users/{regular_user.id}/roles', json={'role': 'admin'})
        assert response.status_code == 200
        assert response.json['message'] == f'Role admin assigned to user {regular_user.id}'
        
        # Verificar que se asignó el rol
        db.session.refresh(regular_user)
        assert len(regular_user.roles) == 2
        role_names = [role.name for role in regular_user.roles]
        assert 'editor' in role_names
        assert 'admin' in role_names
        
        # Eliminar rol de editor
        response = client.delete(f'/admin/users/{regular_user.id}/roles/editor')
        assert response.status_code == 200
        assert response.json['message'] == f'Role editor removed from user {regular_user.id}'
        
        # Verificar que se eliminó el rol
        db.session.refresh(regular_user)
        assert len(regular_user.roles) == 1
        assert regular_user.roles[0].name == 'admin'
    
    def test_password_reset_flow(self, app, client, db, regular_user):
        """Prueba el flujo de restablecimiento de contraseña."""
        # Definir rutas de restablecimiento de contraseña
        @app.route('/auth/forgot-password', methods=['POST'])
        def forgot_password():
            data = json.loads(client.get_data(as_text=True))
            email = data['email']
            
            # Buscar usuario
            user = User.query.filter_by(email=email).first()
            if not user:
                # No revelar si el usuario existe o no
                return {'message': 'If your email is registered, you will receive a reset link'}, 200
            
            # En una aplicación real, enviaríamos un correo con un token
            # Para la prueba, simplemente generamos un token
            reset_token = 'test_reset_token'
            
            # Almacenar token en la base de datos
            user.reset_token = reset_token
            user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            return {'message': 'If your email is registered, you will receive a reset link'}, 200
        
        @app.route('/auth/reset-password', methods=['POST'])
        def reset_password():
            data = json.loads(client.get_data(as_text=True))
            token = data['token']
            new_password = data['new_password']
            
            # Buscar usuario por token
            user = User.query.filter_by(reset_token=token).first()
            if not user or user.reset_token_expires_at < datetime.utcnow():
                return {'error': 'Invalid or expired token'}, 400
            
            # En una aplicación real, hashearíamos la contraseña
            # Para la prueba, simplemente la almacenamos
            user.password_hash = 'new_hashed_password'
            user.reset_token = None
            user.reset_token_expires_at = None
            db.session.commit()
            
            return {'message': 'Password reset successfully'}, 200
        
        # Solicitar restablecimiento de contraseña
        response = client.post('/auth/forgot-password', json={'email': regular_user.email})
        assert response.status_code == 200
        assert response.json['message'] == 'If your email is registered, you will receive a reset link'
        
        # Verificar que se generó el token
        db.session.refresh(regular_user)
        assert regular_user.reset_token == 'test_reset_token'
        assert regular_user.reset_token_expires_at is not None
        
        # Restablecer contraseña
        response = client.post('/auth/reset-password', json={
            'token': 'test_reset_token',
            'new_password': 'new_password123'
        })
        assert response.status_code == 200
        assert response.json['message'] == 'Password reset successfully'
        
        # Verificar que se actualizó la contraseña
        db.session.refresh(regular_user)
        assert regular_user.password_hash == 'new_hashed_password'
        assert regular_user.reset_token is None
        assert regular_user.reset_token_expires_at is None
