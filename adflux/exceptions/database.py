"""
Excepciones relacionadas con la base de datos para AdFlux.

Este módulo define las excepciones relacionadas con la base de datos utilizadas en AdFlux.
"""

from typing import Dict, Any, Optional, List, Union

from .base import AdFluxError


class DatabaseError(AdFluxError):
    """Excepción base para errores de base de datos."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa una nueva excepción de base de datos.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
        """
        super().__init__(message, code, status_code, details, cause)


class DatabaseConnectionError(DatabaseError):
    """Excepción para errores de conexión a la base de datos."""

    def __init__(
        self,
        message: str = "Error de conexión a la base de datos",
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa una nueva excepción de conexión a la base de datos.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
        """
        super().__init__(message, code, status_code, details, cause)


class DatabaseQueryError(DatabaseError):
    """Excepción para errores en consultas a la base de datos."""

    def __init__(
        self,
        message: str = "Error en consulta a la base de datos",
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        query: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de consulta a la base de datos.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            query: Consulta que generó el error.
        """
        details = details or {}
        if query:
            details["query"] = query
        super().__init__(message, code, status_code, details, cause)
        self.query = query


class DatabaseIntegrityError(DatabaseError):
    """Excepción para errores de integridad en la base de datos."""

    def __init__(
        self,
        message: str = "Error de integridad en la base de datos",
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa una nueva excepción de integridad en la base de datos.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
        """
        super().__init__(message, code, status_code, details, cause)


class DatabaseTimeoutError(DatabaseError):
    """Excepción para errores de tiempo de espera en la base de datos."""

    def __init__(
        self,
        message: str = "Tiempo de espera agotado en la base de datos",
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        timeout: Optional[float] = None
    ):
        """
        Inicializa una nueva excepción de tiempo de espera en la base de datos.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            timeout: Tiempo de espera en segundos.
        """
        details = details or {}
        if timeout:
            details["timeout"] = timeout
        super().__init__(message, code, status_code, details, cause)
        self.timeout = timeout


class DatabaseNotFoundError(DatabaseError):
    """Excepción para errores de recurso no encontrado en la base de datos."""

    def __init__(
        self,
        message: str = "Recurso no encontrado en la base de datos",
        code: Optional[str] = None,
        status_code: int = 404,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        resource: Optional[str] = None,
        resource_id: Optional[Union[str, int]] = None
    ):
        """
        Inicializa una nueva excepción de recurso no encontrado en la base de datos.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 404).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            resource: Tipo de recurso no encontrado.
            resource_id: Identificador del recurso no encontrado.
        """
        details = details or {}
        if resource:
            details["resource"] = resource
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(message, code, status_code, details, cause)
        self.resource = resource
        self.resource_id = resource_id
