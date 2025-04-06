"""
Gestión de palabras clave para la API de Google Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
palabras clave en Google Ads.
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
logger = get_logger("GoogleAdsKeywords")


class KeywordManager:
    """
    Gestor de palabras clave para la API de Google Ads.
    """
    
    def __init__(self, client: Optional[GoogleAdsApiClient] = None):
        """
        Inicializa el gestor de palabras clave.
        
        Args:
            client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()
    
    @handle_google_ads_api_error
    def get_keywords(self, customer_id: str, ad_group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene las palabras clave para un cliente específico.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            ad_group_id: ID del grupo de anuncios para filtrar las palabras clave. Si es None, se obtienen todas.
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'keywords': []
            }
        
        try:
            # Crear servicio de GoogleAdsService
            google_ads_service = google_client.get_service("GoogleAdsService")
            
            # Crear consulta para obtener palabras clave
            query = """
                SELECT
                  ad_group_criterion.criterion_id,
                  ad_group_criterion.keyword.text,
                  ad_group_criterion.keyword.match_type,
                  ad_group_criterion.status,
                  ad_group_criterion.ad_group,
                  ad_group.id,
                  ad_group.name,
                  ad_group_criterion.quality_info.quality_score
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = 'KEYWORD'
            """
            
            # Añadir filtro por grupo de anuncios si se proporciona
            if ad_group_id:
                query += f" AND ad_group.id = {ad_group_id}"
            
            query += " ORDER BY ad_group_criterion.keyword.text"
            
            # Ejecutar consulta
            response = google_ads_service.search(customer_id=customer_id, query=query)
            
            # Procesar resultados
            keywords = []
            for row in response:
                ad_group_criterion = row.ad_group_criterion
                ad_group = row.ad_group
                keyword = ad_group_criterion.keyword
                quality_info = ad_group_criterion.quality_info
                
                keyword_data = {
                    'id': ad_group_criterion.criterion_id,
                    'text': keyword.text,
                    'match_type': keyword.match_type.name,
                    'status': ad_group_criterion.status.name,
                    'ad_group_id': ad_group.id,
                    'ad_group_name': ad_group.name,
                    'quality_score': quality_info.quality_score if hasattr(quality_info, 'quality_score') else None
                }
                keywords.append(keyword_data)
            
            logger.info(f"Se recuperaron {len(keywords)} palabras clave para el cliente {customer_id}.")
            return {
                'success': True,
                'message': f"Se recuperaron {len(keywords)} palabras clave.",
                'keywords': keywords
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al obtener palabras clave para el cliente {customer_id}: {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'keywords': []
            }
    
    @handle_google_ads_api_error
    def create_keyword(
        self,
        customer_id: str,
        ad_group_id: str,
        keyword_text: str,
        match_type: str = "EXACT",
        status: str = "PAUSED",
        bid_micros: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva palabra clave en Google Ads.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            ad_group_id: ID del grupo de anuncios al que pertenecerá la palabra clave.
            keyword_text: Texto de la palabra clave.
            match_type: Tipo de coincidencia ('EXACT', 'PHRASE', 'BROAD'). Por defecto 'EXACT'.
            status: Estado inicial ('ENABLED', 'PAUSED', 'REMOVED'). Por defecto 'PAUSED'.
            bid_micros: Puja en micros (1 dólar = 1,000,000 micros). Si es None, se usa la puja predeterminada.
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'keyword_id': None
            }
        
        try:
            # Convertir match_type y status a enums
            keyword_match_type = getattr(google_client.enums.KeywordMatchTypeEnum, match_type)
            criterion_status = getattr(google_client.enums.AdGroupCriterionStatusEnum, status)
            
            # Obtener el resource name del grupo de anuncios
            ad_group_service = google_client.get_service("AdGroupService")
            ad_group_resource_name = ad_group_service.ad_group_path(customer_id, ad_group_id)
            
            # Crear palabra clave
            ad_group_criterion_service = google_client.get_service("AdGroupCriterionService")
            ad_group_criterion_operation = google_client.get_type("AdGroupCriterionOperation")
            ad_group_criterion = ad_group_criterion_operation.create
            
            # Configurar el grupo de anuncios
            ad_group_criterion.ad_group = ad_group_resource_name
            ad_group_criterion.status = criterion_status
            
            # Configurar la palabra clave
            ad_group_criterion.keyword.text = keyword_text
            ad_group_criterion.keyword.match_type = keyword_match_type
            
            # Configurar la puja si se proporciona
            if bid_micros is not None:
                ad_group_criterion.cpc_bid_micros = bid_micros
            
            # Crear palabra clave
            ad_group_criterion_response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=customer_id,
                operations=[ad_group_criterion_operation]
            )
            ad_group_criterion_resource_name = ad_group_criterion_response.results[0].resource_name
            
            # Extraer el ID de la palabra clave
            criterion_id = ad_group_criterion_service.parse_ad_group_criterion_path(ad_group_criterion_resource_name)["criterion_id"]
            
            logger.info(f"Se creó correctamente la palabra clave '{keyword_text}' con ID: {criterion_id}")
            
            return {
                'success': True,
                'message': f"Se creó correctamente la palabra clave '{keyword_text}'",
                'keyword_id': criterion_id
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear la palabra clave '{keyword_text}': {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'keyword_id': None
            }
    
    @handle_google_ads_api_error
    def create_keywords_batch(
        self,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Crea múltiples palabras clave en un solo lote.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            ad_group_id: ID del grupo de anuncios al que pertenecerán las palabras clave.
            keywords: Lista de diccionarios con información de palabras clave.
                Cada diccionario debe tener las siguientes claves:
                - 'text': Texto de la palabra clave.
                - 'match_type': Tipo de coincidencia ('EXACT', 'PHRASE', 'BROAD'). Opcional, por defecto 'EXACT'.
                - 'status': Estado inicial ('ENABLED', 'PAUSED', 'REMOVED'). Opcional, por defecto 'PAUSED'.
                - 'bid_micros': Puja en micros. Opcional.
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'keyword_ids': []
            }
        
        try:
            # Obtener el resource name del grupo de anuncios
            ad_group_service = google_client.get_service("AdGroupService")
            ad_group_resource_name = ad_group_service.ad_group_path(customer_id, ad_group_id)
            
            # Crear servicio de AdGroupCriterionService
            ad_group_criterion_service = google_client.get_service("AdGroupCriterionService")
            
            # Crear operaciones para cada palabra clave
            operations = []
            for keyword_data in keywords:
                # Extraer datos de la palabra clave
                keyword_text = keyword_data['text']
                match_type = keyword_data.get('match_type', 'EXACT')
                status = keyword_data.get('status', 'PAUSED')
                bid_micros = keyword_data.get('bid_micros')
                
                # Convertir match_type y status a enums
                keyword_match_type = getattr(google_client.enums.KeywordMatchTypeEnum, match_type)
                criterion_status = getattr(google_client.enums.AdGroupCriterionStatusEnum, status)
                
                # Crear operación
                ad_group_criterion_operation = google_client.get_type("AdGroupCriterionOperation")
                ad_group_criterion = ad_group_criterion_operation.create
                
                # Configurar el grupo de anuncios
                ad_group_criterion.ad_group = ad_group_resource_name
                ad_group_criterion.status = criterion_status
                
                # Configurar la palabra clave
                ad_group_criterion.keyword.text = keyword_text
                ad_group_criterion.keyword.match_type = keyword_match_type
                
                # Configurar la puja si se proporciona
                if bid_micros is not None:
                    ad_group_criterion.cpc_bid_micros = bid_micros
                
                operations.append(ad_group_criterion_operation)
            
            # Crear palabras clave en lote
            ad_group_criterion_response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=customer_id,
                operations=operations
            )
            
            # Extraer los IDs de las palabras clave
            keyword_ids = []
            for result in ad_group_criterion_response.results:
                criterion_id = ad_group_criterion_service.parse_ad_group_criterion_path(result.resource_name)["criterion_id"]
                keyword_ids.append(criterion_id)
            
            logger.info(f"Se crearon correctamente {len(keyword_ids)} palabras clave.")
            
            return {
                'success': True,
                'message': f"Se crearon correctamente {len(keyword_ids)} palabras clave.",
                'keyword_ids': keyword_ids
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear palabras clave en lote: {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'keyword_ids': []
            }


# Crear una instancia del gestor por defecto
_default_manager = None


def get_keyword_manager(client: Optional[GoogleAdsApiClient] = None) -> KeywordManager:
    """
    Obtiene una instancia del gestor de palabras clave.
    
    Args:
        client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        
    Returns:
        Una instancia de KeywordManager.
    """
    global _default_manager
    
    if client:
        return KeywordManager(client)
    
    if _default_manager is None:
        _default_manager = KeywordManager()
    
    return _default_manager
