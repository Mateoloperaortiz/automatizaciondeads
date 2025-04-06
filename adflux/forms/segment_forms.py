"""
Formularios de segmento para AdFlux.

Este módulo contiene formularios relacionados con la gestión de segmentos de candidatos.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class SegmentForm(FlaskForm):
    """
    Formulario para editar Segmentos de candidatos.

    Este formulario permite a los usuarios editar segmentos de candidatos,
    especificando detalles como nombre y descripción.
    """

    name = StringField(
        "Nombre del Segmento",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={
            "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        },
    )
    description = TextAreaField(
        "Descripción",
        validators=[Optional(), Length(max=500)],
        render_kw={
            "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
            "rows": 3,
        },
    )
    submit = SubmitField(
        "Guardar Segmento",
        render_kw={
            "class": "inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        },
    )
