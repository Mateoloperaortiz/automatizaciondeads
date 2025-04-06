"""
Formularios de configuración de API para AdFlux.

Este módulo contiene formularios relacionados con la configuración de APIs externas.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class MetaApiSettingsForm(FlaskForm):
    """
    Formulario para configurar la API de Meta.
    
    Este formulario permite a los usuarios configurar los parámetros de conexión
    a la API de Meta (Facebook/Instagram).
    """
    app_id = StringField(
        'ID de Aplicación', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "ID de aplicación de Meta"}
    )
    app_secret = PasswordField(
        'Secreto de Aplicación', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "Secreto de aplicación de Meta"}
    )
    access_token = PasswordField(
        'Token de Acceso', 
        validators=[DataRequired(), Length(min=5, max=500)],
        render_kw={"placeholder": "Token de acceso de larga duración"}
    )
    ad_account_id = StringField(
        'ID de Cuenta Publicitaria', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "ID de cuenta publicitaria (con o sin 'act_')"}
    )
    page_id = StringField(
        'ID de Página', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "ID de página de Facebook"}
    )
    test_connection = BooleanField(
        'Probar Conexión', 
        default=True,
        validators=[Optional()]
    )
    submit = SubmitField('Guardar Configuración de Meta')


class GoogleAdsSettingsForm(FlaskForm):
    """
    Formulario para configurar la API de Google Ads.
    
    Este formulario permite a los usuarios configurar los parámetros de conexión
    a la API de Google Ads.
    """
    client_id = StringField(
        'ID de Cliente', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "ID de cliente de OAuth"}
    )
    client_secret = PasswordField(
        'Secreto de Cliente', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "Secreto de cliente de OAuth"}
    )
    developer_token = PasswordField(
        'Token de Desarrollador', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "Token de desarrollador de Google Ads"}
    )
    refresh_token = PasswordField(
        'Token de Actualización', 
        validators=[DataRequired(), Length(min=5, max=500)],
        render_kw={"placeholder": "Token de actualización de OAuth"}
    )
    customer_id = StringField(
        'ID de Cliente de Google Ads', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "ID de cliente de Google Ads (sin guiones)"}
    )
    test_connection = BooleanField(
        'Probar Conexión', 
        default=True,
        validators=[Optional()]
    )
    generate_config = BooleanField(
        'Generar Archivo de Configuración', 
        default=False,
        validators=[Optional()]
    )
    submit = SubmitField('Guardar Configuración de Google Ads')


class GeminiSettingsForm(FlaskForm):
    """
    Formulario para configurar la API de Gemini.
    
    Este formulario permite a los usuarios configurar los parámetros de conexión
    a la API de Gemini de Google.
    """
    api_key = PasswordField(
        'Clave API', 
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={"placeholder": "Clave API de Gemini"}
    )
    test_connection = BooleanField(
        'Probar Conexión', 
        default=True,
        validators=[Optional()]
    )
    list_models = BooleanField(
        'Listar Modelos Disponibles', 
        default=False,
        validators=[Optional()]
    )
    submit = SubmitField('Guardar Configuración de Gemini')
