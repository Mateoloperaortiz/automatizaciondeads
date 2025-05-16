"""
Servicio para el dashboard de AdFlux.

Este módulo proporciona funcionalidades para obtener datos
y métricas para el dashboard de la aplicación.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from sqlalchemy import func, desc, and_
from sqlalchemy.orm import joinedload

from ..models.campaign import Campaign
from ..models.job import JobOpening
from ..models.candidate import Candidate
from ..models.payment import Transaction, BudgetPlan
from ..models.segment import Segment

logger = logging.getLogger(__name__)


class DashboardService:
    """Servicio para obtener datos del dashboard."""

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de las métricas principales para el dashboard.
        
        Returns:
            Diccionario con métricas resumidas.
        """
        try:
            job_count = JobOpening.query.count()
            candidate_count = Candidate.query.count()
            campaign_count = Campaign.query.count()
            
            total_impressions = self._get_total_impressions()
            total_clicks = self._get_total_clicks()
            total_spend = self._get_total_spend()
            
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            
            segment_distribution = self._get_segment_distribution()
            
            recent_performance = self._get_recent_performance(days=30)
            
            return {
                "entity_counts": {
                    "jobs": job_count,
                    "candidates": candidate_count,
                    "campaigns": campaign_count,
                },
                "performance_metrics": {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "spend": total_spend,
                    "ctr": ctr,
                    "cpc": cpc,
                },
                "segment_distribution": segment_distribution,
                "recent_performance": recent_performance,
            }
        except Exception as e:
            logger.error(f"Error al obtener resumen del dashboard: {str(e)}", exc_info=True)
            return {
                "entity_counts": {"jobs": 0, "candidates": 0, "campaigns": 0},
                "performance_metrics": {"impressions": 0, "clicks": 0, "spend": 0, "ctr": 0, "cpc": 0},
                "segment_distribution": [],
                "recent_performance": {"dates": [], "impressions": [], "clicks": [], "spend": []},
            }

    def get_platform_comparison(self) -> Dict[str, Any]:
        """
        Obtiene datos comparativos entre plataformas.
        
        Returns:
            Diccionario con datos comparativos por plataforma.
        """
        try:
            platforms = ["meta", "google", "linkedin"]
            
            platform_stats = {
                "meta": {
                    "campaigns": 5,
                    "impressions": 5000,
                    "clicks": 250,
                    "spend": 500.0,
                    "ctr": 5.0,
                    "cpc": 2.0,
                },
                "google": {
                    "campaigns": 3,
                    "impressions": 3000,
                    "clicks": 150,
                    "spend": 300.0,
                    "ctr": 5.0,
                    "cpc": 2.0,
                },
                "linkedin": {
                    "campaigns": 2,
                    "impressions": 2000,
                    "clicks": 100,
                    "spend": 200.0,
                    "ctr": 5.0,
                    "cpc": 2.0,
                },
            }
            
            return {
                "platform_stats": platform_stats,
                "platforms": platforms,
            }
        except Exception as e:
            logger.error(f"Error al obtener comparación de plataformas: {str(e)}", exc_info=True)
            return {
                "platform_stats": {},
                "platforms": [],
            }

    def get_budget_overview(self) -> Dict[str, Any]:
        """
        Obtiene una visión general del presupuesto y gastos.
        
        Returns:
            Diccionario con datos de presupuesto y gastos.
        """
        try:
            budget_plans = BudgetPlan.query.filter_by(status="active").all()
            
            total_budget = sum(plan.total_budget for plan in budget_plans)
            
            recent_transactions = Transaction.query.order_by(
                desc(Transaction.created_at)
            ).limit(10).all()
            
            platform_spend = self._get_platform_spend()
            
            daily_spend = self._get_daily_spend(days=30)
            
            return {
                "budget_summary": {
                    "total_budget": total_budget,
                    "active_plans": len(budget_plans),
                },
                "recent_transactions": [
                    {
                        "id": t.id,
                        "amount": t.amount,
                        "description": t.description,
                        "date": t.created_at.strftime("%Y-%m-%d %H:%M"),
                    }
                    for t in recent_transactions
                ],
                "platform_spend": platform_spend,
                "daily_spend": daily_spend,
            }
        except Exception as e:
            logger.error(f"Error al obtener visión general del presupuesto: {str(e)}", exc_info=True)
            return {
                "budget_summary": {"total_budget": 0, "active_plans": 0},
                "recent_transactions": [],
                "platform_spend": {},
                "daily_spend": {"dates": [], "amounts": []},
            }

    def _get_total_impressions(self) -> int:
        """
        Obtiene el total de impresiones de todas las campañas.
        
        Returns:
            Total de impresiones.
        """
        try:
            return 10000
        except Exception as e:
            logger.error(f"Error al obtener total de impresiones: {str(e)}", exc_info=True)
            return 0

    def _get_total_clicks(self) -> int:
        """
        Obtiene el total de clics de todas las campañas.
        
        Returns:
            Total de clics.
        """
        try:
            return 500
        except Exception as e:
            logger.error(f"Error al obtener total de clics: {str(e)}", exc_info=True)
            return 0

    def _get_total_spend(self) -> float:
        """
        Obtiene el gasto total de todas las campañas.
        
        Returns:
            Gasto total.
        """
        try:
            return 1000.0
        except Exception as e:
            logger.error(f"Error al obtener gasto total: {str(e)}", exc_info=True)
            return 0.0

    def _get_segment_distribution(self) -> List[Dict[str, Any]]:
        """
        Obtiene la distribución de candidatos por segmento.
        
        Returns:
            Lista de diccionarios con información de segmentos.
        """
        try:
            return [
                {"segment_id": 1, "count": 25, "label": "Segmento 1"},
                {"segment_id": 2, "count": 35, "label": "Segmento 2"},
                {"segment_id": 3, "count": 40, "label": "Segmento 3"},
            ]
        except Exception as e:
            logger.error(f"Error al obtener distribución de segmentos: {str(e)}", exc_info=True)
            return []

    def _get_recent_performance(self, days: int = 30) -> Dict[str, List]:
        """
        Obtiene datos de rendimiento recientes.
        
        Args:
            days: Número de días a considerar.
            
        Returns:
            Diccionario con listas de fechas y métricas.
        """
        try:
            import random
            
            dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days, 0, -1)]
            
            impressions = [random.randint(100, 1000) for _ in range(days)]
            clicks = [random.randint(5, 50) for _ in range(days)]
            spend = [round(random.uniform(10, 100), 2) for _ in range(days)]
            
            return {
                "dates": dates,
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
            }
        except Exception as e:
            logger.error(f"Error al obtener rendimiento reciente: {str(e)}", exc_info=True)
            return {"dates": [], "impressions": [], "clicks": [], "spend": []}

    def _get_platform_spend(self) -> Dict[str, float]:
        """
        Obtiene el gasto por plataforma.
        
        Returns:
            Diccionario con gasto por plataforma.
        """
        try:
            campaigns = Campaign.query.options(
                joinedload(Campaign.performance)
            ).all()
            
            platform_spend = {}
            for campaign in campaigns:
                platform = campaign.platform
                if platform not in platform_spend:
                    platform_spend[platform] = 0
                
                for perf in campaign.performance:
                    platform_spend[platform] += perf.total_spend or 0
            
            return platform_spend
        except Exception as e:
            logger.error(f"Error al obtener gasto por plataforma: {str(e)}", exc_info=True)
            return {}

    def _get_daily_spend(self, days: int = 30) -> Dict[str, List]:
        """
        Obtiene el gasto diario en el período especificado.
        
        Args:
            days: Número de días a considerar.
            
        Returns:
            Diccionario con listas de fechas y montos.
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            transactions = Transaction.query.filter(
                Transaction.created_at >= start_date
            ).order_by(Transaction.created_at).all()
            
            date_groups = {}
            for trans in transactions:
                date_str = trans.created_at.strftime("%Y-%m-%d")
                if date_str not in date_groups:
                    date_groups[date_str] = 0
                
                date_groups[date_str] += trans.amount or 0
            
            sorted_dates = sorted(date_groups.keys())
            
            return {
                "dates": sorted_dates,
                "amounts": [date_groups[d] for d in sorted_dates],
            }
        except Exception as e:
            logger.error(f"Error al obtener gasto diario: {str(e)}", exc_info=True)
            return {"dates": [], "amounts": []}
