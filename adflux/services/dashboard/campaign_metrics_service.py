"""
Servicio para métricas de campañas del dashboard.

Este servicio proporciona métricas relacionadas con campañas,
como estado de campañas, gasto, impresiones, clics, etc.
"""

from datetime import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy import func, desc

from ...models import db, Campaign, MetaInsight
from ...constants import CAMPAIGN_STATUS
from .base_metrics_service import BaseMetricsService


class CampaignMetricsService(BaseMetricsService):
    """
    Servicio para obtener métricas relacionadas con campañas.
    
    Proporciona métricas como estado de campañas, gasto, impresiones, clics, etc.
    """
    
    def get_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene métricas relacionadas con campañas.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con métricas de campañas
        """
        stats = {
            "status_counts": {},
            "status_chart_data": {"labels": [], "data": []},
            "total_spend": 0.0,
            "total_impressions": 0,
            "total_clicks": 0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
            "spend_over_time_chart": {"labels": [], "data": []},
            "top_campaigns": [],
        }
        
        # Obtener estado de campañas
        stats.update(self._get_campaign_status_stats())
        
        # Obtener métricas de rendimiento
        stats.update(self._get_performance_metrics(start_date, end_date))
        
        # Obtener gasto a lo largo del tiempo
        stats.update(self._get_spend_over_time(start_date, end_date))
        
        # Obtener campañas de mayor rendimiento
        stats.update(self._get_top_campaigns(start_date, end_date))
        
        return stats
    
    def _get_campaign_status_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de estado de campañas.
        
        Returns:
            Diccionario con estadísticas de estado de campañas
        """
        result = {
            "status_counts": {},
            "status_chart_data": {"labels": [], "data": []},
        }
        
        campaigns_by_status = self.execute_query_safely(
            lambda: db.session.query(Campaign.status, func.count(Campaign.id))
                .group_by(Campaign.status)
                .all(),
            "Error al obtener estadísticas de estado de campañas",
            []
        )
        
        standardized_status_counts = {}
        for status, count in campaigns_by_status:
            if status is not None:
                standardized_status = CAMPAIGN_STATUS.get(status.upper(), status.title())
                standardized_status_counts[standardized_status] = standardized_status_counts.get(standardized_status, 0) + count
        
        result["status_counts"] = standardized_status_counts
        
        if standardized_status_counts:
            result["status_chart_data"] = self.prepare_chart_data(
                list(standardized_status_counts.keys()),
                list(standardized_status_counts.values())
            )
        
        return result
    
    def _get_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento de campañas.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con métricas de rendimiento
        """
        result = {
            "total_spend": 0.0,
            "total_impressions": 0,
            "total_clicks": 0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
        }
        
        def query_performance_totals():
            return MetaInsight.query.filter(
                MetaInsight.date_start >= start_date,
                MetaInsight.date_stop <= end_date
            ).with_entities(
                func.sum(MetaInsight.spend),
                func.sum(MetaInsight.impressions),
                func.sum(MetaInsight.clicks),
            ).first()
        
        performance_totals = self.execute_query_safely(
            query_performance_totals,
            "Error al obtener métricas de rendimiento",
            (0.0, 0, 0)
        )
        
        total_spend = float(performance_totals[0] or 0.0)
        total_impressions = int(performance_totals[1] or 0)
        total_clicks = int(performance_totals[2] or 0)
        
        result["total_spend"] = total_spend
        result["total_impressions"] = total_impressions
        result["total_clicks"] = total_clicks
        result["ctr"] = (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0
        result["cpc"] = total_spend / total_clicks if total_clicks > 0 else 0.0
        result["cpm"] = (total_spend / total_impressions) * 1000.0 if total_impressions > 0 else 0.0
        
        return result
    
    def _get_spend_over_time(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene datos de gasto a lo largo del tiempo.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con datos de gasto a lo largo del tiempo
        """
        result = {
            "spend_over_time_chart": {"labels": [], "data": []},
        }
        
        def query_spend_over_time():
            return MetaInsight.query.filter(
                MetaInsight.date_start >= start_date,
                MetaInsight.date_stop <= end_date
            ).with_entities(
                MetaInsight.date_start,
                func.sum(MetaInsight.spend)
            ).group_by(
                MetaInsight.date_start
            ).order_by(
                MetaInsight.date_start
            ).all()
        
        spend_over_time = self.execute_query_safely(
            query_spend_over_time,
            "Error al obtener datos de gasto a lo largo del tiempo",
            []
        )
        
        valid_spend_data = [(date.strftime("%Y-%m-%d"), float(spend or 0.0)) for date, spend in spend_over_time]
        
        if valid_spend_data:
            result["spend_over_time_chart"] = self.prepare_chart_data(
                [item[0] for item in valid_spend_data],
                [item[1] for item in valid_spend_data]
            )
        
        return result
    
    def _get_top_campaigns(self, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene las campañas de mayor rendimiento.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con lista de campañas de mayor rendimiento
        """
        result = {
            "top_campaigns": [],
        }
        
        def query_top_campaigns():
            return db.session.query(
                Campaign.id.label("campaign_id"),
                Campaign.name.label("campaign_name"),
                func.sum(MetaInsight.spend).label("total_spend"),
                func.sum(MetaInsight.impressions).label("total_impressions"),
                func.sum(MetaInsight.clicks).label("total_clicks"),
            ).select_from(
                MetaInsight
            ).join(
                Campaign,
                Campaign.external_id == MetaInsight.meta_campaign_id
            ).filter(
                MetaInsight.date_start >= start_date,
                MetaInsight.date_stop <= end_date
            ).group_by(
                Campaign.id,
                Campaign.name
            ).having(
                func.sum(MetaInsight.clicks) > 0
            ).order_by(
                func.sum(MetaInsight.clicks).desc()
            ).limit(5).all()
        
        top_campaign_results = self.execute_query_safely(
            query_top_campaigns,
            "Error al obtener campañas de mayor rendimiento",
            []
        )
        
        top_campaign_data = []
        for row in top_campaign_results:
            spend = float(row.total_spend or 0.0)
            impressions = int(row.total_impressions or 0)
            clicks = int(row.total_clicks or 0)
            ctr = (clicks / impressions) * 100.0 if impressions > 0 else 0.0
            
            top_campaign_data.append({
                "id": row.campaign_id,
                "name": row.campaign_name,
                "spend": round(spend, 2),
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr, 2),
            })
        
        result["top_campaigns"] = top_campaign_data
        
        return result
