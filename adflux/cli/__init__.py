"""
Paquete de comandos CLI para AdFlux.

Este paquete contiene todos los comandos CLI utilizados por AdFlux,
organizados en módulos específicos según su funcionalidad.
"""

# Importar grupos de comandos
from .sync_commands import sync_group
from .data_commands import data_ops_group
from .scheduler_commands import scheduler_group
from .ml_commands import ml_group


# Función para registrar todos los comandos en la aplicación Flask
def register_commands(app):
    """
    Registra todos los comandos CLI en la aplicación Flask.

    Args:
        app: Instancia de la aplicación Flask.
    """
    # Registrar grupos de comandos
    app.cli.add_command(sync_group)
    app.cli.add_command(data_ops_group)
    app.cli.add_command(scheduler_group)
    app.cli.add_command(ml_group)

    # Registrar comandos individuales
    # (Ninguno por ahora, todos están en grupos)


# Para mantener compatibilidad con el código existente
__all__ = ["register_commands", "sync_group", "data_ops_group", "scheduler_group", "ml_group"]
