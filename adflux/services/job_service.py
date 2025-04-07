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
from ..api.common.excepciones import ErrorValidacion
from .base_service import BaseService
from ..utils.validation import ValidationUtils


class JobService(BaseService[JobOpening]):
    """
    Servicio para operaciones relacionadas con trabajos.
    
    Esta clase centraliza la lógica de negocio para operaciones CRUD y otras
    funcionalidades relacionadas con trabajos, optimizando las consultas
    mediante joins y carga diferida.
    """
    
    model_class = JobOpening
    id_attribute = "job_id"
    entity_name = "trabajo"
    
    @classmethod
    def get_jobs(
        cls,
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
        page, per_page = ValidationUtils.validate_pagination_params(page, per_page)
        
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
    
    @classmethod
    def get_job_by_id(cls, job_id: str) -> Optional[JobOpening]:
        """
        Obtiene un trabajo por su ID.
        
        Args:
            job_id: ID único del trabajo
                
        Returns:
            Objeto JobOpening o None si no se encuentra
        """
        return cls.get_by_id(job_id)
    
    @classmethod
    def create_job(cls, job_data: Dict[str, Any]) -> Tuple[Union[JobOpening, None], str, int]:
        """
        Crea un nuevo trabajo.
        
        Args:
            job_data: Diccionario con datos del trabajo
                
        Returns:
            Tupla con (trabajo creado, mensaje, código de estado)
        """
        ValidationUtils.validate_required_fields(job_data, ["title"])
        
        if "salary_min" in job_data and "salary_max" in job_data:
            if job_data["salary_min"] is not None and job_data["salary_max"] is not None:
                if job_data["salary_min"] > job_data["salary_max"]:
                    raise ErrorValidacion(
                        mensaje="El salario mínimo no puede ser mayor que el salario máximo",
                        errores={"salary_min": ["Debe ser menor o igual al salario máximo"]}
                    )
        
        job_data["job_id"] = f"JOB-{uuid.uuid4().hex[:8].upper()}"
        
        job, mensaje, codigo = cls.create(job_data)
        
        if job:
            cls._notify_job_created(job)
            return job, f"Trabajo '{job.title}' creado exitosamente.", codigo
        
        return job, mensaje, codigo
    
    @classmethod
    def update_job(cls, job_id: str, job_data: Dict[str, Any]) -> Tuple[Union[JobOpening, None], str, int]:
        """
        Actualiza un trabajo existente.
        
        Args:
            job_id: ID único del trabajo
            job_data: Diccionario con datos actualizados
                
        Returns:
            Tupla con (trabajo actualizado, mensaje, código de estado)
        """
        if "salary_min" in job_data and "salary_max" in job_data:
            if job_data["salary_min"] is not None and job_data["salary_max"] is not None:
                if job_data["salary_min"] > job_data["salary_max"]:
                    raise ErrorValidacion(
                        mensaje="El salario mínimo no puede ser mayor que el salario máximo",
                        errores={"salary_min": ["Debe ser menor o igual al salario máximo"]}
                    )
        
        job, mensaje, codigo = cls.update(job_id, job_data)
        
        if job:
            cls._notify_job_updated(job)
            return job, f"Trabajo '{job.title}' actualizado exitosamente.", codigo
        
        return job, mensaje, codigo
    
    @classmethod
    def delete_job(cls, job_id: str) -> Tuple[bool, str, int]:
        """
        Elimina un trabajo.
        
        Args:
            job_id: ID único del trabajo
                
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        return cls.delete(job_id)
    
    @classmethod
    def _preprocess_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocesa datos antes de crear o actualizar un trabajo.
        
        Args:
            data: Diccionario con datos a procesar
                
        Returns:
            Diccionario con datos procesados
        """
        processed_data = data.copy()
        
        if 'required_skills' in processed_data and isinstance(processed_data['required_skills'], str):
            processed_data['required_skills'] = ValidationUtils.string_to_list(processed_data['required_skills'])
        
        if 'benefits' in processed_data and isinstance(processed_data['benefits'], str):
            processed_data['benefits'] = ValidationUtils.string_to_list(processed_data['benefits'])
        
        if 'posted_date' not in processed_data or not processed_data['posted_date']:
            processed_data['posted_date'] = datetime.now().date()
        
        return processed_data
    
    @classmethod
    def _notify_job_created(cls, job: JobOpening) -> None:
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
    
    @classmethod
    def _notify_job_updated(cls, job: JobOpening) -> None:
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
