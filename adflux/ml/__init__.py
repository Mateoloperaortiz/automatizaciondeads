"""
Paquete de machine learning para AdFlux.

Este paquete contiene todas las funcionalidades relacionadas con machine learning
utilizadas por AdFlux, organizadas en módulos específicos según su funcionalidad.
"""

# Importar constantes
from .constants import (
    DEFAULT_MODEL_DIR,
    DEFAULT_MODEL_PATH,
    DEFAULT_PREPROCESSOR_PATH,
    DEFAULT_N_CLUSTERS
)

# Importar funciones de preprocesamiento
from .preprocessing import (
    load_candidate_data,
    create_preprocessor
)

# Importar funciones de modelos
from .models import (
    train_segmentation_model
)

# Importar funciones de predicción
from .prediction import (
    predict_candidate_segments
)

# Importar funciones de evaluación
from .evaluation import (
    analyze_segments_from_db
)

# Importar funciones de utilidades
from .utils import (
    load_segmentation_model
)

# Para mantener compatibilidad con el código existente
__all__ = [
    # Constantes
    'DEFAULT_MODEL_DIR',
    'DEFAULT_MODEL_PATH',
    'DEFAULT_PREPROCESSOR_PATH',
    'DEFAULT_N_CLUSTERS',
    
    # Preprocesamiento
    'load_candidate_data',
    'create_preprocessor',
    
    # Modelos
    'train_segmentation_model',
    
    # Predicción
    'predict_candidate_segments',
    
    # Evaluación
    'analyze_segments_from_db',
    
    # Utilidades
    'load_segmentation_model'
]
