"""
Funciones de modelos para el módulo de machine learning de AdFlux.
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from typing import Tuple

from .constants import DEFAULT_N_CLUSTERS, DEFAULT_MODEL_PATH, DEFAULT_PREPROCESSOR_PATH
from .preprocessing import create_preprocessor


def train_segmentation_model(
    df: pd.DataFrame, 
    n_clusters: int = DEFAULT_N_CLUSTERS,
    model_path: str = DEFAULT_MODEL_PATH, 
    preprocessor_path: str = DEFAULT_PREPROCESSOR_PATH
) -> Tuple[KMeans, ColumnTransformer]:
    """
    Preprocesa datos de candidatos, entrena un modelo K-means y guarda ambos.
    
    Args:
        df: DataFrame con datos de candidatos (debe incluir características y 'skills_text').
        n_clusters: Número de segmentos (clústeres) a crear.
        model_path: Ruta para guardar el modelo K-means entrenado.
        preprocessor_path: Ruta para guardar el preprocesador ajustado.

    Returns:
        Tupla que contiene el modelo KMeans ajustado y el ColumnTransformer ajustado.
    """
    if df.empty:
        print("Error: El DataFrame de entrada está vacío. No se puede entrenar el modelo.")
        # O lanzar un error
        raise ValueError("No se puede entrenar el modelo en un DataFrame vacío")
        
    print(f"Iniciando preprocesamiento y entrenamiento para {len(df)} candidatos...")
    preprocessor = create_preprocessor()
    
    # Ajustar el preprocesador y transformar los datos
    print("Ajustando preprocesador...")
    X_processed = preprocessor.fit_transform(df)
    print(f"Preprocesamiento completo. Forma de los datos procesados: {X_processed.shape}")

    # Entrenar el modelo K-means
    print(f"Entrenando modelo K-means con {n_clusters} clústeres...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)  # Establecer n_init explícitamente
    kmeans.fit(X_processed)
    print("Entrenamiento K-means completo.")

    # Asegurar que el directorio del modelo exista
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(preprocessor_path), exist_ok=True)

    # Guardar el modelo y el preprocesador
    try:
        joblib.dump(kmeans, model_path)
        joblib.dump(preprocessor, preprocessor_path)
        print(f"Modelo guardado en {model_path}")
        print(f"Preprocesador guardado en {preprocessor_path}")
    except Exception as e:
        print(f"Error al guardar modelo o preprocesador: {e}")
        # Continuar a pesar del error de guardado - aún podemos devolver el modelo y preprocesador

    return kmeans, preprocessor
