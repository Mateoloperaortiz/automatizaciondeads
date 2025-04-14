"""
Módulo de seguridad para AdFlux.

Este módulo proporciona funcionalidades para la seguridad de la aplicación,
incluyendo encriptación, sanitización de datos y configuración de seguridad.
"""

from .encryption import encrypt, decrypt, hash_password, verify_password, generate_key
from .sanitization import sanitize_html, sanitize_filename, sanitize_input
from .headers import setup_security_headers
from .cors import setup_cors
from .rate_limiting import setup_rate_limiting, rate_limit
from .secrets import get_secret, set_secret, rotate_secret

__all__ = [
    'encrypt',
    'decrypt',
    'hash_password',
    'verify_password',
    'generate_key',
    'sanitize_html',
    'sanitize_filename',
    'sanitize_input',
    'setup_security_headers',
    'setup_cors',
    'setup_rate_limiting',
    'rate_limit',
    'get_secret',
    'set_secret',
    'rotate_secret'
]
