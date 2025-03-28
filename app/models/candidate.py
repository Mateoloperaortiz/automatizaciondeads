from app import db
from datetime import datetime
from typing import List, Dict, Any, Optional

class Candidate(db.Model):
    """Model representing a job candidate for audience segmentation."""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    # Basic demographic information
    name = db.Column(db.String(100), nullable=True)  # Candidate name
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    
    # Education and experience
    education_level = db.Column(db.String(50), nullable=True)  # High School, Bachelor's, Master's, etc.
    field_of_study = db.Column(db.String(100), nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    
    # Job preferences
    desired_job_type = db.Column(db.String(50), nullable=True)  # Full-time, Part-time, Contract, etc.
    desired_industry = db.Column(db.String(100), nullable=True)
    desired_role = db.Column(db.String(100), nullable=True)
    desired_salary = db.Column(db.Integer, nullable=True)
    
    # Skills and preferences
    _skills = db.Column('skills', db.JSON, nullable=True)  # List of skills
    _job_preferences = db.Column('job_preferences', db.JSON, nullable=True)  # List of job preferences
    
    # For ML segmentation
    segment_id = db.Column(db.Integer, nullable=True)  # Will be populated by the clustering algorithm
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def skills(self) -> List[str]:
        """Get list of skills."""
        if self._skills is None:
            return []
        return self._skills
    
    @skills.setter
    def skills(self, skills: List[str]):
        """Set list of skills."""
        self._skills = skills
    
    @property
    def job_preferences(self) -> List[str]:
        """Get list of job preferences."""
        if self._job_preferences is None:
            return []
        return self._job_preferences
    
    @job_preferences.setter
    def job_preferences(self, preferences: List[str]):
        """Set list of job preferences."""
        self._job_preferences = preferences
    
    def __repr__(self):
        return f'<Candidate {self.id} - {self.name or self.desired_role or "Unknown"}>'
    
    def to_dict(self):
        """Convert candidate to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'education_level': self.education_level,
            'field_of_study': self.field_of_study,
            'years_of_experience': self.years_of_experience,
            'desired_job_type': self.desired_job_type,
            'desired_industry': self.desired_industry,
            'desired_role': self.desired_role,
            'desired_salary': self.desired_salary,
            'skills': self.skills,
            'job_preferences': self.job_preferences,
            'segment_id': self.segment_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 