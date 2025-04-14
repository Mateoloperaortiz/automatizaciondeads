"""
Configuración de Celery para AdFlux.

Este módulo configura Celery para el procesamiento asíncrono de tareas.
"""

import os
import logging
from typing import Dict, Any, List, Optional

from celery import Celery, Task
from celery.signals import task_failure, task_success, task_retry, worker_ready
from flask import Flask


# Configurar logger
logger = logging.getLogger(__name__)


# Crear aplicación Celery
celery = Celery('adflux')


# Definir colas con prioridades
QUEUE_CONFIG = {
    'high': {
        'exchange': 'high',
        'routing_key': 'high',
        'queue_arguments': {'x-max-priority': 10}
    },
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
        'queue_arguments': {'x-max-priority': 5}
    },
    'low': {
        'exchange': 'low',
        'routing_key': 'low',
        'queue_arguments': {'x-max-priority': 3}
    },
    'batch': {
        'exchange': 'batch',
        'routing_key': 'batch',
        'queue_arguments': {'x-max-priority': 1}
    }
}


def make_celery(app: Flask) -> Celery:
    """
    Configura Celery para trabajar con Flask.
    
    Args:
        app: Aplicación Flask
        
    Returns:
        Aplicación Celery configurada
    """
    # Configurar Celery desde la aplicación Flask
    celery.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        task_default_queue='default',
        task_default_exchange='default',
        task_default_routing_key='default',
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        task_queues=[
            {
                'name': queue_name,
                'exchange': config['exchange'],
                'routing_key': config['routing_key'],
                'queue_arguments': config['queue_arguments']
            }
            for queue_name, config in QUEUE_CONFIG.items()
        ],
        task_routes={
            # Tareas de alta prioridad
            'adflux.tasks.campaign_tasks.publish_campaign': {'queue': 'high', 'priority': 9},
            'adflux.tasks.campaign_tasks.update_campaign': {'queue': 'high', 'priority': 8},
            'adflux.tasks.campaign_tasks.pause_campaign': {'queue': 'high', 'priority': 8},
            'adflux.tasks.campaign_tasks.resume_campaign': {'queue': 'high', 'priority': 8},
            'adflux.tasks.notification_tasks.send_notification': {'queue': 'high', 'priority': 7},
            
            # Tareas de prioridad normal
            'adflux.tasks.sync_tasks.sync_campaign_insights': {'queue': 'default', 'priority': 5},
            'adflux.tasks.sync_tasks.sync_campaign_status': {'queue': 'default', 'priority': 5},
            'adflux.tasks.report_tasks.generate_report': {'queue': 'default', 'priority': 4},
            'adflux.tasks.materialized_view_tasks.refresh_materialized_view': {'queue': 'default', 'priority': 3},
            
            # Tareas de baja prioridad
            'adflux.tasks.sync_tasks.sync_all_campaigns': {'queue': 'low', 'priority': 2},
            'adflux.tasks.materialized_view_tasks.refresh_all_materialized_views': {'queue': 'low', 'priority': 1},
            
            # Tareas por lotes
            'adflux.tasks.batch_tasks.*': {'queue': 'batch', 'priority': 1}
        }
    )
    
    # Definir clase base para tareas
    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Registrar manejadores de señales
    register_signal_handlers()
    
    return celery


def register_signal_handlers():
    """Registra manejadores de señales para Celery."""
    
    @task_failure.connect
    def handle_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, **kw):
        """Manejador para tareas fallidas."""
        logger.error(
            f"Tarea {sender.name} con ID {task_id} falló: {exception}\n"
            f"Args: {args}, Kwargs: {kwargs}"
        )
    
    @task_success.connect
    def handle_task_success(sender=None, result=None, **kwargs):
        """Manejador para tareas exitosas."""
        logger.debug(f"Tarea {sender.name} completada con éxito: {result}")
    
    @task_retry.connect
    def handle_task_retry(sender=None, reason=None, **kwargs):
        """Manejador para reintentos de tareas."""
        logger.warning(f"Reintentando tarea {sender.name}: {reason}")
    
    @worker_ready.connect
    def handle_worker_ready(sender, **kwargs):
        """Manejador para cuando el worker está listo."""
        logger.info(f"Worker {sender.hostname} listo")


def get_task_info() -> Dict[str, Any]:
    """
    Obtiene información sobre las tareas registradas.
    
    Returns:
        Diccionario con información de tareas
    """
    tasks = []
    
    for task_name in sorted(celery.tasks.keys()):
        # Ignorar tareas internas de Celery
        if task_name.startswith('celery.'):
            continue
        
        # Obtener información de la tarea
        task = celery.tasks[task_name]
        
        # Determinar cola y prioridad
        queue = 'default'
        priority = 0
        
        for pattern, route in celery.conf.task_routes.items():
            if pattern == task_name or (pattern.endswith('*') and task_name.startswith(pattern[:-1])):
                queue = route.get('queue', 'default')
                priority = route.get('priority', 0)
                break
        
        tasks.append({
            'name': task_name,
            'queue': queue,
            'priority': priority,
            'max_retries': getattr(task, 'max_retries', None),
            'time_limit': getattr(task, 'time_limit', None),
            'soft_time_limit': getattr(task, 'soft_time_limit', None),
            'rate_limit': getattr(task, 'rate_limit', None)
        })
    
    return {
        'tasks': tasks,
        'queues': list(QUEUE_CONFIG.keys()),
        'total_tasks': len(tasks)
    }
