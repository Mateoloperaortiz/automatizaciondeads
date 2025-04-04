from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from .models import MetaCampaign, MetaAdSet, MetaAd, MetaInsight, JobOpening, Candidate, Application, Campaign

# --- Esquemas de Anuncios Meta ---
class MetaInsightSchema(SQLAlchemyAutoSchema):
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
    actions = auto_field() # Marshmallow debería manejar JSON
    action_values = auto_field() # Marshmallow debería manejar JSON
    submit_applications = auto_field()
    submit_applications_value = auto_field()
    leads = auto_field()
    leads_value = auto_field()
    view_content = auto_field()
    view_content_value = auto_field()
    created_at = auto_field(dump_only=True)
    last_updated = auto_field(dump_only=True)
    meta_campaign_id = auto_field(dump_only=True) # Mantener FKs explícitas
    meta_ad_set_id = auto_field(dump_only=True)
    meta_ad_id = auto_field(dump_only=True)

    class Meta:
        model = MetaInsight
        load_instance = True

class MetaAdSchema(SQLAlchemyAutoSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    effective_status = fields.Str(allow_none=True)
    created_time = fields.DateTime(allow_none=True)
    creative_id = fields.Str(allow_none=True)
    creative_details = fields.Dict(allow_none=True) # Asumiendo que creative_details se almacena como JSON/Dict
    # Campos de relación
    ad_set_id = fields.Str()
    # Insights anidados (opcional)
    # insights = fields.Nested(MetaInsightSchema, many=True)

    class Meta:
        model = MetaAd
        load_instance = True

class MetaAdSetSchema(SQLAlchemyAutoSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    effective_status = fields.Str(allow_none=True)
    daily_budget = fields.Str(allow_none=True) # Meta a menudo devuelve presupuestos como strings
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

# --- Esquemas de Trabajo, Candidato, Aplicación ---

class JobOpeningSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = JobOpening
        load_instance = True
        include_fk = True # Incluir candidate_id si es necesario, o excluir si es ruidoso
        # exclude = ("applications",) # Ejemplo: Excluir relaciones si no son necesarias para un endpoint específico

class CandidateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Candidate
        load_instance = True
        # exclude = ("applications",) # Ejemplo: Excluir relaciones

class ApplicationSchema(SQLAlchemyAutoSchema):
    # Explicitly define FK fields to ensure correct type (String) during loading
    job_id = fields.String(required=True)
    candidate_id = fields.String(required=True)

    class Meta:
        model = Application
        load_instance = True
        include_fk = True
        # Quizás quieras anidar esquemas relacionados aquí para respuestas más detalladas
        # job = ma.Nested(JobOpeningSchema, only=("id", "title"))
        # candidate = ma.Nested(CandidateSchema, only=("id", "first_name", "last_name", "email"))

# --- Esquemas de Campaña AdFlux (Único y Múltiple) ---

class CampaignSchema(SQLAlchemyAutoSchema):
    # Opcionalmente incluir detalles anidados de JobOpening
    job_opening = fields.Nested(JobOpeningSchema, only=("job_id", "title"))
    # Definir el campo de segmentos objetivo (esperando una lista de enteros)
    target_segment_ids = fields.List(fields.Integer(), allow_none=True)

    class Meta:
        model = Campaign
        load_instance = True
        include_fk = True # Incluir job_opening_id
        # Hacer que los IDs externos sean de solo lectura en las respuestas de la API (se establecen internamente)
        dump_only = ("id", "created_at", "updated_at", 
                     "external_campaign_id", "external_ad_set_id", 
                     "external_ad_id", "external_audience_id") 

# --- Instanciar Esquemas ---

# Esquemas Meta (Único y Múltiple)
meta_campaign_schema = MetaCampaignSchema()
meta_campaigns_schema = MetaCampaignSchema(many=True)
meta_ad_set_schema = MetaAdSetSchema()
meta_ad_sets_schema = MetaAdSetSchema(many=True)
meta_ad_schema = MetaAdSchema()
meta_ads_schema = MetaAdSchema(many=True)
meta_insight_schema = MetaInsightSchema()
meta_insights_schema = MetaInsightSchema(many=True)

# Esquemas de Trabajo (Único y Múltiple)
job_schema = JobOpeningSchema()
jobs_schema = JobOpeningSchema(many=True)

# Esquemas de Candidato (Único y Múltiple)
candidate_schema = CandidateSchema()
candidates_schema = CandidateSchema(many=True)

# Esquemas de Aplicación (Único y Múltiple)
application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)

# Esquemas de Campaña (Único y Múltiple)
campaign_schema = CampaignSchema()
campaigns_schema = CampaignSchema(many=True)
