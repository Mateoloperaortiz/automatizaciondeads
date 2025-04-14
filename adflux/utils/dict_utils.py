"""
Utilidades para manejo de diccionarios en AdFlux.

Este módulo proporciona funciones para trabajar con diccionarios.
"""

from typing import Any, Dict, List, Optional, Tuple, Union, Callable


def merge_dicts(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    overwrite: bool = True
) -> Dict[str, Any]:
    """
    Combina dos diccionarios.
    
    Args:
        dict1: Primer diccionario
        dict2: Segundo diccionario
        overwrite: Si se deben sobrescribir los valores existentes
        
    Returns:
        Diccionario combinado
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursivamente combinar diccionarios anidados
            result[key] = merge_dicts(result[key], value, overwrite)
        elif key not in result or overwrite:
            # Añadir o sobrescribir valor
            result[key] = value
    
    return result


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = '',
    separator: str = '.'
) -> Dict[str, Any]:
    """
    Aplana un diccionario anidado.
    
    Args:
        d: Diccionario a aplanar
        parent_key: Clave padre para claves anidadas
        separator: Separador para claves anidadas
        
    Returns:
        Diccionario aplanado
    """
    items = []
    
    for key, value in d.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            # Recursivamente aplanar diccionarios anidados
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def unflatten_dict(
    d: Dict[str, Any],
    separator: str = '.'
) -> Dict[str, Any]:
    """
    Desaplana un diccionario aplanado.
    
    Args:
        d: Diccionario aplanado
        separator: Separador para claves anidadas
        
    Returns:
        Diccionario desaplanado
    """
    result = {}
    
    for key, value in d.items():
        parts = key.split(separator)
        
        # Navegar por el diccionario y crear estructura anidada
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Asignar valor a la última parte de la clave
        current[parts[-1]] = value
    
    return result


def filter_dict(
    d: Dict[str, Any],
    keys: List[str] = None,
    exclude_keys: List[str] = None,
    predicate: Callable[[str, Any], bool] = None
) -> Dict[str, Any]:
    """
    Filtra un diccionario según las claves o un predicado.
    
    Args:
        d: Diccionario a filtrar
        keys: Lista de claves a incluir (None = todas)
        exclude_keys: Lista de claves a excluir
        predicate: Función que recibe clave y valor y devuelve True si se debe incluir
        
    Returns:
        Diccionario filtrado
    """
    result = {}
    
    for key, value in d.items():
        # Verificar si la clave está en la lista de exclusión
        if exclude_keys and key in exclude_keys:
            continue
        
        # Verificar si la clave está en la lista de inclusión
        if keys and key not in keys:
            continue
        
        # Verificar predicado
        if predicate and not predicate(key, value):
            continue
        
        # Incluir clave y valor
        result[key] = value
    
    return result


def get_nested_value(
    d: Dict[str, Any],
    key_path: str,
    separator: str = '.',
    default: Any = None
) -> Any:
    """
    Obtiene un valor anidado de un diccionario.
    
    Args:
        d: Diccionario
        key_path: Ruta de la clave (por ejemplo, "user.address.city")
        separator: Separador para la ruta de la clave
        default: Valor por defecto si la clave no existe
        
    Returns:
        Valor anidado o valor por defecto si no existe
    """
    keys = key_path.split(separator)
    
    # Navegar por el diccionario
    current = d
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    
    return current


def set_nested_value(
    d: Dict[str, Any],
    key_path: str,
    value: Any,
    separator: str = '.',
    create_missing: bool = True
) -> Dict[str, Any]:
    """
    Establece un valor anidado en un diccionario.
    
    Args:
        d: Diccionario
        key_path: Ruta de la clave (por ejemplo, "user.address.city")
        value: Valor a establecer
        separator: Separador para la ruta de la clave
        create_missing: Si se deben crear claves intermedias que no existen
        
    Returns:
        Diccionario modificado
    """
    keys = key_path.split(separator)
    
    # Navegar por el diccionario
    current = d
    for key in keys[:-1]:
        if key not in current:
            if create_missing:
                current[key] = {}
            else:
                return d
        
        if not isinstance(current[key], dict):
            if create_missing:
                current[key] = {}
            else:
                return d
        
        current = current[key]
    
    # Establecer valor
    current[keys[-1]] = value
    
    return d
