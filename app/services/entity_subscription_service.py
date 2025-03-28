"""
Entity Subscription Service
Manages subscriptions to entity updates for real-time notifications
"""

from app import db
from app.models.notification import Notification, NotificationType, NotificationCategory
from app.services.notification_service import NotificationService
import json
import logging
from datetime import datetime

logger = logging.getLogger('entity_subscription')

class EntitySubscriptionService:
    """
    Service for managing entity subscriptions and notifications
    """
    
    @staticmethod
    def notify_entity_update(entity_type, entity_id, update_type, entity_data, user_id=None):
        """
        Create notification for entity update and trigger real-time notification.
        
        Args:
            entity_type (str): Type of entity (campaign, segment, etc.)
            entity_id (int): ID of the entity
            update_type (str): Type of update (created, updated, deleted, etc.)
            entity_data (dict): Entity data
            user_id (int, optional): User ID to send notification to (None for all users)
            
        Returns:
            tuple: (notification_id, broadcast_success)
        """
        from app.routes.websocket import emit_entity_update
        
        try:
            # Determine notification type based on update type
            if update_type in ['created', 'published']:
                notification_type = NotificationType.SUCCESS
            elif update_type in ['updated', 'status_change']:
                notification_type = NotificationType.INFO
            elif update_type in ['deleted', 'cancelled']:
                notification_type = NotificationType.WARNING
            elif update_type in ['error', 'failed']:
                notification_type = NotificationType.ERROR
            else:
                notification_type = NotificationType.INFO
            
            # Map entity_type to notification category
            category_mapping = {
                'campaign': NotificationCategory.CAMPAIGN,
                'segment': NotificationCategory.SEGMENT,
                'candidate': NotificationCategory.SYSTEM,
                'job_opening': NotificationCategory.SYSTEM,
                'platform_status': NotificationCategory.API,
                'analytics': NotificationCategory.ANALYTICS,
                'task': NotificationCategory.SYSTEM,
                'user': NotificationCategory.SYSTEM,
                'team': NotificationCategory.SYSTEM,
                'credential': NotificationCategory.API,
                'alert': NotificationCategory.SYSTEM,
                'ad': NotificationCategory.CAMPAIGN,
                'notification': NotificationCategory.SYSTEM,
                'collaboration': NotificationCategory.SYSTEM,
            }
            
            notification_category = category_mapping.get(
                entity_type, NotificationCategory.SYSTEM
            )
            
            # Generate notification title and message
            entity_name = entity_data.get('name') or entity_data.get('title') or f"#{entity_id}"
            
            if update_type == 'created':
                title = f"New {entity_type.replace('_', ' ').title()}"
                message = f"A new {entity_type.replace('_', ' ')} '{entity_name}' has been created."
            elif update_type == 'updated':
                title = f"{entity_type.replace('_', ' ').title()} Updated"
                message = f"The {entity_type.replace('_', ' ')} '{entity_name}' has been updated."
            elif update_type == 'deleted':
                title = f"{entity_type.replace('_', ' ').title()} Deleted"
                message = f"The {entity_type.replace('_', ' ')} '{entity_name}' has been deleted."
            elif update_type == 'published':
                title = f"{entity_type.replace('_', ' ').title()} Published"
                message = f"The {entity_type.replace('_', ' ')} '{entity_name}' has been published."
            elif update_type == 'status_change':
                status = entity_data.get('status', 'unknown')
                title = f"{entity_type.replace('_', ' ').title()} Status Changed"
                message = f"The {entity_type.replace('_', ' ')} '{entity_name}' status changed to {status}."
            else:
                title = f"{entity_type.replace('_', ' ').title()} Update"
                message = f"The {entity_type.replace('_', ' ')} '{entity_name}' has been updated ({update_type})."
            
            # Create notification in database
            notification = NotificationService.create_notification(
                title=title,
                message=message,
                type=notification_type,
                category=notification_category,
                related_entity_type=entity_type,
                related_entity_id=entity_id,
                extra_data={
                    'update_type': update_type,
                    'entity_data': entity_data,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Broadcast to WebSocket subscribers
            subscribers_notified = emit_entity_update(
                entity_type=entity_type,
                entity_id=entity_id,
                update_type=update_type,
                entity_data=entity_data
            )
            
            logger.info(
                f"Entity update notification sent: {entity_type}:{entity_id} "
                f"({update_type}) to {subscribers_notified} subscribers"
            )
            
            return notification.id, subscribers_notified > 0
            
        except Exception as e:
            logger.error(f"Error creating entity update notification: {str(e)}")
            return None, False
    
    @staticmethod
    def track_entity_access(entity_type, entity_id, user_id=None):
        """
        Track entity access for analytics purposes.
        
        Args:
            entity_type (str): Type of entity
            entity_id (int): ID of the entity
            user_id (int, optional): User ID accessing the entity
            
        Returns:
            bool: Success status
        """
        try:
            # In a real implementation, this would track user access to entities
            # for analytics and personalization purposes
            # For now, we'll just log it
            logger.info(
                f"Entity access: {entity_type}:{entity_id} by user {user_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Error tracking entity access: {str(e)}")
            return False
    
    @staticmethod
    def get_subscriber_count(entity_type, entity_id):
        """
        Get the count of subscribers for an entity.
        
        Args:
            entity_type (str): Type of entity
            entity_id (int): ID of the entity
            
        Returns:
            int: Number of subscribers
        """
        from app.routes.websocket import entity_subscribers
        
        # Convert entity_id to string for consistency
        entity_id = str(entity_id)
        
        try:
            if entity_type in entity_subscribers and entity_id in entity_subscribers[entity_type]:
                return len(entity_subscribers[entity_type][entity_id])
            return 0
        except Exception as e:
            logger.error(f"Error getting subscriber count: {str(e)}")
            return 0