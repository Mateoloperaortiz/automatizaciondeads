"""
Tareas de machine learning para AdFlux.

Este módulo contiene tareas relacionadas con el entrenamiento de modelos de machine learning,
segmentación de candidatos y otras operaciones de ML.
"""

import time
import traceback
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import logging

from ..extensions import db, scheduler, celery
from ..models import Candidate, Segment
from ..ml import (
    load_candidate_data,
    train_segmentation_model,
    predict_candidate_segments,
    load_segmentation_model,
    DEFAULT_N_CLUSTERS
)

# Obtener instancia del logger
log = logging.getLogger(__name__)


@scheduler.task('cron', id='train_and_predict_segments', hour=2, minute=30)  # Ejemplo: Ejecutar diariamente a las 2:30 AM
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
            app.logger.info("No se encontraron candidatos en la base de datos. Omitiendo segmentación.")
            return

        candidate_df = load_candidate_data(candidates=all_candidates)
        if candidate_df.empty:
            app.logger.info("El DataFrame de candidatos está vacío después de la carga. Omitiendo segmentación.")
            return

        app.logger.info(f"Cargados {len(candidate_df)} candidatos.")

        # 2. Entrenar (o reentrenar) el modelo
        # Usando las rutas predeterminadas definidas en ml_model.py
        app.logger.info("Entrenando/reentrenando modelo de segmentación...")
        model, preprocessor = train_segmentation_model(
            candidate_df,
            n_clusters=app.config.get('ML_N_CLUSTERS', DEFAULT_N_CLUSTERS)  # Permitir sobrescribir mediante configuración
        )
        app.logger.info("Entrenamiento del modelo completo.")

        # --- INICIO: Asegurar que existan registros de Segmento --- #
        try:
            n_clusters_used = model.n_clusters  # Obtener el número de clústeres del modelo entrenado
            app.logger.info(f"Asegurando que existan registros de Segmento para {n_clusters_used} clústeres (IDs 0 a {n_clusters_used - 1})...")

            existing_segment_ids = {s.id for s in db.session.query(Segment.id).filter(Segment.id.in_(range(n_clusters_used))).all()}
            app.logger.debug(f"IDs de segmento existentes encontrados: {existing_segment_ids}")

            segments_to_add = []
            for i in range(n_clusters_used):
                if i not in existing_segment_ids:
                    segment_name = f"Segmento {i}"
                    segment_description = f"Segmento generado automáticamente para clúster K-means {i}"
                    new_segment = Segment(id=i, name=segment_name, description=segment_description)
                    segments_to_add.append(new_segment)
                    app.logger.info(f"Creando registro de segmento faltante para ID {i} ('{segment_name}').")

            if segments_to_add:
                db.session.add_all(segments_to_add)
                db.session.commit()
                app.logger.info(f"Se añadieron {len(segments_to_add)} nuevos registros de segmento a la base de datos.")
            else:
                app.logger.info("Todos los registros de segmento requeridos ya existen.")

        except AttributeError:
            app.logger.error("No se pudo determinar n_clusters desde el objeto del modelo. Omitiendo la creación del registro de segmento.")
            # Considerar fallar la tarea si esto es crítico
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error de base de datos al asegurar registros de segmento: {e}", exc_info=True)
            raise  # Volver a lanzar para marcar la tarea como fallida
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error inesperado al asegurar registros de segmento: {e}", exc_info=True)
            raise  # Volver a lanzar para marcar la tarea como fallida
        # --- FIN: Asegurar que existan registros de Segmento --- #

        # 3. Predecir segmentos para los candidatos cargados
        app.logger.info("Prediciendo segmentos para todos los candidatos...")
        # Hacer una copia para evitar modificar el df usado para entrenamiento si se necesita en otro lugar
        predict_df = candidate_df.copy()
        df_with_segments = predict_candidate_segments(predict_df, model, preprocessor)
        app.logger.info("Predicción de segmentos completa.")

        # 4. Actualizar candidatos en la base de datos
        app.logger.info("Actualizando segmentos de candidatos en la base de datos...")
        update_count = 0
        error_count = 0

        try:
            # Crear mapa usando candidate_id como clave (el índice del DF)
            segment_map = df_with_segments['segment'].to_dict()
            app.logger.debug(f"Mapa de segmentos construido: {len(segment_map)} entradas.")

            # Iterar a través de los objetos Candidate originales
            for candidate in all_candidates:
                try:
                    predicted_segment_float = segment_map.get(candidate.candidate_id)
                    current_segment_id = candidate.segment_id
                    # logger.debug(...) # Mantener logs detallados por ahora si se desea

                    if predicted_segment_float is not None:
                        predicted_segment_int = int(predicted_segment_float)
                        update_needed = (current_segment_id is None or current_segment_id != predicted_segment_int)
                        # logger.debug(...) # Mantener logs detallados por ahora si se desea
                        if update_needed:
                            candidate.segment_id = predicted_segment_int
                            update_count += 1
                    else:
                        app.logger.warning(f"No se encontró predicción de segmento para el candidato {candidate.candidate_id} en el mapa.")

                except Exception as e:
                    app.logger.error(f"Error procesando segmento para el candidato {candidate.candidate_id}: {e}")
                    error_count += 1

            # Confirmar cambios si hubo actualizaciones
            if update_count > 0:
                app.logger.info(f"Intentando confirmar {update_count} actualizaciones de segmento...")
                db.session.commit()
                app.logger.info(f"Segmentos actualizados exitosamente para {update_count} candidatos.")
            else:
                app.logger.info("No fue necesario actualizar ningún segmento de candidato.")  # Esto ahora significa que ningún segmento cambió O no se predijo ninguno

            if error_count > 0:
                app.logger.warning(f"Se encontraron errores al procesar segmentos para {error_count} candidatos.")

        except KeyError as e:
            app.logger.error(f"Error al construir el mapa de segmentos - ¿Falta la columna 'segment'? Índice actual: {df_with_segments.index.name}. Error: {e}")
            db.session.rollback()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error de base de datos durante la actualización masiva de segmentos: {e}", exc_info=True)
            raise  # Volver a lanzar error de BD para marcar la tarea como fallida
        except Exception as e:  # Capturar otros errores inesperados en este bloque
            db.session.rollback()
            app.logger.error(f"Error inesperado durante la actualización de la base de datos de segmentos: {e}", exc_info=True)
            raise

    except Exception as e:
        # Registrar cualquier otro error inesperado durante la tarea
        db.session.rollback()  # Revertir cualquier cambio parcial potencial
        app.logger.error(f"Error durante la tarea de segmentación programada: {e}")
        app.logger.error(traceback.format_exc())

    finally:
        end_time = time.time()
        app.logger.info(f"Tarea programada de segmentación de candidatos finalizada. Duración: {end_time - start_time:.2f} segundos")


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


@celery.task(bind=True, name='tasks.run_candidate_segmentation_task')
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

    results = {
        "success": False,
        "message": "",
        "updated_count": 0,
        "error_count": 0
    }

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
            logger.info(f"[Tarea {self.request.id}] Cargando {len(candidate_ids)} candidatos específicos...")
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

        # 3. Preparar datos
        candidate_df = load_candidate_data(candidates=candidates)
        if candidate_df.empty:
            msg = "El DataFrame de candidatos está vacío después de la carga."
            logger.warning(f"[Tarea {self.request.id}] {msg}")
            results["message"] = msg
            return results

        # 4. Predecir segmentos
        logger.info(f"[Tarea {self.request.id}] Prediciendo segmentos para {len(candidate_df)} candidatos...")
        df_with_segments = predict_candidate_segments(candidate_df, model, preprocessor)

        # 5. Actualizar candidatos en la base de datos
        logger.info(f"[Tarea {self.request.id}] Actualizando segmentos en la base de datos...")
        update_count = 0
        error_count = 0

        try:
            # Crear mapa usando candidate_id como clave
            segment_map = df_with_segments['segment'].to_dict()

            # Iterar a través de los candidatos
            for candidate in candidates:
                try:
                    predicted_segment_float = segment_map.get(candidate.candidate_id)
                    if predicted_segment_float is not None:
                        predicted_segment_int = int(predicted_segment_float)
                        if candidate.segment_id != predicted_segment_int:
                            candidate.segment_id = predicted_segment_int
                            update_count += 1
                except Exception as e:
                    logger.error(f"[Tarea {self.request.id}] Error procesando segmento para candidato {candidate.candidate_id}: {e}")
                    error_count += 1

            # Confirmar cambios
            if update_count > 0:
                db.session.commit()
                logger.info(f"[Tarea {self.request.id}] Segmentos actualizados para {update_count} candidatos.")
            else:
                logger.info(f"[Tarea {self.request.id}] No fue necesario actualizar ningún segmento.")

        except Exception as e:
            db.session.rollback()
            logger.error(f"[Tarea {self.request.id}] Error durante la actualización de segmentos: {e}", exc_info=True)
            results["message"] = f"Error durante la actualización de segmentos: {str(e)}"
            return results

        # 6. Preparar resultados
        results["success"] = True
        results["message"] = f"Segmentación completada. {update_count} candidatos actualizados, {error_count} errores."
        results["updated_count"] = update_count
        results["error_count"] = error_count

        logger.info(f"[Tarea {self.request.id}] {results['message']}")
        return results

    except Exception as e:
        db.session.rollback()
        logger.error(f"[Tarea {self.request.id}] Error inesperado durante la segmentación: {e}", exc_info=True)
        results["message"] = f"Error inesperado: {str(e)}"
        return results
