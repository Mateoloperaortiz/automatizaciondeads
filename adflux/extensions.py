from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api, Namespace
from flask_apscheduler import APScheduler
from flask_marshmallow import Marshmallow
from flask_wtf.csrf import CSRFProtect
from celery import Celery

# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate(compare_type=True)
scheduler = APScheduler()
ma = Marshmallow()
csrf = CSRFProtect()

# Initialize Celery instance
celery = Celery()

# Define API object globally
api = Api(
    version='1.0',
    title='AdFlux Recruitment API',
    description='API para gestionar ofertas de trabajo y candidatos',
    validate=True
)

# --- REMOVER Definiciones de Namespace ---
# Ahora se definen en sus respectivos archivos dentro de adflux/routes/
# jobs_ns = Namespace('jobs', description='Operaciones de Ofertas de Trabajo', path='/api/v1/jobs')
# candidates_ns = Namespace('candidates', description='Operaciones de Candidatos', path='/api/v1/candidates')
# applications_ns = Namespace('applications', description='Operaciones de Aplicaciones', path='/api/v1/applications')
