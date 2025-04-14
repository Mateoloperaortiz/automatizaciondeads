"""
Pruebas para encriptación y seguridad de datos en AdFlux.

Este módulo contiene pruebas para verificar las funcionalidades de encriptación
y seguridad de datos implementadas en AdFlux.
"""

import pytest
from unittest.mock import patch

from adflux.security.encryption import (
    encrypt, decrypt, hash_password, verify_password, generate_key, EncryptedField
)
from adflux.security.sanitization import (
    sanitize_html, sanitize_filename, sanitize_input, sanitize_sql_like,
    sanitize_json, sanitize_url, sanitize_email, sanitize_phone
)
from adflux.security.secrets import (
    get_secret, set_secret, delete_secret, rotate_secret, Secret
)


@pytest.mark.security
class TestEncryption:
    """Pruebas para funcionalidades de encriptación."""
    
    def test_encrypt_decrypt(self):
        """Prueba la encriptación y desencriptación de datos."""
        # Datos a encriptar
        data = "datos sensibles"
        
        # Encriptar datos
        encrypted_data, key = encrypt(data)
        
        # Verificar que los datos están encriptados
        assert encrypted_data != data.encode()
        
        # Desencriptar datos
        decrypted_data = decrypt(encrypted_data, key)
        
        # Verificar que los datos se desencriptaron correctamente
        assert decrypted_data.decode() == data
    
    def test_hash_password(self):
        """Prueba el hashing de contraseñas."""
        # Contraseña a hashear
        password = "contraseña123"
        
        # Hashear contraseña
        password_hash = hash_password(password)
        
        # Verificar que el hash no es igual a la contraseña original
        assert password_hash != password
        
        # Verificar que el hash tiene el formato correcto de Argon2
        assert password_hash.startswith("$argon2")
    
    def test_verify_password(self):
        """Prueba la verificación de contraseñas hasheadas."""
        # Contraseña a hashear
        password = "contraseña123"
        
        # Hashear contraseña
        password_hash = hash_password(password)
        
        # Verificar contraseña correcta
        assert verify_password(password, password_hash) is True
        
        # Verificar contraseña incorrecta
        assert verify_password("contraseña456", password_hash) is False
    
    def test_generate_key(self):
        """Prueba la generación de claves a partir de contraseñas."""
        # Contraseña
        password = "contraseña123"
        
        # Generar clave
        key, salt = generate_key(password)
        
        # Verificar que la clave y la sal no son nulas
        assert key is not None
        assert salt is not None
        
        # Generar clave con la misma sal
        key2, _ = generate_key(password, salt)
        
        # Verificar que las claves son iguales
        assert key == key2
        
        # Generar clave con contraseña diferente
        key3, _ = generate_key("contraseña456", salt)
        
        # Verificar que las claves son diferentes
        assert key != key3
    
    def test_encrypted_field(self):
        """Prueba el descriptor EncryptedField."""
        # Crear clase con campo encriptado
        class TestModel:
            _ssn = None
            _ssn_key = None
            
            ssn = EncryptedField('_ssn', '_ssn_key')
        
        # Crear instancia
        model = TestModel()
        
        # Establecer valor
        model.ssn = "123-45-6789"
        
        # Verificar que el valor se encriptó
        assert model._ssn is not None
        assert model._ssn_key is not None
        assert model._ssn != "123-45-6789".encode()
        
        # Verificar que el valor se puede recuperar
        assert model.ssn == "123-45-6789"


@pytest.mark.security
class TestSanitization:
    """Pruebas para funcionalidades de sanitización de datos."""
    
    def test_sanitize_html(self):
        """Prueba la sanitización de HTML."""
        # HTML con etiquetas permitidas y no permitidas
        html = """
        <p>Texto normal</p>
        <script>alert('XSS')</script>
        <a href="https://example.com" onclick="alert('XSS')">Enlace</a>
        <img src="image.jpg" onerror="alert('XSS')" />
        """
        
        # Sanitizar HTML
        sanitized = sanitize_html(html)
        
        # Verificar que las etiquetas permitidas se mantienen
        assert "<p>Texto normal</p>" in sanitized
        assert '<a href="https://example.com">Enlace</a>' in sanitized
        assert '<img src="image.jpg" />' in sanitized or '<img src="image.jpg">' in sanitized
        
        # Verificar que las etiquetas y atributos no permitidos se eliminan
        assert "<script>" not in sanitized
        assert "alert('XSS')" not in sanitized
        assert "onclick=" not in sanitized
        assert "onerror=" not in sanitized
    
    def test_sanitize_filename(self):
        """Prueba la sanitización de nombres de archivo."""
        # Nombres de archivo maliciosos
        filenames = [
            "../../../etc/passwd",
            "file.php;.jpg",
            "file.jpg/../../etc/passwd",
            "file with spaces.jpg",
            "file\nwith\nnewlines.jpg",
            "file<with>special\"chars'.jpg"
        ]
        
        # Sanitizar y verificar
        for filename in filenames:
            sanitized = sanitize_filename(filename)
            
            # Verificar que no hay caracteres peligrosos
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized
            assert ";" not in sanitized
            assert " " not in sanitized
            assert "\n" not in sanitized
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert "\"" not in sanitized
            assert "'" not in sanitized
    
    def test_sanitize_input(self):
        """Prueba la sanitización de entrada general."""
        # Entradas con posibles ataques XSS
        inputs = [
            "<script>alert('XSS')</script>",
            "normal text",
            "text with <b>tags</b>",
            "text with &lt;script&gt;",
            "text with ' and \""
        ]
        
        # Sanitizar y verificar
        for input_text in inputs:
            sanitized = sanitize_input(input_text)
            
            # Verificar que los caracteres especiales se escapan
            assert "<script>" not in sanitized
            assert "alert('XSS')" not in sanitized or "alert(&#x27;XSS&#x27;)" in sanitized
            
            # Verificar que el texto normal se mantiene
            if input_text == "normal text":
                assert sanitized == "normal text"
    
    def test_sanitize_sql_like(self):
        """Prueba la sanitización de cadenas para consultas LIKE."""
        # Cadenas con caracteres especiales de LIKE
        inputs = [
            "normal text",
            "text with %",
            "text with _",
            "text with \\"
        ]
        
        # Sanitizar y verificar
        for input_text in inputs:
            sanitized = sanitize_sql_like(input_text)
            
            # Verificar que los caracteres especiales se escapan
            if "%" in input_text:
                assert "\\%" in sanitized
            
            if "_" in input_text:
                assert "\\_" in sanitized
            
            if "\\" in input_text:
                assert "\\\\" in sanitized
    
    def test_sanitize_url(self):
        """Prueba la sanitización de URLs."""
        # URLs con posibles problemas
        urls = [
            "https://example.com",
            "http://example.com",
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            "example.com",
            "example.com/path?param=value"
        ]
        
        # Sanitizar y verificar
        for url in urls:
            sanitized = sanitize_url(url)
            
            # Verificar que las URLs válidas se mantienen
            if url.startswith("http"):
                assert url in sanitized
            
            # Verificar que las URLs sin protocolo se les añade https://
            if url == "example.com":
                assert sanitized == "https://example.com"
            
            # Verificar que las URLs maliciosas se sanitizan
            if "javascript:" in url:
                assert "javascript:" not in sanitized
            
            if "data:" in url:
                assert "data:" not in sanitized or "<script>" not in sanitized
    
    def test_sanitize_email(self):
        """Prueba la sanitización de direcciones de correo electrónico."""
        # Direcciones de correo con posibles problemas
        emails = [
            "user@example.com",
            "user+tag@example.com",
            "user@example.com;rm -rf /",
            "user@example.com\nBcc: victim@example.com",
            "<script>alert('XSS')</script>@example.com",
            "not an email"
        ]
        
        # Sanitizar y verificar
        for email in emails:
            sanitized = sanitize_email(email)
            
            # Verificar que las direcciones válidas se mantienen
            if email == "user@example.com" or email == "user+tag@example.com":
                assert sanitized == email
            
            # Verificar que las direcciones inválidas se rechazan
            if ";" in email or "\n" in email or "<script>" in email or " " in email:
                assert sanitized == ""


@pytest.mark.security
class TestSecrets:
    """Pruebas para gestión de secretos."""
    
    def test_set_get_secret(self, db):
        """Prueba la configuración y obtención de secretos."""
        # Establecer secreto
        result = set_secret("test_secret", "secret_value")
        
        # Verificar resultado
        assert result is True
        
        # Obtener secreto
        value = get_secret("test_secret")
        
        # Verificar valor
        assert value == "secret_value"
    
    def test_delete_secret(self, db):
        """Prueba la eliminación de secretos."""
        # Establecer secreto
        set_secret("delete_test", "delete_value")
        
        # Verificar que existe
        assert get_secret("delete_test") == "delete_value"
        
        # Eliminar secreto
        result = delete_secret("delete_test")
        
        # Verificar resultado
        assert result is True
        
        # Verificar que no existe
        assert get_secret("delete_test") is None
    
    def test_rotate_secret(self, db):
        """Prueba la rotación de secretos."""
        # Establecer secreto
        set_secret("rotate_test", "rotate_value")
        
        # Obtener secreto original
        secret = Secret.query.filter_by(name="rotate_test").first()
        original_value = secret.value
        original_key = secret.key
        
        # Rotar secreto
        result = rotate_secret("rotate_test")
        
        # Verificar resultado
        assert result is True
        
        # Obtener secreto rotado
        rotated_secret = Secret.query.filter_by(name="rotate_test").first()
        
        # Verificar que la clave cambió
        assert rotated_secret.key != original_key
        
        # Verificar que el valor encriptado cambió
        assert rotated_secret.value != original_value
        
        # Verificar que el valor desencriptado es el mismo
        assert rotated_secret.get_value() == "rotate_value"
