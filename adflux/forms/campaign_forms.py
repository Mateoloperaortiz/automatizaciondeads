"""
Formularios de campaña para AdFlux.

Este módulo contiene formularios relacionados con la gestión de campañas publicitarias.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SubmitField,
    SelectMultipleField,
    widgets,
    FloatField,
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField

from .utils import get_job_openings, get_segment_choices


class CampaignForm(FlaskForm):
    """
    Formulario para crear y editar Campañas AdFlux.

    Este formulario permite a los usuarios crear y editar campañas publicitarias,
    especificando detalles como nombre, descripción, plataforma, presupuesto,
    trabajo asociado, segmentos objetivo, y contenido creativo.
    """

    name = StringField(
        "Nombre de la Campaña",
        validators=[DataRequired(), Length(min=3, max=255)],
        render_kw={"placeholder": "ej., Campaña de Prácticas SWE Verano 2025"},
    )
    description = TextAreaField(
        "Descripción",
        validators=[Optional(), Length(max=1000)],
        render_kw={
            "rows": 3,
            "placeholder": "Opcional: Describe el objetivo de la campaña o la audiencia objetivo...",
        },
    )
    platform = SelectField(
        "Plataforma",
        choices=[
            ("meta", "Meta (Facebook/Instagram)"),
            # Añadir otras plataformas a medida que sean soportadas
            # ('linkedin', 'LinkedIn'),
            ("google", "Google Ads"),
        ],
        validators=[DataRequired()],
    )
    daily_budget = FloatField(
        "Presupuesto Diario ($)",
        validators=[Optional(), NumberRange(min=1.00)],  # Presupuesto mínimo de $1.00
        render_kw={"placeholder": "ej., 5.00", "step": "0.01"},
    )
    # Usar QuerySelectField para crear un desplegable a partir de los resultados de la consulta de JobOpening
    job_opening = QuerySelectField(
        "Vincular a Oferta de Trabajo (Opcional)",
        query_factory=get_job_openings,
        get_label="title",  # Mostrar el título del trabajo en el desplegable
        get_pk=lambda obj: obj.job_id,  # Usar job_id como valor
        allow_blank=True,
        blank_text="-- Selecciona un Trabajo --",
        validators=[Optional()],
    )
    # Añadir campo para seleccionar segmentos objetivo
    target_segment_ids = SelectMultipleField(
        "Segmentos Objetivo",
        choices=get_segment_choices,  # Usar la función auxiliar para poblar las opciones dinámicamente
        option_widget=widgets.CheckboxInput(),  # Mostrar como casillas de verificación
        widget=widgets.ListWidget(
            prefix_label=False
        ),  # Renderizar casillas de verificación en una lista
        coerce=int,  # Convertir los valores enviados de nuevo a enteros
        validators=[Optional()],
    )
    # Campos de Creativo Publicitario
    primary_text = TextAreaField(
        "Texto Principal",
        validators=[Optional(), Length(max=200)],
        render_kw={"rows": 3, "placeholder": "Texto principal del anuncio (150-200 caracteres)"},
    )
    headline = StringField(
        "Titular",
        validators=[Optional(), Length(max=40)],
        render_kw={"placeholder": "Titular llamativo (25-40 caracteres)"},
    )
    link_description = StringField(
        "Descripción del Enlace",
        validators=[Optional(), Length(max=50)],
        render_kw={
            "placeholder": "Descripción breve para la vista previa del enlace (30-50 caracteres)"
        },
    )
    creative_image = FileField(
        "Imagen del Creativo",
        validators=[Optional(), FileAllowed(["jpg", "png", "jpeg"], "¡Solo imágenes!")],
    )
    status = SelectField(
        "Estado",
        choices=[
            ("draft", "Borrador"),
            ("active", "Activa"),
            ("paused", "Pausada"),
            ("archived", "Archivada"),
        ],
        default="draft",
        validators=[DataRequired()],
    )
    submit = SubmitField("Guardar Campaña")
