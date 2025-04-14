"""
Rutas del API Gateway.

Este módulo define las rutas del API Gateway y cómo se enrutan
las solicitudes a los diferentes servicios.
"""

import requests
from flask import request, jsonify, current_app, Response, stream_with_context
from werkzeug.exceptions import BadGateway, ServiceUnavailable

from .circuit_breaker import circuit_breaker
from .auth import jwt_required, get_jwt_identity


def register_routes(app):
    """
    Registra todas las rutas del API Gateway.
    
    Args:
        app: Aplicación Flask
    """
    # Ruta de estado
    @app.route('/health')
    def health_check():
        """Endpoint para verificar el estado del API Gateway."""
        return jsonify({
            'status': 'ok',
            'version': '1.0.0',
            'services': _check_services_health()
        })
    
    # Rutas de autenticación
    @app.route('/api/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def auth_service(path):
        """
        Enruta solicitudes al servicio de autenticación.
        
        Args:
            path: Ruta relativa en el servicio de autenticación
            
        Returns:
            Respuesta del servicio de autenticación
        """
        return _proxy_request('auth', path)
    
    # Rutas de candidatos
    @app.route('/api/candidates/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @jwt_required()
    def candidate_service(path):
        """
        Enruta solicitudes al servicio de candidatos.
        
        Args:
            path: Ruta relativa en el servicio de candidatos
            
        Returns:
            Respuesta del servicio de candidatos
        """
        return _proxy_request('candidate', path)
    
    # Rutas de trabajos
    @app.route('/api/jobs/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @jwt_required()
    def job_service(path):
        """
        Enruta solicitudes al servicio de trabajos.
        
        Args:
            path: Ruta relativa en el servicio de trabajos
            
        Returns:
            Respuesta del servicio de trabajos
        """
        return _proxy_request('job', path)
    
    # Rutas de campañas
    @app.route('/api/campaigns/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @jwt_required()
    def campaign_service(path):
        """
        Enruta solicitudes al servicio de campañas.
        
        Args:
            path: Ruta relativa en el servicio de campañas
            
        Returns:
            Respuesta del servicio de campañas
        """
        return _proxy_request('campaign', path)
    
    # Rutas de machine learning
    @app.route('/api/ml/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @jwt_required()
    def ml_service(path):
        """
        Enruta solicitudes al servicio de machine learning.
        
        Args:
            path: Ruta relativa en el servicio de machine learning
            
        Returns:
            Respuesta del servicio de machine learning
        """
        return _proxy_request('ml', path)
    
    # Rutas de reportes
    @app.route('/api/reports/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @jwt_required()
    def report_service(path):
        """
        Enruta solicitudes al servicio de reportes.
        
        Args:
            path: Ruta relativa en el servicio de reportes
            
        Returns:
            Respuesta del servicio de reportes
        """
        return _proxy_request('report', path)
    
    # Ruta por defecto al monolito
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def monolith_fallback(path):
        """
        Enruta solicitudes al monolito para rutas no manejadas específicamente.
        
        Args:
            path: Ruta relativa en el monolito
            
        Returns:
            Respuesta del monolito
        """
        return _proxy_request('monolith', path)


@circuit_breaker
def _proxy_request(service_name, path):
    """
    Envía una solicitud proxy al servicio especificado.
    
    Args:
        service_name: Nombre del servicio destino
        path: Ruta relativa en el servicio
        
    Returns:
        Respuesta del servicio
        
    Raises:
        BadGateway: Si hay un error en la comunicación con el servicio
        ServiceUnavailable: Si el servicio no está disponible
    """
    service_config = current_app.config['SERVICES'].get(service_name)
    if not service_config:
        current_app.logger.error(f"Servicio no configurado: {service_name}")
        return jsonify({'error': 'Servicio no disponible'}), 503
    
    service_url = service_config['url']
    timeout = service_config['timeout']
    
    # Construir URL destino
    target_url = f"{service_url}/{path}"
    
    # Obtener headers, excluyendo los que no deben reenviarse
    headers = {key: value for key, value in request.headers.items()
               if key.lower() not in ['host', 'content-length']}
    
    # Añadir información de usuario si está autenticado
    try:
        user_id = get_jwt_identity()
        if user_id:
            headers['X-User-ID'] = str(user_id)
    except Exception:
        pass  # No hay usuario autenticado
    
    try:
        # Realizar solicitud al servicio
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            timeout=timeout,
            stream=True  # Para manejar respuestas grandes
        )
        
        # Crear respuesta Flask a partir de la respuesta del servicio
        flask_response = Response(
            stream_with_context(response.iter_content(chunk_size=1024)),
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )
        
        # Copiar headers relevantes
        for key, value in response.headers.items():
            if key.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                flask_response.headers[key] = value
        
        return flask_response
    
    except requests.exceptions.Timeout:
        current_app.logger.error(f"Timeout al conectar con {service_name}: {target_url}")
        raise ServiceUnavailable(f"El servicio {service_name} no responde")
    
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error al conectar con {service_name}: {target_url} - {str(e)}")
        raise BadGateway(f"Error al comunicarse con el servicio {service_name}")


def _check_services_health():
    """
    Verifica el estado de salud de todos los servicios.
    
    Returns:
        Diccionario con el estado de cada servicio
    """
    services_health = {}
    
    for service_name, service_config in current_app.config['SERVICES'].items():
        try:
            health_url = f"{service_config['url']}/health"
            response = requests.get(health_url, timeout=5)
            services_health[service_name] = {
                'status': 'ok' if response.status_code == 200 else 'error',
                'code': response.status_code
            }
        except Exception as e:
            services_health[service_name] = {
                'status': 'error',
                'message': str(e)
            }
    
    return services_health
