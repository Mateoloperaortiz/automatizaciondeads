"""
Sistema de auditoría para AdFlux.

Este módulo proporciona funcionalidades para registrar y consultar actividades
de los usuarios en el sistema, facilitando la auditoría de seguridad.
"""

import json
import logging
import ipaddress
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

from flask import request, current_app, g
from sqlalchemy.dialects.postgresql import JSONB

from ..models import db


# Configurar logger
logger = logging.getLogger(__name__)


class AuditLog(db.Model):
    """
    Modelo para logs de auditoría.
    
    Registra acciones realizadas por los usuarios en el sistema.
    """
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(50), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 puede tener hasta 45 caracteres
    user_agent = db.Column(db.String(255), nullable=True)
    endpoint = db.Column(db.String(255), nullable=True)
    method = db.Column(db.String(10), nullable=True)
    status_code = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    
    # Relación con el usuario
    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))
    
    def __repr__(self) -> str:
        return f'<AuditLog {self.id}: {self.action} by {self.user_id} at {self.timestamp}>'
    
    @classmethod
    def create(cls, action: str, user_id: Optional[int] = None, resource_type: Optional[str] = None,
              resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
              status_code: Optional[int] = None) -> 'AuditLog':
        """
        Crea un nuevo log de auditoría.
        
        Args:
            action: Acción realizada
            user_id: ID del usuario (opcional)
            resource_type: Tipo de recurso (opcional)
            resource_id: ID del recurso (opcional)
            details: Detalles adicionales (opcional)
            status_code: Código de estado HTTP (opcional)
            
        Returns:
            Log de auditoría creado
        """
        # Obtener información de la solicitud actual
        ip_address = None
        user_agent = None
        endpoint = None
        method = None
        
        if request:
            # Obtener dirección IP
            ip_address = request.remote_addr
            
            # Obtener User-Agent
            user_agent = request.user_agent.string if request.user_agent else None
            
            # Obtener endpoint y método
            endpoint = request.path
            method = request.method
        
        # Crear log de auditoría
        audit_log = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            details=details
        )
        
        # Guardar en la base de datos
        db.session.add(audit_log)
        db.session.commit()
        
        return audit_log
    
    @classmethod
    def search(cls, user_id: Optional[int] = None, action: Optional[str] = None,
              resource_type: Optional[str] = None, resource_id: Optional[str] = None,
              start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
              ip_address: Optional[str] = None, status_code: Optional[int] = None,
              limit: int = 100, offset: int = 0) -> List['AuditLog']:
        """
        Busca logs de auditoría según criterios.
        
        Args:
            user_id: ID del usuario (opcional)
            action: Acción realizada (opcional)
            resource_type: Tipo de recurso (opcional)
            resource_id: ID del recurso (opcional)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            ip_address: Dirección IP (opcional)
            status_code: Código de estado HTTP (opcional)
            limit: Límite de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            Lista de logs de auditoría
        """
        # Construir consulta
        query = cls.query
        
        # Aplicar filtros
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        
        if action:
            query = query.filter(cls.action == action)
        
        if resource_type:
            query = query.filter(cls.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(cls.resource_id == resource_id)
        
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        
        if ip_address:
            query = query.filter(cls.ip_address == ip_address)
        
        if status_code is not None:
            query = query.filter(cls.status_code == status_code)
        
        # Ordenar por fecha descendente
        query = query.order_by(cls.timestamp.desc())
        
        # Aplicar paginación
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @classmethod
    def get_user_activity(cls, user_id: int, limit: int = 100) -> List['AuditLog']:
        """
        Obtiene la actividad reciente de un usuario.
        
        Args:
            user_id: ID del usuario
            limit: Límite de resultados
            
        Returns:
            Lista de logs de auditoría
        """
        return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_resource_activity(cls, resource_type: str, resource_id: str, limit: int = 100) -> List['AuditLog']:
        """
        Obtiene la actividad reciente sobre un recurso.
        
        Args:
            resource_type: Tipo de recurso
            resource_id: ID del recurso
            limit: Límite de resultados
            
        Returns:
            Lista de logs de auditoría
        """
        return cls.query.filter_by(
            resource_type=resource_type,
            resource_id=resource_id
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_suspicious_activity(cls, limit: int = 100) -> List['AuditLog']:
        """
        Obtiene actividad sospechosa.
        
        Args:
            limit: Límite de resultados
            
        Returns:
            Lista de logs de auditoría
        """
        # Actividad sospechosa: intentos de acceso fallidos, cambios de permisos, etc.
        return cls.query.filter(
            ((cls.action == 'login') & (cls.status_code != 200)) |
            (cls.action.in_(['change_permissions', 'change_role', 'reset_password']))
        ).order_by(cls.timestamp.desc()).limit(limit).all()


def log_activity(action: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None,
                details: Optional[Dict[str, Any]] = None, status_code: Optional[int] = None) -> AuditLog:
    """
    Registra una actividad en el log de auditoría.
    
    Args:
        action: Acción realizada
        resource_type: Tipo de recurso (opcional)
        resource_id: ID del recurso (opcional)
        details: Detalles adicionales (opcional)
        status_code: Código de estado HTTP (opcional)
        
    Returns:
        Log de auditoría creado
    """
    # Obtener ID del usuario actual
    user_id = None
    
    # Intentar obtener usuario de JWT
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
    except Exception:
        # Si no hay JWT, intentar obtener usuario de g
        if hasattr(g, 'user') and g.user:
            user_id = g.user.id
    
    # Crear log de auditoría
    return AuditLog.create(
        action=action,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        status_code=status_code
    )


def setup_audit_hooks(app):
    """
    Configura hooks para auditoría automática.
    
    Args:
        app: Aplicación Flask
    """
    @app.after_request
    def log_request(response):
        """
        Registra solicitudes HTTP en el log de auditoría.
        
        Args:
            response: Respuesta HTTP
            
        Returns:
            Respuesta HTTP
        """
        # Ignorar solicitudes a rutas estáticas
        if request.path.startswith('/static'):
            return response
        
        # Ignorar solicitudes OPTIONS (CORS preflight)
        if request.method == 'OPTIONS':
            return response
        
        # Determinar acción según método y ruta
        action = f"{request.method.lower()}_{request.endpoint}" if request.endpoint else request.method.lower()
        
        # Determinar tipo de recurso y ID
        resource_type = None
        resource_id = None
        
        # Extraer tipo de recurso y ID de la ruta
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 1:
            resource_type = path_parts[0]
        if len(path_parts) >= 2 and path_parts[1].isdigit():
            resource_id = path_parts[1]
        
        # Registrar actividad
        try:
            log_activity(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                status_code=response.status_code
            )
        except Exception as e:
            logger.error(f"Error al registrar actividad: {str(e)}")
        
        return response
