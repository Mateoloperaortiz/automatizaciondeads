"""
Funciones de predicción para el módulo de machine learning de AdFlux.
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from typing import Optional

from .utils import load_segmentation_model


def predict_candidate_segments(
    df: pd.DataFrame,
    model: Optional[KMeans] = None,
    preprocessor: Optional[ColumnTransformer] = None,
) -> pd.DataFrame:
    """
    Predice segmentos para candidatos usando un modelo K-means entrenado.

    Args:
        df: DataFrame con datos de candidatos.
        model: Modelo K-means entrenado. Si es None, intenta cargar desde la ruta predeterminada.
        preprocessor: Preprocesador ajustado. Si es None, intenta cargar desde la ruta predeterminada.

    Returns:
        DataFrame con una columna 'segment' añadida que contiene el segmento predicho para cada candidato.
    """
    if df.empty:
        print("Error: El DataFrame de entrada está vacío. No se pueden predecir segmentos.")
        return df

    if model is None or preprocessor is None:
        print(
            "Modelo o preprocesador no proporcionado, intentando cargar desde rutas predeterminadas..."
        )
        model, preprocessor = load_segmentation_model()

    if model is None or preprocessor is None:
        print(
            "Error: No se pudo cargar el modelo o el preprocesador. No se pueden predecir segmentos."
        )
        # O lanzar un error
        df["segment"] = -1  # Indicar fallo
        return df

    # Asegurar que 'skills_text' exista si no está presente (podría ocurrir si se predice sobre datos nuevos)
    if "skills_text" not in df.columns and "skills" in df.columns:
        df["skills_text"] = df["skills"].apply(lambda x: " ".join(x) if x else "")
    elif "skills_text" not in df.columns:
        print("Error: Falta la columna 'skills' o 'skills_text' para la predicción.")
        df["segment"] = -1
        return df

    try:
        print(f"Preprocesando {len(df)} candidatos para predicción...")
        # Usar el preprocesador *cargado* para transformar los datos
        X_processed = preprocessor.transform(df)
        print("Prediciendo segmentos...")
        # Predecir etiquetas de clúster
        segments = model.predict(X_processed)
        df["segment"] = segments
        print("Predicción de segmentos completa.")
    except Exception as e:
        print(f"Error durante la predicción: {e}")
        # Asignar segmento por defecto/error
        df["segment"] = -1

    return df
