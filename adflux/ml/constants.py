"""
Constantes utilizadas en el módulo de machine learning de AdFlux.
"""

import os

# Rutas para guardar y cargar modelos
DEFAULT_MODEL_DIR = 'instance/ml_models'  # Guardar modelos en la carpeta instance
DEFAULT_MODEL_PATH = os.path.join(DEFAULT_MODEL_DIR, 'kmeans_model.joblib')
DEFAULT_PREPROCESSOR_PATH = os.path.join(DEFAULT_MODEL_DIR, 'kmeans_preprocessor.joblib')

# Parámetros de modelos
DEFAULT_N_CLUSTERS = 5
