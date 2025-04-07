"""
Servicio base para operaciones CRUD en AdFlux.

Este módulo proporciona una clase base para estandarizar operaciones CRUD
y reducir duplicación de código en los servicios específicos.
"""

from typing import Dict, List, Optional, Tuple, Any, Union, TypeVar, Generic, Type
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc

from ..models import db
from ..api.common.excepciones import ErrorRecursoNoEncontrado, ErrorValidacion, ErrorBaseDatos
from ..api.common.error_handling import registrar_error

T = TypeVar('T')


class BaseService(Generic[T]):
    """
    Clase base para servicios que proporciona operaciones CRUD estándar.
    
    Esta clase debe ser extendida por servicios específicos para
    aprovechar la funcionalidad común y reducir duplicación de código.
    """
    
    model_class: Type[T] = None
    
    id_attribute: str = None
    
    entity_name: str = "elemento"
    
    @classmethod
    def get_by_id(cls, entity_id: Any) -> Optional[T]:
        """
        Obtiene una entidad por su ID.
        
        Args:
            entity_id: ID único de la entidad
                
        Returns:
            Objeto de la entidad o None si no se encuentra
        """
        if not cls.model_class or not cls.id_attribute:
            raise NotImplementedError("Las clases hijas deben definir model_class e id_attribute")
            
        filter_kwargs = {cls.id_attribute: entity_id}
        return cls.model_class.query.filter_by(**filter_kwargs).first()
    
    @classmethod
    def get_list(
        cls,
        page: int = 1, 
        per_page: int = 10,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        **filters
    ) -> Tuple[List[T], Any]:
        """
        Obtiene una lista paginada de entidades con opciones de filtrado y ordenación.
        
        Args:
            page: Número de página para paginación
            per_page: Número de elementos por página
            sort_by: Campo por el cual ordenar los resultados
            sort_order: Orden de clasificación ('asc' o 'desc')
            **filters: Filtros adicionales a aplicar
                
        Returns:
            Tupla con la lista de entidades y el objeto de paginación
        """
        if not cls.model_class:
            raise NotImplementedError("Las clases hijas deben definir model_class")
            
        query = cls.model_class.query
        
        for key, value in filters.items():
            if value is not None and hasattr(cls.model_class, key):
                query = query.filter(getattr(cls.model_class, key) == value)
        
        if sort_by and hasattr(cls.model_class, sort_by):
            sort_column = getattr(cls.model_class, sort_by)
            if sort_order.lower() == "desc":
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        items = pagination.items
        
        return items, pagination
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> Tuple[Union[T, None], str, int]:
        """
        Crea una nueva entidad.
        
        Args:
            data: Diccionario con datos de la entidad
                
        Returns:
            Tupla con (entidad creada, mensaje, código de estado)
        """
        if not cls.model_class:
            raise NotImplementedError("Las clases hijas deben definir model_class")
            
        try:
            processed_data = cls._preprocess_data(data)
            
            new_entity = cls.model_class(**processed_data)
            
            db.session.add(new_entity)
            db.session.commit()
            
            if hasattr(cls, '_notify_entity_created'):
                cls._notify_entity_created(new_entity)
            
            return new_entity, f"{cls.entity_name.capitalize()} creado exitosamente.", 201
            
        except ErrorValidacion as e:
            db.session.rollback()
            registrar_error(
                f"Error de validación al crear {cls.entity_name}: {str(e)}",
                excepcion=e
            )
            return None, str(e), e.codigo
        except SQLAlchemyError as e:
            db.session.rollback()
            error_db = ErrorBaseDatos(
                mensaje=f"Error de base de datos al crear {cls.entity_name}: {str(e)}"
            )
            registrar_error(
                f"Error de base de datos al crear {cls.entity_name}",
                excepcion=e,
                exc_info=True
            )
            return None, str(error_db), error_db.codigo
        except Exception as e:
            db.session.rollback()
            registrar_error(
                f"Error inesperado al crear {cls.entity_name}",
                excepcion=e,
                exc_info=True
            )
            return None, f"Error al crear {cls.entity_name}: {str(e)}", 500
    
    @classmethod
    def update(cls, entity_id: Any, data: Dict[str, Any]) -> Tuple[Union[T, None], str, int]:
        """
        Actualiza una entidad existente.
        
        Args:
            entity_id: ID único de la entidad
            data: Diccionario con datos actualizados
                
        Returns:
            Tupla con (entidad actualizada, mensaje, código de estado)
        """
        if not cls.model_class or not cls.id_attribute:
            raise NotImplementedError("Las clases hijas deben definir model_class e id_attribute")
            
        entity = cls.get_by_id(entity_id)
        
        if not entity:
            error = ErrorRecursoNoEncontrado(
                mensaje=f"{cls.entity_name.capitalize()} con ID {entity_id} no encontrado."
            )
            return None, str(error), error.codigo
        
        try:
            processed_data = cls._preprocess_data(data)
            
            for key, value in processed_data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            db.session.commit()
            
            if hasattr(cls, '_notify_entity_updated'):
                cls._notify_entity_updated(entity)
            
            return entity, f"{cls.entity_name.capitalize()} actualizado exitosamente.", 200
            
        except ErrorValidacion as e:
            db.session.rollback()
            registrar_error(
                f"Error de validación al actualizar {cls.entity_name}: {str(e)}",
                excepcion=e
            )
            return None, str(e), e.codigo
        except SQLAlchemyError as e:
            db.session.rollback()
            error_db = ErrorBaseDatos(
                mensaje=f"Error de base de datos al actualizar {cls.entity_name}: {str(e)}"
            )
            registrar_error(
                f"Error de base de datos al actualizar {cls.entity_name}",
                excepcion=e,
                exc_info=True
            )
            return None, str(error_db), error_db.codigo
        except Exception as e:
            db.session.rollback()
            registrar_error(
                f"Error inesperado al actualizar {cls.entity_name}",
                excepcion=e,
                exc_info=True
            )
            return None, f"Error al actualizar {cls.entity_name}: {str(e)}", 500
    
    @classmethod
    def delete(cls, entity_id: Any) -> Tuple[bool, str, int]:
        """
        Elimina una entidad.
        
        Args:
            entity_id: ID único de la entidad
                
        Returns:
            Tupla con (éxito, mensaje, código de estado)
        """
        if not cls.model_class or not cls.id_attribute:
            raise NotImplementedError("Las clases hijas deben definir model_class e id_attribute")
            
        entity = cls.get_by_id(entity_id)
        
        if not entity:
            error = ErrorRecursoNoEncontrado(
                mensaje=f"{cls.entity_name.capitalize()} con ID {entity_id} no encontrado."
            )
            return False, str(error), error.codigo
        
        try:
            db.session.delete(entity)
            db.session.commit()
            
            return True, f"{cls.entity_name.capitalize()} eliminado exitosamente.", 204
            
        except SQLAlchemyError as e:
            db.session.rollback()
            error_db = ErrorBaseDatos(
                mensaje=f"Error de base de datos al eliminar {cls.entity_name}: {str(e)}"
            )
            registrar_error(
                f"Error de base de datos al eliminar {cls.entity_name}",
                excepcion=e,
                exc_info=True
            )
            return False, str(error_db), error_db.codigo
        except Exception as e:
            db.session.rollback()
            registrar_error(
                f"Error inesperado al eliminar {cls.entity_name}",
                excepcion=e,
                exc_info=True
            )
            return False, f"Error al eliminar {cls.entity_name}: {str(e)}", 500
    
    @classmethod
    def _preprocess_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocesa datos antes de crear o actualizar una entidad.
        
        Las clases hijas deben sobrescribir este método para implementar
        validaciones específicas o transformación de datos.
        
        Args:
            data: Diccionario con datos a procesar
                
        Returns:
            Diccionario con datos procesados
        """
        return data.copy()
