from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from app.services.alert_service import AlertService
from app.models.alert import AlertType
from app.utils.realtime import broadcast_entity_change, entity_changed
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationCategory
from datetime import datetime
import json
import logging

alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')
logger = logging.getLogger(__name__)

@alerts_bp.route('/')
def list_alerts():
    """View all alerts management page."""
    active_alerts = AlertService.get_active_alerts()
    
    return render_template(
        'alerts/list.html',
        active_alerts=active_alerts,
        alert_types=[t.value for t in AlertType]
    )

@alerts_bp.route('/api/active')
def api_active_alerts():
    """API endpoint to get active alerts."""
    active_alerts = AlertService.get_active_alerts()
    
    return jsonify({
        'success': True,
        'data': [alert.to_dict() for alert in active_alerts],
        'count': len(active_alerts)
    })

@alerts_bp.route('/api/system-alert')
def api_system_alert():
    """API endpoint to get the current system alert for the banner."""
    alert = AlertService.get_active_system_alert()
    
    return jsonify({
        'success': True,
        'has_alert': alert is not None,
        'data': alert.to_dict() if alert else None
    })

@alerts_bp.route('/api/dismiss/<int:alert_id>', methods=['POST'])
def api_dismiss_alert(alert_id):
    """API endpoint to dismiss an alert."""
    from app.models.alert import Alert
    
    # Get alert details before deactivation for broadcasting
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({
            'success': False,
            'message': 'Alert not found'
        })
    
    # Store alert data for broadcasting
    alert_data = alert.to_dict()
    
    # Deactivate the alert
    success = AlertService.deactivate_alert(alert_id)
    
    if success:
        try:
            # Broadcast alert dismissal via real-time
            entity_changed(
                entity_type='alert',
                entity_id=alert_id,
                update_type='dismissed',
                entity_data={
                    'id': alert_id,
                    'title': alert_data.get('title'),
                    'type': alert_data.get('type'),
                    'dismissed_at': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Alert dismissed: {alert_data.get('title')} (ID: {alert_id})")
        except Exception as e:
            logger.error(f"Error broadcasting alert dismissal: {str(e)}")
    
    return jsonify({
        'success': success,
        'message': 'Alert dismissed' if success else 'Alert not found'
    })

@alerts_bp.route('/create', methods=['GET', 'POST'])
def create_alert():
    """Create a new system alert."""
    if request.method == 'POST':
        # Parse form data
        title = request.form.get('title')
        message = request.form.get('message')
        alert_type = request.form.get('type', 'warning')
        icon = request.form.get('icon')
        active = request.form.get('active') == 'on'
        dismissible = request.form.get('dismissible') == 'on'
        
        # Parse dates if provided
        starts_at = None
        if request.form.get('starts_at'):
            starts_at = datetime.fromisoformat(request.form.get('starts_at').replace('Z', '+00:00'))
            
        ends_at = None
        if request.form.get('ends_at'):
            ends_at = datetime.fromisoformat(request.form.get('ends_at').replace('Z', '+00:00'))
        
        # Create the alert
        created_by = 'Admin'  # Replace with actual user info when authentication is implemented
        
        alert = AlertService.create_alert(
            title=title,
            message=message,
            type=alert_type,
            icon=icon,
            active=active,
            dismissible=dismissible,
            starts_at=starts_at,
            ends_at=ends_at,
            created_by=created_by
        )
        
        # Broadcast new alert via real-time
        try:
            # Only broadcast if alert is currently active
            if alert.is_active:
                entity_changed(
                    entity_type='alert',
                    entity_id=alert.id,
                    update_type='created',
                    entity_data=alert.to_dict()
                )
                
                # Create system notification
                priority_notification = alert_type in ['error', 'critical', 'warning']
                notification_type = NotificationType.WARNING if priority_notification else NotificationType.INFO
                
                # Create system-wide notification
                NotificationService.create_notification(
                    title=f"New {alert_type.upper()} Alert",
                    message=title,
                    type=notification_type,
                    category=NotificationCategory.SYSTEM,
                    related_entity_type="alert",
                    related_entity_id=alert.id
                )
                
                logger.info(f"New alert created and broadcast: {title} (ID: {alert.id}, Type: {alert_type})")
            else:
                logger.info(f"Alert created but not active yet: {title} (ID: {alert.id})")
        except Exception as e:
            logger.error(f"Error broadcasting new alert: {str(e)}")
        
        flash('Alert created successfully', 'success')
        return redirect(url_for('alerts.list_alerts'))
        
    return render_template(
        'alerts/create.html',
        alert_types=[t.value for t in AlertType]
    )

@alerts_bp.route('/update/<int:alert_id>', methods=['GET', 'POST'])
def update_alert(alert_id):
    """Update an existing alert."""
    from app.models.alert import Alert
    
    alert = Alert.query.get_or_404(alert_id)
    
    if request.method == 'POST':
        # Parse form data
        title = request.form.get('title')
        message = request.form.get('message')
        alert_type = request.form.get('type', 'warning')
        icon = request.form.get('icon')
        active = request.form.get('active') == 'on'
        dismissible = request.form.get('dismissible') == 'on'
        
        # Parse dates if provided
        starts_at = None
        if request.form.get('starts_at'):
            starts_at = datetime.fromisoformat(request.form.get('starts_at').replace('Z', '+00:00'))
            
        ends_at = None
        if request.form.get('ends_at'):
            ends_at = datetime.fromisoformat(request.form.get('ends_at').replace('Z', '+00:00'))
        
        # Store original values for comparison
        original_active = alert.active
        original_message = alert.message
        original_type = alert.type
        
        # Update the alert
        updated_alert = AlertService.update_alert(
            alert_id=alert_id,
            title=title,
            message=message,
            type=alert_type,
            icon=icon,
            active=active,
            dismissible=dismissible,
            starts_at=starts_at,
            ends_at=ends_at
        )
        
        # Broadcast alert update via real-time
        try:
            # Check activation status change
            activation_changed = original_active != active
            
            # If alert became active, broadcast creation
            if activation_changed and active and updated_alert.is_active:
                entity_changed(
                    entity_type='alert',
                    entity_id=alert_id,
                    update_type='created',
                    entity_data=updated_alert.to_dict()
                )
                
                logger.info(f"Alert activated: {title} (ID: {alert_id})")
            
            # If alert was deactivated, broadcast dismissal
            elif activation_changed and not active:
                entity_changed(
                    entity_type='alert',
                    entity_id=alert_id,
                    update_type='dismissed',
                    entity_data={
                        'id': alert_id,
                        'title': title,
                        'type': alert_type,
                        'dismissed_at': datetime.utcnow().isoformat()
                    }
                )
                
                logger.info(f"Alert deactivated: {title} (ID: {alert_id})")
            
            # If alert was already active and remains active, broadcast update
            elif active and updated_alert.is_active:
                entity_changed(
                    entity_type='alert',
                    entity_id=alert_id,
                    update_type='updated',
                    entity_data=updated_alert.to_dict()
                )
                
                # Create notification if important fields changed
                if original_type != alert_type or original_message != message:
                    # Create system-wide notification for important changes
                    priority_notification = alert_type in ['error', 'critical', 'warning']
                    notification_type = NotificationType.WARNING if priority_notification else NotificationType.INFO
                    
                    NotificationService.create_notification(
                        title=f"Alert Updated",
                        message=f"Alert '{title}' has been updated.",
                        type=notification_type,
                        category=NotificationCategory.SYSTEM,
                        related_entity_type="alert",
                        related_entity_id=alert_id
                    )
                
                logger.info(f"Alert updated: {title} (ID: {alert_id})")
        except Exception as e:
            logger.error(f"Error broadcasting alert update: {str(e)}")
        
        flash('Alert updated successfully', 'success')
        return redirect(url_for('alerts.list_alerts'))
        
    return render_template(
        'alerts/update.html',
        alert=alert,
        alert_types=[t.value for t in AlertType]
    )

@alerts_bp.route('/delete/<int:alert_id>', methods=['POST'])
def delete_alert(alert_id):
    """Delete an alert."""
    from app.models.alert import Alert
    from app import db
    
    alert = Alert.query.get_or_404(alert_id)
    
    # Store alert data for broadcasting
    alert_data = alert.to_dict()
    alert_title = alert.title
    alert_type = alert.type
    
    db.session.delete(alert)
    db.session.commit()
    
    # Broadcast alert deletion via real-time
    try:
        # Only broadcast if alert was active
        if alert_data.get('is_active', False):
            entity_changed(
                entity_type='alert',
                entity_id=alert_id,
                update_type='deleted',
                entity_data={
                    'id': alert_id,
                    'title': alert_title,
                    'type': alert_type,
                    'deleted_at': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Alert deleted: {alert_title} (ID: {alert_id})")
    except Exception as e:
        logger.error(f"Error broadcasting alert deletion: {str(e)}")
    
    flash('Alert deleted successfully', 'success')
    return redirect(url_for('alerts.list_alerts'))