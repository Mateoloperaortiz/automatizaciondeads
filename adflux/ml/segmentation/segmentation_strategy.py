"""
Interfaz para estrategias de segmentación.

Define la interfaz que deben implementar todas las estrategias
de segmentación de candidatos.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np


class SegmentationStrategy(ABC):
    """
    Interfaz para estrategias de segmentación de candidatos.
    
    Define los métodos que deben implementar todas las estrategias
    de segmentación para garantizar que sean intercambiables.
    """
    
    @abstractmethod
    def segment_candidates(self, data: pd.DataFrame, n_segments: int = 5) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Segmenta candidatos en grupos basados en sus características.
        
        Args:
            data: DataFrame con datos de candidatos
            n_segments: Número de segmentos a crear
            
        Returns:
            Tupla con (DataFrame con segmentos asignados, métricas de evaluación)
        """
        pass
    
    @abstractmethod
    def get_segment_profiles(self, data: pd.DataFrame, segment_column: str = 'segment') -> Dict[int, Dict[str, Any]]:
        """
        Genera perfiles para cada segmento basados en las características de los candidatos.
        
        Args:
            data: DataFrame con datos de candidatos y segmentos asignados
            segment_column: Nombre de la columna que contiene los segmentos
            
        Returns:
            Diccionario con perfiles de segmentos {segment_id: {feature: value, ...}}
        """
        pass
    
    @abstractmethod
    def predict_segment(self, candidate_data: Dict[str, Any], model_data: Any) -> int:
        """
        Predice el segmento al que pertenece un nuevo candidato.
        
        Args:
            candidate_data: Diccionario con datos del candidato
            model_data: Datos del modelo entrenado
            
        Returns:
            ID del segmento predicho
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Obtiene el nombre de la estrategia de segmentación.
        
        Returns:
            Nombre de la estrategia
        """
        pass
    
    @abstractmethod
    def get_strategy_description(self) -> str:
        """
        Obtiene la descripción de la estrategia de segmentación.
        
        Returns:
            Descripción de la estrategia
        """
        pass
