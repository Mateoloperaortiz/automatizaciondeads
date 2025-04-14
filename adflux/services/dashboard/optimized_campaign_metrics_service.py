"""
Servicio optimizado para métricas de campañas.

Este servicio proporciona métricas relacionadas con campañas publicitarias,
utilizando consultas optimizadas para mejorar el rendimiento.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy import func, case, desc, text
from sqlalchemy.orm import aliased

from ...models import db, Campaign, MetaCampaign, MetaAdSet, MetaAd, MetaInsight
from .base_metrics_service import BaseMetricsService


class OptimizedCampaignMetricsService(BaseMetricsService):
    """
    Servicio optimizado para obtener métricas relacionadas con campañas.
    
    Proporciona métricas como estado de campañas, gasto, impresiones, etc.
    utilizando consultas optimizadas para mejorar el rendimiento.
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
        # Inicializar diccionario de estadísticas
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
        
        # Obtener todas las métricas en una sola consulta
        metrics = self._get_all_metrics(start_date, end_date)
        
        # Actualizar estadísticas con los resultados
        if metrics:
            stats.update(metrics)
        
        return stats
    
    def _get_all_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene todas las métricas de campañas en una sola consulta compuesta.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con todas las métricas de campañas
        """
        result = {
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
        
        try:
            # 1. Obtener estado de campañas
            status_counts = self._get_campaign_status_stats()
            result.update(status_counts)
            
            # 2. Obtener métricas de rendimiento en una sola consulta
            performance_metrics = db.session.query(
                func.sum(MetaInsight.spend).label('total_spend'),
                func.sum(MetaInsight.impressions).label('total_impressions'),
                func.sum(MetaInsight.clicks).label('total_clicks')
            ).filter(
                MetaInsight.date_start >= start_date,
                MetaInsight.date_stop <= end_date
            ).first()
            
            if performance_metrics:
                total_spend = float(performance_metrics.total_spend or 0.0)
                total_impressions = int(performance_metrics.total_impressions or 0)
                total_clicks = int(performance_metrics.total_clicks or 0)
                
                result["total_spend"] = total_spend
                result["total_impressions"] = total_impressions
                result["total_clicks"] = total_clicks
                result["ctr"] = (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0
                result["cpc"] = total_spend / total_clicks if total_clicks > 0 else 0.0
                result["cpm"] = (total_spend / total_impressions) * 1000.0 if total_impressions > 0 else 0.0
            
            # 3. Obtener gasto a lo largo del tiempo
            spend_over_time = db.session.query(
                func.date_trunc('day', MetaInsight.date_start).label('date'),
                func.sum(MetaInsight.spend).label('spend')
            ).filter(
                MetaInsight.date_start >= start_date,
                MetaInsight.date_stop <= end_date
            ).group_by(
                func.date_trunc('day', MetaInsight.date_start)
            ).order_by(
                func.date_trunc('day', MetaInsight.date_start)
            ).all()
            
            if spend_over_time:
                valid_spend_data = [(date.strftime("%Y-%m-%d"), float(spend or 0.0)) for date, spend in spend_over_time]
                
                result["spend_over_time_chart"] = self.prepare_chart_data(
                    [item[0] for item in valid_spend_data],
                    [item[1] for item in valid_spend_data]
                )
            
            # 4. Obtener campañas de mayor rendimiento
            # Unir tablas para obtener datos de campañas y sus métricas en una sola consulta
            campaign_alias = aliased(Campaign)
            meta_campaign_alias = aliased(MetaCampaign)
            
            top_campaigns = db.session.query(
                campaign_alias.id,
                campaign_alias.name,
                meta_campaign_alias.external_id,
                func.sum(MetaInsight.spend).label('total_spend'),
                func.sum(MetaInsight.impressions).label('total_impressions'),
                func.sum(MetaInsight.clicks).label('total_clicks'),
                (func.sum(MetaInsight.clicks) * 100.0 / func.nullif(func.sum(MetaInsight.impressions), 0)).label('ctr')
            ).join(
                meta_campaign_alias, campaign_alias.id == meta_campaign_alias.campaign_id
            ).join(
                MetaInsight, meta_campaign_alias.external_id == MetaInsight.meta_campaign_id
            ).filter(
                MetaInsight.date_start >= start_date,
                MetaInsight.date_stop <= end_date
            ).group_by(
                campaign_alias.id,
                campaign_alias.name,
                meta_campaign_alias.external_id
            ).order_by(
                desc('total_spend')
            ).limit(5).all()
            
            if top_campaigns:
                result["top_campaigns"] = [
                    {
                        "id": campaign.id,
                        "name": campaign.name,
                        "external_id": campaign.external_id,
                        "spend": float(campaign.total_spend or 0.0),
                        "impressions": int(campaign.total_impressions or 0),
                        "clicks": int(campaign.total_clicks or 0),
                        "ctr": float(campaign.ctr or 0.0)
                    }
                    for campaign in top_campaigns
                ]
            
        except Exception as e:
            self.errors.append(f"Error al obtener métricas de campañas: {str(e)}")
        
        return result
    
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
        
        try:
            # Consulta optimizada para contar campañas por estado
            status_counts = db.session.query(
                Campaign.status,
                func.count(Campaign.id).label('count')
            ).group_by(
                Campaign.status
            ).all()
            
            if status_counts:
                # Convertir resultados a diccionario
                status_dict = {status: count for status, count in status_counts}
                result["status_counts"] = status_dict
                
                # Preparar datos para gráfico
                result["status_chart_data"] = self.prepare_chart_data(
                    list(status_dict.keys()),
                    list(status_dict.values())
                )
            
        except Exception as e:
            self.errors.append(f"Error al obtener estadísticas de estado de campañas: {str(e)}")
        
        return result
    
    def prepare_chart_data(self, labels: List[str], data: List[Any]) -> Dict[str, List[Any]]:
        """
        Prepara datos para gráficos.
        
        Args:
            labels: Etiquetas para el gráfico
            data: Datos para el gráfico
            
        Returns:
            Diccionario con etiquetas y datos para el gráfico
        """
        return {
            "labels": labels,
            "data": data
        }
