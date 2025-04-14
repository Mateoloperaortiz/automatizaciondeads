"""
Gestor de caché para AdFlux.

Este módulo proporciona un gestor centralizado para la caché de la aplicación.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timedelta

from .redis_cache import RedisCache


# Configurar logger
logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gestor centralizado para la caché de la aplicación.
    
    Proporciona métodos para gestionar diferentes tipos de caché.
    """
    
    def __init__(self, redis_cache: RedisCache):
        """
        Inicializa el gestor de caché.
        
        Args:
            redis_cache: Instancia de RedisCache
        """
        self.redis_cache = redis_cache
        
        # Prefijos para diferentes tipos de caché
        self.prefixes = {
            'api': 'api:',
            'view': 'view:',
            'data': 'data:',
            'fragment': 'fragment:',
            'user': 'user:',
            'session': 'session:',
            'rate_limit': 'rate_limit:'
        }
    
    def _get_prefixed_key(self, key: str, prefix_type: str) -> str:
        """
        Obtiene una clave con el prefijo del tipo especificado.
        
        Args:
            key: Clave base
            prefix_type: Tipo de prefijo
            
        Returns:
            Clave con prefijo
        """
        if prefix_type not in self.prefixes:
            logger.warning(f"Tipo de prefijo desconocido: {prefix_type}")
            return key
        
        return f"{self.prefixes[prefix_type]}{key}"
    
    def get_api_cache(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la caché de API.
        
        Args:
            key: Clave del valor
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor almacenado o valor por defecto
        """
        return self.redis_cache.get(self._get_prefixed_key(key, 'api'), default)
    
    def set_api_cache(
        self,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Almacena un valor en la caché de API.
        
        Args:
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        return self.redis_cache.set(self._get_prefixed_key(key, 'api'), value, timeout)
    
    def delete_api_cache(self, key: str) -> bool:
        """
        Elimina un valor de la caché de API.
        
        Args:
            key: Clave del valor
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        return self.redis_cache.delete(self._get_prefixed_key(key, 'api'))
    
    def get_view_cache(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la caché de vistas.
        
        Args:
            key: Clave del valor
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor almacenado o valor por defecto
        """
        return self.redis_cache.get(self._get_prefixed_key(key, 'view'), default)
    
    def set_view_cache(
        self,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Almacena un valor en la caché de vistas.
        
        Args:
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        return self.redis_cache.set(self._get_prefixed_key(key, 'view'), value, timeout)
    
    def delete_view_cache(self, key: str) -> bool:
        """
        Elimina un valor de la caché de vistas.
        
        Args:
            key: Clave del valor
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        return self.redis_cache.delete(self._get_prefixed_key(key, 'view'))
    
    def get_data_cache(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la caché de datos.
        
        Args:
            key: Clave del valor
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor almacenado o valor por defecto
        """
        return self.redis_cache.get(self._get_prefixed_key(key, 'data'), default)
    
    def set_data_cache(
        self,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Almacena un valor en la caché de datos.
        
        Args:
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        return self.redis_cache.set(self._get_prefixed_key(key, 'data'), value, timeout)
    
    def delete_data_cache(self, key: str) -> bool:
        """
        Elimina un valor de la caché de datos.
        
        Args:
            key: Clave del valor
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        return self.redis_cache.delete(self._get_prefixed_key(key, 'data'))
    
    def get_fragment_cache(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la caché de fragmentos.
        
        Args:
            key: Clave del valor
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor almacenado o valor por defecto
        """
        return self.redis_cache.get(self._get_prefixed_key(key, 'fragment'), default)
    
    def set_fragment_cache(
        self,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Almacena un valor en la caché de fragmentos.
        
        Args:
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        return self.redis_cache.set(self._get_prefixed_key(key, 'fragment'), value, timeout)
    
    def delete_fragment_cache(self, key: str) -> bool:
        """
        Elimina un valor de la caché de fragmentos.
        
        Args:
            key: Clave del valor
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        return self.redis_cache.delete(self._get_prefixed_key(key, 'fragment'))
    
    def get_user_cache(self, user_id: str, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la caché de usuario.
        
        Args:
            user_id: ID del usuario
            key: Clave del valor
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor almacenado o valor por defecto
        """
        cache_key = f"{user_id}:{key}"
        return self.redis_cache.get(self._get_prefixed_key(cache_key, 'user'), default)
    
    def set_user_cache(
        self,
        user_id: str,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Almacena un valor en la caché de usuario.
        
        Args:
            user_id: ID del usuario
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        cache_key = f"{user_id}:{key}"
        return self.redis_cache.set(self._get_prefixed_key(cache_key, 'user'), value, timeout)
    
    def delete_user_cache(self, user_id: str, key: str) -> bool:
        """
        Elimina un valor de la caché de usuario.
        
        Args:
            user_id: ID del usuario
            key: Clave del valor
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        cache_key = f"{user_id}:{key}"
        return self.redis_cache.delete(self._get_prefixed_key(cache_key, 'user'))
    
    def clear_user_cache(self, user_id: str) -> int:
        """
        Elimina toda la caché de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Número de claves eliminadas
        """
        pattern = self._get_prefixed_key(f"{user_id}:*", 'user')
        return self.redis_cache.flush(pattern)
    
    def get_session_cache(self, session_id: str, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la caché de sesión.
        
        Args:
            session_id: ID de la sesión
            key: Clave del valor
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor almacenado o valor por defecto
        """
        cache_key = f"{session_id}:{key}"
        return self.redis_cache.get(self._get_prefixed_key(cache_key, 'session'), default)
    
    def set_session_cache(
        self,
        session_id: str,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Almacena un valor en la caché de sesión.
        
        Args:
            session_id: ID de la sesión
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        cache_key = f"{session_id}:{key}"
        return self.redis_cache.set(self._get_prefixed_key(cache_key, 'session'), value, timeout)
    
    def delete_session_cache(self, session_id: str, key: str) -> bool:
        """
        Elimina un valor de la caché de sesión.
        
        Args:
            session_id: ID de la sesión
            key: Clave del valor
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        cache_key = f"{session_id}:{key}"
        return self.redis_cache.delete(self._get_prefixed_key(cache_key, 'session'))
    
    def clear_session_cache(self, session_id: str) -> int:
        """
        Elimina toda la caché de una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Número de claves eliminadas
        """
        pattern = self._get_prefixed_key(f"{session_id}:*", 'session')
        return self.redis_cache.flush(pattern)
    
    def get_rate_limit(self, key: str) -> int:
        """
        Obtiene el valor actual de un límite de tasa.
        
        Args:
            key: Clave del límite
            
        Returns:
            Valor actual del límite
        """
        value = self.redis_cache.get(self._get_prefixed_key(key, 'rate_limit'), 0)
        return int(value) if value is not None else 0
    
    def increment_rate_limit(
        self,
        key: str,
        timeout: int,
        amount: int = 1
    ) -> int:
        """
        Incrementa el valor de un límite de tasa.
        
        Args:
            key: Clave del límite
            timeout: Tiempo de expiración en segundos
            amount: Cantidad a incrementar
            
        Returns:
            Nuevo valor del límite
        """
        cache_key = self._get_prefixed_key(key, 'rate_limit')
        
        # Incrementar valor
        value = self.redis_cache.incr(cache_key, amount)
        
        # Establecer tiempo de expiración si es un valor nuevo
        if value == amount:
            self.redis_cache.expire(cache_key, timeout)
        
        return value
    
    def reset_rate_limit(self, key: str) -> bool:
        """
        Restablece un límite de tasa.
        
        Args:
            key: Clave del límite
            
        Returns:
            True si se restableció correctamente, False en caso contrario
        """
        return self.redis_cache.delete(self._get_prefixed_key(key, 'rate_limit'))
    
    def clear_all_cache(self) -> bool:
        """
        Elimina toda la caché.
        
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        return self.redis_cache.clear()
    
    def clear_cache_by_type(self, prefix_type: str) -> int:
        """
        Elimina toda la caché de un tipo específico.
        
        Args:
            prefix_type: Tipo de prefijo
            
        Returns:
            Número de claves eliminadas
        """
        if prefix_type not in self.prefixes:
            logger.warning(f"Tipo de prefijo desconocido: {prefix_type}")
            return 0
        
        pattern = f"{self.prefixes[prefix_type]}*"
        return self.redis_cache.flush(pattern)
