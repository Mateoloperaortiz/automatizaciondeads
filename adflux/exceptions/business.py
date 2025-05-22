"""
Excepciones de negocio para AdFlux.

Este módulo define las excepciones relacionadas con la lógica de negocio utilizadas en AdFlux.
"""

from typing import Dict, Any, Optional, List, Union

from .base import AdFluxError


class BusinessError(AdFluxError):
    """Excepción base para errores de lógica de negocio."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa una nueva excepción de lógica de negocio.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
        """
        super().__init__(message, code, status_code, details, cause)


class ResourceNotFoundError(BusinessError):
    """Excepción para recursos no encontrados."""

    def __init__(
        self,
        message: str = "Recurso no encontrado",
        code: Optional[str] = None,
        status_code: int = 404,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        resource: Optional[str] = None,
        resource_id: Optional[Union[str, int]] = None
    ):
        """
        Inicializa una nueva excepción de recurso no encontrado.

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
            if message == "Recurso no encontrado":
                message = f"{resource or 'Recurso'} con ID {resource_id} no encontrado"
        super().__init__(message, code, status_code, details, cause)
        self.resource = resource
        self.resource_id = resource_id


class ResourceAlreadyExistsError(BusinessError):
    """Excepción para recursos que ya existen."""

    def __init__(
        self,
        message: str = "El recurso ya existe",
        code: Optional[str] = None,
        status_code: int = 409,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        resource: Optional[str] = None,
        resource_id: Optional[Union[str, int]] = None
    ):
        """
        Inicializa una nueva excepción de recurso que ya existe.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 409).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            resource: Tipo de recurso que ya existe.
            resource_id: Identificador del recurso que ya existe.
        """
        details = details or {}
        if resource:
            details["resource"] = resource
        if resource_id:
            details["resource_id"] = resource_id
            if message == "El recurso ya existe":
                message = f"{resource or 'Recurso'} con ID {resource_id} ya existe"
        super().__init__(message, code, status_code, details, cause)
        self.resource = resource
        self.resource_id = resource_id


class ResourceInUseError(BusinessError):
    """Excepción para recursos en uso."""

    def __init__(
        self,
        message: str = "El recurso está en uso",
        code: Optional[str] = None,
        status_code: int = 409,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        resource: Optional[str] = None,
        resource_id: Optional[Union[str, int]] = None,
        used_by: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de recurso en uso.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 409).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            resource: Tipo de recurso en uso.
            resource_id: Identificador del recurso en uso.
            used_by: Entidad que está utilizando el recurso.
        """
        details = details or {}
        if resource:
            details["resource"] = resource
        if resource_id:
            details["resource_id"] = resource_id
        if used_by:
            details["used_by"] = used_by
        super().__init__(message, code, status_code, details, cause)
        self.resource = resource
        self.resource_id = resource_id
        self.used_by = used_by


class OperationNotAllowedError(BusinessError):
    """Excepción para operaciones no permitidas."""

    def __init__(
        self,
        message: str = "Operación no permitida",
        code: Optional[str] = None,
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        operation: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de operación no permitida.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 403).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            operation: Operación no permitida.
            reason: Razón por la que la operación no está permitida.
        """
        details = details or {}
        if operation:
            details["operation"] = operation
        if reason:
            details["reason"] = reason
        super().__init__(message, code, status_code, details, cause)
        self.operation = operation
        self.reason = reason


class LimitExceededError(BusinessError):
    """Excepción para límites excedidos."""

    def __init__(
        self,
        message: str = "Límite excedido",
        code: Optional[str] = None,
        status_code: int = 429,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        limit: Optional[int] = None,
        current: Optional[int] = None,
        resource: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de límite excedido.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 429).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            limit: Valor límite.
            current: Valor actual.
            resource: Recurso para el que se excedió el límite.
        """
        details = details or {}
        if limit is not None:
            details["limit"] = limit
        if current is not None:
            details["current"] = current
        if resource:
            details["resource"] = resource
        super().__init__(message, code, status_code, details, cause)
        self.limit = limit
        self.current = current
        self.resource = resource
