"""
Pruebas de integración para el módulo de API de AdFlux.

Estas pruebas verifican que los diferentes componentes del módulo de API
funcionan correctamente en conjunto.
"""

import unittest
from unittest.mock import patch, MagicMock

from adflux.api import get_meta_client, get_google_client, get_gemini_client
from adflux.api import MetaCampaignManager, GoogleCampaignManager, ContentGenerator


class TestMetaApiIntegration(unittest.TestCase):
    """
    Pruebas de integración para la API de Meta.
    """
    
    @patch('adflux.api.meta.client.FacebookAdsApi')
    def setUp(self, mock_facebook_ads_api):
        """Configuración para las pruebas."""
        # Configurar el mock
        self.mock_api = MagicMock()
        mock_facebook_ads_api.init.return_value = self.mock_api
        
        # Crear cliente
        self.client = get_meta_client()
        
        # Crear gestor de campañas
        self.campaign_manager = MetaCampaignManager(self.client)
    
    @patch('adflux.api.meta.campaigns.AdAccount')
    def test_create_campaign_flow(self, mock_ad_account):
        """Prueba el flujo completo de creación de una campaña."""
        # Configurar los mocks
        mock_account_instance = MagicMock()
        mock_ad_account.return_value = mock_account_instance
        
        mock_campaign = MagicMock()
        mock_campaign.get.side_effect = lambda field: {
            'id': '123456789',
            'name': 'Test Campaign',
            'status': 'PAUSED',
            'objective': 'LINK_CLICKS'
        }.get(field)
        
        mock_account_instance.create_campaign.return_value = mock_campaign
        
        # Crear campaña
        success, message, campaign_data = self.campaign_manager.create_campaign(
            ad_account_id='act_123456789',
            name='Test Campaign',
            objective='LINK_CLICKS',
            status='PAUSED'
        )
        
        # Verificar que se llamó a AdAccount con el ID correcto
        mock_ad_account.assert_called_once_with('act_123456789')
        
        # Verificar que se llamó a create_campaign
        mock_account_instance.create_campaign.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertEqual(campaign_data['id'], '123456789')
        self.assertEqual(campaign_data['name'], 'Test Campaign')
        self.assertEqual(campaign_data['status'], 'PAUSED')
        self.assertEqual(campaign_data['objective'], 'LINK_CLICKS')


class TestGoogleAdsApiIntegration(unittest.TestCase):
    """
    Pruebas de integración para la API de Google Ads.
    """
    
    @patch('adflux.api.google.client.GoogleAdsClient')
    def setUp(self, mock_google_ads_client):
        """Configuración para las pruebas."""
        # Configurar el mock
        self.mock_client_instance = MagicMock()
        mock_google_ads_client.load_from_dict.return_value = self.mock_client_instance
        
        # Crear cliente
        self.client = get_google_client()
        
        # Crear gestor de campañas
        self.campaign_manager = GoogleCampaignManager(self.client)
    
    def test_create_campaign_flow(self):
        """Prueba el flujo completo de creación de una campaña."""
        # Configurar los mocks
        self.mock_client_instance.enums.CampaignStatusEnum.PAUSED = 'PAUSED'
        
        mock_campaign_service = MagicMock()
        self.mock_client_instance.get_service.return_value = mock_campaign_service
        
        mock_campaign_budget_operation = MagicMock()
        mock_campaign_operation = MagicMock()
        mock_ad_group_operation = MagicMock()
        
        self.mock_client_instance.get_type.side_effect = lambda type_name: {
            'CampaignBudgetOperation': mock_campaign_budget_operation,
            'CampaignOperation': mock_campaign_operation,
            'AdGroupOperation': mock_ad_group_operation
        }.get(type_name)
        
        mock_campaign_budget_response = MagicMock()
        mock_campaign_budget_response.results = [MagicMock()]
        mock_campaign_budget_response.results[0].resource_name = 'customers/123456789/campaignBudgets/1234567890'
        
        mock_campaign_response = MagicMock()
        mock_campaign_response.results = [MagicMock()]
        mock_campaign_response.results[0].resource_name = 'customers/123456789/campaigns/1234567890'
        
        mock_ad_group_response = MagicMock()
        mock_ad_group_response.results = [MagicMock()]
        mock_ad_group_response.results[0].resource_name = 'customers/123456789/adGroups/1234567890'
        
        mock_campaign_service.mutate_campaign_budgets.return_value = mock_campaign_budget_response
        mock_campaign_service.mutate_campaigns.return_value = mock_campaign_response
        mock_campaign_service.mutate_ad_groups.return_value = mock_ad_group_response
        
        mock_campaign_service.parse_campaign_path.return_value = {'campaign_id': '1234567890'}
        mock_campaign_service.parse_campaign_budget_path.return_value = {'campaign_budget_id': '1234567890'}
        mock_campaign_service.parse_ad_group_path.return_value = {'ad_group_id': '1234567890'}
        
        # Crear campaña
        result = self.campaign_manager.create_campaign(
            customer_id='123456789',
            name='Test Campaign',
            daily_budget_micros=1000000,
            status='PAUSED'
        )
        
        # Verificar que se llamó a get_service
        self.mock_client_instance.get_service.assert_called()
        
        # Verificar que se llamó a mutate_campaign_budgets
        mock_campaign_service.mutate_campaign_budgets.assert_called_once()
        
        # Verificar que se llamó a mutate_campaigns
        mock_campaign_service.mutate_campaigns.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(result['success'])
        self.assertEqual(result['external_ids']['campaign_id'], '1234567890')
        self.assertEqual(result['external_ids']['ad_group_id'], '1234567890')
        self.assertEqual(result['external_ids']['budget_id'], '1234567890')


class TestGeminiApiIntegration(unittest.TestCase):
    """
    Pruebas de integración para la API de Gemini.
    """
    
    @patch('adflux.api.gemini.client.genai')
    def setUp(self, mock_genai):
        """Configuración para las pruebas."""
        # Configurar el mock
        mock_genai.configure.return_value = None
        
        # Crear cliente
        self.client = get_gemini_client('test_api_key')
        self.client.initialized = True
        
        # Crear generador de contenido
        self.content_generator = ContentGenerator(self.client)
    
    @patch('adflux.api.gemini.content_generation.genai.GenerativeModel')
    def test_generate_ad_creative_flow(self, mock_generative_model):
        """Prueba el flujo completo de generación de contenido creativo."""
        # Configurar los mocks
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = """
        {
            "primary_headline": "Desarrollador Python",
            "secondary_headline": "Únete a nuestro equipo",
            "primary_description": "Buscamos talento en Flask y SQLAlchemy",
            "secondary_description": "Trabaja en proyectos innovadores",
            "call_to_action": "Aplica ahora"
        }
        """
        mock_model_instance.generate_content.return_value = mock_response
        
        # Generar contenido creativo
        success, message, creative = self.content_generator.generate_ad_creative(
            job_title='Desarrollador Python',
            job_description='Buscamos un desarrollador Python con experiencia en Flask y SQLAlchemy.',
            target_audience='profesionales de tecnología'
        )
        
        # Verificar que se llamó a GenerativeModel
        mock_generative_model.assert_called_once()
        
        # Verificar que se llamó a generate_content
        mock_model_instance.generate_content.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertEqual(creative['primary_headline'], 'Desarrollador Python')
        self.assertEqual(creative['secondary_headline'], 'Únete a nuestro equipo')
        self.assertEqual(creative['primary_description'], 'Buscamos talento en Flask y SQLAlchemy')
        self.assertEqual(creative['secondary_description'], 'Trabaja en proyectos innovadores')
        self.assertEqual(creative['call_to_action'], 'Aplica ahora')


if __name__ == '__main__':
    unittest.main()
