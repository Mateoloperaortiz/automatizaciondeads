"""
Utilidades del planificador para AdFlux.

Este módulo contiene funciones para configurar y utilizar el planificador.
"""

import os
from flask import current_app


def configure_scheduled_jobs(app, scheduler):
    """
    Configura trabajos programados con APScheduler.
    
    Args:
        app: Aplicación Flask.
        scheduler: Instancia de APScheduler.
    """
    # Ejemplo: Programar sincronización diaria de Meta Ads
    # scheduler.add_job(id='sync_meta_all_accounts',
    #                   func=run_meta_sync_for_all_accounts,
    #                   trigger='cron', 
    #                   hour=3, # Ejecutar diariamente a las 3 AM
    #                   minute=0,
    #                   replace_existing=True)
    
    # Nota: Los trabajos programados ahora se configuran a través de comandos CLI
    # Ver adflux/cli/scheduler_commands.py
    pass


def run_meta_sync_for_all_accounts(date_preset='last_30d'):
    """
    Sincroniza datos de Meta Ads para todas las cuentas configuradas.
    
    Args:
        date_preset: Preset de fecha para la sincronización.
        
    Returns:
        Mensaje de estado.
    """
    try:
        # Obtener ID de cuenta de Meta Ads de la configuración
        meta_ad_account_id = os.environ.get('META_AD_ACCOUNT_ID') or current_app.config.get('META_AD_ACCOUNT_ID')
        
        if not meta_ad_account_id:
            current_app.logger.error("No se encontró ID de cuenta de Meta Ads en la configuración.")
            return "Error: No se encontró ID de cuenta de Meta Ads en la configuración."
        
        # Importar la tarea asíncrona
        from ..tasks import sync_meta_insights_task
        
        # Llamar a la tarea asíncronamente
        task = sync_meta_insights_task.delay(meta_ad_account_id, date_preset=date_preset)
        
        current_app.logger.info(f"Tarea de sincronización de Meta Ads iniciada en segundo plano. ID de Tarea: {task.id}")
        return f"Tarea de sincronización de Meta Ads iniciada en segundo plano. ID de Tarea: {task.id}"
    
    except Exception as e:
        current_app.logger.error(f"Error enviando tarea de sincronización de Meta Ads: {e}")
        return f"Error: {str(e)}"
