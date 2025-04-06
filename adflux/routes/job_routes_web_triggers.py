"""
Triggers de notificaciones para eventos relacionados con trabajos en AdFlux.

Este módulo contiene funciones para generar notificaciones automáticas
cuando ocurren eventos importantes relacionados con trabajos.
"""

from ..models.notifications.service import NotificationService
from ..models.notification import NotificationType, NotificationCategory


def notify_job_created(job):
    """
    Genera una notificación cuando se crea un nuevo trabajo.
    
    Args:
        job: Objeto JobOpening recién creado.
    """
    NotificationService.create_notification(
        title="Nuevo trabajo creado",
        message=f"Se ha creado un nuevo trabajo: {job.title} en {job.company_name}.",
        notification_type=NotificationType.INFO,
        category=NotificationCategory.JOB,
        entity_type="job",
        entity_id=str(job.id),
        send_realtime=True
    )


def notify_job_updated(job):
    """
    Genera una notificación cuando se actualiza un trabajo.
    
    Args:
        job: Objeto JobOpening actualizado.
    """
    NotificationService.create_notification(
        title="Trabajo actualizado",
        message=f"Se ha actualizado el trabajo: {job.title} en {job.company_name}.",
        notification_type=NotificationType.INFO,
        category=NotificationCategory.JOB,
        entity_type="job",
        entity_id=str(job.id),
        send_realtime=True
    )


def notify_job_campaign_created(job, campaign):
    """
    Genera una notificación cuando se crea una campaña para un trabajo.
    
    Args:
        job: Objeto JobOpening asociado a la campaña.
        campaign: Objeto Campaign recién creado.
    """
    NotificationService.create_notification(
        title="Nueva campaña creada",
        message=f"Se ha creado una nueva campaña para el trabajo: {job.title}.",
        notification_type=NotificationType.SUCCESS,
        category=NotificationCategory.CAMPAIGN,
        entity_type="campaign",
        entity_id=str(campaign.id),
        send_realtime=True,
        send_email=True
    )


def notify_job_campaign_status_change(job, campaign, old_status, new_status):
    """
    Genera una notificación cuando cambia el estado de una campaña.
    
    Args:
        job: Objeto JobOpening asociado a la campaña.
        campaign: Objeto Campaign cuyo estado ha cambiado.
        old_status: Estado anterior de la campaña.
        new_status: Nuevo estado de la campaña.
    """
    NotificationService.create_notification(
        title="Cambio de estado en campaña",
        message=f"La campaña para el trabajo '{job.title}' ha cambiado de estado: {old_status} → {new_status}.",
        notification_type=NotificationType.INFO,
        category=NotificationCategory.CAMPAIGN,
        entity_type="campaign",
        entity_id=str(campaign.id),
        send_realtime=True
    )
