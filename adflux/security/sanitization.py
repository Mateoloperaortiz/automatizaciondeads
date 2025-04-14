"""
Sanitización de datos para AdFlux.

Este módulo proporciona funciones para sanitizar datos de entrada,
previniendo ataques como XSS, inyección SQL, etc.
"""

import re
import logging
import html
import unicodedata
from typing import Any, Dict, List, Optional, Union

import bleach
from markupsafe import Markup, escape


# Configurar logger
logger = logging.getLogger(__name__)


# Etiquetas HTML permitidas para contenido enriquecido
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code', 'div', 'em',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p',
    'pre', 'span', 'strong', 'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul'
]

# Atributos HTML permitidos
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'abbr': ['title'],
    'acronym': ['title'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'div': ['class'],
    'p': ['class'],
    'span': ['class'],
    'table': ['class', 'width'],
    'td': ['class', 'colspan', 'rowspan'],
    'th': ['class', 'colspan', 'rowspan', 'scope'],
    '*': ['class']
}

# Protocolos permitidos para URLs
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']


def sanitize_html(html_content: str, allowed_tags: Optional[List[str]] = None,
                 allowed_attributes: Optional[Dict[str, List[str]]] = None,
                 allowed_protocols: Optional[List[str]] = None) -> str:
    """
    Sanitiza contenido HTML para prevenir XSS.
    
    Args:
        html_content: Contenido HTML a sanitizar
        allowed_tags: Lista de etiquetas HTML permitidas (opcional)
        allowed_attributes: Diccionario de atributos permitidos por etiqueta (opcional)
        allowed_protocols: Lista de protocolos permitidos para URLs (opcional)
        
    Returns:
        Contenido HTML sanitizado
    """
    if not html_content:
        return ''
    
    # Usar valores por defecto si no se proporcionan
    if allowed_tags is None:
        allowed_tags = ALLOWED_TAGS
    
    if allowed_attributes is None:
        allowed_attributes = ALLOWED_ATTRIBUTES
    
    if allowed_protocols is None:
        allowed_protocols = ALLOWED_PROTOCOLS
    
    # Sanitizar HTML con bleach
    clean_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        strip=True,
        strip_comments=True
    )
    
    return clean_html


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo para prevenir path traversal.
    
    Args:
        filename: Nombre de archivo a sanitizar
        
    Returns:
        Nombre de archivo sanitizado
    """
    if not filename:
        return ''
    
    # Normalizar caracteres Unicode
    filename = unicodedata.normalize('NFKD', filename)
    
    # Eliminar caracteres no ASCII
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Eliminar espacios en blanco al inicio y al final
    filename = filename.strip()
    
    # Reemplazar espacios por guiones bajos
    filename = re.sub(r'\s+', '_', filename)
    
    # Eliminar secuencias de puntos (para prevenir path traversal)
    filename = re.sub(r'\.+', '.', filename)
    
    # Eliminar barras y caracteres especiales
    filename = re.sub(r'[/\\:*?"<>|]', '', filename)
    
    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    
    return filename


def sanitize_input(value: Any, max_length: Optional[int] = None) -> str:
    """
    Sanitiza una entrada de usuario para prevenir XSS.
    
    Args:
        value: Valor a sanitizar
        max_length: Longitud máxima permitida (opcional)
        
    Returns:
        Valor sanitizado
    """
    if value is None:
        return ''
    
    # Convertir a cadena
    value = str(value)
    
    # Escapar HTML
    value = html.escape(value)
    
    # Limitar longitud si se especifica
    if max_length is not None and len(value) > max_length:
        value = value[:max_length]
    
    return value


def sanitize_sql_like(value: str) -> str:
    """
    Sanitiza una cadena para usar en consultas LIKE.
    
    Args:
        value: Cadena a sanitizar
        
    Returns:
        Cadena sanitizada
    """
    if not value:
        return ''
    
    # Escapar caracteres especiales de LIKE
    value = value.replace('\\', '\\\\')
    value = value.replace('%', '\\%')
    value = value.replace('_', '\\_')
    
    return value


def sanitize_json(data: Union[Dict, List]) -> Union[Dict, List]:
    """
    Sanitiza datos JSON para prevenir XSS.
    
    Args:
        data: Datos JSON a sanitizar
        
    Returns:
        Datos JSON sanitizados
    """
    if isinstance(data, dict):
        return {k: sanitize_json(v) if isinstance(v, (dict, list)) else sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json(item) if isinstance(item, (dict, list)) else sanitize_input(item) for item in data]
    else:
        return data


def sanitize_url(url: str) -> str:
    """
    Sanitiza una URL para prevenir ataques.
    
    Args:
        url: URL a sanitizar
        
    Returns:
        URL sanitizada
    """
    if not url:
        return ''
    
    # Verificar si la URL tiene un protocolo permitido
    allowed_protocols = ['http://', 'https://', 'mailto:', 'tel:']
    has_protocol = any(url.startswith(protocol) for protocol in allowed_protocols)
    
    if not has_protocol:
        # Añadir https:// por defecto
        url = 'https://' + url
    
    # Escapar caracteres especiales
    url = html.escape(url)
    
    return url


def sanitize_email(email: str) -> str:
    """
    Sanitiza una dirección de correo electrónico.
    
    Args:
        email: Dirección de correo electrónico a sanitizar
        
    Returns:
        Dirección de correo electrónico sanitizada
    """
    if not email:
        return ''
    
    # Eliminar espacios en blanco
    email = email.strip()
    
    # Convertir a minúsculas
    email = email.lower()
    
    # Verificar formato básico
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return ''
    
    return email


def sanitize_phone(phone: str) -> str:
    """
    Sanitiza un número de teléfono.
    
    Args:
        phone: Número de teléfono a sanitizar
        
    Returns:
        Número de teléfono sanitizado
    """
    if not phone:
        return ''
    
    # Eliminar caracteres no numéricos
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Verificar formato básico
    if not re.match(r'^\+?[\d]{8,15}$', phone):
        return ''
    
    return phone
