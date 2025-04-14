"""
Adaptador para la API de Meta Ads.

Este módulo implementa la interfaz abstracta AdAPI para la API de Meta Ads.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..abstract.ad_api import AdAPI, AdCampaign, AdSet, Ad, AdCreative, AdInsight
from ..meta.client import get_client, MetaApiClient
from ..meta.campaigns import get_campaign_manager
from ..meta.ad_sets import get_ad_set_manager
from ..meta.ads import get_ad_manager
from ..meta.ad_creatives import get_ad_creative_manager
from ..meta.insights import get_insight_manager


class MetaAdAPI(AdAPI):
    """
    Adaptador para la API de Meta Ads.

    Implementa la interfaz abstracta AdAPI para la API de Meta Ads.
    """

    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None,
                access_token: Optional[str] = None, ad_account_id: Optional[str] = None):
        """
        Inicializa el adaptador para la API de Meta Ads.

        Args:
            app_id: ID de la aplicación de Meta
            app_secret: Secreto de la aplicación de Meta
            access_token: Token de acceso de Meta
            ad_account_id: ID de la cuenta publicitaria de Meta
        """
        self.client = get_client(app_id, app_secret, access_token)
        self.ad_account_id = ad_account_id

        # Inicializar gestores
        self.campaign_manager = get_campaign_manager(self.client)
        self.adset_manager = get_ad_set_manager(self.client)
        self.ad_manager = get_ad_manager(self.client)
        self.creative_manager = get_ad_creative_manager(self.client)
        self.insight_manager = get_insight_manager(self.client)

    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la cuenta publicitaria.

        Returns:
            Diccionario con información de la cuenta
        """
        if not self.ad_account_id:
            return {'error': 'No se ha especificado un ID de cuenta publicitaria'}

        success, message, accounts = self.client.get_ad_accounts()
        if not success:
            return {'error': message}

        for account in accounts:
            if account['id'] == self.ad_account_id:
                return account

        return {'error': f'No se encontró la cuenta publicitaria con ID {self.ad_account_id}'}

    def get_campaigns(self, status: Optional[str] = None, limit: int = 100) -> List[AdCampaign]:
        """
        Obtiene las campañas publicitarias.

        Args:
            status: Estado de las campañas a obtener (opcional)
            limit: Número máximo de campañas a obtener

        Returns:
            Lista de campañas publicitarias
        """
        if not self.ad_account_id:
            return []

        success, message, campaigns = self.campaign_manager.get_campaigns(self.ad_account_id)
        if not success:
            return []

        result = []
        for campaign in campaigns[:limit]:
            if status and campaign.get('status') != status:
                continue

            campaign_obj = AdCampaign(
                id=campaign.get('id', ''),
                name=campaign.get('name', ''),
                status=campaign.get('status', ''),
                objective=campaign.get('objective', ''),
                start_time=self._parse_datetime(campaign.get('start_time')),
                end_time=self._parse_datetime(campaign.get('end_time')),
                daily_budget=campaign.get('daily_budget'),
                lifetime_budget=campaign.get('lifetime_budget'),
                created_time=self._parse_datetime(campaign.get('created_time')),
                updated_time=self._parse_datetime(campaign.get('updated_time'))
            )
            result.append(campaign_obj)

        return result

    def get_campaign(self, campaign_id: str) -> Optional[AdCampaign]:
        """
        Obtiene una campaña publicitaria por su ID.

        Args:
            campaign_id: ID de la campaña

        Returns:
            Campaña publicitaria o None si no existe
        """
        if not self.ad_account_id:
            return None

        success, message, campaign = self.campaign_manager.get_campaign(campaign_id)
        if not success:
            return None

        return AdCampaign(
            id=campaign.get('id', ''),
            name=campaign.get('name', ''),
            status=campaign.get('status', ''),
            objective=campaign.get('objective', ''),
            start_time=self._parse_datetime(campaign.get('start_time')),
            end_time=self._parse_datetime(campaign.get('end_time')),
            daily_budget=campaign.get('daily_budget'),
            lifetime_budget=campaign.get('lifetime_budget'),
            created_time=self._parse_datetime(campaign.get('created_time')),
            updated_time=self._parse_datetime(campaign.get('updated_time'))
        )

    def create_campaign(self, name: str, objective: str, status: str = 'PAUSED',
                       daily_budget: Optional[float] = None,
                       lifetime_budget: Optional[float] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> AdCampaign:
        """
        Crea una nueva campaña publicitaria.

        Args:
            name: Nombre de la campaña
            objective: Objetivo de la campaña
            status: Estado inicial de la campaña
            daily_budget: Presupuesto diario en la moneda de la cuenta
            lifetime_budget: Presupuesto total en la moneda de la cuenta
            start_time: Fecha y hora de inicio de la campaña
            end_time: Fecha y hora de finalización de la campaña

        Returns:
            Campaña publicitaria creada
        """
        if not self.ad_account_id:
            raise ValueError('No se ha especificado un ID de cuenta publicitaria')

        # Convertir presupuesto a centavos (Meta requiere centavos)
        daily_budget_cents = int(daily_budget * 100) if daily_budget else None
        lifetime_budget_cents = int(lifetime_budget * 100) if lifetime_budget else None

        # Crear campaña
        success, message, campaign = self.campaign_manager.create_campaign(
            ad_account_id=self.ad_account_id,
            name=name,
            objective=objective,
            status=status,
            daily_budget=daily_budget_cents,
            lifetime_budget=lifetime_budget_cents,
            start_time=start_time.isoformat() if start_time else None,
            end_time=end_time.isoformat() if end_time else None
        )

        if not success:
            raise ValueError(message)

        return AdCampaign(
            id=campaign.get('id', ''),
            name=name,
            status=status,
            objective=objective,
            start_time=start_time,
            end_time=end_time,
            daily_budget=daily_budget,
            lifetime_budget=lifetime_budget,
            created_time=datetime.now()
        )

    def update_campaign(self, campaign_id: str, name: Optional[str] = None,
                       status: Optional[str] = None,
                       daily_budget: Optional[float] = None,
                       lifetime_budget: Optional[float] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> AdCampaign:
        """
        Actualiza una campaña publicitaria existente.

        Args:
            campaign_id: ID de la campaña
            name: Nuevo nombre de la campaña
            status: Nuevo estado de la campaña
            daily_budget: Nuevo presupuesto diario
            lifetime_budget: Nuevo presupuesto total
            start_time: Nueva fecha y hora de inicio
            end_time: Nueva fecha y hora de finalización

        Returns:
            Campaña publicitaria actualizada
        """
        if not self.ad_account_id:
            raise ValueError('No se ha especificado un ID de cuenta publicitaria')

        # Convertir presupuesto a centavos (Meta requiere centavos)
        daily_budget_cents = int(daily_budget * 100) if daily_budget else None
        lifetime_budget_cents = int(lifetime_budget * 100) if lifetime_budget else None

        # Actualizar campaña
        success, message, campaign = self.campaign_manager.update_campaign(
            campaign_id=campaign_id,
            name=name,
            status=status,
            daily_budget=daily_budget_cents,
            lifetime_budget=lifetime_budget_cents,
            start_time=start_time.isoformat() if start_time else None,
            end_time=end_time.isoformat() if end_time else None
        )

        if not success:
            raise ValueError(message)

        return self.get_campaign(campaign_id)

    def delete_campaign(self, campaign_id: str) -> bool:
        """
        Elimina una campaña publicitaria.

        Args:
            campaign_id: ID de la campaña

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        success, message, _ = self.campaign_manager.delete_campaign(campaign_id)
        return success

    def get_adsets(self, campaign_id: Optional[str] = None, status: Optional[str] = None,
                 limit: int = 100) -> List[AdSet]:
        """
        Obtiene los conjuntos de anuncios.

        Args:
            campaign_id: ID de la campaña (opcional)
            status: Estado de los conjuntos a obtener (opcional)
            limit: Número máximo de conjuntos a obtener

        Returns:
            Lista de conjuntos de anuncios
        """
        if not self.ad_account_id:
            return []

        if campaign_id:
            success, message, adsets = self.adset_manager.get_adsets_by_campaign(campaign_id)
        else:
            success, message, adsets = self.adset_manager.get_adsets(self.ad_account_id)

        if not success:
            return []

        result = []
        for adset in adsets[:limit]:
            if status and adset.get('status') != status:
                continue

            targeting = adset.get('targeting', {})
            adset_obj = AdSet(
                id=adset.get('id', ''),
                name=adset.get('name', ''),
                campaign_id=adset.get('campaign_id', ''),
                status=adset.get('status', ''),
                targeting=targeting,
                start_time=self._parse_datetime(adset.get('start_time')),
                end_time=self._parse_datetime(adset.get('end_time')),
                daily_budget=adset.get('daily_budget'),
                lifetime_budget=adset.get('lifetime_budget'),
                bid_amount=adset.get('bid_amount'),
                bid_strategy=adset.get('bid_strategy'),
                optimization_goal=adset.get('optimization_goal'),
                billing_event=adset.get('billing_event'),
                created_time=self._parse_datetime(adset.get('created_time')),
                updated_time=self._parse_datetime(adset.get('updated_time'))
            )
            result.append(adset_obj)

        return result

    def get_adset(self, adset_id: str) -> Optional[AdSet]:
        """
        Obtiene un conjunto de anuncios por su ID.

        Args:
            adset_id: ID del conjunto

        Returns:
            Conjunto de anuncios o None si no existe
        """
        success, message, adset = self.adset_manager.get_adset(adset_id)
        if not success:
            return None

        targeting = adset.get('targeting', {})
        return AdSet(
            id=adset.get('id', ''),
            name=adset.get('name', ''),
            campaign_id=adset.get('campaign_id', ''),
            status=adset.get('status', ''),
            targeting=targeting,
            start_time=self._parse_datetime(adset.get('start_time')),
            end_time=self._parse_datetime(adset.get('end_time')),
            daily_budget=adset.get('daily_budget'),
            lifetime_budget=adset.get('lifetime_budget'),
            bid_amount=adset.get('bid_amount'),
            bid_strategy=adset.get('bid_strategy'),
            optimization_goal=adset.get('optimization_goal'),
            billing_event=adset.get('billing_event'),
            created_time=self._parse_datetime(adset.get('created_time')),
            updated_time=self._parse_datetime(adset.get('updated_time'))
        )

    def create_adset(self, name: str, campaign_id: str, targeting: Dict[str, Any],
                    status: str = 'PAUSED', optimization_goal: Optional[str] = None,
                    billing_event: Optional[str] = None, bid_amount: Optional[float] = None,
                    daily_budget: Optional[float] = None, lifetime_budget: Optional[float] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> AdSet:
        """
        Crea un nuevo conjunto de anuncios.

        Args:
            name: Nombre del conjunto
            campaign_id: ID de la campaña
            targeting: Configuración de segmentación
            status: Estado inicial del conjunto
            optimization_goal: Objetivo de optimización
            billing_event: Evento de facturación
            bid_amount: Cantidad de puja
            daily_budget: Presupuesto diario
            lifetime_budget: Presupuesto total
            start_time: Fecha y hora de inicio
            end_time: Fecha y hora de finalización

        Returns:
            Conjunto de anuncios creado
        """
        if not self.ad_account_id:
            raise ValueError('No se ha especificado un ID de cuenta publicitaria')

        # Convertir presupuesto y puja a centavos (Meta requiere centavos)
        daily_budget_cents = int(daily_budget * 100) if daily_budget else None
        lifetime_budget_cents = int(lifetime_budget * 100) if lifetime_budget else None
        bid_amount_cents = int(bid_amount * 100) if bid_amount else None

        # Crear conjunto de anuncios
        success, message, adset = self.adset_manager.create_ad_set(
            ad_account_id=self.ad_account_id,
            campaign_id=campaign_id,
            name=name,
            optimization_goal=optimization_goal or 'LINK_CLICKS',
            billing_event=billing_event or 'IMPRESSIONS',
            daily_budget_cents=daily_budget_cents or 1000,  # 10 USD por defecto
            targeting_spec=targeting,
            status=status,
            bid_amount=bid_amount_cents
        )

        if not success:
            raise ValueError(message)

        return AdSet(
            id=adset.get('id', ''),
            name=name,
            campaign_id=campaign_id,
            status=status,
            targeting=targeting,
            start_time=start_time,
            end_time=end_time,
            daily_budget=daily_budget,
            lifetime_budget=lifetime_budget,
            bid_amount=bid_amount,
            optimization_goal=optimization_goal,
            billing_event=billing_event,
            created_time=datetime.now()
        )

    def update_adset(self, adset_id: str, name: Optional[str] = None,
                    status: Optional[str] = None, targeting: Optional[Dict[str, Any]] = None,
                    optimization_goal: Optional[str] = None,
                    billing_event: Optional[str] = None, bid_amount: Optional[float] = None,
                    daily_budget: Optional[float] = None, lifetime_budget: Optional[float] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> AdSet:
        """
        Actualiza un conjunto de anuncios existente.

        Args:
            adset_id: ID del conjunto
            name: Nuevo nombre del conjunto
            status: Nuevo estado del conjunto
            targeting: Nueva configuración de segmentación
            optimization_goal: Nuevo objetivo de optimización
            billing_event: Nuevo evento de facturación
            bid_amount: Nueva cantidad de puja
            daily_budget: Nuevo presupuesto diario
            lifetime_budget: Nuevo presupuesto total
            start_time: Nueva fecha y hora de inicio
            end_time: Nueva fecha y hora de finalización

        Returns:
            Conjunto de anuncios actualizado
        """
        # Convertir presupuesto y puja a centavos (Meta requiere centavos)
        daily_budget_cents = int(daily_budget * 100) if daily_budget else None
        lifetime_budget_cents = int(lifetime_budget * 100) if lifetime_budget else None
        bid_amount_cents = int(bid_amount * 100) if bid_amount else None

        # Actualizar conjunto de anuncios
        success, message, _ = self.adset_manager.update_ad_set(
            ad_set_id=adset_id,
            name=name,
            status=status,
            targeting_spec=targeting,
            optimization_goal=optimization_goal,
            billing_event=billing_event,
            bid_amount=bid_amount_cents,
            daily_budget=daily_budget_cents,
            lifetime_budget=lifetime_budget_cents
        )

        if not success:
            raise ValueError(message)

        return self.get_adset(adset_id)

    def delete_adset(self, adset_id: str) -> bool:
        """
        Elimina un conjunto de anuncios.

        Args:
            adset_id: ID del conjunto

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        success, message, _ = self.adset_manager.delete_ad_set(adset_id)
        return success

    def get_ads(self, adset_id: Optional[str] = None, status: Optional[str] = None,
               limit: int = 100) -> List[Ad]:
        """
        Obtiene los anuncios.

        Args:
            adset_id: ID del conjunto de anuncios (opcional)
            status: Estado de los anuncios a obtener (opcional)
            limit: Número máximo de anuncios a obtener

        Returns:
            Lista de anuncios
        """
        if not adset_id:
            return []

        success, message, ads = self.ad_manager.get_ads(adset_id)
        if not success:
            return []

        result = []
        for ad in ads[:limit]:
            if status and ad.get('status') != status:
                continue

            ad_obj = Ad(
                id=ad.get('id', ''),
                name=ad.get('name', ''),
                adset_id=adset_id,
                creative_id=ad.get('creative_id', ''),
                status=ad.get('status', ''),
                created_time=self._parse_datetime(ad.get('created_time')),
                updated_time=self._parse_datetime(ad.get('updated_time'))
            )
            result.append(ad_obj)

        return result

    def get_ad(self, ad_id: str) -> Optional[Ad]:
        """
        Obtiene un anuncio por su ID.

        Args:
            ad_id: ID del anuncio

        Returns:
            Anuncio o None si no existe
        """
        success, message, ad = self.ad_manager.get_ad(ad_id)
        if not success:
            return None

        return Ad(
            id=ad.get('id', ''),
            name=ad.get('name', ''),
            adset_id=ad.get('adset_id', ''),
            creative_id=ad.get('creative_id', ''),
            status=ad.get('status', ''),
            created_time=self._parse_datetime(ad.get('created_time')),
            updated_time=self._parse_datetime(ad.get('updated_time'))
        )

    def create_ad(self, name: str, adset_id: str, creative_id: str,
                 status: str = 'PAUSED') -> Ad:
        """
        Crea un nuevo anuncio.

        Args:
            name: Nombre del anuncio
            adset_id: ID del conjunto de anuncios
            creative_id: ID del creativo
            status: Estado inicial del anuncio

        Returns:
            Anuncio creado
        """
        if not self.ad_account_id:
            raise ValueError('No se ha especificado un ID de cuenta publicitaria')

        # Crear anuncio
        success, message, ad = self.ad_manager.create_ad(
            ad_account_id=self.ad_account_id,
            name=name,
            adset_id=adset_id,
            creative_id=creative_id,
            status=status
        )

        if not success:
            raise ValueError(message)

        return Ad(
            id=ad.get('id', ''),
            name=name,
            adset_id=adset_id,
            creative_id=creative_id,
            status=status,
            created_time=datetime.now()
        )

    def update_ad(self, ad_id: str, name: Optional[str] = None,
                 status: Optional[str] = None) -> Ad:
        """
        Actualiza un anuncio existente.

        Args:
            ad_id: ID del anuncio
            name: Nuevo nombre del anuncio
            status: Nuevo estado del anuncio

        Returns:
            Anuncio actualizado
        """
        # Actualizar anuncio
        success, message, _ = self.ad_manager.update_ad(
            ad_id=ad_id,
            name=name,
            status=status
        )

        if not success:
            raise ValueError(message)

        return self.get_ad(ad_id)

    def delete_ad(self, ad_id: str) -> bool:
        """
        Elimina un anuncio.

        Args:
            ad_id: ID del anuncio

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        success, message, _ = self.ad_manager.delete_ad(ad_id)
        return success

    def get_ad_creatives(self, ad_id: Optional[str] = None, limit: int = 100) -> List[AdCreative]:
        """
        Obtiene los creativos de anuncios.

        Args:
            ad_id: ID del anuncio (opcional)
            limit: Número máximo de creativos a obtener

        Returns:
            Lista de creativos
        """
        if not self.ad_account_id:
            return []

        success, message, creatives = self.creative_manager.get_ad_creatives(self.ad_account_id)
        if not success:
            return []

        result = []
        for creative in creatives[:limit]:
            creative_obj = AdCreative(
                id=creative.get('id', ''),
                name=creative.get('name', ''),
                title=creative.get('title', ''),
                body=creative.get('body', ''),
                image_url=creative.get('image_url', ''),
                image_hash=creative.get('image_hash', ''),
                video_id=creative.get('video_id', ''),
                call_to_action=creative.get('call_to_action_type', ''),
                link_url=creative.get('link_url', ''),
                created_time=self._parse_datetime(creative.get('created_time'))
            )
            result.append(creative_obj)

        return result

    def get_ad_creative(self, creative_id: str) -> Optional[AdCreative]:
        """
        Obtiene un creativo por su ID.

        Args:
            creative_id: ID del creativo

        Returns:
            Creativo o None si no existe
        """
        success, message, creative = self.creative_manager.get_ad_creative(creative_id)
        if not success:
            return None

        return AdCreative(
            id=creative.get('id', ''),
            name=creative.get('name', ''),
            title=creative.get('title', ''),
            body=creative.get('body', ''),
            image_url=creative.get('image_url', ''),
            image_hash=creative.get('image_hash', ''),
            video_id=creative.get('video_id', ''),
            call_to_action=creative.get('call_to_action_type', ''),
            link_url=creative.get('link_url', ''),
            created_time=self._parse_datetime(creative.get('created_time'))
        )

    def create_ad_creative(self, name: str, title: str, body: str,
                          image_url: Optional[str] = None, image_hash: Optional[str] = None,
                          video_id: Optional[str] = None,
                          call_to_action: Optional[str] = None,
                          link_url: Optional[str] = None) -> AdCreative:
        """
        Crea un nuevo creativo.

        Args:
            name: Nombre del creativo
            title: Título del anuncio
            body: Cuerpo del anuncio
            image_url: URL de la imagen
            image_hash: Hash de la imagen
            video_id: ID del video
            call_to_action: Llamada a la acción
            link_url: URL de destino

        Returns:
            Creativo creado
        """
        if not self.ad_account_id:
            raise ValueError('No se ha especificado un ID de cuenta publicitaria')

        # Crear creativo
        success, message, creative = self.creative_manager.create_ad_creative(
            ad_account_id=self.ad_account_id,
            name=name,
            page_id='me',  # Usar la página asociada al token de acceso
            message=body,
            link=link_url or 'https://example.com',
            link_title=title,
            link_description=body,
            image_hash=image_hash,
            call_to_action_type=call_to_action or 'APPLY_NOW'
        )

        if not success:
            raise ValueError(message)

        return AdCreative(
            id=creative.get('id', ''),
            name=name,
            title=title,
            body=body,
            image_url=image_url,
            image_hash=image_hash,
            video_id=video_id,
            call_to_action=call_to_action,
            link_url=link_url,
            created_time=datetime.now()
        )

    def get_insights(self, object_ids: List[str], level: str,
                    fields: List[str], date_preset: Optional[str] = None,
                    time_range: Optional[Dict[str, str]] = None,
                    filtering: Optional[List[Dict[str, Any]]] = None,
                    breakdowns: Optional[List[str]] = None,
                    limit: int = 100) -> List[AdInsight]:
        """
        Obtiene insights de rendimiento.

        Args:
            object_ids: IDs de los objetos (campañas, conjuntos, anuncios)
            level: Nivel de agregación ('campaign', 'adset', 'ad')
            fields: Campos a obtener
            date_preset: Preajuste de fecha ('today', 'yesterday', 'this_week', etc.)
            time_range: Rango de fechas personalizado
            filtering: Filtros adicionales
            breakdowns: Desgloses adicionales
            limit: Número máximo de resultados

        Returns:
            Lista de insights
        """
        if not object_ids:
            return []

        # Obtener insights
        success, message, insights = self.insight_manager.get_insights(
            object_ids=object_ids,
            level=level,
            fields=fields,
            date_preset=date_preset,
            time_range=time_range,
            filtering=filtering,
            breakdowns=breakdowns,
            limit=limit
        )

        if not success:
            return []

        result = []
        for insight in insights:
            # Determinar ID del objeto según el nivel
            campaign_id = insight.get('campaign_id') if level in ['campaign', 'adset', 'ad'] else None
            adset_id = insight.get('adset_id') if level in ['adset', 'ad'] else None
            ad_id = insight.get('ad_id') if level == 'ad' else None

            # Crear objeto de insight
            insight_obj = AdInsight(
                date_start=self._parse_datetime(insight.get('date_start')) or datetime.now(),
                date_stop=self._parse_datetime(insight.get('date_stop')) or datetime.now(),
                campaign_id=campaign_id,
                adset_id=adset_id,
                ad_id=ad_id,
                impressions=insight.get('impressions'),
                clicks=insight.get('clicks'),
                spend=insight.get('spend'),
                reach=insight.get('reach'),
                frequency=insight.get('frequency'),
                cpm=insight.get('cpm'),
                cpc=insight.get('cpc'),
                ctr=insight.get('ctr'),
                conversions=insight.get('conversions'),
                cost_per_conversion=insight.get('cost_per_conversion')
            )
            result.append(insight_obj)

        return result

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """
        Convierte una cadena de fecha y hora a un objeto datetime.

        Args:
            dt_str: Cadena de fecha y hora

        Returns:
            Objeto datetime o None si la cadena es None
        """
        if not dt_str:
            return None

        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None
