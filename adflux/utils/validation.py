"""
Utilidades de validación para AdFlux.

Este módulo proporciona funciones para validar datos y estandarizar
las validaciones en toda la aplicación.
"""

import re
from typing import Dict, List, Any, Optional, Union, Tuple
from ..api.common.excepciones import ErrorValidacion


class ValidationUtils:
    """
    Clase de utilidades para validación de datos.
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida un formato de correo electrónico.
        
        Args:
            email: Correo electrónico a validar
                
        Returns:
            True si el formato es válido, False en caso contrario
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Valida que los campos requeridos estén presentes y no sean nulos.
        
        Args:
            data: Diccionario con datos a validar
            required_fields: Lista de nombres de campos requeridos
                
        Raises:
            ErrorValidacion: Si algún campo requerido falta o es nulo
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                missing_fields.append(field)
        
        if missing_fields:
            raise ErrorValidacion(
                mensaje=f"Faltan campos requeridos: {', '.join(missing_fields)}",
                errores={campo: ["Este campo es requerido."] for campo in missing_fields}
            )
    
    @staticmethod
    def validate_numeric_range(
        value: Union[int, float], 
        field_name: str, 
        min_value: Optional[Union[int, float]] = None, 
        max_value: Optional[Union[int, float]] = None
    ) -> None:
        """
        Valida que un valor numérico esté dentro de un rango.
        
        Args:
            value: Valor a validar
            field_name: Nombre del campo (para mensajes de error)
            min_value: Valor mínimo permitido (opcional)
            max_value: Valor máximo permitido (opcional)
                
        Raises:
            ErrorValidacion: Si el valor está fuera del rango especificado
        """
        errors = []
        
        if min_value is not None and value < min_value:
            errors.append(f"El valor debe ser mayor o igual a {min_value}.")
            
        if max_value is not None and value > max_value:
            errors.append(f"El valor debe ser menor o igual a {max_value}.")
            
        if errors:
            raise ErrorValidacion(
                mensaje=f"Valor fuera de rango para {field_name}",
                errores={field_name: errors}
            )
    
    @staticmethod
    def string_to_list(value: Union[str, List[str]], separator: str = ',') -> List[str]:
        """
        Convierte una cadena separada por delimitador a una lista.
        
        Args:
            value: Cadena a convertir o lista a mantener
            separator: Separador utilizado en la cadena
                
        Returns:
            Lista de cadenas
        """
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        return value if isinstance(value, list) else []
    
    @staticmethod
    def validate_pagination_params(page: int, per_page: int, max_per_page: int = 100) -> Tuple[int, int]:
        """
        Valida y normaliza parámetros de paginación.
        
        Args:
            page: Número de página solicitado
            per_page: Número de elementos por página solicitado
            max_per_page: Máximo número de elementos por página permitido
                
        Returns:
            Tupla con (page, per_page) normalizados
                
        Raises:
            ErrorValidacion: Si los parámetros están fuera de rangos permitidos
        """
        if page < 1:
            raise ErrorValidacion(
                mensaje="El número de página debe ser mayor o igual a 1",
                errores={"page": ["Debe ser mayor o igual a 1"]}
            )
            
        if per_page < 1:
            raise ErrorValidacion(
                mensaje="El número de elementos por página debe ser mayor o igual a 1",
                errores={"per_page": ["Debe ser mayor o igual a 1"]}
            )
            
        if per_page > max_per_page:
            per_page = max_per_page
        
        return page, per_page
