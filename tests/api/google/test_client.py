"""
Pruebas para el cliente de Google Ads API.
"""

import unittest
from unittest.mock import patch, MagicMock

from adflux.api.google.client import GoogleAdsApiClient, get_client


class TestGoogleAdsApiClient(unittest.TestCase):
    """
    Pruebas para la clase GoogleAdsApiClient.
    """
    
    def setUp(self):
        """Configuración para las pruebas."""
        # Crear cliente con credenciales de prueba
        self.client = GoogleAdsApiClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            developer_token='test_developer_token',
            refresh_token='test_refresh_token',
            login_customer_id='test_login_customer_id'
        )
    
    @patch('adflux.api.google.client.GoogleAdsClient')
    def test_initialize(self, mock_google_ads_client):
        """Prueba la inicialización del cliente."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_google_ads_client.load_from_dict.return_value = mock_instance
        
        # Inicializar el cliente
        result = self.client.initialize()
        
        # Verificar que se llamó a GoogleAdsClient.load_from_dict con los parámetros correctos
        mock_google_ads_client.load_from_dict.assert_called_once()
        args, kwargs = mock_google_ads_client.load_from_dict.call_args
        config = args[0]
        self.assertEqual(config['developer_token'], 'test_developer_token')
        self.assertEqual(config['client_id'], 'test_client_id')
        self.assertEqual(config['client_secret'], 'test_client_secret')
        self.assertEqual(config['refresh_token'], 'test_refresh_token')
        self.assertEqual(config['login_customer_id'], 'test_login_customer_id')
        self.assertTrue(config['use_proto_plus'])
        
        # Verificar que el resultado es el mock_instance
        self.assertEqual(result, mock_instance)
    
    @patch('adflux.api.google.client.GoogleAdsClient')
    def test_initialize_with_config_path(self, mock_google_ads_client):
        """Prueba la inicialización del cliente con ruta de configuración."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_google_ads_client.load_from_storage.return_value = mock_instance
        
        # Crear cliente con ruta de configuración
        client = GoogleAdsApiClient(config_path='/ruta/a/config.yaml')
        
        # Configurar el mock para que os.path.exists devuelva True
        with patch('os.path.exists', return_value=True):
            # Inicializar el cliente
            result = client.initialize()
            
            # Verificar que se llamó a GoogleAdsClient.load_from_storage con los parámetros correctos
            mock_google_ads_client.load_from_storage.assert_called_once_with('/ruta/a/config.yaml')
            
            # Verificar que el resultado es el mock_instance
            self.assertEqual(result, mock_instance)
    
    @patch('adflux.api.google.client.GoogleAdsClient')
    def test_get_client(self, mock_google_ads_client):
        """Prueba la obtención del cliente."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_google_ads_client.load_from_dict.return_value = mock_instance
        
        # Obtener el cliente
        result = self.client.get_client()
        
        # Verificar que se llamó a GoogleAdsClient.load_from_dict con los parámetros correctos
        mock_google_ads_client.load_from_dict.assert_called_once()
        
        # Verificar que el resultado es el mock_instance
        self.assertEqual(result, mock_instance)
        
        # Verificar que la segunda llamada no inicializa de nuevo
        mock_google_ads_client.load_from_dict.reset_mock()
        result2 = self.client.get_client()
        mock_google_ads_client.load_from_dict.assert_not_called()
        self.assertEqual(result2, mock_instance)
    
    @patch('adflux.api.google.client.GoogleAdsClient')
    def test_test_connection(self, mock_google_ads_client):
        """Prueba la conexión a la API."""
        # Configurar los mocks
        mock_client_instance = MagicMock()
        mock_google_ads_client.load_from_dict.return_value = mock_client_instance
        
        mock_service = MagicMock()
        mock_client_instance.get_service.return_value = mock_service
        
        # Configurar el mock para la respuesta de la consulta
        mock_row = MagicMock()
        mock_customer = MagicMock()
        mock_customer.id = '123456789'
        mock_customer.descriptive_name = 'Test Account'
        mock_customer.currency_code = 'USD'
        mock_row.customer = mock_customer
        mock_service.search.return_value = [mock_row]
        
        # Inicializar el cliente
        self.client.initialize()
        
        # Probar la conexión
        result = self.client.test_connection('123456789')
        
        # Verificar que se llamó a get_service con el parámetro correcto
        mock_client_instance.get_service.assert_called_once_with("GoogleAdsService")
        
        # Verificar que se llamó a search con los parámetros correctos
        mock_service.search.assert_called_once()
        args, kwargs = mock_service.search.call_args
        self.assertEqual(kwargs['customer_id'], '123456789')
        
        # Verificar el resultado
        self.assertTrue(result['success'])
        self.assertIn('Test Account', result['message'])
        self.assertEqual(result['data']['customer_id'], '123456789')
        self.assertEqual(result['data']['descriptive_name'], 'Test Account')
        self.assertEqual(result['data']['currency_code'], 'USD')
    
    @patch('adflux.api.google.client.GoogleAdsClient')
    def test_create_config_file(self, mock_google_ads_client):
        """Prueba la creación de un archivo de configuración."""
        # Configurar el mock para open
        mock_open = unittest.mock.mock_open()
        
        # Crear cliente con credenciales de prueba
        client = GoogleAdsApiClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            developer_token='test_developer_token',
            refresh_token='test_refresh_token',
            login_customer_id='test_login_customer_id'
        )
        
        # Crear archivo de configuración
        with patch('builtins.open', mock_open):
            success, message = client.create_config_file('/ruta/a/config.yaml')
        
        # Verificar que se llamó a open con los parámetros correctos
        mock_open.assert_called_once_with('/ruta/a/config.yaml', 'w')
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertIn('/ruta/a/config.yaml', message)


class TestGetClient(unittest.TestCase):
    """
    Pruebas para la función get_client.
    """
    
    @patch('adflux.api.google.client.GoogleAdsApiClient')
    def test_get_client_with_credentials(self, mock_google_ads_api_client):
        """Prueba la obtención del cliente con credenciales."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_google_ads_api_client.return_value = mock_instance
        
        # Obtener cliente con credenciales
        client = get_client(
            client_id='test_client_id',
            client_secret='test_client_secret',
            developer_token='test_developer_token',
            refresh_token='test_refresh_token',
            login_customer_id='test_login_customer_id'
        )
        
        # Verificar que se llamó a GoogleAdsApiClient con los parámetros correctos
        mock_google_ads_api_client.assert_called_once_with(
            'test_client_id',
            'test_client_secret',
            'test_developer_token',
            'test_refresh_token',
            'test_login_customer_id',
            None
        )
        
        # Verificar que el resultado es el mock_instance
        self.assertEqual(client, mock_instance)
    
    @patch('adflux.api.google.client.GoogleAdsApiClient')
    def test_get_client_default(self, mock_google_ads_api_client):
        """Prueba la obtención del cliente por defecto."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_google_ads_api_client.return_value = mock_instance
        
        # Obtener cliente por defecto
        client1 = get_client()
        client2 = get_client()
        
        # Verificar que se llamó a GoogleAdsApiClient una sola vez
        mock_google_ads_api_client.assert_called_once_with()
        
        # Verificar que ambos clientes son el mismo
        self.assertEqual(client1, client2)


if __name__ == '__main__':
    unittest.main()
