from app import db
from datetime import datetime

class JobOpening(db.Model):
    """Model representing a job opening to be advertised."""
    __tablename__ = 'job_openings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    salary_range = db.Column(db.String(50), nullable=True)
    job_type = db.Column(db.String(50), nullable=False)  # Full-time, Part-time, Contract, etc.
    experience_level = db.Column(db.String(50), nullable=True)  # Entry, Mid, Senior
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    campaigns = db.relationship('AdCampaign', backref='job_opening', lazy=True)
    
    def __repr__(self):
        return f'<JobOpening {self.title} at {self.company}>'
    
    def to_dict(self):
        """Convert job opening to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'requirements': self.requirements,
            'salary_range': self.salary_range,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'active': self.active
        } 