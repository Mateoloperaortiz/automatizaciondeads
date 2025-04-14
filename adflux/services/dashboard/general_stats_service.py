"""
Servicio para estadísticas generales del dashboard.

Este servicio proporciona estadísticas generales como el número total
de trabajos, campañas y candidatos.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import func

from ...models import db, JobOpening, Campaign, Candidate
from .base_metrics_service import BaseMetricsService


class GeneralStatsService(BaseMetricsService):
    """
    Servicio para obtener estadísticas generales del sistema.
    
    Proporciona métricas como el número total de trabajos, campañas y candidatos.
    """
    
    def get_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del sistema.
        
        Args:
            start_date: Fecha de inicio (no utilizada para estadísticas generales)
            end_date: Fecha de fin (no utilizada para estadísticas generales)
            
        Returns:
            Diccionario con estadísticas generales
        """
        stats = {
            "total_jobs": 0,
            "total_campaigns": 0,
            "total_candidates": 0,
        }
        
        # Obtener total de trabajos
        stats["total_jobs"] = self.execute_query_safely(
            lambda: db.session.query(func.count(JobOpening.job_id)).scalar() or 0,
            "Error al obtener total de trabajos",
            0
        )
        
        # Obtener total de campañas
        stats["total_campaigns"] = self.execute_query_safely(
            lambda: db.session.query(func.count(Campaign.id)).scalar() or 0,
            "Error al obtener total de campañas",
            0
        )
        
        # Obtener total de candidatos
        stats["total_candidates"] = self.execute_query_safely(
            lambda: db.session.query(func.count(Candidate.candidate_id)).scalar() or 0,
            "Error al obtener total de candidatos",
            0
        )
        
        return stats
