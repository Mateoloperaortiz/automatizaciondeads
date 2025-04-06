"""
Script mejorado para crear segmentos en la base de datos.

Este script verifica qué segment_id ya están en uso en la tabla candidates
y crea registros correspondientes en la tabla segments.
"""

from adflux.core.factory import create_app
from adflux.models import db, Segment, Candidate
from adflux.constants import SEGMENT_MAP
from sqlalchemy import distinct

def create_segments_from_candidates():
    """Crea segmentos en la tabla segments basados en los segment_id existentes en la tabla candidates."""
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existen segmentos
        existing_segments = Segment.query.all()
        print(f"Segmentos existentes en tabla segments: {existing_segments}")
        
        # Obtener segment_id distintos de la tabla candidates
        segment_ids_in_use = db.session.query(distinct(Candidate.segment_id))\
                              .filter(Candidate.segment_id.isnot(None))\
                              .order_by(Candidate.segment_id).all()
        
        segment_ids_in_use = [s[0] for s in segment_ids_in_use]
        print(f"Segment_id en uso en tabla candidates: {segment_ids_in_use}")
        
        # Crear segmentos solo para los segment_id que ya están en uso
        segments_created = []
        for segment_id in segment_ids_in_use:
            # Verificar si ya existe un segmento con este ID
            existing_segment = Segment.query.filter_by(id=segment_id).first()
            if not existing_segment:
                # Obtener el nombre del segmento del mapa de segmentos
                segment_name = SEGMENT_MAP.get(segment_id, f"Segmento {segment_id}")
                
                # Crear el segmento
                segment = Segment(id=segment_id, name=segment_name, description=f"Segmento {segment_name} creado automáticamente")
                db.session.add(segment)
                segments_created.append(segment)
        
        # Guardar cambios solo si se crearon segmentos
        if segments_created:
            db.session.commit()
            print(f"Segmentos creados: {segments_created}")
        else:
            print("No se crearon nuevos segmentos.")
        
        # Verificar segmentos actuales
        current_segments = Segment.query.all()
        print(f"Segmentos actuales: {current_segments}")

if __name__ == "__main__":
    create_segments_from_candidates()
