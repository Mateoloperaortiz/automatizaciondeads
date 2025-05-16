"""
DTOs para campañas en AdFlux.

Este módulo define los DTOs utilizados para transferir datos
de campañas entre la capa de presentación y la capa de lógica de negocio.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime

from .base_dto import BaseDTO


@dataclass
class CampaignDTO(BaseDTO):
    """DTO para representar una campaña completa."""
    
    campaign_id: int
    name: str
    platform: str
    job_id: int
    status: str
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    segment_ids: Optional[List[int]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    _validators: ClassVar[Dict[str, Any]] = {
        'name': lambda x: None if len(x) >= 3 else ValueError('Nombre debe tener al menos 3 caracteres'),
        'platform': lambda x: None if x in ['meta', 'google', 'linkedin'] else ValueError('Plataforma no válida'),
        'budget': lambda x: None if x is None or x >= 0 else ValueError('Presupuesto debe ser positivo'),
    }
    
    @classmethod
    def from_model(cls, model: Any) -> 'CampaignDTO':
        """
        Crea un DTO a partir de un modelo de campaña.
        
        Args:
            model: Modelo de campaña
            
        Returns:
            Instancia del DTO
        """
        # Crear un diccionario con los datos del modelo
        model_dict = {}
        for column in model.__table__.columns:
            model_dict[column.name] = getattr(model, column.name)
        
        # Crear instancia del DTO
        dto = cls(**model_dict)
        
        if hasattr(model, 'target_audience') and isinstance(model.target_audience, str):
            import json
            try:
                target_audience = json.loads(model.target_audience) if model.target_audience else {}
                setattr(dto, 'target_audience', target_audience)
            except:
                setattr(dto, 'target_audience', {})
        
        if hasattr(model, 'segment_ids') and isinstance(model.segment_ids, str):
            segment_ids = [int(s.strip()) for s in model.segment_ids.split(',')] if model.segment_ids else []
            setattr(dto, 'segment_ids', segment_ids)
        
        return dto


@dataclass
class CampaignListDTO(BaseDTO):
    """DTO para representar una lista paginada de campañas."""
    
    campaigns: List[CampaignDTO]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    @classmethod
    def from_query_result(cls, campaigns: List[Any], page: int, per_page: int, total: int) -> 'CampaignListDTO':
        """
        Crea un DTO a partir de resultados de consulta paginados.
        
        Args:
            campaigns: Lista de modelos de campañas
            page: Número de página actual
            per_page: Número de elementos por página
            total: Número total de campañas
            
        Returns:
            Instancia del DTO
        """
        campaign_dtos = []
        for c in campaigns:
            dto = CampaignDTO.from_model(c)
            if isinstance(dto, CampaignDTO):
                campaign_dtos.append(dto)
            
        total_pages = (total + per_page - 1) // per_page  # Redondeo hacia arriba
        
        return cls(
            campaigns=campaign_dtos,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )


@dataclass
class CampaignCreateDTO(BaseDTO):
    """DTO para crear una nueva campaña."""
    
    name: str
    platform: str
    job_id: int
    status: str = "draft"
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    segment_ids: Optional[List[int]] = None
    
    _validators: ClassVar[Dict[str, Any]] = {
        'name': lambda x: None if len(x) >= 3 else ValueError('Nombre debe tener al menos 3 caracteres'),
        'platform': lambda x: None if x in ['meta', 'google', 'linkedin'] else ValueError('Plataforma no válida'),
        'budget': lambda x: None if x is None or x >= 0 else ValueError('Presupuesto debe ser positivo'),
    }
    
    def to_model(self, model_class: Any) -> Any:
        """
        Convierte el DTO a un modelo de campaña.
        
        Args:
            model_class: Clase del modelo de campaña
            
        Returns:
            Instancia del modelo
        """
        model = super().to_model(model_class)
        
        if hasattr(self, 'target_audience') and self.target_audience is not None:
            import json
            model.target_audience = json.dumps(self.target_audience)
        
        if hasattr(self, 'segment_ids') and self.segment_ids is not None:
            model.segment_ids = ','.join(str(s) for s in self.segment_ids)
        
        return model


@dataclass
class CampaignUpdateDTO(BaseDTO):
    """DTO para actualizar una campaña existente."""
    
    campaign_id: int
    name: Optional[str] = None
    platform: Optional[str] = None
    job_id: Optional[int] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    segment_ids: Optional[List[int]] = None
    
    _validators: ClassVar[Dict[str, Any]] = {
        'name': lambda x: None if x is None or len(x) >= 3 else ValueError('Nombre debe tener al menos 3 caracteres'),
        'platform': lambda x: None if x is None or x in ['meta', 'google', 'linkedin'] else ValueError('Plataforma no válida'),
        'budget': lambda x: None if x is None or x >= 0 else ValueError('Presupuesto debe ser positivo'),
    }
    
    def update_model(self, model: Any) -> Any:
        """
        Actualiza un modelo de campaña con los datos del DTO.
        
        Args:
            model: Modelo de campaña a actualizar
            
        Returns:
            Modelo actualizado
        """
        for field_name, field_value in self.to_dict().items():
            if field_value is not None and hasattr(model, field_name):
                if field_name == 'target_audience' and isinstance(field_value, dict):
                    import json
                    setattr(model, field_name, json.dumps(field_value))
                elif field_name == 'segment_ids' and isinstance(field_value, list):
                    setattr(model, field_name, ','.join(str(s) for s in field_value))
                else:
                    setattr(model, field_name, field_value)
        
        return model
