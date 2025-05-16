"""
Módulo de servicios para AdFlux.

Este paquete contiene la capa de servicios que centraliza la lógica de negocio
y separa las preocupaciones entre las rutas y los modelos.
"""

# Importar servicios para hacerlos disponibles a través de adflux.services
from .job_service import JobService
from .campaign_service import CampaignService
from .dashboard.dashboard_service import DashboardService
from .segmentation_service import SegmentationService
from .report_service import ReportService
from .application_service import ApplicationService
from .candidate_service import CandidateService
from .settings_service import SettingsService
from .creative_service import CreativeService
from .recommendation_service import RecommendationService

# Definir __all__ para importaciones con wildcard
__all__ = [
    "JobService",
    "CampaignService",
    "DashboardService",
    "SegmentationService",
    "ReportService",
    "ApplicationService",
    "CandidateService",
    "SettingsService",
    "CreativeService",
    "RecommendationService",
]
