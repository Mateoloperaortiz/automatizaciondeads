"""
Modelos de validación para campañas.

Este módulo proporciona modelos de validación para campañas publicitarias.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import Field, validator, root_validator

from .base import BaseModel
from .validators import (
    validate_non_empty_string,
    validate_positive_number,
    validate_url,
    validate_date,
    validate_enum_value,
)


class CampaignStatus(str, Enum):
    """Estados posibles para una campaña."""
    
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"
    COMPLETED = "COMPLETED"


class CampaignObjective(str, Enum):
    """Objetivos posibles para una campaña."""
    
    AWARENESS = "AWARENESS"
    CONSIDERATION = "CONSIDERATION"
    CONVERSION = "CONVERSION"
    LEAD_GENERATION = "LEAD_GENERATION"
    TRAFFIC = "TRAFFIC"
    APP_INSTALLS = "APP_INSTALLS"
    VIDEO_VIEWS = "VIDEO_VIEWS"
    MESSAGES = "MESSAGES"
    ENGAGEMENT = "ENGAGEMENT"
    REACH = "REACH"


class CampaignPlatform(str, Enum):
    """Plataformas publicitarias soportadas."""
    
    META = "META"
    GOOGLE = "GOOGLE"
    TIKTOK = "TIKTOK"
    SNAPCHAT = "SNAPCHAT"
    LINKEDIN = "LINKEDIN"
    TWITTER = "TWITTER"


class CampaignBase(BaseModel):
    """Modelo base para campañas."""
    
    name: str = Field(..., min_length=1, max_length=100)
    objective: CampaignObjective
    status: CampaignStatus = CampaignStatus.DRAFT
    platform: CampaignPlatform
    daily_budget: Optional[float] = Field(None, ge=0)
    lifetime_budget: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    job_id: Optional[int] = None
    segment_id: Optional[int] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Valida que el nombre no esté vacío."""
        return validate_non_empty_string(v)
    
    @validator('daily_budget', 'lifetime_budget')
    def validate_budget(cls, v):
        """Valida que el presupuesto sea positivo."""
        return validate_positive_number(v)
    
    @root_validator
    def validate_budget_types(cls, values):
        """Valida que se especifique al menos un tipo de presupuesto."""
        daily_budget = values.get('daily_budget')
        lifetime_budget = values.get('lifetime_budget')
        
        if daily_budget is None and lifetime_budget is None:
            raise ValueError("Debe especificar al menos un tipo de presupuesto (diario o total)")
        
        return values
    
    @root_validator
    def validate_dates(cls, values):
        """Valida que la fecha de inicio sea anterior a la fecha de fin."""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        return values


class CampaignCreate(CampaignBase):
    """Modelo para crear una campaña."""
    
    targeting: Optional[Dict[str, Any]] = Field(None)
    
    @validator('targeting')
    def validate_targeting(cls, v):
        """Valida que el targeting sea un diccionario válido."""
        if v is None:
            return {}
        return v


class CampaignUpdate(BaseModel):
    """Modelo para actualizar una campaña."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    objective: Optional[CampaignObjective] = None
    status: Optional[CampaignStatus] = None
    platform: Optional[CampaignPlatform] = None
    daily_budget: Optional[float] = Field(None, ge=0)
    lifetime_budget: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    job_id: Optional[int] = None
    segment_id: Optional[int] = None
    targeting: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Valida que el nombre no esté vacío."""
        if v is None:
            return None
        return validate_non_empty_string(v)
    
    @validator('daily_budget', 'lifetime_budget')
    def validate_budget(cls, v):
        """Valida que el presupuesto sea positivo."""
        return validate_positive_number(v)
    
    @root_validator
    def validate_dates(cls, values):
        """Valida que la fecha de inicio sea anterior a la fecha de fin."""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        return values


class CampaignResponse(CampaignBase):
    """Modelo para respuesta de campaña."""
    
    id: int
    external_id: Optional[str] = None
    targeting: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        """Configuración para el modelo de respuesta."""
        
        orm_mode = True
