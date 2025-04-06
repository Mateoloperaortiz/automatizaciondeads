"""
Gestión de anuncios para la API de Meta (Facebook/Instagram) Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
anuncios en Meta Ads.
"""

from typing import Tuple, List, Dict, Any, Optional

# Intentar importar Facebook Business SDK, pero no fallar si no está disponible
try:
    from facebook_business.exceptions import FacebookRequestError

    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FacebookRequestError = Exception
    FACEBOOK_SDK_AVAILABLE = False

from adflux.api.common.error_handling import handle_meta_api_error
from adflux.api.common.logging import get_logger
from adflux.api.meta.client import get_client, MetaApiClient

# Configurar logger
logger = get_logger("MetaAds")


class AdManager:
    """
    Gestor de anuncios para la API de Meta Ads.
    """

    def __init__(self, client: Optional[MetaApiClient] = None):
        """
        Inicializa el gestor de anuncios.

        Args:
            client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()

    @handle_meta_api_error
    def get_ads(self, ad_set_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Obtiene los anuncios para un conjunto de anuncios específico.

        Args:
            ad_set_id: ID del conjunto de anuncios.

        Returns:
            Una tupla con: (éxito, mensaje, lista de anuncios).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", []

        try:
            from facebook_business.adobjects.adset import AdSet
            from facebook_business.adobjects.ad import Ad

            # Definir los campos que queremos recuperar
            fields = [
                Ad.Field.id,
                Ad.Field.name,
                Ad.Field.status,
                Ad.Field.adset_id,
                Ad.Field.creative,
                Ad.Field.created_time,
                Ad.Field.updated_time,
                Ad.Field.effective_status,
            ]

            ad_set = AdSet(ad_set_id)
            ads = ad_set.get_ads(fields=fields)

            # Procesar los resultados para un formato más amigable
            ads_list = []
            for ad in ads:
                ad_data = {
                    "id": ad.get(Ad.Field.id),
                    "name": ad.get(Ad.Field.name),
                    "status": ad.get(Ad.Field.status),
                    "adset_id": ad.get(Ad.Field.adset_id),
                    "creative": ad.get(Ad.Field.creative),
                    "created_time": ad.get(Ad.Field.created_time),
                    "updated_time": ad.get(Ad.Field.updated_time),
                    "effective_status": ad.get(Ad.Field.effective_status),
                }
                ads_list.append(ad_data)

            logger.info(
                f"Se recuperaron {len(ads_list)} anuncios para el conjunto de anuncios {ad_set_id}."
            )
            return True, f"Se recuperaron {len(ads_list)} anuncios.", ads_list

        except FacebookRequestError:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            return False, f"Error al importar el objeto del SDK de Facebook: {e}", []

    @handle_meta_api_error
    def create_ad(
        self,
        ad_account_id: str,
        name: str,
        ad_set_id: str,
        creative_id: str,
        status: str = "PAUSED",
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Crea un nuevo anuncio en la cuenta publicitaria especificada.

        Args:
            ad_account_id: ID de la cuenta publicitaria (ej., 'act_123456789').
            name: Nombre para el nuevo anuncio.
            ad_set_id: ID del conjunto de anuncios al que pertenecerá el anuncio.
            creative_id: ID de la creatividad que se usará para el anuncio.
            status: Estado inicial ('ACTIVE' o 'PAUSED'). Por defecto 'PAUSED'.

        Returns:
            Una tupla con: (éxito, mensaje, datos del anuncio creado).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", {}

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.ad import Ad

            account = AdAccount(ad_account_id)

            # Preparar los parámetros para la creación del anuncio
            params = {
                Ad.Field.name: name,
                Ad.Field.adset_id: ad_set_id,
                Ad.Field.creative: {"creative_id": creative_id},
                Ad.Field.status: status,
            }

            # Crear el anuncio
            ad = account.create_ad(params=params)
            ad_id = ad.get(Ad.Field.id)

            logger.info(f"Se creó correctamente el anuncio '{name}' con ID: {ad_id}")

            return (
                True,
                f"Se creó correctamente el anuncio '{name}'",
                {
                    "id": ad_id,
                    "name": name,
                    "adset_id": ad_set_id,
                    "creative_id": creative_id,
                    "status": status,
                },
            )

        except FacebookRequestError:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            return False, f"Error al importar el objeto del SDK de Facebook: {e}", {}
        except Exception as e:
            logger.error(f"Error inesperado al crear el anuncio Meta '{name}': {e}", e)
            return False, f"Error inesperado al crear el anuncio: {e}", {}


# Crear una instancia del gestor por defecto
_default_manager = None


def get_ad_manager(client: Optional[MetaApiClient] = None) -> AdManager:
    """
    Obtiene una instancia del gestor de anuncios.

    Args:
        client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.

    Returns:
        Una instancia de AdManager.
    """
    global _default_manager

    if client:
        return AdManager(client)

    if _default_manager is None:
        _default_manager = AdManager()

    return _default_manager
