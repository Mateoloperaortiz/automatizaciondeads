"""
Control de acceso basado en roles (RBAC) para AdFlux.

Este módulo proporciona modelos y funcionalidades para implementar RBAC,
permitiendo definir roles y permisos para los usuarios.
"""

import logging
from typing import List, Set, Dict, Any, Optional

from ..models import db


# Configurar logger
logger = logging.getLogger(__name__)


# Tabla de asociación entre roles y permisos
RolePermission = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


# Tabla de asociación entre usuarios y roles
UserRole = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)


class Permission(db.Model):
    """
    Modelo para permisos.
    
    Representa un permiso específico en el sistema.
    """
    
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self) -> str:
        return f'<Permission {self.name}>'


class Role(db.Model):
    """
    Modelo para roles.
    
    Representa un rol en el sistema, que puede tener múltiples permisos.
    """
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relación con permisos
    permissions = db.relationship('Permission', secondary=RolePermission,
                                 backref=db.backref('roles', lazy='dynamic'))
    
    def __repr__(self) -> str:
        return f'<Role {self.name}>'
    
    def add_permission(self, permission: Permission) -> None:
        """
        Añade un permiso al rol.
        
        Args:
            permission: Permiso a añadir
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        """
        Elimina un permiso del rol.
        
        Args:
            permission: Permiso a eliminar
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def has_permission(self, permission_name: str) -> bool:
        """
        Verifica si el rol tiene un permiso específico.
        
        Args:
            permission_name: Nombre del permiso
            
        Returns:
            True si el rol tiene el permiso, False en caso contrario
        """
        return any(p.name == permission_name for p in self.permissions)


def create_default_roles_and_permissions() -> None:
    """
    Crea roles y permisos por defecto en la base de datos.
    
    Esta función debe ejecutarse durante la inicialización de la aplicación.
    """
    # Definir permisos
    permissions = {
        # Permisos para campañas
        'view_campaigns': 'Ver campañas',
        'create_campaigns': 'Crear campañas',
        'edit_campaigns': 'Editar campañas',
        'delete_campaigns': 'Eliminar campañas',
        'publish_campaigns': 'Publicar campañas',
        
        # Permisos para candidatos
        'view_candidates': 'Ver candidatos',
        'create_candidates': 'Crear candidatos',
        'edit_candidates': 'Editar candidatos',
        'delete_candidates': 'Eliminar candidatos',
        
        # Permisos para trabajos
        'view_jobs': 'Ver trabajos',
        'create_jobs': 'Crear trabajos',
        'edit_jobs': 'Editar trabajos',
        'delete_jobs': 'Eliminar trabajos',
        
        # Permisos para reportes
        'view_reports': 'Ver reportes',
        'create_reports': 'Crear reportes',
        'export_reports': 'Exportar reportes',
        
        # Permisos para usuarios
        'view_users': 'Ver usuarios',
        'create_users': 'Crear usuarios',
        'edit_users': 'Editar usuarios',
        'delete_users': 'Eliminar usuarios',
        
        # Permisos para configuración
        'view_settings': 'Ver configuración',
        'edit_settings': 'Editar configuración',
        
        # Permisos para auditoría
        'view_audit_logs': 'Ver logs de auditoría',
        
        # Permisos para APIs externas
        'manage_api_keys': 'Gestionar claves de API',
        'view_api_usage': 'Ver uso de API',
    }
    
    # Crear permisos en la base de datos
    for name, description in permissions.items():
        # Verificar si el permiso ya existe
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(name=name, description=description)
            db.session.add(permission)
    
    # Guardar cambios para que los permisos tengan IDs
    db.session.commit()
    
    # Definir roles
    roles = {
        'admin': {
            'description': 'Administrador con acceso completo',
            'permissions': list(permissions.keys())  # Todos los permisos
        },
        'manager': {
            'description': 'Gestor con acceso a la mayoría de funcionalidades',
            'permissions': [
                'view_campaigns', 'create_campaigns', 'edit_campaigns', 'publish_campaigns',
                'view_candidates', 'create_candidates', 'edit_candidates',
                'view_jobs', 'create_jobs', 'edit_jobs',
                'view_reports', 'create_reports', 'export_reports',
                'view_users',
                'view_settings',
                'view_audit_logs',
                'view_api_usage'
            ]
        },
        'editor': {
            'description': 'Editor con acceso a contenido',
            'permissions': [
                'view_campaigns', 'create_campaigns', 'edit_campaigns',
                'view_candidates', 'create_candidates', 'edit_candidates',
                'view_jobs', 'create_jobs', 'edit_jobs',
                'view_reports', 'create_reports',
                'view_api_usage'
            ]
        },
        'viewer': {
            'description': 'Visualizador con acceso de solo lectura',
            'permissions': [
                'view_campaigns',
                'view_candidates',
                'view_jobs',
                'view_reports'
            ]
        }
    }
    
    # Crear roles en la base de datos
    for name, role_data in roles.items():
        # Verificar si el rol ya existe
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, description=role_data['description'])
            db.session.add(role)
            db.session.commit()  # Guardar para obtener ID
        
        # Asignar permisos al rol
        for permission_name in role_data['permissions']:
            permission = Permission.query.filter_by(name=permission_name).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    
    # Guardar cambios
    db.session.commit()
    
    logger.info("Roles y permisos por defecto creados")


def get_user_permissions(user_id: int) -> Set[str]:
    """
    Obtiene todos los permisos de un usuario.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Conjunto de nombres de permisos
    """
    from ..models import User
    
    user = User.query.get(user_id)
    if not user:
        return set()
    
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    
    return permissions


def get_user_roles(user_id: int) -> List[str]:
    """
    Obtiene todos los roles de un usuario.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Lista de nombres de roles
    """
    from ..models import User
    
    user = User.query.get(user_id)
    if not user:
        return []
    
    return [role.name for role in user.roles]


def assign_role_to_user(user_id: int, role_name: str) -> bool:
    """
    Asigna un rol a un usuario.
    
    Args:
        user_id: ID del usuario
        role_name: Nombre del rol
        
    Returns:
        True si se asignó correctamente, False en caso contrario
    """
    from ..models import User
    
    user = User.query.get(user_id)
    if not user:
        return False
    
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return False
    
    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()
    
    return True


def remove_role_from_user(user_id: int, role_name: str) -> bool:
    """
    Elimina un rol de un usuario.
    
    Args:
        user_id: ID del usuario
        role_name: Nombre del rol
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    from ..models import User
    
    user = User.query.get(user_id)
    if not user:
        return False
    
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return False
    
    if role in user.roles:
        user.roles.remove(role)
        db.session.commit()
    
    return True
