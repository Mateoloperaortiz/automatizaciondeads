"""
Modelo de aplicación para AdFlux.

Este módulo contiene el modelo Application que representa la aplicación
de un candidato a una oferta de trabajo.
"""

import datetime
from sqlalchemy import String, Date
from . import db


class Application(db.Model):
    """
    Modelo que representa la aplicación de un candidato a una oferta de trabajo.
    
    Una aplicación vincula a un candidato con una oferta de trabajo específica,
    y contiene información sobre la fecha de aplicación y el estado.
    """
    __tablename__ = 'applications'
    
    application_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(String(50), db.ForeignKey('job_openings.job_id'), nullable=False)
    candidate_id = db.Column(String(50), db.ForeignKey('candidates.candidate_id'), nullable=False)
    application_date = db.Column(Date, nullable=False, default=datetime.date.today)
    status = db.Column(String(50), nullable=False, default='Submitted')  # ej., Enviada, En Revisión, Rechazada, Contratada
    source_platform = db.Column(String(50), nullable=True)  # ej., Meta, Google, LinkedIn, Direct
    
    # Campos adicionales
    notes = db.Column(db.Text, nullable=True)
    resume_path = db.Column(String(255), nullable=True)
    cover_letter_path = db.Column(String(255), nullable=True)
    
    # Definir restricción única para prevenir aplicaciones duplicadas
    __table_args__ = (db.UniqueConstraint('job_id', 'candidate_id', name='uq_job_candidate_application'),)
    
    def __repr__(self):
        return f'<Application {self.application_id} - Job: {self.job_id}, Candidate: {self.candidate_id}, Status: {self.status}>'
