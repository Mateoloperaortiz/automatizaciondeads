from app import db
from app.models.notification import Notification, NotificationType, NotificationCategory
import json
from sqlalchemy import desc

class NotificationService:
    """Service for managing application notifications."""
    
    @staticmethod
    def create_notification(title, message, type=NotificationType.INFO, category=NotificationCategory.SYSTEM, 
                          icon=None, related_entity_type=None, related_entity_id=None, extra_data=None):
        """
        Create a new notification in the database.
        
        Args:
            title (str): The notification title
            message (str): The notification message
            type (NotificationType): The notification type (info, success, warning, error)
            category (NotificationCategory): The notification category
            icon (str, optional): Custom icon for the notification
            related_entity_type (str, optional): Type of related entity
            related_entity_id (int, optional): ID of related entity
            extra_data (dict, optional): Additional JSON data to store
            
        Returns:
            Notification: The created notification object
        """
        # Set default icon based on type if not provided
        if not icon:
            if type == NotificationType.SUCCESS or type.value == 'success':
                icon = 'check-circle'
            elif type == NotificationType.WARNING or type.value == 'warning':
                icon = 'alert-triangle'
            elif type == NotificationType.ERROR or type.value == 'error':
                icon = 'alert-octagon'
            else:  # INFO
                icon = 'info'
        
        # Convert enum to string value if needed
        if isinstance(type, NotificationType):
            type = type.value
        if isinstance(category, NotificationCategory):
            category = category.value
            
        # Convert extra_data to JSON string if provided
        extra_data_json = None
        if extra_data:
            extra_data_json = json.dumps(extra_data)
        
        # Create notification
        notification = Notification(
            title=title,
            message=message,
            type=type,
            category=category,
            icon=icon,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            extra_data=extra_data_json
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def get_notifications(limit=10, offset=0, unread_only=False, category=None):
        """
        Get notifications, with optional filtering.
        
        Args:
            limit (int): Maximum number of notifications to return
            offset (int): Offset for pagination
            unread_only (bool): If True, return only unread notifications
            category (str): Filter by category
            
        Returns:
            list: List of notification objects
        """
        query = Notification.query.order_by(desc(Notification.created_at))
        
        if unread_only:
            query = query.filter_by(is_read=False)
            
        if category:
            if isinstance(category, NotificationCategory):
                category = category.value
            query = query.filter_by(category=category)
            
        return query.limit(limit).offset(offset).all()
    
    @staticmethod
    def get_unread_count(category=None):
        """
        Get count of unread notifications.
        
        Args:
            category (str, optional): Filter by category
            
        Returns:
            int: Count of unread notifications
        """
        query = Notification.query.filter_by(is_read=False)
        
        if category:
            if isinstance(category, NotificationCategory):
                category = category.value
            query = query.filter_by(category=category)
            
        return query.count()
    
    @staticmethod
    def mark_as_read(notification_id):
        """
        Mark a notification as read.
        
        Args:
            notification_id (int): ID of notification to mark as read
            
        Returns:
            bool: True if successful, False otherwise
        """
        notification = Notification.query.get(notification_id)
        if not notification:
            return False
            
        notification.is_read = True
        db.session.commit()
        return True
    
    @staticmethod
    def mark_all_as_read(category=None):
        """
        Mark all notifications as read, optionally filtered by category.
        
        Args:
            category (str, optional): Category to filter by
            
        Returns:
            int: Number of notifications marked as read
        """
        query = Notification.query.filter_by(is_read=False)
        
        if category:
            if isinstance(category, NotificationCategory):
                category = category.value
            query = query.filter_by(category=category)
            
        count = query.count()
        
        for notification in query.all():
            notification.is_read = True
            
        db.session.commit()
        return count
    
    @staticmethod
    def delete_notification(notification_id):
        """
        Delete a notification.
        
        Args:
            notification_id (int): ID of notification to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        notification = Notification.query.get(notification_id)
        if not notification:
            return False
            
        db.session.delete(notification)
        db.session.commit()
        return True
    
    @staticmethod
    def delete_read_notifications(days_old=30):
        """
        Delete read notifications older than a certain number of days.
        
        Args:
            days_old (int): Delete notifications older than this many days
            
        Returns:
            int: Number of notifications deleted
        """
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        query = Notification.query.filter(
            Notification.is_read == True,
            Notification.created_at < cutoff_date
        )
        
        count = query.count()
        
        for notification in query.all():
            db.session.delete(notification)
            
        db.session.commit()
        return count