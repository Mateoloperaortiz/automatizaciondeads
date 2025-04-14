"""
Pruebas de integración para la API de Meta en AdFlux.

Este módulo contiene pruebas para verificar la integración con la API de Meta.
"""

import pytest
import json
import responses
from unittest.mock import patch, MagicMock

from adflux.meta.client import MetaApiClient
from adflux.meta.campaigns import create_campaign, get_campaign, update_campaign, delete_campaign
from adflux.meta.ad_sets import create_ad_set, get_ad_set, update_ad_set, delete_ad_set
from adflux.meta.ads import create_ad, get_ad, update_ad, delete_ad
from adflux.meta.insights import get_campaign_insights, get_ad_set_insights, get_ad_insights


@pytest.mark.integration
class TestMetaApi:
    """Pruebas para la API de Meta."""
    
    @responses.activate
    def test_meta_api_client(self):
        """Prueba el cliente de la API de Meta."""
        # Configurar respuesta simulada
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/me',
            json={'id': '123456789', 'name': 'Test User'},
            status=200
        )
        
        # Crear cliente
        client = MetaApiClient(
            app_id='test_app_id',
            app_secret='test_app_secret',
            access_token='test_access_token'
        )
        
        # Hacer solicitud
        response = client.get('me')
        
        # Verificar respuesta
        assert response['id'] == '123456789'
        assert response['name'] == 'Test User'
        
        # Verificar que se usó el token de acceso
        assert 'Authorization' in responses.calls[0].request.headers
        assert 'Bearer test_access_token' in responses.calls[0].request.headers['Authorization']
    
    @responses.activate
    def test_create_campaign(self):
        """Prueba la creación de una campaña en Meta."""
        # Configurar respuesta simulada
        responses.add(
            responses.POST,
            'https://graph.facebook.com/v18.0/act_123456789/campaigns',
            json={'id': '987654321'},
            status=200
        )
        
        # Crear campaña
        campaign_data = {
            'name': 'Test Campaign',
            'objective': 'BRAND_AWARENESS',
            'status': 'PAUSED',
            'special_ad_categories': [],
            'daily_budget': 1000  # En centavos
        }
        
        result = create_campaign(
            account_id='123456789',
            name=campaign_data['name'],
            objective=campaign_data['objective'],
            status=campaign_data['status'],
            special_ad_categories=campaign_data['special_ad_categories'],
            daily_budget=campaign_data['daily_budget'],
            access_token='test_access_token'
        )
        
        # Verificar resultado
        assert result['id'] == '987654321'
        
        # Verificar solicitud
        assert responses.calls[0].request.url == 'https://graph.facebook.com/v18.0/act_123456789/campaigns'
        
        # Verificar datos enviados
        request_data = json.loads(responses.calls[0].request.body)
        assert request_data['name'] == 'Test Campaign'
        assert request_data['objective'] == 'BRAND_AWARENESS'
        assert request_data['status'] == 'PAUSED'
        assert request_data['daily_budget'] == '1000'
    
    @responses.activate
    def test_get_campaign(self):
        """Prueba la obtención de una campaña de Meta."""
        # Configurar respuesta simulada
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/987654321',
            json={
                'id': '987654321',
                'name': 'Test Campaign',
                'objective': 'BRAND_AWARENESS',
                'status': 'PAUSED'
            },
            status=200
        )
        
        # Obtener campaña
        result = get_campaign(
            campaign_id='987654321',
            fields=['id', 'name', 'objective', 'status'],
            access_token='test_access_token'
        )
        
        # Verificar resultado
        assert result['id'] == '987654321'
        assert result['name'] == 'Test Campaign'
        assert result['objective'] == 'BRAND_AWARENESS'
        assert result['status'] == 'PAUSED'
        
        # Verificar solicitud
        assert responses.calls[0].request.url.startswith('https://graph.facebook.com/v18.0/987654321')
        assert 'fields=id%2Cname%2Cobjective%2Cstatus' in responses.calls[0].request.url
    
    @responses.activate
    def test_update_campaign(self):
        """Prueba la actualización de una campaña de Meta."""
        # Configurar respuesta simulada
        responses.add(
            responses.POST,
            'https://graph.facebook.com/v18.0/987654321',
            json={'success': True},
            status=200
        )
        
        # Actualizar campaña
        result = update_campaign(
            campaign_id='987654321',
            name='Updated Campaign',
            status='ACTIVE',
            access_token='test_access_token'
        )
        
        # Verificar resultado
        assert result['success'] is True
        
        # Verificar solicitud
        assert responses.calls[0].request.url == 'https://graph.facebook.com/v18.0/987654321'
        
        # Verificar datos enviados
        request_data = json.loads(responses.calls[0].request.body)
        assert request_data['name'] == 'Updated Campaign'
        assert request_data['status'] == 'ACTIVE'
    
    @responses.activate
    def test_delete_campaign(self):
        """Prueba la eliminación de una campaña de Meta."""
        # Configurar respuesta simulada
        responses.add(
            responses.DELETE,
            'https://graph.facebook.com/v18.0/987654321',
            json={'success': True},
            status=200
        )
        
        # Eliminar campaña
        result = delete_campaign(
            campaign_id='987654321',
            access_token='test_access_token'
        )
        
        # Verificar resultado
        assert result['success'] is True
        
        # Verificar solicitud
        assert responses.calls[0].request.url == 'https://graph.facebook.com/v18.0/987654321'
        assert responses.calls[0].request.method == 'DELETE'
    
    @responses.activate
    def test_create_ad_set(self):
        """Prueba la creación de un conjunto de anuncios en Meta."""
        # Configurar respuesta simulada
        responses.add(
            responses.POST,
            'https://graph.facebook.com/v18.0/act_123456789/adsets',
            json={'id': '123456'},
            status=200
        )
        
        # Crear conjunto de anuncios
        result = create_ad_set(
            account_id='123456789',
            name='Test Ad Set',
            campaign_id='987654321',
            daily_budget=500,
            bid_amount=100,
            billing_event='IMPRESSIONS',
            optimization_goal='REACH',
            targeting={'age_min': 18, 'age_max': 65, 'genders': [1, 2]},
            status='PAUSED',
            access_token='test_access_token'
        )
        
        # Verificar resultado
        assert result['id'] == '123456'
        
        # Verificar solicitud
        assert responses.calls[0].request.url == 'https://graph.facebook.com/v18.0/act_123456789/adsets'
        
        # Verificar datos enviados
        request_data = json.loads(responses.calls[0].request.body)
        assert request_data['name'] == 'Test Ad Set'
        assert request_data['campaign_id'] == '987654321'
        assert request_data['daily_budget'] == '500'
        assert request_data['bid_amount'] == '100'
        assert request_data['billing_event'] == 'IMPRESSIONS'
        assert request_data['optimization_goal'] == 'REACH'
        assert request_data['targeting']['age_min'] == 18
        assert request_data['targeting']['age_max'] == 65
        assert request_data['targeting']['genders'] == [1, 2]
        assert request_data['status'] == 'PAUSED'
    
    @responses.activate
    def test_get_campaign_insights(self):
        """Prueba la obtención de insights de una campaña de Meta."""
        # Configurar respuesta simulada
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/987654321/insights',
            json={
                'data': [
                    {
                        'date_start': '2023-01-01',
                        'date_stop': '2023-01-07',
                        'impressions': '1000',
                        'clicks': '50',
                        'spend': '100.00'
                    }
                ],
                'paging': {
                    'cursors': {
                        'before': 'before_cursor',
                        'after': 'after_cursor'
                    }
                }
            },
            status=200
        )
        
        # Obtener insights
        result = get_campaign_insights(
            campaign_id='987654321',
            fields=['impressions', 'clicks', 'spend'],
            date_preset='last_7d',
            access_token='test_access_token'
        )
        
        # Verificar resultado
        assert 'data' in result
        assert len(result['data']) == 1
        assert result['data'][0]['impressions'] == '1000'
        assert result['data'][0]['clicks'] == '50'
        assert result['data'][0]['spend'] == '100.00'
        
        # Verificar solicitud
        assert responses.calls[0].request.url.startswith('https://graph.facebook.com/v18.0/987654321/insights')
        assert 'fields=impressions%2Cclicks%2Cspend' in responses.calls[0].request.url
        assert 'date_preset=last_7d' in responses.calls[0].request.url
