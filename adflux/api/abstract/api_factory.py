"""
Fábrica de APIs publicitarias.

Este módulo define la fábrica para crear instancias de APIs publicitarias
según la plataforma especificada.
"""

from typing import Dict, Any, Optional, Type
from .ad_api import AdAPI


class AdAPIFactory:
    """
    Fábrica para crear instancias de APIs publicitarias.
    
    Implementa el patrón Factory para crear instancias de APIs publicitarias
    según la plataforma especificada.
    """
    
    # Registro de implementaciones de APIs
    _apis: Dict[str, Type[AdAPI]] = {}
    
    @classmethod
    def register(cls, platform: str, api_class: Type[AdAPI]) -> None:
        """
        Registra una implementación de API para una plataforma.
        
        Args:
            platform: Nombre de la plataforma ('meta', 'google', 'tiktok', etc.)
            api_class: Clase que implementa la interfaz AdAPI
        """
        cls._apis[platform.lower()] = api_class
    
    @classmethod
    def create(cls, platform: str, config: Dict[str, Any]) -> AdAPI:
        """
        Crea una instancia de API para la plataforma especificada.
        
        Args:
            platform: Nombre de la plataforma ('meta', 'google', 'tiktok', etc.)
            config: Configuración para la API
            
        Returns:
            Instancia de la API
            
        Raises:
            ValueError: Si la plataforma no está registrada
        """
        platform = platform.lower()
        if platform not in cls._apis:
            raise ValueError(f"Plataforma no soportada: {platform}")
        
        api_class = cls._apis[platform]
        return api_class(**config)
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """
        Obtiene la lista de plataformas soportadas.
        
        Returns:
            Lista de nombres de plataformas
        """
        return list(cls._apis.keys())
