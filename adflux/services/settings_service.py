"""
Servicio para la lógica de negocio relacionada con la configuración.
"""

import os
from flask import current_app

# Asumiendo que los clientes API pueden ser importados y usados directamente
from ..api.meta.client import get_client as get_meta_client
from ..api.google.client import get_client as get_google_client
from ..api.gemini.client import get_client as get_gemini_client

# TODO: Considerar usar una librería como python-dotenv para leer/escribir .env
# from dotenv import set_key, find_dotenv

class SettingsService:
    """Contiene la lógica de negocio para gestionar la configuración."""

    def get_api_settings(self):
        """Obtiene la configuración actual de las APIs desde las variables de entorno."""
        return {
            "meta": {
                "app_id": os.environ.get("META_APP_ID", ""),
                "app_secret": os.environ.get("META_APP_SECRET", ""),
                "access_token": os.environ.get("META_ACCESS_TOKEN", ""),
                "ad_account_id": os.environ.get("META_AD_ACCOUNT_ID", ""), # Nota: El form usa ad_account_id, no META_ACCOUNT_ID
                "page_id": os.environ.get("META_PAGE_ID", "")
            },
            "google": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
                "developer_token": os.environ.get("GOOGLE_DEVELOPER_TOKEN", ""),
                "refresh_token": os.environ.get("GOOGLE_REFRESH_TOKEN", ""),
                "customer_id": os.environ.get("GOOGLE_CUSTOMER_ID", "")
            },
            "gemini": {
                "api_key": os.environ.get("GEMINI_API_KEY", "")
            }
        }

    def test_meta_connection(self, settings):
        """Prueba la conexión con la API de Meta usando las credenciales proporcionadas."""
        app_id = settings.get("app_id")
        app_secret = settings.get("app_secret")
        access_token = settings.get("access_token")
        ad_account_id = settings.get("ad_account_id")

        if not (app_id and app_secret and access_token and ad_account_id):
            return False, "Se requieren todos los campos para probar la conexión.", None

        try:
            client = get_meta_client(app_id=app_id, app_secret=app_secret, access_token=access_token)
            success, message, data = client.test_connection(ad_account_id)
            return success, message, data
        except Exception as e:
            current_app.logger.error(f"Error en prueba de conexión Meta API: {e}", exc_info=True)
            return False, str(e), None

    def test_google_connection(self, settings):
        """Prueba la conexión con la API de Google Ads usando las credenciales proporcionadas."""
        client_id = settings.get("client_id")
        client_secret = settings.get("client_secret")
        developer_token = settings.get("developer_token")
        refresh_token = settings.get("refresh_token")
        customer_id = settings.get("customer_id")

        if not (client_id and client_secret and developer_token and refresh_token and customer_id):
            return False, "Se requieren todos los campos para probar la conexión.", None

        try:
            client = get_google_client(
                client_id=client_id,
                client_secret=client_secret,
                developer_token=developer_token,
                refresh_token=refresh_token,
            )
            # El método test_connection en el cliente original devuelve un dict
            result = client.test_connection(customer_id)
            return result.get("success", False), result.get("message", "Error desconocido"), None
        except Exception as e:
            current_app.logger.error(f"Error en prueba de conexión Google Ads API: {e}", exc_info=True)
            return False, str(e), None

    def test_gemini_connection(self, settings):
        """Prueba la conexión con la API de Gemini usando la clave proporcionada."""
        api_key = settings.get("api_key")
        # Validación simple, podría mejorarse
        if not api_key or len(api_key) < 5:
             return False, "Se requiere una clave API válida (mínimo 5 caracteres).", None

        try:
            client = get_gemini_client(api_key)
            success, message, data = client.test_connection()
            return success, message, data
        except Exception as e:
            current_app.logger.error(f"Error en prueba de conexión Gemini API: {e}", exc_info=True)
            return False, str(e), None

    def save_settings(self, platform, settings_data):
        """Guarda la configuración para una plataforma específica.

        Args:
            platform (str): 'meta', 'google', o 'gemini'.
            settings_data (dict): Diccionario con las claves y valores a guardar.

        Returns:
            tuple: (bool: success, str: message)
        """
        # --- Punto de Mejora: Escribir en .env --- #
        # Aquí deberíamos usar una librería como python-dotenv para actualizar
        # el archivo .env de forma segura.
        # Ejemplo conceptual con python-dotenv:
        # dotenv_path = find_dotenv()
        # for key, value in settings_data.items():
        #     env_var_name = f"{platform.upper()}_{key.upper()}" # Ajustar según nombres en .env
        #     set_key(dotenv_path, env_var_name, value)

        # Por ahora, solo actualizamos os.environ (afecta solo al proceso actual)
        try:
            prefix = platform.upper()
            if platform == "meta":
                # Asegurar que los nombres coinciden con los usados en get_api_settings y el form
                os.environ["META_APP_ID"] = settings_data.get("app_id", "")
                os.environ["META_APP_SECRET"] = settings_data.get("app_secret", "")
                os.environ["META_ACCESS_TOKEN"] = settings_data.get("access_token", "")
                os.environ["META_AD_ACCOUNT_ID"] = settings_data.get("ad_account_id", "")
                os.environ["META_PAGE_ID"] = settings_data.get("page_id", "")
            elif platform == "google":
                os.environ["GOOGLE_CLIENT_ID"] = settings_data.get("client_id", "")
                os.environ["GOOGLE_CLIENT_SECRET"] = settings_data.get("client_secret", "")
                os.environ["GOOGLE_DEVELOPER_TOKEN"] = settings_data.get("developer_token", "")
                os.environ["GOOGLE_REFRESH_TOKEN"] = settings_data.get("refresh_token", "")
                os.environ["GOOGLE_CUSTOMER_ID"] = settings_data.get("customer_id", "")
            elif platform == "gemini":
                os.environ["GEMINI_API_KEY"] = settings_data.get("api_key", "")
            else:
                return False, f"Plataforma '{platform}' no reconocida."

            current_app.logger.info(f"Configuración de {platform.capitalize()} API actualizada en os.environ.")
            # Advertir que el cambio no es persistente
            current_app.logger.warning("Los cambios en la configuración solo afectan al proceso actual. Reinicie la aplicación y workers para aplicar los cambios globalmente si no se usa escritura en .env.")
            return True, f"Configuración de {platform.capitalize()} API actualizada (solo proceso actual)."

        except Exception as e:
            current_app.logger.error(f"Error al guardar configuración {platform.capitalize()} API: {e}", exc_info=True)
            return False, str(e)

    def generate_google_config_file(self, settings):
         """Genera el archivo google-ads.yaml."""
         client_id = settings.get("client_id")
         client_secret = settings.get("client_secret")
         developer_token = settings.get("developer_token")
         refresh_token = settings.get("refresh_token")

         if not (client_id and client_secret and developer_token and refresh_token):
             return False, "Se requieren Client ID, Client Secret, Developer Token y Refresh Token."

         try:
             client = get_google_client(
                 client_id=client_id,
                 client_secret=client_secret,
                 developer_token=developer_token,
                 refresh_token=refresh_token,
             )
             # Asegurarse que la carpeta instance existe
             instance_path = current_app.instance_path
             os.makedirs(instance_path, exist_ok=True)
             config_path = os.path.join(instance_path, "google-ads.yaml")
             success, message = client.create_config_file(config_path)
             return success, message
         except Exception as e:
             current_app.logger.error(f"Error al generar archivo de configuración de Google Ads: {e}", exc_info=True)
             return False, str(e)

    def get_gemini_models(self, api_key):
        """Obtiene la lista de modelos disponibles de Gemini."""
        if not api_key or len(api_key) < 5:
             return False, "Se requiere una clave API válida.", None
        try:
            client = get_gemini_client(api_key)
            success, message, data = client.get_available_models()
            return success, message, data
        except Exception as e:
            current_app.logger.error(f"Error al obtener modelos de Gemini API: {e}", exc_info=True)
            return False, str(e), None 