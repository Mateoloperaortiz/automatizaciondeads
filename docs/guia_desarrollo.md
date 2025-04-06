# 👨‍💻 Guía de Desarrollo

Esta guía está diseñada para ayudar a los desarrolladores a configurar su entorno de desarrollo, entender las convenciones de código y contribuir efectivamente al proyecto AdFlux.

## 🔧 Configuración del Entorno de Desarrollo

### Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git
- Redis (para tareas en segundo plano)
- Un editor de código (recomendado: VS Code, PyCharm)

### Configuración Paso a Paso

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/Mateoloperaortiz/automatizaciondeads.git
cd automatizaciondeads
```

#### 2. Crear y Activar Entorno Virtual

```bash
# En Windows
python -m venv .venv
.venv\Scripts\activate

# En macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependencias adicionales para desarrollo
```

#### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Configuración de Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev_secret_key_change_in_production

# Configuración de Base de Datos
DATABASE_URL=sqlite:///adflux_dev.db

# Configuración de Redis/Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Configuración de APIs (usar credenciales de desarrollo/prueba)
META_APP_ID=your_test_app_id
META_APP_SECRET=your_test_app_secret
META_ACCESS_TOKEN=your_test_access_token
META_AD_ACCOUNT_ID=your_test_ad_account_id
META_PAGE_ID=your_test_page_id

GOOGLE_ADS_DEVELOPER_TOKEN=your_test_developer_token
GOOGLE_ADS_CLIENT_ID=your_test_client_id
GOOGLE_ADS_CLIENT_SECRET=your_test_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_test_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_test_login_customer_id
GOOGLE_ADS_TARGET_CUSTOMER_ID=your_test_target_customer_id

GEMINI_API_KEY=your_test_api_key
```

#### 5. Inicializar la Base de Datos

```bash
flask db upgrade
```

#### 6. Generar Datos de Prueba

```bash
flask data generate-jobs 5
flask data generate-candidates 20
flask data generate-applications 10
```

#### 7. Ejecutar la Aplicación

```bash
# Terminal 1: Aplicación Flask
flask run

# Terminal 2: Worker de Celery
celery -A adflux.extensions.celery worker --loglevel=info

# Terminal 3: Beat de Celery (opcional, para tareas programadas)
celery -A adflux.extensions.celery beat --loglevel=info
```

#### 8. Configurar Pre-commit Hooks (opcional)

```bash
pip install pre-commit
pre-commit install
```

## 📂 Estructura del Proyecto

AdFlux sigue una estructura modular para facilitar el mantenimiento y la escalabilidad:

```
adflux/
├── api/                  # Integraciones con APIs externas
│   ├── common/           # Utilidades comunes para APIs
│   ├── gemini/           # Cliente y funciones para Gemini AI
│   ├── google/           # Cliente y funciones para Google Ads
│   └── meta/             # Cliente y funciones para Meta Ads
├── cli/                  # Comandos de línea de comandos
├── config/               # Configuraciones para diferentes entornos
├── core/                 # Funcionalidades centrales
├── forms/                # Formularios web
├── ml/                   # Módulos de machine learning
├── models/               # Modelos de base de datos
├── routes/               # Rutas y controladores web
├── schemas/              # Esquemas para serialización/deserialización
├── simulation/           # Generación de datos simulados
├── static/               # Archivos estáticos (CSS, JS, imágenes)
├── swagger/              # Configuración de Swagger para API
├── tasks/                # Tareas de Celery
└── templates/            # Plantillas HTML
```

### Archivos Principales

- `run.py`: Punto de entrada principal para ejecutar la aplicación
- `adflux/app.py`: Configuración de la aplicación Flask
- `adflux/extensions.py`: Inicialización de extensiones (SQLAlchemy, Celery, etc.)
- `adflux/constants.py`: Constantes utilizadas en toda la aplicación
- `adflux/core/factory.py`: Fábrica para crear la aplicación Flask
- `migrations/`: Migraciones de base de datos con Alembic

## 🧩 Patrones de Diseño

AdFlux utiliza varios patrones de diseño para mantener el código organizado y mantenible:

### Patrón Factory

La aplicación Flask se crea utilizando el patrón Factory en `core/factory.py`:

```python
def create_app(config_class=Config):
    """
    Crea y configura la aplicación Flask.
    
    Args:
        config_class: Clase de configuración a utilizar.
        
    Returns:
        Aplicación Flask configurada.
    """
    app = Flask(__name__,
              instance_relative_config=True,
              static_folder='../static',
              template_folder='../templates')
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    # ... otras inicializaciones
    
    # Registrar blueprints
    from ..routes import main_bp, dashboard_bp, campaign_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(campaign_bp, url_prefix='/campaigns')
    # ... otros blueprints
    
    return app
```

### Patrón Repository

Para el acceso a datos, AdFlux utiliza un patrón similar a Repository a través de SQLAlchemy:

```python
class CampaignRepository:
    """Repositorio para operaciones con campañas."""
    
    @staticmethod
    def get_by_id(campaign_id):
        """Obtiene una campaña por su ID."""
        return Campaign.query.get(campaign_id)
    
    @staticmethod
    def get_all(platform=None, status=None):
        """Obtiene todas las campañas con filtros opcionales."""
        query = Campaign.query
        
        if platform:
            query = query.filter_by(platform=platform)
            
        if status:
            query = query.filter_by(status=status)
            
        return query.all()
    
    @staticmethod
    def create(data):
        """Crea una nueva campaña."""
        campaign = Campaign(**data)
        db.session.add(campaign)
        db.session.commit()
        return campaign
    
    @staticmethod
    def update(campaign_id, data):
        """Actualiza una campaña existente."""
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return None
            
        for key, value in data.items():
            setattr(campaign, key, value)
            
        db.session.commit()
        return campaign
    
    @staticmethod
    def delete(campaign_id):
        """Elimina una campaña."""
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return False
            
        db.session.delete(campaign)
        db.session.commit()
        return True
```

### Patrón Service

Para la lógica de negocio, AdFlux utiliza servicios que encapsulan operaciones complejas:

```python
class CampaignService:
    """Servicio para operaciones de negocio con campañas."""
    
    @staticmethod
    def create_campaign(data, job_id=None):
        """
        Crea una campaña y la asocia a un trabajo si se proporciona.
        
        Args:
            data: Datos de la campaña.
            job_id: ID opcional del trabajo a asociar.
            
        Returns:
            Campaña creada.
        """
        # Validar datos
        if not data.get('name'):
            raise ValueError("El nombre de la campaña es obligatorio")
            
        if not data.get('platform'):
            raise ValueError("La plataforma es obligatoria")
        
        # Asociar trabajo si se proporciona ID
        if job_id:
            job = JobOpening.query.get(job_id)
            
            if not job:
                raise ValueError(f"Trabajo con ID {job_id} no encontrado")
                
            data['job_opening_id'] = job_id
        
        # Crear campaña
        campaign = CampaignRepository.create(data)
        
        return campaign
    
    @staticmethod
    def publish_campaign(campaign_id):
        """
        Publica una campaña en la plataforma correspondiente.
        
        Args:
            campaign_id: ID de la campaña a publicar.
            
        Returns:
            Resultado de la operación.
        """
        campaign = CampaignRepository.get_by_id(campaign_id)
        
        if not campaign:
            raise ValueError(f"Campaña con ID {campaign_id} no encontrada")
            
        if campaign.status != 'draft':
            raise ValueError("Solo se pueden publicar campañas en estado borrador")
        
        # Iniciar tarea según la plataforma
        if campaign.platform == 'meta':
            task = create_meta_campaign_task.delay(campaign_id)
        elif campaign.platform == 'google':
            task = create_google_campaign_task.delay(campaign_id)
        else:
            raise ValueError(f"Plataforma no soportada: {campaign.platform}")
        
        # Actualizar estado
        CampaignRepository.update(campaign_id, {
            'status': 'publishing',
            'task_id': task.id
        })
        
        return {
            'status': 'success',
            'message': 'Campaña en proceso de publicación',
            'task_id': task.id
        }
```

## 📝 Convenciones de Código

### Estilo de Código

AdFlux sigue las convenciones de estilo de PEP 8 con algunas modificaciones:

- **Longitud de línea**: Máximo 100 caracteres
- **Indentación**: 4 espacios (no tabs)
- **Nombres de variables**: snake_case para variables y funciones
- **Nombres de clases**: CamelCase para clases
- **Constantes**: MAYÚSCULAS_CON_GUIONES_BAJOS
- **Docstrings**: Estilo Google para documentación

### Ejemplo de Docstring

```python
def function_name(param1, param2):
    """
    Breve descripción de la función.
    
    Descripción más detallada que puede abarcar
    múltiples líneas si es necesario.
    
    Args:
        param1: Descripción del primer parámetro.
        param2: Descripción del segundo parámetro.
        
    Returns:
        Descripción de lo que devuelve la función.
        
    Raises:
        ValueError: Descripción de cuándo se lanza esta excepción.
        TypeError: Descripción de cuándo se lanza esta excepción.
    """
    # Implementación de la función
```

### Importaciones

Organiza las importaciones en el siguiente orden:

1. Importaciones de la biblioteca estándar
2. Importaciones de bibliotecas de terceros
3. Importaciones de módulos de la aplicación

```python
# Biblioteca estándar
import os
import json
from datetime import datetime

# Bibliotecas de terceros
import flask
from flask import Blueprint, render_template
from sqlalchemy import Column, String

# Módulos de la aplicación
from adflux.models import db
from adflux.extensions import celery
from adflux.api.meta.client import MetaApiClient
```

### Comentarios

- Los comentarios deben estar en español
- Usa comentarios para explicar "por qué", no "qué" o "cómo"
- Evita comentarios obvios que no añaden valor

```python
# Mal: Incrementa contador en 1
counter += 1

# Bien: Compensamos el índice base-0 para mostrar números de página amigables
page_number += 1
```

## 🧪 Pruebas

AdFlux utiliza pytest para las pruebas unitarias e integración.

### Estructura de Pruebas

```
tests/
├── conftest.py           # Fixtures compartidos
├── unit/                 # Pruebas unitarias
│   ├── api/              # Pruebas de módulos de API
│   ├── models/           # Pruebas de modelos
│   └── ...
└── integration/          # Pruebas de integración
    ├── api/              # Pruebas de integración de API
    └── ...
```

### Fixtures

Define fixtures reutilizables en `conftest.py`:

```python
import pytest
from adflux.core.factory import create_app
from adflux.models import db as _db
from adflux.models import JobOpening, Candidate, Campaign

@pytest.fixture
def app():
    """Crea y configura una instancia de la aplicación Flask para pruebas."""
    app = create_app('adflux.config.TestingConfig')
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def db(app):
    """Proporciona acceso a la base de datos de prueba."""
    return _db

@pytest.fixture
def client(app):
    """Proporciona un cliente de prueba para la aplicación Flask."""
    return app.test_client()

@pytest.fixture
def sample_job(db):
    """Crea un trabajo de muestra para pruebas."""
    job = JobOpening(
        job_id="JOB-TEST",
        title="Test Job",
        description="Test Description",
        location="Test Location",
        company_name="Test Company"
    )
    db.session.add(job)
    db.session.commit()
    return job
```

### Ejemplo de Prueba Unitaria

```python
def test_campaign_creation(db, sample_job):
    """Prueba la creación de una campaña."""
    # Configurar
    campaign_data = {
        'name': 'Test Campaign',
        'platform': 'meta',
        'status': 'draft',
        'job_opening_id': sample_job.job_id
    }
    
    # Ejecutar
    campaign = Campaign(**campaign_data)
    db.session.add(campaign)
    db.session.commit()
    
    # Verificar
    assert campaign.id is not None
    assert campaign.name == 'Test Campaign'
    assert campaign.platform == 'meta'
    assert campaign.status == 'draft'
    assert campaign.job_opening_id == sample_job.job_id
    assert campaign.job_opening == sample_job
```

### Ejemplo de Prueba de Integración

```python
def test_create_campaign_api(client, sample_job):
    """Prueba la creación de una campaña a través de la API."""
    # Configurar
    campaign_data = {
        'name': 'API Test Campaign',
        'platform': 'meta',
        'status': 'draft',
        'job_opening_id': sample_job.job_id,
        'daily_budget': 1000
    }
    
    # Ejecutar
    response = client.post(
        '/api/campaigns',
        json=campaign_data,
        content_type='application/json'
    )
    
    # Verificar
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'API Test Campaign'
    assert data['platform'] == 'meta'
    assert data['status'] == 'draft'
    assert data['job_opening_id'] == sample_job.job_id
    
    # Verificar en la base de datos
    campaign = Campaign.query.get(data['id'])
    assert campaign is not None
    assert campaign.name == 'API Test Campaign'
```

### Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas unitarias
pytest tests/unit/

# Ejecutar pruebas de integración
pytest tests/integration/

# Ejecutar pruebas con cobertura
pytest --cov=adflux

# Generar informe de cobertura HTML
pytest --cov=adflux --cov-report=html
```

## 🔄 Control de Versiones

### Flujo de Trabajo Git

AdFlux utiliza un flujo de trabajo basado en ramas:

- `main`: Rama principal, siempre estable
- `develop`: Rama de desarrollo, integración de características
- `feature/nombre-caracteristica`: Ramas para nuevas características
- `bugfix/nombre-bug`: Ramas para corrección de errores
- `release/x.y.z`: Ramas para preparación de versiones

### Convenciones de Commits

AdFlux sigue el formato de Conventional Commits:

```
<tipo>[ámbito opcional]: <descripción>

[cuerpo opcional]

[pie opcional]
```

Tipos comunes:
- `feat`: Nueva característica
- `fix`: Corrección de error
- `docs`: Cambios en documentación
- `style`: Cambios de formato (espacios, indentación, etc.)
- `refactor`: Refactorización de código
- `test`: Adición o corrección de pruebas
- `chore`: Tareas de mantenimiento

Ejemplos:

```
feat(campaigns): añadir soporte para campañas de Google Ads

fix(api): corregir error en la autenticación de Meta API

docs: actualizar documentación de instalación

refactor(models): reorganizar modelos de campaña para mejor mantenibilidad
```

### Pull Requests

- Crea un PR desde tu rama de característica a `develop`
- Incluye una descripción clara de los cambios
- Asegúrate de que todas las pruebas pasen
- Solicita revisión de al menos un desarrollador
- Aborda los comentarios de la revisión

## 📚 Recursos Adicionales

### Documentación de Bibliotecas

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Celery](https://docs.celeryq.dev/)
- [Meta Marketing API](https://developers.facebook.com/docs/marketing-apis/)
- [Google Ads API](https://developers.google.com/google-ads/api/docs/start)
- [Gemini API](https://ai.google.dev/docs)

### Herramientas Recomendadas

- **VS Code** con extensiones:
  - Python
  - Pylance
  - SQLAlchemy
  - GitLens
  - Python Test Explorer

- **PyCharm Professional** con:
  - Soporte para Flask
  - Soporte para SQLAlchemy
  - Herramientas de base de datos

- **Herramientas de Línea de Comandos**:
  - `httpie` para pruebas de API
  - `pgcli` para PostgreSQL
  - `redis-cli` para Redis

## 🤝 Contribución

### Proceso de Contribución

1. **Seleccionar una Tarea**: Elige una tarea del sistema de seguimiento de problemas
2. **Crear una Rama**: Crea una rama desde `develop` con el formato adecuado
3. **Desarrollar**: Implementa los cambios siguiendo las convenciones de código
4. **Pruebas**: Asegúrate de que todas las pruebas pasen y añade nuevas si es necesario
5. **Documentación**: Actualiza la documentación si es necesario
6. **Commit**: Realiza commits siguiendo las convenciones
7. **Pull Request**: Crea un PR a `develop` con una descripción clara
8. **Revisión**: Aborda los comentarios de la revisión
9. **Fusión**: Una vez aprobado, el PR será fusionado

### Reporte de Problemas

Si encuentras un error o tienes una sugerencia:

1. Verifica si el problema ya ha sido reportado
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducirlo
   - Comportamiento esperado vs. actual
   - Capturas de pantalla si es relevante
   - Información del entorno (versión de Python, sistema operativo, etc.)

## 🔍 Solución de Problemas Comunes

### Problemas de Entorno

**Problema**: Error "ModuleNotFoundError" al ejecutar la aplicación.

**Solución**: Asegúrate de que el entorno virtual esté activado y todas las dependencias estén instaladas:
```bash
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -r requirements.txt
```

### Problemas de Base de Datos

**Problema**: Error al ejecutar migraciones.

**Solución**: Reinicia la base de datos desde cero:
```bash
flask db stamp head  # Marca la base de datos como actualizada
flask db migrate     # Genera una nueva migración
flask db upgrade     # Aplica la migración
```

### Problemas de Celery

**Problema**: Las tareas de Celery no se ejecutan.

**Solución**: Verifica que Redis esté en ejecución y las variables de entorno estén configuradas correctamente:
```bash
redis-cli ping  # Debería responder "PONG"
```

### Problemas de API

**Problema**: Errores de autenticación con APIs externas.

**Solución**: Verifica que las credenciales en el archivo `.env` sean correctas y estén actualizadas. Para Meta API, asegúrate de que los tokens no hayan expirado.
