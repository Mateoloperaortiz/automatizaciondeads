"""
Tareas Celery para actualizar vistas materializadas.

Este módulo define tareas Celery para actualizar las vistas materializadas
utilizadas para mejorar el rendimiento de consultas frecuentes.
"""

import logging
from celery import shared_task

from ..services.materialized_view_service import MaterializedViewService
from ..exceptions import DatabaseError


# Configurar logger
logger = logging.getLogger(__name__)


@shared_task(
    name="refresh_all_materialized_views",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutos
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,  # 1 hora
    retry_jitter=True
)
def refresh_all_materialized_views(self):
    """
    Tarea Celery para actualizar todas las vistas materializadas.
    
    Returns:
        Mensaje de resultado
    """
    try:
        logger.info("Iniciando actualización de todas las vistas materializadas")
        success, message = MaterializedViewService.refresh_all_views()
        
        if success:
            logger.info(message)
            return message
        else:
            logger.error(message)
            raise Exception(message)
    
    except DatabaseError as e:
        logger.error(f"Error de base de datos al actualizar vistas materializadas: {str(e)}")
        raise self.retry(exc=e)
    
    except Exception as e:
        logger.error(f"Error inesperado al actualizar vistas materializadas: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    name="refresh_materialized_view",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutos
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,  # 1 hora
    retry_jitter=True
)
def refresh_materialized_view(self, view_name):
    """
    Tarea Celery para actualizar una vista materializada específica.
    
    Args:
        view_name: Nombre de la vista materializada
        
    Returns:
        Mensaje de resultado
    """
    try:
        logger.info(f"Iniciando actualización de vista materializada: {view_name}")
        success, message = MaterializedViewService.refresh_view(view_name)
        
        if success:
            logger.info(message)
            return message
        else:
            logger.error(message)
            raise Exception(message)
    
    except DatabaseError as e:
        logger.error(f"Error de base de datos al actualizar vista materializada {view_name}: {str(e)}")
        raise self.retry(exc=e)
    
    except Exception as e:
        logger.error(f"Error inesperado al actualizar vista materializada {view_name}: {str(e)}")
        raise self.retry(exc=e)
