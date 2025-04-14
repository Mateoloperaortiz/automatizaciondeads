"""
Interfaces abstractas para APIs publicitarias.

Este módulo define las interfaces abstractas para las APIs publicitarias
utilizadas por AdFlux, como Meta Ads API, Google Ads API, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime


@dataclass
class AdCampaign:
    """Clase base para campañas publicitarias."""
    
    id: str
    name: str
    status: str
    objective: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    budget: Optional[float] = None
    budget_remaining: Optional[float] = None
    daily_budget: Optional[float] = None
    lifetime_budget: Optional[float] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la campaña a un diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'objective': self.objective,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'budget': self.budget,
            'budget_remaining': self.budget_remaining,
            'daily_budget': self.daily_budget,
            'lifetime_budget': self.lifetime_budget,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None,
        }


@dataclass
class AdSet:
    """Clase base para conjuntos de anuncios."""
    
    id: str
    name: str
    campaign_id: str
    status: str
    targeting: Dict[str, Any]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    budget: Optional[float] = None
    daily_budget: Optional[float] = None
    lifetime_budget: Optional[float] = None
    bid_amount: Optional[float] = None
    bid_strategy: Optional[str] = None
    optimization_goal: Optional[str] = None
    billing_event: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el conjunto de anuncios a un diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'campaign_id': self.campaign_id,
            'status': self.status,
            'targeting': self.targeting,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'budget': self.budget,
            'daily_budget': self.daily_budget,
            'lifetime_budget': self.lifetime_budget,
            'bid_amount': self.bid_amount,
            'bid_strategy': self.bid_strategy,
            'optimization_goal': self.optimization_goal,
            'billing_event': self.billing_event,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None,
        }


@dataclass
class AdCreative:
    """Clase base para creativos de anuncios."""
    
    id: str
    name: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[str] = None
    image_hash: Optional[str] = None
    video_id: Optional[str] = None
    call_to_action: Optional[str] = None
    link_url: Optional[str] = None
    created_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el creativo a un diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'body': self.body,
            'image_url': self.image_url,
            'image_hash': self.image_hash,
            'video_id': self.video_id,
            'call_to_action': self.call_to_action,
            'link_url': self.link_url,
            'created_time': self.created_time.isoformat() if self.created_time else None,
        }


@dataclass
class Ad:
    """Clase base para anuncios."""
    
    id: str
    name: str
    adset_id: str
    creative_id: str
    status: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el anuncio a un diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'adset_id': self.adset_id,
            'creative_id': self.creative_id,
            'status': self.status,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None,
        }


@dataclass
class AdInsight:
    """Clase base para insights de anuncios."""
    
    date_start: datetime
    date_stop: datetime
    campaign_id: Optional[str] = None
    adset_id: Optional[str] = None
    ad_id: Optional[str] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    spend: Optional[float] = None
    reach: Optional[int] = None
    frequency: Optional[float] = None
    cpm: Optional[float] = None
    cpc: Optional[float] = None
    ctr: Optional[float] = None
    conversions: Optional[int] = None
    cost_per_conversion: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el insight a un diccionario."""
        return {
            'date_start': self.date_start.isoformat(),
            'date_stop': self.date_stop.isoformat(),
            'campaign_id': self.campaign_id,
            'adset_id': self.adset_id,
            'ad_id': self.ad_id,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'spend': self.spend,
            'reach': self.reach,
            'frequency': self.frequency,
            'cpm': self.cpm,
            'cpc': self.cpc,
            'ctr': self.ctr,
            'conversions': self.conversions,
            'cost_per_conversion': self.cost_per_conversion,
        }


class AdAPI(ABC):
    """
    Interfaz abstracta para APIs publicitarias.
    
    Define los métodos comunes que deben implementar todas las APIs
    publicitarias utilizadas por AdFlux.
    """
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la cuenta publicitaria.
        
        Returns:
            Diccionario con información de la cuenta
        """
        pass
    
    @abstractmethod
    def get_campaigns(self, status: Optional[str] = None, limit: int = 100) -> List[AdCampaign]:
        """
        Obtiene las campañas publicitarias.
        
        Args:
            status: Estado de las campañas a obtener (opcional)
            limit: Número máximo de campañas a obtener
            
        Returns:
            Lista de campañas publicitarias
        """
        pass
    
    @abstractmethod
    def get_campaign(self, campaign_id: str) -> Optional[AdCampaign]:
        """
        Obtiene una campaña publicitaria por su ID.
        
        Args:
            campaign_id: ID de la campaña
            
        Returns:
            Campaña publicitaria o None si no existe
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def delete_campaign(self, campaign_id: str) -> bool:
        """
        Elimina una campaña publicitaria.
        
        Args:
            campaign_id: ID de la campaña
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_adset(self, adset_id: str) -> Optional[AdSet]:
        """
        Obtiene un conjunto de anuncios por su ID.
        
        Args:
            adset_id: ID del conjunto
            
        Returns:
            Conjunto de anuncios o None si no existe
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def delete_adset(self, adset_id: str) -> bool:
        """
        Elimina un conjunto de anuncios.
        
        Args:
            adset_id: ID del conjunto
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_ad(self, ad_id: str) -> Optional[Ad]:
        """
        Obtiene un anuncio por su ID.
        
        Args:
            ad_id: ID del anuncio
            
        Returns:
            Anuncio o None si no existe
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def delete_ad(self, ad_id: str) -> bool:
        """
        Elimina un anuncio.
        
        Args:
            ad_id: ID del anuncio
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_ad_creatives(self, ad_id: Optional[str] = None, limit: int = 100) -> List[AdCreative]:
        """
        Obtiene los creativos de anuncios.
        
        Args:
            ad_id: ID del anuncio (opcional)
            limit: Número máximo de creativos a obtener
            
        Returns:
            Lista de creativos
        """
        pass
    
    @abstractmethod
    def get_ad_creative(self, creative_id: str) -> Optional[AdCreative]:
        """
        Obtiene un creativo por su ID.
        
        Args:
            creative_id: ID del creativo
            
        Returns:
            Creativo o None si no existe
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
