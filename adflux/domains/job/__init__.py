"""
Dominio de trabajo para AdFlux.

Este módulo contiene todo lo relacionado con el dominio de trabajo,
incluyendo modelos, servicios, rutas, etc.
"""

from .models import JobOpening
from .service import JobService

__all__ = [
    "JobOpening",
    "JobService",
]
