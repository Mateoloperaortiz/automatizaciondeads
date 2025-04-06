"""
Utilidades de Celery para AdFlux.

Este módulo contiene funciones para configurar y utilizar Celery.
"""

from ..extensions import celery


def make_celery(app):
    """
    Configura Celery para trabajar con Flask.
    
    Args:
        app: Aplicación Flask.
        
    Returns:
        Instancia de Celery configurada.
    """
    # Establecer explícitamente broker y backend desde la config de Flask
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']

    # Actualizar el resto de la configuración de Celery desde la config de Flask
    celery.conf.update(app.config)

    # Subclase Task para empujar automáticamente el contexto de la aplicación
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
