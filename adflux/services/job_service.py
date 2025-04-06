"""
Servicio para gestión de trabajos en AdFlux.

Este módulo centraliza la lógica de negocio relacionada con trabajos,
optimizando las consultas a la base de datos mediante joins y carga diferida.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from sqlalchemy import desc
from datetime import datetime
import uuid

from ..models import db, JobOpening
from ..models.notifications.service import NotificationService
from ..models.notification import NotificationType, NotificationCategory


class JobService:
    """
    Servicio para operaciones relacionadas con trabajos.
    
    Esta clase centraliza la lógica de negocio para operaciones CRUD y otras
    funcionalidades relacionadas con trabajos, optimizando las consultas
    mediante joins y carga diferida.
    """
    
    @staticmethod
    def get_jobs(
        page: int = 1, 
        per_page: int = 10,
        query: str = "",
        status: Optional[str] = None,
        sort_by: str = "posted_date",
        sort_order: str = "desc"
    ) -> Tuple[List[JobOpening], Any]:
        """
        Obtiene una lista paginada de trabajos con opciones de filtrado y ordenación.
        
        Args:
            page: Número de página para paginación
            per_page: Número de elementos por página
            query: Término de búsqueda para filtrar trabajos
            status: Filtro opcional por estado del trabajo
            sort_by: Campo por el cual ordenar los resultados
            sort_order: Orden de clasificación ('asc' o 'desc')
            
        Returns:
            Tupla con la lista de trabajos y el objeto de paginación
        """
        job_query = JobOpening.query
        
        if query:
            search_term = f"%{query}%"
            job_query = job_query.filter(
                db.or_(
                    JobOpening.title.ilike(search_term),
                    JobOpening.company_name.ilike(search_term),
                    JobOpening.location.ilike(search_term)
                )
            )
        
        if status:
            job_query = job_query.filter(JobOpening.status == status)
        
        sort_column = getattr(JobOpening, sort_by, JobOpening.posted_date)
        if sort_order.lower() == "desc":
            sort_column = desc(sort_column)
        
        pagination = job_query.order_by(sort_column).paginate(
            page=page, per_page=per_page, error_out=False
        )
        jobs = pagination.items
        
        return jobs, pagination
    
    @staticmethod
    def get_job_by_id(job_id: str) -> Optional[JobOpening]:
        """
        Obtiene un trabajo por su ID.
        
        Args:
            job_id: ID único del trabajo
            
        Returns:
            Objeto JobOpening o None si no se encuentra
        """
        return JobOpening.query.filter_by(job_id=job_id).first()
    
    @staticmethod
    def create_job(job_data: Dict[str, Any]) -> Tuple[Union[JobOpening, None], str, int]:
        """
        Crea un nuevo trabajo.
        
        Args:
            job_data: Diccionario con datos del trabajo
            
        Returns:
            Tupla con (trabajo creado, mensaje, código de estado)
        """
        try:
            job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
            
            if 'required_skills' in job_data and isinstance(job_data['required_skills'], str):
                job_data['required_skills'] = [skill.strip() for skill in job_data['required_skills'].split(',') if skill.strip()]
                
            if 'benefits' in job_data and isinstance(job_data['benefits'], str):
                job_data['benefits'] = [benefit.strip() for benefit in job_data['benefits'].split(',') if benefit.strip()]
            
            if 'posted_date' not in job_data or not job_data['posted_date']:
                job_data['posted_date'] = datetime.now().date()
            
            new_job = JobOpening(job_id=job_id, **job_data)
            
            db.session.add(new_job)
            db.session.commit()
            
            JobService._notify_job_created(new_job)
            
            return new_job, f"Trabajo '{new_job.title}' creado exitosamente.", 201
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error al crear trabajo: {str(e)}", 500
    
    @staticmethod
    def update_job(job_id: str, job_data: Dict[str, Any]) -> Tuple[Union[JobOpening, None], str, int]:
        """
        Actualiza un trabajo existente.
        
        Args:
            job_id: ID único del trabajo
            job_data: Diccionario con datos actualizados
            
        Returns:
            Tupla con (trabajo actualizado, mensaje, código de estado)
        """
        job = JobService.get_job_by_id(job_id)
        
        if not job:
            return None, f"Trabajo con ID {job_id} no encontrado.", 404
        
        try:
            if 'required_skills' in job_data and isinstance(job_data['required_skills'], str):
                job_data['required_skills'] = [skill.strip() for skill in job_data['required_skills'].split(',') if skill.strip()]
                
            if 'benefits' in job_data and isinstance(job_data['benefits'], str):
                job_data['benefits'] = [benefit.strip() for benefit in job_data['benefits'].split(',') if benefit.strip()]
            
            for key, value in job_data.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            db.session.commit()
            
            JobService._notify_job_updated(job)
            
            return job, f"Trabajo '{job.title}' actualizado exitosamente.", 200
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error al actualizar trabajo: {str(e)}", 500
    
    @staticmethod
    def delete_job(job_id: str) -> Tuple[bool, str, int]:
        """
        Elimina un trabajo.
        
        Args:
            job_id: ID único del trabajo
            
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        job = JobService.get_job_by_id(job_id)
        
        if not job:
            return False, f"Trabajo con ID {job_id} no encontrado.", 404
        
        try:
            db.session.delete(job)
            db.session.commit()
            
            return True, f"Trabajo eliminado exitosamente.", 204
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error al eliminar trabajo: {str(e)}", 500
    
    @staticmethod
    def _notify_job_created(job: JobOpening) -> None:
        """
        Genera una notificación cuando se crea un nuevo trabajo.
        
        Args:
            job: Objeto JobOpening recién creado
        """
        NotificationService.create_notification(
            title="Nueva oferta de trabajo registrada",
            message=f"Se ha registrado una nueva oferta de trabajo: {job.title}.",
            notification_type=NotificationType.INFO,
            category=NotificationCategory.JOB,
            entity_type="job",
            entity_id=str(job.job_id),
            send_realtime=True
        )
    
    @staticmethod
    def _notify_job_updated(job: JobOpening) -> None:
        """
        Genera una notificación cuando se actualiza un trabajo.
        
        Args:
            job: Objeto JobOpening actualizado
        """
        NotificationService.create_notification(
            title="Oferta de trabajo actualizada",
            message=f"Se ha actualizado la información de la oferta de trabajo: {job.title}.",
            notification_type=NotificationType.INFO,
            category=NotificationCategory.JOB,
            entity_type="job",
            entity_id=str(job.job_id),
            send_realtime=True
        )
