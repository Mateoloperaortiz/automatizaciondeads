"""
Utilidades para la API de Meta (Facebook/Instagram) Ads.

Este módulo proporciona funciones de utilidad para trabajar con la API de Meta Ads,
como la carga de imágenes, la creación de audiencias personalizadas, etc.
"""

import os
from typing import Tuple, List, Dict, Any, Optional
import hashlib

# Intentar importar Facebook Business SDK, pero no fallar si no está disponible
try:
    from facebook_business.exceptions import FacebookRequestError
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.customaudience import CustomAudience
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FacebookRequestError = Exception
    AdAccount = object
    CustomAudience = object
    FACEBOOK_SDK_AVAILABLE = False

from adflux.api.common.error_handling import handle_meta_api_error
from adflux.api.common.logging import get_logger
from adflux.api.meta.client import get_client, MetaApiClient

# Configurar logger
logger = get_logger("MetaUtils")


class MetaUtils:
    """
    Utilidades para trabajar con la API de Meta Ads.
    """
    
    def __init__(self, client: Optional[MetaApiClient] = None):
        """
        Inicializa las utilidades de Meta.
        
        Args:
            client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()
    
    @handle_meta_api_error
    def upload_image(self, ad_account_id: str, image_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Sube una imagen a la Biblioteca de Anuncios de Meta.
        
        Args:
            ad_account_id: ID de la cuenta publicitaria (ej., 'act_123456789').
            image_path: Ruta al archivo de imagen a subir.
            
        Returns:
            Una tupla con: (éxito, mensaje, datos de la imagen).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", {}
        
        try:
            # Verificar que el archivo existe
            if not os.path.exists(image_path):
                return False, f"El archivo de imagen no existe: {image_path}", {}
            
            # Obtener la cuenta publicitaria
            account = AdAccount(ad_account_id)
            
            # Subir la imagen
            with open(image_path, 'rb') as image_file:
                image = account.create_ad_image(
                    params={
                        'bytes': image_file.read(),
                    }
                )
            
            # Obtener el hash de la imagen
            image_hash = image.get('hash')
            
            logger.info(f"Imagen subida correctamente con hash: {image_hash}")
            
            return True, "Imagen subida correctamente", {
                'hash': image_hash,
                'id': image.get('id'),
                'url': image.get('url')
            }
            
        except FacebookRequestError as e:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al subir la imagen: {e}", e)
            return False, f"Error inesperado al subir la imagen: {e}", {}
    
    @handle_meta_api_error
    def create_custom_audience(
        self,
        ad_account_id: str,
        name: str,
        description: str,
        customer_file_source: str,
        subtype: str,
        user_identifiers: List[Dict[str, str]],
        identifier_type: str = "EXTERN_ID"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Crea una Audiencia Personalizada Meta a partir de una lista de IDs externos.
        
        Args:
            ad_account_id: ID de la cuenta publicitaria (ej., 'act_123456789').
            name: Nombre para la audiencia personalizada.
            description: Descripción de la audiencia personalizada.
            customer_file_source: Fuente del archivo de clientes (ej., 'USER_PROVIDED_ONLY').
            subtype: Subtipo de audiencia (ej., 'CUSTOM').
            user_identifiers: Lista de identificadores de usuario.
            identifier_type: Tipo de identificador (ej., 'EXTERN_ID', 'EMAIL', 'PHONE').
            
        Returns:
            Una tupla con: (éxito, mensaje, datos de la audiencia).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", {}
        
        try:
            # Obtener la cuenta publicitaria
            account = AdAccount(ad_account_id)
            
            # Crear la audiencia personalizada
            audience = account.create_custom_audience(
                params={
                    CustomAudience.Field.name: name,
                    CustomAudience.Field.description: description,
                    CustomAudience.Field.customer_file_source: customer_file_source,
                    CustomAudience.Field.subtype: subtype,
                }
            )
            
            audience_id = audience.get('id')
            
            # Añadir usuarios a la audiencia
            if user_identifiers:
                # Preparar los datos de usuario
                schema = [
                    identifier_type
                ]
                
                # Hashear los identificadores si es necesario
                hashed_users = []
                for user in user_identifiers:
                    hashed_user = {}
                    for key, value in user.items():
                        if key == identifier_type:
                            # Hashear el valor si no está ya hasheado
                            if not self._is_hashed(value):
                                hashed_value = self._hash_value(value)
                            else:
                                hashed_value = value
                            hashed_user[key] = hashed_value
                    hashed_users.append(hashed_user)
                
                # Añadir usuarios a la audiencia
                audience = CustomAudience(audience_id)
                audience.add_users(
                    schema=schema,
                    data=hashed_users,
                )
            
            logger.info(f"Audiencia personalizada '{name}' creada correctamente con ID: {audience_id}")
            
            return True, f"Audiencia personalizada '{name}' creada correctamente", {
                'id': audience_id,
                'name': name,
                'description': description
            }
            
        except FacebookRequestError as e:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear la audiencia personalizada: {e}", e)
            return False, f"Error inesperado al crear la audiencia personalizada: {e}", {}
    
    def _is_hashed(self, value: str) -> bool:
        """
        Verifica si un valor ya está hasheado (SHA256).
        
        Args:
            value: El valor a verificar.
            
        Returns:
            True si el valor parece estar hasheado, False en caso contrario.
        """
        # Un hash SHA256 tiene 64 caracteres hexadecimales
        if len(value) != 64:
            return False
        
        # Verificar que todos los caracteres son hexadecimales
        try:
            int(value, 16)
            return True
        except ValueError:
            return False
    
    def _hash_value(self, value: str) -> str:
        """
        Hashea un valor usando SHA256.
        
        Args:
            value: El valor a hashear.
            
        Returns:
            El valor hasheado.
        """
        # Normalizar el valor (convertir a minúsculas y eliminar espacios)
        normalized = value.lower().strip()
        
        # Hashear el valor
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


# Crear una instancia de las utilidades por defecto
_default_utils = None


def get_meta_utils(client: Optional[MetaApiClient] = None) -> MetaUtils:
    """
    Obtiene una instancia de las utilidades de Meta.
    
    Args:
        client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        
    Returns:
        Una instancia de MetaUtils.
    """
    global _default_utils
    
    if client:
        return MetaUtils(client)
    
    if _default_utils is None:
        _default_utils = MetaUtils()
    
    return _default_utils
