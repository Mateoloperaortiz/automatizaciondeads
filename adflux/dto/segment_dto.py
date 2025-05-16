"""
DTOs para segmentos en AdFlux.

Este módulo define los DTOs utilizados para transferir datos
de segmentos entre la capa de presentación y la capa de lógica de negocio.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime

from .base_dto import BaseDTO


@dataclass
class SegmentDTO(BaseDTO):
    """DTO para representar un segmento completo."""
    
    segment_id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    _validators: ClassVar[Dict[str, Any]] = {
        'name': lambda x: None if len(x) >= 2 else ValueError('Nombre debe tener al menos 2 caracteres'),
    }
    
    @classmethod
    def from_model(cls, model: Any) -> 'SegmentDTO':
        """
        Crea un DTO a partir de un modelo de segmento.
        
        Args:
            model: Modelo de segmento
            
        Returns:
            Instancia del DTO
        """
        model_dict = {}
        for column in model.__table__.columns:
            model_dict[column.name] = getattr(model, column.name)
        
        if 'id' in model_dict and 'segment_id' not in model_dict:
            model_dict['segment_id'] = model_dict.pop('id')
        
        return cls(**model_dict)


@dataclass
class SegmentListDTO(BaseDTO):
    """DTO para representar una lista paginada de segmentos."""
    
    segments: List[SegmentDTO]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    @classmethod
    def from_query_result(cls, segments: List[Any], page: int, per_page: int, total: int) -> 'SegmentListDTO':
        """
        Crea un DTO a partir de resultados de consulta paginados.
        
        Args:
            segments: Lista de modelos de segmentos
            page: Número de página actual
            per_page: Número de elementos por página
            total: Número total de segmentos
            
        Returns:
            Instancia del DTO
        """
        segment_dtos = []
        for s in segments:
            dto = SegmentDTO.from_model(s)
            if isinstance(dto, SegmentDTO):
                segment_dtos.append(dto)
            
        total_pages = (total + per_page - 1) // per_page  # Redondeo hacia arriba
        
        return cls(
            segments=segment_dtos,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
