"""
Módulo de autenticación y autorización para AdFlux.

Este módulo proporciona funcionalidades para la autenticación y autorización
de usuarios en la aplicación AdFlux.
"""

from .jwt_auth import jwt, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from .two_factor import generate_totp_secret, verify_totp, get_totp_uri
from .rbac import Role, Permission, RolePermission, UserRole
from .decorators import role_required, permission_required
from .audit import AuditLog, log_activity

__all__ = [
    'jwt',
    'jwt_required',
    'create_access_token',
    'create_refresh_token',
    'get_jwt_identity',
    'generate_totp_secret',
    'verify_totp',
    'get_totp_uri',
    'Role',
    'Permission',
    'RolePermission',
    'UserRole',
    'role_required',
    'permission_required',
    'AuditLog',
    'log_activity'
]
