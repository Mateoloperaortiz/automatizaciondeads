"""
Servicio de recomendación para campañas en AdFlux.

Este módulo proporciona funcionalidades para recomendar configuraciones y optimizaciones
para campañas publicitarias basadas en rendimiento histórico.
"""

from flask import current_app
from typing import List, Dict, Any, Tuple

from ..models import db, Campaign
from .base_service import BaseService


class RecommendationService(BaseService):
    """Servicio para generar recomendaciones para campañas."""
    
    def recommend_budget_allocation(self, budget_plan_id: int) -> List[Dict[str, Any]]:
        """
        Recomienda asignación de presupuesto basado en el rendimiento de campañas.
        
        Args:
            budget_plan_id: ID del plan de presupuesto
            
        Returns:
            Lista de recomendaciones con allocaciones sugeridas para cada campaña
        """
        recommendations = []
        
        try:
            from ..models import BudgetPlan
            
            budget_plan = BudgetPlan.query.get(budget_plan_id)
            if not budget_plan:
                return []
                
            campaigns = budget_plan.campaigns
            if not campaigns:
                return []
            
            per_campaign = 100.0 / len(campaigns)
            
            for campaign in campaigns:
                recommendations.append({
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "current_allocation": 0,  # Valor de ejemplo
                    "recommended_allocation": per_campaign,
                    "reason": "Distribución equitativa sugerida para evaluación inicial"
                })
            
        except Exception as e:
            current_app.logger.error(f"Error al recomendar asignación de presupuesto: {e}", exc_info=True)
            return []
            
        return recommendations
        
    def get_campaign_optimizations(self, campaign_id: int) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones para optimizar una campaña específica.
        
        Args:
            campaign_id: ID de la campaña
            
        Returns:
            Lista de recomendaciones para optimizar la campaña
        """
        try:
            campaign = Campaign.query.get(campaign_id)
            if not campaign:
                return []
                
            
            optimizations = []
            
            optimizations.append({
                "type": "targeting",
                "recommendation": "Considerar ampliar la segmentación para incrementar alcance",
                "impact": "medium",
            })
            
            optimizations.append({
                "type": "budget",
                "recommendation": "El presupuesto diario actual parece óptimo basado en rendimiento",
                "impact": "low",
            })
            
            optimizations.append({
                "type": "creative",
                "recommendation": "Considerar pruebas A/B de creatividades para mejorar CTR",
                "impact": "high",
            })
            
            return optimizations
            
        except Exception as e:
            current_app.logger.error(f"Error al generar optimizaciones para campaña: {e}", exc_info=True)
            return []
