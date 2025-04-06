"""
Servicio para gestión de aplicaciones en AdFlux.

Este módulo centraliza la lógica de negocio relacionada con aplicaciones,
optimizando las consultas a la base de datos mediante joins y carga diferida.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from ..models import db, Application, JobOpening, Candidate
from ..models.notifications.service import NotificationService
from ..models.notification import NotificationType, NotificationCategory


class ApplicationService:
    """
    Servicio para operaciones relacionadas con aplicaciones.
    
    Esta clase centraliza la lógica de negocio para operaciones CRUD y otras
    funcionalidades relacionadas con aplicaciones, optimizando las consultas
    mediante joins y carga diferida.
    """
    
    @staticmethod
    def get_applications(
        page: int = 1, 
        per_page: int = 10,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "application_date",
        sort_order: str = "desc"
    ) -> Tuple[List[Application], Any]:
        """
        Obtiene una lista paginada de aplicaciones con opciones de filtrado y ordenación.
        
        Args:
            page: Número de página para paginación
            per_page: Número de elementos por página
            job_id: Filtro opcional por ID de trabajo
            candidate_id: Filtro opcional por ID de candidato
            status: Filtro opcional por estado de aplicación
            sort_by: Campo por el cual ordenar los resultados
            sort_order: Orden de clasificación ('asc' o 'desc')
            
        Returns:
            Tupla con la lista de aplicaciones y el objeto de paginación
        """
        query = Application.query.options(
            joinedload(Application.job),
            joinedload(Application.candidate)
        )
        
        if job_id:
            query = query.filter(Application.job_id == job_id)
        if candidate_id:
            query = query.filter(Application.candidate_id == candidate_id)
        if status:
            query = query.filter(Application.status == status)
        
        sort_column = getattr(Application, sort_by, Application.application_date)
        if sort_order.lower() == "desc":
            sort_column = desc(sort_column)
        
        pagination = query.order_by(sort_column).paginate(
            page=page, per_page=per_page, error_out=False
        )
        applications = pagination.items
        
        return applications, pagination
    
    @staticmethod
    def get_application_by_id(application_id: int) -> Optional[Application]:
        """
        Obtiene una aplicación por su ID con carga anticipada de relaciones.
        
        Args:
            application_id: ID único de la aplicación
            
        Returns:
            Objeto Application o None si no se encuentra
        """
        return Application.query.options(
            joinedload(Application.job),
            joinedload(Application.candidate)
        ).filter_by(application_id=application_id).first()
    
    @staticmethod
    def create_application(application_data: Dict[str, Any]) -> Tuple[Union[Application, None], str, int]:
        """
        Crea una nueva aplicación.
        
        Args:
            application_data: Diccionario con datos de la aplicación
            
        Returns:
            Tupla con (aplicación creada, mensaje, código de estado)
        """
        try:
            job_id = application_data.get('job_id')
            candidate_id = application_data.get('candidate_id')
            
            job = JobOpening.query.filter_by(job_id=job_id).first()
            if not job:
                return None, f"Trabajo con ID {job_id} no encontrado.", 404
                
            candidate = Candidate.query.filter_by(candidate_id=candidate_id).first()
            if not candidate:
                return None, f"Candidato con ID {candidate_id} no encontrado.", 404
            
            existing = Application.query.filter_by(
                job_id=job_id, candidate_id=candidate_id
            ).first()
            
            if existing:
                return None, "El candidato ya ha aplicado a esta oferta de trabajo.", 409
            
            new_application = Application(**application_data)
            
            db.session.add(new_application)
            db.session.commit()
            
            ApplicationService._notify_application_created(new_application, job, candidate)
            
            return new_application, "Aplicación creada exitosamente.", 201
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error al crear aplicación: {str(e)}", 500
    
    @staticmethod
    def update_application(application_id: int, application_data: Dict[str, Any]) -> Tuple[Union[Application, None], str, int]:
        """
        Actualiza una aplicación existente.
        
        Args:
            application_id: ID único de la aplicación
            application_data: Diccionario con datos actualizados
            
        Returns:
            Tupla con (aplicación actualizada, mensaje, código de estado)
        """
        application = ApplicationService.get_application_by_id(application_id)
        
        if not application:
            return None, f"Aplicación con ID {application_id} no encontrada.", 404
        
        try:
            allowed_fields = ['status', 'notes']
            for key, value in application_data.items():
                if key in allowed_fields and hasattr(application, key):
                    setattr(application, key, value)
            
            db.session.commit()
            
            if 'status' in application_data:
                ApplicationService._notify_application_updated(application)
            
            return application, "Aplicación actualizada exitosamente.", 200
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error al actualizar aplicación: {str(e)}", 500
    
    @staticmethod
    def delete_application(application_id: int) -> Tuple[bool, str, int]:
        """
        Elimina una aplicación.
        
        Args:
            application_id: ID único de la aplicación
            
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        application = ApplicationService.get_application_by_id(application_id)
        
        if not application:
            return False, f"Aplicación con ID {application_id} no encontrada.", 404
        
        try:
            db.session.delete(application)
            db.session.commit()
            
            return True, "Aplicación eliminada exitosamente.", 204
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error al eliminar aplicación: {str(e)}", 500
    
    @staticmethod
    def _notify_application_created(application: Application, job: JobOpening, candidate: Candidate) -> None:
        """
        Genera una notificación cuando se crea una nueva aplicación.
        
        Args:
            application: Objeto Application recién creado
            job: Objeto JobOpening asociado
            candidate: Objeto Candidate asociado
        """
        NotificationService.create_notification(
            title="Nueva aplicación recibida",
            message=f"El candidato {candidate.name} ha aplicado al trabajo {job.title}.",
            notification_type=NotificationType.INFO,
            category=NotificationCategory.APPLICATION,
            entity_type="application",
            entity_id=str(application.application_id),
            send_realtime=True
        )
    
    @staticmethod
    def _notify_application_updated(application: Application) -> None:
        """
        Genera una notificación cuando se actualiza una aplicación.
        
        Args:
            application: Objeto Application actualizado
        """
        job = application.job
        candidate = application.candidate
        
        if not job:
            job = JobOpening.query.filter_by(job_id=application.job_id).first()
        
        if not candidate:
            candidate = Candidate.query.filter_by(candidate_id=application.candidate_id).first()
        
        if job and candidate:
            NotificationService.create_notification(
                title="Aplicación actualizada",
                message=f"La aplicación de {candidate.name} para {job.title} ha sido actualizada a estado: {application.status}.",
                notification_type=NotificationType.INFO,
                category=NotificationCategory.APPLICATION,
                entity_type="application",
                entity_id=str(application.application_id),
                send_realtime=True
            )
