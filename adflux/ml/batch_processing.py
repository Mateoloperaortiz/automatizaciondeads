"""
Funciones para procesamiento por lotes de datos de candidatos.

Este módulo proporciona utilidades para procesar grandes conjuntos de datos
de candidatos en lotes, mejorando la eficiencia de memoria.
"""

import pandas as pd
from typing import List, Callable, Iterator, Optional, Tuple, Any
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer

from ..models import Candidate


def process_candidates_in_batches(
    candidates: List[Candidate],
    batch_size: int = 500,
    processing_func: Optional[Callable] = None,
    model: Optional[KMeans] = None,
    preprocessor: Optional[ColumnTransformer] = None,
) -> Tuple[int, int]:
    """
    Procesa candidatos en lotes para mejorar la eficiencia de memoria.

    Args:
        candidates: Lista de objetos Candidate a procesar.
        batch_size: Tamaño de cada lote.
        processing_func: Función opcional para procesar cada lote.
        model: Modelo KMeans opcional para predicción.
        preprocessor: Preprocesador opcional para transformación de datos.

    Returns:
        Tupla con el conteo de actualizaciones exitosas y errores.
    """
    total_updated = 0
    total_errors = 0
    
    batches = list(batch_iterator(candidates, batch_size))
    
    for i, batch in enumerate(batches):
        try:
            if processing_func:
                updated, errors = processing_func(batch, model, preprocessor)
                total_updated += updated
                total_errors += errors
        except Exception as e:
            print(f"Error procesando lote {i+1}/{len(batches)}: {e}")
            total_errors += len(batch)
            
    return total_updated, total_errors


def batch_iterator(items: List[Any], batch_size: int) -> Iterator[List[Any]]:
    """
    Genera lotes de elementos de una lista.

    Args:
        items: Lista de elementos a dividir en lotes.
        batch_size: Tamaño de cada lote.

    Yields:
        Lotes de elementos.
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]
