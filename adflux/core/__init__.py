"""
Paquete core para AdFlux.

Este paquete contiene los componentes principales de la aplicación AdFlux,
incluyendo la fábrica de aplicaciones, configuración de Celery, y utilidades.
"""

from .factory import create_app
from .celery_utils import make_celery
from .jinja_utils import nl2br
from .scheduler_utils import configure_scheduled_jobs, run_meta_sync_for_all_accounts

# Para mantener compatibilidad con el código existente
__all__ = [
    'create_app',
    'make_celery',
    'nl2br',
    'configure_scheduled_jobs',
    'run_meta_sync_for_all_accounts'
]
