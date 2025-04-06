"""
Utilidades para el logging en las APIs.

Este módulo proporciona funciones para el logging consistente
en todas las llamadas a APIs externas.
"""

from typing import Optional, Any

# Intentar importar Flask, pero no fallar si no está disponible
try:
    from flask import current_app
except ImportError:
    current_app = None


def log_info(mensaje: str, modulo: str = "API") -> None:
    """
    Registra un mensaje de información.

    Args:
        mensaje: El mensaje a registrar.
        modulo: El nombre del módulo que genera el mensaje.
    """
    mensaje_completo = f"[{modulo}] {mensaje}"
    if current_app:
        current_app.logger.info(mensaje_completo)
    else:
        print(f"INFO: {mensaje_completo}")


def log_warning(mensaje: str, modulo: str = "API") -> None:
    """
    Registra un mensaje de advertencia.

    Args:
        mensaje: El mensaje a registrar.
        modulo: El nombre del módulo que genera el mensaje.
    """
    mensaje_completo = f"[{modulo}] {mensaje}"
    if current_app:
        current_app.logger.warning(mensaje_completo)
    else:
        print(f"WARNING: {mensaje_completo}")


def log_error(mensaje: str, excepcion: Optional[Exception] = None, modulo: str = "API") -> None:
    """
    Registra un mensaje de error.

    Args:
        mensaje: El mensaje a registrar.
        excepcion: La excepción asociada al error, si existe.
        modulo: El nombre del módulo que genera el mensaje.
    """
    mensaje_completo = f"[{modulo}] {mensaje}"
    if current_app:
        if excepcion:
            current_app.logger.error(mensaje_completo, exc_info=excepcion)
        else:
            current_app.logger.error(mensaje_completo)
    else:
        print(f"ERROR: {mensaje_completo}")
        if excepcion:
            print(f"Excepción: {excepcion}")


class ApiLogger:
    """
    Clase para manejar el logging específico de un módulo de API.
    """

    def __init__(self, modulo: str):
        """
        Inicializa el logger con un nombre de módulo específico.

        Args:
            modulo: El nombre del módulo para el que se registrarán los mensajes.
        """
        self.modulo = modulo

    def info(self, mensaje: str) -> None:
        """
        Registra un mensaje de información.

        Args:
            mensaje: El mensaje a registrar.
        """
        log_info(mensaje, self.modulo)

    def warning(self, mensaje: str) -> None:
        """
        Registra un mensaje de advertencia.

        Args:
            mensaje: El mensaje a registrar.
        """
        log_warning(mensaje, self.modulo)

    def error(self, mensaje: str, excepcion: Optional[Exception] = None) -> None:
        """
        Registra un mensaje de error.

        Args:
            mensaje: El mensaje a registrar.
            excepcion: La excepción asociada al error, si existe.
        """
        log_error(mensaje, excepcion, self.modulo)


def get_logger(modulo: str) -> ApiLogger:
    """
    Obtiene un logger para un módulo específico.

    Args:
        modulo: El nombre del módulo para el que se registrarán los mensajes.

    Returns:
        Un ApiLogger configurado para el módulo especificado.
    """
    return ApiLogger(modulo)
