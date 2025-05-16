"""
Fábrica de aplicaciones para AdFlux.

Este módulo contiene la función create_app() que inicializa la aplicación Flask.
"""

import os
from flask import Flask
from jinja2 import ChainableUndefined
from flask_restx import Api
import logging
from logging.handlers import RotatingFileHandler

from ..config import Config
from ..extensions import db, migrate, scheduler, ma, csrf
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
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=static_folder,
        template_folder=template_folder,
    )
    app.config.from_object(config_class)

    # --- Configurar Logging --- #
    # Eliminar manejadores predeterminados si no estamos en modo debug y no usamos nuestro manejador de consola
    # O simplemente establecer el nivel y añadir nuestros manejadores.
    # Probemos añadiendo primero.
    log_formatter = logging.Formatter(app.config.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    app.logger.setLevel(log_level)

    # Manejador de consola
    if app.config.get("LOG_TO_CONSOLE", True):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(log_level)
        app.logger.addHandler(stream_handler)

    # Manejador de archivo rotatorio
    if app.config.get("LOG_TO_FILE", False):
        log_file = app.config.get("LOG_FILE", "adflux.log")
        # Asegurarse de que la ruta del log sea absoluta o relativa a la instancia
        if not os.path.isabs(log_file):
             log_file = os.path.join(app.instance_path, log_file)
        # Crear directorio si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
             try:
                  os.makedirs(log_dir)
             except OSError:
                  app.logger.error(f"No se pudo crear el directorio de logs: {log_dir}")

        # 10 MB por archivo, 5 archivos de respaldo
        file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 10, backupCount=5, encoding='utf-8')
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

    app.logger.info(f"Logging configurado. Nivel: {log_level_name}, Consola: {app.config.get('LOG_TO_CONSOLE')}, Archivo: {app.config.get('LOG_TO_FILE')}")

    # --- Habilitar Extensiones Jinja2 ---
    app.jinja_env.add_extension("jinja2.ext.do")
    # Establecer manejador undefined para mejor depuración (opcional)
    app.jinja_env.undefined = ChainableUndefined

    # --- Registrar Filtros Personalizados ---
    app.jinja_env.filters["nl2br"] = nl2br

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
        dashboard_bp,
        campaign_bp,
        segmentation_bp,
        settings_bp,
        report_bp,
        application_bp,
        candidate_mvc_bp,
    )
    from ..routes.job_routes_web import job_bp
    from ..routes.candidate_routes_web import candidate_bp
    from ..routes.main_routes import main_bp
    from ..routes.swagger_routes import swagger_bp
    from ..routes.notification_routes_web import notification_bp
    from ..routes.creative_routes import creative_bp
    from ..sse import sse_bp

    # Registrar blueprints
    app.register_blueprint(main_bp)  # Registrar primero el blueprint principal para la raíz
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(campaign_bp, url_prefix="/campaigns")
    app.register_blueprint(segmentation_bp, url_prefix="/segmentation")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(report_bp, url_prefix="/reports")
    app.register_blueprint(job_bp, url_prefix="/jobs")
    app.register_blueprint(candidate_bp, url_prefix="/candidates")
    app.register_blueprint(application_bp, url_prefix="/applications")
    app.register_blueprint(notification_bp, url_prefix="/notifications")
    app.register_blueprint(sse_bp, url_prefix="/sse")
    app.register_blueprint(swagger_bp)
    app.register_blueprint(creative_bp, url_prefix="/creative")

    # Registrar blueprints MVC
    app.register_blueprint(candidate_mvc_bp)

    # Registrar blueprint de API
    from ..routes import api_bp

    app.register_blueprint(api_bp)  # Ya tiene url_prefix='/api'

    # --- Registrar Namespaces con API ---
    with app.app_context():
        # Importar namespaces
        from ..routes import jobs_ns, candidates_ns, applications_ns, meta_ns, test_ns
        from ..routes.task_routes import tasks_ns

        # Configurar API con prefijo /api
        api = Api(
            app,
            version="1.0",
            title="AdFlux API",
            description="API para gestión de ofertas de empleo y candidatos",
            doc="/",  # Documentación en /api/
            prefix="/api",
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
        pass
        # Importar tareas después de que Celery esté configurado
        # Importar otros módulos necesarios
        from .. import api as api_module  # Renombrar para evitar conflicto con api de extensions

    # --- Registrar Comandos CLI ---
    from ..cli import register_commands

    register_commands(app)

    return app
