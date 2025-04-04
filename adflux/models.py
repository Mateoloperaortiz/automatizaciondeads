# Modelos de datos usando SQLAlchemy

from flask_sqlalchemy import SQLAlchemy
# Importar tipo JSON en lugar de ARRAY para mayor compatibilidad (SQLite)
from sqlalchemy import Integer, String, Text, Date, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import inspect # Importar inspect
import datetime

# Importar db desde el módulo central de extensiones
from .extensions import db

# --- Nuevo Modelo de Segmento --- #
class Segment(db.Model):
    __tablename__ = 'segments'
    id = db.Column(db.Integer, primary_key=True) # El ID numérico del segmento
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    candidates = db.relationship('Candidate', backref='segment_relation', lazy='dynamic')

    def __repr__(self):
        return f'<Segment {self.id}: {self.name}>'

class JobOpening(db.Model):
    """Modelo que representa una oferta de trabajo."""
    __tablename__ = 'job_openings'

    # Coincidir campos de data_simulation.py
    job_id = db.Column(String(50), primary_key=True) # ej., JOB-0001
    title = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    location = db.Column(String(100), nullable=True)
    company = db.Column(String(100), nullable=True)
    # El tipo ARRAY puede requerir soporte específico de base de datos (como PostgreSQL)
    # Para mayor compatibilidad (como SQLite), considera almacenar como cadena JSON o tabla relacionada
    # Usando el tipo JSON para mejor compatibilidad con SQLite durante el desarrollo
    required_skills = db.Column(JSON, nullable=True)
    salary_min = db.Column(Integer, nullable=True)
    salary_max = db.Column(Integer, nullable=True)
    posted_date = db.Column(Date, nullable=True)
    status = db.Column(String(50), nullable=True, default='open') # Estado del trabajo (ej., abierto, cerrado)
    
    # ---- Añadido para Segmentación Objetivo ----
    target_segments = db.Column(JSON, nullable=True) # Lista de IDs de segmentos de candidatos [1, 3]
    # -----------------------------------

    # Relación con Aplicaciones
    applications = db.relationship('Application', backref='job', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<JobOpening {self.job_id}: {self.title}>'

class Candidate(db.Model):
    """Modelo que representa un perfil de candidato."""
    __tablename__ = 'candidates'

    # Coincidir campos de data_simulation.py
    candidate_id = db.Column(String(50), primary_key=True) # ej., CAND-00001
    name = db.Column(String(100), nullable=False)
    location = db.Column(String(100), nullable=True)
    years_experience = db.Column(Integer, nullable=True)
    education_level = db.Column(String(50), nullable=True)
    # La consideración del tipo ARRAY también aplica aquí - usando JSON para compatibilidad con SQLite
    skills = db.Column(JSON, nullable=True)
    primary_skill = db.Column(String(100), nullable=True)
    desired_salary = db.Column(Integer, nullable=True)

    # ---- Actualizado para Segmentación ML ----
    # Cambiar 'segment' a 'segment_id' y añadir Clave Foránea
    segment_id = db.Column(Integer, db.ForeignKey('segments.id'), nullable=True, index=True)
    # Eliminar la columna antigua de segmento si se migra desde un estado existente donde era solo Integer
    # segment = db.Column(Integer, nullable=True, index=True) # ANTIGUO - será reemplazado por segment_id
    # -----------------------------------

    # Relación con Aplicaciones
    applications = db.relationship('Application', backref='candidate', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Candidate {self.name} ({self.candidate_id})>'

# --- Tabla de Asociación para Aplicaciones de Trabajo ---

class Application(db.Model):
    """Representa la aplicación de un candidato a una oferta de trabajo."""
    __tablename__ = 'applications'

    application_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), db.ForeignKey('job_openings.job_id'), nullable=False)
    candidate_id = db.Column(db.String(50), db.ForeignKey('candidates.candidate_id'), nullable=False)
    application_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    status = db.Column(db.String(50), nullable=False, default='Submitted') # ej., Enviada, En Revisión, Rechazada, Contratada

    # Definir restricción única para prevenir aplicaciones duplicadas
    __table_args__ = (db.UniqueConstraint('job_id', 'candidate_id', name='uq_job_candidate_application'),)

    def __repr__(self):
        return f'<Application {self.application_id} - Job: {self.job_id}, Candidate: {self.candidate_id}, Status: {self.status}>'

# --- Modelos de Anuncios Meta ---

class MetaCampaign(db.Model):
    __tablename__ = 'meta_campaigns'
    id = db.Column(db.String, primary_key=True) # Usar el ID de Meta
    name = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)
    objective = db.Column(db.String, nullable=True)
    effective_status = db.Column(db.String, nullable=True)
    created_time = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    stop_time = db.Column(db.DateTime, nullable=True)
    daily_budget = db.Column(db.String, nullable=True) # Almacenado como string desde la API
    lifetime_budget = db.Column(db.String, nullable=True) # Almacenado como string desde la API
    budget_remaining = db.Column(db.String, nullable=True) # Almacenado como string desde la API
    account_id = db.Column(db.String, nullable=False) # Enlazar de vuelta a la Cuenta Publicitaria (aún no es un modelo aquí)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    ad_sets = db.relationship('MetaAdSet', backref='campaign', lazy=True)

    def __repr__(self):
        return f'<MetaCampaign {self.id} ({self.name})>'

class MetaAdSet(db.Model):
    __tablename__ = 'meta_ad_sets'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)
    effective_status = db.Column(db.String, nullable=True)
    daily_budget = db.Column(db.String, nullable=True)
    lifetime_budget = db.Column(db.String, nullable=True)
    budget_remaining = db.Column(db.String, nullable=True)
    optimization_goal = db.Column(db.String, nullable=True)
    billing_event = db.Column(db.String, nullable=True)
    bid_amount = db.Column(db.String, nullable=True) # A menudo entero, pero se mantiene como string por seguridad
    created_time = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    campaign_id = db.Column(db.String, db.ForeignKey('meta_campaigns.id'), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    ads = db.relationship('MetaAd', backref='ad_set', lazy=True)

    def __repr__(self):
        return f'<MetaAdSet {self.id} ({self.name})>'

class MetaAd(db.Model):
    __tablename__ = 'meta_ads'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)
    effective_status = db.Column(db.String, nullable=True)
    created_time = db.Column(db.DateTime, nullable=True)
    creative_id = db.Column(db.String, nullable=True)
    creative_details = db.Column(db.JSON, nullable=True) # Almacenar información del creativo como JSON
    ad_set_id = db.Column(db.String, db.ForeignKey('meta_ad_sets.id'), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<MetaAd {self.id} ({self.name})>'

class MetaInsight(db.Model):
    __tablename__ = 'meta_insights'
    # Clave primaria compuesta: object_id, fecha y nivel
    object_id = db.Column(db.String, primary_key=True)
    level = db.Column(db.String, primary_key=True) # 'campaign', 'adset', 'ad', 'account'
    date_start = db.Column(db.Date, primary_key=True)
    date_stop = db.Column(db.Date, nullable=False)

    # Métricas (usar Float para métricas que pueden ser fraccionarias)
    impressions = db.Column(db.Integer, nullable=True)
    clicks = db.Column(db.Integer, nullable=True)
    spend = db.Column(db.Float, nullable=True)
    cpc = db.Column(db.Float, nullable=True)
    cpm = db.Column(db.Float, nullable=True)
    ctr = db.Column(db.Float, nullable=True)
    cpp = db.Column(db.Float, nullable=True) # Costo por resultado (a menudo usa conversión primaria)
    frequency = db.Column(db.Float, nullable=True)
    reach = db.Column(db.Integer, nullable=True)
    unique_clicks = db.Column(db.Integer, nullable=True)
    unique_ctr = db.Column(db.Float, nullable=True)
    # Datos de acciones sin procesar (útiles para depuración o análisis futuro)
    actions = db.Column(db.JSON, nullable=True) # Array de desgloses de tipo de acción
    action_values = db.Column(db.JSON, nullable=True) # Array de desgloses de valor de acción

    # Acciones específicas importantes (derivadas de 'actions' y 'action_values')
    submit_applications = db.Column(db.Integer, nullable=True)
    submit_applications_value = db.Column(db.Float, nullable=True)
    leads = db.Column(db.Integer, nullable=True)
    leads_value = db.Column(db.Float, nullable=True)
    view_content = db.Column(db.Integer, nullable=True)
    view_content_value = db.Column(db.Float, nullable=True)

    # Claves foráneas (pobladas según el nivel)
    meta_campaign_id = db.Column(db.String, db.ForeignKey('meta_campaigns.id'), nullable=True)
    meta_ad_set_id = db.Column(db.String, db.ForeignKey('meta_ad_sets.id'), nullable=True)
    meta_ad_id = db.Column(db.String, db.ForeignKey('meta_ads.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

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

# --- Modelo de Campaña AdFlux ---

class Campaign(db.Model):
    """Modelo que representa un concepto de campaña AdFlux de alto nivel."""
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    platform = db.Column(db.String(50), nullable=False, index=True) # ej., 'meta', 'linkedin', 'google'
    status = db.Column(db.String(50), nullable=False, default='draft', index=True) # ej., 'borrador', 'activa', 'pausada', 'archivada'
    
    # Presupuesto (en centavos)
    daily_budget = db.Column(db.Integer, nullable=True) # ej., 500 para $5.00

    # Enlace a la oferta de trabajo específica para la que es esta campaña
    job_opening_id = db.Column(db.String(50), db.ForeignKey('job_openings.job_id'), nullable=True)
    job_opening = db.relationship('JobOpening', backref='adflux_campaigns')

    # Almacenar lista de IDs de segmentos objetivo (de nuestro modelo ML)
    target_segment_ids = db.Column(db.JSON, nullable=True) 

    # Campos del Creativo Publicitario
    primary_text = db.Column(db.String(200), nullable=True)
    headline = db.Column(db.String(40), nullable=True)
    link_description = db.Column(db.String(50), nullable=True)
    creative_image_filename = db.Column(db.String(255), nullable=True) # Nombre de archivo de la imagen subida

    # Almacenar IDs después de publicar en la plataforma externa
    external_campaign_id = db.Column(db.String(255), nullable=True, index=True)
    # --- Campos específicos de Meta eliminados ---
    # external_ad_set_id = db.Column(db.String(255), nullable=True)
    # external_ad_id = db.Column(db.String(255), nullable=True)
    # external_audience_id = db.Column(db.String(255), nullable=True)
    # --- Añadido campo JSON genérico para IDs externos ---
    external_ids = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Campaign {self.id}: {self.name} ({self.platform} - {self.status})>'

# Función para crear tablas (generalmente llamada una vez durante la configuración de la aplicación)
# Esto necesita un contexto de aplicación Flask para funcionar correctamente con Flask-SQLAlchemy
def create_tables(app):
    with app.app_context():
        print("Creando tablas de base de datos...")
        db.create_all()
        print("Tablas creadas.")

# Marcador de posición para la configuración de la conexión a la base de datos (se configurará en la aplicación Flask)
def init_db_connection(app, database_uri):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    # Opcional: Deshabilitar el seguimiento de modificaciones si no es necesario
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    print(f"Conexión a la base de datos inicializada para URI: {database_uri}")

# Ejemplo de Uso (Conceptual - requiere contexto de aplicación Flask)
# if __name__ == '__main__':
#     # Este bloque necesita una aplicación Flask ficticia para proporcionar contexto para las operaciones de db
#     from flask import Flask
#     temp_app = Flask(__name__)
#     # Usar SQLite para pruebas locales simples
#     db_uri = 'sqlite:///./temp_adflux.db'
#     init_db_connection(temp_app, db_uri)
#     create_tables(temp_app)
#
#     # Ejemplo de adición de datos (requiere contexto de aplicación)
#     with temp_app.app_context():
#         # Aquí obtendrías los datos generados
#         from data_simulation import generate_job_opening
#         new_job_data = generate_job_opening(999)
#
#         # Convertir cadena de fecha a objeto de fecha si es necesario
#         new_job_data['posted_date'] = datetime.date.fromisoformat(new_job_data['posted_date'])
#
#         new_job = JobOpening(**new_job_data)
#         db.session.add(new_job)
#         db.session.commit()
#         print(f"Trabajo añadido: {new_job}")
#
#         # Consultar de nuevo
#         queried_job = db.session.get(JobOpening, 'JOB-0999') # Usar db.session.get para búsqueda por clave primaria
#         print(f"Trabajo consultado: {queried_job}")

# Nota: El modelo CandidateSegment mencionado anteriormente podría ser generado
#       por el proceso de ML en lugar de almacenarse directamente como una tabla fija.
#       Podemos añadirlo más tarde si es necesario.
