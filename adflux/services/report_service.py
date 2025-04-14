"""
Servicio para la lógica de negocio relacionada con los informes.
"""

from flask import current_app
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any

from ..models import db, Campaign, JobOpening, Candidate, MetaInsight
from .interfaces import IReportService


class ReportService(IReportService):
    """Contiene la lógica de negocio para generar informes."""

    def generate_campaign_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Genera los datos para el informe de campañas."""
        report_data = {
            "title": "Informe de Campañas",
            "period": f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            "campaigns": [],
            "summary": {},
            "charts": {},
        }

        try:
            # Consultar campañas (considerar filtrar por fecha si es relevante)
            # campaigns = Campaign.query.options(db.joinedload(Campaign.job_opening)).all()

            # Consultar insights para el período y para campañas existentes
            # Realizar una única consulta agregada que una Campaign e Insights
            aggregated_data_query = db.session.query(
                Campaign.id,
                Campaign.name,
                Campaign.platform,
                Campaign.status,
                Campaign.external_campaign_id,
                Campaign.created_at,
                JobOpening.title.label("job_title"),
                func.sum(db.case((MetaInsight.date_start >= start_date, MetaInsight.impressions), else_=0)).label("total_impressions"),
                func.sum(db.case((MetaInsight.date_start >= start_date, MetaInsight.clicks), else_=0)).label("total_clicks"),
                func.sum(db.case((MetaInsight.date_start >= start_date, MetaInsight.spend), else_=0.0)).label("total_spend"),
            ).select_from(Campaign)\
            .outerjoin(JobOpening, Campaign.job_opening_id == JobOpening.id)\
            .outerjoin(MetaInsight, db.and_(
                Campaign.external_campaign_id == MetaInsight.meta_campaign_id,
                # Ajustar filtro de fecha según la lógica requerida
                MetaInsight.date_start >= start_date,
                MetaInsight.date_stop <= end_date
            ))\
            .group_by(
                Campaign.id,
                Campaign.name,
                Campaign.platform,
                Campaign.status,
                Campaign.external_campaign_id,
                Campaign.created_at,
                JobOpening.title
            )\
            .order_by(Campaign.created_at.desc())

            # Ejecutar la consulta agregada
            aggregated_results = aggregated_data_query.all()

            # Procesar los resultados agregados
            for row in aggregated_results:
                # Calcular métricas
                total_impressions = int(row.total_impressions or 0)
                total_clicks = int(row.total_clicks or 0)
                total_spend = float(row.total_spend or 0.0)

                # Calcular métricas derivadas
                ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                cpc = total_spend / total_clicks if total_clicks > 0 else 0
                cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0

                # Añadir datos de la campaña
                campaign_data = {
                    "id": row.id,
                    "name": row.name,
                    "platform": row.platform,
                    "status": row.status,
                    "job_title": row.job_title,
                    "external_id": row.external_campaign_id,
                    "created_at": row.created_at.strftime("%Y-%m-%d") if row.created_at else "N/A",
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "spend": round(total_spend, 2), # Redondear gasto
                    "ctr": round(ctr, 2),
                    "cpc": round(cpc, 2),
                    "cpm": round(cpm, 2),
                }
                report_data["campaigns"].append(campaign_data)

            # Ordenar campañas por impresiones (descendente)
            report_data["campaigns"].sort(key=lambda x: x["impressions"], reverse=True)

            # Calcular resumen
            total_campaigns = len(report_data["campaigns"])
            total_impressions_summary = sum(c["impressions"] for c in report_data["campaigns"])
            total_clicks_summary = sum(c["clicks"] for c in report_data["campaigns"])
            total_spend_summary = sum(c["spend"] for c in report_data["campaigns"])

            report_data["summary"] = {
                "total_campaigns": total_campaigns,
                "total_impressions": total_impressions_summary,
                "total_clicks": total_clicks_summary,
                "total_spend": round(total_spend_summary, 2),
                "avg_ctr": round(
                    (total_clicks_summary / total_impressions_summary * 100) if total_impressions_summary > 0 else 0, 2
                ),
                "avg_cpc": round(total_spend_summary / total_clicks_summary if total_clicks_summary > 0 else 0, 2),
                "avg_cpm": round(
                    (total_spend_summary / total_impressions_summary * 1000) if total_impressions_summary > 0 else 0, 2
                ),
            }

            # Preparar datos para gráficos
            platform_counts = {}
            for campaign_d in report_data["campaigns"]:
                platform = campaign_d["platform"] or "Desconocida"
                if platform not in platform_counts:
                    platform_counts[platform] = 0
                platform_counts[platform] += 1
            report_data["charts"]["platform"] = {
                "labels": list(platform_counts.keys()),
                "data": list(platform_counts.values()),
            }

            # Gráfico de impresiones por campaña (top 10)
            top_campaigns_imp = sorted(
                report_data["campaigns"], key=lambda x: x["impressions"], reverse=True
            )[:10]
            report_data["charts"]["impressions"] = {
                "labels": [c["name"] for c in top_campaigns_imp],
                "data": [c["impressions"] for c in top_campaigns_imp],
            }

            # Gráfico de clics por campaña (top 10)
            top_campaigns_clicks = sorted(report_data["campaigns"], key=lambda x: x["clicks"], reverse=True)[:10]
            report_data["charts"]["clicks"] = {
                "labels": [c["name"] for c in top_campaigns_clicks],
                "data": [c["clicks"] for c in top_campaigns_clicks],
            }

        except Exception as e:
            current_app.logger.error(f"Error al generar informe de campañas: {e}", exc_info=True)
            report_data["error"] = f"Error al generar informe: {str(e)}"

        return report_data


    def generate_job_report(self, start_date, end_date):
        """Genera los datos para el informe de trabajos."""
        report_data = {
            "title": "Informe de Trabajos",
            "period": f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            "jobs": [],
            "summary": {},
            "charts": {},
        }

        try:
            # Consultar trabajos creados en el rango o activos en el rango?
            # Por ahora, consultamos todos los trabajos.
            jobs = JobOpening.query.order_by(JobOpening.created_at.desc()).all()

            job_ids = [j.job_id for j in jobs]
            if not job_ids:
                return report_data

            # Contar campañas asociadas por job_id
            campaign_counts = dict(db.session.query(
                Campaign.job_opening_id,
                func.count(Campaign.id)
            ).filter(Campaign.job_opening_id.in_(job_ids)).group_by(Campaign.job_opening_id).all())

            # Contar candidatos asociados por job_id (considerar filtrar por fecha de creación del candidato?)
            candidate_counts = dict(db.session.query(
                Candidate.job_id,
                func.count(Candidate.candidate_id)
            ).filter(
                Candidate.job_id.in_(job_ids),
                # Candidate.created_at.between(start_date, end_date) # Opcional: filtrar por fecha candidato
            ).group_by(Candidate.job_id).all())

            # Procesar cada trabajo
            for job in jobs:
                job_data = {
                    "id": job.job_id,
                    "title": job.title,
                    "company": job.company_name,
                    "location": job.location,
                    "status": job.status,
                    "created_at": job.created_at.strftime("%Y-%m-%d") if job.created_at else "N/A",
                    "campaign_count": campaign_counts.get(job.job_id, 0),
                    "candidate_count": candidate_counts.get(job.job_id, 0),
                }
                report_data["jobs"].append(job_data)

            # Ordenar trabajos por número de candidatos (descendente)
            report_data["jobs"].sort(key=lambda x: x["candidate_count"], reverse=True)

            # Calcular resumen
            total_jobs = len(report_data["jobs"])
            total_campaigns = sum(j["campaign_count"] for j in report_data["jobs"])
            total_candidates = sum(j["candidate_count"] for j in report_data["jobs"])

            report_data["summary"] = {
                "total_jobs": total_jobs,
                "total_campaigns": total_campaigns,
                "total_candidates": total_candidates,
                "avg_campaigns_per_job": round(
                    total_campaigns / total_jobs if total_jobs > 0 else 0, 2
                ),
                "avg_candidates_per_job": round(
                    total_candidates / total_jobs if total_jobs > 0 else 0, 2
                ),
            }

            # Preparar datos para gráficos
            status_counts = {}
            for job_d in report_data["jobs"]:
                status = job_d["status"] or "Desconocido"
                if status not in status_counts:
                    status_counts[status] = 0
                status_counts[status] += 1
            report_data["charts"]["status"] = {
                "labels": list(status_counts.keys()),
                "data": list(status_counts.values()),
            }

            # Gráfico de candidatos por trabajo (top 10)
            top_jobs = sorted(report_data["jobs"], key=lambda x: x["candidate_count"], reverse=True)[:10]
            report_data["charts"]["candidates"] = {
                "labels": [j["title"] for j in top_jobs],
                "data": [j["candidate_count"] for j in top_jobs],
            }

        except Exception as e:
            current_app.logger.error(f"Error al generar informe de trabajos: {e}", exc_info=True)
            report_data["error"] = f"Error al generar informe: {str(e)}"

        return report_data


    def generate_candidate_report(self, start_date, end_date):
        """Genera los datos para el informe de candidatos."""
        report_data = {
            "title": "Informe de Candidatos",
            "period": f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            "candidates": [],
            "summary": {},
            "charts": {},
        }

        try:
            # Consultar candidatos creados en el rango
            candidates_query = Candidate.query.options(db.joinedload(Candidate.job)).filter(
                # Candidate.created_at.between(start_date, end_date) # Opcional: filtrar por fecha candidato
            ).order_by(Candidate.created_at.desc())

            candidates = candidates_query.all()

            # Procesar cada candidato
            for candidate in candidates:
                candidate_data = {
                    "id": candidate.candidate_id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "location": candidate.location,
                    "years_experience": candidate.years_experience,
                    "education_level": candidate.education_level,
                    "primary_skill": candidate.primary_skill,
                    "job_title": candidate.job.title if candidate.job else "N/A",
                    "segment_id": candidate.segment_id,
                    "created_at": candidate.created_at.strftime("%Y-%m-%d") if candidate.created_at else "N/A",
                }
                report_data["candidates"].append(candidate_data)

            # Ordenar candidatos por años de experiencia (descendente)
            report_data["candidates"].sort(
                key=lambda x: x["years_experience"] if x["years_experience"] is not None else -1, # Tratar None como menor
                reverse=True,
            )

            # Calcular resumen
            total_candidates = len(report_data["candidates"])
            candidates_with_exp = [c["years_experience"] for c in report_data["candidates"] if c["years_experience"] is not None]
            avg_experience = (
                sum(candidates_with_exp) / len(candidates_with_exp)
                if candidates_with_exp
                else 0
            )

            report_data["summary"] = {
                "total_candidates": total_candidates,
                "avg_experience": round(avg_experience, 2),
            }

            # Preparar datos para gráficos
            education_counts = {}
            for candidate_d in report_data["candidates"]:
                education = candidate_d["education_level"] or "Desconocido"
                if education not in education_counts:
                    education_counts[education] = 0
                education_counts[education] += 1
            report_data["charts"]["education"] = {
                "labels": list(education_counts.keys()),
                "data": list(education_counts.values()),
            }

            # Gráfico de segmentos
            segment_counts = {}
            for candidate_d in report_data["candidates"]:
                segment = (
                    f"Segmento {candidate_d['segment_id']}"
                    if candidate_d["segment_id"] is not None
                    else "Sin segmentar"
                )
                if segment not in segment_counts:
                    segment_counts[segment] = 0
                segment_counts[segment] += 1
            report_data["charts"]["segments"] = {
                "labels": list(segment_counts.keys()),
                "data": list(segment_counts.values()),
            }

            # Gráfico de habilidades primarias (top 10)
            skill_counts = {}
            for candidate_d in report_data["candidates"]:
                skill = candidate_d["primary_skill"]
                if skill and skill not in skill_counts:
                    skill_counts[skill] = 0
                if skill:
                    skill_counts[skill] += 1
            top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            report_data["charts"]["skills"] = {
                "labels": [s[0] for s in top_skills],
                "data": [s[1] for s in top_skills],
            }

        except Exception as e:
            current_app.logger.error(f"Error al generar informe de candidatos: {e}", exc_info=True)
            report_data["error"] = f"Error al generar informe: {str(e)}"

        return report_data