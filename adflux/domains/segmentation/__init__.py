"""
Dominio de segmentación para AdFlux.

Este módulo contiene todo lo relacionado con el dominio de segmentación,
incluyendo modelos, servicios, rutas, etc.
"""

from .models import Segment
from .service import SegmentationService

__all__ = [
    "Segment",
    "SegmentationService",
]
