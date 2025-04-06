"""
Modelo de preferencias de usuario para AdFlux.

Este módulo contiene el modelo UserPreferences que representa las preferencias
de notificación para los usuarios del sistema.
"""

from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from . import db


class UserPreferences(db.Model):
    """
    Modelo que representa las preferencias de notificación de un usuario.
    
    Permite a los usuarios configurar qué tipos de notificaciones desean recibir
    y por qué canales (email, tiempo real, etc.).
    """
    
    __tablename__ = "user_preferences"
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey("users.id"), nullable=False)
    
    notify_job_events = db.Column(Boolean, default=True, nullable=False)
    notify_candidate_events = db.Column(Boolean, default=True, nullable=False)
    notify_application_events = db.Column(Boolean, default=True, nullable=False)
    notify_campaign_events = db.Column(Boolean, default=True, nullable=False)
    notify_segmentation_events = db.Column(Boolean, default=True, nullable=False)
    notify_system_events = db.Column(Boolean, default=True, nullable=False)
    
    email_notifications = db.Column(Boolean, default=True, nullable=False)
    realtime_notifications = db.Column(Boolean, default=True, nullable=False)
    
    email_frequency = db.Column(String(20), default="immediate", nullable=False)
    
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences for user_id={self.user_id}>"
    
    def should_notify(self, category):
        """
        Determina si se debe notificar al usuario según la categoría.
        
        Args:
            category: Categoría de la notificación.
            
        Returns:
            True si se debe notificar, False en caso contrario.
        """
        if category.value == "job":
            return self.notify_job_events
        elif category.value == "candidate":
            return self.notify_candidate_events
        elif category.value == "application":
            return self.notify_application_events
        elif category.value == "campaign":
            return self.notify_campaign_events
        elif category.value == "segmentation":
            return self.notify_segmentation_events
        elif category.value == "system":
            return self.notify_system_events
        return True
    
    def should_send_email(self):
        """
        Determina si se deben enviar notificaciones por email.
        
        Returns:
            True si se deben enviar emails, False en caso contrario.
        """
        return self.email_notifications
    
    def should_send_realtime(self):
        """
        Determina si se deben enviar notificaciones en tiempo real.
        
        Returns:
            True si se deben enviar notificaciones en tiempo real, False en caso contrario.
        """
        return self.realtime_notifications
