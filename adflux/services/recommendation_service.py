"""
Servicio para generar recomendaciones de campañas publicitarias.

Este servicio analiza datos históricos de campañas y características de ofertas
de trabajo para recomendar la mejor plataforma y configuración.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import numpy as np
from collections import Counter

from ..models import db, Campaign, JobOpening, MetaInsight, Segment
from ..api.common.logging import get_logger

logger = get_logger("RecommendationService")

class RecommendationService:
    """
    Servicio que proporciona recomendaciones de plataformas y configuraciones
    para campañas publicitarias basadas en datos históricos y características del trabajo.
    """
    
    def __init__(self):
        """Inicializa el servicio de recomendación."""
        self.supported_platforms = ["meta", "google", "tiktok", "snapchat"]
        self.metric_weights = {
            "ctr": 0.45,           # Alto peso para CTR (45%)
            "conversions": 0.45,   # Alto peso para conversiones (45%)
            "cpc": 0.05,           # Bajo peso para CPC (5%)
            "impressions": 0.05    # Bajo peso para impresiones (5%)
        }
        self.exploratory_factor = 0.7  # 70% de peso para exploración
        
    def get_job_recommendations(self, job_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera recomendaciones para una oferta de trabajo específica.
        
        Args:
            job_id: ID de la oferta de trabajo
            
        Returns:
            Tupla con (éxito, mensaje, datos de recomendación)
        """
        try:
            job = JobOpening.query.filter_by(job_id=job_id).first()
            if not job:
                return False, f"No se encontró la oferta de trabajo con ID {job_id}", {}
            
            return self._generate_recommendations(job)
            
        except Exception as e:
            logger.error(f"Error al generar recomendaciones para trabajo {job_id}: {str(e)}", exc_info=True)
            return False, f"Error al generar recomendaciones: {str(e)}", {}
    
    def _generate_recommendations(self, job: JobOpening) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera recomendaciones basadas en las características del trabajo y datos históricos.
        
        Args:
            job: Objeto JobOpening
            
        Returns:
            Tupla con (éxito, mensaje, datos de recomendación)
        """
        similar_jobs = self._find_similar_jobs(job)
        
        platform_performance = self._analyze_platform_performance(similar_jobs)
        
        platform_performance = self._apply_exploratory_approach(platform_performance, job)
        
        if not self._has_sufficient_data(platform_performance):
            recommendations = self._generate_exploratory_recommendations(job)
            return True, "Recomendaciones generadas con enfoque exploratorio basado en características del trabajo", recommendations
        
        best_platform, platform_configs = self._get_best_platform_and_config(platform_performance)
        
        recommended_budget = self._recommend_budget(best_platform, platform_performance)
        
        recommendations = {
            "best_platform": best_platform,
            "platform_ranking": self._rank_platforms(platform_performance),
            "recommended_config": platform_configs.get(best_platform, {}),
            "recommended_budget": recommended_budget,
            "targeting_suggestions": self._generate_targeting_suggestions(job),
            "confidence_score": platform_performance.get(best_platform, {}).get("confidence", 70),
            "based_on_historical": len(similar_jobs) > 0,
            "similar_job_count": len(similar_jobs)
        }
        
        return True, "Recomendaciones generadas con éxito", recommendations
    
    def _has_sufficient_data(self, platform_performance: Dict[str, Dict[str, Any]]) -> bool:
        """
        Determina si hay suficientes datos para generar recomendaciones basadas en rendimiento.
        Con enfoque exploratorio, se requieren menos datos.
        
        Args:
            platform_performance: Diccionario con rendimiento por plataforma
            
        Returns:
            True si hay suficientes datos, False en caso contrario
        """
        platforms_with_data = sum(1 for p in platform_performance.values() if p.get("campaign_count", 0) > 0)
        
        return platforms_with_data >= 1
    
    def _find_similar_jobs(self, job: JobOpening) -> List[JobOpening]:
        """
        Encuentra trabajos similares basados en título, skills y segmentos objetivo.
        
        Args:
            job: Objeto JobOpening
            
        Returns:
            Lista de JobOpening similares
        """
        jobs_with_campaigns = (
            JobOpening.query
            .join(Campaign, JobOpening.job_id == Campaign.job_opening_id)
            .filter(JobOpening.job_id != job.job_id)
            .distinct()
            .all()
        )
        
        if not jobs_with_campaigns:
            return []
        
        similarities = []
        for other_job in jobs_with_campaigns:
            similarity_score = 0
            
            if job.title and other_job.title:
                title_words = set(job.title.lower().split())
                other_title_words = set(other_job.title.lower().split())
                common_words = title_words.intersection(other_title_words)
                if common_words:
                    similarity_score += len(common_words) / max(len(title_words), len(other_title_words)) * 0.4
            
            if job.required_skills and other_job.required_skills:
                job_skills = set(skill.lower() for skill in job.required_skills)
                other_skills = set(skill.lower() for skill in other_job.required_skills)
                if job_skills and other_skills:
                    common_skills = job_skills.intersection(other_skills)
                    if common_skills:
                        similarity_score += len(common_skills) / max(len(job_skills), len(other_skills)) * 0.4
            
            if job.target_segments and other_job.target_segments:
                common_segments = set(job.target_segments).intersection(set(other_job.target_segments))
                if common_segments:
                    similarity_score += len(common_segments) / max(len(job.target_segments), len(other_job.target_segments)) * 0.2
            
            if job.location and other_job.location and job.location.lower() == other_job.location.lower():
                similarity_score += 0.1
                
            if job.employment_type and other_job.employment_type and job.employment_type.lower() == other_job.employment_type.lower():
                similarity_score += 0.1
            
            if similarity_score > 0.2:  # Umbral más bajo (antes 0.3)
                similarities.append((other_job, similarity_score))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        most_similar = similarities[:min(8, len(similarities))]  # Tomamos más trabajos similares (antes 5)
        
        return [job for job, _ in most_similar]
    
    def _analyze_platform_performance(self, similar_jobs: List[JobOpening]) -> Dict[str, Dict[str, Any]]:
        """
        Analiza el rendimiento de campañas asociadas a trabajos similares.
        
        Args:
            similar_jobs: Lista de trabajos similares
            
        Returns:
            Diccionario con rendimiento por plataforma
        """
        if not similar_jobs:
            return {}
        
        job_ids = [job.job_id for job in similar_jobs]
        
        campaigns = (
            Campaign.query
            .filter(Campaign.job_opening_id.in_(job_ids))
            .all()
        )
        
        if not campaigns:
            return {}
        
        platform_performance = {}
        
        cutoff_date = datetime.now() - timedelta(days=120)
        
        for campaign in campaigns:
            platform = campaign.platform
            if platform not in platform_performance:
                platform_performance[platform] = {
                    "campaign_count": 0,
                    "total_spend": 0,
                    "total_clicks": 0,
                    "total_impressions": 0,
                    "total_conversions": 0,
                    "total_ctr": 0,
                    "total_cpc": 0,
                    "conversion_rate": 0,
                    "avg_daily_budget": 0,
                    "config_options": {},
                    "confidence": 0
                }
            
            platform_performance[platform]["campaign_count"] += 1
            
            if campaign.daily_budget:
                platform_performance[platform]["avg_daily_budget"] += campaign.daily_budget
            
            if campaign.target_segment_ids:
                segment_key = "target_segment_ids"
                if segment_key not in platform_performance[platform]["config_options"]:
                    platform_performance[platform]["config_options"][segment_key] = []
                platform_performance[platform]["config_options"][segment_key].extend(campaign.target_segment_ids)
            
            if platform == "meta" and hasattr(campaign, 'meta_objective'):
                objective_key = "objective"
                if objective_key not in platform_performance[platform]["config_options"]:
                    platform_performance[platform]["config_options"][objective_key] = []
                platform_performance[platform]["config_options"][objective_key].append(campaign.meta_objective)
            
            if campaign.external_campaign_id:
                insights = MetaInsight.query.filter(
                    MetaInsight.meta_campaign_id == campaign.external_campaign_id,
                    MetaInsight.date_start >= cutoff_date
                ).all()
                
                for insight in insights:
                    if insight.spend:
                        platform_performance[platform]["total_spend"] += insight.spend
                    if insight.impressions:
                        platform_performance[platform]["total_impressions"] += insight.impressions
                    if insight.clicks:
                        platform_performance[platform]["total_clicks"] += insight.clicks
                    
                    conversions = 0
                    if hasattr(insight, 'leads') and insight.leads:
                        conversions += insight.leads
                    if hasattr(insight, 'complete_registration') and insight.complete_registration:
                        conversions += insight.complete_registration
                    if hasattr(insight, 'submit_application') and insight.submit_application:
                        conversions += insight.submit_application
                    
                    platform_performance[platform]["total_conversions"] += conversions
        
        for platform, data in platform_performance.items():
            if data["campaign_count"] > 0:
                data["avg_daily_budget"] = data["avg_daily_budget"] / data["campaign_count"]
            
            if data["total_impressions"] > 0:
                data["total_ctr"] = (data["total_clicks"] / data["total_impressions"]) * 100
            if data["total_clicks"] > 0:
                data["total_cpc"] = data["total_spend"] / data["total_clicks"]
                
            if data["total_clicks"] > 0:
                data["conversion_rate"] = (data["total_conversions"] / data["total_clicks"]) * 100
            
            for option, values in data["config_options"].items():
                if values:
                    value_counts = Counter(values)
                    data["config_options"][option] = [value for value, _ in value_counts.most_common(3)]
            
            data["confidence"] = min(100, 60 + (data["campaign_count"] * 8))
        
        return platform_performance
    
    def _apply_exploratory_approach(self, platform_performance: Dict[str, Dict[str, Any]], job: JobOpening) -> Dict[str, Dict[str, Any]]:
        """
        Aplica un enfoque exploratorio para sugerir plataformas incluso con datos limitados.
        
        Args:
            platform_performance: Rendimiento basado en datos históricos
            job: Trabajo para el que se generan recomendaciones
            
        Returns:
            Rendimiento ajustado con enfoque exploratorio
        """
        for platform in self.supported_platforms:
            if platform not in platform_performance:
                platform_performance[platform] = {
                    "campaign_count": 0,
                    "total_spend": 0,
                    "total_clicks": 0,
                    "total_impressions": 0,
                    "total_conversions": 0,
                    "total_ctr": 0,
                    "total_cpc": 0,
                    "conversion_rate": 0,
                    "avg_daily_budget": 1500,  # Valor predeterminado $15.00
                    "config_options": {},
                    "exploratory_score": 0,
                    "confidence": 50  # Confianza media para plataformas sin datos
                }
        
        for platform, data in platform_performance.items():
            exploratory_score = 0
            
            job_title_lower = job.title.lower() if job.title else ""
            
            tech_keywords = ["programador", "desarrollador", "software", "ingeniero", "sistemas", "data", "tech"]
            if platform == "google" and any(keyword in job_title_lower for keyword in tech_keywords):
                exploratory_score += 30
            
            creative_keywords = ["diseñador", "creativo", "marketing", "comunicación", "social media", "contenido"]
            if platform == "meta" and any(keyword in job_title_lower for keyword in creative_keywords):
                exploratory_score += 25
            if platform == "tiktok" and any(keyword in job_title_lower for keyword in creative_keywords):
                exploratory_score += 35
                
            junior_keywords = ["junior", "asistente", "practicante", "estudiante", "becario"]
            if platform in ["tiktok", "snapchat"] and any(keyword in job_title_lower for keyword in junior_keywords):
                exploratory_score += 30
                
            executive_keywords = ["gerente", "director", "jefe", "supervisor", "líder", "senior", "manager"]
            if platform == "meta" and any(keyword in job_title_lower for keyword in executive_keywords):
                exploratory_score += 25
                
            total_campaigns = sum(p["campaign_count"] for p in platform_performance.values())
            if total_campaigns > 0:
                platform_usage = data["campaign_count"] / total_campaigns
                exploratory_score += int(30 * (1 - platform_usage))
            
            data["exploratory_score"] = exploratory_score
            
        return platform_performance
    
    def _get_best_platform_and_config(self, platform_performance: Dict[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Dict[str, Any]]]:
        """
        Identifica la mejor plataforma y configuración óptima.
        
        Args:
            platform_performance: Diccionario con rendimiento por plataforma
            
        Returns:
            Tupla con (mejor plataforma, configuraciones por plataforma)
        """
        if not platform_performance:
            return "meta", {}  # Plataforma predeterminada si no hay datos
        
        platform_scores = {}
        platform_configs = {}
        
        for platform, data in platform_performance.items():
            performance_score = 0
            
            ctr_score = data["total_ctr"] * self.metric_weights["ctr"] * 5
            
            conversion_score = data["conversion_rate"] * self.metric_weights["conversions"] * 5
            
            cpc_score = 0
            if data["total_cpc"] > 0:
                cpc_score = (1 / data["total_cpc"]) * self.metric_weights["cpc"] * 10
            
            impression_score = min(100, data["total_impressions"] / 1000) * self.metric_weights["impressions"] * 0.1
            
            performance_score = ctr_score + conversion_score + cpc_score + impression_score
            
            campaign_factor = min(1, data["campaign_count"] / 5)  # Saturar en 5 campañas
            
            if "exploratory_score" in data:
                normalized_exploratory = data["exploratory_score"] * 2
                
                final_score = (performance_score * campaign_factor * (1 - self.exploratory_factor)) + \
                              (normalized_exploratory * self.exploratory_factor)
            else:
                final_score = performance_score * campaign_factor
            
            platform_scores[platform] = final_score
            
            platform_configs[platform] = {
                "daily_budget": data["avg_daily_budget"],
                "target_segment_ids": data["config_options"].get("target_segment_ids", []),
            }
            
            if platform == "meta":
                platform_configs[platform]["objective"] = data["config_options"].get("objective", ["LEAD_GENERATION"])[0]
        
        if platform_scores:
            best_platform = max(platform_scores.items(), key=lambda x: x[1])[0]
        else:
            best_platform = "meta"  # Plataforma predeterminada
        
        return best_platform, platform_configs
    
    def _recommend_budget(self, platform: str, platform_performance: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera recomendación de presupuesto.
        
        Args:
            platform: Plataforma seleccionada
            platform_performance: Datos de rendimiento por plataforma
            
        Returns:
            Diccionario con recomendación de presupuesto
        """
        budget_recommendation = {
            "daily_min": 500,  # $5.00
            "daily_recommended": 1500,  # $15.00
            "daily_max": 5000,  # $50.00
            "is_based_on_data": False
        }
        
        if platform in platform_performance and platform_performance[platform]["avg_daily_budget"] > 0:
            avg_budget = platform_performance[platform]["avg_daily_budget"]
            budget_recommendation["daily_min"] = max(500, int(avg_budget * 0.7))
            budget_recommendation["daily_recommended"] = max(1000, int(avg_budget))
            budget_recommendation["daily_max"] = max(5000, int(avg_budget * 1.5))
            budget_recommendation["is_based_on_data"] = True
        
        return budget_recommendation
    
    def _rank_platforms(self, platform_performance: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Genera un ranking de plataformas basado en rendimiento.
        
        Args:
            platform_performance: Datos de rendimiento por plataforma
            
        Returns:
            Lista de plataformas ordenadas por puntuación
        """
        platform_ranking = []
        
        for platform in self.supported_platforms:
            if platform in platform_performance:
                data = platform_performance[platform]
                
                ctr_score = data["total_ctr"] * self.metric_weights["ctr"] * 5
                
                conversion_score = data["conversion_rate"] * self.metric_weights["conversions"] * 5
                
                cpc_score = 0
                if data["total_cpc"] > 0:
                    cpc_score = (1 / data["total_cpc"]) * self.metric_weights["cpc"] * 10
                
                impression_score = min(100, data["total_impressions"] / 1000) * self.metric_weights["impressions"] * 0.1
                
                performance_score = ctr_score + conversion_score + cpc_score + impression_score
                campaign_factor = min(1, data["campaign_count"] / 5)
                
                if "exploratory_score" in data:
                    normalized_exploratory = data["exploratory_score"] * 2
                    total_score = (performance_score * campaign_factor * (1 - self.exploratory_factor)) + \
                                  (normalized_exploratory * self.exploratory_factor)
                else:
                    total_score = performance_score * campaign_factor
                
                platform_ranking.append({
                    "platform": platform,
                    "score": total_score,
                    "ctr": data["total_ctr"],
                    "conversion_rate": data["conversion_rate"],
                    "cpc": data["total_cpc"],
                    "campaign_count": data["campaign_count"],
                    "confidence": data["confidence"],
                    "exploratory_score": data.get("exploratory_score", 0)
                })
            else:
                platform_ranking.append({
                    "platform": platform,
                    "score": 0,
                    "ctr": 0,
                    "conversion_rate": 0,
                    "cpc": 0,
                    "campaign_count": 0,
                    "confidence": 50,  # Confianza media para plataformas sin datos
                    "exploratory_score": 0
                })
        
        platform_ranking.sort(key=lambda x: x["score"], reverse=True)
        
        return platform_ranking
    
    def _generate_exploratory_recommendations(self, job: JobOpening) -> Dict[str, Any]:
        """
        Genera recomendaciones con enfoque exploratorio cuando no hay datos históricos suficientes.
        
        Args:
            job: Objeto JobOpening
            
        Returns:
            Diccionario con recomendaciones
        """
        mock_performance = {}
        for platform in self.supported_platforms:
            mock_performance[platform] = {
                "campaign_count": 0,
                "total_spend": 0,
                "total_clicks": 0,
                "total_impressions": 0,
                "total_conversions": 0,
                "total_ctr": 0,
                "total_cpc": 0,
                "conversion_rate": 0,
                "avg_daily_budget": 1500,  # $15.00 por defecto
                "config_options": {},
                "exploratory_score": 0,
                "confidence": 50  # Confianza media
            }
        
        platform_performance = self._apply_exploratory_approach(mock_performance, job)
        
        best_platform, platform_configs = self._get_best_platform_and_config(platform_performance)
        
        segments = Segment.query.all()
        segment_ids = [segment.id for segment in segments]
        
        for platform in self.supported_platforms:
            if "target_segment_ids" not in platform_configs[platform]:
                platform_configs[platform]["target_segment_ids"] = segment_ids[:2] if segment_ids else []
        
        if "objective" not in platform_configs.get("meta", {}):
            platform_configs["meta"]["objective"] = "LEAD_GENERATION"
        
        platform_ranking = self._rank_platforms(platform_performance)
        
        return {
            "best_platform": best_platform,
            "platform_ranking": platform_ranking,
            "recommended_config": platform_configs.get(best_platform, {}),
            "recommended_budget": {
                "daily_min": 500,  # $5.00
                "daily_recommended": 1500,  # $15.00
                "daily_max": 5000,  # $50.00
                "is_based_on_data": False
            },
            "targeting_suggestions": self._generate_targeting_suggestions(job),
            "confidence_score": 70,  # Confianza media-alta para enfoque exploratorio
            "based_on_historical": False,
            "similar_job_count": 0
        }
    
    def _generate_targeting_suggestions(self, job: JobOpening) -> Dict[str, Any]:
        """
        Genera sugerencias de targeting basadas en características del trabajo.
        
        Args:
            job: Objeto JobOpening
            
        Returns:
            Diccionario con sugerencias de targeting
        """
        targeting = {
            "locations": [],
            "interests": [],
            "demographics": {},
            "education_levels": [],
            "job_titles": []
        }
        
        if job.location:
            targeting["locations"].append(job.location)
        
        if job.required_skills:
            targeting["interests"] = job.required_skills[:5]  # Primeras 5 habilidades como intereses
        
        if job.education_level:
            targeting["education_levels"].append(job.education_level)
        elif "senior" in job.title.lower() if job.title else False:
            targeting["education_levels"].append("Bachelor's Degree")
        
        if job.title:
            job_title_words = job.title.lower().split()
            if "desarrollador" in job_title_words or "programador" in job_title_words:
                targeting["job_titles"] = ["Desarrollador", "Programador", "Ingeniero de Software"]
            elif "diseñador" in job_title_words:
                targeting["job_titles"] = ["Diseñador", "Diseñador Gráfico", "UX Designer"]
            elif "ventas" in job_title_words:
                targeting["job_titles"] = ["Ventas", "Ejecutivo de Ventas", "Account Manager"]
        
        if job.employment_type == "full-time" or job.employment_type == "part-time":
            targeting["demographics"] = {
                "age_min": 22,
                "age_max": 55
            }
        elif job.employment_type == "internship":
            targeting["demographics"] = {
                "age_min": 18,
                "age_max": 30
            }
        else:
            targeting["demographics"] = {
                "age_min": 22,
                "age_max": 65
            }
        
        return targeting
