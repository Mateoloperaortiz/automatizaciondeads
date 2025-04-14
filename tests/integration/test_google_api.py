"""
Pruebas de integración para la API de Google Ads en AdFlux.

Este módulo contiene pruebas para verificar la integración con la API de Google Ads.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from adflux.google.client import GoogleAdsApiClient
from adflux.google.campaigns import create_campaign, get_campaign, update_campaign, delete_campaign
from adflux.google.ad_groups import create_ad_group, get_ad_group, update_ad_group, delete_ad_group
from adflux.google.ads import create_ad, get_ad, update_ad, delete_ad


@pytest.mark.integration
class TestGoogleAdsApi:
    """Pruebas para la API de Google Ads."""
    
    @patch('adflux.google.client.GoogleAdsClient')
    def test_google_ads_api_client(self, mock_google_ads_client):
        """Prueba el cliente de la API de Google Ads."""
        # Configurar mock
        mock_client = MagicMock()
        mock_google_ads_client.load_from_dict.return_value = mock_client
        
        # Crear cliente
        client = GoogleAdsApiClient(
            developer_token='test_developer_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token',
            login_customer_id='1234567890'
        )
        
        # Verificar que se creó el cliente
        assert client.client == mock_client
        
        # Verificar que se llamó a load_from_dict con los parámetros correctos
        mock_google_ads_client.load_from_dict.assert_called_once()
        config = mock_google_ads_client.load_from_dict.call_args[0][0]
        assert config['developer_token'] == 'test_developer_token'
        assert config['client_id'] == 'test_client_id'
        assert config['client_secret'] == 'test_client_secret'
        assert config['refresh_token'] == 'test_refresh_token'
        assert config['login_customer_id'] == '1234567890'
    
    @patch('adflux.google.campaigns.GoogleAdsApiClient')
    def test_create_campaign(self, mock_client_class):
        """Prueba la creación de una campaña en Google Ads."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Configurar respuesta simulada
        mock_campaign_service = MagicMock()
        mock_client.get_service.return_value = mock_campaign_service
        
        mock_campaign_operation = MagicMock()
        mock_client.get_type.return_value = mock_campaign_operation
        
        mock_mutate_response = MagicMock()
        mock_campaign_service.mutate_campaigns.return_value = mock_mutate_response
        mock_mutate_response.results = [MagicMock()]
        mock_mutate_response.results[0].resource_name = 'customers/1234567890/campaigns/9876543210'
        
        # Crear campaña
        result = create_campaign(
            customer_id='1234567890',
            name='Test Campaign',
            budget_amount=1000000,  # En micros (1000000 = $1.00)
            advertising_channel_type='SEARCH',
            status='PAUSED',
            developer_token='test_developer_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token'
        )
        
        # Verificar resultado
        assert result == 'customers/1234567890/campaigns/9876543210'
        
        # Verificar que se llamó al servicio de campañas
        mock_client.get_service.assert_called_with('CampaignService')
        
        # Verificar que se llamó a mutate_campaigns
        mock_campaign_service.mutate_campaigns.assert_called_once()
    
    @patch('adflux.google.campaigns.GoogleAdsApiClient')
    def test_get_campaign(self, mock_client_class):
        """Prueba la obtención de una campaña de Google Ads."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Configurar respuesta simulada
        mock_google_ads_service = MagicMock()
        mock_client.get_service.return_value = mock_google_ads_service
        
        mock_search_response = MagicMock()
        mock_google_ads_service.search.return_value = mock_search_response
        
        mock_row = MagicMock()
        mock_row.campaign.id = 9876543210
        mock_row.campaign.name = 'Test Campaign'
        mock_row.campaign.status = 'PAUSED'
        mock_search_response.__iter__.return_value = [mock_row]
        
        # Obtener campaña
        result = get_campaign(
            customer_id='1234567890',
            campaign_id='9876543210',
            developer_token='test_developer_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token'
        )
        
        # Verificar resultado
        assert result['id'] == 9876543210
        assert result['name'] == 'Test Campaign'
        assert result['status'] == 'PAUSED'
        
        # Verificar que se llamó al servicio de Google Ads
        mock_client.get_service.assert_called_with('GoogleAdsService')
        
        # Verificar que se llamó a search con la consulta correcta
        mock_google_ads_service.search.assert_called_once()
        query = mock_google_ads_service.search.call_args[1]['query']
        assert 'SELECT campaign.id, campaign.name, campaign.status' in query
        assert 'FROM campaign' in query
        assert 'WHERE campaign.id = 9876543210' in query
    
    @patch('adflux.google.campaigns.GoogleAdsApiClient')
    def test_update_campaign(self, mock_client_class):
        """Prueba la actualización de una campaña de Google Ads."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Configurar respuesta simulada
        mock_campaign_service = MagicMock()
        mock_client.get_service.return_value = mock_campaign_service
        
        mock_campaign_operation = MagicMock()
        mock_client.get_type.return_value = mock_campaign_operation
        
        mock_mutate_response = MagicMock()
        mock_campaign_service.mutate_campaigns.return_value = mock_mutate_response
        mock_mutate_response.results = [MagicMock()]
        mock_mutate_response.results[0].resource_name = 'customers/1234567890/campaigns/9876543210'
        
        # Actualizar campaña
        result = update_campaign(
            customer_id='1234567890',
            campaign_id='9876543210',
            name='Updated Campaign',
            status='ENABLED',
            developer_token='test_developer_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token'
        )
        
        # Verificar resultado
        assert result == 'customers/1234567890/campaigns/9876543210'
        
        # Verificar que se llamó al servicio de campañas
        mock_client.get_service.assert_called_with('CampaignService')
        
        # Verificar que se llamó a mutate_campaigns
        mock_campaign_service.mutate_campaigns.assert_called_once()
    
    @patch('adflux.google.campaigns.GoogleAdsApiClient')
    def test_delete_campaign(self, mock_client_class):
        """Prueba la eliminación de una campaña de Google Ads."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Configurar respuesta simulada
        mock_campaign_service = MagicMock()
        mock_client.get_service.return_value = mock_campaign_service
        
        mock_mutate_response = MagicMock()
        mock_campaign_service.mutate_campaigns.return_value = mock_mutate_response
        mock_mutate_response.results = [MagicMock()]
        mock_mutate_response.results[0].resource_name = 'customers/1234567890/campaigns/9876543210'
        
        # Eliminar campaña
        result = delete_campaign(
            customer_id='1234567890',
            campaign_id='9876543210',
            developer_token='test_developer_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token'
        )
        
        # Verificar resultado
        assert result == 'customers/1234567890/campaigns/9876543210'
        
        # Verificar que se llamó al servicio de campañas
        mock_client.get_service.assert_called_with('CampaignService')
        
        # Verificar que se llamó a mutate_campaigns
        mock_campaign_service.mutate_campaigns.assert_called_once()
    
    @patch('adflux.google.ad_groups.GoogleAdsApiClient')
    def test_create_ad_group(self, mock_client_class):
        """Prueba la creación de un grupo de anuncios en Google Ads."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Configurar respuesta simulada
        mock_ad_group_service = MagicMock()
        mock_client.get_service.return_value = mock_ad_group_service
        
        mock_ad_group_operation = MagicMock()
        mock_client.get_type.return_value = mock_ad_group_operation
        
        mock_mutate_response = MagicMock()
        mock_ad_group_service.mutate_ad_groups.return_value = mock_mutate_response
        mock_mutate_response.results = [MagicMock()]
        mock_mutate_response.results[0].resource_name = 'customers/1234567890/adGroups/5555555555'
        
        # Crear grupo de anuncios
        result = create_ad_group(
            customer_id='1234567890',
            campaign_id='9876543210',
            name='Test Ad Group',
            status='PAUSED',
            type='SEARCH_STANDARD',
            cpc_bid_micros=1000000,  # $1.00
            developer_token='test_developer_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token'
        )
        
        # Verificar resultado
        assert result == 'customers/1234567890/adGroups/5555555555'
        
        # Verificar que se llamó al servicio de grupos de anuncios
        mock_client.get_service.assert_called_with('AdGroupService')
        
        # Verificar que se llamó a mutate_ad_groups
        mock_ad_group_service.mutate_ad_groups.assert_called_once()
    
    @patch('adflux.google.ads.GoogleAdsApiClient')
    def test_create_ad(self, mock_client_class):
        """Prueba la creación de un anuncio en Google Ads."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Configurar respuesta simulada
        mock_ad_service = MagicMock()
        mock_client.get_service.return_value = mock_ad_service
        
        mock_ad_operation = MagicMock()
        mock_client.get_type.return_value = mock_ad_operation
        
        mock_mutate_response = MagicMock()
        mock_ad_service.mutate_ads.return_value = mock_mutate_response
        mock_mutate_response.results = [MagicMock()]
        mock_mutate_response.results[0].resource_name = 'customers/1234567890/ads/6666666666'
        
        # Crear anuncio
        result = create_ad(
            customer_id='1234567890',
            ad_group_id='5555555555',
            headline_1='Test Headline 1',
            headline_2='Test Headline 2',
            headline_3='Test Headline 3',
            description_1='Test Description 1',
            description_2='Test Description 2',
            final_url='https://example.com',
            developer_token='test_developer_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token'
        )
        
        # Verificar resultado
        assert result == 'customers/1234567890/ads/6666666666'
        
        # Verificar que se llamó al servicio de anuncios
        mock_client.get_service.assert_called_with('AdService')
        
        # Verificar que se llamó a mutate_ads
        mock_ad_service.mutate_ads.assert_called_once()
