"""
Módulo de validación para AdFlux.

Este módulo proporciona clases y funciones para validar datos de entrada
utilizando Pydantic.
"""

from .base import BaseModel, ValidationError
from .campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from .candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from .job import JobCreate, JobUpdate, JobResponse
from .segment import SegmentCreate, SegmentUpdate, SegmentResponse
from .report import ReportRequest, ReportResponse
from .validators import validate_email, validate_phone, validate_url

__all__ = [
    'BaseModel',
    'ValidationError',
    'CampaignCreate',
    'CampaignUpdate',
    'CampaignResponse',
    'CandidateCreate',
    'CandidateUpdate',
    'CandidateResponse',
    'JobCreate',
    'JobUpdate',
    'JobResponse',
    'SegmentCreate',
    'SegmentUpdate',
    'SegmentResponse',
    'ReportRequest',
    'ReportResponse',
    'validate_email',
    'validate_phone',
    'validate_url',
]
