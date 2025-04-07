"""
Utilidades de transacción para AdFlux.

Este módulo proporciona clases y funciones para gestionar transacciones
de base de datos de manera más robusta.
"""

from typing import Optional, Callable, Any
from functools import wraps

from ..models import db
from ..api.common.error_handling import registrar_error


class TransactionManager:
    """
    Gestor de contexto para transacciones de base de datos.
    
    Ejemplo de uso:
    ```
    with TransactionManager() as tm:
        db.session.add(my_entity)
        tm.commit()  # Confirmar dentro del bloque
        
    with TransactionManager():
        db.session.add(my_entity)
    ```
    """
    
    def __init__(self, auto_commit: bool = True, on_error: Optional[Callable[[Exception], Any]] = None):
        """
        Inicializa el gestor de transacciones.
        
        Args:
            auto_commit: Si debe confirmar automáticamente al salir del bloque sin excepciones
            on_error: Función opcional a llamar cuando ocurre un error
        """
        self.auto_commit = auto_commit
        self.on_error = on_error
        self._committed = False
        self._rolled_back = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if not self._rolled_back:
                self.rollback()
            
            if self.on_error:
                self.on_error(exc_val)
            
            registrar_error(
                f"Error en transacción: {str(exc_val)}",
                excepcion=exc_val,
                exc_info=True
            )
            
            return False  # Re-levanta la excepción
        else:
            if self.auto_commit and not self._committed and not self._rolled_back:
                self.commit()
            return True
    
    def commit(self):
        """Confirma la transacción actual."""
        db.session.commit()
        self._committed = True
    
    def rollback(self):
        """Revierte la transacción actual."""
        db.session.rollback()
        self._rolled_back = True


def transactional(auto_commit: bool = True):
    """
    Decorador para funciones que deben ejecutarse dentro de una transacción.
    
    Args:
        auto_commit: Si debe confirmar automáticamente si la función termina sin excepciones
        
    Returns:
        Decorador para funciones
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with TransactionManager(auto_commit=auto_commit):
                return func(*args, **kwargs)
        return wrapper
    return decorator
