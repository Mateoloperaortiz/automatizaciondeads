"""
Utilidades para formularios de AdFlux.

Este módulo contiene funciones auxiliares utilizadas por los formularios de AdFlux.
"""

from sqlalchemy import distinct
from ..models import db, JobOpening, Candidate, Segment
from ..constants import SEGMENT_MAP, DEFAULT_SEGMENT_NAME


def get_job_openings():
    """
    Función auxiliar para consultar ofertas de trabajo para el desplegable.

    Returns:
        Lista de objetos JobOpening ordenados por ID.
    """
    # Consultar trabajos abiertos, ordenados por ID. Quizás quieras ajustar el filtrado/orden.
    return JobOpening.query.filter_by(status='open').order_by(JobOpening.job_id).all()


def get_segment_choices():
    """
    Función auxiliar para consultar segmentos para las opciones.

    Returns:
        Lista de tuplas (id, etiqueta) para usar en SelectMultipleField.
    """
    try:
        # Consultar todos los segmentos de la tabla Segment
        segments = Segment.query.order_by(Segment.name).all()

        # Consultar IDs de segmentos distintos y no nulos de la tabla Candidate
        segment_ids_in_use = db.session.query(distinct(Candidate.segment_id))\
                          .filter(Candidate.segment_id.isnot(None))\
                          .order_by(Candidate.segment_id).all()
        segment_ids_in_use = [s[0] for s in segment_ids_in_use]

        # Si hay segmentos en la tabla Segment, usarlos
        if segments:
            # Priorizar los segmentos que tienen candidatos asignados
            choices = []
            for s in segments:
                # Si este segmento tiene candidatos asignados, marcarlo como "en uso"
                if s.id in segment_ids_in_use:
                    choices.append((s.id, f"{s.name} (en uso)"))
                else:
                    choices.append((s.id, s.name))
        else:
            # Si no hay segmentos en la tabla Segment, usar los segment_id de Candidate
            choices = [(s, SEGMENT_MAP.get(s, f"Segmento {s}")) for s in segment_ids_in_use]

        return choices
    except Exception as e:
        # Registrar error o manejar apropiadamente
        print(f"Error al obtener las opciones de segmento: {e}")
        return [] # Devolver lista vacía en caso de error
