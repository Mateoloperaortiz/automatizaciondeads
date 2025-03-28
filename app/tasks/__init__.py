"""
Task module for handling asynchronous operations via Celery
"""

# Import tasks to register them with Celery
from app.tasks import notification_tasks