"""
Pruebas para el cliente de Gemini API.
"""

import unittest
from unittest.mock import patch, MagicMock

from adflux.api.gemini.client import GeminiApiClient, get_client


class TestGeminiApiClient(unittest.TestCase):
    """
    Pruebas para la clase GeminiApiClient.
    """
    
    def setUp(self):
        """Configuración para las pruebas."""
        # Crear cliente con clave de API de prueba
        self.client = GeminiApiClient('test_api_key')
    
    @patch('adflux.api.gemini.client.genai')
    def test_initialize(self, mock_genai):
        """Prueba la inicialización del cliente."""
        # Inicializar el cliente
        result = self.client.initialize()
        
        # Verificar que se llamó a genai.configure con los parámetros correctos
        mock_genai.configure.assert_called_once_with(api_key='test_api_key')
        
        # Verificar que el resultado es True
        self.assertTrue(result)
        
        # Verificar que initialized es True
        self.assertTrue(self.client.initialized)
    
    @patch('adflux.api.gemini.client.genai')
    def test_initialize_no_api_key(self, mock_genai):
        """Prueba la inicialización del cliente sin clave de API."""
        # Crear cliente sin clave de API
        client = GeminiApiClient()
        
        # Inicializar el cliente
        result = client.initialize()
        
        # Verificar que no se llamó a genai.configure
        mock_genai.configure.assert_not_called()
        
        # Verificar que el resultado es False
        self.assertFalse(result)
        
        # Verificar que initialized es False
        self.assertFalse(client.initialized)
    
    @patch('adflux.api.gemini.client.genai')
    def test_ensure_initialized(self, mock_genai):
        """Prueba la función ensure_initialized."""
        # Configurar el mock
        mock_genai.configure.return_value = None
        
        # Llamar a ensure_initialized
        result = self.client.ensure_initialized()
        
        # Verificar que se llamó a genai.configure con los parámetros correctos
        mock_genai.configure.assert_called_once_with(api_key='test_api_key')
        
        # Verificar que el resultado es True
        self.assertTrue(result)
        
        # Verificar que initialized es True
        self.assertTrue(self.client.initialized)
        
        # Verificar que la segunda llamada no inicializa de nuevo
        mock_genai.configure.reset_mock()
        result2 = self.client.ensure_initialized()
        mock_genai.configure.assert_not_called()
        self.assertTrue(result2)
    
    @patch('adflux.api.gemini.client.genai')
    def test_test_connection(self, mock_genai):
        """Prueba la conexión a la API."""
        # Configurar los mocks
        mock_model1 = MagicMock()
        mock_model1.name = 'gemini-pro'
        mock_model2 = MagicMock()
        mock_model2.name = 'gemini-vision-pro'
        mock_genai.list_models.return_value = [mock_model1, mock_model2]
        
        # Inicializar el cliente
        self.client.initialized = True
        
        # Probar la conexión
        success, message, data = self.client.test_connection()
        
        # Verificar que se llamó a genai.list_models
        mock_genai.list_models.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertIn('2', message)  # 2 modelos disponibles
        self.assertEqual(data['models'], ['gemini-pro', 'gemini-vision-pro'])
    
    @patch('adflux.api.gemini.client.genai')
    def test_test_connection_no_models(self, mock_genai):
        """Prueba la conexión a la API sin modelos disponibles."""
        # Configurar los mocks
        mock_genai.list_models.return_value = []
        
        # Inicializar el cliente
        self.client.initialized = True
        
        # Probar la conexión
        success, message, data = self.client.test_connection()
        
        # Verificar que se llamó a genai.list_models
        mock_genai.list_models.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertIn('no se encontraron', message.lower())
        self.assertEqual(data['models'], [])
    
    @patch('adflux.api.gemini.client.genai')
    def test_test_connection_not_initialized(self, mock_genai):
        """Prueba la conexión a la API sin inicializar."""
        # Configurar los mocks para que ensure_initialized devuelva False
        self.client.initialized = False
        mock_genai.configure.return_value = None
        
        # Probar la conexión
        success, message, data = self.client.test_connection()
        
        # Verificar que se llamó a genai.configure
        mock_genai.configure.assert_called_once_with(api_key='test_api_key')
        
        # Verificar que se llamó a genai.list_models
        mock_genai.list_models.assert_called_once()
        
        # Verificar que initialized es True
        self.assertTrue(self.client.initialized)
    
    @patch('adflux.api.gemini.client.genai')
    def test_get_available_models(self, mock_genai):
        """Prueba la obtención de modelos disponibles."""
        # Configurar los mocks
        mock_model1 = MagicMock()
        mock_model1.name = 'gemini-pro'
        mock_model1.display_name = 'Gemini Pro'
        mock_model1.description = 'A large language model for text generation'
        mock_model1.input_token_limit = 30720
        mock_model1.output_token_limit = 2048
        mock_model1.supported_generation_methods = ['generateContent', 'countTokens']
        
        mock_model2 = MagicMock()
        mock_model2.name = 'gemini-vision-pro'
        mock_model2.display_name = 'Gemini Vision Pro'
        mock_model2.description = 'A large language model for text and image generation'
        mock_model2.input_token_limit = 12288
        mock_model2.output_token_limit = 4096
        mock_model2.supported_generation_methods = ['generateContent', 'countTokens']
        
        mock_genai.list_models.return_value = [mock_model1, mock_model2]
        
        # Inicializar el cliente
        self.client.initialized = True
        
        # Obtener modelos disponibles
        success, message, models = self.client.get_available_models()
        
        # Verificar que se llamó a genai.list_models
        mock_genai.list_models.assert_called_once()
        
        # Verificar el resultado
        self.assertTrue(success)
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]['name'], 'gemini-pro')
        self.assertEqual(models[0]['display_name'], 'Gemini Pro')
        self.assertEqual(models[0]['description'], 'A large language model for text generation')
        self.assertEqual(models[0]['input_token_limit'], 30720)
        self.assertEqual(models[0]['output_token_limit'], 2048)
        self.assertEqual(models[0]['supported_generation_methods'], ['generateContent', 'countTokens'])
        self.assertEqual(models[1]['name'], 'gemini-vision-pro')
        self.assertEqual(models[1]['display_name'], 'Gemini Vision Pro')
        self.assertEqual(models[1]['description'], 'A large language model for text and image generation')
        self.assertEqual(models[1]['input_token_limit'], 12288)
        self.assertEqual(models[1]['output_token_limit'], 4096)
        self.assertEqual(models[1]['supported_generation_methods'], ['generateContent', 'countTokens'])


class TestGetClient(unittest.TestCase):
    """
    Pruebas para la función get_client.
    """
    
    @patch('adflux.api.gemini.client.GeminiApiClient')
    def test_get_client_with_api_key(self, mock_gemini_api_client):
        """Prueba la obtención del cliente con clave de API."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_gemini_api_client.return_value = mock_instance
        
        # Obtener cliente con clave de API
        client = get_client('test_api_key')
        
        # Verificar que se llamó a GeminiApiClient con los parámetros correctos
        mock_gemini_api_client.assert_called_once_with('test_api_key')
        
        # Verificar que el resultado es el mock_instance
        self.assertEqual(client, mock_instance)
    
    @patch('adflux.api.gemini.client.GeminiApiClient')
    def test_get_client_default(self, mock_gemini_api_client):
        """Prueba la obtención del cliente por defecto."""
        # Configurar el mock
        mock_instance = MagicMock()
        mock_gemini_api_client.return_value = mock_instance
        
        # Obtener cliente por defecto
        client1 = get_client()
        client2 = get_client()
        
        # Verificar que se llamó a GeminiApiClient una sola vez
        mock_gemini_api_client.assert_called_once_with()
        
        # Verificar que ambos clientes son el mismo
        self.assertEqual(client1, client2)


if __name__ == '__main__':
    unittest.main()
