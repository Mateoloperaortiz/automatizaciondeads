"""
Logging de seguridad para AdFlux.

Este módulo proporciona funciones para configurar y utilizar logging de seguridad,
facilitando la detección y análisis de eventos de seguridad.
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from flask import Flask, request, g, has_request_context


# Configurar logger
logger = logging.getLogger(__name__)


class SecurityLogFormatter(logging.Formatter):
    """
    Formateador personalizado para logs de seguridad.
    
    Añade información adicional a los logs, como dirección IP, usuario, etc.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea un registro de log.
        
        Args:
            record: Registro de log
            
        Returns:
            Registro formateado
        """
        # Añadir información de la solicitud si está disponible
        if has_request_context():
            record.ip = request.remote_addr
            record.method = request.method
            record.path = request.path
            record.user_agent = request.user_agent.string if request.user_agent else None
            
            # Añadir información del usuario si está disponible
            if hasattr(g, 'user') and g.user:
                record.user_id = g.user.id
                record.username = g.user.username
            else:
                record.user_id = None
                record.username = None
        else:
            record.ip = None
            record.method = None
            record.path = None
            record.user_agent = None
            record.user_id = None
            record.username = None
        
        # Formatear registro
        return super().format(record)


def setup_security_logging(app: Flask, log_dir: Optional[str] = None) -> None:
    """
    Configura logging de seguridad en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
        log_dir: Directorio para logs (opcional)
    """
    # Crear logger de seguridad
    security_logger = logging.getLogger('adflux.security')
    security_logger.setLevel(logging.INFO)
    
    # Determinar directorio de logs
    if log_dir is None:
        log_dir = app.config.get('LOG_DIR', 'logs')
    
    # Crear directorio de logs si no existe
    os.makedirs(log_dir, exist_ok=True)
    
    # Crear manejador de archivo para logs de seguridad
    security_log_file = os.path.join(log_dir, 'security.log')
    file_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    
    # Crear formateador
    formatter = SecurityLogFormatter(
        '%(asctime)s [%(levelname)s] [%(ip)s] [%(user_id)s] [%(method)s %(path)s] %(message)s'
    )
    
    # Configurar manejador
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Añadir manejador al logger
    security_logger.addHandler(file_handler)
    
    # Crear manejador de archivo para logs de seguridad en formato JSON
    json_log_file = os.path.join(log_dir, 'security.json.log')
    json_handler = logging.handlers.RotatingFileHandler(
        json_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    
    # Crear formateador JSON
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Añadir información de la solicitud si está disponible
            if hasattr(record, 'ip'):
                log_data['ip'] = record.ip
                log_data['method'] = record.method
                log_data['path'] = record.path
                log_data['user_agent'] = record.user_agent
                log_data['user_id'] = record.user_id
                log_data['username'] = record.username
            
            # Añadir información adicional si está disponible
            if hasattr(record, 'data') and record.data:
                log_data['data'] = record.data
            
            return json.dumps(log_data)
    
    # Configurar manejador JSON
    json_handler.setFormatter(JsonFormatter())
    json_handler.setLevel(logging.INFO)
    
    # Añadir manejador JSON al logger
    security_logger.addHandler(json_handler)
    
    # Registrar middleware para logging de solicitudes
    @app.before_request
    def log_request_start():
        """
        Registra el inicio de una solicitud.
        """
        # Ignorar solicitudes a rutas estáticas
        if request.path.startswith('/static'):
            return None
        
        # Registrar inicio de solicitud
        security_logger.info(
            f"Solicitud iniciada: {request.method} {request.path}"
        )
        
        # Almacenar tiempo de inicio
        g.request_start_time = datetime.utcnow()
        
        return None
    
    @app.after_request
    def log_request_end(response):
        """
        Registra el fin de una solicitud.
        
        Args:
            response: Respuesta HTTP
            
        Returns:
            Respuesta HTTP
        """
        # Ignorar solicitudes a rutas estáticas
        if request.path.startswith('/static'):
            return response
        
        # Calcular tiempo de respuesta
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds()
        else:
            duration = 0
        
        # Registrar fin de solicitud
        security_logger.info(
            f"Solicitud completada: {request.method} {request.path} "
            f"- Estado: {response.status_code} - Duración: {duration:.3f}s"
        )
        
        return response
    
    # Registrar manejador de errores
    @app.errorhandler(Exception)
    def log_exception(error):
        """
        Registra excepciones no manejadas.
        
        Args:
            error: Excepción
            
        Returns:
            Respuesta de error
        """
        security_logger.error(
            f"Excepción no manejada: {str(error)}",
            exc_info=True
        )
        
        # Continuar con el manejo normal de errores
        raise error
    
    logger.info("Logging de seguridad configurado")


def log_security_event(event_type: str, message: str, data: Optional[Dict[str, Any]] = None,
                      level: str = 'info') -> None:
    """
    Registra un evento de seguridad.
    
    Args:
        event_type: Tipo de evento
        message: Mensaje descriptivo
        data: Datos adicionales (opcional)
        level: Nivel de log (info, warning, error, critical)
    """
    # Obtener logger de seguridad
    security_logger = logging.getLogger('adflux.security')
    
    # Crear registro con datos adicionales
    log_record = logging.LogRecord(
        name=security_logger.name,
        level=getattr(logging, level.upper()),
        pathname=__file__,
        lineno=0,
        msg=f"[{event_type}] {message}",
        args=(),
        exc_info=None
    )
    
    # Añadir datos adicionales
    log_record.data = data
    
    # Procesar registro
    for handler in security_logger.handlers:
        if log_record.levelno >= handler.level:
            handler.handle(log_record)


def log_authentication_event(event: str, user_id: Optional[int] = None, username: Optional[str] = None,
                           success: bool = True, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Registra un evento de autenticación.
    
    Args:
        event: Tipo de evento (login, logout, password_change, etc.)
        user_id: ID del usuario (opcional)
        username: Nombre de usuario (opcional)
        success: Si el evento fue exitoso
        details: Detalles adicionales (opcional)
    """
    # Crear datos del evento
    data = {
        'user_id': user_id,
        'username': username,
        'success': success
    }
    
    # Añadir detalles adicionales
    if details:
        data.update(details)
    
    # Determinar nivel de log
    level = 'info' if success else 'warning'
    
    # Registrar evento
    log_security_event(
        event_type='authentication',
        message=f"Evento de autenticación: {event}",
        data=data,
        level=level
    )


def log_authorization_event(event: str, user_id: Optional[int] = None, username: Optional[str] = None,
                          resource: Optional[str] = None, action: Optional[str] = None,
                          success: bool = True, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Registra un evento de autorización.
    
    Args:
        event: Tipo de evento (access_denied, permission_change, etc.)
        user_id: ID del usuario (opcional)
        username: Nombre de usuario (opcional)
        resource: Recurso afectado (opcional)
        action: Acción intentada (opcional)
        success: Si el evento fue exitoso
        details: Detalles adicionales (opcional)
    """
    # Crear datos del evento
    data = {
        'user_id': user_id,
        'username': username,
        'resource': resource,
        'action': action,
        'success': success
    }
    
    # Añadir detalles adicionales
    if details:
        data.update(details)
    
    # Determinar nivel de log
    level = 'info' if success else 'warning'
    
    # Registrar evento
    log_security_event(
        event_type='authorization',
        message=f"Evento de autorización: {event}",
        data=data,
        level=level
    )


def log_data_access_event(event: str, user_id: Optional[int] = None, username: Optional[str] = None,
                        resource: Optional[str] = None, resource_id: Optional[str] = None,
                        action: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Registra un evento de acceso a datos.
    
    Args:
        event: Tipo de evento (read, create, update, delete, etc.)
        user_id: ID del usuario (opcional)
        username: Nombre de usuario (opcional)
        resource: Tipo de recurso (opcional)
        resource_id: ID del recurso (opcional)
        action: Acción realizada (opcional)
        details: Detalles adicionales (opcional)
    """
    # Crear datos del evento
    data = {
        'user_id': user_id,
        'username': username,
        'resource': resource,
        'resource_id': resource_id,
        'action': action
    }
    
    # Añadir detalles adicionales
    if details:
        data.update(details)
    
    # Registrar evento
    log_security_event(
        event_type='data_access',
        message=f"Evento de acceso a datos: {event}",
        data=data,
        level='info'
    )


def log_security_violation(event: str, severity: str = 'warning',
                         details: Optional[Dict[str, Any]] = None) -> None:
    """
    Registra una violación de seguridad.
    
    Args:
        event: Tipo de evento (xss, csrf, injection, etc.)
        severity: Severidad de la violación (warning, error, critical)
        details: Detalles adicionales (opcional)
    """
    # Crear datos del evento
    data = {
        'severity': severity
    }
    
    # Añadir detalles adicionales
    if details:
        data.update(details)
    
    # Registrar evento
    log_security_event(
        event_type='security_violation',
        message=f"Violación de seguridad detectada: {event}",
        data=data,
        level=severity
    )
