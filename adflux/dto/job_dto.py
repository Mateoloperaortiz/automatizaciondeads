"""
DTOs para trabajos en AdFlux.

Este módulo define los DTOs utilizados para transferir datos
de trabajos entre la capa de presentación y la capa de lógica de negocio.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime

from .base_dto import BaseDTO


@dataclass
class JobDTO(BaseDTO):
    """DTO para representar un trabajo completo."""
    
    job_id: int
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    requirements: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    _validators: ClassVar[Dict[str, Any]] = {
        'title': lambda x: None if len(x) >= 3 else ValueError('Título debe tener al menos 3 caracteres'),
        'salary_min': lambda x: None if x is None or x >= 0 else ValueError('Salario mínimo debe ser positivo'),
        'salary_max': lambda x: None if x is None or x >= 0 else ValueError('Salario máximo debe ser positivo'),
    }


@dataclass
class JobListDTO(BaseDTO):
    """DTO para representar una lista paginada de trabajos."""
    
    jobs: List[JobDTO]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    @classmethod
    def from_query_result(cls, jobs: List[Any], page: int, per_page: int, total: int) -> 'JobListDTO':
        """
        Crea un DTO a partir de resultados de consulta paginados.
        
        Args:
            jobs: Lista de modelos de trabajos
            page: Número de página actual
            per_page: Número de elementos por página
            total: Número total de trabajos
            
        Returns:
            Instancia del DTO
        """
        job_dtos = []
        for j in jobs:
            dto = JobDTO.from_model(j)
            if isinstance(dto, JobDTO):
                job_dtos.append(dto)
            
        total_pages = (total + per_page - 1) // per_page  # Redondeo hacia arriba
        
        return cls(
            jobs=job_dtos,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )


@dataclass
class JobCreateDTO(BaseDTO):
    """DTO para crear un nuevo trabajo."""
    
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    requirements: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    status: Optional[str] = None
    
    _validators: ClassVar[Dict[str, Any]] = {
        'title': lambda x: None if len(x) >= 3 else ValueError('Título debe tener al menos 3 caracteres'),
        'company': lambda x: None if len(x) >= 2 else ValueError('Empresa debe tener al menos 2 caracteres'),
        'salary_min': lambda x: None if x is None or x >= 0 else ValueError('Salario mínimo debe ser positivo'),
        'salary_max': lambda x: None if x is None or x >= 0 else ValueError('Salario máximo debe ser positivo'),
    }


@dataclass
class JobUpdateDTO(BaseDTO):
    """DTO para actualizar un trabajo existente."""
    
    job_id: int
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    requirements: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    status: Optional[str] = None
    
    _validators: ClassVar[Dict[str, Any]] = {
        'title': lambda x: None if x is None or len(x) >= 3 else ValueError('Título debe tener al menos 3 caracteres'),
        'company': lambda x: None if x is None or len(x) >= 2 else ValueError('Empresa debe tener al menos 2 caracteres'),
        'salary_min': lambda x: None if x is None or x >= 0 else ValueError('Salario mínimo debe ser positivo'),
        'salary_max': lambda x: None if x is None or x >= 0 else ValueError('Salario máximo debe ser positivo'),
    }
    
    def update_model(self, model: Any) -> Any:
        """
        Actualiza un modelo de trabajo con los datos del DTO.
        
        Args:
            model: Modelo de trabajo a actualizar
            
        Returns:
            Modelo actualizado
        """
        for field_name, field_value in self.to_dict().items():
            if field_value is not None and hasattr(model, field_name):
                setattr(model, field_name, field_value)
        
        return model
