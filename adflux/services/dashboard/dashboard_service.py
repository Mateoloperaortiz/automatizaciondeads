"""
Servicio principal del dashboard.

Este servicio coordina los servicios especializados para obtener
todos los datos necesarios para el dashboard.
"""

from datetime import datetime
from typing import Dict, Any, List

from ...services.interfaces import IDashboardService
from .general_stats_service import GeneralStatsService
from .campaign_metrics_service import CampaignMetricsService
from .job_stats_service import JobStatsService
from .candidate_stats_service import CandidateStatsService


class DashboardService(IDashboardService):
    """
    Servicio principal del dashboard.
    
    Coordina los servicios especializados para obtener todos los datos
    necesarios para el dashboard.
    """
    
    def __init__(self):
        """Inicializa el servicio del dashboard con sus servicios especializados."""
        self.general_stats_service = GeneralStatsService()
        self.campaign_metrics_service = CampaignMetricsService()
        self.job_stats_service = JobStatsService()
        self.candidate_stats_service = CandidateStatsService()
    
    def get_dashboard_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Recopila y procesa todos los datos necesarios para el dashboard.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con todos los datos procesados para el dashboard
        """
        # Inicializar diccionario de estadísticas
        stats = {
            "errors": []  # Para recopilar errores no críticos
        }
        
        # Obtener estadísticas generales
        stats.update(self.general_stats_service.get_metrics(start_date, end_date))
        stats["errors"].extend(self.general_stats_service.get_errors())
        
        # Obtener métricas de campañas
        stats.update(self.campaign_metrics_service.get_metrics(start_date, end_date))
        stats["errors"].extend(self.campaign_metrics_service.get_errors())
        
        # Obtener estadísticas de trabajos
        stats.update(self.job_stats_service.get_metrics(start_date, end_date))
        stats["errors"].extend(self.job_stats_service.get_errors())
        
        # Obtener estadísticas de candidatos
        stats.update(self.candidate_stats_service.get_metrics(start_date, end_date))
        stats["errors"].extend(self.candidate_stats_service.get_errors())
        
        return stats
