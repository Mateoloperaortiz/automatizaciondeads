"""
Autenticación para el API Gateway.

Este módulo implementa la autenticación y autorización para el API Gateway.
"""

import jwt
from functools import wraps
from datetime import datetime, timezone
from flask import request, jsonify, current_app, g


def register_auth_handlers(app):
    """
    Registra los manejadores de autenticación para el API Gateway.
    
    Args:
        app: Aplicación Flask
    """
    # Manejador para errores de autenticación
    @app.errorhandler(401)
    def unauthorized(error):
        """Maneja errores de autenticación."""
        return jsonify({
            'error': True,
            'message': 'No autorizado',
            'status_code': 401
        }), 401
    
    # Manejador para errores de autorización
    @app.errorhandler(403)
    def forbidden(error):
        """Maneja errores de autorización."""
        return jsonify({
            'error': True,
            'message': 'Acceso prohibido',
            'status_code': 403
        }), 403


def jwt_required():
    """
    Decorador que requiere un token JWT válido para acceder a un endpoint.
    
    Returns:
        Función decoradora
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            
            if not token:
                return jsonify({
                    'error': True,
                    'message': 'Token de acceso requerido'
                }), 401
            
            try:
                # Decodificar token
                payload = jwt.decode(
                    token,
                    current_app.config['JWT_SECRET_KEY'],
                    algorithms=['HS256']
                )
                
                # Verificar expiración
                exp = payload.get('exp')
                if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                    return jsonify({
                        'error': True,
                        'message': 'Token expirado'
                    }), 401
                
                # Guardar información del usuario en g
                g.user_id = payload.get('sub')
                g.user_roles = payload.get('roles', [])
                
            except jwt.InvalidTokenError:
                return jsonify({
                    'error': True,
                    'message': 'Token inválido'
                }), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(role):
    """
    Decorador que requiere que el usuario tenga un rol específico.
    
    Args:
        role: Rol requerido
        
    Returns:
        Función decoradora
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar que el usuario esté autenticado
            if not hasattr(g, 'user_roles'):
                return jsonify({
                    'error': True,
                    'message': 'No autorizado'
                }), 401
            
            # Verificar que el usuario tenga el rol requerido
            if role not in g.user_roles:
                return jsonify({
                    'error': True,
                    'message': 'Acceso prohibido'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_jwt_identity():
    """
    Obtiene la identidad del usuario del token JWT.
    
    Returns:
        ID del usuario o None si no está autenticado
    """
    return getattr(g, 'user_id', None)


def create_access_token(identity, roles=None, expires_delta=None):
    """
    Crea un token de acceso JWT.
    
    Args:
        identity: Identidad del usuario (generalmente ID)
        roles: Lista de roles del usuario
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT
    """
    if expires_delta is None:
        expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
    
    now = datetime.now(timezone.utc)
    exp = now + expires_delta
    
    payload = {
        'sub': str(identity),
        'iat': now,
        'exp': exp,
    }
    
    if roles:
        payload['roles'] = roles
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )


def create_refresh_token(identity, expires_delta=None):
    """
    Crea un token de actualización JWT.
    
    Args:
        identity: Identidad del usuario (generalmente ID)
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT de actualización
    """
    if expires_delta is None:
        expires_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
    
    now = datetime.now(timezone.utc)
    exp = now + expires_delta
    
    payload = {
        'sub': str(identity),
        'iat': now,
        'exp': exp,
        'type': 'refresh'
    }
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
