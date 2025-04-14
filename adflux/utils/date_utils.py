"""
Utilidades para manejo de fechas en AdFlux.

Este módulo proporciona funciones para trabajar con fechas y horas.
"""

import re
from typing import List, Optional, Tuple, Union, cast
from datetime import datetime, date, time, timedelta
import calendar
import pytz


def format_date(
    date_obj: Union[datetime, date],
    format_str: str = "%Y-%m-%d"
) -> str:
    """
    Formatea una fecha según el formato especificado.
    
    Args:
        date_obj: Objeto de fecha o datetime
        format_str: Formato de fecha (por defecto: YYYY-MM-DD)
        
    Returns:
        Cadena con la fecha formateada
    """
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    return date_obj.strftime(format_str)


def parse_date(
    date_str: str,
    formats: List[str] = None
) -> Optional[date]:
    """
    Parsea una cadena de fecha según los formatos especificados.
    
    Args:
        date_str: Cadena de fecha
        formats: Lista de formatos a probar (por defecto: ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"])
        
    Returns:
        Objeto de fecha o None si no se pudo parsear
    """
    if formats is None:
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def get_date_range(
    start_date: Union[datetime, date],
    end_date: Union[datetime, date]
) -> List[date]:
    """
    Obtiene una lista de fechas en el rango especificado.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        Lista de fechas en el rango
    """
    # Convertir a objetos date si son datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Crear lista de fechas
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    return date_list


def get_current_date() -> date:
    """
    Obtiene la fecha actual.
    
    Returns:
        Fecha actual
    """
    return datetime.now().date()


def get_current_datetime(timezone: str = "UTC") -> datetime:
    """
    Obtiene la fecha y hora actual en la zona horaria especificada.
    
    Args:
        timezone: Zona horaria (por defecto: UTC)
        
    Returns:
        Fecha y hora actual
    """
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def get_date_diff(
    date1: Union[datetime, date],
    date2: Union[datetime, date]
) -> int:
    """
    Obtiene la diferencia en días entre dos fechas.
    
    Args:
        date1: Primera fecha
        date2: Segunda fecha
        
    Returns:
        Diferencia en días (positivo si date1 > date2, negativo si date1 < date2)
    """
    # Convertir a objetos date si son datetime
    if isinstance(date1, datetime):
        date1 = date1.date()
    if isinstance(date2, datetime):
        date2 = date2.date()
    
    return (date1 - date2).days


def get_date_add(
    date_obj: Union[datetime, date],
    days: int = 0,
    months: int = 0,
    years: int = 0
) -> date:
    """
    Añade días, meses y/o años a una fecha.
    
    Args:
        date_obj: Fecha base
        days: Días a añadir
        months: Meses a añadir
        years: Años a añadir
        
    Returns:
        Nueva fecha
    """
    # Convertir a objeto date si es datetime
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    # Añadir días
    result = date_obj + timedelta(days=days)
    
    # Añadir meses y años
    if months != 0 or years != 0:
        # Calcular nuevo año y mes
        year = result.year + years + (result.month + months - 1) // 12
        month = (result.month + months - 1) % 12 + 1
        
        # Ajustar día si es necesario (por ejemplo, 31 de enero + 1 mes = 28/29 de febrero)
        day = min(result.day, calendar.monthrange(year, month)[1])
        
        # Crear nueva fecha
        result = date(year, month, day)
    
    return result


def get_date_subtract(
    date_obj: Union[datetime, date],
    days: int = 0,
    months: int = 0,
    years: int = 0
) -> date:
    """
    Resta días, meses y/o años a una fecha.
    
    Args:
        date_obj: Fecha base
        days: Días a restar
        months: Meses a restar
        years: Años a restar
        
    Returns:
        Nueva fecha
    """
    return get_date_add(date_obj, -days, -months, -years)


def get_first_day_of_month(date_obj: Union[datetime, date]) -> date:
    """
    Obtiene el primer día del mes de la fecha especificada.
    
    Args:
        date_obj: Fecha
        
    Returns:
        Primer día del mes
    """
    # Convertir a objeto date si es datetime
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    return date(date_obj.year, date_obj.month, 1)


def get_last_day_of_month(date_obj: Union[datetime, date]) -> date:
    """
    Obtiene el último día del mes de la fecha especificada.
    
    Args:
        date_obj: Fecha
        
    Returns:
        Último día del mes
    """
    # Convertir a objeto date si es datetime
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    # Obtener último día del mes
    last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
    
    return date(date_obj.year, date_obj.month, last_day)


def get_first_day_of_week(
    date_obj: Union[datetime, date],
    start_of_week: int = 0  # 0 = lunes, 6 = domingo
) -> date:
    """
    Obtiene el primer día de la semana de la fecha especificada.
    
    Args:
        date_obj: Fecha
        start_of_week: Día de inicio de la semana (0 = lunes, 6 = domingo)
        
    Returns:
        Primer día de la semana
    """
    # Convertir a objeto date si es datetime
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    # Calcular días a restar
    weekday = date_obj.weekday()
    days_to_subtract = (weekday - start_of_week) % 7
    
    return date_obj - timedelta(days=days_to_subtract)


def get_last_day_of_week(
    date_obj: Union[datetime, date],
    start_of_week: int = 0  # 0 = lunes, 6 = domingo
) -> date:
    """
    Obtiene el último día de la semana de la fecha especificada.
    
    Args:
        date_obj: Fecha
        start_of_week: Día de inicio de la semana (0 = lunes, 6 = domingo)
        
    Returns:
        Último día de la semana
    """
    # Obtener primer día de la semana
    first_day = get_first_day_of_week(date_obj, start_of_week)
    
    # Último día es 6 días después del primer día
    return first_day + timedelta(days=6)
