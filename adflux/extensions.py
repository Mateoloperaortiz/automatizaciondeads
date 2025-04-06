from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from flask_apscheduler import APScheduler
from flask_marshmallow import Marshmallow
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from celery import Celery

# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate(compare_type=True)
scheduler = APScheduler()
ma = Marshmallow()
csrf = CSRFProtect()
mail = Mail()

# Initialize Celery instance
celery = Celery()

# Define API object globally
api = Api(
    version="1.0",
    title="AdFlux Recruitment API",
    description="API para gestionar ofertas de trabajo y candidatos",
    validate=True,
)
