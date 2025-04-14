"""
Pruebas para procesamiento asíncrono en AdFlux.

Este módulo contiene pruebas para verificar la funcionalidad y el rendimiento
del procesamiento asíncrono implementado en AdFlux.
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from adflux.tasks.batch_tasks import process_in_batches, chunk_list


@pytest.mark.performance
class TestAsyncProcessing:
    """Pruebas para procesamiento asíncrono."""
    
    def test_chunk_list(self):
        """Prueba la función chunk_list."""
        # Lista de prueba
        items = list(range(100))
        
        # Dividir en chunks de 10
        chunks = list(chunk_list(items, 10))
        
        # Verificar número de chunks
        assert len(chunks) == 10
        
        # Verificar tamaño de cada chunk
        for chunk in chunks:
            assert len(chunk) == 10
        
        # Verificar que todos los elementos están presentes
        all_items = [item for chunk in chunks for item in chunk]
        assert all_items == items
        
        # Probar con tamaño que no divide exactamente
        items = list(range(95))
        chunks = list(chunk_list(items, 10))
        
        # Verificar número de chunks
        assert len(chunks) == 10
        
        # Verificar tamaño de chunks
        for i in range(9):
            assert len(chunks[i]) == 10
        
        # Último chunk debería tener 5 elementos
        assert len(chunks[9]) == 5
        
        # Verificar que todos los elementos están presentes
        all_items = [item for chunk in chunks for item in chunk]
        assert all_items == items
    
    @patch('adflux.tasks.batch_tasks.celery')
    def test_process_in_batches(self, mock_celery):
        """Prueba la función process_in_batches."""
        # Configurar mock
        mock_task = MagicMock()
        mock_celery.tasks = {'process_item': mock_task}
        
        # Lista de prueba
        items = list(range(50))
        
        # Procesar en lotes
        process_in_batches(
            items=items,
            task_name='process_item',
            batch_size=10,
            queue='batch'
        )
        
        # Verificar que se llamó a la tarea para cada elemento
        assert mock_task.apply_async.call_count == 50
        
        # Verificar argumentos de las llamadas
        for i in range(50):
            args, kwargs = mock_task.apply_async.call_args_list[i][0], mock_task.apply_async.call_args_list[i][1]
            assert args[0] == (i,)  # El primer argumento debería ser el elemento
            assert kwargs['queue'] == 'batch'  # Debería usar la cola especificada
    
    @patch('adflux.tasks.batch_tasks.celery')
    def test_process_in_batches_with_args(self, mock_celery):
        """Prueba la función process_in_batches con argumentos adicionales."""
        # Configurar mock
        mock_task = MagicMock()
        mock_celery.tasks = {'process_item_with_args': mock_task}
        
        # Lista de prueba
        items = list(range(20))
        
        # Procesar en lotes con argumentos adicionales
        process_in_batches(
            items=items,
            task_name='process_item_with_args',
            batch_size=5,
            queue='high',
            args=('extra_arg',),
            kwargs={'option': 'value'}
        )
        
        # Verificar que se llamó a la tarea para cada elemento
        assert mock_task.apply_async.call_count == 20
        
        # Verificar argumentos de las llamadas
        for i in range(20):
            args, kwargs = mock_task.apply_async.call_args_list[i][0], mock_task.apply_async.call_args_list[i][1]
            assert args[0] == (i, 'extra_arg')  # Argumentos: (elemento, extra_arg)
            assert kwargs['queue'] == 'high'  # Cola especificada
            assert kwargs['kwargs'] == {'option': 'value'}  # Kwargs adicionales
    
    @patch('adflux.tasks.batch_tasks.time')
    @patch('adflux.tasks.batch_tasks.celery')
    def test_process_in_batches_with_rate_limit(self, mock_celery, mock_time):
        """Prueba la función process_in_batches con límite de tasa."""
        # Configurar mocks
        mock_task = MagicMock()
        mock_celery.tasks = {'rate_limited_task': mock_task}
        
        # Lista de prueba
        items = list(range(10))
        
        # Procesar en lotes con límite de tasa
        process_in_batches(
            items=items,
            task_name='rate_limited_task',
            batch_size=2,
            rate_limit=5,  # 5 tareas por segundo
            queue='default'
        )
        
        # Verificar que se llamó a la tarea para cada elemento
        assert mock_task.apply_async.call_count == 10
        
        # Verificar que se llamó a time.sleep
        # Debería haber 5 llamadas a sleep (una después de cada 2 elementos)
        assert mock_time.sleep.call_count == 5
        
        # Verificar tiempo de espera
        for call in mock_time.sleep.call_args_list:
            args = call[0]
            assert args[0] == 0.2  # 1/5 = 0.2 segundos entre lotes
    
    @patch('adflux.tasks.batch_tasks.logger')
    @patch('adflux.tasks.batch_tasks.celery')
    def test_process_in_batches_with_progress(self, mock_celery, mock_logger):
        """Prueba la función process_in_batches con registro de progreso."""
        # Configurar mock
        mock_task = MagicMock()
        mock_celery.tasks = {'progress_task': mock_task}
        
        # Lista de prueba
        items = list(range(100))
        
        # Procesar en lotes con registro de progreso
        process_in_batches(
            items=items,
            task_name='progress_task',
            batch_size=10,
            log_progress=True,
            queue='default'
        )
        
        # Verificar que se llamó a la tarea para cada elemento
        assert mock_task.apply_async.call_count == 100
        
        # Verificar que se registró el progreso
        # Debería haber 11 llamadas a logger.info (inicio + después de cada lote)
        assert mock_logger.info.call_count == 11
        
        # Verificar mensajes de progreso
        for i, call in enumerate(mock_logger.info.call_args_list):
            args = call[0]
            if i == 0:
                assert "Iniciando procesamiento" in args[0]
            else:
                assert "Progreso" in args[0]
                assert f"{i*10}%" in args[0]
