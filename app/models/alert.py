from app import db
from datetime import datetime
import enum

class AlertType(enum.Enum):
    """Enum for alert types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Alert(db.Model):
    """Model representing a system-wide alert."""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default=AlertType.WARNING.value)
    icon = db.Column(db.String(50), nullable=True, default="alert-triangle")
    
    # Alert display controls
    active = db.Column(db.Boolean, default=True)
    dismissible = db.Column(db.Boolean, default=True)
    starts_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Alert {self.id}: {self.title}>'
    
    @property
    def is_active(self):
        """Check if the alert is currently active based on time constraints."""
        if not self.active:
            return False
            
        now = datetime.utcnow()
        
        if self.starts_at and self.starts_at > now:
            return False
            
        if self.ends_at and self.ends_at < now:
            return False
            
        return True
        
    def to_dict(self):
        """Convert alert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'icon': self.icon,
            'active': self.active,
            'dismissible': self.dismissible,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'ends_at': self.ends_at.isoformat() if self.ends_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'is_active': self.is_active
        }