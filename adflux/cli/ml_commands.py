"""
Comandos CLI de machine learning para AdFlux.

Este módulo contiene comandos para gestionar modelos de machine learning.
"""

import click
from flask.cli import with_appcontext
from ..tasks import trigger_train_and_predict, run_candidate_segmentation_task

# Crear grupo de comandos
ml_group = click.Group(name='ml', help='Comandos para gestionar modelos de machine learning.')


@ml_group.command('train')
@click.option('--clusters', default=5, help='Número de clústeres a crear')
@with_appcontext
def train_model_command(clusters):
    """Entrena el modelo de segmentación de candidatos."""
    click.echo(f"Entrenando modelo de segmentación con {clusters} clústeres...")
    try:
        # Llamar a la función que dispara el entrenamiento
        success, message = trigger_train_and_predict()
        if success:
            click.echo(f"Entrenamiento iniciado exitosamente: {message}")
        else:
            click.echo(f"Error iniciando entrenamiento: {message}", err=True)
    except Exception as e:
        click.echo(f"Error durante el entrenamiento del modelo: {e}", err=True)


@ml_group.command('segment')
@click.option('--candidate-id', help='ID de candidato específico para segmentar. Si no se proporciona, se segmentan todos los candidatos.')
@with_appcontext
def segment_candidates_command(candidate_id):
    """Segmenta candidatos usando el modelo entrenado."""
    if candidate_id:
        click.echo(f"Segmentando candidato {candidate_id}...")
        candidate_ids = [candidate_id]
    else:
        click.echo("Segmentando todos los candidatos...")
        candidate_ids = None
    
    try:
        # Llamar a la tarea asíncrona
        task = run_candidate_segmentation_task.delay(candidate_ids)
        click.echo(f"Tarea de segmentación iniciada en segundo plano. ID de Tarea: {task.id}")
        click.echo("Revisa los logs del worker de Celery para ver el progreso y estado de finalización.")
    except Exception as e:
        click.echo(f"Error enviando tarea de segmentación: {e}", err=True)


@ml_group.command('analyze')
@with_appcontext
def analyze_segments_command():
    """Analiza los segmentos de candidatos y muestra estadísticas."""
    click.echo("Analizando segmentos de candidatos...")
    try:
        from ..ml import analyze_segments_from_db
        
        # Obtener análisis de segmentos
        analysis = analyze_segments_from_db()
        
        if 'error' in analysis:
            click.echo(f"Error al analizar segmentos: {analysis['error']}", err=True)
            return
        
        # Mostrar estadísticas generales
        click.echo(f"Total de candidatos: {analysis.get('total_candidates', 0)}")
        click.echo(f"Número de segmentos: {analysis.get('n_segments', 0)}")
        
        # Mostrar estadísticas por segmento
        segments = analysis.get('segments', {})
        for segment_id, segment_data in segments.items():
            click.echo(f"\nSegmento {segment_id}:")
            click.echo(f"  Tamaño: {segment_data.get('size', 0)} candidatos ({segment_data.get('percentage', 0)}%)")
            click.echo(f"  Experiencia promedio: {segment_data.get('avg_experience', 'N/A')} años")
            
            # Mostrar habilidades principales
            top_skills = segment_data.get('top_primary_skills', [])
            if top_skills:
                click.echo("  Habilidades principales:")
                for skill, count in top_skills[:5]:
                    click.echo(f"    - {skill}: {count}")
            
            # Mostrar ubicaciones principales
            top_locations = segment_data.get('locations', [])
            if top_locations:
                click.echo("  Ubicaciones principales:")
                for location, count in top_locations[:5]:
                    click.echo(f"    - {location}: {count}")
    
    except Exception as e:
        click.echo(f"Error durante el análisis de segmentos: {e}", err=True)
        import traceback
        click.echo(traceback.format_exc())
