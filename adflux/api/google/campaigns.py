"""
Gestión de campañas para la API de Google Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
campañas publicitarias en Google Ads.
"""

import uuid
import time
from typing import Dict, Any, Optional, List

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
from adflux.api.google.client import get_client, GoogleAdsApiClient

# Configurar logger
logger = get_logger("GoogleAdsCampaigns")


class CampaignManager:
    """
    Gestor de campañas para la API de Google Ads.
    """

    def __init__(self, client: Optional[GoogleAdsApiClient] = None):
        """
        Inicializa el gestor de campañas.

        Args:
            client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()

    @handle_google_ads_api_error
    def get_campaigns(self, customer_id: str) -> Dict[str, Any]:
        """
        Obtiene las campañas para un cliente específico.

        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).

        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'campaigns': []
            }

        try:
            # Crear servicio de GoogleAdsService
            google_ads_service = google_client.get_service("GoogleAdsService")

            # Crear consulta para obtener campañas
            query = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.status,
                  campaign.advertising_channel_type,
                  campaign.start_date,
                  campaign.end_date,
                  campaign_budget.amount_micros
                FROM campaign
                ORDER BY campaign.id
            """

            # Ejecutar consulta
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Procesar resultados
            campaigns = []
            for row in response:
                campaign = row.campaign
                budget = row.campaign_budget

                campaign_data = {
                    'id': campaign.id,
                    'name': campaign.name,
                    'status': campaign.status.name,
                    'channel_type': campaign.advertising_channel_type.name,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date,
                    'budget_micros': budget.amount_micros if budget else None,
                    'budget_dollars': budget.amount_micros / 1000000 if budget else None
                }
                campaigns.append(campaign_data)

            logger.info(f"Se recuperaron {len(campaigns)} campañas para el cliente {customer_id}.")
            return {
                'success': True,
                'message': f"Se recuperaron {len(campaigns)} campañas.",
                'campaigns': campaigns
            }

        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al obtener campañas para el cliente {customer_id}: {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'campaigns': []
            }

    @handle_google_ads_api_error
    def create_campaign(
        self,
        customer_id: str,
        name: str,
        daily_budget_micros: int,
        adflux_campaign_id: Optional[int] = None,
        status: str = "PAUSED"
    ) -> Dict[str, Any]:
        """
        Crea una nueva campaña en Google Ads.

        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            name: Nombre para la nueva campaña.
            daily_budget_micros: Presupuesto diario en micros (1 dólar = 1,000,000 micros).
            adflux_campaign_id: ID de la campaña en AdFlux. Se añadirá al nombre de la campaña.
            status: Estado inicial ('ENABLED', 'PAUSED', 'REMOVED'). Por defecto 'PAUSED'.

        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'external_ids': None
            }

        try:
            # Añadir un identificador único al nombre de la campaña
            campaign_name = name
            if adflux_campaign_id:
                campaign_name = f"AdFlux {adflux_campaign_id}: {name}"
            campaign_name = f"{campaign_name} - {uuid.uuid4()}"

            # Convertir estado a enum
            campaign_status = getattr(google_client.enums.CampaignStatusEnum, status)

            # Crear presupuesto
            campaign_budget_service = google_client.get_service("CampaignBudgetService")
            campaign_budget_operation = google_client.get_type("CampaignBudgetOperation")
            campaign_budget = campaign_budget_operation.create

            campaign_budget.name = f"Budget for {campaign_name}"
            campaign_budget.amount_micros = daily_budget_micros
            campaign_budget.delivery_method = google_client.enums.BudgetDeliveryMethodEnum.STANDARD
            campaign_budget.explicitly_shared = False

            # Crear presupuesto
            campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id,
                operations=[campaign_budget_operation]
            )
            budget_resource_name = campaign_budget_response.results[0].resource_name

            # Crear campaña
            campaign_service = google_client.get_service("CampaignService")
            campaign_operation = google_client.get_type("CampaignOperation")
            campaign = campaign_operation.create

            campaign.name = campaign_name
            campaign.status = campaign_status
            campaign.campaign_budget = budget_resource_name
            campaign.advertising_channel_type = google_client.enums.AdvertisingChannelTypeEnum.SEARCH

            # Añadir estrategia de puja (requerido por la API)
            # Usar estrategia de puja maximize_conversions (maximizar conversiones)
            # Esta estrategia es más simple y no requiere configuración adicional
            campaign.maximize_conversions = {}

            # Configuración de red
            campaign.network_settings.target_google_search = True
            campaign.network_settings.target_search_network = True
            campaign.network_settings.target_content_network = False
            campaign.network_settings.target_partner_search_network = False

            # Crear campaña
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            campaign_resource_name = campaign_response.results[0].resource_name
            campaign_id = campaign_service.parse_campaign_path(campaign_resource_name)["campaign_id"]

            logger.info(f"Se creó correctamente la campaña '{campaign_name}' con ID: {campaign_id}")

            # Crear grupo de anuncios
            ad_group_service = google_client.get_service("AdGroupService")
            ad_group_operation = google_client.get_type("AdGroupOperation")
            ad_group = ad_group_operation.create

            ad_group.name = f"Ad Group for Campaign {campaign_id}"
            ad_group.campaign = campaign_resource_name
            ad_group.status = google_client.enums.AdGroupStatusEnum.PAUSED

            # Crear grupo de anuncios
            ad_group_response = ad_group_service.mutate_ad_groups(
                customer_id=customer_id,
                operations=[ad_group_operation]
            )
            ad_group_resource_name = ad_group_response.results[0].resource_name
            ad_group_id = ad_group_service.parse_ad_group_path(ad_group_resource_name)["ad_group_id"]

            logger.info(f"Se creó correctamente el grupo de anuncios con ID: {ad_group_id}")

            return {
                'success': True,
                'message': f"Se creó correctamente la campaña '{campaign_name}'",
                'external_ids': {
                    'campaign_id': campaign_id,
                    'ad_group_id': ad_group_id,
                    'budget_id': campaign_budget_service.parse_campaign_budget_path(budget_resource_name)["campaign_budget_id"]
                }
            }

        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear la campaña '{name}': {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'external_ids': None
            }

    @handle_google_ads_api_error
    def publish_campaign(
        self,
        customer_id: str,
        adflux_campaign_id: int,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publica una campaña completa en Google Ads, incluyendo grupo de anuncios y anuncios.

        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            adflux_campaign_id: ID de la campaña en AdFlux.
            campaign_data: Diccionario con los datos de la campaña.
                Claves esperadas: 'name', 'daily_budget' (en centavos),
                'primary_text', 'headline', 'job_id'.

        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'external_ids': None
            }

        try:
            # Extraer datos de la campaña
            name = campaign_data.get('name', 'Campaña sin título')
            daily_budget_cents = campaign_data.get('daily_budget', 1000)  # Valor predeterminado: $10
            primary_text = campaign_data.get('primary_text', '')
            headline = campaign_data.get('headline', '')

            # Convertir presupuesto de centavos a micros (1 dólar = 1,000,000 micros)
            daily_budget_micros = daily_budget_cents * 10000  # centavos * 10000 = micros

            # Crear campaña
            result = self.create_campaign(
                customer_id=customer_id,
                name=name,
                daily_budget_micros=daily_budget_micros,
                adflux_campaign_id=adflux_campaign_id,
                status="PAUSED"
            )

            if not result['success']:
                return result

            # Extraer IDs
            campaign_id = result['external_ids']['campaign_id']
            ad_group_id = result['external_ids']['ad_group_id']

            # TODO: Crear anuncios de texto expandidos
            # Esta funcionalidad se implementará en una versión futura

            return {
                'success': True,
                'message': f"Se publicó correctamente la campaña '{name}'",
                'external_ids': result['external_ids']
            }

        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al publicar la campaña para AdFlux ID {adflux_campaign_id}: {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'external_ids': None
            }


# Crear una instancia del gestor por defecto
_default_manager = None


def get_campaign_manager(client: Optional[GoogleAdsApiClient] = None) -> CampaignManager:
    """
    Obtiene una instancia del gestor de campañas.

    Args:
        client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.

    Returns:
        Una instancia de CampaignManager.
    """
    global _default_manager

    if client:
        return CampaignManager(client)

    if _default_manager is None:
        _default_manager = CampaignManager()

    return _default_manager
