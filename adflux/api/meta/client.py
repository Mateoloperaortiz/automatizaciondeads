"""
Cliente para la API de Meta (Facebook/Instagram) Ads.

Este módulo proporciona la clase principal para interactuar con la API de Meta Ads,
incluyendo la inicialización y prueba de conexión.
"""

import os
from dotenv import load_dotenv
from typing import Tuple, Optional, Dict, Any

# Intentar importar Flask, pero no fallar si no está disponible
try:
    from flask import current_app
except ImportError:
    current_app = None

# Intentar importar Facebook Business SDK, pero no fallar si no está disponible
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.exceptions import FacebookRequestError
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FacebookAdsApi = None
    FacebookRequestError = Exception
    FACEBOOK_SDK_AVAILABLE = False

from adflux.api.common.error_handling import handle_meta_api_error
from adflux.api.common.logging import get_logger

# Cargar variables de entorno
load_dotenv()

# Configurar logger
logger = get_logger("MetaAPI")


class MetaApiClient:
    """
    Cliente para interactuar con la API de Meta (Facebook/Instagram) Ads.
    """

    def __init__(self, app_id=None, app_secret=None, access_token=None):
        """
        Inicializa el cliente de la API de Meta.

        Args:
            app_id: ID de la aplicación de Meta. Si es None, se usa META_APP_ID del entorno.
            app_secret: Secreto de la aplicación de Meta. Si es None, se usa META_APP_SECRET del entorno.
            access_token: Token de acceso de Meta. Si es None, se usa META_ACCESS_TOKEN del entorno.
        """
        self.app_id = app_id or os.getenv('META_APP_ID')
        self.app_secret = app_secret or os.getenv('META_APP_SECRET')
        self.access_token = access_token or os.getenv('META_ACCESS_TOKEN')
        self.api = None

    def initialize(self) -> Optional[FacebookAdsApi]:
        """
        Inicializa la API de Meta Ads con las credenciales.

        Returns:
            La instancia de la API inicializada, o None si falla la inicialización.
        """
        if not all([self.app_id, self.app_secret, self.access_token]):
            logger.error("META_APP_ID, META_APP_SECRET y META_ACCESS_TOKEN deben estar configurados.")
            return None

        try:
            self.api = FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            logger.info("API de Meta Ads inicializada correctamente.")
            return self.api
        except FacebookRequestError as e:
            logger.error(f"Error al inicializar la API de Meta Ads: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al inicializar la API de Meta Ads: {e}", e)
            return None

    def get_api(self) -> Optional[FacebookAdsApi]:
        """
        Obtiene la instancia de la API, inicializándola si es necesario.

        Returns:
            La instancia de la API inicializada, o None si falla la inicialización.
        """
        if not self.api:
            return self.initialize()
        return self.api

    @handle_meta_api_error
    def test_connection(self, ad_account_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Prueba la conexión a la API de Meta usando las credenciales proporcionadas.

        Args:
            ad_account_id: El ID de la cuenta publicitaria (ej., 'act_123456789').

        Returns:
            Una tupla con: (éxito, mensaje, datos adicionales).
        """
        api = self.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", {}

        from facebook_business.adobjects.adaccount import AdAccount

        account = AdAccount(ad_account_id)
        account.api_get(fields=[AdAccount.Field.name])

        account_name = account.get(AdAccount.Field.name, "Nombre Desconocido")
        return True, f"¡Conexión exitosa! Nombre de la Cuenta: {account_name}", {"account_name": account_name}

    @handle_meta_api_error
    def get_ad_accounts(self) -> Tuple[bool, str, list]:
        """
        Obtiene las cuentas publicitarias asociadas con el token de acceso.

        Returns:
            Una tupla con: (éxito, mensaje, lista de cuentas).
        """
        api = self.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", []

        from facebook_business.adobjects.user import User

        user = User(fbid='me')
        ad_accounts = user.get_ad_accounts(fields=['id', 'name', 'account_status'])

        accounts_list = [
            {
                'id': account['id'],
                'name': account['name'],
                'status': account['account_status']
            }
            for account in ad_accounts
        ]

        logger.info(f"Se recuperaron {len(accounts_list)} cuentas publicitarias.")
        return True, f"Se recuperaron {len(accounts_list)} cuentas publicitarias.", accounts_list


# Crear una instancia del cliente por defecto
_default_client = None


def get_client(app_id=None, app_secret=None, access_token=None) -> MetaApiClient:
    """
    Obtiene una instancia del cliente de la API de Meta.

    Si se proporcionan credenciales, se crea un nuevo cliente con esas credenciales.
    Si no, se devuelve el cliente por defecto (creándolo si es necesario).

    Args:
        app_id: ID de la aplicación de Meta.
        app_secret: Secreto de la aplicación de Meta.
        access_token: Token de acceso de Meta.

    Returns:
        Una instancia de MetaApiClient.
    """
    global _default_client

    if all([app_id, app_secret, access_token]):
        return MetaApiClient(app_id, app_secret, access_token)

    if _default_client is None:
        _default_client = MetaApiClient()

    return _default_client
