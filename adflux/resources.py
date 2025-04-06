from flask_restx import abort
import datetime
from sqlalchemy import func, select, alias, text, column  # Importar column


# Función auxiliar para manejar posibles errores de conversión de cadena de fecha
def parse_date(date_str):
    try:
        return datetime.date.fromisoformat(date_str)
    except (ValueError, TypeError):
        abort(400, message="Formato de fecha inválido. Use YYYY-MM-DD.")
