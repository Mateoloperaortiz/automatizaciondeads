"""
Excepciones de validación para AdFlux.

Este módulo define las excepciones de validación utilizadas en AdFlux.
"""

from typing import Dict, Any, Optional, List, Union

from .base import AdFluxError


class ValidationError(AdFluxError):
    """Excepción base para errores de validación."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Inicializa una nueva excepción de validación.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            errors: Lista de errores de validación.
        """
        details = details or {}
        if errors:
            details["errors"] = errors
        super().__init__(message, code, status_code, details)
        self.errors = errors


class InvalidInputError(ValidationError):
    """Excepción para entradas inválidas."""

    def __init__(
        self,
        message: str = "Entrada inválida",
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        """
        Inicializa una nueva excepción de entrada inválida.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            errors: Lista de errores de validación.
            field: Campo que contiene la entrada inválida.
            value: Valor inválido.
        """
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, code, status_code, details, errors)
        self.field = field
        self.value = value


class MissingRequiredFieldError(ValidationError):
    """Excepción para campos requeridos faltantes."""

    def __init__(
        self,
        message: str = "Campo requerido faltante",
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        field: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de campo requerido faltante.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            errors: Lista de errores de validación.
            field: Campo requerido faltante.
        """
        details = details or {}
        if field:
            details["field"] = field
            if message == "Campo requerido faltante":
                message = f"Campo requerido faltante: {field}"
        super().__init__(message, code, status_code, details, errors)
        self.field = field


class InvalidFormatError(ValidationError):
    """Excepción para formatos inválidos."""

    def __init__(
        self,
        message: str = "Formato inválido",
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_format: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de formato inválido.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            errors: Lista de errores de validación.
            field: Campo con formato inválido.
            value: Valor con formato inválido.
            expected_format: Formato esperado.
        """
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        if expected_format:
            details["expected_format"] = expected_format
        super().__init__(message, code, status_code, details, errors)
        self.field = field
        self.value = value
        self.expected_format = expected_format


class InvalidValueError(ValidationError):
    """Excepción para valores inválidos."""

    def __init__(
        self,
        message: str = "Valor inválido",
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        allowed_values: Optional[List[Any]] = None
    ):
        """
        Inicializa una nueva excepción de valor inválido.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            errors: Lista de errores de validación.
            field: Campo con valor inválido.
            value: Valor inválido.
            allowed_values: Valores permitidos.
        """
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        if allowed_values:
            details["allowed_values"] = [str(v) for v in allowed_values]
        super().__init__(message, code, status_code, details, errors)
        self.field = field
        self.value = value
        self.allowed_values = allowed_values


class InvalidTypeError(ValidationError):
    """Excepción para tipos inválidos."""

    def __init__(
        self,
        message: str = "Tipo inválido",
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_type: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de tipo inválido.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            errors: Lista de errores de validación.
            field: Campo con tipo inválido.
            value: Valor con tipo inválido.
            expected_type: Tipo esperado.
        """
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
            details["actual_type"] = type(value).__name__
        if expected_type:
            details["expected_type"] = expected_type
        super().__init__(message, code, status_code, details, errors)
        self.field = field
        self.value = value
        self.expected_type = expected_type
