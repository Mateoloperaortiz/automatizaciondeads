"""
Gestión de secretos para AdFlux.

Este módulo proporciona funciones para gestionar secretos de manera segura,
como claves de API, contraseñas, etc.
"""

import os
import json
import logging
import base64
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from flask import current_app

from ..models import db
from .encryption import encrypt, decrypt


# Configurar logger
logger = logging.getLogger(__name__)


class Secret(db.Model):
    """
    Modelo para secretos.
    
    Almacena secretos encriptados en la base de datos.
    """
    
    __tablename__ = 'secrets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.LargeBinary, nullable=False)
    key = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    metadata = db.Column(db.JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f'<Secret {self.name}>'
    
    @property
    def is_expired(self) -> bool:
        """
        Verifica si el secreto ha expirado.
        
        Returns:
            True si el secreto ha expirado, False en caso contrario
        """
        if self.expires_at is None:
            return False
        
        return self.expires_at < datetime.utcnow()
    
    def get_value(self) -> str:
        """
        Obtiene el valor desencriptado del secreto.
        
        Returns:
            Valor desencriptado
        """
        try:
            decrypted_value = decrypt(self.value, self.key)
            return decrypted_value.decode('utf-8')
        except Exception as e:
            logger.error(f"Error al desencriptar secreto {self.name}: {str(e)}")
            raise ValueError(f"No se pudo desencriptar el secreto {self.name}")
    
    def set_value(self, value: str) -> None:
        """
        Establece el valor encriptado del secreto.
        
        Args:
            value: Valor a encriptar
        """
        try:
            encrypted_value, key = encrypt(value)
            self.value = encrypted_value
            self.key = key
            self.updated_at = datetime.utcnow()
        except Exception as e:
            logger.error(f"Error al encriptar secreto {self.name}: {str(e)}")
            raise ValueError(f"No se pudo encriptar el secreto {self.name}")


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtiene un secreto por su nombre.
    
    Args:
        name: Nombre del secreto
        default: Valor por defecto si el secreto no existe
        
    Returns:
        Valor del secreto o valor por defecto
    """
    try:
        # Buscar secreto en la base de datos
        secret = Secret.query.filter_by(name=name).first()
        
        if secret is None:
            # Si no existe en la base de datos, buscar en variables de entorno
            env_value = os.environ.get(name)
            if env_value is not None:
                return env_value
            
            # Si no existe en variables de entorno, buscar en configuración
            if current_app and name in current_app.config:
                return current_app.config[name]
            
            # Si no existe en ningún lado, devolver valor por defecto
            return default
        
        # Verificar si el secreto ha expirado
        if secret.is_expired:
            logger.warning(f"Secreto {name} ha expirado")
            return default
        
        # Desencriptar y devolver valor
        return secret.get_value()
    
    except Exception as e:
        logger.error(f"Error al obtener secreto {name}: {str(e)}")
        return default


def set_secret(name: str, value: str, expires_in: Optional[int] = None,
              metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Establece un secreto.
    
    Args:
        name: Nombre del secreto
        value: Valor del secreto
        expires_in: Tiempo de expiración en segundos (opcional)
        metadata: Metadatos adicionales (opcional)
        
    Returns:
        True si se estableció correctamente, False en caso contrario
    """
    try:
        # Calcular fecha de expiración
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Buscar secreto existente
        secret = Secret.query.filter_by(name=name).first()
        
        if secret is None:
            # Crear nuevo secreto
            secret = Secret(name=name, metadata=metadata, expires_at=expires_at)
        else:
            # Actualizar metadatos y fecha de expiración
            secret.metadata = metadata
            secret.expires_at = expires_at
        
        # Establecer valor
        secret.set_value(value)
        
        # Guardar en la base de datos
        db.session.add(secret)
        db.session.commit()
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al establecer secreto {name}: {str(e)}")
        return False


def delete_secret(name: str) -> bool:
    """
    Elimina un secreto.
    
    Args:
        name: Nombre del secreto
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    try:
        # Buscar secreto
        secret = Secret.query.filter_by(name=name).first()
        
        if secret is None:
            return False
        
        # Eliminar secreto
        db.session.delete(secret)
        db.session.commit()
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar secreto {name}: {str(e)}")
        return False


def rotate_secret(name: str) -> bool:
    """
    Rota un secreto (re-encripta con una nueva clave).
    
    Args:
        name: Nombre del secreto
        
    Returns:
        True si se rotó correctamente, False en caso contrario
    """
    try:
        # Buscar secreto
        secret = Secret.query.filter_by(name=name).first()
        
        if secret is None:
            return False
        
        # Obtener valor actual
        current_value = secret.get_value()
        
        # Re-encriptar con nueva clave
        encrypted_value, key = encrypt(current_value)
        secret.value = encrypted_value
        secret.key = key
        secret.updated_at = datetime.utcnow()
        
        # Guardar en la base de datos
        db.session.add(secret)
        db.session.commit()
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al rotar secreto {name}: {str(e)}")
        return False


def cleanup_expired_secrets() -> int:
    """
    Elimina secretos expirados.
    
    Returns:
        Número de secretos eliminados
    """
    try:
        # Eliminar secretos expirados
        result = Secret.query.filter(
            Secret.expires_at.isnot(None),
            Secret.expires_at < datetime.utcnow()
        ).delete()
        
        db.session.commit()
        
        return result
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al limpiar secretos expirados: {str(e)}")
        return 0
