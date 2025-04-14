"""
Implementación de estrategia de segmentación K-Means.

Implementa la estrategia de segmentación utilizando el algoritmo K-Means.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score

from .segmentation_strategy import SegmentationStrategy


class KMeansSegmentation(SegmentationStrategy):
    """
    Estrategia de segmentación utilizando el algoritmo K-Means.
    
    Implementa la segmentación de candidatos utilizando el algoritmo
    K-Means de clustering.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Inicializa la estrategia de segmentación K-Means.
        
        Args:
            random_state: Semilla para reproducibilidad
        """
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = None
        self.feature_columns = None
    
    def segment_candidates(self, data: pd.DataFrame, n_segments: int = 5) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Segmenta candidatos utilizando K-Means.
        
        Args:
            data: DataFrame con datos de candidatos
            n_segments: Número de segmentos a crear
            
        Returns:
            Tupla con (DataFrame con segmentos asignados, métricas de evaluación)
        """
        # Seleccionar columnas numéricas para clustering
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Excluir columnas que no son características (IDs, fechas, etc.)
        exclude_cols = ['candidate_id', 'segment_id', 'created_at', 'updated_at']
        self.feature_columns = [col for col in numeric_cols if col not in exclude_cols]
        
        if not self.feature_columns:
            raise ValueError("No se encontraron columnas numéricas para segmentación")
        
        # Preparar datos para clustering
        X = data[self.feature_columns].copy()
        
        # Manejar valores faltantes
        X = X.fillna(X.mean())
        
        # Escalar datos
        X_scaled = self.scaler.fit_transform(X)
        
        # Entrenar modelo K-Means
        self.model = KMeans(n_clusters=n_segments, random_state=self.random_state)
        segments = self.model.fit_predict(X_scaled)
        
        # Añadir segmentos al DataFrame original
        result_df = data.copy()
        result_df['segment'] = segments
        
        # Calcular métricas de evaluación
        metrics = self._calculate_metrics(X_scaled, segments)
        
        return result_df, metrics
    
    def get_segment_profiles(self, data: pd.DataFrame, segment_column: str = 'segment') -> Dict[int, Dict[str, Any]]:
        """
        Genera perfiles para cada segmento basados en las características de los candidatos.
        
        Args:
            data: DataFrame con datos de candidatos y segmentos asignados
            segment_column: Nombre de la columna que contiene los segmentos
            
        Returns:
            Diccionario con perfiles de segmentos {segment_id: {feature: value, ...}}
        """
        if self.feature_columns is None:
            raise ValueError("Debe ejecutar segment_candidates primero")
        
        profiles = {}
        
        # Para cada segmento, calcular estadísticas de las características
        for segment_id in data[segment_column].unique():
            segment_data = data[data[segment_column] == segment_id]
            
            profile = {
                'count': len(segment_data),
                'percentage': (len(segment_data) / len(data)) * 100,
                'features': {}
            }
            
            # Calcular media y desviación estándar para cada característica
            for feature in self.feature_columns:
                profile['features'][feature] = {
                    'mean': segment_data[feature].mean(),
                    'std': segment_data[feature].std(),
                    'min': segment_data[feature].min(),
                    'max': segment_data[feature].max(),
                }
            
            profiles[int(segment_id)] = profile
        
        return profiles
    
    def predict_segment(self, candidate_data: Dict[str, Any], model_data: Any = None) -> int:
        """
        Predice el segmento al que pertenece un nuevo candidato.
        
        Args:
            candidate_data: Diccionario con datos del candidato
            model_data: Datos del modelo entrenado (no utilizado en K-Means)
            
        Returns:
            ID del segmento predicho
        """
        if self.model is None or self.feature_columns is None:
            raise ValueError("Debe ejecutar segment_candidates primero")
        
        # Extraer características relevantes
        features = []
        for feature in self.feature_columns:
            if feature in candidate_data:
                features.append(candidate_data[feature])
            else:
                # Si falta alguna característica, usar 0 como valor por defecto
                features.append(0)
        
        # Convertir a array y escalar
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Predecir segmento
        segment = self.model.predict(X_scaled)[0]
        
        return int(segment)
    
    def get_strategy_name(self) -> str:
        """
        Obtiene el nombre de la estrategia de segmentación.
        
        Returns:
            Nombre de la estrategia
        """
        return "K-Means Clustering"
    
    def get_strategy_description(self) -> str:
        """
        Obtiene la descripción de la estrategia de segmentación.
        
        Returns:
            Descripción de la estrategia
        """
        return (
            "Algoritmo de clustering que agrupa candidatos en segmentos basados en la "
            "similitud de sus características, minimizando la distancia entre los puntos "
            "dentro de cada segmento y maximizando la distancia entre segmentos."
        )
    
    def _calculate_metrics(self, X: np.ndarray, segments: np.ndarray) -> Dict[str, Any]:
        """
        Calcula métricas de evaluación para el clustering.
        
        Args:
            X: Datos escalados
            segments: Etiquetas de segmentos asignados
            
        Returns:
            Diccionario con métricas de evaluación
        """
        metrics = {}
        
        # Calcular inercia (suma de distancias al cuadrado dentro de los clusters)
        metrics['inertia'] = self.model.inertia_
        
        # Calcular coeficiente de silueta (mide qué tan similar es un objeto a su propio cluster vs. otros clusters)
        try:
            metrics['silhouette_score'] = silhouette_score(X, segments)
        except:
            metrics['silhouette_score'] = 0
        
        # Calcular índice Calinski-Harabasz (mide la relación entre la dispersión entre clusters y dentro de clusters)
        try:
            metrics['calinski_harabasz_score'] = calinski_harabasz_score(X, segments)
        except:
            metrics['calinski_harabasz_score'] = 0
        
        return metrics
