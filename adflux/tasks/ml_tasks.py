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
    logger = app.logger or log # Use configured logger
    log_prefix = "[APScheduler train_and_predict_segments]"
    logger.info(f"{log_prefix} Iniciando tarea programada...")

    start_time = time.time()

    try:
        logger.info(f"{log_prefix} Paso 1: Cargando datos de candidatos...")
        all_candidates = Candidate.query.all()
        if not all_candidates:
            logger.info(f"{log_prefix} No se encontraron candidatos. Tarea finalizada.")
            return

        num_candidates = len(all_candidates)
        logger.info(f"{log_prefix} Encontrados {num_candidates} candidatos.")
        if num_candidates > 10000: # Example threshold
            logger.warning(f"{log_prefix} Alerta: Cargando un gran número de candidatos ({num_candidates}), considerar optimización de memoria si es necesario.")

        candidate_df = load_candidate_data(candidates=all_candidates)
        if candidate_df.empty:
            logger.info(f"{log_prefix} DataFrame de candidatos vacío después de la carga. Tarea finalizada.")
            return

        logger.info(f"{log_prefix} Paso 2: Entrenando/reentrenando modelo de segmentación...")
        n_clusters = app.config.get("ML_N_CLUSTERS", DEFAULT_N_CLUSTERS)
        model, preprocessor = train_segmentation_model(
            candidate_df,
            n_clusters=n_clusters
        )
        logger.info(f"{log_prefix} Entrenamiento del modelo completo (Clusters: {n_clusters}).")

        logger.info(f"{log_prefix} Paso 3: Asegurando registros de Segmento en BD...")
        if not ensure_segment_records(model, logger=logger):
            logger.error(f"{log_prefix} No se pudieron crear/verificar los registros de Segmento. Abortando actualización.")
            return

        logger.info(f"{log_prefix} Paso 4: Actualizando segmentos para {num_candidates} candidatos (Batch size: {BATCH_SIZE})...")
        update_count, error_count = update_candidate_segments(
            candidates=all_candidates,
            model=model,
            preprocessor=preprocessor,
            logger=logger,
            batch_size=BATCH_SIZE
        )
        
        if update_count > 0:
            logger.info(f"{log_prefix} Segmentos actualizados exitosamente para {update_count} candidatos.")
        elif update_count == 0:
            logger.info(f"{log_prefix} No fue necesario actualizar ningún segmento de candidato.")
            
        if error_count > 0:
            logger.warning(f"{log_prefix} Se encontraron errores al procesar segmentos para {error_count} candidatos.")

    except Exception as e:
        db.session.rollback()  # Revertir cualquier cambio parcial potencial
        err_msg = f"Error INESPERADO durante la tarea de segmentación programada: {e}"
        logger.error(f"{log_prefix} {err_msg}")
        logger.error(traceback.format_exc())
        # Note: APScheduler tasks do not automatically retry on failure.
        # Consider moving to Celery if automatic retries are needed for transient errors.

    finally:
        end_time = time.time()
        logger.info(
            f"{log_prefix} Tarea finalizada. Duración: {end_time - start_time:.2f} segundos"
        )


def trigger_train_and_predict():
    """Disparar manualmente la tarea de segmentación (ej., vía CLI)."""
    # Esto necesita el contexto de la aplicación para ejecutarse
    app = current_app._get_current_object()
    with app.app_context():
        logger = app.logger or log
        logger.info("[Manual Trigger] Disparando tarea scheduled_train_and_predict...")
        # Nota: La función scheduled_train_and_predict espera ser ejecutada
        # por el scheduler que proporciona el contexto implícitamente.
        # Llamarla directamente requiere el envoltorio de contexto.
        scheduled_train_and_predict()
        logger.info("[Manual Trigger] Tarea scheduled_train_and_predict finalizada.")

        # Devolver estado de éxito y mensaje
        return True, "Tarea de segmentación disparada exitosamente."


@celery.task(bind=True, name="tasks.run_candidate_segmentation_task",
             autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
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
    task_id = self.request.id
    log_prefix = f"[Celery {task_id} run_candidate_segmentation]"
    logger.info(f"{log_prefix} Iniciando tarea (Candidatos: {candidate_ids or 'Todos'})...")

    results = {"success": False, "message": "", "updated_count": 0, "error_count": 0}
    candidates = [] # Initialize

    try:
        logger.info(f"{log_prefix} Paso 1: Cargando modelo y preprocesador existentes...")
        model, preprocessor = load_segmentation_model()
        if model is None or preprocessor is None:
            msg = "No se pudo cargar el modelo de segmentación. Ejecute primero el entrenamiento."
            logger.error(f"{log_prefix} {msg}")
            results["message"] = msg
            # Non-retryable setup error
            return results

        logger.info(f"{log_prefix} Paso 2: Cargando candidatos...")
        if candidate_ids:
            logger.debug(f"{log_prefix} Cargando {len(candidate_ids)} candidatos específicos.")
            candidates = Candidate.query.filter(Candidate.candidate_id.in_(candidate_ids)).all()
            if not candidates:
                msg = f"No se encontraron candidatos con los IDs proporcionados: {candidate_ids}"
                logger.warning(f"{log_prefix} {msg}")
                results["message"] = msg
                results["success"] = True # Not an error if IDs don't match
                return results
        else:
            logger.debug(f"{log_prefix} Cargando todos los candidatos.")
            candidates = Candidate.query.all()
            if not candidates:
                msg = "No se encontraron candidatos en la base de datos."
                logger.warning(f"{log_prefix} {msg}")
                results["message"] = msg
                results["success"] = True # Not an error if DB is empty
                return results

        num_candidates = len(candidates)
        logger.info(f"{log_prefix} Encontrados {num_candidates} candidatos para procesar.")
        if not candidate_ids and num_candidates > 10000:
            logger.warning(f"{log_prefix} Alerta: Procesando todos los candidatos ({num_candidates}), podría ser intensivo en recursos.")

        logger.info(f"{log_prefix} Paso 3: Actualizando segmentos para {num_candidates} candidatos (Batch size: {BATCH_SIZE})...")
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

        logger.info(f"{log_prefix} {results['message']}")
        return results

    except Exception as e:
        db.session.rollback()
        # Log and re-raise for Celery retry/failure handling
        err_msg = f"Error INESPERADO durante la segmentación: {e}"
        logger.error(f"{log_prefix} {err_msg}", exc_info=True)
        results["message"] = err_msg
        results["success"] = False
        # Re-raise the exception caught
        raise
