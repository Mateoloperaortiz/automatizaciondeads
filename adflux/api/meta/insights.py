"""
Gestión de insights para la API de Meta (Facebook/Instagram) Ads.

Este módulo proporciona funcionalidades para obtener y analizar
métricas de rendimiento (insights) de campañas, conjuntos de anuncios y anuncios.
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
logger = get_logger("MetaInsights")


class InsightsManager:
    """
    Gestor de insights para la API de Meta Ads.
    """

    def __init__(self, client: Optional[MetaApiClient] = None):
        """
        Inicializa el gestor de insights.

        Args:
            client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.
        """
        self.client = client or get_client()

    @handle_meta_api_error
    def get_insights(
        self,
        object_id: str,
        level: str,
        date_preset: str = "last_30d",
        time_increment: Optional[int] = None,
        fields: Optional[List[str]] = None,
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Obtiene insights para un objeto específico (campaña, conjunto de anuncios o anuncio).

        Args:
            object_id: ID del objeto (campaña, conjunto de anuncios o anuncio).
            level: Nivel de los insights ('campaign', 'adset', 'ad').
            date_preset: Período de tiempo predefinido (ej., 'last_30d', 'last_7d', 'yesterday').
            time_increment: Incremento de tiempo para agrupar los resultados (ej., 1 para diario).
            fields: Lista de campos a recuperar. Si es None, se usan campos predeterminados.

        Returns:
            Una tupla con: (éxito, mensaje, lista de insights).
        """
        api = self.client.get_api()
        if not api:
            return False, "No se pudo inicializar la API de Meta", []

        try:
            # Importar los objetos necesarios según el nivel
            if level == "campaign":
                from facebook_business.adobjects.campaign import Campaign

                obj = Campaign(object_id)
            elif level == "adset":
                from facebook_business.adobjects.adset import AdSet

                obj = AdSet(object_id)
            elif level == "ad":
                from facebook_business.adobjects.ad import Ad

                obj = Ad(object_id)
            else:
                return False, f"Nivel no válido: {level}. Debe ser 'campaign', 'adset' o 'ad'.", []

            # Definir los campos predeterminados si no se proporcionan
            if fields is None:
                fields = [
                    "impressions",
                    "clicks",
                    "spend",
                    "reach",
                    "cpm",
                    "cpc",
                    "ctr",
                    "frequency",
                    "actions",
                    "cost_per_action_type",
                ]

            # Preparar los parámetros para la solicitud de insights
            params = {"date_preset": date_preset}

            # Añadir time_increment si se proporciona
            if time_increment is not None:
                params["time_increment"] = time_increment

            # Obtener los insights
            insights = obj.get_insights(fields=fields, params=params)

            # Procesar los resultados para un formato más amigable
            insights_list = []
            for insight in insights:
                insight_data = {}
                for field in fields:
                    insight_data[field] = insight.get(field)

                # Añadir información de fecha si está disponible
                if "date_start" in insight:
                    insight_data["date_start"] = insight.get("date_start")
                if "date_stop" in insight:
                    insight_data["date_stop"] = insight.get("date_stop")

                insights_list.append(insight_data)

            logger.info(
                f"Se recuperaron {len(insights_list)} insights para el {level} {object_id}."
            )
            return True, f"Se recuperaron {len(insights_list)} insights.", insights_list

        except FacebookRequestError:
            # Este error ya será manejado por el decorador handle_meta_api_error
            raise
        except ImportError as e:
            logger.error(f"Error al importar el objeto del SDK de Facebook: {e}")
            return False, f"Error al importar el objeto del SDK de Facebook: {e}", []
        except Exception as e:
            logger.error(f"Error inesperado al obtener insights para {level} {object_id}: {e}", e)
            return False, f"Error inesperado al obtener insights: {e}", []


# Crear una instancia del gestor por defecto
_default_manager = None


def get_insights_manager(client: Optional[MetaApiClient] = None) -> InsightsManager:
    """
    Obtiene una instancia del gestor de insights.

    Args:
        client: Cliente de la API de Meta. Si es None, se usa el cliente por defecto.

    Returns:
        Una instancia de InsightsManager.
    """
    global _default_manager

    if client:
        return InsightsManager(client)

    if _default_manager is None:
        _default_manager = InsightsManager()

    return _default_manager
