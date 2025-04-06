"""
Gestión de targeting para la API de Google Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
opciones de targeting en Google Ads, como ubicaciones geográficas, demografía, etc.
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
logger = get_logger("GoogleAdsTargeting")


class TargetingManager:
    """
    Gestor de targeting para la API de Google Ads.
    """
    
    def __init__(self, client: Optional[GoogleAdsApiClient] = None):
        """
        Inicializa el gestor de targeting.
        
        Args:
            client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()
    
    @handle_google_ads_api_error
    def get_location_criteria(self, customer_id: str, query: str) -> Dict[str, Any]:
        """
        Busca criterios de ubicación geográfica.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            query: Consulta para buscar ubicaciones (ej., 'Colombia', 'Bogotá').
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'locations': []
            }
        
        try:
            # Crear servicio de LocationCriterionService
            location_criterion_service = google_client.get_service("GoogleAdsService")
            
            # Crear consulta para buscar ubicaciones
            search_query = f"""
                SELECT
                  geo_target_constant.resource_name,
                  geo_target_constant.id,
                  geo_target_constant.name,
                  geo_target_constant.country_code,
                  geo_target_constant.target_type,
                  geo_target_constant.status
                FROM geo_target_constant
                WHERE geo_target_constant.name LIKE '%{query}%'
                ORDER BY geo_target_constant.name
                LIMIT 50
            """
            
            # Ejecutar consulta
            response = location_criterion_service.search(customer_id=customer_id, query=search_query)
            
            # Procesar resultados
            locations = []
            for row in response:
                geo_target_constant = row.geo_target_constant
                
                location_data = {
                    'id': geo_target_constant.id,
                    'name': geo_target_constant.name,
                    'country_code': geo_target_constant.country_code,
                    'target_type': geo_target_constant.target_type.name,
                    'status': geo_target_constant.status.name,
                    'resource_name': geo_target_constant.resource_name
                }
                locations.append(location_data)
            
            logger.info(f"Se encontraron {len(locations)} ubicaciones para la consulta '{query}'.")
            return {
                'success': True,
                'message': f"Se encontraron {len(locations)} ubicaciones.",
                'locations': locations
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al buscar ubicaciones para la consulta '{query}': {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'locations': []
            }
    
    @handle_google_ads_api_error
    def add_campaign_targeting_criteria(
        self,
        customer_id: str,
        campaign_id: str,
        location_ids: Optional[List[str]] = None,
        language_ids: Optional[List[str]] = None,
        gender: Optional[str] = None,
        age_ranges: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Añade criterios de targeting a una campaña.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            campaign_id: ID de la campaña a la que se añadirán los criterios.
            location_ids: Lista de IDs de ubicaciones geográficas.
            language_ids: Lista de IDs de idiomas.
            gender: Género ('MALE', 'FEMALE', 'UNDETERMINED').
            age_ranges: Lista de rangos de edad ('AGE_RANGE_18_24', 'AGE_RANGE_25_34', etc.).
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'criteria_ids': []
            }
        
        try:
            # Obtener el resource name de la campaña
            campaign_service = google_client.get_service("CampaignService")
            campaign_resource_name = campaign_service.campaign_path(customer_id, campaign_id)
            
            # Crear servicio de CampaignCriterionService
            campaign_criterion_service = google_client.get_service("CampaignCriterionService")
            
            # Crear operaciones para cada criterio
            operations = []
            
            # Añadir ubicaciones geográficas
            if location_ids:
                for location_id in location_ids:
                    campaign_criterion_operation = google_client.get_type("CampaignCriterionOperation")
                    campaign_criterion = campaign_criterion_operation.create
                    campaign_criterion.campaign = campaign_resource_name
                    campaign_criterion.location.geo_target_constant = f"geoTargetConstants/{location_id}"
                    operations.append(campaign_criterion_operation)
            
            # Añadir idiomas
            if language_ids:
                for language_id in language_ids:
                    campaign_criterion_operation = google_client.get_type("CampaignCriterionOperation")
                    campaign_criterion = campaign_criterion_operation.create
                    campaign_criterion.campaign = campaign_resource_name
                    campaign_criterion.language.language_constant = f"languageConstants/{language_id}"
                    operations.append(campaign_criterion_operation)
            
            # Añadir género
            if gender:
                campaign_criterion_operation = google_client.get_type("CampaignCriterionOperation")
                campaign_criterion = campaign_criterion_operation.create
                campaign_criterion.campaign = campaign_resource_name
                campaign_criterion.gender.type_ = getattr(google_client.enums.GenderTypeEnum, gender)
                operations.append(campaign_criterion_operation)
            
            # Añadir rangos de edad
            if age_ranges:
                for age_range in age_ranges:
                    campaign_criterion_operation = google_client.get_type("CampaignCriterionOperation")
                    campaign_criterion = campaign_criterion_operation.create
                    campaign_criterion.campaign = campaign_resource_name
                    campaign_criterion.age_range.type_ = getattr(google_client.enums.AgeRangeTypeEnum, age_range)
                    operations.append(campaign_criterion_operation)
            
            # Si no hay operaciones, devolver éxito pero sin criterios
            if not operations:
                return {
                    'success': True,
                    'message': "No se proporcionaron criterios de targeting para añadir.",
                    'criteria_ids': []
                }
            
            # Añadir criterios en lote
            campaign_criterion_response = campaign_criterion_service.mutate_campaign_criteria(
                customer_id=customer_id,
                operations=operations
            )
            
            # Extraer los IDs de los criterios
            criteria_ids = []
            for result in campaign_criterion_response.results:
                criterion_id = campaign_criterion_service.parse_campaign_criterion_path(result.resource_name)["criterion_id"]
                criteria_ids.append(criterion_id)
            
            logger.info(f"Se añadieron correctamente {len(criteria_ids)} criterios de targeting a la campaña {campaign_id}.")
            
            return {
                'success': True,
                'message': f"Se añadieron correctamente {len(criteria_ids)} criterios de targeting.",
                'criteria_ids': criteria_ids
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al añadir criterios de targeting a la campaña {campaign_id}: {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'criteria_ids': []
            }
    
    @handle_google_ads_api_error
    def get_campaign_targeting_criteria(self, customer_id: str, campaign_id: str) -> Dict[str, Any]:
        """
        Obtiene los criterios de targeting de una campaña.
        
        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            campaign_id: ID de la campaña.
            
        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                'success': False,
                'message': "No se pudo inicializar el cliente de Google Ads",
                'criteria': {
                    'locations': [],
                    'languages': [],
                    'genders': [],
                    'age_ranges': []
                }
            }
        
        try:
            # Crear servicio de GoogleAdsService
            google_ads_service = google_client.get_service("GoogleAdsService")
            
            # Crear consulta para obtener criterios de targeting
            query = f"""
                SELECT
                  campaign_criterion.criterion_id,
                  campaign_criterion.type,
                  campaign_criterion.location.geo_target_constant,
                  campaign_criterion.language.language_constant,
                  campaign_criterion.gender.type,
                  campaign_criterion.age_range.type
                FROM campaign_criterion
                WHERE campaign.id = {campaign_id}
            """
            
            # Ejecutar consulta
            response = google_ads_service.search(customer_id=customer_id, query=query)
            
            # Procesar resultados
            locations = []
            languages = []
            genders = []
            age_ranges = []
            
            for row in response:
                campaign_criterion = row.campaign_criterion
                criterion_type = campaign_criterion.type_.name
                
                if criterion_type == 'LOCATION':
                    location_resource_name = campaign_criterion.location.geo_target_constant
                    location_id = location_resource_name.split('/')[-1]
                    locations.append({
                        'id': location_id,
                        'resource_name': location_resource_name
                    })
                elif criterion_type == 'LANGUAGE':
                    language_resource_name = campaign_criterion.language.language_constant
                    language_id = language_resource_name.split('/')[-1]
                    languages.append({
                        'id': language_id,
                        'resource_name': language_resource_name
                    })
                elif criterion_type == 'GENDER':
                    gender_type = campaign_criterion.gender.type_.name
                    genders.append({
                        'type': gender_type
                    })
                elif criterion_type == 'AGE_RANGE':
                    age_range_type = campaign_criterion.age_range.type_.name
                    age_ranges.append({
                        'type': age_range_type
                    })
            
            logger.info(f"Se recuperaron los criterios de targeting para la campaña {campaign_id}.")
            return {
                'success': True,
                'message': "Se recuperaron los criterios de targeting.",
                'criteria': {
                    'locations': locations,
                    'languages': languages,
                    'genders': genders,
                    'age_ranges': age_ranges
                }
            }
            
        except GoogleAdsException as e:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al obtener criterios de targeting para la campaña {campaign_id}: {e}", e)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}",
                'criteria': {
                    'locations': [],
                    'languages': [],
                    'genders': [],
                    'age_ranges': []
                }
            }


# Crear una instancia del gestor por defecto
_default_manager = None


def get_targeting_manager(client: Optional[GoogleAdsApiClient] = None) -> TargetingManager:
    """
    Obtiene una instancia del gestor de targeting.
    
    Args:
        client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        
    Returns:
        Una instancia de TargetingManager.
    """
    global _default_manager
    
    if client:
        return TargetingManager(client)
    
    if _default_manager is None:
        _default_manager = TargetingManager()
    
    return _default_manager
