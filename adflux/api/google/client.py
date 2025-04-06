"""
Cliente para la API de Google Ads.

Este módulo proporciona la clase principal para interactuar con la API de Google Ads,
incluyendo la inicialización y configuración del cliente.
"""

import os
from typing import Dict, Any, Optional, Tuple
import yaml

# Intentar importar Google Ads SDK, pero no fallar si no está disponible
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    GOOGLE_ADS_SDK_AVAILABLE = True
except ImportError:
    GoogleAdsClient = None
    GoogleAdsException = Exception
    GOOGLE_ADS_SDK_AVAILABLE = False

from adflux.api.common.error_handling import handle_google_ads_api_error
from adflux.api.common.logging import get_logger

# Configurar logger
logger = get_logger("GoogleAdsAPI")


class GoogleAdsApiClient:
    """
    Cliente para interactuar con la API de Google Ads.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        developer_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        login_customer_id: Optional[str] = None,
        config_path: Optional[str] = None,
    ):
        """
        Inicializa el cliente de la API de Google Ads.

        Args:
            client_id: ID de cliente de OAuth. Si es None, se usa GOOGLE_CLIENT_ID del entorno.
            client_secret: Secreto de cliente de OAuth. Si es None, se usa GOOGLE_CLIENT_SECRET del entorno.
            developer_token: Token de desarrollador. Si es None, se usa GOOGLE_DEVELOPER_TOKEN del entorno.
            refresh_token: Token de actualización. Si es None, se usa GOOGLE_REFRESH_TOKEN del entorno.
            login_customer_id: ID de cliente de inicio de sesión. Si es None, se usa GOOGLE_LOGIN_CUSTOMER_ID del entorno.
            config_path: Ruta al archivo de configuración YAML. Si se proporciona, se usa en lugar de los parámetros individuales.
        """
        # Buscar variables con prefijo GOOGLE_ADS_ primero, luego con prefijo GOOGLE_
        self.client_id = (
            client_id or os.getenv("GOOGLE_ADS_CLIENT_ID") or os.getenv("GOOGLE_CLIENT_ID")
        )
        self.client_secret = (
            client_secret
            or os.getenv("GOOGLE_ADS_CLIENT_SECRET")
            or os.getenv("GOOGLE_CLIENT_SECRET")
        )
        self.developer_token = (
            developer_token
            or os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
            or os.getenv("GOOGLE_DEVELOPER_TOKEN")
        )
        self.refresh_token = (
            refresh_token
            or os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
            or os.getenv("GOOGLE_REFRESH_TOKEN")
        )
        self.login_customer_id = (
            login_customer_id
            or os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
            or os.getenv("GOOGLE_LOGIN_CUSTOMER_ID")
        )

        # Registrar las credenciales encontradas (sin mostrar valores sensibles)
        logger.info(
            "Credenciales de Google Ads encontradas: "
            + f"client_id={'✓' if self.client_id else '✗'}, "
            + f"client_secret={'✓' if self.client_secret else '✗'}, "
            + f"developer_token={'✓' if self.developer_token else '✗'}, "
            + f"refresh_token={'✓' if self.refresh_token else '✗'}, "
            + f"login_customer_id={'✓' if self.login_customer_id else '✗'}"
        )
        self.config_path = config_path
        self.client = None

    def initialize(self) -> Optional[GoogleAdsClient]:
        """
        Inicializa el cliente de la API de Google Ads con las credenciales.

        Returns:
            La instancia del cliente inicializada, o None si falla la inicialización.
        """
        if not GOOGLE_ADS_SDK_AVAILABLE:
            logger.error(
                "El SDK de Google Ads no está disponible. Instálalo con 'pip install google-ads'."
            )
            return None

        try:
            # Si se proporciona una ruta de configuración, usar esa configuración
            if self.config_path and os.path.exists(self.config_path):
                logger.info(f"Usando archivo de configuración: {self.config_path}")
                self.client = GoogleAdsClient.load_from_storage(self.config_path)
                return self.client

            # De lo contrario, usar las credenciales proporcionadas
            if not all(
                [self.client_id, self.client_secret, self.developer_token, self.refresh_token]
            ):
                logger.error(
                    "Se requieren client_id, client_secret, developer_token y refresh_token para inicializar la API de Google Ads."
                )
                return None

            # Crear configuración
            config = {
                "developer_token": self.developer_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "use_proto_plus": True,  # Recomendado para mejor rendimiento
            }

            # Añadir login_customer_id si está disponible
            if self.login_customer_id:
                config["login_customer_id"] = self.login_customer_id

            # Inicializar cliente
            self.client = GoogleAdsClient.load_from_dict(config)
            logger.info("Cliente de Google Ads inicializado correctamente.")
            return self.client

        except Exception as e:
            logger.error(f"Error al inicializar el cliente de Google Ads: {e}", e)
            return None

    def get_client(self) -> Optional[GoogleAdsClient]:
        """
        Obtiene la instancia del cliente, inicializándola si es necesario.

        Returns:
            La instancia del cliente inicializada, o None si falla la inicialización.
        """
        if not self.client:
            return self.initialize()
        return self.client

    @handle_google_ads_api_error
    def test_connection(self, customer_id: str) -> Dict[str, Any]:
        """
        Prueba la conexión a la API de Google Ads usando las credenciales proporcionadas.

        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).

        Returns:
            Un diccionario con el resultado de la prueba.
        """
        client = self.get_client()
        if not client:
            return {
                "success": False,
                "message": "No se pudo inicializar el cliente de Google Ads",
                "data": None,
            }

        try:
            # Crear servicio de GoogleAdsService
            google_ads_service = client.get_service("GoogleAdsService")

            # Crear consulta para obtener información básica de la cuenta
            query = """
                SELECT
                  customer.id,
                  customer.descriptive_name,
                  customer.currency_code
                FROM customer
                LIMIT 1
            """

            # Ejecutar consulta
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Procesar resultados
            for row in response:
                customer = row.customer
                return {
                    "success": True,
                    "message": f"Conexión exitosa a la cuenta: {customer.descriptive_name}",
                    "data": {
                        "customer_id": customer.id,
                        "descriptive_name": customer.descriptive_name,
                        "currency_code": customer.currency_code,
                    },
                }

            # Si no hay resultados
            return {
                "success": True,
                "message": "Conexión exitosa, pero no se encontraron datos de la cuenta",
                "data": None,
            }

        except GoogleAdsException:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al probar la conexión a Google Ads: {e}", e)
            return {"success": False, "message": f"Error inesperado: {str(e)}", "data": None}

    def create_config_file(self, path: str) -> Tuple[bool, str]:
        """
        Crea un archivo de configuración YAML para Google Ads.

        Args:
            path: Ruta donde guardar el archivo de configuración.

        Returns:
            Una tupla con: (éxito, mensaje).
        """
        if not all([self.client_id, self.client_secret, self.developer_token, self.refresh_token]):
            return (
                False,
                "Se requieren client_id, client_secret, developer_token y refresh_token para crear el archivo de configuración.",
            )

        try:
            # Crear configuración
            config = {
                "developer_token": self.developer_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "use_proto_plus": True,
            }

            # Añadir login_customer_id si está disponible
            if self.login_customer_id:
                config["login_customer_id"] = self.login_customer_id

            # Guardar configuración en archivo YAML
            with open(path, "w") as file:
                yaml.dump(config, file)

            logger.info(f"Archivo de configuración de Google Ads creado en: {path}")
            return True, f"Archivo de configuración creado en: {path}"

        except Exception as e:
            logger.error(f"Error al crear el archivo de configuración de Google Ads: {e}", e)
            return False, f"Error al crear el archivo de configuración: {str(e)}"


# Crear una instancia del cliente por defecto
_default_client = None


def get_client(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    developer_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    login_customer_id: Optional[str] = None,
    config_path: Optional[str] = None,
) -> GoogleAdsApiClient:
    """
    Obtiene una instancia del cliente de la API de Google Ads.

    Si se proporcionan credenciales, se crea un nuevo cliente con esas credenciales.
    Si no, se devuelve el cliente por defecto (creándolo si es necesario).

    Args:
        client_id: ID de cliente de OAuth.
        client_secret: Secreto de cliente de OAuth.
        developer_token: Token de desarrollador.
        refresh_token: Token de actualización.
        login_customer_id: ID de cliente de inicio de sesión.
        config_path: Ruta al archivo de configuración YAML.

    Returns:
        Una instancia de GoogleAdsApiClient.
    """
    global _default_client

    if any(
        [client_id, client_secret, developer_token, refresh_token, login_customer_id, config_path]
    ):
        return GoogleAdsApiClient(
            client_id, client_secret, developer_token, refresh_token, login_customer_id, config_path
        )

    if _default_client is None:
        _default_client = GoogleAdsApiClient()

    return _default_client
