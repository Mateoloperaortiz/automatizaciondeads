"""
Paquete de modelos para AdFlux.

Este paquete contiene todos los modelos de base de datos utilizados por AdFlux,
organizados en módulos específicos según su funcionalidad.
"""

# Importar db desde extensions para evitar múltiples instancias de SQLAlchemy
from ..extensions import db

# Importar modelos principales
from .base import create_tables, init_db_connection
from .segment import Segment
from .job import JobOpening
from .candidate import Candidate
from .application import Application

# Importar modelos de Meta
from .meta import MetaCampaign, MetaAdSet, MetaAd, MetaInsight

# Importar modelos de campaña
from .campaign import Campaign

# Para mantener compatibilidad con el código existente
__all__ = [
    # SQLAlchemy
    'db',

    # Funciones de base de datos
    'create_tables',
    'init_db_connection',

    # Modelos principales
    'Segment',
    'JobOpening',
    'Candidate',
    'Application',

    # Modelos de Meta
    'MetaCampaign',
    'MetaAdSet',
    'MetaAd',
    'MetaInsight',

    # Modelos de campaña
    'Campaign'
]
