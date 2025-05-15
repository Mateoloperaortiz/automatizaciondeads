"""
Paquete de estrategias de segmentación.

Este paquete contiene las diferentes estrategias de segmentación
que se pueden utilizar para segmentar candidatos.
"""

from .segmentation_strategy import SegmentationStrategy
from .kmeans_segmentation import KMeansSegmentation
from .hierarchical_segmentation import HierarchicalSegmentation
from .dbscan_segmentation import DBSCANSegmentation
from .segmentation_context import SegmentationContext

__all__ = [
    "SegmentationStrategy",
    "KMeansSegmentation",
    "HierarchicalSegmentation",
    "DBSCANSegmentation",
    "SegmentationContext",
]
