"""
Clase base para DTOs en AdFlux.

Este módulo define la clase base para todos los DTOs (Data Transfer Objects)
utilizados en AdFlux.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, ClassVar, List, Optional
from datetime import datetime


@dataclass
class BaseDTO:
    """
    Clase base para todos los DTOs.
    
    Proporciona funcionalidad común para todos los DTOs,
    como conversión a diccionario y validación.
    """
    
    # Campos que deben ser excluidos al convertir a diccionario
    _exclude_fields: ClassVar[List[str]] = ['_exclude_fields', '_validators']
    
    # Validadores para los campos
    _validators: ClassVar[Dict[str, Any]] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el DTO a un diccionario.
        
        Returns:
            Diccionario con los datos del DTO
        """
        return {k: v for k, v in asdict(self).items() if k not in self._exclude_fields}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseDTO':
        """
        Crea un DTO a partir de un diccionario.
        
        Args:
            data: Diccionario con los datos
            
        Returns:
            Instancia del DTO
        """
        # Filtrar campos que no están en la clase
        valid_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_fields)
    
    def validate(self) -> List[str]:
        """
        Valida los datos del DTO.
        
        Returns:
            Lista de errores de validación (vacía si no hay errores)
        """
        errors = []
        
        # Aplicar validadores definidos en la clase
        for field_name, validator in self._validators.items():
            if hasattr(self, field_name):
                field_value = getattr(self, field_name)
                try:
                    validator(field_value)
                except ValueError as e:
                    errors.append(f"{field_name}: {str(e)}")
        
        return errors
    
    @classmethod
    def from_model(cls, model: Any) -> 'BaseDTO':
        """
        Crea un DTO a partir de un modelo de base de datos.
        
        Args:
            model: Modelo de base de datos
            
        Returns:
            Instancia del DTO
        """
        # Convertir modelo a diccionario
        model_dict = {}
        for column in model.__table__.columns:
            model_dict[column.name] = getattr(model, column.name)
        
        # Crear DTO a partir del diccionario
        return cls.from_dict(model_dict)
    
    def to_model(self, model_class: Any) -> Any:
        """
        Convierte el DTO a un modelo de base de datos.
        
        Args:
            model_class: Clase del modelo de base de datos
            
        Returns:
            Instancia del modelo
        """
        # Crear instancia del modelo
        model = model_class()
        
        # Copiar datos del DTO al modelo
        for field_name, field_value in self.to_dict().items():
            if hasattr(model, field_name):
                setattr(model, field_name, field_value)
        
        return model
