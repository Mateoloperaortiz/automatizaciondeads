"""
Esquemas de Meta para AdFlux.

Este módulo contiene esquemas relacionados con Meta Ads, como campañas,
conjuntos de anuncios, anuncios e insights.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from ..models import MetaCampaign, MetaAdSet, MetaAd, MetaInsight


class MetaInsightSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo MetaInsight.
    """
    # Definir explícitamente TODOS los campos usando auto_field
    object_id = auto_field(dump_only=True)
    level = auto_field(dump_only=True)
    date_start = auto_field(dump_only=True)
    date_stop = auto_field()
    impressions = auto_field()
    clicks = auto_field()
    spend = auto_field()
    cpc = auto_field()
    cpm = auto_field()
    ctr = auto_field()
    cpp = auto_field()
    frequency = auto_field()
    reach = auto_field()
    unique_clicks = auto_field()
    unique_ctr = auto_field()
    actions = auto_field()  # Marshmallow debería manejar JSON
    action_values = auto_field()  # Marshmallow debería manejar JSON
    submit_applications = auto_field()
    submit_applications_value = auto_field()
    leads = auto_field()
    leads_value = auto_field()
    view_content = auto_field()
    view_content_value = auto_field()
    created_at = auto_field(dump_only=True)
    last_updated = auto_field(dump_only=True)
    meta_campaign_id = auto_field(dump_only=True)  # Mantener FKs explícitas
    meta_ad_set_id = auto_field(dump_only=True)
    meta_ad_id = auto_field(dump_only=True)

    class Meta:
        model = MetaInsight
        load_instance = True


class MetaAdSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo MetaAd.
    """
    id = fields.Str(dump_only=True)
    name = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    effective_status = fields.Str(allow_none=True)
    created_time = fields.DateTime(allow_none=True)
    creative_id = fields.Str(allow_none=True)
    creative_details = fields.Dict(allow_none=True)  # Asumiendo que creative_details se almacena como JSON/Dict
    # Campos de relación
    ad_set_id = fields.Str()
    # Insights anidados (opcional)
    # insights = fields.Nested(MetaInsightSchema, many=True)

    class Meta:
        model = MetaAd
        load_instance = True


class MetaAdSetSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo MetaAdSet.
    """
    id = fields.Str(dump_only=True)
    name = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    effective_status = fields.Str(allow_none=True)
    daily_budget = fields.Str(allow_none=True)  # Meta a menudo devuelve presupuestos como strings
    lifetime_budget = fields.Str(allow_none=True)
    budget_remaining = fields.Str(allow_none=True)
    optimization_goal = fields.Str(allow_none=True)
    billing_event = fields.Str(allow_none=True)
    bid_amount = fields.Int(allow_none=True)
    created_time = fields.DateTime(allow_none=True)
    start_time = fields.DateTime(allow_none=True)
    end_time = fields.DateTime(allow_none=True)
    # Campos de relación
    campaign_id = fields.Str()
    # Anuncios o insights anidados (opcional)
    # ads = fields.Nested(MetaAdSchema, many=True)
    # insights = fields.Nested(MetaInsightSchema, many=True)

    class Meta:
        model = MetaAdSet
        load_instance = True


class MetaCampaignSchema(SQLAlchemyAutoSchema):
    """
    Esquema para el modelo MetaCampaign.
    """
    id = fields.Str(dump_only=True)
    name = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    objective = fields.Str(allow_none=True)
    effective_status = fields.Str(allow_none=True)
    created_time = fields.DateTime(allow_none=True)
    start_time = fields.DateTime(allow_none=True)
    stop_time = fields.DateTime(allow_none=True)
    daily_budget = fields.Str(allow_none=True)
    lifetime_budget = fields.Str(allow_none=True)
    budget_remaining = fields.Str(allow_none=True)
    # Campos de relación
    account_id = fields.Str()
    # Conjuntos de anuncios o insights anidados (opcional)
    # ad_sets = fields.Nested(MetaAdSetSchema, many=True)
    # insights = fields.Nested(MetaInsightSchema, many=True)

    class Meta:
        model = MetaCampaign
        load_instance = True


# Instanciar esquemas
meta_campaign_schema = MetaCampaignSchema()
meta_campaigns_schema = MetaCampaignSchema(many=True)
meta_ad_set_schema = MetaAdSetSchema()
meta_ad_sets_schema = MetaAdSetSchema(many=True)
meta_ad_schema = MetaAdSchema()
meta_ads_schema = MetaAdSchema(many=True)
meta_insight_schema = MetaInsightSchema()
meta_insights_schema = MetaInsightSchema(many=True)
