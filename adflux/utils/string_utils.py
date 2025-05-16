"""
Utilidades para manipulación de strings en AdFlux.

Este módulo proporciona funciones para manipular y formatear strings.
"""

import re
import random
import string
import html
from typing import Optional, Union


def slugify(text: str) -> str:
    """
    Convierte un texto en un slug (URL amigable).
    
    Args:
        text: Texto a convertir en slug.
        
    Returns:
        String convertido a slug.
    """
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'\-+', '-', text)
    text = text.strip('-')
    return text


def truncate(text: str, length: int, suffix: str = '...') -> str:
    """
    Trunca un texto a una longitud específica y añade un sufijo.
    
    Args:
        text: Texto a truncar.
        length: Longitud máxima del texto.
        suffix: Sufijo a añadir si el texto es truncado.
        
    Returns:
        Texto truncado.
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def strip_html(text: str) -> str:
    """
    Elimina etiquetas HTML de un texto.
    
    Args:
        text: Texto con etiquetas HTML.
        
    Returns:
        Texto sin etiquetas HTML.
    """
    text = html.unescape(text)
    text = re.sub(r'<[^>]*>', '', text)
    return text


def random_string(length: int = 10, include_digits: bool = True, include_special: bool = False) -> str:
    """
    Genera una cadena aleatoria de caracteres.
    
    Args:
        length: Longitud de la cadena a generar.
        include_digits: Si se incluyen dígitos.
        include_special: Si se incluyen caracteres especiales.
        
    Returns:
        Cadena aleatoria.
    """
    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    return ''.join(random.choice(chars) for _ in range(length))


def mask_email(email: str, visible_chars: int = 2) -> str:
    """
    Enmascara una dirección de correo electrónico.
    
    Args:
        email: Dirección de correo electrónico.
        visible_chars: Número de caracteres visibles al inicio del nombre de usuario.
        
    Returns:
        Dirección de correo electrónico enmascarada.
    """
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    
    if len(username) <= visible_chars:
        masked_username = username
    else:
        masked_username = username[:visible_chars] + '*' * (len(username) - visible_chars)
    
    return f"{masked_username}@{domain}"


def mask_phone(phone: str, visible_digits: int = 4) -> str:
    """
    Enmascara un número de teléfono.
    
    Args:
        phone: Número de teléfono.
        visible_digits: Número de dígitos visibles al final.
        
    Returns:
        Número de teléfono enmascarado.
    """
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) <= visible_digits:
        return phone
    
    masked_digits = '*' * (len(digits) - visible_digits) + digits[-visible_digits:]
    
    masked_phone = ''
    digit_index = 0
    
    for char in phone:
        if char.isdigit():
            masked_phone += masked_digits[digit_index]
            digit_index += 1
        else:
            masked_phone += char
    
    return masked_phone


def format_currency(amount: Union[int, float], currency: str = 'USD', decimals: int = 2) -> str:
    """
    Formatea un valor monetario.
    
    Args:
        amount: Cantidad a formatear.
        currency: Código de moneda.
        decimals: Número de decimales.
        
    Returns:
        Valor monetario formateado.
    """
    if currency == 'USD':
        return f"${amount:,.{decimals}f}"
    elif currency == 'EUR':
        return f"€{amount:,.{decimals}f}"
    elif currency == 'COP':
        return f"${amount:,.0f}"
    else:
        return f"{amount:,.{decimals}f} {currency}"


def format_number(number: Union[int, float], decimals: int = 0) -> str:
    """
    Formatea un número con separadores de miles.
    
    Args:
        number: Número a formatear.
        decimals: Número de decimales.
        
    Returns:
        Número formateado.
    """
    return f"{number:,.{decimals}f}"


def format_percentage(value: Union[int, float], decimals: int = 1) -> str:
    """
    Formatea un valor como porcentaje.
    
    Args:
        value: Valor a formatear (0.1 = 10%).
        decimals: Número de decimales.
        
    Returns:
        Porcentaje formateado.
    """
    return f"{value * 100:.{decimals}f}%"
