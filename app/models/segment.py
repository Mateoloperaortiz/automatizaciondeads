from app import db
from datetime import datetime
from typing import List, Optional

class Segment(db.Model):
    """Model representing a candidate segment for targeted advertising."""
    __tablename__ = 'segments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    segment_code = db.Column(db.String(50), nullable=True)  # Unique code for the segment (e.g., CLUSTER_0)
    criteria = db.Column(db.JSON, nullable=True)  # Stores the criteria used for segmentation
    _candidate_ids = db.Column('candidate_ids', db.JSON, nullable=True)  # Store candidate IDs directly for ML integration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidates = db.relationship('Candidate', secondary='candidate_segments', backref=db.backref('segments', lazy='dynamic'))
    
    @property
    def candidate_ids(self) -> List[int]:
        """Get list of candidate IDs in this segment."""
        if self._candidate_ids is None:
            return []
        return self._candidate_ids
    
    @candidate_ids.setter
    def candidate_ids(self, ids: List[int]):
        """Set list of candidate IDs in this segment."""
        self._candidate_ids = ids
    
    def __repr__(self):
        return f'<Segment {self.name}>'
    
    def to_dict(self):
        """Convert segment to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'segment_code': self.segment_code,
            'description': self.description,
            'criteria': self.criteria,
            'candidate_count': len(self.candidate_ids),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Association table for many-to-many relationship between candidates and segments
candidate_segments = db.Table('candidate_segments',
    db.Column('candidate_id', db.Integer, db.ForeignKey('candidates.id'), primary_key=True),
    db.Column('segment_id', db.Integer, db.ForeignKey('segments.id'), primary_key=True),
    db.Column('score', db.Float, nullable=True),  # Optional: track match score for each candidate-segment pair
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
) 