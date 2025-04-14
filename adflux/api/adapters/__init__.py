"""
Módulo de adaptadores para APIs externas.

Este módulo contiene los adaptadores que implementan las interfaces abstractas
para las APIs externas utilizadas por AdFlux.
"""

from .meta_adapter import MetaAdAPI
from .google_adapter import GoogleAdAPI

__all__ = [
    'MetaAdAPI',
    'GoogleAdAPI',
]
