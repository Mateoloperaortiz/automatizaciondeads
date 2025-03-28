"""
Notification Tasks
Celery tasks for handling notifications and real-time updates
"""

from app.utils.celery_config import celery
from app.services.notification_service import NotificationService
from app.services.entity_subscription_service import EntitySubscriptionService
import logging
import time
from celery.signals import task_failure, task_success, task_retry

logger = logging.getLogger('notification_tasks')

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_entity_update_notification(self, entity_type, entity_id, update_type, entity_data, user_id=None):
    """
    Task to send entity update notification.
    
    Args:
        entity_type (str): Type of entity (campaign, segment, etc.)
        entity_id (int): ID of the entity
        update_type (str): Type of update (created, updated, deleted, etc.)
        entity_data (dict): Entity data
        user_id (int, optional): User ID to send notification to (None for all users)
        
    Returns:
        dict: Result information
    """
    try:
        start_time = time.time()
        
        # Create notification and broadcast to WebSocket
        notification_id, broadcast_success = EntitySubscriptionService.notify_entity_update(
            entity_type=entity_type,
            entity_id=entity_id,
            update_type=update_type,
            entity_data=entity_data,
            user_id=user_id
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            'success': True,
            'notification_id': notification_id,
            'broadcast_success': broadcast_success,
            'processing_time': processing_time
        }
    except Exception as e:
        logger.error(f"Error sending entity update notification: {str(e)}")
        
        # Retry the task with exponential backoff
        retry_count = self.request.retries
        backoff = 60 * (2 ** retry_count)  # 60s, 120s, 240s
        
        # Retry up to max_retries times
        if retry_count < self.max_retries:
            logger.info(f"Retrying task in {backoff}s (attempt {retry_count + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=backoff)
        
        # Create error notification if all retries fail
        error_notification = NotificationService.create_notification(
            title=f"Failed to Process {entity_type.replace('_', ' ').title()} Update",
            message=f"An error occurred while processing {entity_type} #{entity_id} update: {str(e)}",
            type='error',
            category='system',
            related_entity_type=entity_type,
            related_entity_id=entity_id,
            extra_data={
                'error': str(e),
                'update_type': update_type,
                'retry_count': retry_count
            }
        )
        
        return {
            'success': False,
            'error': str(e),
            'retry_count': retry_count,
            'error_notification_id': error_notification.id if error_notification else None
        }

@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def process_notification_queue(self):
    """
    Process the notification queue to check for pending notifications.
    
    This task runs periodically to ensure all notifications are processed
    even if real-time delivery failed.
    """
    try:
        from app import db
        from app.models.notification import Notification
        from app.routes.websocket import emit_entity_update
        import json
        
        # Find unprocessed notifications (those with extra_data.broadcast_status not set to 'sent')
        unprocessed_notifications = Notification.query.filter(
            Notification.extra_data.isnot(None),
            ~Notification.extra_data.like('%"broadcast_status": "sent"%')
        ).limit(50).all()
        
        processed_count = 0
        
        for notification in unprocessed_notifications:
            try:
                # Get extra data
                extra_data = notification.get_extra_data()
                
                # Check if this notification has entity information
                if not (notification.related_entity_type and notification.related_entity_id):
                    continue
                
                # Get update type from extra data or default to 'updated'
                update_type = extra_data.get('update_type', 'updated')
                
                # Get entity data or use minimal data
                entity_data = extra_data.get('entity_data', {
                    'id': notification.related_entity_id,
                    'title': notification.title,
                    'message': notification.message
                })
                
                # Attempt to broadcast via WebSocket
                subscribers_notified = emit_entity_update(
                    entity_type=notification.related_entity_type,
                    entity_id=notification.related_entity_id,
                    update_type=update_type,
                    entity_data=entity_data
                )
                
                # Update notification with broadcast status
                extra_data['broadcast_status'] = 'sent'
                extra_data['broadcast_time'] = time.time()
                extra_data['subscribers_notified'] = subscribers_notified
                
                # Update notification in database
                notification.extra_data = json.dumps(extra_data)
                db.session.commit()
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing notification {notification.id}: {str(e)}")
                continue
        
        return {
            'success': True,
            'processed_count': processed_count,
            'total_unprocessed': len(unprocessed_notifications)
        }
    
    except Exception as e:
        logger.error(f"Error in process_notification_queue: {str(e)}")
        
        # Retry the task
        retry_count = self.request.retries
        if retry_count < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            'success': False,
            'error': str(e)
        }

@celery.task
def cleanup_old_notifications():
    """
    Clean up old notifications to prevent database bloat.
    """
    try:
        # Delete read notifications older than 30 days
        deleted_count = NotificationService.delete_read_notifications(days_old=30)
        
        return {
            'success': True,
            'deleted_count': deleted_count
        }
    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {str(e)}")
        
        return {
            'success': False,
            'error': str(e)
        }

# Log task failures
@task_failure.connect
def log_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, **_):
    """Log details when a task fails."""
    logger.error(
        f"Task {sender.name}[{task_id}] failed: {exception}\n"
        f"Args: {args}\nKwargs: {kwargs}"
    )

# Log task success
@task_success.connect
def log_task_success(sender=None, result=None, **_):
    """Log basic info when a task succeeds."""
    logger.info(f"Task {sender.name} completed successfully: {result}")

# Log task retry
@task_retry.connect
def log_task_retry(sender=None, request=None, reason=None, **_):
    """Log when a task is being retried."""
    logger.info(
        f"Task {sender.name} is being retried: {reason}\n"
        f"Retries: {request.retries}/{sender.max_retries}"
    )