import click
from flask.cli import with_appcontext
import pandas as pd

# Importar la función de sincronización
# ELIMINADO: from .sync_tasks import sync_meta_data
from .extensions import scheduler, db
from .app import run_meta_sync_for_all_accounts
# Importar la función de disparo ML
from .tasks import trigger_train_and_predict
from .models import Candidate

@click.group()
def sync():
    """Comandos para sincronizar datos desde APIs externas."""
    pass

@sync.command('meta')
@click.argument('ad_account_id')
@click.option('--date-preset', default='last_30d', 
              type=click.Choice(['today', 'yesterday', 'this_month', 'last_month', 
                               'this_quarter', 'maximum', 'last_3d', 'last_7d', 
                               'last_14d', 'last_28d', 'last_30d', 'last_90d', 
                               'last_week_mon_sun', 'last_week_sun_sat', 
                               'last_quarter', 'last_year', 'this_year'], case_sensitive=False),
              help='Preajuste de fecha de la API de Meta para obtener insights.')
@with_appcontext
def sync_meta_command(ad_account_id, date_preset):
    """Dispara la tarea asíncrona de sincronización de datos de Meta Ads."""
    click.echo(f"Disparando sincronización asíncrona de Meta Ads para la cuenta: {ad_account_id} usando preajuste de fecha: {date_preset}")
    try:
        # Importar la tarea asíncrona
        from ..sync_tasks import async_sync_meta_data
        # Llamar a la tarea asíncronamente
        task = async_sync_meta_data.delay(ad_account_id, date_preset=date_preset)
        click.echo(f"Tarea de sincronización de Meta Ads iniciada en segundo plano. ID de Tarea: {task.id}")
        click.echo("Revisa los logs del worker de Celery para ver el progreso y estado de finalización.")
    except Exception as e:
        click.echo(f"Error enviando tarea de sincronización de Meta Ads: {e}", err=True)

@click.command('setup-jobs')
@with_appcontext
def setup_jobs_command():
    """Registra los trabajos programados con APScheduler."""
    click.echo("Configurando trabajos programados...")
    try:
        scheduler.add_job(id='sync_meta_all_accounts',
                          func=run_meta_sync_for_all_accounts,
                          trigger='cron', 
                          hour=3, # Ejecutar diariamente a las 3 AM
                          minute=0,
                          replace_existing=True)
        click.echo("Trabajo 'sync_meta_all_accounts' añadido/actualizado correctamente.")
    except Exception as e:
        click.echo(f"Error añadiendo trabajo: {e}")

@click.command('train-predict')
@with_appcontext
def train_predict_ml_command():
    """Dispara manualmente el entrenamiento del modelo ML y la segmentación de candidatos."""
    click.echo("Iniciando tarea de entrenamiento y predicción ML...")
    try:
        trigger_train_and_predict()
        click.echo("Tarea de entrenamiento y predicción ML finalizada.")
    except Exception as e:
        click.echo(f"Error durante la tarea ML: {e}", err=True)
        # Opcionalmente imprimir traceback
        # import traceback
        # traceback.print_exc()

@click.command('analyze-segments')
@with_appcontext
def analyze_segments_command():
    """Analiza e imprime características de los segmentos de candidatos."""
    click.echo("Analizando segmentos de candidatos...")

    try:
        candidates = Candidate.query.all()
        if not candidates:
            click.echo("No se encontraron candidatos en la base de datos.")
            return

        # Convertir a DataFrame
        # Ajustar columnas según la definición de tu modelo Candidate
        df = pd.DataFrame([{
            'id': c.candidate_id,
            'name': c.name,
            'title': c.primary_skill,
            'skills': c.skills, # Asumiendo que skills es una lista/string
            'experience_years': c.years_experience,
            'location': c.location,
            'segment': c.segment
        } for c in candidates])

        # Asegurar que el segmento se trate como categórico/objeto para agrupar
        df['segment'] = df['segment'].astype('category') 
        
        # Asegurar tipos numéricos donde corresponda
        df['experience_years'] = pd.to_numeric(df['experience_years'], errors='coerce')

        if df['segment'].isnull().all():
            click.echo("La columna de segmento no está poblada para ningún candidato.")
            return
            
        # Obtener segmentos únicos ordenados
        segments = sorted(df['segment'].dropna().unique())

        click.echo(f"Se encontraron {len(segments)} segmentos: {segments}")
        click.echo("-" * 30)

        for segment_id in segments:
            segment_df = df[df['segment'] == segment_id]
            click.echo() # Añadir nueva línea antes del encabezado del segmento
            click.echo(f"--- Segmento {segment_id} ({len(segment_df)} candidatos) ---")

            # Análisis numérico (ejemplo: experiencia)
            if 'experience_years' in segment_df.columns:
                click.echo() # Añadir nueva línea
                click.echo("Experiencia (años):")
                click.echo(segment_df['experience_years'].describe())

            # Análisis categórico (ejemplo: títulos)
            if 'title' in segment_df.columns:
                 click.echo() # Añadir nueva línea
                 click.echo("Habilidades Principales Principales:")
                 # Mostrar las 5 habilidades principales principales o menos
                 top_titles = segment_df['title'].value_counts().nlargest(5)
                 click.echo(top_titles.to_string())


            # Análisis categórico (ejemplo: ubicaciones)
            if 'location' in segment_df.columns:
                click.echo() # Añadir nueva línea
                click.echo("Ubicaciones Principales:")
                top_locations = segment_df['location'].value_counts().nlargest(5)
                click.echo(top_locations.to_string())

            # Análisis de habilidades (más complejo, quizás mostrar las habilidades comunes principales)
            if 'skills' in segment_df.columns and not segment_df['skills'].isnull().all():
                try:
                    # Manejar habilidades almacenadas como listas JSON
                    skills_series = segment_df['skills'].dropna()
                    
                    # Asegurarse de que solo procesamos listas reales (opcional pero más seguro)
                    skills_series = skills_series[skills_series.apply(lambda x: isinstance(x, list))]

                    if not skills_series.empty:
                        # Expandir las listas en entradas de habilidades individuales
                        exploded_skills = skills_series.explode()
                        
                        # Convertir a string, quitar espacios en blanco y filtrar vacíos
                        valid_skills = exploded_skills.astype(str).str.strip()
                        valid_skills = valid_skills[valid_skills != '']

                        if not valid_skills.empty:
                            click.echo() # Añadir nueva línea
                            click.echo("Habilidades Principales:")
                            top_skills = valid_skills.value_counts().nlargest(10)
                            click.echo(top_skills.to_string())
                        else:
                             click.echo() # Añadir nueva línea
                             click.echo("Habilidades: No se encontraron habilidades válidas después de procesar listas.")
                    else:
                        click.echo() # Añadir nueva línea
                        click.echo("Habilidades: No se encontraron datos de habilidades basados en listas para este segmento.")
                except Exception as e:
                     click.echo() # Añadir nueva línea
                     click.echo(f"Habilidades: No se pudieron procesar los datos de habilidades - {e}")


            click.echo("-" * 30)

    except Exception as e:
        click.echo(f"Error durante el análisis de segmentos: {e}", err=True)
        import traceback
        traceback.print_exc()

def register_commands(app):
    app.cli.add_command(sync)
    app.cli.add_command(setup_jobs_command)
    app.cli.add_command(train_predict_ml_command)
    app.cli.add_command(analyze_segments_command)
