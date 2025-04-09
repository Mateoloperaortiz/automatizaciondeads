"""
Pruebas para el cliente de Gemini API.
"""

import unittest
from unittest.mock import patch, MagicMock
import os

from adflux.api.gemini.client import GeminiApiClient, get_client
from adflux.api.common.excepciones import AdFluxError, ErrorAPI


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
        # Should not raise
        result = self.client.initialize()
        self.assertTrue(result)
        self.assertTrue(self.client.initialized)
    
    def test_initialize_no_api_key(self):
        """Prueba la inicialización del cliente sin clave de API."""
        # Patch os.getenv specifically for this test
        with patch('adflux.api.gemini.client.os.getenv', return_value=None) as mock_getenv:
            client = GeminiApiClient(api_key=None)

            # Expect AdFluxError because api_key is missing
            with self.assertRaises(AdFluxError) as cm:
                client.initialize()

            # Check the specific error message
            self.assertIn("No se proporcionó una clave de API para Google Gemini", cm.exception.mensaje)

            # Verify initialization state wasn't set
            self.assertFalse(client.initialized)

            # Verify os.getenv was called for GEMINI_API_KEY
            mock_getenv.assert_any_call("GEMINI_API_KEY")
    
    @patch('adflux.api.gemini.client.genai')
    def test_ensure_initialized_logic(self, mock_genai):
        """Prueba la lógica de ensure_initialized (primera y segunda llamada)."""
        # Primera llamada (no inicializado)
        self.client.initialized = False
        self.client.ensure_initialized() # No debe lanzar error
        mock_genai.configure.assert_called_once_with(api_key='test_api_key')
        self.assertTrue(self.client.initialized)

        # Segunda llamada (ya inicializado)
        mock_genai.configure.reset_mock()
        self.client.ensure_initialized() # No debe lanzar error
        mock_genai.configure.assert_not_called() # No debe llamar de nuevo

    @patch('adflux.api.gemini.client.genai')
    def test_test_connection(self, mock_genai):
        """Prueba la conexión a la API."""
        # Configurar los mocks
        mock_model1 = MagicMock()
        mock_model1.name = 'gemini-pro'
        mock_model2 = MagicMock()
        mock_model2.name = 'gemini-vision-pro'
        mock_genai.list_models.return_value = [mock_model1, mock_model2]
        
        # Inicializar el cliente (simulado)
        self.client.initialized = True
        
        # Probar la conexión (should call ensure_initialized which does nothing)
        success, message, data = self.client.test_connection()
        
        # Verificar que se llamó a genai.list_models
        mock_genai.list_models.assert_called_once()
        
        # Verificar el resultado (devuelve tupla en éxito)
        self.assertTrue(success)
        self.assertIn('2', message)
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
