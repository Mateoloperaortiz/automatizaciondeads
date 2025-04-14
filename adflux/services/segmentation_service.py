"""
Servicio para la lógica de negocio relacionada con la segmentación.
"""

from flask import current_app, url_for
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd

from ..models import db, Candidate, Segment, Campaign
from ..tasks import run_candidate_segmentation_task
from ..ml import analyze_segments_from_db
from ..ml.segmentation import SegmentationContext, KMeansSegmentation, HierarchicalSegmentation
from ..constants import SEGMENT_MAP, DEFAULT_SEGMENT_NAME
from .interfaces import ISegmentationService


class SegmentationService(ISegmentationService):
    """Contiene la lógica de negocio para la segmentación de candidatos."""

    def get_segmentation_analysis_data(self) -> Dict[str, Any]:
        """Recopila y procesa los datos para la página de análisis de segmentación."""
        analysis_data = {
            "chart_data": None,
            "segment_summary": [],
            "summary_stats": {},
            "error": None,
        }

        try:
            # 1. Obtener todos los segmentos definidos
            all_segments = Segment.query.order_by(Segment.id).all()
            analysis_data["summary_stats"]["total_segments"] = len(all_segments)

            # 2. Obtener análisis de ML (si existe)
            ml_analysis_results = analyze_segments_from_db()
            if "error" in ml_analysis_results:
                 # Registrar error de ML pero continuar si es posible
                 current_app.logger.warning(f"Error en análisis ML: {ml_analysis_results['error']}")
                 ml_segments_data = {}
                 # Podríamos añadir este error a una lista de errores en analysis_data si fuera necesario
            else:
                 ml_segments_data = ml_analysis_results.get("segments", {})

            # Inicializar estadísticas agregadas
            total_analyzed_candidates = ml_analysis_results.get("total_candidates", 0)
            total_segmented_candidates = sum(
                seg_data.get("size", 0) for seg_data in ml_segments_data.values()
            )
            active_segments_count = len(ml_segments_data)

            analysis_data["summary_stats"]["total_candidates"] = total_analyzed_candidates
            analysis_data["summary_stats"]["segmented_candidates"] = total_segmented_candidates
            analysis_data["summary_stats"]["active_segments"] = active_segments_count

            # 3. Procesar cada segmento definido
            chart_labels = []
            chart_data_values = []
            segment_summary_list = []

            all_segment_ids = [s.id for s in all_segments]
            # Obtener todas las campañas relevantes de una vez
            campaigns = Campaign.query.filter(Campaign.target_segment_ids.isnot(None)).all()
            campaigns_by_segment = {seg_id: [] for seg_id in all_segment_ids}
            for camp in campaigns:
                if camp.target_segment_ids: # Asegurar que no sea None
                    for target_seg_id in camp.target_segment_ids:
                        if target_seg_id in campaigns_by_segment:
                             campaigns_by_segment[target_seg_id].append({
                                "id": camp.id,
                                "name": camp.name,
                                "platform": camp.platform,
                                "status": camp.status,
                                "url": url_for("campaign.view_campaign_details", campaign_id=camp.id),
                            })


            for segment_obj in all_segments:
                segment_id = segment_obj.id
                segment_name = segment_obj.name
                segment_description = segment_obj.description or ""

                ml_segment_data = ml_segments_data.get(str(segment_id), {})
                segment_size = ml_segment_data.get("size", 0)

                # Si el análisis ML no proporcionó tamaño, intentar contarlo
                if not ml_segment_data:
                     try:
                          segment_size = Candidate.query.filter_by(segment_id=segment_id).count()
                     except SQLAlchemyError as e:
                          current_app.logger.error(f"Error al contar candidatos para segmento {segment_id}: {e}")
                          segment_size = 0 # O manejar de otra forma

                chart_labels.append(segment_name)
                chart_data_values.append(segment_size)

                associated_campaigns = campaigns_by_segment.get(segment_id, [])

                segment_summary_list.append({
                    "id": int(segment_id),
                    "name": segment_name,
                    "description": segment_description,
                    "count": segment_size,
                    "view_url": url_for("candidate.list_candidates", segment=segment_id),
                    "edit_url": url_for("segmentation.edit_segment", segment_id=segment_id),
                    "avg_experience": ml_segment_data.get("avg_experience"),
                    "top_skills": ml_segment_data.get("top_primary_skills", []),
                    "top_locations": ml_segment_data.get("locations", []),
                    "education_distribution": ml_segment_data.get("education_levels", []),
                    "associated_campaigns": associated_campaigns,
                    "total_campaign_count": len(associated_campaigns),
                    "charts": {
                        "skills": ml_segment_data.get("primary_skills_chart"),
                        "experience": ml_segment_data.get("experience_chart"),
                        "education": ml_segment_data.get("education_chart"),
                    },
                    "is_active": bool(ml_segment_data) or segment_size > 0,
                })

            # Ordenar segmentos
            segment_summary_list.sort(key=lambda x: (not x["is_active"], -x["count"]))
            analysis_data["segment_summary"] = segment_summary_list

            # 4. Añadir "Sin segmentar"
            try:
                unsegmented_count = Candidate.query.filter(Candidate.segment_id.is_(None)).count()
                if unsegmented_count > 0:
                    segment_name = "Sin segmentar"
                    chart_labels.append(segment_name)
                    chart_data_values.append(unsegmented_count)
                    analysis_data["summary_stats"]["total_candidates"] += unsegmented_count # Añadir al total
                    # Añadir entrada al resumen si se desea
                    analysis_data["segment_summary"].append({
                            "id": None,
                            "name": segment_name,
                            "description": "Candidatos no asignados a ningún segmento.",
                            "count": unsegmented_count,
                            "view_url": url_for("candidate.list_candidates", segment="none"),
                            "is_active": True, # Considerarlo activo si tiene candidatos
                             # Rellenar otros campos con None o valores vacíos
                            "avg_experience": None,
                            "top_skills": [],
                            "top_locations": [],
                            "education_distribution": {},
                            "associated_campaigns": [],
                            "total_campaign_count": 0,
                            "charts": {},
                            "edit_url": None,
                    })
            except SQLAlchemyError as e:
                 current_app.logger.error(f"Error al contar candidatos sin segmento: {e}")

            if chart_labels:
                 analysis_data["chart_data"] = {"labels": chart_labels, "data": chart_data_values}

        except Exception as e:
            current_app.logger.error(f"Error general en el servicio de análisis de segmentación: {e}", exc_info=True)
            analysis_data["error"] = "Error inesperado al generar el análisis."

        return analysis_data

    def trigger_segmentation_task(self) -> Tuple[bool, str]:
        """Dispara la tarea Celery para ejecutar la segmentación."""
        return self.trigger_segmentation_with_strategy()

    def trigger_segmentation_with_strategy(self, strategy_name: str = 'kmeans') -> Tuple[bool, str]:
        """Dispara la tarea Celery para ejecutar la segmentación con una estrategia específica."""
        try:
            # Verificar si hay suficientes candidatos para segmentar
            candidate_count = Candidate.query.count()
            if candidate_count < 10:
                return False, f"No hay suficientes candidatos para segmentar. Se requieren al menos 10, pero solo hay {candidate_count}."

            # Lanzar tarea asíncrona con la estrategia seleccionada
            task = run_candidate_segmentation_task.delay(strategy_name)

            return True, f"Tarea iniciada con estrategia '{strategy_name}' (ID: {task.id})"
        except Exception as e:
            current_app.logger.error(f"Error al disparar la tarea de segmentación: {e}", exc_info=True)
            return False, "Error al iniciar la tarea."

    def get_segment_by_id(self, segment_id: int) -> Any:
        """Obtiene un segmento por su ID."""
        # get_or_404 lanzará un error si no se encuentra, lo cual es bueno para la ruta
        return Segment.query.get_or_404(segment_id)

    def update_segment(self, segment_id, data):
        """Actualiza el nombre y descripción de un segmento."""
        segment = self.get_segment_by_id(segment_id)
        try:
            segment.name = data.get('name', segment.name)
            segment.description = data.get('description', segment.description)
            db.session.commit()
            return True, f"Segmento '{segment.name}' actualizado."
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error de BD al actualizar segmento {segment_id}: {e}", exc_info=True)
            return False, "Error de base de datos al actualizar."
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error inesperado al actualizar segmento {segment_id}: {e}", exc_info=True)
            return False, "Error inesperado al actualizar."