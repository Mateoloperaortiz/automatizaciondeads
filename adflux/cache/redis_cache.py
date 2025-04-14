"""
Implementación de caché con Redis.

Este módulo proporciona una implementación de caché utilizando Redis.
"""

import json
import logging
import pickle
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timedelta

import redis


# Configurar logger
logger = logging.getLogger(__name__)


class RedisCache:
    """
    Implementación de caché con Redis.
    
    Proporciona métodos para almacenar y recuperar datos en caché.
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = 'adflux:',
        default_timeout: int = 300,
        serializer: str = 'json'
    ):
        """
        Inicializa la caché Redis.
        
        Args:
            host: Host de Redis
            port: Puerto de Redis
            db: Base de datos de Redis
            password: Contraseña de Redis
            prefix: Prefijo para las claves de caché
            default_timeout: Tiempo de expiración por defecto en segundos
            serializer: Serializador a utilizar ('json' o 'pickle')
        """
        self.prefix = prefix
        self.default_timeout = default_timeout
        self.serializer = serializer
        
        # Conectar a Redis
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False  # No decodificar respuestas automáticamente
        )
        
        # Verificar conexión
        try:
            self.redis.ping()
            logger.info(f"Conexión exitosa a Redis en {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Error al conectar a Redis: {str(e)}")
            raise
    
    def _get_key(self, key: str) -> str:
        """
        Obtiene la clave completa con prefijo.
        
        Args:
            key: Clave base
            
        Returns:
            Clave completa con prefijo
        """
        return f"{self.prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """
        Serializa un valor para almacenarlo en Redis.
        
        Args:
            value: Valor a serializar
            
        Returns:
            Valor serializado
            
        Raises:
            ValueError: Si el valor no se puede serializar
        """
        try:
            if self.serializer == 'json':
                return json.dumps(value).encode('utf-8')
            else:  # pickle
                return pickle.dumps(value)
        except (TypeError, pickle.PickleError) as e:
            logger.error(f"Error al serializar valor: {str(e)}")
            raise ValueError(f"No se puede serializar el valor: {str(e)}")
    
    def _deserialize(self, value: bytes) -> Any:
        """
        Deserializa un valor almacenado en Redis.
        
        Args:
            value: Valor serializado
            
        Returns:
            Valor deserializado
            
        Raises:
            ValueError: Si el valor no se puede deserializar
        """
        if value is None:
            return None
        
        try:
            if self.serializer == 'json':
                return json.loads(value.decode('utf-8'))
            else:  # pickle
                return pickle.loads(value)
        except (json.JSONDecodeError, pickle.PickleError, UnicodeDecodeError) as e:
            logger.error(f"Error al deserializar valor: {str(e)}")
            raise ValueError(f"No se puede deserializar el valor: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la caché.
        
        Args:
            key: Clave del valor
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor almacenado o valor por defecto
        """
        try:
            value = self.redis.get(self._get_key(key))
            if value is None:
                return default
            
            return self._deserialize(value)
        
        except Exception as e:
            logger.error(f"Error al obtener valor de caché para clave '{key}': {str(e)}")
            return default
    
    def set(
        self,
        key: str,
        value: Any,
        timeout: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Almacena un valor en la caché.
        
        Args:
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos (None = default_timeout)
            nx: Solo establecer si la clave no existe
            xx: Solo establecer si la clave ya existe
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        if timeout is None:
            timeout = self.default_timeout
        
        try:
            serialized_value = self._serialize(value)
            
            if nx and xx:
                logger.warning("No se pueden especificar nx=True y xx=True simultáneamente")
                return False
            
            if nx:
                return bool(self.redis.set(
                    self._get_key(key),
                    serialized_value,
                    ex=timeout,
                    nx=True
                ))
            
            if xx:
                return bool(self.redis.set(
                    self._get_key(key),
                    serialized_value,
                    ex=timeout,
                    xx=True
                ))
            
            return bool(self.redis.set(
                self._get_key(key),
                serialized_value,
                ex=timeout
            ))
        
        except Exception as e:
            logger.error(f"Error al establecer valor en caché para clave '{key}': {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Elimina un valor de la caché.
        
        Args:
            key: Clave del valor
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            return bool(self.redis.delete(self._get_key(key)))
        
        except Exception as e:
            logger.error(f"Error al eliminar valor de caché para clave '{key}': {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en la caché.
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si la clave existe, False en caso contrario
        """
        try:
            return bool(self.redis.exists(self._get_key(key)))
        
        except Exception as e:
            logger.error(f"Error al verificar existencia de clave '{key}': {str(e)}")
            return False
    
    def expire(self, key: str, timeout: int) -> bool:
        """
        Establece un tiempo de expiración para una clave.
        
        Args:
            key: Clave a expirar
            timeout: Tiempo de expiración en segundos
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        try:
            return bool(self.redis.expire(self._get_key(key), timeout))
        
        except Exception as e:
            logger.error(f"Error al establecer expiración para clave '{key}': {str(e)}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        Obtiene el tiempo de vida restante de una clave.
        
        Args:
            key: Clave a consultar
            
        Returns:
            Tiempo de vida en segundos, -1 si no expira, -2 si no existe
        """
        try:
            return self.redis.ttl(self._get_key(key))
        
        except Exception as e:
            logger.error(f"Error al obtener TTL para clave '{key}': {str(e)}")
            return -2
    
    def incr(self, key: str, amount: int = 1) -> int:
        """
        Incrementa el valor de una clave.
        
        Args:
            key: Clave a incrementar
            amount: Cantidad a incrementar
            
        Returns:
            Nuevo valor
        """
        try:
            return self.redis.incr(self._get_key(key), amount)
        
        except Exception as e:
            logger.error(f"Error al incrementar valor para clave '{key}': {str(e)}")
            return 0
    
    def decr(self, key: str, amount: int = 1) -> int:
        """
        Decrementa el valor de una clave.
        
        Args:
            key: Clave a decrementar
            amount: Cantidad a decrementar
            
        Returns:
            Nuevo valor
        """
        try:
            return self.redis.decr(self._get_key(key), amount)
        
        except Exception as e:
            logger.error(f"Error al decrementar valor para clave '{key}': {str(e)}")
            return 0
    
    def keys(self, pattern: str = '*') -> List[str]:
        """
        Obtiene las claves que coinciden con un patrón.
        
        Args:
            pattern: Patrón de búsqueda
            
        Returns:
            Lista de claves
        """
        try:
            keys = self.redis.keys(self._get_key(pattern))
            # Eliminar prefijo de las claves
            prefix_len = len(self.prefix)
            return [key.decode('utf-8')[prefix_len:] for key in keys]
        
        except Exception as e:
            logger.error(f"Error al obtener claves con patrón '{pattern}': {str(e)}")
            return []
    
    def flush(self, pattern: str = '*') -> int:
        """
        Elimina todas las claves que coinciden con un patrón.
        
        Args:
            pattern: Patrón de búsqueda
            
        Returns:
            Número de claves eliminadas
        """
        try:
            keys = self.redis.keys(self._get_key(pattern))
            if not keys:
                return 0
            
            return self.redis.delete(*keys)
        
        except Exception as e:
            logger.error(f"Error al eliminar claves con patrón '{pattern}': {str(e)}")
            return 0
    
    def clear(self) -> bool:
        """
        Elimina todas las claves con el prefijo configurado.
        
        Returns:
            True si se eliminaron correctamente, False en caso contrario
        """
        return self.flush() > 0
    
    def get_many(self, keys: List[str], default: Any = None) -> Dict[str, Any]:
        """
        Obtiene múltiples valores de la caché.
        
        Args:
            keys: Lista de claves
            default: Valor por defecto para claves no encontradas
            
        Returns:
            Diccionario con claves y valores
        """
        if not keys:
            return {}
        
        try:
            # Convertir claves a formato Redis
            redis_keys = [self._get_key(key) for key in keys]
            
            # Obtener valores
            values = self.redis.mget(redis_keys)
            
            # Deserializar valores
            result = {}
            for i, key in enumerate(keys):
                value = values[i]
                if value is None:
                    result[key] = default
                else:
                    try:
                        result[key] = self._deserialize(value)
                    except ValueError:
                        result[key] = default
            
            return result
        
        except Exception as e:
            logger.error(f"Error al obtener múltiples valores de caché: {str(e)}")
            return {key: default for key in keys}
    
    def set_many(
        self,
        mapping: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> bool:
        """
        Almacena múltiples valores en la caché.
        
        Args:
            mapping: Diccionario con claves y valores
            timeout: Tiempo de expiración en segundos (None = default_timeout)
            
        Returns:
            True si se almacenaron correctamente, False en caso contrario
        """
        if not mapping:
            return True
        
        if timeout is None:
            timeout = self.default_timeout
        
        try:
            # Serializar valores
            redis_mapping = {}
            for key, value in mapping.items():
                try:
                    redis_mapping[self._get_key(key)] = self._serialize(value)
                except ValueError:
                    logger.warning(f"No se pudo serializar el valor para la clave '{key}'")
            
            # Almacenar valores
            pipeline = self.redis.pipeline()
            pipeline.mset(redis_mapping)
            
            # Establecer tiempo de expiración
            for key in mapping:
                pipeline.expire(self._get_key(key), timeout)
            
            pipeline.execute()
            return True
        
        except Exception as e:
            logger.error(f"Error al establecer múltiples valores en caché: {str(e)}")
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """
        Elimina múltiples valores de la caché.
        
        Args:
            keys: Lista de claves
            
        Returns:
            True si se eliminaron correctamente, False en caso contrario
        """
        if not keys:
            return True
        
        try:
            # Convertir claves a formato Redis
            redis_keys = [self._get_key(key) for key in keys]
            
            # Eliminar valores
            self.redis.delete(*redis_keys)
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar múltiples valores de caché: {str(e)}")
            return False
