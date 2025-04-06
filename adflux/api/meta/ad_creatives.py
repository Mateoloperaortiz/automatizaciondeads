"""
Módulo para gestionar creativos de anuncios en Meta Ads API.

Este módulo proporciona funciones para crear y gestionar creativos de anuncios
en la plataforma Meta Ads.
"""

import logging
from typing import Dict, Any, Tuple, Optional, List

from facebook_business.exceptions import FacebookRequestError

from .client import MetaApiClient, get_client
from ..common.error_handling import handle_meta_api_error

logger = logging.getLogger(__name__)


class AdCreativeManager:
    """
    Gestor para operaciones con creativos de anuncios en Meta Ads.
    """

    def __init__(self, client: Optional[MetaApiClient] = None):
        """
        Inicializa el gestor de creativos de anuncios.

        Args:
            client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()

    @handle_meta_api_error
    def create_ad_creative(
        self,
        ad_account_id: str,
        name: str,
        page_id: str,
        message: str,
        link: str,
        link_title: str,
        link_description: str,
        image_hash: Optional[str] = None,
        call_to_action_type: str = 'APPLY_NOW'
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Crea un nuevo creativo de anuncio en la cuenta publicitaria especificada.

        Args:
            ad_account_id: ID de la cuenta publicitaria (ej., 'act_123456789').
            name: Nombre para el nuevo creativo.
            page_id: ID de la página de Facebook que publicará el anuncio.
            message: Texto principal del anuncio.
            link: URL de destino del anuncio.
            link_title: Título del enlace.
            link_description: Descripción del enlace.
            image_hash: Hash de la imagen a usar (opcional).
            call_to_action_type: Tipo de llamada a la acción (por defecto 'APPLY_NOW').

        Returns:
            Una tupla con: (éxito, mensaje, datos del creativo creado).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", {}

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adcreative import AdCreative

            account = AdAccount(ad_account_id)

            # Preparar los parámetros para la creación del creativo
            # Usar un enfoque más simple para evitar problemas con imágenes
            logger.info(f"Creando anuncio simple para '{name}'")

            # Crear un anuncio simple con solo los campos requeridos
            params = {
                'name': name,
                'object_story_spec': {
                    'page_id': page_id,
                    'link_data': {
                        'message': message,
                        'link': link,
                        'call_to_action': {
                            'type': call_to_action_type,
                            'value': {
                                'link': link
                            }
                        }
                    }
                }
            }

            # Si tenemos un hash de imagen, añadirlo
            if image_hash:
                params['object_story_spec']['link_data']['image_hash'] = image_hash

            # Crear el creativo
            creative = account.create_ad_creative(params=params)
            creative_id = creative.get(AdCreative.Field.id)

            logger.info(f"Se creó correctamente el creativo de anuncio '{name}' con ID: {creative_id}")

            return True, f"Se creó correctamente el creativo de anuncio '{name}'", {
                'id': creative_id,
                'name': name,
                'page_id': page_id,
                'message': message,
                'link': link,
                'link_title': link_title,
                'link_description': link_description,
                'image_hash': image_hash
            }

        except FacebookRequestError as e:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            return False, f"Error al importar el objeto del SDK de Facebook: {e}", {}
        except Exception as e:
            logger.error(f"Error inesperado al crear el creativo de anuncio Meta '{name}': {e}")
            return False, f"Error inesperado al crear el creativo de anuncio: {e}", {}


# Crear una instancia del gestor por defecto
_default_manager = None


def get_ad_creative_manager(client: Optional[MetaApiClient] = None) -> AdCreativeManager:
    """
    Obtiene una instancia del gestor de creativos de anuncios.

    Args:
        client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.

    Returns:
        Una instancia de AdCreativeManager.
    """
    global _default_manager

    if client:
        return AdCreativeManager(client)

    if _default_manager is None:
        _default_manager = AdCreativeManager()

    return _default_manager
