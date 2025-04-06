"""
Rutas de configuración para AdFlux.

Este módulo contiene las rutas relacionadas con la configuración de la aplicación.
"""

from flask import Blueprint, render_template, flash, request, current_app
import os
from ..forms import MetaApiSettingsForm, GoogleAdsSettingsForm, GeminiSettingsForm
from ..api.meta.client import get_client as get_meta_client
from ..api.google.client import get_client as get_google_client
from ..api.gemini.client import get_client as get_gemini_client
from flask_wtf.csrf import generate_csrf

# Definir el blueprint
settings_bp = Blueprint("settings", __name__, template_folder="../templates")


@settings_bp.route("/", methods=["GET", "POST"])
def settings():
    """Renderiza la página de configuración principal."""
    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()

    # Inicializar formularios
    meta_form = MetaApiSettingsForm()
    google_form = GoogleAdsSettingsForm()
    gemini_form = GeminiSettingsForm()

    # Cargar valores actuales desde variables de entorno
    if request.method == "GET":
        meta_form.app_id.data = os.environ.get("META_APP_ID", "")
        meta_form.app_secret.data = os.environ.get("META_APP_SECRET", "")
        meta_form.access_token.data = os.environ.get("META_ACCESS_TOKEN", "")
        meta_form.ad_account_id.data = os.environ.get("META_AD_ACCOUNT_ID", "")
        meta_form.page_id.data = os.environ.get("META_PAGE_ID", "")

        google_form.client_id.data = os.environ.get("GOOGLE_CLIENT_ID", "")
        google_form.client_secret.data = os.environ.get("GOOGLE_CLIENT_SECRET", "")
        google_form.developer_token.data = os.environ.get("GOOGLE_DEVELOPER_TOKEN", "")
        google_form.refresh_token.data = os.environ.get("GOOGLE_REFRESH_TOKEN", "")
        google_form.customer_id.data = os.environ.get("GOOGLE_CUSTOMER_ID", "")

        gemini_form.api_key.data = os.environ.get("GEMINI_API_KEY", "")

    # Procesar formulario de Meta API
    if (
        request.method == "POST"
        and "platform" in request.form
        and request.form["platform"] == "meta"
    ):
        action = request.form.get("action", "")
        current_app.logger.info(f"Meta form action: {action}")
        current_app.logger.info(f"Meta form data: {request.form}")

        # Manejar la acción de prueba de conexión sin validación completa del formulario
        if action == "test_meta" or request.form.get("test_connection") == "1":
            current_app.logger.info("Ejecutando prueba de conexión Meta API")
            app_id = request.form.get("app_id")
            app_secret = request.form.get("app_secret")
            access_token = request.form.get("access_token")
            ad_account_id = request.form.get("ad_account_id")

            if app_id and app_secret and access_token and ad_account_id:
                current_app.logger.info("Testing Meta API connection")
                try:
                    # Actualizar variables de entorno temporalmente
                    os.environ["META_APP_ID"] = app_id
                    os.environ["META_APP_SECRET"] = app_secret
                    os.environ["META_ACCESS_TOKEN"] = access_token
                    os.environ["META_AD_ACCOUNT_ID"] = ad_account_id

                    client = get_meta_client(
                        app_id=app_id, app_secret=app_secret, access_token=access_token
                    )
                    success, message, _ = client.test_connection(ad_account_id)
                    if success:
                        flash(f"Conexión a Meta API exitosa: {message}", "success")
                        current_app.logger.info(f"Conexión a Meta API exitosa: {message}")
                    else:
                        flash(f"Error al conectar a Meta API: {message}", "error")
                        current_app.logger.info(f"Error al conectar a Meta API: {message}")
                except Exception as e:
                    flash(f"Error al probar la conexión con Meta API: {str(e)}", "error")
                    current_app.logger.error(
                        f"Error en prueba de conexión Meta API: {e}", exc_info=True
                    )
            else:
                flash(
                    "Se requieren todos los campos para probar la conexión con Meta API.", "error"
                )

        # Procesar el formulario completo para guardar configuración
        elif action == "save_meta" and meta_form.validate_on_submit():
            try:
                # Actualizar variables de entorno (en memoria)
                os.environ["META_APP_ID"] = meta_form.app_id.data
                os.environ["META_APP_SECRET"] = meta_form.app_secret.data
                os.environ["META_ACCESS_TOKEN"] = meta_form.access_token.data
                os.environ["META_AD_ACCOUNT_ID"] = meta_form.ad_account_id.data
                os.environ["META_PAGE_ID"] = meta_form.page_id.data

                current_app.logger.info("Saving Meta API configuration")
                flash("Configuración de Meta API actualizada.", "success")
            except Exception as e:
                flash(f"Error al guardar la configuración de Meta API: {str(e)}", "error")
                current_app.logger.error(
                    f"Error al guardar configuración Meta API: {e}", exc_info=True
                )
        elif action == "save_meta":
            # Mostrar errores de validación
            current_app.logger.error(f"Meta form validation errors: {meta_form.errors}")
            for field, errors in meta_form.errors.items():
                for error in errors:
                    flash(f"Error en {field}: {error}", "error")

    # Procesar formulario de Google Ads API
    if (
        request.method == "POST"
        and "platform" in request.form
        and request.form["platform"] == "google"
    ):
        action = request.form.get("action", "")
        current_app.logger.info(f"Google form action: {action}")
        current_app.logger.info(f"Google form data: {request.form}")

        # Manejar la acción de prueba de conexión sin validación completa del formulario
        if action == "test_google":
            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")
            developer_token = request.form.get("developer_token")
            refresh_token = request.form.get("refresh_token")
            customer_id = request.form.get("customer_id")

            if client_id and client_secret and developer_token and refresh_token and customer_id:
                current_app.logger.info("Testing Google Ads API connection")
                try:
                    # Actualizar variables de entorno temporalmente
                    os.environ["GOOGLE_CLIENT_ID"] = client_id
                    os.environ["GOOGLE_CLIENT_SECRET"] = client_secret
                    os.environ["GOOGLE_DEVELOPER_TOKEN"] = developer_token
                    os.environ["GOOGLE_REFRESH_TOKEN"] = refresh_token
                    os.environ["GOOGLE_CUSTOMER_ID"] = customer_id

                    client = get_google_client(
                        client_id=client_id,
                        client_secret=client_secret,
                        developer_token=developer_token,
                        refresh_token=refresh_token,
                    )
                    result = client.test_connection(customer_id)
                    if result.get("success"):
                        flash(
                            f"Conexión a Google Ads API exitosa: {result.get('message')}", "success"
                        )
                    else:
                        flash(
                            f"Error al conectar a Google Ads API: {result.get('message')}", "error"
                        )
                except Exception as e:
                    flash(f"Error al probar la conexión con Google Ads API: {str(e)}", "error")
                    current_app.logger.error(
                        f"Error en prueba de conexión Google Ads API: {e}", exc_info=True
                    )
            else:
                flash(
                    "Se requieren todos los campos para probar la conexión con Google Ads API.",
                    "error",
                )

        # Procesar el formulario completo para guardar configuración
        elif action == "save_google" and google_form.validate_on_submit():
            try:
                # Actualizar variables de entorno (en memoria)
                os.environ["GOOGLE_CLIENT_ID"] = google_form.client_id.data
                os.environ["GOOGLE_CLIENT_SECRET"] = google_form.client_secret.data
                os.environ["GOOGLE_DEVELOPER_TOKEN"] = google_form.developer_token.data
                os.environ["GOOGLE_REFRESH_TOKEN"] = google_form.refresh_token.data
                os.environ["GOOGLE_CUSTOMER_ID"] = google_form.customer_id.data

                current_app.logger.info("Saving Google Ads API configuration")
                flash("Configuración de Google Ads API actualizada.", "success")
            except Exception as e:
                flash(f"Error al guardar la configuración de Google Ads API: {str(e)}", "error")
                current_app.logger.error(
                    f"Error al guardar configuración Google Ads API: {e}", exc_info=True
                )
        elif action == "save_google":
            # Mostrar errores de validación
            current_app.logger.error(f"Google form validation errors: {google_form.errors}")
            for field, errors in google_form.errors.items():
                for error in errors:
                    flash(f"Error en {field}: {error}", "error")

        # Generar archivo de configuración si se solicita
        if (
            request.method == "POST"
            and "platform" in request.form
            and request.form["platform"] == "google"
            and request.form.get("generate_config") == "1"
        ):
            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")
            developer_token = request.form.get("developer_token")
            refresh_token = request.form.get("refresh_token")

            if client_id and client_secret and developer_token and refresh_token:
                try:
                    client = get_google_client(
                        client_id=client_id,
                        client_secret=client_secret,
                        developer_token=developer_token,
                        refresh_token=refresh_token,
                    )
                    config_path = os.path.join(current_app.instance_path, "google-ads.yaml")
                    success, message = client.create_config_file(config_path)
                    if success:
                        flash(
                            f"Archivo de configuración de Google Ads generado: {message}", "success"
                        )
                    else:
                        flash(f"Error al generar archivo de configuración: {message}", "error")
                except Exception as e:
                    flash(
                        f"Error al generar archivo de configuración de Google Ads: {str(e)}",
                        "error",
                    )
                    current_app.logger.error(
                        f"Error al generar archivo de configuración de Google Ads: {e}",
                        exc_info=True,
                    )
            else:
                flash(
                    "Se requieren todos los campos para generar el archivo de configuración de Google Ads.",
                    "error",
                )

    # Procesar formulario de Gemini API
    if (
        request.method == "POST"
        and "platform" in request.form
        and request.form["platform"] == "gemini"
    ):
        action = request.form.get("action", "")
        current_app.logger.info(f"Gemini form action: {action}")
        current_app.logger.info(f"Gemini form data: {request.form}")

        # Manejar la acción de prueba de conexión sin validación completa del formulario
        if action == "test_gemini" or request.form.get("test_connection") == "1":
            api_key = request.form.get("api_key")
            if api_key and api_key != "None" and len(api_key) >= 5:
                current_app.logger.info("Testing Gemini API connection")
                try:
                    # Actualizar variable de entorno temporalmente
                    os.environ["GEMINI_API_KEY"] = api_key

                    client = get_gemini_client(api_key)
                    success, message, data = client.test_connection()
                    if success:
                        models = data.get("models", [])
                        flash(
                            f"Conexión a Gemini API exitosa: {message} ({len(models)} modelos disponibles)",
                            "success",
                        )

                        # Obtener modelos disponibles para mostrar en el dropdown
                        try:
                            success, _, model_data = client.get_available_models()
                            if success and model_data:
                                current_app.logger.info(
                                    f"Obtenidos {len(model_data)} modelos de Gemini"
                                )
                        except Exception as e:
                            current_app.logger.error(f"Error al obtener modelos de Gemini: {e}")
                    else:
                        flash(f"Error al conectar a Gemini API: {message}", "error")
                except Exception as e:
                    flash(f"Error al probar la conexión con Gemini API: {str(e)}", "error")
                    current_app.logger.error(
                        f"Error en prueba de conexión Gemini API: {e}", exc_info=True
                    )
            else:
                flash(
                    "Se requiere una clave API válida para probar la conexión (mínimo 5 caracteres).",
                    "error",
                )

        # Procesar el formulario completo para guardar configuración
        elif action == "save_gemini" and gemini_form.validate_on_submit():
            current_app.logger.info("Gemini form validated successfully")
            try:
                # Actualizar variables de entorno (en memoria)
                os.environ["GEMINI_API_KEY"] = gemini_form.api_key.data
                current_app.logger.info("Saving Gemini API configuration")
                flash("Configuración de Gemini API actualizada.", "success")
            except Exception as e:
                flash(f"Error al guardar la configuración de Gemini API: {str(e)}", "error")
                current_app.logger.error(
                    f"Error al guardar configuración Gemini API: {e}", exc_info=True
                )
        elif action == "save_gemini":
            # Mostrar errores de validación
            current_app.logger.error(f"Gemini form validation errors: {gemini_form.errors}")
            for field, errors in gemini_form.errors.items():
                for error in errors:
                    flash(f"Error en {field}: {error}", "error")

        # Listar modelos disponibles si se solicita (independiente de la acción)
        if (
            request.method == "POST"
            and "platform" in request.form
            and request.form["platform"] == "gemini"
            and request.form.get("list_models") == "1"
        ):
            api_key = request.form.get("api_key")
            if api_key and api_key != "None" and len(api_key) >= 5:
                try:
                    client = get_gemini_client(api_key)
                    success, message, data = client.get_available_models()
                    if success:
                        models = data
                        model_names = [model.get("name") for model in models]
                        flash(f"Modelos Gemini disponibles: {', '.join(model_names)}", "info")
                    else:
                        flash(f"Error al obtener modelos Gemini: {message}", "error")
                except Exception as e:
                    flash(f"Error al listar modelos de Gemini API: {str(e)}", "error")
                    current_app.logger.error(
                        f"Error al listar modelos de Gemini API: {e}", exc_info=True
                    )
            else:
                flash(
                    "Se requiere una clave API válida para listar modelos (mínimo 5 caracteres).",
                    "error",
                )

    # Preparar datos para la plantilla
    available_models = []

    # Si hay una clave API de Gemini válida, intentar obtener los modelos disponibles
    if gemini_form.api_key.data and len(gemini_form.api_key.data) >= 5:
        try:
            client = get_gemini_client(gemini_form.api_key.data)
            success, _, data = client.get_available_models()
            if success and data:
                available_models = data
                current_app.logger.info(
                    f"Cargados {len(available_models)} modelos de Gemini para la plantilla"
                )
        except Exception as e:
            current_app.logger.error(f"Error al cargar modelos de Gemini: {e}")

    return render_template(
        "settings.html",
        title="Configuración",
        meta_form=meta_form,
        google_form=google_form,
        gemini_form=gemini_form,
        csrf_token_value=csrf_token_value,
        available_models=available_models,
    )
