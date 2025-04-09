"""
Servicio para gestión de candidatos en AdFlux.

Este módulo centraliza la lógica de negocio relacionada con candidatos,
eliminando duplicación entre rutas API y web.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from sqlalchemy import or_

from ..models import db, Candidate, Segment
from ..models.notifications.service import NotificationService
from ..models.notification import NotificationType, NotificationCategory
import uuid
from flask import current_app


class CandidateService:
    """
    Servicio para operaciones relacionadas con candidatos.
    
    Esta clase centraliza la lógica de negocio para operaciones CRUD y otras
    funcionalidades relacionadas con candidatos.
    """
    
    @staticmethod
    def get_candidates(
        page: int = 1, 
        per_page: int = 10, 
        query: str = "", 
        sort_by: str = "name",
        sort_order: str = "asc",
        segment_filter: Optional[str] = None
    ) -> Tuple[List[Candidate], Any]:
        """
        Obtiene una lista paginada de candidatos con opciones de filtrado y ordenación.
        
        Args:
            page: Número de página para paginación
            per_page: Número de elementos por página
            query: Término de búsqueda para filtrar candidatos
            sort_by: Campo por el cual ordenar los resultados
            sort_order: Orden de clasificación ('asc' o 'desc')
            segment_filter: Filtro opcional por ID de segmento
            
        Returns:
            Tupla con la lista de candidatos y el objeto de paginación
        """
        candidate_query = Candidate.query
        
        if segment_filter is not None:
            if segment_filter.lower() == "none":
                candidate_query = candidate_query.filter(Candidate.segment_id.is_(None))
            else:
                try:
                    segment_id = int(segment_filter)
                    candidate_query = candidate_query.filter(Candidate.segment_id == segment_id)
                except ValueError:
                    pass
        
        if query:
            search_term = f"%{query}%"
            candidate_query = candidate_query.filter(
                or_(Candidate.name.ilike(search_term), Candidate.primary_skill.ilike(search_term))
            )
        
        sort_column = getattr(
            Candidate, sort_by if sort_by != "segment" else "segment_id", Candidate.name
        )
        if sort_order == "desc":
            sort_column = sort_column.desc()
        
        pagination = candidate_query.order_by(sort_column).paginate(
            page=page, per_page=per_page, error_out=False
        )
        candidates = pagination.items
        
        return candidates, pagination
    
    @staticmethod
    def get_candidate_by_id(candidate_id: str) -> Optional[Candidate]:
        """
        Obtiene un candidato por su ID.
        
        Args:
            candidate_id: ID único del candidato
            
        Returns:
            Objeto Candidate o None si no se encuentra
        """
        return Candidate.query.filter_by(candidate_id=candidate_id).first()
    
    @staticmethod
    def get_candidate_details(candidate_id: str) -> Tuple[Optional[Candidate], Optional[str]]:
        """
        Obtiene un candidato por su ID junto con el nombre de su segmento.

        Args:
            candidate_id: ID único del candidato

        Returns:
            Tupla con (objeto Candidate, nombre del segmento) o (None, None) si no se encuentra.
        """
        candidate = CandidateService.get_candidate_by_id(candidate_id)
        if not candidate:
            return None, None

        segment_name = None
        if candidate.segment_id:
            try:
                # Usar consulta simple para obtener solo el nombre
                segment = db.session.query(Segment.name).filter(Segment.id == candidate.segment_id).scalar()
                if segment:
                    segment_name = segment
            except Exception as e:
                 # Loggear el error pero no fallar la obtención del candidato
                 # Asumimos que el logger está disponible o usar logging
                 import logging
                 log = logging.getLogger(__name__)
                 log.error(f"Error al obtener nombre de segmento para ID {candidate.segment_id}: {e}", exc_info=True)

        return candidate, segment_name
    
    @staticmethod
    def create_candidate(candidate_data: Dict[str, Any]) -> Tuple[Union[Candidate, None], str, int]:
        """
        Crea un nuevo candidato.
        
        Args:
            candidate_data: Diccionario con datos del candidato
            
        Returns:
            Tupla con (candidato creado, mensaje, código de estado)
        """
        try:
            candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
            
            if 'skills' in candidate_data and isinstance(candidate_data['skills'], str):
                candidate_data['skills'] = [skill.strip() for skill in candidate_data['skills'].split(',') if skill.strip()]
                
            if 'languages' in candidate_data and isinstance(candidate_data['languages'], str):
                candidate_data['languages'] = [lang.strip() for lang in candidate_data['languages'].split(',') if lang.strip()]
            
            new_candidate = Candidate(candidate_id=candidate_id, **candidate_data)
            
            db.session.add(new_candidate)
            db.session.commit()
            
            CandidateService._notify_candidate_created(new_candidate)
            
            return new_candidate, f"Candidato '{new_candidate.name}' creado exitosamente.", 201
            
        except Exception as e:
            db.session.rollback()
            # Log con más contexto
            log_context = {"name": candidate_data.get("name"), "email": candidate_data.get("email")}
            current_app.logger.error(f"Error al crear candidato: {e} - Data: {log_context}", exc_info=True)
            return None, f"Error al crear candidato: {str(e)}", 500
    
    @staticmethod
    def update_candidate(candidate_id: str, candidate_data: Dict[str, Any]) -> Tuple[Union[Candidate, None], str, int]:
        """
        Actualiza un candidato existente.
        
        Args:
            candidate_id: ID único del candidato
            candidate_data: Diccionario con datos actualizados
            
        Returns:
            Tupla con (candidato actualizado, mensaje, código de estado)
        """
        candidate = CandidateService.get_candidate_by_id(candidate_id)
        
        if not candidate:
            return None, f"Candidato con ID {candidate_id} no encontrado.", 404
        
        try:
            if 'skills' in candidate_data and isinstance(candidate_data['skills'], str):
                candidate_data['skills'] = [skill.strip() for skill in candidate_data['skills'].split(',') if skill.strip()]
                
            if 'languages' in candidate_data and isinstance(candidate_data['languages'], str):
                candidate_data['languages'] = [lang.strip() for lang in candidate_data['languages'].split(',') if lang.strip()]
            
            for key, value in candidate_data.items():
                if hasattr(candidate, key):
                    setattr(candidate, key, value)
            
            db.session.commit()
            
            CandidateService._notify_candidate_updated(candidate)
            
            return candidate, f"Candidato '{candidate.name}' actualizado exitosamente.", 200
            
        except Exception as e:
            db.session.rollback()
            # Log con más contexto
            log_context = {"candidate_id": candidate_id, "name": candidate_data.get("name")}
            current_app.logger.error(f"Error al actualizar candidato {candidate_id}: {e} - Data: {log_context}", exc_info=True)
            return None, f"Error al actualizar candidato: {str(e)}", 500
    
    @staticmethod
    def delete_candidate(candidate_id: str) -> Tuple[bool, str, int]:
        """
        Elimina un candidato.
        
        Args:
            candidate_id: ID único del candidato
            
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        candidate = CandidateService.get_candidate_by_id(candidate_id)
        
        if not candidate:
            return False, f"Candidato con ID {candidate_id} no encontrado.", 404
        
        try:
            db.session.delete(candidate)
            db.session.commit()
            
            return True, f"Candidato eliminado exitosamente.", 204
            
        except Exception as e:
            db.session.rollback()
            # Log con más contexto
            candidate_name = candidate.name if candidate else '???'
            current_app.logger.error(f"Error al eliminar candidato {candidate_id} ('{candidate_name}'): {e}", exc_info=True)
            return False, f"Error al eliminar candidato: {str(e)}", 500
    
    @staticmethod
    def get_segment_names(candidates: List[Candidate]) -> Dict[int, str]:
        """
        Obtiene los nombres de segmentos para una lista de candidatos.
        
        Args:
            candidates: Lista de objetos Candidate
            
        Returns:
            Diccionario con {id_segmento: nombre_segmento}
        """
        if not candidates:
            return {}
            
        segment_ids = set(c.segment_id for c in candidates if c.segment_id is not None)
        
        if not segment_ids:
            return {}
            
        segments = Segment.query.filter(Segment.id.in_(segment_ids)).all()
        return {s.id: s.name for s in segments}
    
    @staticmethod
    def _notify_candidate_created(candidate: Candidate) -> None:
        """
        Genera una notificación cuando se crea un nuevo candidato.
        
        Args:
            candidate: Objeto Candidate recién creado
        """
        NotificationService.create_notification(
            title="Nuevo candidato registrado",
            message=f"Se ha registrado un nuevo candidato: {candidate.name}.",
            notification_type=NotificationType.INFO,
            category=NotificationCategory.CANDIDATE,
            entity_type="candidate",
            entity_id=str(candidate.candidate_id),
            send_realtime=True
        )
    
    @staticmethod
    def _notify_candidate_updated(candidate: Candidate) -> None:
        """
        Genera una notificación cuando se actualiza un candidato.
        
        Args:
            candidate: Objeto Candidate actualizado
        """
        NotificationService.create_notification(
            title="Candidato actualizado",
            message=f"Se ha actualizado la información del candidato: {candidate.name}.",
            notification_type=NotificationType.INFO,
            category=NotificationCategory.CANDIDATE,
            entity_type="candidate",
            entity_id=str(candidate.candidate_id),
            send_realtime=True
        )
