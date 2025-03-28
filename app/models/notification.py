from app import db
from datetime import datetime
import enum
import json

class NotificationType(enum.Enum):
    """Enum for notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    
class NotificationCategory(enum.Enum):
    """Enum for notification categories."""
    CAMPAIGN = "campaign"
    API = "api"
    SEGMENT = "segment"
    SYSTEM = "system"
    ANALYTICS = "analytics"

class Notification(db.Model):
    """Model representing a notification."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default=NotificationType.INFO.value)
    category = db.Column(db.String(20), nullable=False, default=NotificationCategory.SYSTEM.value)
    icon = db.Column(db.String(50), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional reference to related entities
    related_entity_type = db.Column(db.String(50), nullable=True)  # e.g., 'campaign', 'platform', etc.
    related_entity_id = db.Column(db.Integer, nullable=True)       # ID of the related entity
    
    # Additional data as JSON
    extra_data = db.Column(db.Text, nullable=True)  # JSON string for additional data
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'
    
    @property
    def formatted_created_at(self):
        """Return a human-readable created_at time."""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            if diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return self.created_at.strftime("%b %d, %Y")
        
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        
        minutes = (diff.seconds % 3600) // 60
        if minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        
        return "Just now"
    
    def get_extra_data(self):
        """Parse and return the extra_data JSON."""
        if not self.extra_data:
            return {}
        try:
            return json.loads(self.extra_data)
        except:
            return {}
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'category': self.category,
            'icon': self.icon,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'formatted_time': self.formatted_created_at,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'extra_data': self.get_extra_data()
        }