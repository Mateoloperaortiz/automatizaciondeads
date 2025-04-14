"""
Configuración de logging para el API Gateway.

Este módulo configura el sistema de logging para el API Gateway.
"""

import logging
import json
import sys
from flask import request, g
from pythonjsonlogger import jsonlogger


class RequestInfoFilter(logging.Filter):
    """
    Filtro que añade información de la solicitud a los registros de log.
    """
    
    def filter(self, record):
        """
        Añade información de la solicitud al registro de log.
        
        Args:
            record: Registro de log
            
        Returns:
            True para incluir el registro, False para excluirlo
        """
        record.request_id = getattr(g, 'request_id', 'N/A')
        record.remote_addr = request.remote_addr if request else 'N/A'
        record.method = request.method if request else 'N/A'
        record.path = request.path if request else 'N/A'
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Formateador JSON personalizado para logs.
    """
    
    def add_fields(self, log_record, record, message_dict):
        """
        Añade campos adicionales al registro de log.
        
        Args:
            log_record: Registro de log en formato JSON
            record: Registro de log original
            message_dict: Diccionario de mensaje
        """
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['request_id'] = getattr(record, 'request_id', 'N/A')
        log_record['remote_addr'] = getattr(record, 'remote_addr', 'N/A')
        log_record['method'] = getattr(record, 'method', 'N/A')
        log_record['path'] = getattr(record, 'path', 'N/A')


def configure_logging(app):
    """
    Configura el sistema de logging para el API Gateway.
    
    Args:
        app: Aplicación Flask
    """
    # Obtener nivel de log de la configuración
    log_level_name = app.config.get('LOG_LEVEL', 'INFO')
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Configurar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Determinar el formato según la configuración
    if app.config.get('LOG_FORMAT') == 'json':
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - '
            '%(request_id)s - %(remote_addr)s - %(method)s %(path)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    
    # Configurar filtro para añadir información de la solicitud
    request_filter = RequestInfoFilter()
    handler.addFilter(request_filter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Eliminar handlers existentes
    for hdlr in root_logger.handlers:
        root_logger.removeHandler(hdlr)
    
    root_logger.addHandler(handler)
    
    # Configurar logger específico para el API Gateway
    logger = logging.getLogger('adflux.gateway')
    logger.setLevel(log_level)
    
    # Configurar loggers de bibliotecas externas
    for logger_name in ['werkzeug', 'requests', 'urllib3']:
        ext_logger = logging.getLogger(logger_name)
        ext_logger.setLevel(logging.WARNING)  # Reducir verbosidad
    
    # Registrar inicio del API Gateway
    logger.info(f"API Gateway iniciado con nivel de log: {log_level_name}")
    
    return logger
