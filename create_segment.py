"""
Script para crear un segmento de prueba en la base de datos.

Este script verifica si hay segmentos en la base de datos y, si no hay, crea uno.
"""

from adflux.core.factory import create_app
from adflux.models import db, Segment
from adflux.constants import SEGMENT_MAP

def create_test_segment():
    """Crea un segmento de prueba en la base de datos."""
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existen segmentos
        existing_segments = Segment.query.all()
        print(f"Segmentos existentes: {existing_segments}")
        
        if not existing_segments:
            # Crear un segmento para cada entrada en SEGMENT_MAP
            for segment_id, segment_name in SEGMENT_MAP.items():
                segment = Segment(id=segment_id, name=segment_name, description=f"Segmento {segment_name} creado automáticamente")
                db.session.add(segment)
            
            # Guardar cambios
            db.session.commit()
            print("Segmentos creados exitosamente.")
            
            # Verificar que se hayan creado
            new_segments = Segment.query.all()
            print(f"Nuevos segmentos: {new_segments}")
        else:
            print("Ya existen segmentos en la base de datos.")

if __name__ == "__main__":
    create_test_segment()
