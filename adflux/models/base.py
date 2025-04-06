"""
Funciones de base de datos para AdFlux.

Este módulo contiene funciones para inicializar la conexión a la base de datos
y crear las tablas.
"""

from . import db


def create_tables(app):
    """
    Crea todas las tablas de la base de datos.

    Args:
        app: Instancia de la aplicación Flask.
    """
    with app.app_context():
        print("Creando tablas de base de datos...")
        db.create_all()
        print("Tablas creadas.")


def init_db_connection(app, database_uri):
    """
    Inicializa la conexión a la base de datos.

    Args:
        app: Instancia de la aplicación Flask.
        database_uri: URI de la base de datos.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    # Opcional: Deshabilitar el seguimiento de modificaciones si no es necesario
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    print(f"Conexión a la base de datos inicializada para URI: {database_uri}")
