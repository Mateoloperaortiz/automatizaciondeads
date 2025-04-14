"""
Servicio para estadísticas de trabajos del dashboard.

Este servicio proporciona estadísticas relacionadas con trabajos,
como estado de trabajos, distribución por ubicación, etc.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import func

from ...models import db, JobOpening
from .base_metrics_service import BaseMetricsService


class JobStatsService(BaseMetricsService):
    """
    Servicio para obtener estadísticas relacionadas con trabajos.
    
    Proporciona métricas como estado de trabajos, distribución por ubicación, etc.
    """
    
    def get_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene estadísticas relacionadas con trabajos.
        
        Args:
            start_date: Fecha de inicio para filtrar datos (no utilizada actualmente)
            end_date: Fecha de fin para filtrar datos (no utilizada actualmente)
            
        Returns:
            Diccionario con estadísticas de trabajos
        """
        stats = {
            "job_status_chart_data": {"labels": [], "data": []},
        }
        
        # Obtener estado de trabajos
        stats.update(self._get_job_status_stats())
        
        return stats
    
    def _get_job_status_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de estado de trabajos.
        
        Returns:
            Diccionario con estadísticas de estado de trabajos
        """
        result = {
            "job_status_chart_data": {"labels": [], "data": []},
        }
        
        job_status_counts = self.execute_query_safely(
            lambda: db.session.query(JobOpening.status, func.count(JobOpening.job_id))
                .group_by(JobOpening.status)
                .all(),
            "Error al obtener estadísticas de estado de trabajos",
            []
        )
        
        valid_job_statuses = {str(status).title(): count for status, count in job_status_counts if status is not None}
        
        if valid_job_statuses:
            result["job_status_chart_data"] = self.prepare_chart_data(
                list(valid_job_statuses.keys()),
                list(valid_job_statuses.values())
            )
        
        return result
