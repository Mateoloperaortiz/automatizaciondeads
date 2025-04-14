"""
Autenticación JWT para AdFlux.

Este módulo proporciona funcionalidades para la autenticación basada en JWT (JSON Web Tokens).
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Union

from flask import Flask, jsonify, request, current_app
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt, verify_jwt_in_request
)

from ..models import db, User


# Configurar logger
logger = logging.getLogger(__name__)


# Crear instancia de JWTManager
jwt = JWTManager()


def init_jwt(app: Flask) -> None:
    """
    Inicializa la autenticación JWT en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
    """
    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-key-insecure')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    # Inicializar JWT
    jwt.init_app(app)
    
    # Registrar callbacks
    register_jwt_callbacks(jwt)
    
    logger.info("Autenticación JWT inicializada")


def register_jwt_callbacks(jwt_manager: JWTManager) -> None:
    """
    Registra callbacks para JWT.
    
    Args:
        jwt_manager: Instancia de JWTManager
    """
    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> bool:
        """
        Verifica si un token está en la lista negra.
        
        Args:
            jwt_header: Cabecera del token JWT
            jwt_payload: Payload del token JWT
            
        Returns:
            True si el token está revocado, False en caso contrario
        """
        jti = jwt_payload['jti']
        token = RevokedToken.query.filter_by(jti=jti).first()
        return token is not None
    
    @jwt_manager.user_identity_loader
    def user_identity_lookup(user_id: int) -> int:
        """
        Convierte la identidad del usuario para el token JWT.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            ID del usuario
        """
        return user_id
    
    @jwt_manager.user_lookup_loader
    def user_lookup_callback(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> Optional[User]:
        """
        Busca un usuario a partir del payload del token JWT.
        
        Args:
            jwt_header: Cabecera del token JWT
            jwt_payload: Payload del token JWT
            
        Returns:
            Usuario o None si no se encuentra
        """
        identity = jwt_payload['sub']
        return User.query.get(identity)
    
    @jwt_manager.additional_claims_loader
    def add_claims_to_access_token(identity: int) -> Dict[str, Any]:
        """
        Añade claims adicionales al token JWT.
        
        Args:
            identity: ID del usuario
            
        Returns:
            Claims adicionales
        """
        user = User.query.get(identity)
        if not user:
            return {}
        
        # Obtener roles y permisos del usuario
        roles = [role.name for role in user.roles]
        permissions = []
        
        for role in user.roles:
            for permission in role.permissions:
                if permission.name not in permissions:
                    permissions.append(permission.name)
        
        return {
            'roles': roles,
            'permissions': permissions,
            'email': user.email,
            'name': user.name
        }
    
    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> Any:
        """
        Callback para tokens expirados.
        
        Args:
            jwt_header: Cabecera del token JWT
            jwt_payload: Payload del token JWT
            
        Returns:
            Respuesta de error
        """
        return jsonify({
            'status': 401,
            'sub_status': 42,
            'msg': 'El token ha expirado'
        }), 401
    
    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error: str) -> Any:
        """
        Callback para tokens inválidos.
        
        Args:
            error: Mensaje de error
            
        Returns:
            Respuesta de error
        """
        return jsonify({
            'status': 401,
            'sub_status': 43,
            'msg': 'Token inválido: ' + error
        }), 401
    
    @jwt_manager.unauthorized_loader
    def missing_token_callback(error: str) -> Any:
        """
        Callback para solicitudes sin token.
        
        Args:
            error: Mensaje de error
            
        Returns:
            Respuesta de error
        """
        return jsonify({
            'status': 401,
            'sub_status': 44,
            'msg': 'Falta token de autorización: ' + error
        }), 401
    
    @jwt_manager.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> Any:
        """
        Callback para tokens que necesitan ser frescos.
        
        Args:
            jwt_header: Cabecera del token JWT
            jwt_payload: Payload del token JWT
            
        Returns:
            Respuesta de error
        """
        return jsonify({
            'status': 401,
            'sub_status': 45,
            'msg': 'Se requiere un token fresco para esta acción'
        }), 401
    
    @jwt_manager.revoked_token_loader
    def revoked_token_callback(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> Any:
        """
        Callback para tokens revocados.
        
        Args:
            jwt_header: Cabecera del token JWT
            jwt_payload: Payload del token JWT
            
        Returns:
            Respuesta de error
        """
        return jsonify({
            'status': 401,
            'sub_status': 46,
            'msg': 'El token ha sido revocado'
        }), 401


class RevokedToken(db.Model):
    """
    Modelo para tokens revocados.
    
    Almacena los tokens JWT que han sido revocados antes de su expiración.
    """
    
    __tablename__ = 'revoked_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref=db.backref('revoked_tokens', lazy='dynamic'))
    
    def __repr__(self) -> str:
        return f'<RevokedToken {self.jti}>'
    
    @classmethod
    def revoke_token(cls, jti: str, token_type: str, user_id: int, expires_at: datetime) -> None:
        """
        Revoca un token JWT.
        
        Args:
            jti: ID único del token
            token_type: Tipo de token (access o refresh)
            user_id: ID del usuario
            expires_at: Fecha de expiración del token
        """
        revoked_token = cls(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at
        )
        
        db.session.add(revoked_token)
        db.session.commit()
    
    @classmethod
    def cleanup_expired_tokens(cls) -> int:
        """
        Elimina tokens expirados de la base de datos.
        
        Returns:
            Número de tokens eliminados
        """
        now = datetime.now(timezone.utc)
        expired = cls.query.filter(cls.expires_at < now).delete()
        db.session.commit()
        
        return expired


def revoke_token(token: Dict[str, Any], user_id: int) -> None:
    """
    Revoca un token JWT.
    
    Args:
        token: Token JWT
        user_id: ID del usuario
    """
    jti = token['jti']
    token_type = token['type']
    exp = datetime.fromtimestamp(token['exp'], timezone.utc)
    
    RevokedToken.revoke_token(jti, token_type, user_id, exp)


def get_user_tokens(user_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene los tokens activos de un usuario.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Lista de tokens activos
    """
    # Esta función es un placeholder, ya que no hay una forma directa de obtener
    # todos los tokens activos de un usuario con Flask-JWT-Extended.
    # En una implementación real, se necesitaría almacenar los tokens en la base de datos.
    return []


def revoke_all_user_tokens(user_id: int) -> int:
    """
    Revoca todos los tokens de un usuario.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Número de tokens revocados
    """
    # Esta función es un placeholder, ya que no hay una forma directa de revocar
    # todos los tokens de un usuario con Flask-JWT-Extended.
    # En una implementación real, se necesitaría almacenar los tokens en la base de datos.
    return 0
