"""
Fábrica de aplicaciones para AdFlux.

Este módulo contiene la función create_app() que inicializa la aplicación Flask.
"""

import os
from flask import Flask
from jinja2 import ChainableUndefined
from flask_restx import Api

from ..config import Config
from ..extensions import db, migrate, scheduler, ma, csrf, celery
from .celery_utils import make_celery
from .jinja_utils import nl2br


def create_app(config_class=Config):
    """
    Crea y configura la aplicación Flask.

    Args:
        config_class: Clase de configuración a utilizar.

    Returns:
        Aplicación Flask configurada.
    """
    # Definir rutas relativas al paquete adflux, no al módulo core
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

    app = Flask(__name__,
              instance_relative_config=True,
              static_folder=static_folder,
              template_folder=template_folder)
    app.config.from_object(config_class)

    # --- Habilitar Extensiones Jinja2 ---
    app.jinja_env.add_extension('jinja2.ext.do')
    # Establecer manejador undefined para mejor depuración (opcional)
    app.jinja_env.undefined = ChainableUndefined

    # --- Registrar Filtros Personalizados ---
    app.jinja_env.filters['nl2br'] = nl2br

    # Asegurarse de que la carpeta instance exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # Ya existe

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    migrate.init_app(app, db)
    # Inicializar API PRIMERO
    # api.init_app(app) - Ahora creamos la API más adelante
    scheduler.init_app(app)
    ma.init_app(app)
    # Inicializar CSRF DESPUÉS de API
    csrf.init_app(app)
    # Inicializar Celery
    make_celery(app)

    # --- Registrar Blueprints Web ---
    # Importar blueprints
    from ..routes import (
        dashboard_bp, campaign_bp, segmentation_bp,
        settings_bp, report_bp, job_bp, candidate_bp,
        application_bp
    )
    from ..routes.main_routes import main_bp
    from ..routes.swagger_routes import swagger_bp

    # Registrar blueprints
    app.register_blueprint(main_bp)  # Registrar primero el blueprint principal para la raíz
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(campaign_bp, url_prefix='/campaigns')
    app.register_blueprint(segmentation_bp, url_prefix='/segmentation')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(job_bp, url_prefix='/jobs')
    app.register_blueprint(candidate_bp, url_prefix='/candidates')
    app.register_blueprint(application_bp, url_prefix='/applications')
    app.register_blueprint(swagger_bp)

    # Registrar blueprint de API
    from ..routes import api_bp
    app.register_blueprint(api_bp)  # Ya tiene url_prefix='/api'

    # --- Registrar Namespaces con API ---
    with app.app_context():
        # Importar namespaces
        from ..routes import (
            root_ns, jobs_ns, candidates_ns, applications_ns,
            meta_ns, test_ns
        )
        from ..routes.task_routes import tasks_ns

        # Configurar API con prefijo /api
        api = Api(
            app,
            version='1.0',
            title='AdFlux API',
            description='API para gestión de ofertas de empleo y candidatos',
            doc='/',  # Documentación en /api/
            prefix='/api'
        )

        # Registrar namespaces
        # No registramos root_ns para que no interfiera con la documentación de Swagger
        # api.add_namespace(root_ns)
        api.add_namespace(jobs_ns)
        api.add_namespace(candidates_ns)
        api.add_namespace(applications_ns)
        api.add_namespace(meta_ns)
        api.add_namespace(tasks_ns)
        api.add_namespace(test_ns)

    # --- Importar Módulos Necesarios ---
    with app.app_context():
        # Importar modelos para que SQLAlchemy los conozca
        from .. import models
        # Importar tareas después de que Celery esté configurado
        from .. import tasks
        # Importar otros módulos necesarios
        from .. import api as api_module  # Renombrar para evitar conflicto con api de extensions
        from ..tasks import sync_tasks

    # --- Registrar Comandos CLI ---
    from ..cli import register_commands
    register_commands(app)

    return app
