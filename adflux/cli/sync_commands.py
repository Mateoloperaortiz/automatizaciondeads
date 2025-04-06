"""
Comandos CLI de sincronización para AdFlux.

Este módulo contiene comandos para sincronizar datos desde APIs externas.
"""

import click
from flask.cli import with_appcontext
from ..core import run_meta_sync_for_all_accounts

# Crear grupo de comandos
sync_group = click.Group(name="sync", help="Comandos para sincronizar datos desde APIs externas.")


@sync_group.command("meta")
@click.argument("ad_account_id")
@click.option(
    "--date-preset",
    default="last_30d",
    type=click.Choice(
        [
            "today",
            "yesterday",
            "this_month",
            "last_month",
            "this_quarter",
            "maximum",
            "last_3d",
            "last_7d",
            "last_14d",
            "last_28d",
            "last_30d",
            "last_90d",
            "last_week_mon_sun",
            "last_week_sun_sat",
            "last_quarter",
            "last_year",
            "this_year",
        ],
        case_sensitive=False,
    ),
    help="Preajuste de fecha de la API de Meta para obtener insights.",
)
@with_appcontext
def sync_meta_command(ad_account_id, date_preset):
    """Dispara la tarea asíncrona de sincronización de datos de Meta Ads."""
    click.echo(
        f"Disparando sincronización asíncrona de Meta Ads para la cuenta: {ad_account_id} usando preajuste de fecha: {date_preset}"
    )
    try:
        # Importar la tarea asíncrona
        from ..tasks import sync_meta_insights_task

        # Llamar a la tarea asíncronamente
        task = sync_meta_insights_task.delay(ad_account_id, date_preset=date_preset)
        click.echo(
            f"Tarea de sincronización de Meta Ads iniciada en segundo plano. ID de Tarea: {task.id}"
        )
        click.echo(
            "Revisa los logs del worker de Celery para ver el progreso y estado de finalización."
        )
    except Exception as e:
        click.echo(f"Error enviando tarea de sincronización de Meta Ads: {e}", err=True)


@sync_group.command("meta-all")
@click.option(
    "--date-preset",
    default="last_30d",
    type=click.Choice(
        [
            "today",
            "yesterday",
            "this_month",
            "last_month",
            "this_quarter",
            "maximum",
            "last_3d",
            "last_7d",
            "last_14d",
            "last_28d",
            "last_30d",
            "last_90d",
            "last_week_mon_sun",
            "last_week_sun_sat",
            "last_quarter",
            "last_year",
            "this_year",
        ],
        case_sensitive=False,
    ),
    help="Preajuste de fecha de la API de Meta para obtener insights.",
)
@with_appcontext
def sync_meta_all_command(date_preset):
    """Sincroniza datos de Meta Ads para todas las cuentas configuradas."""
    click.echo(
        f"Sincronizando datos de Meta Ads para todas las cuentas usando preajuste de fecha: {date_preset}"
    )
    try:
        # Llamar a la función que sincroniza todas las cuentas
        result = run_meta_sync_for_all_accounts(date_preset)
        click.echo(f"Sincronización completada: {result}")
    except Exception as e:
        click.echo(f"Error durante la sincronización de Meta Ads: {e}", err=True)


@sync_group.command("insights")
@click.option(
    "--campaign-id",
    type=int,
    help="ID de campaña específica para sincronizar insights. Si no se proporciona, se sincronizan todas las campañas.",
)
@click.option(
    "--date-preset",
    default="last_30d",
    type=click.Choice(
        [
            "today",
            "yesterday",
            "this_month",
            "last_month",
            "this_quarter",
            "maximum",
            "last_3d",
            "last_7d",
            "last_14d",
            "last_28d",
            "last_30d",
            "last_90d",
            "last_week_mon_sun",
            "last_week_sun_sat",
            "last_quarter",
            "last_year",
            "this_year",
        ],
        case_sensitive=False,
    ),
    help="Preajuste de fecha de la API de Meta para obtener insights.",
)
@with_appcontext
def sync_insights_command(campaign_id, date_preset):
    """Sincroniza insights para campañas específicas o todas las campañas."""
    if campaign_id:
        click.echo(
            f"Sincronizando insights para la campaña {campaign_id} usando preajuste de fecha: {date_preset}"
        )
    else:
        click.echo(
            f"Sincronizando insights para todas las campañas usando preajuste de fecha: {date_preset}"
        )

    try:
        # Importar la tarea asíncrona
        from ..tasks import sync_meta_insights_task

        # Llamar a la tarea asíncronamente
        task = sync_meta_insights_task.delay(campaign_id, date_preset)
        click.echo(
            f"Tarea de sincronización de insights iniciada en segundo plano. ID de Tarea: {task.id}"
        )
        click.echo(
            "Revisa los logs del worker de Celery para ver el progreso y estado de finalización."
        )
    except Exception as e:
        click.echo(f"Error enviando tarea de sincronización de insights: {e}", err=True)
