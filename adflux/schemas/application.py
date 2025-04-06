"""
Esquemas de Aplicación para AdFlux.

Este módulo contiene esquemas relacionados con aplicaciones a ofertas de trabajo.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Application


class ApplicationSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo Application.
    """

    class Meta:
        model = Application
        load_instance = True
        include_fk = True  # Incluir job_id y candidate_id


# Instanciar esquemas
application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)
