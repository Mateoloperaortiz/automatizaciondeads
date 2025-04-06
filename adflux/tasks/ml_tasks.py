"""
Tareas de machine learning para AdFlux.

Este módulo contiene tareas relacionadas con el entrenamiento de modelos de machine learning,
segmentación de candidatos y otras operaciones de ML.
"""

import time
import traceback
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..extensions import db, scheduler, celery
from ..models import Candidate
from ..ml import (
    load_candidate_data,
    train_segmentation_model,
    predict_candidate_segments,
    load_segmentation_model,
    DEFAULT_N_CLUSTERS,
    update_candidate_segments,
    ensure_segment_records,
    process_candidates_in_batches,
)

# Obtener instancia del logger
log = logging.getLogger(__name__)

BATCH_SIZE = 500


@scheduler.task(
    "cron", id="train_and_predict_segments", hour=2, minute=30
)  # Ejemplo: Ejecutar diariamente a las 2:30 AM
def scheduled_train_and_predict():
    """
    Tarea programada para reentrenar periódicamente el modelo K-means
    y actualizar los segmentos de candidatos en la base de datos.
    Se ejecuta dentro del contexto de la aplicación proporcionado por Flask-APScheduler.
    """
    app = current_app._get_current_object()  # Obtener la instancia real de la aplicación Flask
    app.logger.info("Iniciando tarea programada de segmentación de candidatos...")

    start_time = time.time()

    try:
        # 1. Cargar todos los candidatos de la BD
        app.logger.info("Cargando datos de candidatos desde la base de datos...")
        all_candidates = Candidate.query.all()
        if not all_candidates:
            app.logger.info(
                "No se encontraron candidatos en la base de datos. Omitiendo segmentación."
            )
            return

        candidate_df = load_candidate_data(candidates=all_candidates)
        if candidate_df.empty:
            app.logger.info(
                "El DataFrame de candidatos está vacío después de la carga. Omitiendo segmentación."
            )
            return

        app.logger.info(f"Cargados {len(candidate_df)} candidatos.")

        # 2. Entrenar (o reentrenar) el modelo
        # Usando las rutas predeterminadas definidas en ml_model.py
        app.logger.info("Entrenando/reentrenando modelo de segmentación...")
        model, preprocessor = train_segmentation_model(
            candidate_df,
            n_clusters=app.config.get(
                "ML_N_CLUSTERS", DEFAULT_N_CLUSTERS
            ),  # Permitir sobrescribir mediante configuración
        )
        app.logger.info("Entrenamiento del modelo completo.")

        if not ensure_segment_records(model, logger=app.logger):
            app.logger.error("No se pudieron crear los registros de segmento necesarios.")
            return

        app.logger.info(f"Actualizando segmentos para {len(all_candidates)} candidatos en lotes de {BATCH_SIZE}...")
        update_count, error_count = update_candidate_segments(
            candidates=all_candidates,
            model=model,
            preprocessor=preprocessor,
            logger=app.logger,
            batch_size=BATCH_SIZE
        )
        
        if update_count > 0:
            app.logger.info(f"Segmentos actualizados exitosamente para {update_count} candidatos.")
        else:
            app.logger.info("No fue necesario actualizar ningún segmento de candidato.")
            
        if error_count > 0:
            app.logger.warning(f"Se encontraron errores al procesar segmentos para {error_count} candidatos.")

    except Exception as e:
        # Registrar cualquier otro error inesperado durante la tarea
        db.session.rollback()  # Revertir cualquier cambio parcial potencial
        app.logger.error(f"Error durante la tarea de segmentación programada: {e}")
        app.logger.error(traceback.format_exc())

    finally:
        end_time = time.time()
        app.logger.info(
            f"Tarea programada de segmentación de candidatos finalizada. Duración: {end_time - start_time:.2f} segundos"
        )


def trigger_train_and_predict():
    """Disparar manualmente la tarea de segmentación (ej., vía CLI)."""
    # Esto necesita el contexto de la aplicación para ejecutarse
    app = current_app._get_current_object()
    with app.app_context():
        app.logger.info("Disparando manualmente la tarea de segmentación de candidatos...")
        # Nota: La función scheduled_train_and_predict espera ser ejecutada
        # por el scheduler que proporciona el contexto implícitamente.
        # Llamarla directamente requiere el envoltorio de contexto.
        scheduled_train_and_predict()
        app.logger.info("Disparo manual de la tarea de segmentación finalizado.")

        # Devolver estado de éxito y mensaje
        return True, "Tarea de segmentación disparada exitosamente."


@celery.task(bind=True, name="tasks.run_candidate_segmentation_task")
def run_candidate_segmentation_task(self, candidate_ids=None):
    """
    Tarea Celery para ejecutar la segmentación de candidatos.
    Si se proporcionan IDs de candidatos, solo se segmentarán esos candidatos.
    De lo contrario, se segmentarán todos los candidatos.

    Args:
        candidate_ids: Lista opcional de IDs de candidatos para segmentar.

    Returns:
        dict: Resultados de la segmentación.
    """
    app = current_app._get_current_object()
    logger = app.logger or log
    logger.info(f"[Tarea {self.request.id}] Iniciando tarea de segmentación de candidatos...")

    results = {"success": False, "message": "", "updated_count": 0, "error_count": 0}

    try:
        # 1. Cargar el modelo y preprocesador existentes
        logger.info(f"[Tarea {self.request.id}] Cargando modelo de segmentación existente...")
        model, preprocessor = load_segmentation_model()
        if model is None or preprocessor is None:
            msg = "No se pudo cargar el modelo de segmentación. Ejecute primero el entrenamiento."
            logger.error(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        # 2. Cargar candidatos
        if candidate_ids:
            logger.info(
                f"[Tarea {self.request.id}] Cargando {len(candidate_ids)} candidatos específicos..."
            )
            candidates = Candidate.query.filter(Candidate.candidate_id.in_(candidate_ids)).all()
            if not candidates:
                msg = f"No se encontraron candidatos con los IDs proporcionados: {candidate_ids}"
                logger.warning(f"[Tarea {self.request.id}] {msg}")
                results["message"] = msg
                return results
        else:
            logger.info(f"[Tarea {self.request.id}] Cargando todos los candidatos...")
            candidates = Candidate.query.all()
            if not candidates:
                msg = "No se encontraron candidatos en la base de datos."
                logger.warning(f"[Tarea {self.request.id}] {msg}")
                results["message"] = msg
                return results

        logger.info(f"[Tarea {self.request.id}] Actualizando segmentos para {len(candidates)} candidatos en lotes de {BATCH_SIZE}...")
        update_count, error_count = update_candidate_segments(
            candidates=candidates,
            model=model,
            preprocessor=preprocessor,
            logger=logger,
            batch_size=BATCH_SIZE
        )

        results["success"] = True
        results["message"] = (
            f"Segmentación completada. {update_count} candidatos actualizados, {error_count} errores."
        )
        results["updated_count"] = update_count
        results["error_count"] = error_count

        logger.info(f"[Tarea {self.request.id}] {results['message']}")
        return results

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"[Tarea {self.request.id}] Error inesperado durante la segmentación: {e}",
            exc_info=True,
        )
        results["message"] = f"Error inesperado: {str(e)}"
        return results
