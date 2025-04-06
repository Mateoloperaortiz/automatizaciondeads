"""
Esquemas de Campaña para AdFlux.

Este módulo contiene esquemas relacionados con campañas publicitarias.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Campaign


class CampaignSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo Campaign.
    """

    class Meta:
        model = Campaign
        load_instance = True
        include_fk = True  # Incluir job_opening_id


# Instanciar esquemas
campaign_schema = CampaignSchema()
campaigns_schema = CampaignSchema(many=True)
