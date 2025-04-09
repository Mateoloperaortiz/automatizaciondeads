"""
Servicio de notificaciones para AdFlux.

Este módulo contiene el servicio que gestiona la creación, envío y gestión
de notificaciones en el sistema.
"""

from datetime import datetime
from flask import current_app
from ...models import db, Notification, NotificationType, NotificationCategory
from ...extensions import celery


class NotificationService:
    """
    Servicio para gestionar notificaciones en el sistema.
    
    Este servicio proporciona métodos para crear, enviar y gestionar
    notificaciones, incluyendo notificaciones en tiempo real y por email.
    """
    
    @staticmethod
    def create_notification(
        title,
        message,
        notification_type=NotificationType.INFO,
        category=NotificationCategory.SYSTEM,
        entity_type=None,
        entity_id=None,
        task_id=None,
        send_email=False,
        send_realtime=True
    ):
        """
        Crea una nueva notificación en el sistema.
        
        Args:
            title: Título de la notificación.
            message: Mensaje detallado de la notificación.
            notification_type: Tipo de notificación (INFO, SUCCESS, WARNING, ERROR, TASK).
            category: Categoría de la notificación (SYSTEM, JOB, CANDIDATE, etc.).
            entity_type: Tipo de entidad relacionada con la notificación.
            entity_id: ID de la entidad relacionada.
            task_id: ID de la tarea de Celery relacionada.
            send_email: Si se debe enviar la notificación por email.
            send_realtime: Si se debe enviar la notificación en tiempo real.
            
        Returns:
            La notificación creada.
        """
        notification = Notification(
            title=title,
            message=message,
            type=notification_type,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            task_id=task_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        if send_realtime:
            NotificationService.send_realtime_notification(notification)
        
        if send_email:
            NotificationService.send_email_notification.delay(notification.id)
        
        return notification
    
    @staticmethod
    def get_unread_count():
        """
        Obtiene el número total de notificaciones no leídas.
        
        Returns:
            Número entero de notificaciones no leídas.
        """
        try:
            return Notification.query.filter_by(is_read=False).count()
        except Exception as e:
            current_app.logger.error(f"Error al contar notificaciones no leídas: {e}", exc_info=True)
            return 0 # Devolver 0 en caso de error
    
    @staticmethod
    def get_unread_notifications(limit=10):
        """
        Obtiene las notificaciones no leídas más recientes.
        
        Args:
            limit: Número máximo de notificaciones a retornar.
            
        Returns:
            Lista de notificaciones no leídas.
        """
        return Notification.query.filter_by(is_read=False).order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_all_notifications(limit=50):
        """
        Obtiene todas las notificaciones, ordenadas por fecha de creación.
        
        Args:
            limit: Número máximo de notificaciones a retornar.
            
        Returns:
            Lista de notificaciones.
        """
        return Notification.query.order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def mark_as_read(notification_id):
        """
        Marca una notificación como leída.
        
        Args:
            notification_id: ID de la notificación a marcar.
            
        Returns:
            La notificación actualizada o None si no se encuentra.
        """
        notification = Notification.query.get(notification_id)
        if notification:
            notification.mark_as_read()
            return notification
        return None
    
    @staticmethod
    def mark_all_as_read():
        """
        Marca todas las notificaciones como leídas.
        
        Returns:
            Número de notificaciones actualizadas.
        """
        now = datetime.utcnow()
        result = Notification.query.filter_by(is_read=False).update({
            "is_read": True,
            "read_at": now
        })
        db.session.commit()
        return result
    
    @staticmethod
    def send_realtime_notification(notification):
        """
        Envía una notificación en tiempo real usando SSE.
        
        Args:
            notification: Objeto Notification a enviar.
            
        Returns:
            True si se envió correctamente, False en caso contrario.
        """
        try:
            from ...sse import push_notification
            
            notification_data = notification.to_dict()
            
            push_notification(notification_data)
            
            notification.realtime_sent = True
            notification.realtime_status = "delivered"
            db.session.commit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error al enviar notificación en tiempo real: {e}")
            return False
    
    @celery.task
    def send_email_notification(notification_id):
        """
        Tarea de Celery para enviar una notificación por email.
        
        Args:
            notification_id: ID de la notificación a enviar.
            
        Returns:
            True si se envió correctamente, False en caso contrario.
        """
        try:
            from ...email import send_email
            
            notification = Notification.query.get(notification_id)
            if not notification:
                return False
            
            
            notification.email_sent = True
            notification.email_status = "delivered"
            db.session.commit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error al enviar notificación por email: {e}")
            return False
