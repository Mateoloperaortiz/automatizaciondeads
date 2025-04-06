"""
Módulo de envío de emails para AdFlux.

Este módulo proporciona funcionalidad para enviar emails de notificación
a los usuarios del sistema.
"""

from flask import current_app, render_template
from flask_mail import Message
from .extensions import mail


def send_email(subject, recipients, template, **kwargs):
    """
    Envía un email usando una plantilla HTML.
    
    Args:
        subject: Asunto del email.
        recipients: Lista de destinatarios.
        template: Nombre de la plantilla HTML a usar.
        **kwargs: Variables para renderizar la plantilla.
        
    Returns:
        True si el email se envió correctamente, False en caso contrario.
    """
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@adflux.com")
        )
        
        msg.html = render_template(f"emails/{template}.html", **kwargs)
        
        msg.body = render_template(f"emails/{template}.txt", **kwargs)
        
        mail.send(msg)
        
        current_app.logger.info(f"Email enviado a {recipients}: {subject}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar email: {e}")
        return False


def send_notification_email(notification, recipient_email):
    """
    Envía un email de notificación.
    
    Args:
        notification: Objeto Notification a enviar.
        recipient_email: Email del destinatario.
        
    Returns:
        True si el email se envió correctamente, False en caso contrario.
    """
    try:
        template = "notification"
        
        return send_email(
            subject=f"AdFlux: {notification.title}",
            recipients=[recipient_email],
            template=template,
            notification=notification
        )
    except Exception as e:
        current_app.logger.error(f"Error al enviar email de notificación: {e}")
        return False
