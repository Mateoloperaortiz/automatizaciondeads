"""
Excepciones relacionadas con archivos para AdFlux.

Este módulo define las excepciones relacionadas con operaciones de archivos utilizadas en AdFlux.
"""

from typing import Dict, Any, Optional, List, Union
import os

from .base import AdFluxError


class FileError(AdFluxError):
    """Excepción base para errores relacionados con archivos."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de archivo.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            file_path: Ruta del archivo que generó el error.
        """
        details = details or {}
        if file_path:
            details["file_path"] = file_path
        super().__init__(message, code, status_code, details, cause)
        self.file_path = file_path


class FileNotFoundError(FileError):
    """Excepción para archivos no encontrados."""

    def __init__(
        self,
        message: str = "Archivo no encontrado",
        code: Optional[str] = None,
        status_code: int = 404,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de archivo no encontrado.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 404).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            file_path: Ruta del archivo no encontrado.
        """
        if file_path and message == "Archivo no encontrado":
            message = f"Archivo no encontrado: {file_path}"
        super().__init__(message, code, status_code, details, cause, file_path)


class FilePermissionError(FileError):
    """Excepción para errores de permisos de archivos."""

    def __init__(
        self,
        message: str = "Permiso denegado para el archivo",
        code: Optional[str] = None,
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None,
        permission_type: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de permiso de archivo.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 403).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            file_path: Ruta del archivo con error de permisos.
            permission_type: Tipo de permiso requerido (lectura, escritura, ejecución).
        """
        details = details or {}
        if permission_type:
            details["permission_type"] = permission_type
        if file_path and permission_type and message == "Permiso denegado para el archivo":
            message = f"Permiso de {permission_type} denegado para el archivo: {file_path}"
        super().__init__(message, code, status_code, details, cause, file_path)
        self.permission_type = permission_type


class FileFormatError(FileError):
    """Excepción para errores de formato de archivos."""

    def __init__(
        self,
        message: str = "Formato de archivo inválido",
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None,
        expected_format: Optional[str] = None,
        actual_format: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de formato de archivo.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            file_path: Ruta del archivo con formato inválido.
            expected_format: Formato esperado.
            actual_format: Formato actual.
        """
        details = details or {}
        if expected_format:
            details["expected_format"] = expected_format
        if actual_format:
            details["actual_format"] = actual_format
        super().__init__(message, code, status_code, details, cause, file_path)
        self.expected_format = expected_format
        self.actual_format = actual_format


class FileSizeError(FileError):
    """Excepción para errores de tamaño de archivos."""

    def __init__(
        self,
        message: str = "Tamaño de archivo inválido",
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None,
        max_size: Optional[int] = None,
        actual_size: Optional[int] = None
    ):
        """
        Inicializa una nueva excepción de tamaño de archivo.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 400).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            file_path: Ruta del archivo con tamaño inválido.
            max_size: Tamaño máximo permitido en bytes.
            actual_size: Tamaño actual en bytes.
        """
        details = details or {}
        if max_size is not None:
            details["max_size"] = max_size
        if actual_size is not None:
            details["actual_size"] = actual_size
        if file_path and max_size is not None and actual_size is not None and message == "Tamaño de archivo inválido":
            message = f"Tamaño de archivo excede el máximo permitido: {actual_size} > {max_size} bytes"
        super().__init__(message, code, status_code, details, cause, file_path)
        self.max_size = max_size
        self.actual_size = actual_size


class FileUploadError(FileError):
    """Excepción para errores de carga de archivos."""

    def __init__(
        self,
        message: str = "Error al cargar archivo",
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None,
        destination: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de carga de archivo.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            file_path: Ruta del archivo que se intentó cargar.
            destination: Destino de la carga.
        """
        details = details or {}
        if destination:
            details["destination"] = destination
        super().__init__(message, code, status_code, details, cause, file_path)
        self.destination = destination


class FileDownloadError(FileError):
    """Excepción para errores de descarga de archivos."""

    def __init__(
        self,
        message: str = "Error al descargar archivo",
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        file_path: Optional[str] = None,
        source: Optional[str] = None
    ):
        """
        Inicializa una nueva excepción de descarga de archivo.

        Args:
            message: Mensaje descriptivo del error.
            code: Código de error opcional.
            status_code: Código de estado HTTP (por defecto 500).
            details: Información adicional sobre el error.
            cause: Excepción original que causó el error.
            file_path: Ruta donde se intentó guardar el archivo.
            source: Origen de la descarga.
        """
        details = details or {}
        if source:
            details["source"] = source
        super().__init__(message, code, status_code, details, cause, file_path)
        self.source = source
