"""
Configuración para pruebas de AdFlux.

Este módulo contiene fixtures y configuraciones para las pruebas de AdFlux.
"""

import os
import sys
import pytest
import tempfile
from datetime import datetime, timedelta

import flask
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adflux import create_app
from adflux.models import db as _db
from adflux.models import User, Role, Permission, Campaign, MetaCampaign
from adflux.auth.rbac import create_default_roles_and_permissions


@pytest.fixture(scope='session')
def app():
    """
    Fixture para crear una instancia de la aplicación Flask.
    
    Returns:
        Instancia de la aplicación Flask
    """
    # Crear archivo de base de datos temporal
    db_fd, db_path = tempfile.mkstemp()
    
    # Configuración de prueba
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-key',
        'JWT_SECRET_KEY': 'test-jwt-key',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'REDIS_URL': None,  # Desactivar Redis para pruebas
        'CELERY_BROKER_URL': None,  # Desactivar Celery para pruebas
        'CELERY_RESULT_BACKEND': None,
        'MAIL_SUPPRESS_SEND': True,  # Desactivar envío de correos
        'SERVER_NAME': 'localhost',
        'PREFERRED_URL_SCHEME': 'http',
        'APPLICATION_ROOT': '/',
    }
    
    # Crear aplicación
    app = create_app(test_config)
    
    # Establecer contexto de aplicación
    with app.app_context():
        # Crear tablas
        _db.create_all()
        
        # Crear roles y permisos por defecto
        create_default_roles_and_permissions()
        
        yield app
    
    # Limpiar
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def db(app):
    """
    Fixture para proporcionar una sesión de base de datos.
    
    Args:
        app: Fixture de aplicación Flask
        
    Returns:
        Objeto de base de datos SQLAlchemy
    """
    with app.app_context():
        # Limpiar tablas
        _db.session.remove()
        _db.drop_all()
        _db.create_all()
        
        # Crear roles y permisos por defecto
        create_default_roles_and_permissions()
        
        yield _db
        
        # Limpiar después de cada prueba
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Fixture para proporcionar un cliente de prueba.
    
    Args:
        app: Fixture de aplicación Flask
        
    Returns:
        Cliente de prueba Flask
    """
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def admin_user(db):
    """
    Fixture para crear un usuario administrador.
    
    Args:
        db: Fixture de base de datos
        
    Returns:
        Usuario administrador
    """
    # Obtener rol de administrador
    admin_role = Role.query.filter_by(name='admin').first()
    
    # Crear usuario administrador
    admin = User(
        username='admin',
        email='admin@example.com',
        name='Admin User',
        password_hash='$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash',  # 'password'
        active=True
    )
    admin.roles.append(admin_role)
    
    db.session.add(admin)
    db.session.commit()
    
    return admin


@pytest.fixture(scope='function')
def regular_user(db):
    """
    Fixture para crear un usuario regular.
    
    Args:
        db: Fixture de base de datos
        
    Returns:
        Usuario regular
    """
    # Obtener rol de editor
    editor_role = Role.query.filter_by(name='editor').first()
    
    # Crear usuario regular
    user = User(
        username='user',
        email='user@example.com',
        name='Regular User',
        password_hash='$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash',  # 'password'
        active=True
    )
    user.roles.append(editor_role)
    
    db.session.add(user)
    db.session.commit()
    
    return user


@pytest.fixture(scope='function')
def admin_token(app, admin_user):
    """
    Fixture para crear un token JWT para un usuario administrador.
    
    Args:
        app: Fixture de aplicación Flask
        admin_user: Fixture de usuario administrador
        
    Returns:
        Token JWT
    """
    with app.app_context():
        token = create_access_token(identity=admin_user.id)
        return token


@pytest.fixture(scope='function')
def user_token(app, regular_user):
    """
    Fixture para crear un token JWT para un usuario regular.
    
    Args:
        app: Fixture de aplicación Flask
        regular_user: Fixture de usuario regular
        
    Returns:
        Token JWT
    """
    with app.app_context():
        token = create_access_token(identity=regular_user.id)
        return token


@pytest.fixture(scope='function')
def auth_client(client, admin_token):
    """
    Fixture para proporcionar un cliente autenticado como administrador.
    
    Args:
        client: Fixture de cliente Flask
        admin_token: Fixture de token JWT para administrador
        
    Returns:
        Cliente Flask autenticado
    """
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {admin_token}'
    return client


@pytest.fixture(scope='function')
def user_auth_client(client, user_token):
    """
    Fixture para proporcionar un cliente autenticado como usuario regular.
    
    Args:
        client: Fixture de cliente Flask
        user_token: Fixture de token JWT para usuario regular
        
    Returns:
        Cliente Flask autenticado
    """
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {user_token}'
    return client


@pytest.fixture(scope='function')
def sample_campaign(db, admin_user):
    """
    Fixture para crear una campaña de ejemplo.
    
    Args:
        db: Fixture de base de datos
        admin_user: Fixture de usuario administrador
        
    Returns:
        Campaña de ejemplo
    """
    # Crear campaña
    campaign = Campaign(
        name='Test Campaign',
        objective='AWARENESS',
        status='ACTIVE',
        platform='META',
        daily_budget=100.0,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        created_by=admin_user.id
    )
    
    db.session.add(campaign)
    db.session.commit()
    
    # Crear campaña de Meta asociada
    meta_campaign = MetaCampaign(
        campaign_id=campaign.id,
        external_id='123456789',
        status='ACTIVE'
    )
    
    db.session.add(meta_campaign)
    db.session.commit()
    
    return campaign


@pytest.fixture(scope='function')
def mock_redis(monkeypatch):
    """
    Fixture para simular Redis.
    
    Args:
        monkeypatch: Fixture de pytest para parchear objetos
        
    Returns:
        Objeto simulado de Redis
    """
    class MockRedis:
        def __init__(self):
            self.data = {}
            self.expires = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value, ex=None):
            self.data[key] = value
            if ex:
                self.expires[key] = datetime.utcnow() + timedelta(seconds=ex)
            return True
        
        def delete(self, *keys):
            count = 0
            for key in keys:
                if key in self.data:
                    del self.data[key]
                    count += 1
                    if key in self.expires:
                        del self.expires[key]
            return count
        
        def exists(self, key):
            return key in self.data
        
        def expire(self, key, seconds):
            if key in self.data:
                self.expires[key] = datetime.utcnow() + timedelta(seconds=seconds)
                return True
            return False
        
        def ttl(self, key):
            if key not in self.data:
                return -2
            if key not in self.expires:
                return -1
            
            remaining = (self.expires[key] - datetime.utcnow()).total_seconds()
            return max(0, int(remaining))
        
        def incr(self, key, amount=1):
            if key not in self.data:
                self.data[key] = 0
            
            self.data[key] += amount
            return self.data[key]
        
        def decr(self, key, amount=1):
            if key not in self.data:
                self.data[key] = 0
            
            self.data[key] -= amount
            return self.data[key]
        
        def keys(self, pattern='*'):
            import fnmatch
            return [k.encode() for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]
        
        def ping(self):
            return True
    
    mock_redis = MockRedis()
    
    # Parchear Redis en la aplicación
    def mock_redis_from_url(*args, **kwargs):
        return mock_redis
    
    import redis
    monkeypatch.setattr(redis, 'Redis', MockRedis)
    monkeypatch.setattr(redis, 'from_url', mock_redis_from_url)
    
    return mock_redis


@pytest.fixture(scope='function')
def mock_celery(monkeypatch):
    """
    Fixture para simular Celery.
    
    Args:
        monkeypatch: Fixture de pytest para parchear objetos
        
    Returns:
        Objeto simulado de Celery
    """
    class MockTask:
        def __init__(self, task_id='mock-task-id'):
            self.id = task_id
            self.status = 'PENDING'
            self.result = None
            self.args = []
            self.kwargs = {}
        
        def delay(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.status = 'STARTED'
            return self
        
        def apply_async(self, args=None, kwargs=None, **options):
            self.args = args or []
            self.kwargs = kwargs or {}
            self.status = 'STARTED'
            return self
        
        def get(self, timeout=None):
            return self.result
    
    class MockCelery:
        def __init__(self):
            self.tasks = {}
            self.conf = {}
        
        def task(self, *args, **kwargs):
            def decorator(func):
                task = MockTask()
                task.func = func
                task.name = func.__name__
                self.tasks[func.__name__] = task
                return task
            
            # Permitir usar @celery.task o @celery.task()
            if len(args) == 1 and callable(args[0]):
                return decorator(args[0])
            
            return decorator
    
    mock_celery = MockCelery()
    
    # Parchear Celery en la aplicación
    import celery
    monkeypatch.setattr(celery, 'Celery', lambda *args, **kwargs: mock_celery)
    
    return mock_celery
