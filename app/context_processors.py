"""Template context processors for the MagnetoCursor application."""

from flask import current_app
from app.models.platform_connection_status import PlatformConnectionStatus
from app.services.alert_service import AlertService
from app.services.notification_service import NotificationService


def platform_status():
    """Add platform connection status to template context."""
    platform_statuses = PlatformConnectionStatus.get_all_platforms()
    
    # Calculate connected count
    connected_platforms = sum(1 for status in platform_statuses if status.is_connected)
    total_platforms = len(platform_statuses)
    
    return {
        'platforms': platform_statuses,
        'connected_platforms': connected_platforms,
        'total_platforms': total_platforms
    }


def notification_context():
    """Add notification information to template context."""
    # Get active system alert for banner
    try:
        active_system_alert = AlertService.get_active_system_alert()
    except Exception:
        # Handle case where alert system is not yet set up (e.g., before migrations)
        active_system_alert = None
    
    # Get unread notification count
    try:
        unread_notification_count = NotificationService.get_unread_count()
    except Exception:
        # Handle case where notification system is not yet set up
        unread_notification_count = 0
    
    return {
        'active_system_alert': active_system_alert,
        'unread_notification_count': unread_notification_count
    }


def utility_processor():
    """Add utility functions to template context."""
    return {
        'get_platform_icon': lambda platform: PlatformConnectionStatus.PLATFORM_ICONS.get(
            platform, 'fas fa-globe'
        ),
        'get_platform_name': lambda platform: PlatformConnectionStatus.PLATFORM_NAMES.get(
            platform, platform.capitalize()
        )
    }


def register_context_processors(app):
    """Register all context processors with the Flask app."""
    app.context_processor(platform_status)
    app.context_processor(notification_context)
    app.context_processor(utility_processor)