"""
Módulo de DTOs (Data Transfer Objects) para AdFlux.

Este módulo contiene los DTOs utilizados para transferir datos
entre la capa de presentación y la capa de lógica de negocio.
"""

from .base_dto import BaseDTO
from .candidate_dto import CandidateDTO, CandidateListDTO, CandidateCreateDTO, CandidateUpdateDTO
from .job_dto import JobDTO, JobListDTO, JobCreateDTO, JobUpdateDTO
from .campaign_dto import CampaignDTO, CampaignListDTO, CampaignCreateDTO, CampaignUpdateDTO
from .segment_dto import SegmentDTO, SegmentListDTO
from .report_dto import ReportRequestDTO, ReportResponseDTO

__all__ = [
    'BaseDTO',
    'CandidateDTO',
    'CandidateListDTO',
    'CandidateCreateDTO',
    'CandidateUpdateDTO',
    'JobDTO',
    'JobListDTO',
    'JobCreateDTO',
    'JobUpdateDTO',
    'CampaignDTO',
    'CampaignListDTO',
    'CampaignCreateDTO',
    'CampaignUpdateDTO',
    'SegmentDTO',
    'SegmentListDTO',
    'ReportRequestDTO',
    'ReportResponseDTO',
]
