"""
Contexto para estrategias de segmentación.

Implementa el patrón Strategy para la segmentación de candidatos,
permitiendo cambiar el algoritmo de segmentación en tiempo de ejecución.
"""

from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime

from .segmentation_strategy import SegmentationStrategy
from .kmeans_segmentation import KMeansSegmentation
from .hierarchical_segmentation import HierarchicalSegmentation
from .dbscan_segmentation import DBSCANSegmentation


class SegmentationContext:
    """
    Contexto para estrategias de segmentación.
    
    Implementa el patrón Strategy para la segmentación de candidatos,
    permitiendo cambiar el algoritmo de segmentación en tiempo de ejecución.
    """
    
    def __init__(self, strategy: Optional[SegmentationStrategy] = None):
        """
        Inicializa el contexto de segmentación.
        
        Args:
            strategy: Estrategia de segmentación a utilizar (por defecto, K-Means)
        """
        self.strategy = strategy or KMeansSegmentation()
        self.segmented_data = None
        self.segment_profiles = None
        self.metrics = None
        self.last_run_timestamp = None
    
    def set_strategy(self, strategy: SegmentationStrategy) -> None:
        """
        Cambia la estrategia de segmentación.
        
        Args:
            strategy: Nueva estrategia de segmentación
        """
        self.strategy = strategy
    
    def run_segmentation(self, data: pd.DataFrame, n_segments: int = 5) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Ejecuta la segmentación utilizando la estrategia actual.
        
        Args:
            data: DataFrame con datos de candidatos
            n_segments: Número de segmentos a crear
            
        Returns:
            Tupla con (DataFrame con segmentos asignados, métricas de evaluación)
        """
        self.segmented_data, self.metrics = self.strategy.segment_candidates(data, n_segments)
        self.segment_profiles = self.strategy.get_segment_profiles(self.segmented_data)
        self.last_run_timestamp = datetime.now()
        
        return self.segmented_data, self.metrics
    
    def get_segment_profiles(self) -> Dict[int, Dict[str, Any]]:
        """
        Obtiene los perfiles de los segmentos.
        
        Returns:
            Diccionario con perfiles de segmentos
        """
        if self.segment_profiles is None:
            raise ValueError("Debe ejecutar run_segmentation primero")
        
        return self.segment_profiles
    
    def predict_segment(self, candidate_data: Dict[str, Any]) -> int:
        """
        Predice el segmento al que pertenece un nuevo candidato.
        
        Args:
            candidate_data: Diccionario con datos del candidato
            
        Returns:
            ID del segmento predicho
        """
        if self.segmented_data is None:
            raise ValueError("Debe ejecutar run_segmentation primero")
        
        return self.strategy.predict_segment(candidate_data, None)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene las métricas de evaluación de la segmentación.
        
        Returns:
            Diccionario con métricas de evaluación
        """
        if self.metrics is None:
            raise ValueError("Debe ejecutar run_segmentation primero")
        
        return self.metrics
    
    def get_strategy_info(self) -> Dict[str, str]:
        """
        Obtiene información sobre la estrategia actual.
        
        Returns:
            Diccionario con información de la estrategia
        """
        return {
            'name': self.strategy.get_strategy_name(),
            'description': self.strategy.get_strategy_description(),
        }
    
    def save_model(self, filepath: str) -> None:
        """
        Guarda el modelo de segmentación en un archivo.
        
        Args:
            filepath: Ruta del archivo donde guardar el modelo
        """
        if self.segmented_data is None:
            raise ValueError("Debe ejecutar run_segmentation primero")
        
        model_data = {
            'strategy': self.strategy,
            'metrics': self.metrics,
            'segment_profiles': self.segment_profiles,
            'timestamp': self.last_run_timestamp,
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    @classmethod
    def load_model(cls, filepath: str) -> 'SegmentationContext':
        """
        Carga un modelo de segmentación desde un archivo.
        
        Args:
            filepath: Ruta del archivo donde está guardado el modelo
            
        Returns:
            Contexto de segmentación con el modelo cargado
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No se encontró el archivo {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        context = cls(strategy=model_data['strategy'])
        context.metrics = model_data['metrics']
        context.segment_profiles = model_data['segment_profiles']
        context.last_run_timestamp = model_data['timestamp']
        
        return context
