"""
Pruebas para el módulo de logging.
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask

from adflux.api.common.logging import log_info, log_warning, log_error, ApiLogger, get_logger


class TestLogging(unittest.TestCase):
    """
    Pruebas para las funciones de logging.
    """
    
    def setUp(self):
        """Crea una instancia de app para el contexto."""
        self.app = Flask(__name__)
        # Configurar un logger mock en la app para pruebas
        self.mock_logger = MagicMock()
        self.app.logger = self.mock_logger
    
    def test_log_info_with_app(self):
        """Prueba la función log_info con current_app disponible."""
        # Run within app context
        with self.app.app_context():
            log_info('Test message', 'TestModule')
        
        # Verificar que se llamó a logger.info con el mensaje correcto
        self.mock_logger.info.assert_called_once_with('[TestModule] Test message')
    
    @patch('builtins.print')
    def test_log_info_without_app(self, mock_print):
        """Prueba la función log_info sin current_app disponible."""
        # Llamar a la función
        log_info('Test message', 'TestModule')
        
        # Verificar que se llamó a print con el mensaje correcto
        mock_print.assert_called_once_with('INFO: [TestModule] Test message')
    
    def test_log_warning_with_app(self):
        """Prueba la función log_warning con current_app disponible."""
        # Run within app context
        with self.app.app_context():
            log_warning('Test message', 'TestModule')
        
        # Verificar que se llamó a logger.warning con el mensaje correcto
        self.mock_logger.warning.assert_called_once_with('[TestModule] Test message')
    
    @patch('builtins.print')
    def test_log_warning_without_app(self, mock_print):
        """Prueba la función log_warning sin current_app disponible."""
        # Llamar a la función
        log_warning('Test message', 'TestModule')
        
        # Verificar que se llamó a print con el mensaje correcto
        mock_print.assert_called_once_with('WARNING: [TestModule] Test message')
    
    def test_log_error_with_app(self):
        """Prueba la función log_error con current_app disponible."""
        # Run within app context
        with self.app.app_context():
            # Crear una excepción
            exception = Exception('Test exception')
            
            log_error('Test message', exception, 'TestModule')
        
        # Verificar que se llamó a logger.error con el mensaje correcto
        self.mock_logger.error.assert_called_once_with('[TestModule] Test message', exc_info=exception)
    
    @patch('builtins.print')
    def test_log_error_without_app(self, mock_print):
        """Prueba la función log_error sin current_app disponible."""
        # Crear una excepción
        exception = Exception('Test exception')
        
        # Llamar a la función
        log_error('Test message', exception, 'TestModule')
        
        # Verificar que se llamó a print con el mensaje correcto
        mock_print.assert_any_call('ERROR: [TestModule] Test message')
        mock_print.assert_any_call(f'Excepción: {exception}')


class TestApiLogger(unittest.TestCase):
    """
    Pruebas para la clase ApiLogger.
    """
    
    @patch('adflux.api.common.logging.log_info')
    def test_info(self, mock_log_info):
        """Prueba el método info."""
        # Crear logger
        logger = ApiLogger('TestModule')
        
        # Llamar al método
        logger.info('Test message')
        
        # Verificar que se llamó a log_info con los parámetros correctos
        mock_log_info.assert_called_once_with('Test message', 'TestModule')
    
    @patch('adflux.api.common.logging.log_warning')
    def test_warning(self, mock_log_warning):
        """Prueba el método warning."""
        # Crear logger
        logger = ApiLogger('TestModule')
        
        # Llamar al método
        logger.warning('Test message')
        
        # Verificar que se llamó a log_warning con los parámetros correctos
        mock_log_warning.assert_called_once_with('Test message', 'TestModule')
    
    @patch('adflux.api.common.logging.log_error')
    def test_error(self, mock_log_error):
        """Prueba el método error."""
        # Crear logger
        logger = ApiLogger('TestModule')
        
        # Crear una excepción
        exception = Exception('Test exception')
        
        # Llamar al método
        logger.error('Test message', exception)
        
        # Verificar que se llamó a log_error con los parámetros correctos
        mock_log_error.assert_called_once_with('Test message', exception, 'TestModule')


class TestGetLogger(unittest.TestCase):
    """
    Pruebas para la función get_logger.
    """
    
    def test_get_logger(self):
        """Prueba la función get_logger."""
        # Obtener logger
        logger = get_logger('TestModule')
        
        # Verificar que el logger es una instancia de ApiLogger
        self.assertIsInstance(logger, ApiLogger)
        
        # Verificar que el módulo es correcto
        self.assertEqual(logger.modulo, 'TestModule')


if __name__ == '__main__':
    unittest.main()
