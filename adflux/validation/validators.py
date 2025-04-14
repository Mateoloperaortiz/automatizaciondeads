"""
Validadores comunes para AdFlux.

Este módulo proporciona funciones de validación comunes que pueden ser
utilizadas en diferentes modelos de validación.
"""

import re
from typing import Any, Optional, Pattern, Union
from datetime import datetime, date


# Patrones de validación
EMAIL_PATTERN: Pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_PATTERN: Pattern = re.compile(r'^\+?[0-9]{8,15}$')
URL_PATTERN: Pattern = re.compile(
    r'^(https?:\/\/)?'  # Protocolo
    r'(([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}|'  # Dominio
    r'localhost|'  # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
    r'(:\d+)?'  # Puerto
    r'(\/[-a-zA-Z0-9%_.~#+]*)*'  # Ruta
    r'(\?[;&a-zA-Z0-9%_.~+=-]*)?'  # Query string
    r'(\#[-a-zA-Z0-9_]*)?$'  # Fragmento
)


def validate_email(email: str) -> str:
    """
    Valida un correo electrónico.
    
    Args:
        email: Correo electrónico a validar
        
    Returns:
        Correo electrónico validado
        
    Raises:
        ValueError: Si el correo electrónico no es válido
    """
    if not email:
        raise ValueError("El correo electrónico no puede estar vacío")
    
    if not EMAIL_PATTERN.match(email):
        raise ValueError("El correo electrónico no es válido")
    
    return email


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """
    Valida un número de teléfono.
    
    Args:
        phone: Número de teléfono a validar
        
    Returns:
        Número de teléfono validado o None si es None
        
    Raises:
        ValueError: Si el número de teléfono no es válido
    """
    if phone is None:
        return None
    
    # Eliminar espacios y guiones
    phone = re.sub(r'[\s-]', '', phone)
    
    if not PHONE_PATTERN.match(phone):
        raise ValueError("El número de teléfono no es válido")
    
    return phone


def validate_url(url: Optional[str]) -> Optional[str]:
    """
    Valida una URL.
    
    Args:
        url: URL a validar
        
    Returns:
        URL validada o None si es None
        
    Raises:
        ValueError: Si la URL no es válida
    """
    if url is None:
        return None
    
    if not URL_PATTERN.match(url):
        raise ValueError("La URL no es válida")
    
    # Asegurarse de que la URL tenga protocolo
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url


def validate_date(date_value: Union[str, datetime, date, None]) -> Optional[date]:
    """
    Valida una fecha.
    
    Args:
        date_value: Fecha a validar
        
    Returns:
        Fecha validada o None si es None
        
    Raises:
        ValueError: Si la fecha no es válida
    """
    if date_value is None:
        return None
    
    if isinstance(date_value, datetime):
        return date_value.date()
    
    if isinstance(date_value, date):
        return date_value
    
    try:
        # Intentar parsear la fecha en formato ISO
        return datetime.fromisoformat(date_value).date()
    except (ValueError, TypeError):
        try:
            # Intentar parsear la fecha en formato DD/MM/YYYY
            day, month, year = date_value.split('/')
            return date(int(year), int(month), int(day))
        except (ValueError, TypeError):
            raise ValueError("La fecha no es válida")


def validate_positive_number(value: Union[int, float, None]) -> Optional[Union[int, float]]:
    """
    Valida que un número sea positivo.
    
    Args:
        value: Número a validar
        
    Returns:
        Número validado o None si es None
        
    Raises:
        ValueError: Si el número no es positivo
    """
    if value is None:
        return None
    
    if value < 0:
        raise ValueError("El número debe ser positivo")
    
    return value


def validate_non_empty_string(value: Optional[str]) -> Optional[str]:
    """
    Valida que una cadena no esté vacía.
    
    Args:
        value: Cadena a validar
        
    Returns:
        Cadena validada o None si es None
        
    Raises:
        ValueError: Si la cadena está vacía
    """
    if value is None:
        return None
    
    if not value.strip():
        raise ValueError("La cadena no puede estar vacía")
    
    return value.strip()


def validate_max_length(value: Optional[str], max_length: int) -> Optional[str]:
    """
    Valida que una cadena no exceda una longitud máxima.
    
    Args:
        value: Cadena a validar
        max_length: Longitud máxima permitida
        
    Returns:
        Cadena validada o None si es None
        
    Raises:
        ValueError: Si la cadena excede la longitud máxima
    """
    if value is None:
        return None
    
    if len(value) > max_length:
        raise ValueError(f"La cadena no puede exceder {max_length} caracteres")
    
    return value


def validate_enum_value(value: Any, enum_class: Any) -> Any:
    """
    Valida que un valor pertenezca a una enumeración.
    
    Args:
        value: Valor a validar
        enum_class: Clase de enumeración
        
    Returns:
        Valor validado
        
    Raises:
        ValueError: Si el valor no pertenece a la enumeración
    """
    if value is None:
        return None
    
    # Si el valor es una cadena, intentar convertirlo a un miembro de la enumeración
    if isinstance(value, str):
        try:
            return enum_class[value.upper()]
        except KeyError:
            pass
    
    # Si el valor es un miembro de la enumeración, devolverlo
    if isinstance(value, enum_class):
        return value
    
    # Si el valor es un valor de la enumeración, devolverlo
    try:
        return enum_class(value)
    except ValueError:
        pass
    
    # Si llegamos aquí, el valor no es válido
    valid_values = [e.name for e in enum_class]
    raise ValueError(f"El valor debe ser uno de: {', '.join(valid_values)}")


def validate_list_length(value: Optional[list], min_length: int = 0, max_length: Optional[int] = None) -> Optional[list]:
    """
    Valida que una lista tenga una longitud dentro de un rango.
    
    Args:
        value: Lista a validar
        min_length: Longitud mínima permitida
        max_length: Longitud máxima permitida
        
    Returns:
        Lista validada o None si es None
        
    Raises:
        ValueError: Si la lista no cumple con los requisitos de longitud
    """
    if value is None:
        return None
    
    if len(value) < min_length:
        raise ValueError(f"La lista debe tener al menos {min_length} elementos")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"La lista no puede tener más de {max_length} elementos")
    
    return value
