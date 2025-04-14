# Meta API - Visión General

AdFlux se integra con la API de Meta para publicar anuncios en Facebook e Instagram. Esta página proporciona una visión general de la integración.

## Introducción

La API de Meta (anteriormente Facebook Marketing API) permite crear, gestionar y medir campañas publicitarias en Facebook e Instagram. AdFlux utiliza esta API para automatizar la publicación de anuncios de trabajo en estas plataformas.

## Versión de la API

AdFlux utiliza la versión 18.0 de la API de Meta. Esta versión es compatible hasta mayo de 2025.

```python
# Ejemplo de URL base de la API
API_BASE_URL = "https://graph.facebook.com/v18.0/"
```

## Autenticación

La autenticación con la API de Meta se realiza mediante un token de acceso. AdFlux utiliza tokens de acceso de larga duración para aplicaciones de negocio.

### Requisitos

Para utilizar la API de Meta, se necesitan las siguientes credenciales:

- **App ID**: Identificador de la aplicación de Meta.
- **App Secret**: Secreto de la aplicación de Meta.
- **Access Token**: Token de acceso con los permisos necesarios.

### Configuración

Las credenciales se configuran en el archivo `.env`:

```
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=your_access_token
```

### Permisos Necesarios

El token de acceso debe tener los siguientes permisos:

- `ads_management`: Para crear y gestionar campañas publicitarias.
- `ads_read`: Para leer información sobre campañas publicitarias.
- `business_management`: Para gestionar cuentas publicitarias de negocio.

## Cliente de la API

AdFlux implementa un cliente personalizado para la API de Meta en `adflux/meta/client.py`:

```python
class MetaApiClient:
    def __init__(self, app_id=None, app_secret=None, access_token=None):
        self.app_id = app_id or os.environ.get('META_APP_ID')
        self.app_secret = app_secret or os.environ.get('META_APP_SECRET')
        self.access_token = access_token or os.environ.get('META_ACCESS_TOKEN')
        self.base_url = "https://graph.facebook.com/v18.0/"
        
    def get(self, endpoint, params=None):
        """Realiza una solicitud GET a la API de Meta."""
        url = self.base_url + endpoint
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def post(self, endpoint, data=None):
        """Realiza una solicitud POST a la API de Meta."""
        url = self.base_url + endpoint
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    # Otros métodos para DELETE, etc.
```

## Estructura de la Integración

La integración con la API de Meta está organizada en módulos:

- **client.py**: Cliente base para la API.
- **campaigns.py**: Operaciones relacionadas con campañas.
- **ad_sets.py**: Operaciones relacionadas con conjuntos de anuncios.
- **ads.py**: Operaciones relacionadas con anuncios.
- **ad_creatives.py**: Operaciones relacionadas con creativos de anuncios.
- **insights.py**: Operaciones para obtener métricas e insights.
- **utils.py**: Utilidades comunes.

## Flujo de Trabajo Típico

El flujo de trabajo típico para publicar un anuncio de trabajo en Meta es:

1. Crear una campaña publicitaria.
2. Crear un conjunto de anuncios con la segmentación adecuada.
3. Crear un creativo para el anuncio.
4. Crear un anuncio utilizando el creativo.
5. Publicar la campaña.
6. Monitorizar el rendimiento a través de insights.

## Ejemplo de Uso

```python
from adflux.meta.client import MetaApiClient
from adflux.meta.campaigns import create_campaign
from adflux.meta.ad_sets import create_ad_set
from adflux.meta.ad_creatives import create_ad_creative
from adflux.meta.ads import create_ad

# Crear cliente
client = MetaApiClient()

# Crear campaña
campaign = create_campaign(
    account_id='act_123456789',
    name='Software Developer Job Opening',
    objective='REACH',
    status='PAUSED',
    special_ad_categories=[],
    daily_budget=1000  # En centavos (10 USD)
)

# Crear conjunto de anuncios
ad_set = create_ad_set(
    account_id='act_123456789',
    name='Software Developers in New York',
    campaign_id=campaign['id'],
    optimization_goal='REACH',
    billing_event='IMPRESSIONS',
    bid_amount=500,  # En centavos
    targeting={
        'geo_locations': {
            'countries': ['US'],
            'regions': [{'key': '2421', 'name': 'New York'}]
        },
        'age_min': 22,
        'age_max': 55,
        'interests': [
            {'id': '6003139266461', 'name': 'Software development'}
        ]
    },
    status='PAUSED'
)

# Crear creativo
creative = create_ad_creative(
    account_id='act_123456789',
    name='Software Developer Job Ad',
    object_story_spec={
        'page_id': '123456789',
        'link_data': {
            'message': 'We\'re hiring Software Developers!',
            'link': 'https://example.com/careers',
            'image_hash': 'abc123def456',
            'call_to_action': {
                'type': 'APPLY_NOW',
                'value': {
                    'link': 'https://example.com/careers'
                }
            }
        }
    }
)

# Crear anuncio
ad = create_ad(
    account_id='act_123456789',
    name='Software Developer Job Ad',
    adset_id=ad_set['id'],
    creative_id=creative['id'],
    status='PAUSED'
)

print(f"Campaign created with ID: {campaign['id']}")
print(f"Ad Set created with ID: {ad_set['id']}")
print(f"Creative created with ID: {creative['id']}")
print(f"Ad created with ID: {ad['id']}")
```

## Manejo de Errores

La API de Meta puede devolver varios tipos de errores. AdFlux implementa un sistema de manejo de errores que incluye reintentos automáticos para errores transitorios:

```python
def handle_meta_api_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [429, 500, 502, 503, 504] and attempt < max_retries - 1:
                    # Error transitorio, reintentar
                    time.sleep(retry_delay * (2 ** attempt))  # Backoff exponencial
                    continue
                
                # Procesar error de la API de Meta
                error_data = e.response.json().get('error', {})
                error_code = error_data.get('code')
                error_message = error_data.get('message')
                
                # Registrar error
                logger.error(f"Meta API Error: {error_code} - {error_message}")
                
                # Manejar errores específicos
                if error_code == 190:
                    raise MetaAuthError("Invalid or expired access token")
                elif error_code == 4:
                    raise MetaRateLimitError("Rate limit exceeded")
                else:
                    raise MetaApiError(f"{error_code}: {error_message}")
            
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise
    
    return wrapper
```

## Limitaciones y Consideraciones

- **Límites de Tasa**: La API de Meta tiene límites de tasa que varían según el endpoint y el tipo de cuenta.
- **Políticas Publicitarias**: Los anuncios deben cumplir con las políticas publicitarias de Meta.
- **Categorías Especiales de Anuncios**: Los anuncios de empleo se consideran una categoría especial y tienen requisitos adicionales.
- **Cambios en la API**: La API de Meta cambia con frecuencia, por lo que es importante mantener actualizada la integración.

## Recursos Adicionales

- [Documentación oficial de la API de Meta](https://developers.facebook.com/docs/marketing-apis/)
- [Políticas publicitarias de Meta](https://www.facebook.com/policies/ads/)
- [Herramienta de exploración de la API de Meta](https://developers.facebook.com/tools/explorer/)
