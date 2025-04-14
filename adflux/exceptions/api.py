"""
Excepciones para APIs externas en AdFlux.

Este módulo define las excepciones relacionadas con APIs externas.
"""

from typing import Any, Dict, List, Optional, Union
from .base import AdFluxError


class APIError(AdFluxError):
    """
    Excepción base para errores relacionados con APIs externas.
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        api_name: Optional[str] = None,
        request_id: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa la excepción.
        
        Args:
            message: Mensaje de error
            code: Código de error interno
            status_code: Código de estado HTTP
            details: Detalles adicionales del error
            cause: Excepción que causó este error
            api_name: Nombre de la API externa
            request_id: ID de la solicitud
            response: Respuesta de la API
        """
        self.api_name = api_name
        self.request_id = request_id
        self.response = response
        
        # Añadir información de API a los detalles
        api_details = {}
        if api_name:
            api_details["api_name"] = api_name
        if request_id:
            api_details["request_id"] = request_id
        if response:
            api_details["response"] = response
        
        # Combinar detalles
        combined_details = details or {}
        if api_details:
            combined_details["api"] = api_details
        
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=combined_details,
            cause=cause
        )


class APIConnectionError(APIError):
    """
    Excepción para errores de conexión con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Error de conexión con la API externa",
        **kwargs
    ):
        super().__init__(
            message=message,
            code="api_connection_error",
            status_code=503,
            **kwargs
        )


class APITimeoutError(APIError):
    """
    Excepción para errores de tiempo de espera con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Tiempo de espera agotado para la API externa",
        **kwargs
    ):
        super().__init__(
            message=message,
            code="api_timeout_error",
            status_code=504,
            **kwargs
        )


class APIRateLimitError(APIError):
    """
    Excepción para errores de límite de tasa con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Límite de tasa excedido para la API externa",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if retry_after is not None:
            details["retry_after"] = retry_after
        
        kwargs["details"] = details
        
        super().__init__(
            message=message,
            code="api_rate_limit_error",
            status_code=429,
            **kwargs
        )


class APIAuthenticationError(APIError):
    """
    Excepción para errores de autenticación con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Error de autenticación con la API externa",
        **kwargs
    ):
        super().__init__(
            message=message,
            code="api_authentication_error",
            status_code=401,
            **kwargs
        )


class APIPermissionError(APIError):
    """
    Excepción para errores de permisos con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Permiso denegado para la API externa",
        **kwargs
    ):
        super().__init__(
            message=message,
            code="api_permission_error",
            status_code=403,
            **kwargs
        )


class APIResourceError(APIError):
    """
    Excepción para errores de recursos con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Error de recurso en la API externa",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        kwargs["details"] = details
        
        super().__init__(
            message=message,
            code="api_resource_error",
            status_code=400,
            **kwargs
        )


class APIValidationError(APIError):
    """
    Excepción para errores de validación con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Error de validación en la API externa",
        field_errors: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if field_errors:
            details["field_errors"] = field_errors
        
        kwargs["details"] = details
        
        super().__init__(
            message=message,
            code="api_validation_error",
            status_code=400,
            **kwargs
        )


class APINotFoundError(APIError):
    """
    Excepción para errores de recurso no encontrado con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Recurso no encontrado en la API externa",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        kwargs["details"] = details
        
        super().__init__(
            message=message,
            code="api_not_found_error",
            status_code=404,
            **kwargs
        )


class APIServerError(APIError):
    """
    Excepción para errores de servidor con APIs externas.
    """
    
    def __init__(
        self,
        message: str = "Error de servidor en la API externa",
        **kwargs
    ):
        super().__init__(
            message=message,
            code="api_server_error",
            status_code=502,
            **kwargs
        )
