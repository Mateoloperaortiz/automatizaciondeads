"""
Utilidades para paginación eficiente.

Este módulo proporciona funciones y clases para implementar paginación eficiente,
incluyendo keyset pagination para consultas de gran volumen.
"""

from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, Generic, Callable
from dataclasses import dataclass
from sqlalchemy import desc, asc
from sqlalchemy.orm import Query
from flask import url_for, request

from ..models import db


T = TypeVar('T')


@dataclass
class PaginationResult(Generic[T]):
    """
    Resultado de paginación.
    
    Contiene los elementos de la página actual y metadatos de paginación.
    """
    
    items: List[T]
    total: Optional[int]
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int]
    prev_page: Optional[int]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el resultado de paginación a un diccionario.
        
        Returns:
            Diccionario con elementos y metadatos de paginación
        """
        return {
            "items": self.items,
            "pagination": {
                "total": self.total,
                "page": self.page,
                "per_page": self.per_page,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
                "next_page": self.next_page,
                "prev_page": self.prev_page,
                "next_cursor": self.next_cursor,
                "prev_cursor": self.prev_cursor
            }
        }


def paginate_query(
    query: Query,
    page: int = 1,
    per_page: int = 20,
    count_total: bool = True
) -> PaginationResult:
    """
    Pagina una consulta SQLAlchemy utilizando offset pagination.
    
    Args:
        query: Consulta SQLAlchemy
        page: Número de página (1-indexed)
        per_page: Elementos por página
        count_total: Si se debe contar el total de elementos
        
    Returns:
        Resultado de paginación
    """
    # Validar parámetros
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    
    # Calcular total si es necesario
    total = None
    if count_total:
        total = query.count()
    
    # Aplicar paginación
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    # Determinar si hay páginas anterior y siguiente
    has_next = len(items) == per_page
    has_prev = page > 1
    
    # Calcular números de página anterior y siguiente
    next_page = page + 1 if has_next else None
    prev_page = page - 1 if has_prev else None
    
    return PaginationResult(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        has_next=has_next,
        has_prev=has_prev,
        next_page=next_page,
        prev_page=prev_page,
        next_cursor=None,
        prev_cursor=None
    )


def keyset_paginate(
    query: Query,
    column,
    cursor: Optional[str] = None,
    per_page: int = 20,
    ascending: bool = False,
    cursor_converter: Optional[Callable[[str], Any]] = None
) -> PaginationResult:
    """
    Pagina una consulta SQLAlchemy utilizando keyset pagination.
    
    Args:
        query: Consulta SQLAlchemy
        column: Columna para ordenar y paginar
        cursor: Cursor para la paginación
        per_page: Elementos por página
        ascending: Si el orden es ascendente
        cursor_converter: Función para convertir el cursor a un valor
        
    Returns:
        Resultado de paginación
    """
    # Validar parámetros
    if per_page < 1:
        per_page = 20
    
    # Determinar dirección de ordenamiento
    direction = asc if ascending else desc
    
    # Clonar la consulta para no modificar la original
    base_query = query
    
    # Aplicar filtro de cursor si existe
    if cursor and cursor != "null" and cursor != "undefined":
        cursor_value = cursor
        if cursor_converter:
            cursor_value = cursor_converter(cursor)
        
        if ascending:
            query = query.filter(column > cursor_value)
        else:
            query = query.filter(column < cursor_value)
    
    # Aplicar ordenamiento
    query = query.order_by(direction(column))
    
    # Obtener elementos
    items = query.limit(per_page + 1).all()
    
    # Determinar si hay página siguiente
    has_next = len(items) > per_page
    if has_next:
        items = items[:-1]  # Eliminar elemento extra
    
    # Determinar cursores
    next_cursor = None
    prev_cursor = None
    
    if has_next and items:
        next_cursor = str(getattr(items[-1], column.name))
    
    if cursor and cursor != "null" and cursor != "undefined":
        # Para la página anterior, necesitamos hacer una consulta adicional
        cursor_value = cursor
        if cursor_converter:
            cursor_value = cursor_converter(cursor)
        
        prev_query = base_query
        if ascending:
            prev_query = prev_query.filter(column < cursor_value)
            prev_query = prev_query.order_by(desc(column))
        else:
            prev_query = prev_query.filter(column > cursor_value)
            prev_query = prev_query.order_by(asc(column))
        
        prev_items = prev_query.limit(per_page).all()
        has_prev = len(prev_items) > 0
        
        if has_prev:
            prev_cursor = str(getattr(prev_items[0], column.name))
    else:
        has_prev = False
    
    return PaginationResult(
        items=items,
        total=None,  # No se calcula el total en keyset pagination
        page=1,  # No hay concepto de "página" en keyset pagination
        per_page=per_page,
        has_next=has_next,
        has_prev=has_prev,
        next_page=None,  # No hay concepto de "página siguiente" en keyset pagination
        prev_page=None,  # No hay concepto de "página anterior" en keyset pagination
        next_cursor=next_cursor,
        prev_cursor=prev_cursor
    )


def get_pagination_links(
    endpoint: str,
    pagination: PaginationResult,
    **kwargs
) -> Dict[str, Optional[str]]:
    """
    Genera enlaces de paginación para una API RESTful.
    
    Args:
        endpoint: Nombre del endpoint de Flask
        pagination: Resultado de paginación
        **kwargs: Argumentos adicionales para url_for
        
    Returns:
        Diccionario con enlaces de paginación
    """
    links = {}
    
    # Enlace a la primera página
    links["first"] = url_for(
        endpoint,
        page=1,
        per_page=pagination.per_page,
        **kwargs,
        _external=True
    )
    
    # Enlace a la página anterior
    if pagination.has_prev:
        if pagination.prev_cursor:
            links["prev"] = url_for(
                endpoint,
                cursor=pagination.prev_cursor,
                per_page=pagination.per_page,
                **kwargs,
                _external=True
            )
        elif pagination.prev_page:
            links["prev"] = url_for(
                endpoint,
                page=pagination.prev_page,
                per_page=pagination.per_page,
                **kwargs,
                _external=True
            )
    else:
        links["prev"] = None
    
    # Enlace a la página actual
    if pagination.next_cursor or pagination.prev_cursor:
        # Keyset pagination
        current_cursor = request.args.get("cursor")
        links["self"] = url_for(
            endpoint,
            cursor=current_cursor,
            per_page=pagination.per_page,
            **kwargs,
            _external=True
        )
    else:
        # Offset pagination
        links["self"] = url_for(
            endpoint,
            page=pagination.page,
            per_page=pagination.per_page,
            **kwargs,
            _external=True
        )
    
    # Enlace a la página siguiente
    if pagination.has_next:
        if pagination.next_cursor:
            links["next"] = url_for(
                endpoint,
                cursor=pagination.next_cursor,
                per_page=pagination.per_page,
                **kwargs,
                _external=True
            )
        elif pagination.next_page:
            links["next"] = url_for(
                endpoint,
                page=pagination.next_page,
                per_page=pagination.per_page,
                **kwargs,
                _external=True
            )
    else:
        links["next"] = None
    
    # Enlace a la última página (solo para offset pagination)
    if pagination.total is not None:
        last_page = (pagination.total - 1) // pagination.per_page + 1
        links["last"] = url_for(
            endpoint,
            page=last_page,
            per_page=pagination.per_page,
            **kwargs,
            _external=True
        )
    else:
        links["last"] = None
    
    return links
