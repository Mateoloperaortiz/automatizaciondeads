from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from app.services.notification_service import NotificationService
from app.models.notification import NotificationCategory, NotificationType
from app import db

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
def list_notifications():
    """View all notifications."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get filter parameters
    category = request.args.get('category')
    unread_only = request.args.get('unread_only') == 'true'
    
    # Get notifications
    notifications = NotificationService.get_notifications(
        limit=per_page, 
        offset=offset, 
        unread_only=unread_only,
        category=category
    )
    
    # Get total count for pagination
    query = db.session.query(db.func.count()).select_from(db.session.query(db.session.get_bind()).metadata.tables['notifications'])
    if unread_only:
        query = query.filter_by(is_read=False)
    if category:
        query = query.filter_by(category=category)
    total_count = query.scalar()
    
    return render_template(
        'notifications/list.html', 
        notifications=notifications,
        page=page,
        per_page=per_page,
        total_count=total_count,
        total_pages=(total_count + per_page - 1) // per_page,
        unread_only=unread_only,
        category=category,
        categories=[c.value for c in NotificationCategory]
    )

@notifications_bp.route('/api/list')
def api_list_notifications():
    """API endpoint to get notifications in JSON format."""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    unread_only = request.args.get('unread_only') == 'true'
    category = request.args.get('category')
    
    notifications = NotificationService.get_notifications(
        limit=limit,
        offset=offset,
        unread_only=unread_only,
        category=category
    )
    
    unread_count = NotificationService.get_unread_count()
    
    return jsonify({
        'success': True,
        'data': [notification.to_dict() for notification in notifications],
        'unread_count': unread_count,
        'count': len(notifications)
    })

@notifications_bp.route('/api/mark-read/<int:notification_id>', methods=['POST'])
def api_mark_read(notification_id):
    """API endpoint to mark a notification as read."""
    success = NotificationService.mark_as_read(notification_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': NotificationService.get_unread_count()
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Notification not found'
        }), 404

@notifications_bp.route('/api/mark-all-read', methods=['POST'])
def api_mark_all_read():
    """API endpoint to mark all notifications as read."""
    category = request.json.get('category') if request.json else None
    count = NotificationService.mark_all_as_read(category)
    
    return jsonify({
        'success': True,
        'message': f'{count} notifications marked as read',
        'unread_count': NotificationService.get_unread_count()
    })

@notifications_bp.route('/api/counts')
def api_notification_counts():
    """API endpoint to get notification counts."""
    unread_total = NotificationService.get_unread_count()
    
    # Get counts by category
    counts_by_category = {}
    for category in NotificationCategory:
        counts_by_category[category.value] = NotificationService.get_unread_count(category.value)
    
    return jsonify({
        'success': True,
        'unread_total': unread_total,
        'by_category': counts_by_category
    })

@notifications_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
def mark_read(notification_id):
    """Mark a notification as read and redirect back."""
    success = NotificationService.mark_as_read(notification_id)
    
    if success:
        flash('Notification marked as read', 'success')
    else:
        flash('Notification not found', 'error')
        
    return redirect(request.referrer or url_for('notifications.list_notifications'))

@notifications_bp.route('/mark-all-read', methods=['POST'])
def mark_all_read():
    """Mark all notifications as read and redirect back."""
    category = request.form.get('category')
    count = NotificationService.mark_all_as_read(category)
    
    flash(f'{count} notifications marked as read', 'success')
    return redirect(request.referrer or url_for('notifications.list_notifications'))

@notifications_bp.route('/delete/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    """Delete a notification and redirect back."""
    success = NotificationService.delete_notification(notification_id)
    
    if success:
        flash('Notification deleted', 'success')
    else:
        flash('Notification not found', 'error')
        
    return redirect(request.referrer or url_for('notifications.list_notifications'))