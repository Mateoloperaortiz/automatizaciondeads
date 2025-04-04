# adflux/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, SelectMultipleField, widgets, FloatField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from sqlalchemy import distinct

# Importar modelos necesarios para consultas
from .models import db, JobOpening, Candidate, Segment

def get_job_openings():
    """Función auxiliar para consultar ofertas de trabajo para el desplegable."""
    # Consultar trabajos abiertos, ordenados por ID. Quizás quieras ajustar el filtrado/orden.
    return JobOpening.query.filter_by(status='open').order_by(JobOpening.job_id).all()

def get_segment_choices():
    """Función auxiliar para consultar IDs de segmentos distintos para las opciones."""
    try:
        # Consultar IDs de segmentos distintos y no nulos de la tabla Candidate
        segments = db.session.query(distinct(Candidate.segment))\
                          .filter(Candidate.segment.isnot(None))\
                          .order_by(Candidate.segment).all()
        # Formato para las opciones de SelectMultipleField: (valor, etiqueta)
        # Asegurarse de que el valor sea string para compatibilidad con WTForms si es necesario, la etiqueta es fácil de usar
        choices = [(str(s[0]), f"Segmento {s[0]}") for s in segments]
        return choices
    except Exception as e:
        # Registrar error o manejar apropiadamente
        print(f"Error al obtener las opciones de segmento: {e}")
        return [] # Devolver lista vacía en caso de error

class CampaignForm(FlaskForm):
    """Formulario para crear y editar Campañas AdFlux."""
    name = StringField(
        'Nombre de la Campaña', 
        validators=[DataRequired(), Length(min=3, max=255)],
        render_kw={"placeholder": "ej., Campaña de Prácticas SWE Verano 2025"}
    )
    description = TextAreaField(
        'Descripción', 
        validators=[Optional(), Length(max=1000)],
        render_kw={"rows": 3, "placeholder": "Opcional: Describe el objetivo de la campaña o la audiencia objetivo..."}
    )
    platform = SelectField(
        'Plataforma', 
        choices=[
            ('meta', 'Meta (Facebook/Instagram)'),
            # Añadir otras plataformas a medida que sean soportadas
            # ('linkedin', 'LinkedIn'),
            ('google', 'Google Ads'),
        ],
        validators=[DataRequired()]
    )
    daily_budget = FloatField(
        'Presupuesto Diario ($)', 
        validators=[Optional(), NumberRange(min=1.00)], # Presupuesto mínimo de $1.00
        render_kw={"placeholder": "ej., 5.00", "step": "0.01"}
    )
    # Usar QuerySelectField para crear un desplegable a partir de los resultados de la consulta de JobOpening
    job_opening = QuerySelectField(
        'Vincular a Oferta de Trabajo (Opcional)',
        query_factory=get_job_openings,
        get_label='title', # Mostrar el título del trabajo en el desplegable
        get_pk=lambda obj: obj.job_id, # Usar job_id como valor
        allow_blank=True,
        blank_text='-- Selecciona un Trabajo --',
        validators=[Optional()]
    )
    # Añadir campo para seleccionar segmentos objetivo
    target_segment_ids = SelectMultipleField(
        'Segmentos Objetivo',
        choices=get_segment_choices, # Usar la función auxiliar para poblar las opciones dinámicamente
        option_widget=widgets.CheckboxInput(), # Mostrar como casillas de verificación
        widget=widgets.ListWidget(prefix_label=False), # Renderizar casillas de verificación en una lista
        coerce=int, # Convertir los valores enviados de nuevo a enteros
        validators=[Optional()]
    )
    # Campos de Creativo Publicitario
    primary_text = TextAreaField(
        'Texto Principal',
        validators=[Optional(), Length(max=200)],
        render_kw={"rows": 3, "placeholder": "Texto principal del anuncio (150-200 caracteres)"}
    )
    headline = StringField(
        'Titular',
        validators=[Optional(), Length(max=40)],
        render_kw={"placeholder": "Titular llamativo (25-40 caracteres)"}
    )
    link_description = StringField(
        'Descripción del Enlace',
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "Descripción breve para la vista previa del enlace (30-50 caracteres)"}
    )
    creative_image = FileField(
        'Imagen del Creativo',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'png', 'jpeg'], '¡Solo imágenes!')
        ]
    )
    status = SelectField(
        'Estado', 
        choices=[
            ('draft', 'Borrador'),
            ('active', 'Activa'),
            ('paused', 'Pausada'),
            ('archived', 'Archivada')
        ],
        default='draft',
        validators=[DataRequired()]
    )
    submit = SubmitField('Guardar Campaña')

# --- Formulario de Edición de Segmento --- #
class SegmentForm(FlaskForm):
    name = StringField('Nombre del Segmento', 
                       validators=[DataRequired(), Length(min=2, max=100)],
                       render_kw={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"})
    description = TextAreaField('Descripción', 
                                validators=[Optional(), Length(max=500)],
                                render_kw={"class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm", "rows": 3})
    submit = SubmitField('Guardar Segmento', 
                         render_kw={"class": "inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"}) 