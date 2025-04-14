"""
Excepciones base para AdFlux.

Este módulo define las excepciones base utilizadas en AdFlux.
"""

from typing import Any, Dict, List, Optional, Union


class AdFluxError(Exception):
    """
    Excepción base para todos los errores de AdFlux.
    
    Esta excepción proporciona funcionalidad adicional como códigos de error,
    mensajes detallados y metadatos.
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Inicializa la excepción.
        
        Args:
            message: Mensaje de error
            code: Código de error interno
            status_code: Código de estado HTTP
            details: Detalles adicionales del error
            cause: Excepción que causó este error
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.cause = cause
        
        # Inicializar excepción base
        super().__init__(message)
    
    def __str__(self) -> str:
        """
        Devuelve una representación en cadena de la excepción.
        
        Returns:
            Representación en cadena
        """
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la excepción a un diccionario.
        
        Returns:
            Diccionario con información de la excepción
        """
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        
        if self.code:
            result["code"] = self.code
        
        if self.details:
            result["details"] = self.details
        
        return result


class AdFluxWarning(Warning):
    """
    Advertencia base para todas las advertencias de AdFlux.
    
    Esta advertencia proporciona funcionalidad adicional como códigos de advertencia,
    mensajes detallados y metadatos.
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa la advertencia.
        
        Args:
            message: Mensaje de advertencia
            code: Código de advertencia interno
            details: Detalles adicionales de la advertencia
        """
        self.message = message
        self.code = code
        self.details = details or {}
        
        # Inicializar advertencia base
        super().__init__(message)
    
    def __str__(self) -> str:
        """
        Devuelve una representación en cadena de la advertencia.
        
        Returns:
            Representación en cadena
        """
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la advertencia a un diccionario.
        
        Returns:
            Diccionario con información de la advertencia
        """
        result = {
            "warning": self.__class__.__name__,
            "message": self.message,
        }
        
        if self.code:
            result["code"] = self.code
        
        if self.details:
            result["details"] = self.details
        
        return result
