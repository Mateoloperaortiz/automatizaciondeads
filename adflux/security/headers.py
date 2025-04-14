"""
Cabeceras HTTP de seguridad para AdFlux.

Este módulo proporciona funciones para configurar cabeceras HTTP de seguridad,
como Content-Security-Policy, X-XSS-Protection, etc.
"""

import logging
from typing import Dict, List, Optional

from flask import Flask, Response, request


# Configurar logger
logger = logging.getLogger(__name__)


def setup_security_headers(app: Flask) -> None:
    """
    Configura cabeceras HTTP de seguridad en la aplicación Flask.
    
    Args:
        app: Aplicación Flask
    """
    @app.after_request
    def add_security_headers(response: Response) -> Response:
        """
        Añade cabeceras de seguridad a las respuestas HTTP.
        
        Args:
            response: Respuesta HTTP
            
        Returns:
            Respuesta HTTP con cabeceras de seguridad
        """
        # Content Security Policy (CSP)
        # Restringir fuentes de contenido para prevenir XSS
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
            "img-src 'self' data: https:",
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net",
            "connect-src 'self'",
            "frame-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'self'",
            "upgrade-insecure-requests"
        ]
        response.headers['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # X-Content-Type-Options
        # Prevenir MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        # Prevenir clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # X-XSS-Protection
        # Habilitar protección XSS en navegadores antiguos
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        # Controlar información de referencia
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Strict-Transport-Security (HSTS)
        # Forzar HTTPS
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Feature-Policy / Permissions-Policy
        # Restringir características del navegador
        permissions_policy = [
            "accelerometer=())",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()"
        ]
        response.headers['Permissions-Policy'] = ', '.join(permissions_policy)
        
        # Cache-Control
        # Prevenir almacenamiento en caché de información sensible
        if request.path.startswith('/api') or request.path.startswith('/auth'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    logger.info("Cabeceras de seguridad configuradas")


def get_csp_report_uri() -> str:
    """
    Obtiene la URI para reportes CSP.
    
    Returns:
        URI para reportes CSP
    """
    return '/api/security/csp-report'


def setup_csp_reporting(app: Flask) -> None:
    """
    Configura reportes de violaciones CSP.
    
    Args:
        app: Aplicación Flask
    """
    @app.route('/api/security/csp-report', methods=['POST'])
    def csp_report():
        """
        Endpoint para recibir reportes de violaciones CSP.
        
        Returns:
            Respuesta vacía
        """
        try:
            report = request.get_json()
            logger.warning(f"Violación CSP detectada: {report}")
            
            # Aquí se podría almacenar el reporte en la base de datos
            # o enviar una notificación
            
            return '', 204
        
        except Exception as e:
            logger.error(f"Error al procesar reporte CSP: {str(e)}")
            return '', 400
    
    # Actualizar CSP para incluir report-uri
    @app.after_request
    def add_csp_report_uri(response: Response) -> Response:
        """
        Añade report-uri a la cabecera CSP.
        
        Args:
            response: Respuesta HTTP
            
        Returns:
            Respuesta HTTP con report-uri en CSP
        """
        if 'Content-Security-Policy' in response.headers:
            csp = response.headers['Content-Security-Policy']
            report_uri = get_csp_report_uri()
            
            if 'report-uri' not in csp:
                csp += f"; report-uri {report_uri}"
                response.headers['Content-Security-Policy'] = csp
        
        return response
    
    logger.info("Reportes CSP configurados")
