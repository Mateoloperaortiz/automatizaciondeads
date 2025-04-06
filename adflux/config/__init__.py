"""
Paquete de configuración para AdFlux.

Este paquete contiene las clases de configuración para diferentes entornos.
"""

import os

# Determinar el entorno actual
ENV = os.environ.get('FLASK_ENV', 'development')

# Importar la configuración adecuada según el entorno
if ENV == 'production':
    from .production import ProductionConfig as Config
elif ENV == 'testing':
    from .testing import TestingConfig as Config
else:
    from .development import DevelopmentConfig as Config

# Exportar la configuración
__all__ = ['Config']
