"""
Funciones de utilidades para el módulo de machine learning de AdFlux.
"""

import os
import joblib
from typing import Tuple, Optional
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer

from .constants import DEFAULT_MODEL_PATH, DEFAULT_PREPROCESSOR_PATH


def load_segmentation_model(
    model_path: str = DEFAULT_MODEL_PATH, preprocessor_path: str = DEFAULT_PREPROCESSOR_PATH
) -> Tuple[Optional[KMeans], Optional[ColumnTransformer]]:
    """
    Carga un modelo K-means y su preprocesador desde archivos.

    Args:
        model_path: Ruta al archivo del modelo K-means.
        preprocessor_path: Ruta al archivo del preprocesador.

    Returns:
        Tupla que contiene el modelo KMeans y el ColumnTransformer, o (None, None) si falla la carga.
    """
    model = None
    preprocessor = None

    # Intentar cargar el modelo
    try:
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"Modelo cargado desde {model_path}")
        else:
            print(f"Archivo de modelo no encontrado en {model_path}")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")

    # Intentar cargar el preprocesador
    try:
        if os.path.exists(preprocessor_path):
            preprocessor = joblib.load(preprocessor_path)
            print(f"Preprocesador cargado desde {preprocessor_path}")
        else:
            print(f"Archivo de preprocesador no encontrado en {preprocessor_path}")
    except Exception as e:
        print(f"Error al cargar el preprocesador: {e}")

    return model, preprocessor
