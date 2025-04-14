"""
Clase base para servicios de métricas del dashboard.

Esta clase proporciona funcionalidad común para todos los servicios
de métricas del dashboard.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ...models import db


class BaseMetricsService(ABC):
    """
    Clase base abstracta para servicios de métricas.
    
    Proporciona métodos comunes y define la interfaz que deben
    implementar todos los servicios de métricas.
    """
    
    def __init__(self):
        """Inicializa el servicio de métricas."""
        self.errors = []
    
    @abstractmethod
    def get_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene métricas para el rango de fechas especificado.
        
        Args:
            start_date: Fecha de inicio para filtrar datos
            end_date: Fecha de fin para filtrar datos
            
        Returns:
            Diccionario con métricas calculadas
        """
        pass
    
    def log_error(self, error_msg: str, exception: Optional[Exception] = None) -> None:
        """
        Registra un error en el log y lo añade a la lista de errores.
        
        Args:
            error_msg: Mensaje de error
            exception: Excepción que causó el error (opcional)
        """
        if exception:
            current_app.logger.error(f"{error_msg}: {str(exception)}", exc_info=True)
        else:
            current_app.logger.error(error_msg)
        
        self.errors.append(error_msg)
    
    def get_errors(self) -> List[str]:
        """
        Obtiene la lista de errores registrados.
        
        Returns:
            Lista de mensajes de error
        """
        return self.errors
    
    def clear_errors(self) -> None:
        """Limpia la lista de errores."""
        self.errors = []
    
    def execute_query_safely(self, query_func, error_msg: str, default_value: Any = None) -> Any:
        """
        Ejecuta una función de consulta de manera segura, capturando excepciones.
        
        Args:
            query_func: Función que ejecuta la consulta
            error_msg: Mensaje de error en caso de excepción
            default_value: Valor por defecto a devolver en caso de error
            
        Returns:
            Resultado de la consulta o valor por defecto en caso de error
        """
        try:
            return query_func()
        except SQLAlchemyError as e:
            self.log_error(error_msg, e)
            return default_value
        except Exception as e:
            self.log_error(f"Error inesperado: {error_msg}", e)
            return default_value
    
    def prepare_chart_data(self, labels: List[str], data: List[Any]) -> Dict[str, List]:
        """
        Prepara datos para un gráfico.
        
        Args:
            labels: Etiquetas para el eje X
            data: Valores para el eje Y
            
        Returns:
            Diccionario con datos para el gráfico
        """
        return {
            "labels": labels,
            "data": data
        }
