"""
Dominio de candidato para AdFlux.

Este módulo contiene todo lo relacionado con el dominio de candidato,
incluyendo modelos, servicios, rutas, etc.
"""

from .models import Candidate
from .service import CandidateService

__all__ = [
    "Candidate",
    "CandidateService",
]
