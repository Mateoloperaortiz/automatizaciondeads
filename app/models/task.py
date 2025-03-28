"""
Task model for tracking the status of background tasks.
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Text, or_

class Task(db.Model):
    """Model for tracking Celery task status."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True)  # Celery task ID
    name = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, RUNNING, SUCCESS, FAILURE, REVOKED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.JSON, nullable=True)  # Will fallback to Text for SQLite
    error = db.Column(db.Text, nullable=True)
    
    # Association with user (if applicable)
    user_id = db.Column(db.Integer, nullable=True)
    
    @classmethod
    def create_task(cls, task_id, task_name, user_id=None):
        """Create a new task record."""
        task = cls(
            id=task_id,
            name=task_name,
            status='PENDING',
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        return task
    
    @classmethod
    def update_status(cls, task_id, status, result=None, error=None):
        """Update task status and result."""
        task = cls.query.get(task_id)
        if not task:
            return False
            
        task.status = status
        
        if status == 'RUNNING':
            task.started_at = datetime.utcnow()
        elif status in ['SUCCESS', 'FAILURE', 'REVOKED']:
            task.completed_at = datetime.utcnow()
            
        if result is not None:
            task.result = result
            
        if error is not None:
            task.error = error
            
        db.session.commit()
        return True
    
    @classmethod
    def get_active_tasks(cls):
        """Get all active tasks (pending or running)."""
        return cls.query.filter(
            or_(cls.status == 'PENDING', cls.status == 'RUNNING')
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent_tasks(cls, limit=10):
        """Get recent tasks, regardless of status."""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    def to_dict(self):
        """Convert task to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else None,
            'result': self.result,
            'error': self.error,
            'user_id': self.user_id
        }