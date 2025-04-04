# Configuración de la aplicación Flask

import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask.cli import with_appcontext
import click
# import jinja2 # Ya no se necesita aquí
from markupsafe import Markup # Importar Markup desde markupsafe
from celery import Celery # Importar Celery
# Importar Jinja2 ChainableUndefined para depuración (opcional)
from jinja2 import ChainableUndefined
# No necesitamos importar DoExtension directamente

# Importar OBJETOS de extensión solo desde extensions.py
from .extensions import db, migrate, api, scheduler, ma, csrf, celery # Añadir celery
from .config import Config

# Importar TODOS los namespaces del paquete routes
from .routes import meta_ns, jobs_ns, candidates_ns, applications_ns, test_ns, root_ns
from .routes.task_routes import tasks_ns # Importar el nuevo namespace
# Importar el blueprint principal de rutas web
from .routes.main_routes import main_bp
# Importar el blueprint de Swagger
# from .swagger import swagger_bp # Commented out

# Retrasar otras importaciones hasta que sean necesarias
# from . import commands, models, api_clients, sync_tasks # Movido dentro de funciones

# --- Filtro Jinja Personalizado --- #
def nl2br(value):
    """Convierte saltos de línea en texto a etiquetas <br> HTML."""
    if value is None:
        return ''
    # Usar jinja2.Markup para evitar el autoescape de las etiquetas <br>
    return Markup(str(value).replace('\n', '<br>\n')) # Usar Markup directamente
# --- Fin Filtro Personalizado --- #

# --- Ayudante de Celery --- #
def make_celery(app):
    # Configurar Celery desde el objeto de configuración de la app Flask directamente
    # Las claves de configuración como CELERY_BROKER_URL y CELERY_RESULT_BACKEND
    # ya están presentes en app.config derivado de nuestra clase Config.
    # celery.config_from_object(app.config) # Esto podría ser poco fiable para broker/backend

    # Establecer explícitamente broker y backend desde la config de Flask
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']

    # Actualizar el resto de la configuración de Celery desde la config de Flask
    # Esto asegura que otras configuraciones CELERY_ se recojan si es necesario
    celery.conf.update(app.config)

    # Subclase Task para empujar automáticamente el contexto de la aplicación
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
# --- Fin Ayudante de Celery --- #

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # --- Habilitar Extensiones Jinja2 --- Usar ruta de string
    app.jinja_env.add_extension('jinja2.ext.do')
    # Establecer manejador undefined para mejor depuración (opcional)
    app.jinja_env.undefined = ChainableUndefined

    # --- Registrar Filtros Personalizados ---
    app.jinja_env.filters['nl2br'] = nl2br
    # ---------------------------

    # Asegurarse de que la carpeta instance exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Ya existe

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db) # Initialize migrate
    # Initialize API FIRST
    api.init_app(app) # Initialize API Flask-RESTX
    scheduler.init_app(app) # Restore scheduler init
    ma.init_app(app) # Initialize Marshmallow
    # Initialize CSRF AFTER API
    csrf.init_app(app) # Initialize CSRF protection
    # Initialize Celery (using the helper function)
    make_celery(app)

    # --- Registrar Namespaces con API ---
    # Es seguro hacer esto ahora porque api y app están inicializadas
    # Las rutas de los Namespaces se definen en sus respectivos archivos de ruta
    api.add_namespace(root_ns) # Registrar primero el namespace raíz
    api.add_namespace(jobs_ns)
    api.add_namespace(candidates_ns)
    api.add_namespace(applications_ns)
    # --- Exempt API namespaces from CSRF --- 
    # Add exemptions *after* the namespace has been added/registered
    # csrf.exempt(applications_ns) # Incorrect: Can't exempt Namespace directly
    # Exempt the blueprint by its registered name (likely the variable name)
    # csrf.exempt('api') # Didn't work

    # You might want to exempt other API namespaces too, e.g.:
    # csrf.exempt(jobs_ns)
    # csrf.exempt(candidates_ns)
    api.add_namespace(meta_ns)
    api.add_namespace(tasks_ns) # Registrar el nuevo namespace
    api.add_namespace(test_ns) # Registrar el namespace de prueba

    # --- Registrar Blueprints Web ---
    app.register_blueprint(main_bp) # Registrar las rutas web principales
    # Proteger explícitamente el blueprint web después del registro
    # csrf.protect(main_bp) # Remove this line - protection is default now
    # app.register_blueprint(swagger_bp) # Commented out

    # --- Configurar Trabajos Programados ---
    # Importar modelos aquí DESPUÉS de que db esté inicializado
    from . import models # Asegurar que los modelos sean conocidos por SQLAlchemy
    from . import tasks # Importar tareas DESPUÉS de que celery esté configurado

    # --- Registrar Comandos CLI (Inicialización Tardía) ---
    # Importar el módulo de comandos aquí, después de que las extensiones y blueprints estén configurados
    from . import commands
    commands.register_commands(app)
    # TAMBIÉN registrar comandos desde cli.py (que incluye el grupo de base de datos)
    from . import cli as cli_commands
    cli_commands.register_commands(app)

    # Importar otros módulos necesarios solo para el contexto (como api_clients para sync_tasks)
    # Estos podrían no ser estrictamente necesarios aquí si solo se usan dentro de contextos de request/app
    # pero importarlos asegura que se carguen.
    from . import api_clients, sync_tasks

    # --- Comprobación de Inicialización de Base de Datos (Opcional pero útil) ---
    with app.app_context():
        pass # configure_scheduled_jobs() # REMOVER - Se hará mediante comando CLI

    return app

def configure_scheduled_jobs():
    # Definir la función de tarea programada
    # Nota: Necesitamos envolver la llamada en app.app_context porque la tarea se ejecuta fuera
    # del ciclo de vida normal de la solicitud Flask pero necesita acceso a la config de la app, db, etc.
    app.logger.info("Scheduled sync job configured.") # TODO: Translate this logging message if necessary
    # Registrar el trabajo
    scheduler.add_job(id='sync_meta_all_accounts',
                      func=run_meta_sync_for_all_accounts,
                      trigger='cron',
                      hour=3, # Ejecutar diariamente a las 3 AM (ajustar según sea necesario)
                      minute=0,
                      replace_existing=True)

def run_meta_sync_for_all_accounts():
    """Función de trabajo programado para disparar la tarea de sincronización asíncrona para datos de Meta."""
    # Necesitamos el contexto de la aplicación para acceder a config, logger, etc.
    from flask import current_app
    with current_app.app_context():
        app = current_app._get_current_object() # Obtener el objeto real de la app
        logger = app.logger # Usar el logger de la app
        logger.info("Starting scheduled trigger for Meta sync...") # TODO: Translate this logging message if necessary
        # TODO: Reemplazar esto con una forma de obtener todos los IDs de cuenta relevantes
        # Por ahora, usando el del .env como ejemplo
        ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
        if ad_account_id:
            logger.info(f"Triggering async sync task for account: {ad_account_id}") # TODO: Translate this logging message if necessary
            try:
                # Importar la tarea asíncrona
                from .sync_tasks import async_sync_meta_data
                # Llamar a la tarea asíncronamente
                task = async_sync_meta_data.delay(ad_account_id, date_preset='last_7d') # Usar un preajuste por defecto razonable
                logger.info(f"Scheduled Meta sync task submitted successfully. Task ID: {task.id}") # TODO: Translate this logging message if necessary
            except Exception as e:
                logger.error(f"Error submitting scheduled Meta sync task for account {ad_account_id}: {e}", exc_info=True) # TODO: Translate this logging message if necessary
        else:
            logger.warning("META_AD_ACCOUNT_ID not found in environment. Skipping scheduled sync trigger.") # TODO: Translate this logging message if necessary
        logger.info("Scheduled trigger for Meta sync finished.") # TODO: Translate this logging message if necessary

# Para ejecutar el servidor de desarrollo (aunque usaremos principalmente CLI):
if __name__ == '__main__':
    app = create_app()
    # Para desarrollo, debug=True habilita la recarga automática y errores detallados
    app.run(debug=True) # Host por defecto='127.0.0.1', puerto=5000
