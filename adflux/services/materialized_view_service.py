"""
Servicio para gestionar vistas materializadas.

Este servicio proporciona métodos para actualizar las vistas materializadas
utilizadas para mejorar el rendimiento de consultas frecuentes.
"""

import logging
from typing import List, Tuple, Dict, Any
from sqlalchemy import text

from ..models import db
from ..exceptions import DatabaseError


# Configurar logger
logger = logging.getLogger(__name__)


class MaterializedViewService:
    """
    Servicio para gestionar vistas materializadas.
    
    Proporciona métodos para actualizar las vistas materializadas
    utilizadas para mejorar el rendimiento de consultas frecuentes.
    """
    
    @classmethod
    def refresh_all_views(cls) -> Tuple[bool, str]:
        """
        Actualiza todas las vistas materializadas.
        
        Returns:
            Tupla con (éxito, mensaje)
        """
        try:
            # Ejecutar función que actualiza todas las vistas
            db.session.execute(text("SELECT refresh_materialized_views()"))
            db.session.commit()
            
            logger.info("Todas las vistas materializadas actualizadas correctamente")
            return True, "Vistas materializadas actualizadas correctamente"
        
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error al actualizar vistas materializadas: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, cause=e)
    
    @classmethod
    def refresh_view(cls, view_name: str) -> Tuple[bool, str]:
        """
        Actualiza una vista materializada específica.
        
        Args:
            view_name: Nombre de la vista materializada
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        try:
            # Validar nombre de vista para evitar inyección SQL
            valid_views = [
                "campaign_daily_metrics",
                "campaign_monthly_metrics",
                "platform_metrics"
            ]
            
            if view_name not in valid_views:
                error_msg = f"Vista materializada no válida: {view_name}"
                logger.error(error_msg)
                return False, error_msg
            
            # Actualizar vista materializada
            db.session.execute(text(f"REFRESH MATERIALIZED VIEW {view_name}"))
            db.session.commit()
            
            logger.info(f"Vista materializada {view_name} actualizada correctamente")
            return True, f"Vista materializada {view_name} actualizada correctamente"
        
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error al actualizar vista materializada {view_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, cause=e)
    
    @classmethod
    def get_view_status(cls) -> Dict[str, Any]:
        """
        Obtiene el estado de las vistas materializadas.
        
        Returns:
            Diccionario con información sobre las vistas materializadas
        """
        try:
            # Consultar información sobre las vistas materializadas
            result = db.session.execute(text("""
                SELECT
                    matviewname,
                    pg_size_pretty(pg_relation_size(schemaname || '.' || matviewname)) as size,
                    pg_size_pretty(pg_total_relation_size(schemaname || '.' || matviewname)) as total_size,
                    (SELECT COUNT(*) FROM pg_stat_activity WHERE query LIKE '%REFRESH%' || matviewname || '%') as is_refreshing
                FROM pg_matviews
                WHERE schemaname = 'public'
                ORDER BY matviewname;
            """))
            
            views_info = []
            for row in result:
                views_info.append({
                    "name": row[0],
                    "size": row[1],
                    "total_size": row[2],
                    "is_refreshing": row[3] > 0
                })
            
            return {
                "views": views_info,
                "count": len(views_info)
            }
        
        except Exception as e:
            error_msg = f"Error al obtener estado de vistas materializadas: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, cause=e)
