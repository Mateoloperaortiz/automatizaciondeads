"""
Gestión de grupos de anuncios para la API de Google Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
grupos de anuncios en Google Ads.
"""

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
logger = get_logger("GoogleAdsAdGroups")


class AdGroupManager:
    """
    Gestor de grupos de anuncios para la API de Google Ads.
    """
    
    def __init__(self, client: Optional[GoogleAdsApiClient] = None):
        """
        Inicializa el gestor de grupos de anuncios.
        
        Args:
            client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()
    
    @handle_google_ads_api_error
    def get_ad_groups(self, customer_id: str, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene los grupos de anuncios para un cliente específico.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            campaign_id: ID de la campaña para filtrar los grupos de anuncios. Si es None, se obtienen todos.
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'ad_groups': []
            }
        
        try:
            # Crear servicio de GoogleAdsService
            google_ads_service = google_client.get_service("GoogleAdsService")
            
            # Crear consulta para obtener grupos de anuncios
            query = """
                SELECT
                  ad_group.id,
                  ad_group.name,
                  ad_group.status,
                  ad_group.type,
                  ad_group.campaign,
                  campaign.id,
                  campaign.name
                FROM ad_group
            """
            
            # Añadir filtro por campaña si se proporciona
            if campaign_id:
                query += f" WHERE campaign.id = {campaign_id}"
            
            query += " ORDER BY ad_group.id"
            
            # Ejecutar consulta
            response = google_ads_service.search(customer_id=customer_id, query=query)
            
            # Procesar resultados
            ad_groups = []
            for row in response:
                ad_group = row.ad_group
                campaign = row.campaign
                
                ad_group_data = {
                    'id': ad_group.id,
                    'name': ad_group.name,
                    'status': ad_group.status.name,
                    'type': ad_group.type_.name if hasattr(ad_group, 'type_') else None,
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name
                }
                ad_groups.append(ad_group_data)
            
            logger.info(f"Se recuperaron {len(ad_groups)} grupos de anuncios para el cliente {customer_id}.")
            return {
                'success': True,
                'message': f"Se recuperaron {len(ad_groups)} grupos de anuncios.",
                'ad_groups': ad_groups
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al obtener grupos de anuncios para el cliente {customer_id}: {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'ad_groups': []
            }
    
    @handle_google_ads_api_error
    def create_ad_group(
        self,
        customer_id: str,
        campaign_id: str,
        name: str,
        status: str = "PAUSED"
    ) -> Dict[str, Any]:
        """
        Crea un nuevo grupo de anuncios en Google Ads.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            campaign_id: ID de la campaña a la que pertenecerá el grupo de anuncios.
            name: Nombre para el nuevo grupo de anuncios.
            status: Estado inicial ('ENABLED', 'PAUSED', 'REMOVED'). Por defecto 'PAUSED'.
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'ad_group_id': None
            }
        
        try:
            # Convertir estado a enum
            ad_group_status = getattr(google_client.enums.AdGroupStatusEnum, status)
            
            # Obtener el resource name de la campaña
            campaign_service = google_client.get_service("CampaignService")
            campaign_resource_name = campaign_service.campaign_path(customer_id, campaign_id)
            
            # Crear grupo de anuncios
            ad_group_service = google_client.get_service("AdGroupService")
            ad_group_operation = google_client.get_type("AdGroupOperation")
            ad_group = ad_group_operation.create
            
            ad_group.name = name
            ad_group.campaign = campaign_resource_name
            ad_group.status = ad_group_status
            
            # Crear grupo de anuncios
            ad_group_response = ad_group_service.mutate_ad_groups(
                customer_id=customer_id,
                operations=[ad_group_operation]
            )
            ad_group_resource_name = ad_group_response.results[0].resource_name
            ad_group_id = ad_group_service.parse_ad_group_path(ad_group_resource_name)["ad_group_id"]
            
            logger.info(f"Se creó correctamente el grupo de anuncios '{name}' con ID: {ad_group_id}")
            
            return {
                'success': True,
                'message': f"Se creó correctamente el grupo de anuncios '{name}'",
                'ad_group_id': ad_group_id
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear el grupo de anuncios '{name}': {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'ad_group_id': None
            }


# Crear una instancia del gestor por defecto
_default_manager = None


def get_ad_group_manager(client: Optional[GoogleAdsApiClient] = None) -> AdGroupManager:
    """
    Obtiene una instancia del gestor de grupos de anuncios.
    
    Args:
        client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        
    Returns:
        Una instancia de AdGroupManager.
    """
    global _default_manager
    
    if client:
        return AdGroupManager(client)
    
    if _default_manager is None:
        _default_manager = AdGroupManager()
    
    return _default_manager
