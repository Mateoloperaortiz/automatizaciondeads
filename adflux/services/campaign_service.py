"""
Servicio para la lógica de negocio relacionada con las campañas.
"""

from flask import current_app
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union

from ..models import db, Campaign, JobOpening, Segment, MetaInsight, MetaAdSet
from ..tasks import async_publish_adflux_campaign
from ..constants import CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLORS
from .interfaces import ICampaignService


# Constantes para la subida de archivos (podrían moverse a config o utils)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def _allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_uploaded_image(file_storage):
    """Guarda una imagen subida y devuelve la ruta relativa."""
    if file_storage and _allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        upload_path_relative = current_app.config.get(
            "UPLOAD_FOLDER", "adflux/static/uploads"
        )
        upload_path_absolute = os.path.join(current_app.root_path, "..", upload_path_relative)
        os.makedirs(upload_path_absolute, exist_ok=True)
        file_path = os.path.join(upload_path_absolute, filename)
        try:
            file_storage.save(file_path)
            # Devolver ruta relativa para guardar en BD, ajustada para ser desde la raíz del proyecto
            # Asumiendo que UPLOAD_FOLDER es relativo a la raíz o 'static/uploads' dentro de adflux
            if upload_path_relative.startswith("adflux/"):
                 return os.path.join(upload_path_relative.replace("adflux/", "", 1), filename)
            else: # Si es una ruta absoluta o relativa a la raíz
                 return os.path.join(upload_path_relative, filename)

        except Exception as e:
            current_app.logger.error(f"Error al guardar archivo: {e}", exc_info=True)
            return None
    return None


class CampaignService(ICampaignService):
    """Contiene la lógica de negocio para las campañas."""

    def get_campaigns_paginated(
        self, page, per_page, platform_filter=None, status_filter=None, sort_by="created_at", sort_order="desc"
    ):
        """Obtiene una lista paginada de campañas con filtros y ordenación."""
        query = Campaign.query.options(db.joinedload(Campaign.job_opening))

        # Aplicar filtros
        if platform_filter:
            query = query.filter(Campaign.platform == platform_filter)
        if status_filter:
            query = query.filter(Campaign.status == status_filter)

        # Aplicar ordenación
        sort_column = getattr(Campaign, sort_by, Campaign.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination


    def get_campaign_stats(self):
        """Calcula estadísticas agregadas sobre las campañas."""
        stats = {}
        try:
            platform_counts = (
                db.session.query(Campaign.platform, func.count(Campaign.id))
                .group_by(Campaign.platform)
                .all()
            )
            stats["platform_counts"] = dict(p for p in platform_counts if p[0]) # Filtrar nulos/vacíos

            status_counts = (
                db.session.query(Campaign.status, func.count(Campaign.id))
                .group_by(Campaign.status)
                .all()
            )
            stats["status_counts"] = dict(s for s in status_counts if s[0]) # Filtrar nulos/vacíos

            # Preparar datos para gráficos (filtrando claves nulas/vacías)
            if stats.get("platform_counts"):
                 valid_platforms = {p: c for p, c in stats["platform_counts"].items()}
                 stats["platform_chart"] = {"labels": list(valid_platforms.keys()), "data": list(valid_platforms.values())}

            if stats.get("status_counts"):
                 valid_statuses = {s: c for s, c in stats["status_counts"].items()}
                 stats["status_chart"] = {"labels": list(valid_statuses.keys()), "data": list(valid_statuses.values())}

        except Exception as e:
            current_app.logger.error(f"Error al generar estadísticas de campañas: {e}", exc_info=True)
            stats = {} # Retornar vacío en caso de error
        return stats


    def get_campaign_by_id(self, campaign_id):
        """Obtiene una campaña por su ID."""
        return Campaign.query.get_or_404(campaign_id)


    def get_job_opening_choices(self):
        """Obtiene las opciones (choices) para el campo select de JobOpening."""
        try:
            # Devuelve tuplas (valor, etiqueta) -> (job_id, title)
            return [(jo.job_id, jo.title) for jo in JobOpening.query.order_by(JobOpening.title).all()]
        except Exception as e:
            current_app.logger.error(f"Error al obtener choices de JobOpening: {e}", exc_info=True)
            return [] # Retorna lista vacía en caso de error

    def get_segment_choices(self):
        """Obtiene las opciones (choices) para el campo select de Segment."""
        try:
            # Devuelve tuplas (valor, etiqueta) -> (id, name)
            # Asegurarse que el ID (valor) sea el PK entero
            return [(s.id, s.name) for s in Segment.query.order_by(Segment.name).all()]
        except Exception as e:
            current_app.logger.error(f"Error al obtener choices de Segment: {e}", exc_info=True)
            return [] # Retorna lista vacía en caso de error

    def get_job_opening_by_job_id(self, job_id):
        """Busca un JobOpening por su job_id."""
        try:
            return JobOpening.query.filter_by(job_id=job_id).first()
        except Exception as e:
            current_app.logger.error(f"Error al buscar JobOpening por job_id '{job_id}': {e}", exc_info=True)
            return None

    def get_campaign_details_data(self, campaign_id):
         """Prepara los datos necesarios para la vista de detalles de campaña."""
         campaign = self.get_campaign_by_id(campaign_id)
         job = JobOpening.query.get(campaign.job_opening_id) if campaign.job_opening_id else None
         return campaign, job

    def create_campaign(self, form_data, image_file):
        """Crea una nueva campaña."""
        try:
            saved_filename = None
            if image_file:
                saved_filename = _save_uploaded_image(image_file)
                if not saved_filename:
                    # Devolvemos None y una bandera de error de imagen
                    return None, False, "Image upload failed or file type not allowed."

            daily_budget_cents = (
                int(form_data['daily_budget'] * 100) if form_data.get('daily_budget') else None
            )

            # Asegurarse que target_segment_ids es una lista de IDs (enteros)
            target_segment_ids_raw = form_data.get('target_segment_ids', [])
            target_segment_ids = [int(sid) for sid in target_segment_ids_raw if isinstance(sid, (str, int)) and str(sid).isdigit()]


            new_campaign = Campaign(
                name=form_data['name'],
                description=form_data.get('description'),
                platform=form_data['platform'],
                status=form_data.get('status', 'draft'), # Default a draft
                daily_budget=daily_budget_cents,
                job_opening_id=form_data.get('job_opening'), # Asumimos que el form pasa el ID
                target_segment_ids=target_segment_ids,
                primary_text=form_data.get('primary_text'),
                headline=form_data.get('headline'),
                link_description=form_data.get('link_description'),
                creative_image_filename=saved_filename,
            )
            db.session.add(new_campaign)
            db.session.commit()
            return new_campaign, True, None # Retorna campaña, éxito, sin error

        except Exception as e:
            db.session.rollback()
            # Log con más contexto (quizás evitar loggear toda form_data si contiene info sensible)
            log_context = {"form_name": form_data.get("name"), "platform": form_data.get("platform")}
            current_app.logger.error(f"Error al crear campaña: {e} - Data: {log_context}", exc_info=True)
            return None, False, str(e) # Retorna None, fallo, mensaje de error


    def update_campaign(self, campaign_id, form_data, image_file):
        """Actualiza una campaña existente."""
        campaign = self.get_campaign_by_id(campaign_id)
        try:
            if image_file:
                saved_filename = _save_uploaded_image(image_file)
                if saved_filename:
                    campaign.creative_image_filename = saved_filename
                else:
                    # Devolvemos False y una bandera de error de imagen
                     return campaign, False, "Image upload failed or file type not allowed."

            campaign.name = form_data['name']
            campaign.description = form_data.get('description')
            campaign.platform = form_data['platform']
            campaign.status = form_data.get('status', campaign.status)
            campaign.daily_budget = (
                int(form_data['daily_budget'] * 100) if form_data.get('daily_budget') else None
            )
            campaign.job_opening_id = form_data.get('job_opening') # Asumimos que el form pasa el ID
             # Asegurarse que target_segment_ids es una lista de IDs (enteros)
            target_segment_ids_raw = form_data.get('target_segment_ids', [])
            campaign.target_segment_ids = [int(sid) for sid in target_segment_ids_raw if isinstance(sid, (str, int)) and str(sid).isdigit()]

            campaign.primary_text = form_data.get('primary_text')
            campaign.headline = form_data.get('headline')
            campaign.link_description = form_data.get('link_description')

            db.session.commit()
            return campaign, True, None # Retorna campaña, éxito, sin error

        except Exception as e:
            db.session.rollback()
            # Log con más contexto
            log_context = {"campaign_id": campaign_id, "form_name": form_data.get("name")}
            current_app.logger.error(f"Error al actualizar campaña {campaign_id}: {e} - Data: {log_context}", exc_info=True)
            return campaign, False, str(e) # Retorna campaña, fallo, mensaje de error


    def trigger_publish_campaign(self, campaign_id, simulate=False):
        """Dispara la tarea asíncrona para publicar una campaña."""
        campaign = self.get_campaign_by_id(campaign_id)

        if campaign.status == "published":
            return campaign, False, f"La campaña '{campaign.name}' ya está publicada."

        try:
            task = async_publish_adflux_campaign.delay(campaign.id, simulate)
            campaign.status = "publishing"
            db.session.commit()
            return campaign, True, f"Publicación iniciada. ID de tarea: {task.id}"

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al ENCOLAR publicación para campaña {campaign_id}: {e}", exc_info=True)
            return campaign, False, str(e)


    def delete_campaign(self, campaign_id):
        """Elimina una campaña."""
        campaign = self.get_campaign_by_id(campaign_id)
        try:
            name = campaign.name
            db.session.delete(campaign)
            db.session.commit()
            return True, f"Campaña '{name}' eliminada exitosamente."
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al eliminar campaña {campaign_id} ('{campaign.name if campaign else '???'}'): {e}", exc_info=True)
            return False, str(e)

    def get_campaign_performance_report(self, campaign_id, start_date_dt, end_date_dt):
        """Obtiene y calcula las estadísticas de rendimiento para una campaña."""
        campaign = self.get_campaign_by_id(campaign_id)
        stats = {
            "total_spend": 0.0,
            "total_impressions": 0,
            "total_clicks": 0,
            "ctr": 0.0,
            "cpc": 0.0,
            "spend_over_time_chart": None,
            "ad_set_performance": [],
        }

        if not campaign.external_campaign_id:
             return stats # No hay datos si no se ha publicado

        try:
            insights_base_query = MetaInsight.query.filter(
                MetaInsight.meta_campaign_id == campaign.external_campaign_id,
                MetaInsight.date_start >= start_date_dt,
                MetaInsight.date_stop <= end_date_dt,
            )

            performance_totals = insights_base_query.with_entities(
                func.sum(MetaInsight.spend),
                func.sum(MetaInsight.impressions),
                func.sum(MetaInsight.clicks),
            ).first()

            if performance_totals and performance_totals[0] is not None:
                stats["total_spend"] = float(performance_totals[0] or 0)
                stats["total_impressions"] = int(performance_totals[1] or 0)
                stats["total_clicks"] = int(performance_totals[2] or 0)
                if stats["total_impressions"] > 0:
                    stats["ctr"] = (stats["total_clicks"] / stats["total_impressions"]) * 100
                if stats["total_clicks"] > 0:
                    stats["cpc"] = stats["total_spend"] / stats["total_clicks"]

            daily_spend = (
                insights_base_query.with_entities(
                    MetaInsight.date_start, func.sum(MetaInsight.spend)
                )
                .group_by(MetaInsight.date_start)
                .order_by(MetaInsight.date_start)
                .all()
            )
            if daily_spend:
                 # Filtrar días con gasto None o 0 antes de crear el gráfico
                 valid_daily_spend = [(day[0], float(day[1])) for day in daily_spend if day[1] is not None and float(day[1]) > 0]
                 if valid_daily_spend:
                    stats["spend_over_time_chart"] = {
                        "labels": [day[0].strftime("%Y-%m-%d") for day in valid_daily_spend],
                        "data": [day[1] for day in valid_daily_spend],
                    }


            if campaign.platform == "meta":
                # Fetch AdSet objects first (needed for names)
                ad_sets = db.session.query(MetaAdSet.ad_set_id, MetaAdSet.name).filter(
                    meta_campaign_id=campaign.external_campaign_id
                ).all()

                if ad_sets:
                    ad_set_map = {ad_set.ad_set_id: ad_set.name for ad_set in ad_sets}
                    ad_set_ids = list(ad_set_map.keys())

                    # Single query for performance grouped by ad_set_id
                    ad_set_performance_data = (
                        insights_base_query
                        .filter(MetaInsight.meta_ad_set_id.in_(ad_set_ids))
                        .with_entities(
                            MetaInsight.meta_ad_set_id,
                            func.sum(MetaInsight.spend).label("total_spend"),
                            func.sum(MetaInsight.impressions).label("total_impressions"),
                            func.sum(MetaInsight.clicks).label("total_clicks"),
                        )
                        .group_by(MetaInsight.meta_ad_set_id)
                        .all()
                    )

                    # Process results in Python (mapping ID to performance)
                    perf_dict = {str(row.meta_ad_set_id): row for row in ad_set_performance_data}

                    # Combine AdSet info with performance data
                    for ad_set_id, ad_set_name in ad_set_map.items():
                        perf_row = perf_dict.get(str(ad_set_id))

                        if perf_row and perf_row.total_spend is not None:
                            ad_set_spend = float(perf_row.total_spend or 0)
                            ad_set_impressions = int(perf_row.total_impressions or 0)
                            ad_set_clicks = int(perf_row.total_clicks or 0)

                        ad_set_ctr = (ad_set_clicks / ad_set_impressions) * 100 if ad_set_impressions > 0 else 0
                        ad_set_cpc = ad_set_spend / ad_set_clicks if ad_set_clicks > 0 else 0

                        stats["ad_set_performance"].append({
                                "name": ad_set_name,
                                "id": ad_set_id,
                                "spend": ad_set_spend,
                                "impressions": ad_set_impressions,
                                "clicks": ad_set_clicks,
                                "ctr": ad_set_ctr,
                                "cpc": ad_set_cpc,
                            })
                    else:
                            # Optionally include ad sets with 0 spend/data if needed
                            stats["ad_set_performance"].append({
                                "name": ad_set_name, "id": ad_set_id,
                                "spend": 0.0, "impressions": 0, "clicks": 0, "ctr": 0.0, "cpc": 0.0
                            })

        except Exception as e:
            current_app.logger.error(
                f"Error al generar informe de rendimiento para campaña {campaign_id}: {e}", exc_info=True
            )
            # Considerar si devolver error parcial o completo
            # Por ahora, devolvemos las estadísticas que se pudieron calcular

        return stats