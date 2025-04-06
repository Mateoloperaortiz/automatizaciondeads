"""
Pruebas para el módulo de manejo de errores.
"""

import unittest
from unittest.mock import patch, MagicMock

from adflux.api.common.error_handling import handle_meta_api_error, handle_google_ads_api_error, handle_gemini_api_error


class TestErrorHandling(unittest.TestCase):
    """
    Pruebas para los decoradores de manejo de errores.
    """
    
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_meta_api_error_success(self, mock_log_error):
        """Prueba el decorador handle_meta_api_error con éxito."""
        # Crear una función de prueba
        @handle_meta_api_error
        def test_function():
            return True, 'Success', {'data': 'test'}
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result, (True, 'Success', {'data': 'test'}))
        
        # Verificar que no se llamó a log_error
        mock_log_error.assert_not_called()
    
    @patch('adflux.api.common.error_handling.FacebookRequestError', MagicMock)
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_meta_api_error_facebook_error(self, mock_log_error):
        """Prueba el decorador handle_meta_api_error con error de Facebook."""
        # Crear una excepción de Facebook
        class MockFacebookRequestError(Exception):
            def __init__(self):
                self.api_error_code = 100
                self.api_error_message = 'Test error'
                self.api_error_type = 'Test type'
                self.http_status = 400
                self.body = {'error': {'message': 'Test error'}}
        
        # Crear una función de prueba
        @handle_meta_api_error
        def test_function():
            raise MockFacebookRequestError()
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result[0], False)
        self.assertIn('Test error', result[1])
        self.assertEqual(result[2], {})
        
        # Verificar que se llamó a log_error
        mock_log_error.assert_called_once()
    
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_meta_api_error_general_error(self, mock_log_error):
        """Prueba el decorador handle_meta_api_error con error general."""
        # Crear una función de prueba
        @handle_meta_api_error
        def test_function():
            raise Exception('Test error')
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result[0], False)
        self.assertIn('Test error', result[1])
        self.assertEqual(result[2], {})
        
        # Verificar que se llamó a log_error
        mock_log_error.assert_called_once()
    
    @patch('adflux.api.common.error_handling.GoogleAdsException', MagicMock)
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_google_ads_api_error_success(self, mock_log_error):
        """Prueba el decorador handle_google_ads_api_error con éxito."""
        # Crear una función de prueba
        @handle_google_ads_api_error
        def test_function():
            return {'success': True, 'message': 'Success', 'data': 'test'}
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result, {'success': True, 'message': 'Success', 'data': 'test'})
        
        # Verificar que no se llamó a log_error
        mock_log_error.assert_not_called()
    
    @patch('adflux.api.common.error_handling.GoogleAdsException', MagicMock)
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_google_ads_api_error_google_error(self, mock_log_error):
        """Prueba el decorador handle_google_ads_api_error con error de Google Ads."""
        # Crear una excepción de Google Ads
        class MockGoogleAdsException(Exception):
            def __init__(self):
                self.failure = MagicMock()
                self.failure.errors = [MagicMock()]
                self.failure.errors[0].message = 'Test error'
                self.failure.errors[0].error_code.name = 'Test code'
                self.request_id = '123456'
        
        # Crear una función de prueba
        @handle_google_ads_api_error
        def test_function():
            raise MockGoogleAdsException()
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result['success'], False)
        self.assertIn('Test error', result['message'])
        
        # Verificar que se llamó a log_error
        mock_log_error.assert_called_once()
    
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_google_ads_api_error_general_error(self, mock_log_error):
        """Prueba el decorador handle_google_ads_api_error con error general."""
        # Crear una función de prueba
        @handle_google_ads_api_error
        def test_function():
            raise Exception('Test error')
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result['success'], False)
        self.assertIn('Test error', result['message'])
        
        # Verificar que se llamó a log_error
        mock_log_error.assert_called_once()
    
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_gemini_api_error_success(self, mock_log_error):
        """Prueba el decorador handle_gemini_api_error con éxito."""
        # Crear una función de prueba
        @handle_gemini_api_error
        def test_function():
            return True, 'Success', {'data': 'test'}
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result, (True, 'Success', {'data': 'test'}))
        
        # Verificar que no se llamó a log_error
        mock_log_error.assert_not_called()
    
    @patch('adflux.api.common.error_handling.log_error')
    def test_handle_gemini_api_error_general_error(self, mock_log_error):
        """Prueba el decorador handle_gemini_api_error con error general."""
        # Crear una función de prueba
        @handle_gemini_api_error
        def test_function():
            raise Exception('Test error')
        
        # Llamar a la función
        result = test_function()
        
        # Verificar que el resultado es correcto
        self.assertEqual(result[0], False)
        self.assertIn('Test error', result[1])
        self.assertEqual(result[2], {})
        
        # Verificar que se llamó a log_error
        mock_log_error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
