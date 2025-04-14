"""
Encriptación de datos para AdFlux.

Este módulo proporciona funciones para encriptar y desencriptar datos sensibles,
así como para hashear y verificar contraseñas.
"""

import os
import base64
import logging
from typing import Optional, Union, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.hash import argon2


# Configurar logger
logger = logging.getLogger(__name__)


def generate_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    Genera una clave de encriptación a partir de una contraseña.
    
    Args:
        password: Contraseña para generar la clave
        salt: Sal para la derivación de clave (opcional)
        
    Returns:
        Tupla con (clave, sal)
    """
    # Generar sal si no se proporciona
    if salt is None:
        salt = os.urandom(16)
    
    # Derivar clave
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    return key, salt


def encrypt(data: Union[str, bytes], key: Optional[bytes] = None) -> Tuple[bytes, Optional[bytes]]:
    """
    Encripta datos utilizando Fernet (AES-128-CBC).
    
    Args:
        data: Datos a encriptar
        key: Clave de encriptación (opcional)
        
    Returns:
        Tupla con (datos encriptados, clave)
    """
    # Convertir datos a bytes si es una cadena
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Generar clave si no se proporciona
    if key is None:
        key = Fernet.generate_key()
    
    # Crear cifrador
    cipher = Fernet(key)
    
    # Encriptar datos
    encrypted_data = cipher.encrypt(data)
    
    return encrypted_data, key


def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Desencripta datos utilizando Fernet (AES-128-CBC).
    
    Args:
        encrypted_data: Datos encriptados
        key: Clave de encriptación
        
    Returns:
        Datos desencriptados
    """
    # Crear cifrador
    cipher = Fernet(key)
    
    # Desencriptar datos
    decrypted_data = cipher.decrypt(encrypted_data)
    
    return decrypted_data


def hash_password(password: str) -> str:
    """
    Hashea una contraseña utilizando Argon2.
    
    Args:
        password: Contraseña a hashear
        
    Returns:
        Hash de la contraseña
    """
    return argon2.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    
    Args:
        password: Contraseña a verificar
        password_hash: Hash de la contraseña
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    try:
        return argon2.verify(password, password_hash)
    except Exception as e:
        logger.error(f"Error al verificar contraseña: {str(e)}")
        return False


class EncryptedField:
    """
    Descriptor para campos encriptados en modelos SQLAlchemy.
    
    Ejemplo de uso:
    
    ```python
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        _ssn = db.Column(db.LargeBinary)
        _ssn_key = db.Column(db.LargeBinary)
        
        ssn = EncryptedField('_ssn', '_ssn_key')
    ```
    """
    
    def __init__(self, data_attr: str, key_attr: str):
        """
        Inicializa el descriptor.
        
        Args:
            data_attr: Nombre del atributo para datos encriptados
            key_attr: Nombre del atributo para la clave
        """
        self.data_attr = data_attr
        self.key_attr = key_attr
    
    def __get__(self, instance, owner):
        """
        Obtiene el valor desencriptado.
        
        Args:
            instance: Instancia del modelo
            owner: Clase del modelo
            
        Returns:
            Valor desencriptado
        """
        if instance is None:
            return self
        
        encrypted_data = getattr(instance, self.data_attr)
        key = getattr(instance, self.key_attr)
        
        if encrypted_data is None or key is None:
            return None
        
        try:
            decrypted_data = decrypt(encrypted_data, key)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error al desencriptar datos: {str(e)}")
            return None
    
    def __set__(self, instance, value):
        """
        Establece el valor encriptado.
        
        Args:
            instance: Instancia del modelo
            value: Valor a encriptar
        """
        if value is None:
            setattr(instance, self.data_attr, None)
            setattr(instance, self.key_attr, None)
            return
        
        try:
            encrypted_data, key = encrypt(value)
            setattr(instance, self.data_attr, encrypted_data)
            setattr(instance, self.key_attr, key)
        except Exception as e:
            logger.error(f"Error al encriptar datos: {str(e)}")
            raise
