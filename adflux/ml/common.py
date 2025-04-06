"""
Funciones comunes para el módulo de machine learning de AdFlux.

Este módulo proporciona funciones auxiliares compartidas entre diferentes
tareas de machine learning para reducir la duplicación de código.
"""

import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models import Candidate, db
from ..ml import load_candidate_data, predict_candidate_segments
from .batch_processing import process_candidates_in_batches

log = logging.getLogger(__name__)


def update_candidate_segments(
    candidates: List[Candidate],
    model: Any,
    preprocessor: Any,
    logger: Optional[logging.Logger] = None,
    batch_size: int = 500,
) -> Tuple[int, int]:
    """
    Actualiza los segmentos de los candidatos en la base de datos.
    
    Args:
        candidates: Lista de objetos Candidate a actualizar.
        model: Modelo KMeans entrenado.
        preprocessor: Preprocesador ajustado.
        logger: Logger opcional para registrar mensajes.
        batch_size: Tamaño de lote para procesamiento.
        
    Returns:
        Tupla con el conteo de actualizaciones exitosas y errores.
    """
    if logger is None:
        logger = log
        
    if not candidates:
        logger.info("No se encontraron candidatos para actualizar segmentos.")
        return 0, 0
        
    def process_batch(batch: List[Candidate], model: Any, preprocessor: Any) -> Tuple[int, int]:
        """Procesa un lote de candidatos para actualizar sus segmentos."""
        update_count = 0
        error_count = 0
        
        try:
            candidate_df = load_candidate_data(candidates=batch)
            if candidate_df.empty:
                logger.warning("El DataFrame de candidatos está vacío después de la carga.")
                return 0, len(batch)
                
            df_with_segments = predict_candidate_segments(candidate_df, model, preprocessor)
            
            segment_map = df_with_segments["segment"].to_dict()
            
            for candidate in batch:
                try:
                    predicted_segment_float = segment_map.get(candidate.candidate_id)
                    if predicted_segment_float is not None:
                        predicted_segment_int = int(predicted_segment_float)
                        if candidate.segment_id != predicted_segment_int:
                            candidate.segment_id = predicted_segment_int
                            update_count += 1
                except Exception as e:
                    logger.error(f"Error procesando segmento para candidato {candidate.candidate_id}: {e}")
                    error_count += 1
                    
            if update_count > 0:
                db.session.commit()
                logger.info(f"Segmentos actualizados para {update_count} candidatos.")
                
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error de base de datos durante la actualización de segmentos: {e}", exc_info=True)
            error_count += len(batch)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado durante la actualización de segmentos: {e}", exc_info=True)
            error_count += len(batch)
            
        return update_count, error_count
    
    return process_candidates_in_batches(
        candidates=candidates,
        batch_size=batch_size,
        processing_func=process_batch,
        model=model,
        preprocessor=preprocessor
    )


def ensure_segment_records(
    model: Any, 
    logger: Optional[logging.Logger] = None
) -> bool:
    """
    Asegura que existan registros de Segmento para todos los clústeres del modelo.
    
    Args:
        model: Modelo KMeans entrenado.
        logger: Logger opcional para registrar mensajes.
        
    Returns:
        True si la operación fue exitosa, False en caso contrario.
    """
    from ..models import Segment
    
    if logger is None:
        logger = log
        
    try:
        n_clusters_used = model.cluster_centers_.shape[0]
        logger.info(f"Asegurando que existan registros de Segmento para {n_clusters_used} clústeres (IDs 0 a {n_clusters_used - 1})...")
        
        existing_segment_ids = {
            s.id for s in db.session.query(Segment.id)
            .filter(Segment.id.in_(range(n_clusters_used)))
            .all()
        }
        
        segments_to_add = []
        for i in range(n_clusters_used):
            if i not in existing_segment_ids:
                segment_name = f"Segmento {i}"
                segment_description = f"Segmento generado automáticamente para clúster K-means {i}"
                new_segment = Segment(id=i, name=segment_name, description=segment_description)
                segments_to_add.append(new_segment)
                logger.info(f"Creando registro de segmento faltante para ID {i} ('{segment_name}').")
                
        if segments_to_add:
            db.session.add_all(segments_to_add)
            db.session.commit()
            logger.info(f"Se añadieron {len(segments_to_add)} nuevos registros de segmento a la base de datos.")
        else:
            logger.info("Todos los registros de segmento requeridos ya existen.")
            
        return True
        
    except AttributeError as e:
        logger.error(f"No se pudo determinar el número de clústeres desde el objeto del modelo: {e}")
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error de base de datos al asegurar registros de segmento: {e}", exc_info=True)
        return False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado al asegurar registros de segmento: {e}", exc_info=True)
        return False
