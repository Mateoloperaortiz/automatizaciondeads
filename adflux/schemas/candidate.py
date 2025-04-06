"""
Esquemas de Candidato para AdFlux.

Este módulo contiene esquemas relacionados con perfiles de candidatos.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Candidate


class CandidateSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo Candidate.
    """
    class Meta:
        model = Candidate
        load_instance = True
        include_fk = True  # Incluir job_id y segment_id
        # exclude = ("applications",)  # Ejemplo: Excluir relaciones si no son necesarias para un endpoint específico


# Instanciar esquemas
candidate_schema = CandidateSchema()
candidates_schema = CandidateSchema(many=True)
