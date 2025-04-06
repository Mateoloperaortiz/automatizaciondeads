"""
Gestión de anuncios para la API de Google Ads.

Este módulo proporciona funcionalidades para crear, obtener y gestionar
anuncios en Google Ads.
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
logger = get_logger("GoogleAdsAds")


class AdManager:
    """
    Gestor de anuncios para la API de Google Ads.
    """

    def __init__(self, client: Optional[GoogleAdsApiClient] = None):
        """
        Inicializa el gestor de anuncios.

        Args:
            client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()

    @handle_google_ads_api_error
    def get_ads(self, customer_id: str, ad_group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene los anuncios para un cliente específico.

        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            ad_group_id: ID del grupo de anuncios para filtrar los anuncios. Si es None, se obtienen todos.

        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                "success": False,
                "message": "No se pudo inicializar el cliente de Google Ads",
                "ads": [],
            }

        try:
            # Crear servicio de GoogleAdsService
            google_ads_service = google_client.get_service("GoogleAdsService")

            # Crear consulta para obtener anuncios
            query = """
                SELECT
                  ad_group_ad.ad.id,
                  ad_group_ad.ad.name,
                  ad_group_ad.ad.type,
                  ad_group_ad.ad.final_urls,
                  ad_group_ad.status,
                  ad_group_ad.ad_group,
                  ad_group.id,
                  ad_group.name,
                  ad_group_ad.ad.text_ad.headline,
                  ad_group_ad.ad.text_ad.description1,
                  ad_group_ad.ad.text_ad.description2,
                  ad_group_ad.ad.expanded_text_ad.headline_part1,
                  ad_group_ad.ad.expanded_text_ad.headline_part2,
                  ad_group_ad.ad.expanded_text_ad.headline_part3,
                  ad_group_ad.ad.expanded_text_ad.description,
                  ad_group_ad.ad.expanded_text_ad.description2
                FROM ad_group_ad
            """

            # Añadir filtro por grupo de anuncios si se proporciona
            if ad_group_id:
                query += f" WHERE ad_group.id = {ad_group_id}"

            query += " ORDER BY ad_group_ad.ad.id"

            # Ejecutar consulta
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Procesar resultados
            ads = []
            for row in response:
                ad_group_ad = row.ad_group_ad
                ad = ad_group_ad.ad
                ad_group = row.ad_group

                # Determinar el tipo de anuncio y extraer los datos relevantes
                ad_type = ad.type_.name if hasattr(ad, "type_") else None
                ad_details = {}

                if ad_type == "TEXT_AD" and hasattr(ad, "text_ad"):
                    text_ad = ad.text_ad
                    ad_details = {
                        "headline": text_ad.headline if hasattr(text_ad, "headline") else None,
                        "description1": (
                            text_ad.description1 if hasattr(text_ad, "description1") else None
                        ),
                        "description2": (
                            text_ad.description2 if hasattr(text_ad, "description2") else None
                        ),
                    }
                elif ad_type == "EXPANDED_TEXT_AD" and hasattr(ad, "expanded_text_ad"):
                    expanded_text_ad = ad.expanded_text_ad
                    ad_details = {
                        "headline_part1": (
                            expanded_text_ad.headline_part1
                            if hasattr(expanded_text_ad, "headline_part1")
                            else None
                        ),
                        "headline_part2": (
                            expanded_text_ad.headline_part2
                            if hasattr(expanded_text_ad, "headline_part2")
                            else None
                        ),
                        "headline_part3": (
                            expanded_text_ad.headline_part3
                            if hasattr(expanded_text_ad, "headline_part3")
                            else None
                        ),
                        "description": (
                            expanded_text_ad.description
                            if hasattr(expanded_text_ad, "description")
                            else None
                        ),
                        "description2": (
                            expanded_text_ad.description2
                            if hasattr(expanded_text_ad, "description2")
                            else None
                        ),
                    }

                # Construir el objeto de anuncio
                ad_data = {
                    "id": ad.id,
                    "name": ad.name,
                    "type": ad_type,
                    "status": ad_group_ad.status.name,
                    "ad_group_id": ad_group.id,
                    "ad_group_name": ad_group.name,
                    "final_urls": list(ad.final_urls) if hasattr(ad, "final_urls") else [],
                    "details": ad_details,
                }
                ads.append(ad_data)

            logger.info(f"Se recuperaron {len(ads)} anuncios para el cliente {customer_id}.")
            return {"success": True, "message": f"Se recuperaron {len(ads)} anuncios.", "ads": ads}

        except GoogleAdsException:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(
                f"Error inesperado al obtener anuncios para el cliente {customer_id}: {e}", e
            )
            return {"success": False, "message": f"Error inesperado: {str(e)}", "ads": []}

    @handle_google_ads_api_error
    def create_responsive_search_ad(
        self,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_url: str,
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """
        Crea un nuevo anuncio de búsqueda responsivo en Google Ads.

        Args:
            customer_id: ID del cliente de Google Ads (sin guiones).
            ad_group_id: ID del grupo de anuncios al que pertenecerá el anuncio.
            headlines: Lista de titulares para el anuncio (mínimo 3, máximo 15).
            descriptions: Lista de descripciones para el anuncio (mínimo 2, máximo 4).
            final_url: URL final a la que se dirigirá el anuncio.
            status: Estado inicial ('ENABLED', 'PAUSED', 'REMOVED'). Por defecto 'PAUSED'.

        Returns:
            Un diccionario con el resultado de la operación.
        """
        google_client = self.client.get_client()
        if not google_client:
            return {
                "success": False,
                "message": "No se pudo inicializar el cliente de Google Ads",
                "ad_id": None,
            }

        try:
            # Validar entradas
            if len(headlines) < 3:
                return {
                    "success": False,
                    "message": "Se requieren al menos 3 titulares para un anuncio de búsqueda responsivo.",
                    "ad_id": None,
                }

            if len(descriptions) < 2:
                return {
                    "success": False,
                    "message": "Se requieren al menos 2 descripciones para un anuncio de búsqueda responsivo.",
                    "ad_id": None,
                }

            # Convertir estado a enum
            ad_group_ad_status = getattr(google_client.enums.AdGroupAdStatusEnum, status)

            # Obtener el resource name del grupo de anuncios
            ad_group_service = google_client.get_service("AdGroupService")
            ad_group_resource_name = ad_group_service.ad_group_path(customer_id, ad_group_id)

            # Crear anuncio
            ad_group_ad_service = google_client.get_service("AdGroupAdService")
            ad_group_ad_operation = google_client.get_type("AdGroupAdOperation")
            ad_group_ad = ad_group_ad_operation.create

            # Configurar el grupo de anuncios
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.status = ad_group_ad_status

            # Configurar el anuncio responsivo de búsqueda
            ad = ad_group_ad.ad
            ad.final_urls.append(final_url)

            # Añadir titulares
            for headline in headlines[:15]:  # Máximo 15 titulares
                asset = ad.responsive_search_ad.headlines.add()
                asset.text = headline

            # Añadir descripciones
            for description in descriptions[:4]:  # Máximo 4 descripciones
                asset = ad.responsive_search_ad.descriptions.add()
                asset.text = description

            # Crear anuncio
            ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=customer_id, operations=[ad_group_ad_operation]
            )
            ad_group_ad_resource_name = ad_group_ad_response.results[0].resource_name

            # Extraer el ID del anuncio
            ad_id = ad_group_ad_service.parse_ad_group_ad_path(ad_group_ad_resource_name)["ad_id"]

            logger.info(f"Se creó correctamente el anuncio responsivo de búsqueda con ID: {ad_id}")

            return {
                "success": True,
                "message": "Se creó correctamente el anuncio responsivo de búsqueda",
                "ad_id": ad_id,
            }

        except GoogleAdsException:
            # Este error ya será manejado por el decorador handle_google_ads_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear el anuncio responsivo de búsqueda: {e}", e)
            return {"success": False, "message": f"Error inesperado: {str(e)}", "ad_id": None}


# Crear una instancia del gestor por defecto
_default_manager = None


def get_ad_manager(client: Optional[GoogleAdsApiClient] = None) -> AdManager:
    """
    Obtiene una instancia del gestor de anuncios.

    Args:
        client: Cliente de la API de Google Ads. Si es None, se usa el cliente por defecto.

    Returns:
        Una instancia de AdManager.
    """
    global _default_manager

    if client:
        return AdManager(client)

    if _default_manager is None:
        _default_manager = AdManager()

    return _default_manager
