"""
DTOs para candidatos en AdFlux.

Este módulo define los DTOs utilizados para transferir datos
de candidatos entre la capa de presentación y la capa de lógica de negocio.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime

from .base_dto import BaseDTO


@dataclass
class CandidateDTO(BaseDTO):
    """DTO para representar un candidato completo."""
    
    candidate_id: int
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    primary_skill: Optional[str] = None
    skills: Optional[List[str]] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_id: Optional[int] = None
    segment_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Validadores para los campos
    _validators: ClassVar[Dict[str, Any]] = {
        'email': lambda x: None if '@' in x else ValueError('Email inválido'),
        'years_experience': lambda x: None if x is None or x >= 0 else ValueError('Años de experiencia deben ser positivos'),
    }
    
    @classmethod
    def from_model(cls, model: Any) -> 'CandidateDTO':
        """
        Crea un DTO a partir de un modelo de candidato.
        
        Args:
            model: Modelo de candidato
            
        Returns:
            Instancia del DTO
        """
        dto = super().from_model(model)
        
        # Convertir skills de string a lista si es necesario
        if hasattr(model, 'skills') and isinstance(model.skills, str):
            dto.skills = model.skills.split(',') if model.skills else []
        
        return dto


@dataclass
class CandidateListDTO(BaseDTO):
    """DTO para representar una lista paginada de candidatos."""
    
    candidates: List[CandidateDTO]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    @classmethod
    def from_query_result(cls, candidates: List[Any], page: int, per_page: int, total: int) -> 'CandidateListDTO':
        """
        Crea un DTO a partir de resultados de consulta paginados.
        
        Args:
            candidates: Lista de modelos de candidatos
            page: Número de página actual
            per_page: Número de elementos por página
            total: Número total de candidatos
            
        Returns:
            Instancia del DTO
        """
        candidate_dtos = [CandidateDTO.from_model(c) for c in candidates]
        total_pages = (total + per_page - 1) // per_page  # Redondeo hacia arriba
        
        return cls(
            candidates=candidate_dtos,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )


@dataclass
class CandidateCreateDTO(BaseDTO):
    """DTO para crear un nuevo candidato."""
    
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    primary_skill: Optional[str] = None
    skills: Optional[List[str]] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_id: Optional[int] = None
    
    # Validadores para los campos
    _validators: ClassVar[Dict[str, Any]] = {
        'name': lambda x: None if x and len(x) >= 2 else ValueError('Nombre debe tener al menos 2 caracteres'),
        'email': lambda x: None if '@' in x else ValueError('Email inválido'),
        'years_experience': lambda x: None if x is None or x >= 0 else ValueError('Años de experiencia deben ser positivos'),
    }
    
    def to_model(self, model_class: Any) -> Any:
        """
        Convierte el DTO a un modelo de candidato.
        
        Args:
            model_class: Clase del modelo de candidato
            
        Returns:
            Instancia del modelo
        """
        model = super().to_model(model_class)
        
        # Convertir skills de lista a string si es necesario
        if hasattr(self, 'skills') and self.skills is not None:
            model.skills = ','.join(self.skills)
        
        return model


@dataclass
class CandidateUpdateDTO(BaseDTO):
    """DTO para actualizar un candidato existente."""
    
    candidate_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    primary_skill: Optional[str] = None
    skills: Optional[List[str]] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_id: Optional[int] = None
    segment_id: Optional[int] = None
    
    # Validadores para los campos
    _validators: ClassVar[Dict[str, Any]] = {
        'name': lambda x: None if x is None or len(x) >= 2 else ValueError('Nombre debe tener al menos 2 caracteres'),
        'email': lambda x: None if x is None or '@' in x else ValueError('Email inválido'),
        'years_experience': lambda x: None if x is None or x >= 0 else ValueError('Años de experiencia deben ser positivos'),
    }
    
    def update_model(self, model: Any) -> Any:
        """
        Actualiza un modelo de candidato con los datos del DTO.
        
        Args:
            model: Modelo de candidato a actualizar
            
        Returns:
            Modelo actualizado
        """
        # Actualizar solo los campos que no son None
        for field_name, field_value in self.to_dict().items():
            if field_value is not None and hasattr(model, field_name):
                # Manejar skills de forma especial
                if field_name == 'skills' and isinstance(field_value, list):
                    setattr(model, field_name, ','.join(field_value))
                else:
                    setattr(model, field_name, field_value)
        
        return model
