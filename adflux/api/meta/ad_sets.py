"""
Gestión de conjuntos de anuncios para la API de Meta (Facebook/Instagram) Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
conjuntos de anuncios en Meta Ads.
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
logger = get_logger("MetaAdSets")


class AdSetManager:
    """
    Gestor de conjuntos de anuncios para la API de Meta Ads.
    """
    
    def __init__(self, client: Optional[MetaApiClient] = None):
        """
        Inicializa el gestor de conjuntos de anuncios.
        
        Args:
            client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()
    
    @handle_meta_api_error
    def get_ad_sets(self, campaign_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Obtiene los conjuntos de anuncios para una campaña específica.
        
        Args:
            campaign_id: ID de la campaña.
            
        Returns:
            Una tupla con: (éxito, mensaje, lista de conjuntos de anuncios).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", []
        
        try:
            from facebook_business.adobjects.campaign import Campaign
            from facebook_business.adobjects.adset import AdSet
            
            # Definir los campos que queremos recuperar
            fields = [
                AdSet.Field.id,
                AdSet.Field.name,
                AdSet.Field.status,
                AdSet.Field.daily_budget,
                AdSet.Field.lifetime_budget,
                AdSet.Field.optimization_goal,
                AdSet.Field.billing_event,
                AdSet.Field.bid_amount,
                AdSet.Field.targeting,
                AdSet.Field.promoted_object,
                AdSet.Field.created_time,
                AdSet.Field.updated_time,
                AdSet.Field.effective_status
            ]
            
            campaign = Campaign(campaign_id)
            ad_sets = campaign.get_ad_sets(fields=fields)
            
            # Procesar los resultados para un formato más amigable
            ad_sets_list = []
            for ad_set in ad_sets:
                ad_set_data = {
                    'id': ad_set.get(AdSet.Field.id),
                    'name': ad_set.get(AdSet.Field.name),
                    'status': ad_set.get(AdSet.Field.status),
                    'daily_budget': ad_set.get(AdSet.Field.daily_budget),
                    'lifetime_budget': ad_set.get(AdSet.Field.lifetime_budget),
                    'optimization_goal': ad_set.get(AdSet.Field.optimization_goal),
                    'billing_event': ad_set.get(AdSet.Field.billing_event),
                    'bid_amount': ad_set.get(AdSet.Field.bid_amount),
                    'targeting': ad_set.get(AdSet.Field.targeting),
                    'promoted_object': ad_set.get(AdSet.Field.promoted_object),
                    'created_time': ad_set.get(AdSet.Field.created_time),
                    'updated_time': ad_set.get(AdSet.Field.updated_time),
                    'effective_status': ad_set.get(AdSet.Field.effective_status)
                }
                ad_sets_list.append(ad_set_data)
            
            logger.info(f"Se recuperaron {len(ad_sets_list)} conjuntos de anuncios para la campaña {campaign_id}.")
            return True, f"Se recuperaron {len(ad_sets_list)} conjuntos de anuncios.", ad_sets_list
            
        except FacebookRequestError as e:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            return False, f"Error al importar el objeto del SDK de Facebook: {e}", []
    
    @handle_meta_api_error
    def create_ad_set(
        self,
        ad_account_id: str,
        campaign_id: str,
        name: str,
        optimization_goal: str,
        billing_event: str,
        daily_budget_cents: int,
        targeting_spec: Dict[str, Any],
        status: str = 'PAUSED',
        bid_amount: Optional[int] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Crea un nuevo conjunto de anuncios en la cuenta publicitaria especificada.
        
        Args:
            ad_account_id: ID de la cuenta publicitaria (ej., 'act_123456789').
            campaign_id: ID de la campaña a la que pertenecerá el conjunto de anuncios.
            name: Nombre para el nuevo conjunto de anuncios.
            optimization_goal: Objetivo de optimización (ej., 'LINK_CLICKS', 'CONVERSIONS').
            billing_event: Evento de facturación (ej., 'IMPRESSIONS', 'LINK_CLICKS').
            daily_budget_cents: Presupuesto diario en centavos.
            targeting_spec: Especificación de segmentación.
            status: Estado inicial ('ACTIVE' o 'PAUSED'). Por defecto 'PAUSED'.
            bid_amount: Monto de puja en centavos. Opcional.
            
        Returns:
            Una tupla con: (éxito, mensaje, datos del conjunto de anuncios creado).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", {}
        
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adset import AdSet
            
            account = AdAccount(ad_account_id)
            
            # Preparar los parámetros para la creación del conjunto de anuncios
            params = {
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.name: name,
                AdSet.Field.optimization_goal: optimization_goal,
                AdSet.Field.billing_event: billing_event,
                AdSet.Field.daily_budget: daily_budget_cents,
                AdSet.Field.targeting: targeting_spec,
                AdSet.Field.status: status,
            }
            
            # Añadir bid_amount si se proporciona
            if bid_amount is not None:
                params[AdSet.Field.bid_amount] = bid_amount
            
            # Crear el conjunto de anuncios
            ad_set = account.create_ad_set(params=params)
            ad_set_id = ad_set.get(AdSet.Field.id)
            
            logger.info(f"Se creó correctamente el conjunto de anuncios '{name}' con ID: {ad_set_id}")
            
            return True, f"Se creó correctamente el conjunto de anuncios '{name}'", {
                'id': ad_set_id,
                'name': name,
                'campaign_id': campaign_id,
                'optimization_goal': optimization_goal,
                'billing_event': billing_event,
                'daily_budget': daily_budget_cents,
                'status': status
            }
            
        except FacebookRequestError as e:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            return False, f"Error al importar el objeto del SDK de Facebook: {e}", {}
        except Exception as e:
            logger.error(f"Error inesperado al crear el conjunto de anuncios Meta '{name}': {e}", e)
            return False, f"Error inesperado al crear el conjunto de anuncios: {e}", {}


# Crear una instancia del gestor por defecto
_default_manager = None


def get_ad_set_manager(client: Optional[MetaApiClient] = None) -> AdSetManager:
    """
    Obtiene una instancia del gestor de conjuntos de anuncios.
    
    Args:
        client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        
    Returns:
        Una instancia de AdSetManager.
    """
    global _default_manager
    
    if client:
        return AdSetManager(client)
    
    if _default_manager is None:
        _default_manager = AdSetManager()
    
    return _default_manager
