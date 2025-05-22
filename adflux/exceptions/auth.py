"""
Excepciones de autenticación y autorización para AdFlux.

Este módulo define las excepciones relacionadas con la autenticación y autorización utilizadas en AdFlux.
"""

from typing import Dict, Any, Optional, List, Union

from .base import AdFluxError


class AuthenticationError(AdFluxError):
    """Excepción base para errores de autenticación."""

    def __init__(
        self,
        message: str = "Error de autenticación",
        code: Optional[str] = None,
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa una nueva excepción de autenticación.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 401).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
        """
        super().__init__(message, code, status_code, details, cause)


class AuthorizationError(AdFluxError):
    """Excepción base para errores de autorización."""

    def __init__(
        self,
        message: str = "Error de autorización",
        code: Optional[str] = None,
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa una nueva excepción de autorización.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 403).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
        """
        super().__init__(message, code, status_code, details, cause)


class TokenExpiredError(AuthenticationError):
    """Excepción para tokens expirados."""

    def __init__(
        self,
        message: str = "Token expirado",
        code: Optional[str] = None,
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        token_type: Optional[str] = None,
        expiry_time: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de token expirado.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 401).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            token_type: Tipo de token expirado.
            expiry_time: Tiempo de expiración del token.
        """
        details = details or {}
        if token_type:
            details["token_type"] = token_type
        if expiry_time:
            details["expiry_time"] = expiry_time
        super().__init__(message, code, status_code, details, cause)
        self.token_type = token_type
        self.expiry_time = expiry_time


class InvalidTokenError(AuthenticationError):
    """Excepción para tokens inválidos."""

    def __init__(
        self,
        message: str = "Token inválido",
        code: Optional[str] = None,
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        token_type: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de token inválido.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 401).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            token_type: Tipo de token inválido.
            reason: Razón por la que el token es inválido.
        """
        details = details or {}
        if token_type:
            details["token_type"] = token_type
        if reason:
            details["reason"] = reason
        super().__init__(message, code, status_code, details, cause)
        self.token_type = token_type
        self.reason = reason


class InvalidCredentialsError(AuthenticationError):
    """Excepción para credenciales inválidas."""

    def __init__(
        self,
        message: str = "Credenciales inválidas",
        code: Optional[str] = None,
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa una nueva excepción de credenciales inválidas.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 401).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
        """
        super().__init__(message, code, status_code, details, cause)


class AccountLockedError(AuthenticationError):
    """Excepción para cuentas bloqueadas."""

    def __init__(
        self,
        message: str = "Cuenta bloqueada",
        code: Optional[str] = None,
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        reason: Optional[str] = None,
        unlock_time: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de cuenta bloqueada.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 401).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            reason: Razón por la que la cuenta está bloqueada.
            unlock_time: Tiempo en el que la cuenta será desbloqueada.
        """
        details = details or {}
        if reason:
            details["reason"] = reason
        if unlock_time:
            details["unlock_time"] = unlock_time
        super().__init__(message, code, status_code, details, cause)
        self.reason = reason
        self.unlock_time = unlock_time
