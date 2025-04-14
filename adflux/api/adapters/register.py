"""
Registro de adaptadores para APIs externas.

Este módulo registra los adaptadores para las APIs externas en la fábrica de APIs.
"""

from ..abstract.api_factory import AdAPIFactory
from .meta_adapter import MetaAdAPI
from .google_adapter import GoogleAdAPI


def register_adapters():
    """Registra todos los adaptadores en la fábrica de APIs."""
    # Registrar adaptador para Meta Ads
    AdAPIFactory.register('meta', MetaAdAPI)
    
    # Registrar adaptador para Google Ads
    AdAPIFactory.register('google', GoogleAdAPI)
    
    # Aquí se pueden registrar más adaptadores en el futuro
    # AdAPIFactory.register('tiktok', TikTokAdAPI)
    # AdAPIFactory.register('snapchat', SnapchatAdAPI)


# Registrar adaptadores automáticamente al importar el módulo
register_adapters()
