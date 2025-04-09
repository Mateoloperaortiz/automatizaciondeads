"""
Rutas de configuración para AdFlux (Refactorizado para usar SettingsService).

Este módulo contiene las rutas relacionadas con la configuración de la aplicación.
"""

from flask import Blueprint, render_template, flash, request, current_app, redirect, url_for
from ..forms import MetaApiSettingsForm, GoogleAdsSettingsForm, GeminiSettingsForm
from flask_wtf.csrf import generate_csrf

# Importar el servicio
from ..services.settings_service import SettingsService

# Instanciar el servicio
settings_service = SettingsService()

# Definir el blueprint
settings_bp = Blueprint("settings", __name__, template_folder="../templates")


@settings_bp.route("/", methods=["GET", "POST"])
def settings():
    """Renderiza y procesa la página de configuración usando SettingsService."""
    csrf_token_value = generate_csrf()

    # Inicializar formularios
    meta_form = MetaApiSettingsForm(prefix="meta") # Usar prefijos para evitar colisiones de campos
    google_form = GoogleAdsSettingsForm(prefix="google")
    gemini_form = GeminiSettingsForm(prefix="gemini")

    # Formularios agrupados para facilitar el manejo
    forms = {
        "meta": meta_form,
        "google": google_form,
        "gemini": gemini_form
    }

    if request.method == "POST":
        platform = request.form.get("platform")
        action = request.form.get("action")
        form = forms.get(platform)

        if not form:
            flash("Plataforma desconocida.", "error")
            return redirect(url_for("settings.settings"))

        # Extraer datos del formulario específico que se envió
        # WTForms maneja automáticamente los prefijos si se usan en el POST
        form_data = request.form.to_dict()

        # --- Manejar Acciones --- #

        if action == f"save_{platform}":
            if form.validate_on_submit():
                # Pasar solo los datos relevantes del formulario al servicio
                # (WTForms data incluye csrf_token, etc.)
                service_data = {k: v for k, v in form.data.items() if k not in ['csrf_token', 'submit']}
                success, message = settings_service.save_settings(platform, service_data)
                flash(message, "success" if success else "error")
            else:
                # Mostrar errores de validación
                for field, errors in form.errors.items():
                    # Usar el label del campo para mensajes más amigables
                    field_label = getattr(getattr(form, field, None), 'label', None)
                    field_name = field_label.text if field_label else field.replace('_', ' ').title()
                    for error in errors:
                        flash(f"Error en '{field_name}': {error}", "error")

        elif action == f"test_{platform}":
            # Para la prueba, usamos los datos enviados en el POST, no necesariamente los validados
            test_settings = {}
            if platform == "meta":
                 test_settings = {
                     "app_id": form_data.get(f"{platform}-app_id"),
                     "app_secret": form_data.get(f"{platform}-app_secret"),
                     "access_token": form_data.get(f"{platform}-access_token"),
                     "ad_account_id": form_data.get(f"{platform}-ad_account_id")
                 }
            elif platform == "google":
                  test_settings = {
                     "client_id": form_data.get(f"{platform}-client_id"),
                     "client_secret": form_data.get(f"{platform}-client_secret"),
                     "developer_token": form_data.get(f"{platform}-developer_token"),
                     "refresh_token": form_data.get(f"{platform}-refresh_token"),
                     "customer_id": form_data.get(f"{platform}-customer_id")
                  }
            elif platform == "gemini":
                  test_settings = {"api_key": form_data.get(f"{platform}-api_key")} # Correcto

            # Llamar al método de prueba correspondiente
            test_method = getattr(settings_service, f"test_{platform}_connection", None)
            if test_method:
                success, message, _ = test_method(test_settings)
                flash(message, "success" if success else "error")
            else:
                flash(f"Acción de prueba desconocida para {platform}", "error")

        elif platform == "google" and action == "generate_google_config":
            config_settings = {
                 "client_id": form_data.get(f"{platform}-client_id"),
                 "client_secret": form_data.get(f"{platform}-client_secret"),
                 "developer_token": form_data.get(f"{platform}-developer_token"),
                 "refresh_token": form_data.get(f"{platform}-refresh_token")
             }
            success, message = settings_service.generate_google_config_file(config_settings)
            flash(message, "success" if success else "error")

        elif platform == "gemini" and action == "list_gemini_models":
            api_key = form_data.get(f"{platform}-api_key")
            success, message, data = settings_service.get_gemini_models(api_key)
            if success:
                 models = data if data else []
                 model_names = [model.get("name") for model in models if model.get("name")]
                 if model_names:
                     flash(f"Modelos Gemini disponibles: {len(model_names)}", "info")
                     # Podríamos pasar los nombres a la plantilla si quisiéramos mostrarlos directamente
                 else:
                     flash("No se encontraron modelos Gemini.", "info")
            else:
                 flash(f"Error al obtener modelos Gemini: {message}", "error")
        else:
             # Acción desconocida dentro de una plataforma
             flash(f"Acción '{action}' desconocida para la plataforma '{platform}'.", "warning")

        # Recargar datos después de la acción POST para reflejar cambios (si solo afecta os.environ)
        # O idealmente, redirigir para evitar reenvío del formulario (Patrón POST-Redirect-GET)
        # Por simplicidad aquí, no redirigimos, pero poblamos de nuevo.
        # ¡PERO! Como save_settings solo afecta os.environ, necesitamos leer de nuevo.
        current_settings = settings_service.get_api_settings()
        meta_form.process(data=current_settings.get("meta"))
        google_form.process(data=current_settings.get("google"))
        gemini_form.process(data=current_settings.get("gemini"))
        # Esto es necesario porque no estamos usando PRG y os.environ se actualizó.


    # --- Manejar GET o cargar después de POST --- #
    else: # request.method == "GET"
        current_settings = settings_service.get_api_settings()
        # Poblar formularios con datos actuales
        # Usar data= en lugar de obj= porque los nombres de campo pueden no coincidir exactamente
        # y estamos usando prefijos.
        meta_form.process(data=current_settings.get("meta"))
        google_form.process(data=current_settings.get("google"))
        gemini_form.process(data=current_settings.get("gemini"))


    # Obtener modelos disponibles para la plantilla (siempre que haya una clave API válida)
    available_models = []
    gemini_api_key = gemini_form.api_key.data
    if gemini_api_key and len(gemini_api_key) >= 5:
        success, _, data = settings_service.get_gemini_models(gemini_api_key)
        if success and data:
            available_models = data
            current_app.logger.info(f"Cargados {len(available_models)} modelos de Gemini para la plantilla")

    return render_template(
        "settings.html",
        title="Configuración",
        meta_form=meta_form,
        google_form=google_form,
        gemini_form=gemini_form,
        csrf_token_value=csrf_token_value,
        available_models=available_models,
    )

# Eliminar importaciones innecesarias que ahora están en el servicio
# import os
# from ..api.meta.client import get_client as get_meta_client
# ... etc ...
