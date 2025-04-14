# Documentación de Referencia

Esta sección contiene documentación técnica detallada sobre los componentes y funcionalidades de AdFlux.

## Contenido

- [API](./api/): Documentación detallada de la API de AdFlux.
  - [Autenticación](./api/autenticacion.md): Métodos de autenticación para la API.
  - [Endpoints](./api/endpoints/): Documentación de los endpoints de la API.
  - [Modelos](./api/modelos.md): Modelos de datos utilizados en la API.
  - [Errores](./api/errores.md): Códigos de error y su significado.
- [Modelos de Datos](./modelos/): Documentación de los modelos de datos de AdFlux.
- [Servicios](./servicios/): Documentación de los servicios de AdFlux.
- [Utilidades](./utilidades/): Documentación de las utilidades y helpers.
- [Configuración](./configuracion.md): Opciones de configuración disponibles.
- [Glosario](./glosario.md): Términos y definiciones utilizados en AdFlux.
- [Changelog](./changelog.md): Historial de cambios de AdFlux.

## API

La API de AdFlux permite interactuar con el sistema de forma programática. La documentación completa está disponible en la sección [API](./api/).

### Ejemplo de Uso

```python
import requests
import json

# Autenticación
auth_response = requests.post(
    "https://api.adflux.example.com/api/v1/auth/login",
    json={
        "email": "user@example.com",
        "password": "password"
    }
)
token = auth_response.json()["access_token"]

# Crear una campaña
campaign_response = requests.post(
    "https://api.adflux.example.com/api/v1/campaigns",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "name": "Software Developer Campaign",
        "objective": "AWARENESS",
        "platform": "META",
        "status": "DRAFT",
        "daily_budget": 100.0,
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "job_opening_id": 123
    }
)

print(json.dumps(campaign_response.json(), indent=2))
```

## Modelos de Datos

Los modelos de datos de AdFlux están implementados utilizando SQLAlchemy ORM. La documentación completa está disponible en la sección [Modelos de Datos](./modelos/).

### Ejemplo de Modelo

```python
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    objective = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='DRAFT')
    platform = db.Column(db.String(20), nullable=False)
    daily_budget = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    targeting = db.Column(db.JSON)
    ad_creative = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    job_opening_id = db.Column(db.Integer, db.ForeignKey('job_openings.id'))
    
    # Relaciones
    meta_campaign = db.relationship('MetaCampaign', backref='campaign', uselist=False)
    google_campaign = db.relationship('GoogleCampaign', backref='campaign', uselist=False)
```

## Servicios

Los servicios de AdFlux implementan la lógica de negocio de la aplicación. La documentación completa está disponible en la sección [Servicios](./servicios/).

### Ejemplo de Servicio

```python
class CampaignService:
    @staticmethod
    def create_campaign(data, user_id):
        """
        Crea una nueva campaña.
        
        Args:
            data: Datos de la campaña
            user_id: ID del usuario que crea la campaña
            
        Returns:
            Objeto Campaign creado
        """
        # Validar datos
        if not data.get('name'):
            raise ValueError("El nombre de la campaña es obligatorio")
        
        # Crear campaña
        campaign = Campaign(
            name=data['name'],
            objective=data['objective'],
            platform=data['platform'],
            status='DRAFT',
            daily_budget=data['daily_budget'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            targeting=data.get('targeting'),
            ad_creative=data.get('ad_creative'),
            created_by=user_id,
            job_opening_id=data.get('job_opening_id')
        )
        
        # Guardar en la base de datos
        db.session.add(campaign)
        db.session.commit()
        
        return campaign
```

## Utilidades

AdFlux incluye varias utilidades y helpers para facilitar tareas comunes. La documentación completa está disponible en la sección [Utilidades](./utilidades/).

### Ejemplo de Utilidad

```python
def paginate(query, page=1, per_page=20, error_out=True):
    """
    Pagina los resultados de una consulta.
    
    Args:
        query: Consulta SQLAlchemy
        page: Número de página (comenzando desde 1)
        per_page: Número de elementos por página
        error_out: Si es True, lanza un error 404 si la página no existe
        
    Returns:
        Objeto Pagination
    """
    return query.paginate(page=page, per_page=per_page, error_out=error_out)
```

## Configuración

AdFlux proporciona varias opciones de configuración para personalizar su comportamiento. La documentación completa está disponible en [Configuración](./configuracion.md).

### Ejemplo de Configuración

```python
class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///adflux.db')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
```

## Glosario

El [Glosario](./glosario.md) proporciona definiciones de términos específicos utilizados en AdFlux.

## Changelog

El [Changelog](./changelog.md) documenta los cambios realizados en cada versión de AdFlux.
