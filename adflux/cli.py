import click
import json # Para impresión bonita de diccionarios
import datetime # Importar datetime para conversión de fechas
from flask import current_app # Importar current_app

# Importar funciones de generación de datos
from .data_simulation import generate_multiple_jobs, generate_multiple_candidates
# Importar factory de la app Flask y funciones de configuración de DB
from .models import create_tables, JobOpening, Candidate # Importar db para uso directo potencial posterior y modelos para sembrado
from .extensions import db # Importar db desde el módulo central de extensiones

# --- Comandos de Base de Datos ---
@click.group('data_ops')
def data_ops_group():
    """Comandos personalizados de operaciones de datos (crear, sembrar)."""
    pass

@data_ops_group.command('create')
def db_create():
    """Crea las tablas de la base de datos basadas en models.py."""
    # Usar la función create_tables que maneja el contexto de la app
    # Usar current_app proporcionado por el contexto de Flask CLI
    # Asegurarse de que create_tables exista o reemplazar con db.create_all()
    # create_tables(current_app) # Asumiendo que create_tables usa db.create_all()
    with current_app.app_context():
        try:
            db.create_all()
            click.echo('Tablas de base de datos creadas correctamente.')
        except Exception as e:
            click.echo(f'Error creando tablas: {e}', err=True)

@data_ops_group.command('seed')
@click.option('--jobs', default=20, help='Número de ofertas de trabajo a generar y sembrar.', type=int)
@click.option('--candidates', default=50, help='Número de candidatos a generar y sembrar.', type=int)
def db_seed(jobs, candidates):
    """Siembra la base de datos con datos simulados de trabajos y candidatos."""
    click.echo(f"Sembrando base de datos con {jobs} trabajos y {candidates} candidatos...")

    # Asegurar que las operaciones estén dentro del contexto de la app Flask para gestión de sesión
    # Usar current_app proporcionado por el contexto de Flask CLI
    with current_app.app_context():
        try:
            # Eliminar todas las tablas y recrearlas basadas en modelos actuales
            click.echo("Eliminando tablas existentes...")
            db.drop_all()
            click.echo("Creando tablas basadas en modelos actuales...")
            db.create_all()

            click.echo(f"Generando {jobs} trabajos y {candidates} candidatos...")
            # Generar datos
            job_data = generate_multiple_jobs(jobs)
            candidate_data = generate_multiple_candidates(candidates)

            # Crear objetos JobOpening
            for job_dict in job_data:
                # Convertir string de fecha a objeto date para compatibilidad con SQLite
                posted_date_str = job_dict.get('posted_date')
                if posted_date_str and isinstance(posted_date_str, str):
                    # Asegurar que el formato de fecha coincida con lo que provee data_simulation
                    try:
                        job_dict['posted_date'] = datetime.datetime.strptime(posted_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        click.echo(f"Advertencia: Formato de fecha inválido '{posted_date_str}' para trabajo. Estableciendo a None.", err=True)
                        job_dict['posted_date'] = None
                elif not isinstance(posted_date_str, (datetime.date, type(None))):
                    # Manejar tipos inesperados o registrar advertencia si es necesario
                    click.echo(f"Advertencia: Tipo inesperado '{type(posted_date_str)}' para fecha de trabajo. Estableciendo a None.", err=True)
                    job_dict['posted_date'] = None # Por defecto None si el formato es incorrecto

                # Asegurarse de que todos los campos requeridos estén presentes antes de crear el objeto
                # Ejemplo: Comprobar 'job_id', 'title', 'description' etc. requeridos por tu modelo
                required_fields = ['job_id', 'title', 'description', 'location'] # Ajustar según sea necesario
                if all(field in job_dict for field in required_fields):
                    job_obj = JobOpening(**job_dict) # Desempaquetar diccionario en campos del modelo
                    db.session.add(job_obj)
                else:
                     click.echo(f"Advertencia: Saltando trabajo debido a campos requeridos faltantes: {job_dict.get('job_id', 'N/A')}", err=True)

            # Crear objetos Candidate
            for cand_dict in candidate_data:
                # Añadir manejo de fecha similar para cualquier campo de fecha en el modelo Candidate si existen
                # Ejemplo (si Candidate tuviera un campo 'application_date'):
                # app_date_str = cand_dict.get('application_date')
                # if app_date_str and isinstance(app_date_str, str):
                #     cand_dict['application_date'] = datetime.datetime.strptime(app_date_str, '%Y-%m-%d').date()
                # elif not isinstance(app_date_str, (datetime.date, type(None))):
                #     cand_dict['application_date'] = None

                # Comprobar campos requeridos para Candidate
                required_candidate_fields = ['candidate_id', 'name'] # Ajustar según sea necesario
                if all(field in cand_dict for field in required_candidate_fields):
                    cand_obj = Candidate(**cand_dict)
                    db.session.add(cand_obj)
                else:
                    click.echo(f"Advertencia: Saltando candidato debido a campos requeridos faltantes: {cand_dict.get('candidate_id', 'N/A')}", err=True)

            # Confirmar la sesión para guardar objetos en la base de datos
            db.session.commit()
            click.echo("¡Base de datos sembrada correctamente!")

        except Exception as e:
            db.session.rollback() # Revertir en caso de error
            click.echo(f"Error sembrando base de datos: {e}", err=True)
            import traceback
            traceback.print_exc()

@data_ops_group.command('set-job-segments')
@click.argument('job_id', type=str)
@click.argument('segments_json', type=str)
def set_job_segments(job_id, segments_json):
    """Establece la lista JSON target_segments para una oferta de trabajo específica."""
    click.echo(f"Intentando establecer segmentos objetivo para trabajo: {job_id}")

    # Validar y analizar entrada JSON
    try:
        segment_list = json.loads(segments_json)
        if not isinstance(segment_list, list) or not all(isinstance(s, int) for s in segment_list):
            click.echo("Error: segments_json debe ser una lista JSON válida de enteros (ej., '[1, 3]').", err=True)
            return
    except json.JSONDecodeError:
        click.echo("Error: String JSON inválido proporcionado para segmentos.", err=True)
        return

    # Asegurar que las operaciones estén dentro del contexto de la app Flask
    with current_app.app_context():
        try:
            job = JobOpening.query.filter_by(job_id=job_id).first()
            if not job:
                click.echo(f"Error: Trabajo con ID {job_id} no encontrado.", err=True)
                return

            # Actualizar el campo target_segments
            job.target_segments = segment_list
            db.session.commit()
            click.echo(f"Se actualizó correctamente target_segments para trabajo {job_id} a: {segment_list}")

        except Exception as e:
            db.session.rollback()
            click.echo(f"Error actualizando segmentos de trabajo: {e}", err=True)
            import traceback
            traceback.print_exc()

# --- Comandos de Simulación de Datos (pueden ser grupo separado o eliminados si no se necesitan vía Flask CLI) ---
# Comando de ejemplo (puede ser eliminado o mantenido)
# @click.command('hello')
# def hello():
#     """Comando simple de hola."""
#     click.echo("¡Hola desde AdFlux CLI!")

# @click.command("view-jobs")
# @click.option("--count", default=5, help="Número de trabajos simulados a mostrar.", type=int)
# def view_jobs(count):
#     """Ver ofertas de trabajo simuladas."""
#     click.echo(f"--- Mostrando {count} Ofertas de Trabajo Simuladas ---")
#     jobs = generate_multiple_jobs(count)
#     # Imprimir bonitamente cada diccionario de trabajo
#     click.echo(json.dumps(jobs, indent=2))

# @click.command("view-candidates")
# @click.option("--count", default=10, help="Número de candidatos simulados a mostrar.", type=int)
# def view_candidates(count):
#     """Ver perfiles de candidatos simulados."""
#     click.echo(f"--- Mostrando {count} Perfiles de Candidato Simulados ---")
#     candidates = generate_multiple_candidates(count)
#     # Imprimir bonitamente cada diccionario de candidato
#     click.echo(json.dumps(candidates, indent=2))


# Función para registrar comandos con la app Flask
def register_commands(app):
    """Registra los grupos de comandos con la aplicación Flask."""
    app.cli.add_command(data_ops_group) # Registrar el grupo renombrado
    # Añadir otros comandos de nivel superior o grupos aquí si es necesario
    # Ejemplo: app.cli.add_command(view_jobs_command)
