"""
Módulo base para validación con Pydantic.

Este módulo proporciona la clase base para todos los modelos de validación
y la excepción de validación personalizada.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast
from datetime import datetime
from enum import Enum
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError as PydanticValidationError
from pydantic import Field, validator, root_validator


class ValidationError(Exception):
    """
    Excepción personalizada para errores de validación.
    
    Esta excepción encapsula los errores de validación de Pydantic
    y proporciona métodos para obtener los errores en diferentes formatos.
    """
    
    def __init__(self, pydantic_error: PydanticValidationError):
        """
        Inicializa la excepción con un error de validación de Pydantic.
        
        Args:
            pydantic_error: Error de validación de Pydantic
        """
        self.pydantic_error = pydantic_error
        super().__init__(str(pydantic_error))
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """
        Obtiene los errores de validación en formato de lista de diccionarios.
        
        Returns:
            Lista de errores de validación
        """
        return self.pydantic_error.errors()
    
    def get_error_messages(self) -> Dict[str, List[str]]:
        """
        Obtiene los mensajes de error agrupados por campo.
        
        Returns:
            Diccionario con los mensajes de error agrupados por campo
        """
        errors: Dict[str, List[str]] = {}
        
        for error in self.pydantic_error.errors():
            field = '.'.join(str(loc) for loc in error['loc'])
            message = error['msg']
            
            if field not in errors:
                errors[field] = []
            
            errors[field].append(message)
        
        return errors
    
    def get_flat_error_messages(self) -> List[str]:
        """
        Obtiene los mensajes de error en formato plano.
        
        Returns:
            Lista de mensajes de error
        """
        messages = []
        
        for error in self.pydantic_error.errors():
            field = '.'.join(str(loc) for loc in error['loc'])
            message = error['msg']
            messages.append(f"{field}: {message}")
        
        return messages


class BaseModel(PydanticBaseModel):
    """
    Clase base para todos los modelos de validación.
    
    Esta clase extiende la clase BaseModel de Pydantic y proporciona
    funcionalidad adicional para los modelos de validación de AdFlux.
    """
    
    class Config:
        """Configuración para los modelos de validación."""
        
        # Permitir nombres de campo extra (útil para ORM)
        orm_mode = True
        
        # Validar asignaciones de atributos
        validate_assignment = True
        
        # Permitir valores de enumeración por nombre o valor
        use_enum_values = True
        
        # Permitir campos extra (útil para APIs externas)
        extra = 'ignore'
        
        # Convertir camelCase a snake_case
        alias_generator = lambda string: ''.join(
            ['_' + char.lower() if char.isupper() else char for char in string]
        ).lstrip('_')
        
        # Permitir nombres de campo en camelCase
        allow_population_by_field_name = True
    
    @classmethod
    def validate_data(cls: Type['ModelT'], data: Dict[str, Any]) -> 'ModelT':
        """
        Valida datos y devuelve una instancia del modelo.
        
        Args:
            data: Datos a validar
            
        Returns:
            Instancia del modelo con los datos validados
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        try:
            return cls(**data)
        except PydanticValidationError as e:
            raise ValidationError(e)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            Diccionario con los datos del modelo
        """
        return self.dict(by_alias=False, exclude_unset=True)
    
    def to_orm(self, model_class: Type[Any]) -> Any:
        """
        Convierte el modelo a una instancia de ORM.
        
        Args:
            model_class: Clase del modelo ORM
            
        Returns:
            Instancia del modelo ORM
        """
        # Crear instancia del modelo ORM
        orm_instance = model_class()
        
        # Copiar datos del modelo al modelo ORM
        for field_name, field_value in self.to_dict().items():
            if hasattr(orm_instance, field_name):
                setattr(orm_instance, field_name, field_value)
        
        return orm_instance
    
    def update_orm(self, orm_instance: Any) -> Any:
        """
        Actualiza una instancia de ORM con los datos del modelo.
        
        Args:
            orm_instance: Instancia del modelo ORM
            
        Returns:
            Instancia del modelo ORM actualizada
        """
        # Copiar datos del modelo al modelo ORM
        for field_name, field_value in self.to_dict().items():
            if hasattr(orm_instance, field_name) and field_value is not None:
                setattr(orm_instance, field_name, field_value)
        
        return orm_instance


# Tipo genérico para modelos
ModelT = TypeVar('ModelT', bound=BaseModel)
