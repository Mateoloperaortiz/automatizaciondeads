"""
Utilidades para manipulación de listas en AdFlux.

Este módulo proporciona funciones para manipular y procesar listas.
"""

from typing import List, Dict, Any, Callable, TypeVar, Iterable, Optional, Tuple

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Divide una lista en trozos de tamaño específico.
    
    Args:
        lst: Lista a dividir.
        chunk_size: Tamaño de cada trozo.
        
    Returns:
        Lista de listas (trozos).
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[List[T]]) -> List[T]:
    """
    Aplana una lista de listas en una sola lista.
    
    Args:
        nested_list: Lista de listas a aplanar.
        
    Returns:
        Lista aplanada.
    """
    return [item for sublist in nested_list for item in sublist]


def unique_list(lst: List[T]) -> List[T]:
    """
    Elimina duplicados de una lista manteniendo el orden original.
    
    Args:
        lst: Lista con posibles duplicados.
        
    Returns:
        Lista sin duplicados.
    """
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]


def sort_list_by_key(lst: List[Dict[K, V]], key: K, reverse: bool = False) -> List[Dict[K, V]]:
    """
    Ordena una lista de diccionarios por una clave específica.
    
    Args:
        lst: Lista de diccionarios a ordenar.
        key: Clave por la que ordenar.
        reverse: Si se ordena en orden descendente.
        
    Returns:
        Lista ordenada.
    """
    return sorted(lst, key=lambda x: x.get(key, "") if isinstance(x.get(key, ""), str) else x.get(key, 0), reverse=reverse)


def filter_list_by_key(lst: List[Dict[K, V]], key: K, value: V) -> List[Dict[K, V]]:
    """
    Filtra una lista de diccionarios por una clave y valor específicos.
    
    Args:
        lst: Lista de diccionarios a filtrar.
        key: Clave por la que filtrar.
        value: Valor a buscar.
        
    Returns:
        Lista filtrada.
    """
    return [item for item in lst if item.get(key) == value]


def group_by(lst: List[Dict[K, V]], key: K) -> Dict[V, List[Dict[K, V]]]:
    """
    Agrupa una lista de diccionarios por una clave específica.
    
    Args:
        lst: Lista de diccionarios a agrupar.
        key: Clave por la que agrupar.
        
    Returns:
        Diccionario con grupos.
    """
    result = {}
    for item in lst:
        value = item.get(key)
        if value not in result:
            result[value] = []
        result[value].append(item)
    return result
