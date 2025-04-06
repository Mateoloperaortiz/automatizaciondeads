"""
Configuración general de Swagger UI para AdFlux.

Este módulo contiene la configuración general de Swagger UI para la API de AdFlux.
"""

# Importar configuraciones específicas
from .paths.jobs import JOB_PATHS
from .paths.candidates import CANDIDATE_PATHS
from .paths.applications import APPLICATION_PATHS
from .paths.meta import META_PATHS
from .definitions import DEFINITIONS

# Definir la especificación JSON de Swagger
SWAGGER_SPEC = {
    "swagger": "2.0",
    "info": {
        "title": "AdFlux API",
        "description": "API for managing job openings and candidates",
        "version": "1.0"
    },
    "basePath": "/api",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "paths": {
        # Combinar todas las rutas
        **JOB_PATHS,
        **CANDIDATE_PATHS,
        **APPLICATION_PATHS,
        **META_PATHS
    },
    "definitions": DEFINITIONS
}
