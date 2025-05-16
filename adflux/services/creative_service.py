"""
Servicio para la generación de creatividades para anuncios.

Este servicio proporciona funcionalidades para generar contenido creativo
para anuncios en diferentes plataformas utilizando la API de Google Gemini.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from ..api.gemini import get_client
from ..api.gemini.content_generator import get_content_generator
from ..models.job import JobOpening
from ..models.candidate import Candidate
from ..models.segment import Segment
from ..models.campaign import Campaign
from ..models import db

logger = logging.getLogger(__name__)


class CreativeService:
    """
    Servicio para la generación de creatividades para anuncios.
    """

    def __init__(self):
        """
        Inicializa el servicio de creatividades.
        """

    def generate_ad_creative(
        self,
        job_id: str,
        platform: str,
        segment_id: Optional[int] = None,
        format_type: Optional[str] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera contenido creativo para un anuncio basado en una oferta de trabajo y segmento.

        Args:
            job_id: ID de la oferta de trabajo
            platform: Plataforma para la que se genera el contenido (meta, google, tiktok, snapchat)
            segment_id: ID del segmento objetivo (opcional)
            format_type: Tipo de formato (imagen_única, carrusel, video, etc.)

        Returns:
            Tupla con (éxito, mensaje, contenido generado)
        """
        try:
            from ..services.job_service import JobService
            job_service = JobService()
            
            job = job_service.get_job_by_id(job_id)
            if not job:
                return False, f"No se encontró la oferta de trabajo con ID {job_id}", {}

            job_data = self._job_to_dict(job)

            segment_data = None
            if segment_id:
                from ..models.segment import Segment
                segment = Segment.query.get(segment_id)
                if segment:
                    segment_data = self._segment_to_dict(segment)

            from ..api.gemini.content_generator import get_content_generator
            content_generator = get_content_generator()
            
            # Generar contenido creativo
            success, message, content = content_generator.generate_ad_content(
                job_data=job_data,
                platform=platform,
                segment_data=segment_data,
                format_type=format_type
            )
            
            if not success:
                logger.error(f"Error al generar creatividad: {message}")
                return False, message, {}

            return True, "Creatividad generada exitosamente", content

        except Exception as e:
            logger.exception(f"Error al generar creatividad: {e}")
            return False, f"Error al generar creatividad: {str(e)}", {}

    def generate_ad_variations(
        self,
        base_content: Dict[str, Any],
        platform: str,
        num_variations: int = 3,
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Genera variaciones de un anuncio base.

        Args:
            base_content: Contenido base del anuncio
            platform: Plataforma para la que se generan las variaciones
            num_variations: Número de variaciones a generar

        Returns:
            Tupla con (éxito, mensaje, lista de variaciones)
        """
        try:
            content_generator = get_content_generator()

            success, message, variations = content_generator.generate_ad_variations(
                base_content=base_content,
                platform=platform,
                num_variations=num_variations,
            )

            if not success:
                logger.error(f"Error al generar variaciones: {message}")
                return False, message, []

            return True, "Variaciones generadas exitosamente", variations

        except Exception as e:
            logger.exception(f"Error al generar variaciones: {e}")
            return False, f"Error al generar variaciones: {str(e)}", []

    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de plataformas soportadas para la generación de creatividades.

        Returns:
            Lista de plataformas con sus configuraciones
        """
        platforms = [
            {
                "id": "meta",
                "name": "Meta (Facebook/Instagram)",
                "icon": "fab fa-facebook",
                "formats": ["imagen_única", "carrusel", "video"],
                "description": "Anuncios para Facebook e Instagram",
            },
            {
                "id": "google",
                "name": "Google Ads",
                "icon": "fab fa-google",
                "formats": ["texto", "responsive", "imagen"],
                "description": "Anuncios para la red de búsqueda y display de Google",
            },
            {
                "id": "tiktok",
                "name": "TikTok",
                "icon": "fab fa-tiktok",
                "formats": ["video", "imagen"],
                "description": "Anuncios para la plataforma TikTok",
            },
            {
                "id": "snapchat",
                "name": "Snapchat",
                "icon": "fab fa-snapchat",
                "formats": ["video", "imagen", "colección"],
                "description": "Anuncios para la plataforma Snapchat",
            },
        ]
        return platforms

    def _job_to_dict(self, job: JobOpening) -> Dict[str, Any]:
        """
        Convierte una oferta de trabajo a un diccionario para el generador de contenido.

        Args:
            job: Oferta de trabajo

        Returns:
            Diccionario con datos de la oferta de trabajo
        """
        salary_range = ""
        if hasattr(job, 'salary_min') and hasattr(job, 'salary_max') and job.salary_min and job.salary_max:
            salary_range = f"{job.salary_min}-{job.salary_max}"
        elif hasattr(job, 'salary_range'):
            salary_range = job.salary_range
            
        requirements = ""
        if hasattr(job, 'required_skills') and job.required_skills:
            if isinstance(job.required_skills, list):
                requirements = "Habilidades requeridas: " + ", ".join(job.required_skills)
            else:
                requirements = "Habilidades requeridas: " + str(job.required_skills)
        
        return {
            "id": job.job_id,  # Usar job_id en lugar de id
            "title": job.title,
            "description": job.description,
            "requirements": requirements,  # Usar habilidades requeridas o string vacío
            "location": job.location,
            "salary": salary_range,
            "company": job.company_name,
            "created_at": job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
            "status": job.status,
        }

    def _segment_to_dict(self, segment: Segment) -> Dict[str, Any]:
        """
        Convierte un segmento a un diccionario para el generador de contenido.

        Args:
            segment: Segmento

        Returns:
            Diccionario con datos del segmento
        """
        candidates = Candidate.query.filter_by(segment_id=segment.id).all()
        
        avg_experience = sum(c.years_experience for c in candidates if c.years_experience) / len(candidates) if candidates else 0
        
        education_levels = {}
        for c in candidates:
            if c.education_level:
                education_levels[c.education_level] = education_levels.get(c.education_level, 0) + 1
        
        predominant_education = max(education_levels.items(), key=lambda x: x[1])[0] if education_levels else "No disponible"
        
        skills = []
        for c in candidates:
            if c.skills:
                skills.extend(c.skills.split(','))
        
        skill_count = {}
        for skill in skills:
            skill = skill.strip()
            if skill:
                skill_count[skill] = skill_count.get(skill, 0) + 1
        
        top_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:5]
        top_skills = [skill for skill, _ in top_skills]
        
        min_salary = min((c.desired_salary for c in candidates if c.desired_salary), default=0)
        max_salary = max((c.desired_salary for c in candidates if c.desired_salary), default=0)
        
        return {
            "segment_id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "count": len(candidates),
            "avg_experience": round(avg_experience, 1),
            "education_level": predominant_education,
            "skills": top_skills,
            "salary_range": f"{min_salary}-{max_salary}" if min_salary and max_salary else "No disponible",
        }
