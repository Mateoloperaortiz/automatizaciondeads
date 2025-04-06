"""
Modelo de notificación para AdFlux.

Este módulo contiene el modelo Notification que representa una notificación
para los usuarios del sistema.
"""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Enum
import enum
from . import db


class NotificationType(enum.Enum):
    """Tipos de notificaciones soportadas por el sistema."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    TASK = "task"


class NotificationCategory(enum.Enum):
    """Categorías de notificaciones para agrupar por funcionalidad."""
    SYSTEM = "system"
    JOB = "job"
    CANDIDATE = "candidate"
    APPLICATION = "application"
    CAMPAIGN = "campaign"
    SEGMENTATION = "segmentation"


class DeliveryStatus(enum.Enum):
    """Estado de entrega de la notificación."""
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"


class Notification(db.Model):
    """
    Modelo que representa una notificación en el sistema.
    
    Una notificación contiene información sobre un evento que ocurrió
    en el sistema y que debe ser comunicado a los usuarios.
    """
    
    __tablename__ = "notifications"
    
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(100), nullable=False)
    message = db.Column(Text, nullable=False)
    type = db.Column(Enum(NotificationType), default=NotificationType.INFO, nullable=False)
    category = db.Column(Enum(NotificationCategory), default=NotificationCategory.SYSTEM, nullable=False)
    
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = db.Column(Boolean, default=False, nullable=False)
    read_at = db.Column(DateTime, nullable=True)
    
    entity_type = db.Column(String(50), nullable=True)  # 'job', 'candidate', 'application', etc.
    entity_id = db.Column(String(50), nullable=True)    # ID de la entidad relacionada
    
    task_id = db.Column(String(50), nullable=True)      # ID de la tarea de Celery
    
    email_sent = db.Column(Boolean, default=False, nullable=False)
    email_status = db.Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=True)
    
    realtime_sent = db.Column(Boolean, default=False, nullable=False)
    realtime_status = db.Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=True)
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"
    
    def mark_as_read(self):
        """Marca la notificación como leída."""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_unread(self):
        """Marca la notificación como no leída."""
        self.is_read = False
        self.read_at = None
        db.session.commit()
    
    def to_dict(self):
        """Convierte la notificación a un diccionario para APIs y SSE."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type.value,
            "category": self.category.value,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "task_id": self.task_id
        }
