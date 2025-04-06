# Módulo de API de AdFlux

Este módulo proporciona una interfaz unificada para interactuar con diferentes APIs externas utilizadas por AdFlux:

- **Meta (Facebook/Instagram) Ads API**: Para la gestión de campañas publicitarias en Meta.
- **Google Ads API**: Para la gestión de campañas publicitarias en Google.
- **Google Gemini API**: Para la generación de contenido creativo para anuncios.

## Estructura del Módulo

```
adflux/api/
├── __init__.py           # Punto de entrada principal
├── common/               # Utilidades comunes
│   ├── __init__.py
│   ├── error_handling.py # Manejo de errores
│   └── logging.py        # Utilidades de logging
├── meta/                 # API de Meta (Facebook/Instagram)
│   ├── __init__.py
│   ├── client.py         # Cliente principal
│   ├── campaigns.py      # Gestión de campañas
│   ├── ad_sets.py        # Gestión de conjuntos de anuncios
│   ├── ads.py            # Gestión de anuncios
│   └── insights.py       # Obtención de métricas
├── google/               # API de Google Ads
│   ├── __init__.py
│   ├── client.py         # Cliente principal
│   └── campaigns.py      # Gestión de campañas
└── gemini/               # API de Google Gemini
    ├── __init__.py
    ├── client.py         # Cliente principal
    └── content_generation.py # Generación de contenido
```

## Uso

### Meta Ads API

```python
from adflux.api import get_meta_client
from adflux.api import MetaCampaignManager

# Crear cliente
client = get_meta_client()

# Crear gestor de campañas
campaign_manager = MetaCampaignManager(client)

# Obtener campañas
success, message, campaigns = campaign_manager.get_campaigns('act_123456789')
```

### Google Ads API

```python
from adflux.api import get_google_client
from adflux.api import GoogleCampaignManager

# Crear cliente
client = get_google_client()

# Crear gestor de campañas
campaign_manager = GoogleCampaignManager(client)

# Publicar campaña
result = campaign_manager.publish_campaign('123456789', 1, {
    'name': 'Mi Campaña',
    'daily_budget': 1000,  # en centavos
    'primary_text': 'Texto principal',
    'headline': 'Título'
})
```

### Google Gemini API

```python
from adflux.api import get_gemini_client
from adflux.api import get_content_generator

# Crear cliente
client = get_gemini_client('API_KEY')

# Crear generador de contenido
content_generator = get_content_generator(client)

# Generar contenido creativo
success, message, creative = content_generator.generate_ad_creative(
    'Desarrollador Python',
    'Buscamos un desarrollador Python con experiencia en Flask y SQLAlchemy.',
    'profesionales de tecnología'
)
```

## Capa de Compatibilidad

Para mantener la compatibilidad con el código existente, se proporciona una capa de compatibilidad en `adflux.api_clients_compat`. Esta capa implementa la misma interfaz que el archivo original `api_clients.py`, pero utiliza la nueva estructura de módulos internamente.

```python
from adflux.api_clients_compat import (
    get_meta_campaigns,
    create_meta_campaign,
    publish_google_campaign_api,
    generate_ad_creative_gemini
)
```

## Manejo de Errores

Todos los métodos de API devuelven una tupla con tres elementos:

```python
success, message, data = client.method()
```

- `success`: Un booleano que indica si la operación fue exitosa.
- `message`: Un mensaje descriptivo sobre el resultado de la operación.
- `data`: Los datos devueltos por la operación, o None si la operación falló.

## Logging

El módulo proporciona utilidades de logging para registrar información sobre las operaciones de API:

```python
from adflux.api.common.logging import get_logger

logger = get_logger("MiMódulo")
logger.info("Mensaje informativo")
logger.warning("Advertencia")
logger.error("Error", excepcion)
```
