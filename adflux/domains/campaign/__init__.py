"""
Dominio de campaña para AdFlux.

Este módulo contiene todo lo relacionado con el dominio de campaña,
incluyendo modelos, servicios, rutas, etc.
"""

from .models import Campaign
from .service import CampaignService

__all__ = [
    "Campaign",
    "CampaignService",
]
