from flask import request, current_app
from flask_restx import Resource, reqparse, fields, marshal_with, marshal, abort, Api, Namespace
from .models import db, JobOpening, Candidate, Application
from datetime import date
import datetime
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy import func, select, alias, text, column # Importar column

# Función auxiliar para manejar posibles errores de conversión de cadena de fecha
def parse_date(date_str):
    try:
        return datetime.date.fromisoformat(date_str)
    except (ValueError, TypeError):
        abort(400, message="Formato de fecha inválido. Use YYYY-MM-DD.")
