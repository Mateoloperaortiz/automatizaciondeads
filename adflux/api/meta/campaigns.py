"""
Gestión de campañas para la API de Meta (Facebook/Instagram) Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
campañas publicitarias en Meta Ads.
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
from adflux.exceptions.base import AdFluxError

# Configurar logger
logger = get_logger("MetaCampaigns")


class CampaignManager:
    """
    Gestor de campañas para la API de Meta Ads.
    """

    def __init__(self, client: Optional[MetaApiClient] = None):
        """
        Inicializa el gestor de campañas.

        Args:
            client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()

    @handle_meta_api_error
    def get_campaigns(self, ad_account_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Obtiene las campañas para una cuenta publicitaria específica.

        Args:
            ad_account_id: ID de la cuenta publicitaria (ej., 'act_123456789').

        Returns:
            Una tupla con: (éxito, mensaje, lista de campañas).
        """
        api = self.client.get_api()
        if not api:
            raise AdFluxError(message="No se pudo inicializar la API de Meta", status_code=500)

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.campaign import Campaign

            # Definir los campos que queremos recuperar
            fields = [
                Campaign.Field.id,
                Campaign.Field.name,
                Campaign.Field.status,
                Campaign.Field.objective,
                Campaign.Field.effective_status,
                Campaign.Field.created_time,
                Campaign.Field.start_time,
                Campaign.Field.stop_time,
                Campaign.Field.daily_budget,
                Campaign.Field.lifetime_budget,
                Campaign.Field.budget_remaining,
            ]

            account = AdAccount(ad_account_id)
            campaigns = account.get_campaigns(fields=fields)

            # Procesar los resultados para un formato más amigable
            campaigns_list = []
            for campaign in campaigns:
                campaign_data = {
                    "id": campaign.get(Campaign.Field.id),
                    "name": campaign.get(Campaign.Field.name),
                    "status": campaign.get(Campaign.Field.status),
                    "objective": campaign.get(Campaign.Field.objective),
                    "effective_status": campaign.get(Campaign.Field.effective_status),
                    "created_time": campaign.get(Campaign.Field.created_time),
                    "start_time": campaign.get(Campaign.Field.start_time),
                    "stop_time": campaign.get(Campaign.Field.stop_time),
                    "daily_budget": campaign.get(Campaign.Field.daily_budget),
                    "lifetime_budget": campaign.get(Campaign.Field.lifetime_budget),
                    "budget_remaining": campaign.get(Campaign.Field.budget_remaining),
                }
                campaigns_list.append(campaign_data)

            logger.info(
                f"Se recuperaron {len(campaigns_list)} campañas para la cuenta {ad_account_id}."
            )
            return True, f"Se recuperaron {len(campaigns_list)} campañas.", campaigns_list

        except FacebookRequestError:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            raise AdFluxError(message=f"Error al importar el objeto del SDK de Facebook: {e}", status_code=500)

    @handle_meta_api_error
    def create_campaign(
        self,
        ad_account_id: str,
        name: str,
        objective: str,
        status: str = "PAUSED",
        special_ad_categories: List[str] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Crea una nueva campaña en la cuenta publicitaria especificada.

        Args:
            ad_account_id: ID de la cuenta publicitaria (ej., 'act_123456789').
            name: Nombre para la nueva campaña.
            objective: Objetivo de la campaña (ej., 'LINK_CLICKS', 'CONVERSIONS', 'REACH').
            status: Estado inicial ('ACTIVE' o 'PAUSED'). Por defecto 'PAUSED'.
            special_ad_categories: Lista de categorías especiales si aplica (ej., ['EMPLOYMENT']).

        Returns:
            Una tupla con: (éxito, mensaje, datos de la campaña creada).
        """
        api = self.client.get_api()
        if not api:
            raise AdFluxError(message="No se pudo inicializar la API de Meta", status_code=500)

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.campaign import Campaign

            account = AdAccount(ad_account_id)

            # Preparar los parámetros para la creación de la campaña
            params = {
                Campaign.Field.name: name,
                Campaign.Field.objective: objective,
                Campaign.Field.status: status,
            }

            # Añadir categorías especiales si se proporcionan
            if special_ad_categories:
                params[Campaign.Field.special_ad_categories] = special_ad_categories

            # Crear la campaña
            campaign = account.create_campaign(params=params)
            campaign_id = campaign.get(Campaign.Field.id)

            logger.info(f"Se creó correctamente la campaña '{name}' con ID: {campaign_id}")

            return (
                True,
                f"Se creó correctamente la campaña '{name}'",
                {"id": campaign_id, "name": name, "objective": objective, "status": status},
            )

        except FacebookRequestError:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            raise AdFluxError(message=f"Error al importar el objeto del SDK de Facebook: {e}", status_code=500)


# Crear una instancia del gestor por defecto
_default_manager = None


def get_campaign_manager(client: Optional[MetaApiClient] = None) -> CampaignManager:
    """
    Obtiene una instancia del gestor de campañas.

    Args:
        client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.

    Returns:
        Una instancia de CampaignManager.
    """
    global _default_manager

    if client:
        return CampaignManager(client)

    if _default_manager is None:
        _default_manager = CampaignManager()

    return _default_manager
