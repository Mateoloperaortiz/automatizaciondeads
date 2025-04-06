"""
Comandos CLI del planificador para AdFlux.

Este módulo contiene comandos para gestionar trabajos programados con APScheduler.
"""

import click
from flask.cli import with_appcontext
from ..extensions import scheduler
from ..core import run_meta_sync_for_all_accounts

# Crear grupo de comandos
scheduler_group = click.Group(
    name="scheduler", help="Comandos para gestionar trabajos programados."
)


@scheduler_group.command("setup-jobs")
@with_appcontext
def setup_jobs_command():
    """Registra los trabajos programados con APScheduler."""
    click.echo("Configurando trabajos programados...")
    try:
        scheduler.add_job(
            id="sync_meta_all_accounts",
            func=run_meta_sync_for_all_accounts,
            trigger="cron",
            hour=3,  # Ejecutar diariamente a las 3 AM
            minute=0,
            replace_existing=True,
        )

        # Añadir trabajo programado para entrenamiento de ML
        from ..tasks import scheduled_train_and_predict

        scheduler.add_job(
            id="train_and_predict_segments",
            func=scheduled_train_and_predict,
            trigger="cron",
            hour=2,  # Ejecutar diariamente a las 2 AM
            minute=30,
            replace_existing=True,
        )

        click.echo("Trabajos programados configurados exitosamente.")
    except Exception as e:
        click.echo(f"Error configurando trabajos programados: {e}", err=True)


@scheduler_group.command("list-jobs")
@with_appcontext
def list_jobs_command():
    """Lista todos los trabajos programados."""
    click.echo("Trabajos programados:")
    try:
        jobs = scheduler.get_jobs()
        if not jobs:
            click.echo("No hay trabajos programados.")
            return

        for job in jobs:
            click.echo(f"ID: {job.id}")
            click.echo(f"  Función: {job.func}")
            click.echo(f"  Disparador: {job.trigger}")
            click.echo(f"  Próxima ejecución: {job.next_run_time}")
            click.echo("")
    except Exception as e:
        click.echo(f"Error listando trabajos programados: {e}", err=True)


@scheduler_group.command("remove-job")
@click.argument("job_id")
@with_appcontext
def remove_job_command(job_id):
    """Elimina un trabajo programado por su ID."""
    click.echo(f"Eliminando trabajo programado con ID: {job_id}")
    try:
        scheduler.remove_job(job_id)
        click.echo(f"Trabajo programado {job_id} eliminado exitosamente.")
    except Exception as e:
        click.echo(f"Error eliminando trabajo programado: {e}", err=True)


@scheduler_group.command("run-job")
@click.argument("job_id")
@with_appcontext
def run_job_command(job_id):
    """Ejecuta un trabajo programado inmediatamente."""
    click.echo(f"Ejecutando trabajo programado con ID: {job_id}")
    try:
        job = scheduler.get_job(job_id)
        if not job:
            click.echo(f"No se encontró trabajo programado con ID: {job_id}", err=True)
            return

        # Ejecutar la función del trabajo
        job.func()
        click.echo(f"Trabajo programado {job_id} ejecutado exitosamente.")
    except Exception as e:
        click.echo(f"Error ejecutando trabajo programado: {e}", err=True)
