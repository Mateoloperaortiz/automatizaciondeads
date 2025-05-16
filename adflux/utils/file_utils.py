"""
Utilidades para manipulación de archivos en AdFlux.

Este módulo proporciona funciones para trabajar con archivos y determinar
sus propiedades.
"""

import os
import mimetypes
import uuid
import imghdr
from typing import Optional, Tuple


def get_file_extension(filename: str) -> str:
    """
    Obtiene la extensión de un archivo.
    
    Args:
        filename: Nombre del archivo.
        
    Returns:
        Extensión del archivo sin el punto.
    """
    return os.path.splitext(filename)[1].lower().lstrip('.')


def get_file_size(file_path: str) -> int:
    """
    Obtiene el tamaño de un archivo en bytes.
    
    Args:
        file_path: Ruta al archivo.
        
    Returns:
        Tamaño del archivo en bytes.
    """
    return os.path.getsize(file_path)


def get_file_mime_type(filename: str) -> str:
    """
    Obtiene el tipo MIME de un archivo basado en su extensión.
    
    Args:
        filename: Nombre del archivo.
        
    Returns:
        Tipo MIME del archivo.
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def is_valid_image(file_path: str) -> bool:
    """
    Verifica si un archivo es una imagen válida.
    
    Args:
        file_path: Ruta al archivo.
        
    Returns:
        True si el archivo es una imagen válida, False en caso contrario.
    """
    if not os.path.isfile(file_path):
        return False
    
    image_type = imghdr.what(file_path)
    return image_type is not None


def is_valid_document(file_path: str, allowed_extensions: Optional[Tuple[str, ...]] = None) -> bool:
    """
    Verifica si un archivo es un documento válido.
    
    Args:
        file_path: Ruta al archivo.
        allowed_extensions: Tupla de extensiones permitidas (sin el punto).
                           Si es None, se permiten pdf, doc, docx, txt.
        
    Returns:
        True si el archivo es un documento válido, False en caso contrario.
    """
    if allowed_extensions is None:
        allowed_extensions = ('pdf', 'doc', 'docx', 'txt', 'rtf', 'odt')
    
    if not os.path.isfile(file_path):
        return False
    
    extension = get_file_extension(file_path)
    return extension.lower() in allowed_extensions


def generate_unique_filename(original_filename: str) -> str:
    """
    Genera un nombre de archivo único basado en UUID.
    
    Args:
        original_filename: Nombre original del archivo.
        
    Returns:
        Nombre de archivo único.
    """
    extension = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    
    if extension:
        return f"{unique_id}.{extension}"
    else:
        return unique_id
