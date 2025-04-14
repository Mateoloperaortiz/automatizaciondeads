"""
Paquete de servicios relacionados con el dashboard.

Este paquete contiene los servicios relacionados con el dashboard,
divididos en componentes más pequeños y especializados.
"""

from .base_metrics_service import BaseMetricsService
from .general_stats_service import GeneralStatsService
from .campaign_metrics_service import CampaignMetricsService
from .job_stats_service import JobStatsService
from .candidate_stats_service import CandidateStatsService
from .dashboard_service import DashboardService

__all__ = [
    "BaseMetricsService",
    "GeneralStatsService",
    "CampaignMetricsService",
    "JobStatsService",
    "CandidateStatsService",
    "DashboardService",
]
