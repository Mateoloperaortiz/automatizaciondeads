"""
Definiciones de excepciones personalizadas para AdFlux.

Este módulo contiene las clases de excepción personalizadas utilizadas
en toda la aplicación para proporcionar un manejo de errores consistente.
"""

from typing import Dict, Any, Optional, List, Union


class AdFluxError(Exception):
    """Clase base para todas las excepciones de AdFlux."""

    def __init__(
        self, 
        mensaje: str, 
        codigo: Optional[int] = None,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de AdFlux.

        Args:
            mensaje: Mensaje descriptivo del error.
            codigo: Código de error opcional (por ejemplo, código HTTP).
            detalles: Información adicional sobre el error.
        """
        self.mensaje = mensaje
        self.codigo = codigo
        self.detalles = detalles or {}
        super().__init__(mensaje)


class ErrorBaseDatos(AdFluxError):
    """Excepción para errores relacionados con la base de datos."""

    def __init__(
        self, 
        mensaje: str, 
        excepcion_original: Optional[Exception] = None,
        codigo: int = 500,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de base de datos.

        Args:
            mensaje: Mensaje descriptivo del error.
            excepcion_original: Excepción original que causó el error.
            codigo: Código de error HTTP (por defecto 500).
            detalles: Información adicional sobre el error.
        """
        detalles = detalles or {}
        if excepcion_original:
            detalles["excepcion_original"] = str(excepcion_original)
        super().__init__(mensaje, codigo, detalles)
        self.excepcion_original = excepcion_original


class ErrorValidacion(AdFluxError):
    """Excepción para errores de validación de datos."""

    def __init__(
        self, 
        mensaje: str, 
        errores: Optional[Union[Dict[str, List[str]], str]] = None,
        codigo: int = 400,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de validación.

        Args:
            mensaje: Mensaje descriptivo del error.
            errores: Diccionario de errores de validación por campo o mensaje de error.
            codigo: Código de error HTTP (por defecto 400).
            detalles: Información adicional sobre el error.
        """
        detalles = detalles or {}
        if errores:
            detalles["errores"] = errores
        super().__init__(mensaje, codigo, detalles)
        self.errores = errores


class ErrorAutenticacion(AdFluxError):
    """Excepción para errores de autenticación."""

    def __init__(
        self, 
        mensaje: str = "No autorizado", 
        codigo: int = 401,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de autenticación.

        Args:
            mensaje: Mensaje descriptivo del error.
            codigo: Código de error HTTP (por defecto 401).
            detalles: Información adicional sobre el error.
        """
        super().__init__(mensaje, codigo, detalles)


class ErrorAutorizacion(AdFluxError):
    """Excepción para errores de autorización."""

    def __init__(
        self, 
        mensaje: str = "Acceso prohibido", 
        codigo: int = 403,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de autorización.

        Args:
            mensaje: Mensaje descriptivo del error.
            codigo: Código de error HTTP (por defecto 403).
            detalles: Información adicional sobre el error.
        """
        super().__init__(mensaje, codigo, detalles)


class ErrorRecursoNoEncontrado(AdFluxError):
    """Excepción para recursos no encontrados."""

    def __init__(
        self, 
        mensaje: str = "Recurso no encontrado", 
        recurso: Optional[str] = None,
        identificador: Optional[Any] = None,
        codigo: int = 404,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de recurso no encontrado.

        Args:
            mensaje: Mensaje descriptivo del error.
            recurso: Tipo de recurso no encontrado (ej. "Candidato").
            identificador: Identificador del recurso buscado.
            codigo: Código de error HTTP (por defecto 404).
            detalles: Información adicional sobre el error.
        """
        detalles = detalles or {}
        if recurso:
            detalles["recurso"] = recurso
        if identificador:
            detalles["identificador"] = identificador
            if not mensaje or mensaje == "Recurso no encontrado":
                mensaje = f"{recurso or 'Recurso'} con ID {identificador} no encontrado"
        super().__init__(mensaje, codigo, detalles)
        self.recurso = recurso
        self.identificador = identificador


class ErrorAPI(AdFluxError):
    """Excepción para errores en llamadas a APIs externas."""

    def __init__(
        self, 
        mensaje: str, 
        api: str,
        excepcion_original: Optional[Exception] = None,
        codigo: int = 500,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de API externa.

        Args:
            mensaje: Mensaje descriptivo del error.
            api: Nombre de la API que generó el error.
            excepcion_original: Excepción original que causó el error.
            codigo: Código de error HTTP (por defecto 500).
            detalles: Información adicional sobre el error.
        """
        detalles = detalles or {}
        detalles["api"] = api
        if excepcion_original:
            detalles["excepcion_original"] = str(excepcion_original)
        super().__init__(mensaje, codigo, detalles)
        self.api = api
        self.excepcion_original = excepcion_original


class ErrorTarea(AdFluxError):
    """Excepción para errores en tareas en segundo plano."""

    def __init__(
        self, 
        mensaje: str, 
        tarea_id: Optional[str] = None,
        excepcion_original: Optional[Exception] = None,
        codigo: int = 500,
        detalles: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa una nueva excepción de tarea en segundo plano.

        Args:
            mensaje: Mensaje descriptivo del error.
            tarea_id: Identificador de la tarea que falló.
            excepcion_original: Excepción original que causó el error.
            codigo: Código de error HTTP (por defecto 500).
            detalles: Información adicional sobre el error.
        """
        detalles = detalles or {}
        if tarea_id:
            detalles["tarea_id"] = tarea_id
        if excepcion_original:
            detalles["excepcion_original"] = str(excepcion_original)
        super().__init__(mensaje, codigo, detalles)
        self.tarea_id = tarea_id
        self.excepcion_original = excepcion_original
