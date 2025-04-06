"""
Modelo de oferta de trabajo para AdFlux.

Este módulo contiene el modelo JobOpening que representa una oferta de trabajo.
"""

from sqlalchemy import String, Text, Date, JSON, Integer
from . import db


class JobOpening(db.Model):
    """
    Modelo que representa una oferta de trabajo.

    Una oferta de trabajo contiene información sobre un puesto disponible,
    como título, descripción, ubicación, empresa, habilidades requeridas, etc.
    """

    __tablename__ = "job_openings"

    # Coincidir campos de data_simulation.py
    job_id = db.Column(String(50), primary_key=True)  # ej., JOB-0001
    title = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    location = db.Column(String(100), nullable=True)
    company_name = db.Column(
        String(100), nullable=True, name="company"
    )  # Nombre de columna 'company' para compatibilidad

    # El tipo ARRAY puede requerir soporte específico de base de datos (como PostgreSQL)
    # Para mayor compatibilidad (como SQLite), considera almacenar como cadena JSON o tabla relacionada
    # Usando el tipo JSON para mejor compatibilidad con SQLite durante el desarrollo
    required_skills = db.Column(JSON, nullable=True)
    salary_min = db.Column(Integer, nullable=True)
    salary_max = db.Column(Integer, nullable=True)
    posted_date = db.Column(Date, nullable=True)
    status = db.Column(
        String(50), nullable=True, default="open"
    )  # Estado del trabajo (ej., abierto, cerrado)

    # Campos adicionales
    employment_type = db.Column(String(50), nullable=True)  # Full-time, Part-time, Contract, etc.
    experience_level = db.Column(String(50), nullable=True)  # Entry-level, Mid-level, Senior, etc.
    education_level = db.Column(
        String(50), nullable=True
    )  # High School, Bachelor's, Master's, etc.
    department = db.Column(String(100), nullable=True)  # Departamento de la empresa
    remote = db.Column(db.Boolean, nullable=True, default=False)  # Si es trabajo remoto
    application_url = db.Column(String(255), nullable=True)  # URL para aplicar
    closing_date = db.Column(Date, nullable=True)  # Fecha de cierre
    short_description = db.Column(String(150), nullable=True)  # Descripción corta para anuncios
    benefits = db.Column(JSON, nullable=True)  # Lista de beneficios

    # Segmentación objetivo
    target_segments = db.Column(
        JSON, nullable=True
    )  # Lista de IDs de segmentos de candidatos [1, 3]

    # Relación con Aplicaciones
    applications = db.relationship(
        "Application", backref="job", lazy=True, cascade="all, delete-orphan"
    )

    # Relación con Campañas
    campaigns = db.relationship("Campaign", backref="job_opening", lazy=True)

    def __repr__(self):
        return f"<JobOpening {self.job_id}: {self.title}>"
