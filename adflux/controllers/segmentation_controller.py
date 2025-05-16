"""
Controlador para segmentación en AdFlux.

Este módulo define el controlador que maneja las solicitudes HTTP
relacionadas con segmentación y coordina la interacción entre la capa
de presentación y la capa de lógica de negocio.
"""

from typing import Dict, Any, Tuple, List, Optional
from flask import request, jsonify, current_app, Response

from ..services.interfaces import ISegmentationService
from ..dto.segment_dto import SegmentDTO, SegmentListDTO


class SegmentationController:
    """
    Controlador para segmentación.
    
    Maneja las solicitudes HTTP relacionadas con segmentación y coordina
    la interacción entre la capa de presentación y la capa de lógica de negocio.
    """
    
    def __init__(self, segmentation_service: ISegmentationService):
        """
        Inicializa el controlador con el servicio de segmentación.
        
        Args:
            segmentation_service: Servicio de segmentación
        """
        self.segmentation_service = segmentation_service
    
    def get_segments(self) -> Response:
        """
        Obtiene una lista paginada de segmentos.
        
        Returns:
            Respuesta HTTP con la lista de segmentos
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        if page < 1:
            return jsonify({'error': 'La página debe ser mayor o igual a 1'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'El número de elementos por página debe estar entre 1 y 100'}), 400
        
        segments, pagination = self.segmentation_service.get_segments(
            page=page,
            per_page=per_page,
            query=query,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        segment_list_dto = SegmentListDTO.from_query_result(
            segments=segments,
            page=page,
            per_page=per_page,
            total=pagination.total
        )
        
        return jsonify(segment_list_dto.to_dict())
    
    def get_segment(self, segment_id: int) -> Response:
        """
        Obtiene un segmento por su ID.
        
        Args:
            segment_id: ID del segmento
            
        Returns:
            Respuesta HTTP con los datos del segmento
        """
        segment = self.segmentation_service.get_segment_by_id(segment_id)
        
        if not segment:
            return jsonify({'error': f'Segmento con ID {segment_id} no encontrado'}), 404
        
        segment_dto = SegmentDTO.from_model(segment)
        
        return jsonify(segment_dto.to_dict())
    
    def train_model(self) -> Response:
        """
        Entrena el modelo de segmentación.
        
        Returns:
            Respuesta HTTP con el resultado del entrenamiento
        """
        algorithm = request.args.get('algorithm', 'kmeans')
        clusters = request.args.get('clusters', 5, type=int)
        
        result, message, status_code = self.segmentation_service.train_model(
            algorithm=algorithm,
            clusters=clusters
        )
        
        if not result:
            return jsonify({'error': message}), status_code
        
        return jsonify({'message': message, 'algorithm': algorithm, 'clusters': clusters}), 200
    
    def predict_segments(self) -> Response:
        """
        Aplica el modelo de segmentación para predecir segmentos.
        
        Returns:
            Respuesta HTTP con el resultado de la predicción
        """
        algorithm = request.args.get('algorithm', 'kmeans')
        
        result, message, status_code = self.segmentation_service.predict_segments(
            algorithm=algorithm
        )
        
        if not result:
            return jsonify({'error': message}), status_code
        
        return jsonify({'message': message, 'algorithm': algorithm}), 200
    
    def analyze_segments(self) -> Response:
        """
        Analiza las características de los segmentos.
        
        Returns:
            Respuesta HTTP con el análisis de segmentos
        """
        algorithm = request.args.get('algorithm', 'kmeans')
        
        analysis, message, status_code = self.segmentation_service.analyze_segments(
            algorithm=algorithm
        )
        
        if status_code != 200:
            return jsonify({'error': message}), status_code
        
        return jsonify({
            'message': message,
            'algorithm': algorithm,
            'analysis': analysis
        }), 200
