from app import db
from app.models.alert import Alert, AlertType
from datetime import datetime

class AlertService:
    """Service for managing system-wide alerts."""
    
    @staticmethod
    def create_alert(title, message, type=AlertType.WARNING, icon=None, 
                   active=True, dismissible=True, starts_at=None, ends_at=None, created_by=None):
        """
        Create a new system-wide alert.
        
        Args:
            title (str): Alert title
            message (str): Alert message
            type (AlertType): Alert type (info, success, warning, error, critical)
            icon (str, optional): Custom icon for the alert
            active (bool): Whether the alert is active
            dismissible (bool): Whether users can dismiss the alert
            starts_at (datetime, optional): When the alert should start being shown
            ends_at (datetime, optional): When the alert should stop being shown
            created_by (str, optional): Who created the alert
            
        Returns:
            Alert: The created alert object
        """
        # Set default icon based on type if not provided
        if not icon:
            if type == AlertType.SUCCESS or type.value == 'success':
                icon = 'check-circle'
            elif type == AlertType.ERROR or type.value == 'error':
                icon = 'alert-octagon'
            elif type == AlertType.CRITICAL or type.value == 'critical':
                icon = 'alert-circle'
            elif type == AlertType.INFO or type.value == 'info':
                icon = 'info'
            else:  # WARNING
                icon = 'alert-triangle'
        
        # Convert enum to string value if needed
        if isinstance(type, AlertType):
            type = type.value
            
        # Create alert
        alert = Alert(
            title=title,
            message=message,
            type=type,
            icon=icon,
            active=active,
            dismissible=dismissible,
            starts_at=starts_at,
            ends_at=ends_at,
            created_by=created_by
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    @staticmethod
    def get_active_alerts():
        """
        Get all currently active alerts.
        
        Returns:
            list: List of active alert objects
        """
        now = datetime.utcnow()
        
        return Alert.query.filter(
            Alert.active == True,
            (Alert.starts_at.is_(None) | (Alert.starts_at <= now)),
            (Alert.ends_at.is_(None) | (Alert.ends_at >= now))
        ).order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def get_active_system_alert():
        """
        Get the most important currently active alert for display in the global banner.
        Prioritizes by type (critical > error > warning > info > success).
        
        Returns:
            Alert: The most important active alert, or None if no active alerts
        """
        active_alerts = AlertService.get_active_alerts()
        
        if not active_alerts:
            return None
            
        # Priority order
        priority_types = ['critical', 'error', 'warning', 'info', 'success']
        
        # Sort by priority
        active_alerts.sort(key=lambda alert: priority_types.index(alert.type) 
                                if alert.type in priority_types else 999)
        
        return active_alerts[0] if active_alerts else None
    
    @staticmethod
    def deactivate_alert(alert_id):
        """
        Deactivate an alert.
        
        Args:
            alert_id (int): ID of the alert to deactivate
            
        Returns:
            bool: True if successful, False otherwise
        """
        alert = Alert.query.get(alert_id)
        if not alert:
            return False
            
        alert.active = False
        db.session.commit()
        return True
    
    @staticmethod
    def update_alert(alert_id, **kwargs):
        """
        Update an alert's properties.
        
        Args:
            alert_id (int): ID of the alert to update
            **kwargs: Key-value pairs of properties to update
            
        Returns:
            Alert: The updated alert, or None if alert not found
        """
        alert = Alert.query.get(alert_id)
        if not alert:
            return None
            
        # Update allowed properties
        allowed_props = [
            'title', 'message', 'type', 'icon',
            'active', 'dismissible', 'starts_at', 'ends_at'
        ]
        
        for key, value in kwargs.items():
            if key in allowed_props:
                setattr(alert, key, value)
                
        db.session.commit()
        return alert