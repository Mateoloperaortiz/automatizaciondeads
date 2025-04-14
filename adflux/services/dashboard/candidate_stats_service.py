"""
Servicio para estadísticas de candidatos del dashboard.

Este servicio proporciona estadísticas relacionadas con candidatos,
como distribución por segmento, habilidades, etc.
"""

from datetime import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy import func

from ...models import db, Candidate
from ...constants import SEGMENT_MAP, DEFAULT_SEGMENT_NAME
from .base_metrics_service import BaseMetricsService


class CandidateStatsService(BaseMetricsService):
    """
    Servicio para obtener estadísticas relacionadas con candidatos.
    
    Proporciona métricas como distribución por segmento, habilidades, etc.
    """
    
    def get_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene estadísticas relacionadas con candidatos.
        
        Args:
            start_date: Fecha de inicio para filtrar datos (no utilizada actualmente)
            end_date: Fecha de fin para filtrar datos (no utilizada actualmente)
            
        Returns:
            Diccionario con estadísticas de candidatos
        """
        stats = {
            "segment_chart_data": {"labels": [], "data": []},
        }
        
        # Obtener distribución por segmento
        stats.update(self._get_segment_distribution())
        
        return stats
    
    def _get_segment_distribution(self) -> Dict[str, Any]:
        """
        Obtiene la distribución de candidatos por segmento.
        
        Returns:
            Diccionario con distribución de candidatos por segmento
        """
        result = {
            "segment_chart_data": {"labels": [], "data": []},
        }
        
        segment_counts = self.execute_query_safely(
            lambda: db.session.query(Candidate.segment_id, func.count(Candidate.candidate_id))
                .group_by(Candidate.segment_id)
                .order_by(Candidate.segment_id)
                .all(),
            "Error al obtener estadísticas de segmentos de candidatos",
            []
        )
        
        seg_labels = []
        seg_data = []
        
        for s_id, count in segment_counts:
            seg_labels.append(SEGMENT_MAP.get(s_id, DEFAULT_SEGMENT_NAME) if s_id is not None else "Sin segmentar")
            seg_data.append(count)
        
        if seg_labels:
            result["segment_chart_data"] = self.prepare_chart_data(seg_labels, seg_data)
        
        return result
