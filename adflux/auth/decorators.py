"""
Decoradores para autenticación y autorización en AdFlux.

Este módulo proporciona decoradores para controlar el acceso a rutas y funciones
basado en roles y permisos.
"""

import logging
import functools
from typing import Callable, List, Any, TypeVar, cast, Optional, Union

from flask import jsonify, request, current_app, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from .rbac import get_user_permissions, get_user_roles


# Configurar logger
logger = logging.getLogger(__name__)


# Tipo para funciones
F = TypeVar('F', bound=Callable[..., Any])


def role_required(role: Union[str, List[str]], allow_admin: bool = True) -> Callable[[F], F]:
    """
    Decorador que requiere que el usuario tenga un rol específico.
    
    Args:
        role: Rol o lista de roles requeridos
        allow_admin: Si se debe permitir el acceso a administradores
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verificar token JWT
            verify_jwt_in_request()
            
            # Obtener claims del token
            claims = get_jwt()
            
            # Obtener roles del usuario
            user_roles = claims.get('roles', [])
            
            # Permitir acceso a administradores si está habilitado
            if allow_admin and 'admin' in user_roles:
                return func(*args, **kwargs)
            
            # Convertir rol a lista si es una cadena
            required_roles = [role] if isinstance(role, str) else role
            
            # Verificar si el usuario tiene alguno de los roles requeridos
            if any(r in user_roles for r in required_roles):
                return func(*args, **kwargs)
            
            # Acceso denegado
            logger.warning(
                f"Acceso denegado: Usuario con roles {user_roles} intentó acceder a "
                f"ruta protegida que requiere roles {required_roles}"
            )
            
            return jsonify({
                'status': 403,
                'msg': 'No tiene permisos para acceder a este recurso'
            }), 403
        
        return cast(F, wrapper)
    
    return decorator


def permission_required(permission: Union[str, List[str]]) -> Callable[[F], F]:
    """
    Decorador que requiere que el usuario tenga un permiso específico.
    
    Args:
        permission: Permiso o lista de permisos requeridos
        
    Returns:
        Decorador
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verificar token JWT
            verify_jwt_in_request()
            
            # Obtener claims del token
            claims = get_jwt()
            
            # Obtener permisos del usuario
            user_permissions = claims.get('permissions', [])
            
            # Convertir permiso a lista si es una cadena
            required_permissions = [permission] if isinstance(permission, str) else permission
            
            # Verificar si el usuario tiene alguno de los permisos requeridos
            if any(p in user_permissions for p in required_permissions):
                return func(*args, **kwargs)
            
            # Acceso denegado
            logger.warning(
                f"Acceso denegado: Usuario con permisos {user_permissions} intentó acceder a "
                f"ruta protegida que requiere permisos {required_permissions}"
            )
            
            return jsonify({
                'status': 403,
                'msg': 'No tiene permisos para acceder a este recurso'
            }), 403
        
        return cast(F, wrapper)
    
    return decorator


def admin_required(func: F) -> F:
    """
    Decorador que requiere que el usuario sea administrador.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    return role_required('admin')(func)


def api_key_required(func: F) -> F:
    """
    Decorador que requiere una clave de API válida.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Obtener clave de API del encabezado
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'status': 401,
                'msg': 'Se requiere clave de API'
            }), 401
        
        # Verificar clave de API
        from ..models import ApiKey
        
        api_key_obj = ApiKey.query.filter_by(key=api_key, active=True).first()
        if not api_key_obj:
            logger.warning(f"Intento de acceso con clave de API inválida: {api_key}")
            return jsonify({
                'status': 401,
                'msg': 'Clave de API inválida'
            }), 401
        
        # Registrar uso de la clave de API
        api_key_obj.record_usage(request.path, request.method)
        
        # Almacenar información de la clave de API en g
        g.api_key = api_key_obj
        
        return func(*args, **kwargs)
    
    return wrapper
