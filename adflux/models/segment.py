"""
Modelo de segmento para AdFlux.

Este módulo contiene el modelo Segment que representa un segmento de candidatos
generado por el proceso de machine learning.
"""

from . import db


class Segment(db.Model):
    """
    Modelo que representa un segmento de candidatos.
    
    Un segmento es un grupo de candidatos con características similares,
    generado por el proceso de machine learning.
    """
    __tablename__ = 'segments'
    
    id = db.Column(db.Integer, primary_key=True)  # El ID numérico del segmento
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relación con candidatos
    candidates = db.relationship('Candidate', backref='segment_relation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Segment {self.id}: {self.name}>'
