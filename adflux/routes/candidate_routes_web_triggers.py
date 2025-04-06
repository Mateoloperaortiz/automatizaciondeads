"""
Triggers de notificaciones para eventos relacionados con candidatos en AdFlux.

Este módulo contiene funciones para generar notificaciones automáticas
cuando ocurren eventos importantes relacionados con candidatos.
"""

from ..models.notifications.service import NotificationService
from ..models.notification import NotificationType, NotificationCategory


def notify_candidate_created(candidate):
    """
    Genera una notificación cuando se crea un nuevo candidato.
    
    Args:
        candidate: Objeto Candidate recién creado.
    """
    NotificationService.create_notification(
        title="Nuevo candidato registrado",
        message=f"Se ha registrado un nuevo candidato: {candidate.first_name} {candidate.last_name}.",
        notification_type=NotificationType.INFO,
        category=NotificationCategory.CANDIDATE,
        entity_type="candidate",
        entity_id=str(candidate.id),
        send_realtime=True
    )


def notify_candidate_updated(candidate):
    """
    Genera una notificación cuando se actualiza un candidato.
    
    Args:
        candidate: Objeto Candidate actualizado.
    """
    NotificationService.create_notification(
        title="Candidato actualizado",
        message=f"Se ha actualizado la información del candidato: {candidate.first_name} {candidate.last_name}.",
        notification_type=NotificationType.INFO,
        category=NotificationCategory.CANDIDATE,
        entity_type="candidate",
        entity_id=str(candidate.id),
        send_realtime=True
    )


def notify_candidate_application_created(candidate, job, application):
    """
    Genera una notificación cuando un candidato aplica a un trabajo.
    
    Args:
        candidate: Objeto Candidate que ha aplicado.
        job: Objeto JobOpening al que ha aplicado.
        application: Objeto Application recién creado.
    """
    NotificationService.create_notification(
        title="Nueva aplicación de candidato",
        message=f"{candidate.first_name} {candidate.last_name} ha aplicado al trabajo: {job.title}.",
        notification_type=NotificationType.SUCCESS,
        category=NotificationCategory.APPLICATION,
        entity_type="application",
        entity_id=str(application.id),
        send_realtime=True,
        send_email=True
    )


def notify_candidate_segmentation_complete(segment_count):
    """
    Genera una notificación cuando se completa un proceso de segmentación de candidatos.
    
    Args:
        segment_count: Número de segmentos creados.
    """
    NotificationService.create_notification(
        title="Segmentación de candidatos completada",
        message=f"Se ha completado el proceso de segmentación de candidatos. Se han creado {segment_count} segmentos.",
        notification_type=NotificationType.INFO,
        category=NotificationCategory.SEGMENTATION,
        send_realtime=True
    )
