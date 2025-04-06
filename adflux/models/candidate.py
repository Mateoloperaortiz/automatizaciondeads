"""
Modelo de candidato para AdFlux.

Este módulo contiene el modelo Candidate que representa un perfil de candidato.
"""

from sqlalchemy import String, Integer, JSON
from . import db


class Candidate(db.Model):
    """
    Modelo que representa un perfil de candidato.
    
    Un candidato contiene información sobre una persona que busca empleo,
    como nombre, ubicación, experiencia, educación, habilidades, etc.
    """
    __tablename__ = 'candidates'
    
    # Coincidir campos de data_simulation.py
    candidate_id = db.Column(String(50), primary_key=True)  # ej., CAND-00001
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(100), nullable=True)
    phone = db.Column(String(20), nullable=True)
    location = db.Column(String(100), nullable=True)
    years_experience = db.Column(Integer, nullable=True)
    education_level = db.Column(String(50), nullable=True)
    
    # La consideración del tipo ARRAY también aplica aquí - usando JSON para compatibilidad con SQLite
    skills = db.Column(JSON, nullable=True)
    primary_skill = db.Column(String(100), nullable=True)
    desired_salary = db.Column(Integer, nullable=True)
    
    # Campos adicionales
    desired_position = db.Column(String(100), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    availability = db.Column(String(50), nullable=True)
    languages = db.Column(JSON, nullable=True)
    job_id = db.Column(String(50), db.ForeignKey('job_openings.job_id'), nullable=True)
    
    # Segmentación ML
    segment_id = db.Column(Integer, db.ForeignKey('segments.id'), nullable=True, index=True)
    
    # Relación con Aplicaciones
    applications = db.relationship('Application', backref='candidate', lazy=True, cascade="all, delete-orphan")
    
    # Relación con Trabajo (opcional)
    job = db.relationship('JobOpening', backref='candidates', lazy=True)
    
    def __repr__(self):
        return f'<Candidate {self.name} ({self.candidate_id})>'
