"""
Rutas web para notificaciones en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de notificaciones.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from ..models.notifications.service import NotificationService
from ..models import Notification

notification_bp = Blueprint("notification", __name__, template_folder="../templates")


@notification_bp.route("/")
def list_notifications():
    """Renderiza la página de lista de notificaciones."""
    notifications = NotificationService.get_all_notifications(limit=100)
    unread_count = NotificationService.get_unread_count()
    
    return render_template(
        "notifications_list.html",
        title="Notificaciones",
        notifications=notifications,
        unread_count=unread_count
    )


@notification_bp.route("/unread")
def unread_notifications():
    """Renderiza la página de notificaciones no leídas."""
    notifications = NotificationService.get_unread_notifications(limit=100)
    unread_count = NotificationService.get_unread_count()
    
    return render_template(
        "notifications_list.html",
        title="Notificaciones no leídas",
        notifications=notifications,
        unread_count=unread_count,
        show_only_unread=True
    )


@notification_bp.route("/mark-read/<int:notification_id>", methods=["POST"])
def mark_as_read(notification_id):
    """Marca una notificación como leída."""
    notification = NotificationService.mark_as_read(notification_id)
    
    if notification:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True})
        else:
            flash(f"Notificación '{notification.title}' marcada como leída.", "success")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Notificación no encontrada"}), 404
        else:
            flash("Notificación no encontrada.", "error")
    
    return redirect(request.referrer or url_for("notification.list_notifications"))


@notification_bp.route("/mark-all-read", methods=["POST"])
def mark_all_as_read():
    """Marca todas las notificaciones como leídas."""
    count = NotificationService.mark_all_as_read()
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "count": count})
    else:
        flash(f"{count} notificaciones marcadas como leídas.", "success")
        return redirect(request.referrer or url_for("notification.list_notifications"))


@notification_bp.route("/count")
def notification_count():
    """Retorna el número de notificaciones no leídas."""
    count = NotificationService.get_unread_count()
    return jsonify({"count": count})


@notification_bp.route("/test", methods=["POST"])
def create_test_notification():
    """Crea una notificación de prueba."""
    from ..models import NotificationType, NotificationCategory
    
    notification = NotificationService.create_notification(
        title="Notificación de prueba",
        message="Esta es una notificación de prueba creada manualmente.",
        notification_type=NotificationType.INFO,
        category=NotificationCategory.SYSTEM,
        send_realtime=True
    )
    
    flash("Notificación de prueba creada exitosamente.", "success")
    return redirect(url_for("notification.list_notifications"))
