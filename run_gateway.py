#!/usr/bin/env python
"""
Script para ejecutar el API Gateway de AdFlux.

Este script inicia el API Gateway en modo de desarrollo.
"""

import os
from adflux.gateway import create_gateway_app

if __name__ == '__main__':
    # Configurar entorno
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Crear aplicación
    app = create_gateway_app()
    
    # Ejecutar servidor
    app.run(
        host=os.environ.get('GATEWAY_HOST', '0.0.0.0'),
        port=int(os.environ.get('GATEWAY_PORT', '5000')),
        debug=True
    )
