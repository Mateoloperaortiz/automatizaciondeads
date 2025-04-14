"""
Pruebas para el sistema de caché de AdFlux.

Este módulo contiene pruebas para verificar el rendimiento y la funcionalidad
del sistema de caché implementado en AdFlux.
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from adflux.utils.cache import RedisCache, CacheManager, cached, invalidate_cache


@pytest.mark.performance
@pytest.mark.cache
class TestCache:
    """Pruebas para el sistema de caché."""
    
    def test_redis_cache(self, mock_redis):
        """Prueba la clase RedisCache."""
        # Crear caché
        cache = RedisCache(mock_redis, prefix='test:')
        
        # Establecer valor
        cache.set('key1', 'value1')
        
        # Verificar que se estableció correctamente
        assert mock_redis.get('test:key1') == 'value1'
        
        # Obtener valor
        value = cache.get('key1')
        assert value == 'value1'
        
        # Verificar valor inexistente
        assert cache.get('nonexistent') is None
        
        # Establecer valor con tiempo de expiración
        cache.set('key2', 'value2', timeout=60)
        
        # Verificar tiempo de expiración
        assert mock_redis.ttl('test:key2') <= 60
        assert mock_redis.ttl('test:key2') > 0
        
        # Eliminar valor
        cache.delete('key1')
        
        # Verificar que se eliminó
        assert cache.get('key1') is None
        assert mock_redis.get('test:key1') is None
    
    def test_cache_manager(self, mock_redis):
        """Prueba la clase CacheManager."""
        # Crear gestor de caché
        manager = CacheManager(mock_redis)
        
        # Obtener diferentes cachés
        view_cache = manager.get_cache('views')
        api_cache = manager.get_cache('api')
        
        # Verificar que son instancias de RedisCache
        assert isinstance(view_cache, RedisCache)
        assert isinstance(api_cache, RedisCache)
        
        # Verificar que tienen prefijos diferentes
        assert view_cache._prefix != api_cache._prefix
        
        # Establecer valores en diferentes cachés
        view_cache.set('key', 'view_value')
        api_cache.set('key', 'api_value')
        
        # Verificar que los valores son independientes
        assert view_cache.get('key') == 'view_value'
        assert api_cache.get('key') == 'api_value'
        
        # Limpiar una caché
        manager.clear_cache('views')
        
        # Verificar que solo se limpió la caché especificada
        assert view_cache.get('key') is None
        assert api_cache.get('key') == 'api_value'
        
        # Limpiar todas las cachés
        api_cache.set('key', 'api_value')  # Restablecer valor
        manager.clear_all_caches()
        
        # Verificar que todas las cachés se limpiaron
        assert view_cache.get('key') is None
        assert api_cache.get('key') is None
    
    def test_cached_decorator(self, mock_redis):
        """Prueba el decorador cached."""
        # Crear gestor de caché
        manager = CacheManager(mock_redis)
        
        # Función de prueba con contador de llamadas
        call_count = 0
        
        @cached(cache_name='test', key='test_key', timeout=60, cache_manager=manager)
        def test_function():
            nonlocal call_count
            call_count += 1
            return f'result_{call_count}'
        
        # Primera llamada (no cacheada)
        result1 = test_function()
        assert result1 == 'result_1'
        assert call_count == 1
        
        # Segunda llamada (debería usar caché)
        result2 = test_function()
        assert result2 == 'result_1'  # Mismo resultado que la primera llamada
        assert call_count == 1  # La función no se llamó de nuevo
        
        # Verificar que el resultado está en caché
        test_cache = manager.get_cache('test')
        assert test_cache.get('test_key') == 'result_1'
        
        # Limpiar caché
        test_cache.delete('test_key')
        
        # Tercera llamada (no cacheada después de limpiar)
        result3 = test_function()
        assert result3 == 'result_2'  # Nuevo resultado
        assert call_count == 2  # La función se llamó de nuevo
    
    def test_cached_decorator_with_dynamic_key(self, mock_redis):
        """Prueba el decorador cached con clave dinámica."""
        # Crear gestor de caché
        manager = CacheManager(mock_redis)
        
        # Función de prueba con contador de llamadas
        call_count = 0
        
        @cached(cache_name='test', key_prefix='user', timeout=60, cache_manager=manager)
        def get_user_data(user_id):
            nonlocal call_count
            call_count += 1
            return f'data_for_user_{user_id}_{call_count}'
        
        # Llamadas para diferentes usuarios
        result1 = get_user_data(1)
        assert result1 == 'data_for_user_1_1'
        assert call_count == 1
        
        result2 = get_user_data(2)
        assert result2 == 'data_for_user_2_2'
        assert call_count == 2
        
        # Llamada repetida para el primer usuario (debería usar caché)
        result3 = get_user_data(1)
        assert result3 == 'data_for_user_1_1'  # Mismo resultado que la primera llamada
        assert call_count == 2  # La función no se llamó de nuevo
        
        # Verificar que los resultados están en caché
        test_cache = manager.get_cache('test')
        assert test_cache.get('user:1') == 'data_for_user_1_1'
        assert test_cache.get('user:2') == 'data_for_user_2_2'
    
    def test_invalidate_cache_decorator(self, mock_redis):
        """Prueba el decorador invalidate_cache."""
        # Crear gestor de caché
        manager = CacheManager(mock_redis)
        
        # Caché de prueba
        test_cache = manager.get_cache('test')
        
        # Establecer valores en caché
        test_cache.set('user:1', 'data_for_user_1')
        test_cache.set('user:2', 'data_for_user_2')
        test_cache.set('other_key', 'other_value')
        
        # Función que invalida caché
        @invalidate_cache(cache_name='test', key_pattern='user:*', cache_manager=manager)
        def update_users():
            return 'Users updated'
        
        # Llamar función
        result = update_users()
        assert result == 'Users updated'
        
        # Verificar que las claves de usuario se invalidaron
        assert test_cache.get('user:1') is None
        assert test_cache.get('user:2') is None
        
        # Verificar que otras claves no se invalidaron
        assert test_cache.get('other_key') == 'other_value'
    
    def test_invalidate_cache_decorator_with_specific_keys(self, mock_redis):
        """Prueba el decorador invalidate_cache con claves específicas."""
        # Crear gestor de caché
        manager = CacheManager(mock_redis)
        
        # Caché de prueba
        test_cache = manager.get_cache('test')
        
        # Establecer valores en caché
        test_cache.set('user:1', 'data_for_user_1')
        test_cache.set('user:2', 'data_for_user_2')
        
        # Función que invalida caché específica
        @invalidate_cache(cache_name='test', keys=['user:1'], cache_manager=manager)
        def update_user_1():
            return 'User 1 updated'
        
        # Llamar función
        result = update_user_1()
        assert result == 'User 1 updated'
        
        # Verificar que solo la clave específica se invalidó
        assert test_cache.get('user:1') is None
        assert test_cache.get('user:2') == 'data_for_user_2'
    
    def test_cache_performance(self, mock_redis):
        """Prueba el rendimiento del sistema de caché."""
        # Crear gestor de caché
        manager = CacheManager(mock_redis)
        
        # Función de prueba que simula una operación costosa
        def expensive_operation(n):
            time.sleep(0.1)  # Simular operación costosa
            return n * 2
        
        # Versión cacheada de la función
        @cached(cache_name='performance', key_prefix='result', timeout=60, cache_manager=manager)
        def cached_expensive_operation(n):
            return expensive_operation(n)
        
        # Medir tiempo sin caché
        start_time = time.time()
        result1 = expensive_operation(5)
        uncached_time = time.time() - start_time
        
        # Medir tiempo con caché (primera llamada)
        start_time = time.time()
        result2 = cached_expensive_operation(5)
        first_cached_time = time.time() - start_time
        
        # Medir tiempo con caché (segunda llamada)
        start_time = time.time()
        result3 = cached_expensive_operation(5)
        second_cached_time = time.time() - start_time
        
        # Verificar resultados
        assert result1 == result2 == result3 == 10
        
        # Verificar tiempos
        assert first_cached_time <= uncached_time * 1.1  # Permitir pequeña variación
        assert second_cached_time < uncached_time * 0.1  # Caché debería ser mucho más rápido
