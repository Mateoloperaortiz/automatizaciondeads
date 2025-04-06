"""
Modelos de Meta Ads para AdFlux.

Este módulo contiene los modelos relacionados con Meta Ads, como campañas,
conjuntos de anuncios, anuncios e insights.
"""

import datetime
from sqlalchemy import String, DateTime, Float, Integer, JSON, Date
from . import db


class MetaCampaign(db.Model):
    """
    Modelo que representa una campaña de Meta Ads.
    
    Una campaña de Meta Ads es el nivel superior de la estructura de anuncios
    en Meta, y contiene información sobre el objetivo, presupuesto, etc.
    """
    __tablename__ = 'meta_campaigns'
    
    id = db.Column(String, primary_key=True)  # Usar el ID de Meta
    name = db.Column(String, nullable=True)
    status = db.Column(String, nullable=True)
    objective = db.Column(String, nullable=True)
    effective_status = db.Column(String, nullable=True)
    created_time = db.Column(DateTime, nullable=True)
    start_time = db.Column(DateTime, nullable=True)
    stop_time = db.Column(DateTime, nullable=True)
    daily_budget = db.Column(String, nullable=True)  # Almacenado como string desde la API
    lifetime_budget = db.Column(String, nullable=True)  # Almacenado como string desde la API
    budget_remaining = db.Column(String, nullable=True)  # Almacenado como string desde la API
    account_id = db.Column(String, nullable=False)  # Enlazar de vuelta a la Cuenta Publicitaria (aún no es un modelo aquí)
    last_updated = db.Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relaciones
    ad_sets = db.relationship('MetaAdSet', backref='campaign', lazy=True)
    
    def __repr__(self):
        return f'<MetaCampaign {self.id} ({self.name})>'


class MetaAdSet(db.Model):
    """
    Modelo que representa un conjunto de anuncios de Meta Ads.
    
    Un conjunto de anuncios de Meta Ads es el nivel intermedio de la estructura
    de anuncios en Meta, y contiene información sobre el público objetivo,
    presupuesto, optimización, etc.
    """
    __tablename__ = 'meta_ad_sets'
    
    id = db.Column(String, primary_key=True)
    name = db.Column(String, nullable=True)
    status = db.Column(String, nullable=True)
    effective_status = db.Column(String, nullable=True)
    daily_budget = db.Column(String, nullable=True)
    lifetime_budget = db.Column(String, nullable=True)
    budget_remaining = db.Column(String, nullable=True)
    optimization_goal = db.Column(String, nullable=True)
    billing_event = db.Column(String, nullable=True)
    bid_amount = db.Column(String, nullable=True)  # A menudo entero, pero se mantiene como string por seguridad
    created_time = db.Column(DateTime, nullable=True)
    start_time = db.Column(DateTime, nullable=True)
    end_time = db.Column(DateTime, nullable=True)
    campaign_id = db.Column(String, db.ForeignKey('meta_campaigns.id'), nullable=False)
    last_updated = db.Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Campos adicionales
    targeting = db.Column(JSON, nullable=True)  # Especificaciones de segmentación
    
    # Relaciones
    ads = db.relationship('MetaAd', backref='ad_set', lazy=True)
    
    def __repr__(self):
        return f'<MetaAdSet {self.id} ({self.name})>'


class MetaAd(db.Model):
    """
    Modelo que representa un anuncio de Meta Ads.
    
    Un anuncio de Meta Ads es el nivel inferior de la estructura de anuncios
    en Meta, y contiene información sobre el creativo, texto, etc.
    """
    __tablename__ = 'meta_ads'
    
    id = db.Column(String, primary_key=True)
    name = db.Column(String, nullable=True)
    status = db.Column(String, nullable=True)
    effective_status = db.Column(String, nullable=True)
    created_time = db.Column(DateTime, nullable=True)
    creative_id = db.Column(String, nullable=True)
    creative_details = db.Column(JSON, nullable=True)  # Almacenar información del creativo como JSON
    ad_set_id = db.Column(String, db.ForeignKey('meta_ad_sets.id'), nullable=False)
    last_updated = db.Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Campos adicionales
    preview_url = db.Column(String, nullable=True)  # URL de vista previa del anuncio
    
    def __repr__(self):
        return f'<MetaAd {self.id} ({self.name})>'


class MetaInsight(db.Model):
    """
    Modelo que representa insights (métricas) de Meta Ads.
    
    Los insights contienen métricas de rendimiento para campañas, conjuntos de anuncios
    y anuncios individuales, como impresiones, clics, gastos, etc.
    """
    __tablename__ = 'meta_insights'
    
    # Clave primaria compuesta: object_id, fecha y nivel
    object_id = db.Column(String, primary_key=True)
    level = db.Column(String, primary_key=True)  # 'campaign', 'adset', 'ad', 'account'
    date_start = db.Column(Date, primary_key=True)
    date_stop = db.Column(Date, nullable=False)
    
    # Métricas (usar Float para métricas que pueden ser fraccionarias)
    impressions = db.Column(Integer, nullable=True)
    clicks = db.Column(Integer, nullable=True)
    spend = db.Column(Float, nullable=True)
    cpc = db.Column(Float, nullable=True)
    cpm = db.Column(Float, nullable=True)
    ctr = db.Column(Float, nullable=True)
    cpp = db.Column(Float, nullable=True)  # Costo por resultado (a menudo usa conversión primaria)
    frequency = db.Column(Float, nullable=True)
    reach = db.Column(Integer, nullable=True)
    unique_clicks = db.Column(Integer, nullable=True)
    unique_ctr = db.Column(Float, nullable=True)
    
    # Datos de acciones sin procesar (útiles para depuración o análisis futuro)
    actions = db.Column(JSON, nullable=True)  # Array de desgloses de tipo de acción
    action_values = db.Column(JSON, nullable=True)  # Array de desgloses de valor de acción
    
    # Acciones específicas importantes (derivadas de 'actions' y 'action_values')
    submit_applications = db.Column(Integer, nullable=True)
    submit_applications_value = db.Column(Float, nullable=True)
    leads = db.Column(Integer, nullable=True)
    leads_value = db.Column(Float, nullable=True)
    view_content = db.Column(Integer, nullable=True)
    view_content_value = db.Column(Float, nullable=True)
    
    # Claves foráneas (pobladas según el nivel)
    meta_campaign_id = db.Column(String, db.ForeignKey('meta_campaigns.id'), nullable=True)
    meta_ad_set_id = db.Column(String, db.ForeignKey('meta_ad_sets.id'), nullable=True)
    meta_ad_id = db.Column(String, db.ForeignKey('meta_ads.id'), nullable=True)
    
    # Campos de auditoría
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = db.Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relaciones (Opcional: Definir si es necesario para consultar *desde* Insight)
    # COMENTADO TEMPORALMENTE - Posible causa de error de conversión marshmallow-sqlalchemy
    # campaign = db.relationship('MetaCampaign', 
    #                            primaryjoin="and_(MetaInsight.level=='campaign', MetaInsight.object_id==foreign(MetaCampaign.id))", 
    #                            backref='campaign_insights', 
    #                            uselist=False,
    #                            viewonly=True)
    # ad_set = db.relationship('MetaAdSet', 
    #                          primaryjoin="and_(MetaInsight.level=='adset', MetaInsight.object_id==foreign(MetaAdSet.id))", 
    #                          backref='ad_set_insights',
    #                          uselist=False,
    #                          viewonly=True) 
    # ad = db.relationship('MetaAd', 
    #                      primaryjoin="and_(MetaInsight.level=='ad', MetaInsight.object_id==foreign(MetaAd.id))",
    #                      backref='ad_insights',
    #                      uselist=False,
    #                      viewonly=True)
    
    def __repr__(self):
        return f'<MetaInsight {self.level}:{self.object_id} ({self.date_start})>'
