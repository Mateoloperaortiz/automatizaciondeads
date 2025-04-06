"""
Pruebas para el cliente de Meta API.
"""

import unittest
from unittest.mock import patch, MagicMock

from adflux.api.meta.client import MetaApiClient, get_client


class TestMetaApiClient(unittest.TestCase):
    """
    Pruebas para la clase MetaApiClient.
    """
    
    @patch('adflux.api.meta.client.FacebookAdsApi')
    def test_initialize(self, mock_facebook_ads_api):
        """Prueba la inicialización del cliente."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_facebook_ads_api.init.return_value = mock_instance
        
        # Crear cliente con credenciales de prueba
        client = MetaApiClient(
            app_id='test_app_id',
            app_secret='test_app_secret',
            access_token='test_access_token'
        )
        
        # Inicializar el cliente
        result = client.initialize()
        
        # Verificar que se llamó a FacebookAdsApi.init con los parámetros correctos
        mock_facebook_ads_api.init.assert_called_once_with(
            'test_app_id',
            'test_app_secret',
            'test_access_token'
        )
        
        # Verificar que el resultado es el mock_instance
        self.assertEqual(result, mock_instance)
    
    @patch('adflux.api.meta.client.FacebookAdsApi')
    def test_get_api(self, mock_facebook_ads_api):
        """Prueba la obtención de la API."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_facebook_ads_api.init.return_value = mock_instance
        
        # Crear cliente con credenciales de prueba
        client = MetaApiClient(
            app_id='test_app_id',
            app_secret='test_app_secret',
            access_token='test_access_token'
        )
        
        # Obtener la API
        result = client.get_api()
        
        # Verificar que se llamó a FacebookAdsApi.init con los parámetros correctos
        mock_facebook_ads_api.init.assert_called_once_with(
            'test_app_id',
            'test_app_secret',
            'test_access_token'
        )
        
        # Verificar que el resultado es el mock_instance
        self.assertEqual(result, mock_instance)
        
        # Verificar que la segunda llamada no inicializa de nuevo
        mock_facebook_ads_api.init.reset_mock()
        result2 = client.get_api()
        mock_facebook_ads_api.init.assert_not_called()
        self.assertEqual(result2, mock_instance)
    
    @patch('adflux.api.meta.client.AdAccount')
    @patch('adflux.api.meta.client.FacebookAdsApi')
    def test_test_connection(self, mock_facebook_ads_api, mock_ad_account):
        """Prueba la conexión a la API."""
        # Configurar los mocks
        mock_api_instance = MagicMock()
        mock_facebook_ads_api.init.return_value = mock_api_instance
        
        mock_account_instance = MagicMock()
        mock_account_instance.get.return_value = 'Test Account'
        mock_ad_account.return_value = mock_account_instance
        
        # Crear cliente con credenciales de prueba
        client = MetaApiClient(
            app_id='test_app_id',
            app_secret='test_app_secret',
            access_token='test_access_token'
        )
        
        # Probar la conexión
        success, message, data = client.test_connection('act_123456789')
        
        # Verificar que se llamó a AdAccount con el ID correcto
        mock_ad_account.assert_called_once_with('act_123456789')
        
        # Verificar que se llamó a api_get
        mock_account_instance.api_get.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertIn('Test Account', message)
        self.assertEqual(data, {'account_name': 'Test Account'})
    
    @patch('adflux.api.meta.client.User')
    @patch('adflux.api.meta.client.FacebookAdsApi')
    def test_get_ad_accounts(self, mock_facebook_ads_api, mock_user):
        """Prueba la obtención de cuentas publicitarias."""
        # Configurar los mocks
        mock_api_instance = MagicMock()
        mock_facebook_ads_api.init.return_value = mock_api_instance
        
        mock_user_instance = MagicMock()
        mock_user.return_value = mock_user_instance
        
        mock_accounts = [
            {'id': 'act_123', 'name': 'Account 1', 'account_status': 1},
            {'id': 'act_456', 'name': 'Account 2', 'account_status': 2}
        ]
        mock_user_instance.get_ad_accounts.return_value = mock_accounts
        
        # Crear cliente con credenciales de prueba
        client = MetaApiClient(
            app_id='test_app_id',
            app_secret='test_app_secret',
            access_token='test_access_token'
        )
        
        # Obtener cuentas publicitarias
        success, message, accounts = client.get_ad_accounts()
        
        # Verificar que se llamó a User con 'me'
        mock_user.assert_called_once_with(fbid='me')
        
        # Verificar que se llamó a get_ad_accounts
        mock_user_instance.get_ad_accounts.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertEqual(len(accounts), 2)
        self.assertEqual(accounts[0]['id'], 'act_123')
        self.assertEqual(accounts[1]['name'], 'Account 2')


class TestGetClient(unittest.TestCase):
    """
    Pruebas para la función get_client.
    """
    
    @patch('adflux.api.meta.client.MetaApiClient')
    def test_get_client_with_credentials(self, mock_meta_api_client):
        """Prueba la obtención del cliente con credenciales."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_meta_api_client.return_value = mock_instance
        
        # Obtener cliente con credenciales
        client = get_client(
            app_id='test_app_id',
            app_secret='test_app_secret',
            access_token='test_access_token'
        )
        
        # Verificar que se llamó a MetaApiClient con los parámetros correctos
        mock_meta_api_client.assert_called_once_with(
            'test_app_id',
            'test_app_secret',
            'test_access_token'
        )
        
        # Verificar que el resultado es el mock_instance
        self.assertEqual(client, mock_instance)
    
    @patch('adflux.api.meta.client.MetaApiClient')
    def test_get_client_default(self, mock_meta_api_client):
        """Prueba la obtención del cliente por defecto."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_meta_api_client.return_value = mock_instance
        
        # Obtener cliente por defecto
        client1 = get_client()
        client2 = get_client()
        
        # Verificar que se llamó a MetaApiClient una sola vez
        mock_meta_api_client.assert_called_once_with()
        
        # Verificar que ambos clientes son el mismo
        self.assertEqual(client1, client2)


if __name__ == '__main__':
    unittest.main()
