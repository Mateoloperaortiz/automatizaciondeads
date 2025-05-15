"""
Implementación de estrategia de segmentación DBSCAN.

Implementa la estrategia de segmentación utilizando el algoritmo DBSCAN.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.neighbors import NearestNeighbors

from .segmentation_strategy import SegmentationStrategy


class DBSCANSegmentation(SegmentationStrategy):
    """
    Estrategia de segmentación utilizando el algoritmo DBSCAN.
    
    Implementa la segmentación de candidatos utilizando el algoritmo
    DBSCAN (Density-Based Spatial Clustering of Applications with Noise).
    """
    
    def __init__(self, eps: float = 0.5, min_samples: int = 2, metric: str = 'euclidean'):
        """
        Inicializa la estrategia de segmentación DBSCAN.
        
        Args:
            eps: Radio de la vecindad
            min_samples: Número mínimo de muestras en la vecindad para considerar un punto como core
            metric: Métrica de distancia a utilizar
        """
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        self.scaler = StandardScaler()
        self.model = None
        self.feature_columns = None
        self.core_samples_mask = None
        self.labels = None
        self.X_scaled = None
    
    def segment_candidates(self, data: pd.DataFrame, n_segments: int = 5) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Segmenta candidatos utilizando DBSCAN.
        
        Args:
            data: DataFrame con datos de candidatos
            n_segments: Número de segmentos a crear (no utilizado en DBSCAN,
                        el algoritmo determina automáticamente la cantidad óptima)
            
        Returns:
            Tupla con (DataFrame con segmentos asignados, métricas de evaluación)
        """
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        exclude_cols = ['candidate_id', 'segment_id', 'created_at', 'updated_at']
        self.feature_columns = [col for col in numeric_cols if col not in exclude_cols]
        
        if not self.feature_columns:
            raise ValueError("No se encontraron columnas numéricas para segmentación")
        
        X = data[self.feature_columns].copy()
        
        X = X.fillna(X.mean())
        
        self.X_scaled = self.scaler.fit_transform(X)
        
        if self.eps is None:
            nbrs = NearestNeighbors(n_neighbors=self.min_samples, metric=self.metric).fit(self.X_scaled)
            distances, indices = nbrs.kneighbors(self.X_scaled)
            distances = np.sort(distances[:, self.min_samples-1])
            
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(-distances)
            if len(peaks) > 0:
                self.eps = distances[peaks[0]]
            else:
                self.eps = np.percentile(distances, 90)  # Utilizar un percentil como heurística
        
        self.model = DBSCAN(eps=float(self.eps), min_samples=self.min_samples, metric=self.metric)
        self.labels = self.model.fit_predict(self.X_scaled)
        
        self.core_samples_mask = np.zeros_like(self.labels, dtype=bool)
        if hasattr(self.model, 'core_sample_indices_'):
            self.core_samples_mask[self.model.core_sample_indices_] = True
        
        n_clusters = len(set(self.labels)) - (1 if -1 in self.labels else 0)
        
        noise_mask = (self.labels == -1)
        if np.any(noise_mask):
            if n_clusters > 0:
                self._reassign_noise_points()
            else:
                self.labels = np.zeros_like(self.labels)
                n_clusters = 1
        
        result_df = data.copy()
        result_df['segment'] = self.labels
        
        metrics = self._calculate_metrics(self.X_scaled, self.labels)
        metrics['n_clusters'] = n_clusters
        metrics['noise_points'] = np.sum(noise_mask)
        
        return result_df, metrics
    
    def _reassign_noise_points(self):
        """
        Reasigna puntos de ruido al cluster más cercano.
        """
        if self.labels is None or self.X_scaled is None:
            return
            
        noise_mask = (self.labels == -1)
        if not np.any(noise_mask):
            return
        
        for i in np.where(noise_mask)[0]:
            point = self.X_scaled[i].reshape(1, -1)
            
            non_noise_mask = ~noise_mask
            if not np.any(non_noise_mask):
                break
                
            distances = []
            for label in set(self.labels[non_noise_mask]):
                if label == -1:
                    continue
                mask = (self.labels == label)
                if not np.any(mask):
                    continue
                centroid = np.mean(self.X_scaled[mask], axis=0).reshape(1, -1)
                from sklearn.metrics.pairwise import euclidean_distances
                distance = euclidean_distances(point, centroid)[0][0]
                distances.append((label, distance))
            
            if distances:
                closest_label, _ = min(distances, key=lambda x: x[1])
                self.labels[i] = closest_label
    
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
        
        for segment_id in set(data[segment_column].unique()):
            if segment_id == -1:  # Ignorar puntos de ruido si existen
                continue
                
            segment_data = data[data[segment_column] == segment_id]
            
            profile = {
                'count': len(segment_data),
                'percentage': (len(segment_data) / len(data)) * 100,
                'features': {}
            }
            
            for feature in self.feature_columns:
                profile['features'][feature] = {
                    'mean': segment_data[feature].mean(),
                    'std': segment_data[feature].std(),
                    'min': segment_data[feature].min(),
                    'max': segment_data[feature].max(),
                }
            
            if self.core_samples_mask is not None:
                segment_indices = np.where(self.labels == segment_id)[0]
                core_indices = segment_indices[self.core_samples_mask[segment_indices]]
                profile['core_samples'] = len(core_indices)
                profile['non_core_samples'] = len(segment_data) - len(core_indices)
                profile['density'] = len(core_indices) / len(segment_data) if len(segment_data) > 0 else 0
            
            profiles[int(segment_id)] = profile
        
        return profiles
    
    def predict_segment(self, candidate_data: Dict[str, Any], model_data: Any = None) -> int:
        """
        Predice el segmento al que pertenece un nuevo candidato.
        
        Args:
            candidate_data: Diccionario con datos del candidato
            model_data: Datos del modelo entrenado (no utilizado en DBSCAN)
            
        Returns:
            ID del segmento predicho
        """
        if self.model is None or self.feature_columns is None:
            raise ValueError("Debe ejecutar segment_candidates primero")
        
        features = []
        for feature in self.feature_columns:
            if feature in candidate_data:
                features.append(candidate_data[feature])
            else:
                features.append(0)
        
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        
        if self.X_scaled is None or len(self.X_scaled) == 0:
            return 0
        
        from sklearn.metrics.pairwise import euclidean_distances
        distances = euclidean_distances(X_scaled, self.X_scaled)[0]
        
        closest_idx = np.argmin(distances)
        
        if self.labels is None:
            return 0
            
        return int(self.labels[closest_idx])
    
    def get_strategy_name(self) -> str:
        """
        Obtiene el nombre de la estrategia de segmentación.
        
        Returns:
            Nombre de la estrategia
        """
        return "DBSCAN Clustering"
    
    def get_strategy_description(self) -> str:
        """
        Obtiene la descripción de la estrategia de segmentación.
        
        Returns:
            Descripción de la estrategia
        """
        return (
            "Algoritmo de clustering basado en densidad que agrupa puntos que están "
            "cercanos entre sí en regiones con suficiente densidad. DBSCAN puede "
            "encontrar clusters de formas arbitrarias y detectar automáticamente "
            "el número de clusters, además de identificar puntos atípicos (ruido)."
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
        
        n_clusters = len(set(segments)) - (1 if -1 in segments else 0)
        metrics['n_clusters'] = n_clusters
        
        if n_clusters <= 1:
            metrics['silhouette_score'] = 0
            metrics['calinski_harabasz_score'] = 0
            return metrics
        
        mask = segments != -1
        if np.sum(mask) > 1:  # Necesitamos al menos 2 puntos para calcular la silueta
            X_no_noise = X[mask]
            labels_no_noise = segments[mask]
            
            try:
                metrics['silhouette_score'] = silhouette_score(X_no_noise, labels_no_noise)
            except:
                metrics['silhouette_score'] = 0
            
            try:
                metrics['calinski_harabasz_score'] = calinski_harabasz_score(X_no_noise, labels_no_noise)
            except:
                metrics['calinski_harabasz_score'] = 0
        else:
            metrics['silhouette_score'] = 0
            metrics['calinski_harabasz_score'] = 0
        
        return metrics
