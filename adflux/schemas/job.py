"""
Esquemas de Trabajo para AdFlux.

Este módulo contiene esquemas relacionados con ofertas de trabajo.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import JobOpening


class JobOpeningSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo JobOpening.
    """

    class Meta:
        model = JobOpening
        load_instance = True
        include_fk = True  # Incluir candidate_id si es necesario, o excluir si es ruidoso
        # exclude = ("applications",)  # Ejemplo: Excluir relaciones si no son necesarias para un endpoint específico


# Instanciar esquemas
job_schema = JobOpeningSchema()
jobs_schema = JobOpeningSchema(many=True)
