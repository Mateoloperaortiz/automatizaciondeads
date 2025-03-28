"""
Celery configuration for background task processing.

This module sets up Celery to handle asynchronous tasks such as 
long-running ML operations and data processing.
"""

import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def make_celery(app=None):
    """
    Create a Celery instance with the given Flask app context.
    
    Args:
        app: Flask application (optional)
        
    Returns:
        Celery instance configured with the app context
    """
    # Use Redis as the broker and backend
    # Default to localhost if environment variables not set
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    celery = Celery(
        'magnetocursor',
        broker=redis_url,
        backend=redis_url,
        include=[
            'app.tasks.ml_tasks',
            'app.tasks.notification_tasks'  # Include notification tasks
        ]
    )
    
    # Set some common Celery configuration values
    celery.conf.update(
        result_expires=3600,  # Results expire after 1 hour
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        worker_prefetch_multiplier=1,  # Prevent workers from taking too many tasks at once
        task_acks_late=True,  # Tasks are acknowledged after execution (better for long tasks)
    )
    
    # Set up periodic tasks
    from celery.schedules import crontab
    celery.conf.beat_schedule = {
        'process-notification-queue-every-minute': {
            'task': 'app.tasks.notification_tasks.process_notification_queue',
            'schedule': 60.0,  # Run every 60 seconds
        },
        'cleanup-old-notifications-daily': {
            'task': 'app.tasks.notification_tasks.cleanup_old_notifications',
            'schedule': crontab(hour=3, minute=30),  # Run at 3:30 AM every day
        },
    }
    
    # If a Flask app is provided, set up a task context
    if app:
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery

# Create the Celery instance
celery = make_celery()

# If running this file directly, print configuration for debugging
if __name__ == '__main__':
    print(f"Celery broker URL: {celery.conf.get('broker_url')}")
    print(f"Celery result backend: {celery.conf.get('result_backend')}")
    print(f"Task modules: {celery.conf.get('include')}")