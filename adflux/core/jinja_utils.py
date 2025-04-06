"""
Utilidades de Jinja2 para AdFlux.

Este módulo contiene filtros y funciones personalizadas para Jinja2.
"""

import re
from markupsafe import Markup


def nl2br(value):
    """
    Filtro Jinja2 para convertir saltos de línea en etiquetas <br>.
    
    Args:
        value: Texto a convertir.
        
    Returns:
        Texto con saltos de línea convertidos en etiquetas <br>.
    """
    if not value:
        return ""
    
    # Convertir \r\n o \n a <br>
    value = re.sub(r'(\r\n|\n)', '<br>', str(value))
    return Markup(value)
