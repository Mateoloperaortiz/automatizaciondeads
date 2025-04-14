"""
Autenticación de dos factores para AdFlux.

Este módulo proporciona funcionalidades para la autenticación de dos factores (2FA)
utilizando TOTP (Time-based One-Time Password).
"""

import base64
import os
import logging
from typing import Tuple, Optional

import pyotp
import qrcode
from io import BytesIO


# Configurar logger
logger = logging.getLogger(__name__)


def generate_totp_secret() -> str:
    """
    Genera un secreto aleatorio para TOTP.
    
    Returns:
        Secreto en formato base32
    """
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "AdFlux") -> str:
    """
    Genera un URI para código QR de TOTP.
    
    Args:
        secret: Secreto TOTP
        email: Email del usuario
        issuer: Nombre del emisor
        
    Returns:
        URI para código QR
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(email, issuer_name=issuer)


def generate_qr_code(uri: str) -> bytes:
    """
    Genera un código QR a partir de un URI.
    
    Args:
        uri: URI para código QR
        
    Returns:
        Imagen del código QR en formato PNG
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir imagen a bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def verify_totp(secret: str, code: str) -> bool:
    """
    Verifica un código TOTP.
    
    Args:
        secret: Secreto TOTP
        code: Código TOTP a verificar
        
    Returns:
        True si el código es válido, False en caso contrario
    """
    if not secret or not code:
        return False
    
    # Eliminar espacios y guiones
    code = code.replace(" ", "").replace("-", "")
    
    # Verificar código
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_backup_codes(count: int = 10) -> Tuple[list, str]:
    """
    Genera códigos de respaldo para 2FA.
    
    Args:
        count: Número de códigos a generar
        
    Returns:
        Tupla con lista de códigos y hash de los códigos
    """
    # Generar códigos aleatorios
    codes = []
    for _ in range(count):
        # Generar 10 caracteres aleatorios (5 bytes en base32)
        random_bytes = os.urandom(5)
        code = base64.b32encode(random_bytes).decode('utf-8')
        # Tomar solo los primeros 10 caracteres y formatear como XX-XX-XX-XX-XX
        code = code[:10].upper()
        formatted_code = '-'.join([code[i:i+2] for i in range(0, 10, 2)])
        codes.append(formatted_code)
    
    # Generar hash de los códigos (en una implementación real, se almacenarían los hashes)
    # Aquí simplemente los concatenamos como ejemplo
    codes_str = ','.join(codes)
    
    return codes, codes_str


def verify_backup_code(code: str, stored_codes: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica un código de respaldo.
    
    Args:
        code: Código de respaldo a verificar
        stored_codes: Códigos de respaldo almacenados
        
    Returns:
        Tupla con (éxito, nuevos códigos almacenados)
    """
    if not code or not stored_codes:
        return False, None
    
    # Eliminar espacios y guiones
    code = code.replace(" ", "").replace("-", "").upper()
    
    # Convertir códigos almacenados a lista
    codes_list = stored_codes.split(',')
    
    # Verificar si el código está en la lista
    for i, stored_code in enumerate(codes_list):
        # Eliminar espacios y guiones del código almacenado
        clean_stored_code = stored_code.replace(" ", "").replace("-", "").upper()
        
        if code == clean_stored_code:
            # Código válido, eliminarlo de la lista
            codes_list.pop(i)
            # Devolver nuevos códigos almacenados
            return True, ','.join(codes_list)
    
    return False, None
