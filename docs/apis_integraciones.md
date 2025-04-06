# 🔌 APIs e Integraciones

Este documento describe las integraciones con APIs externas que utiliza AdFlux para publicar y gestionar campañas publicitarias en diferentes plataformas.

## 📱 Meta (Facebook/Instagram) API

AdFlux se integra con la API de Meta Ads para crear y gestionar campañas publicitarias en Facebook e Instagram.

### 🔑 Configuración y Autenticación

```python
class MetaApiClient:
    def __init__(self, app_id=None, app_secret=None, access_token=None):
        self.app_id = app_id or os.getenv('META_APP_ID')
        self.app_secret = app_secret or os.getenv('META_APP_SECRET')
        self.access_token = access_token or os.getenv('META_ACCESS_TOKEN')
        self.ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
        self.page_id = os.getenv('META_PAGE_ID')
        self.api = None
        self.initialized = False
```

**Requisitos de Configuración:**
- `META_APP_ID`: ID de la aplicación de Meta
- `META_APP_SECRET`: Secreto de la aplicación de Meta
- `META_ACCESS_TOKEN`: Token de acceso de larga duración
- `META_AD_ACCOUNT_ID`: ID de la cuenta publicitaria
- `META_PAGE_ID`: ID de la página de Facebook

### 📊 Funcionalidades Principales

#### 1. Creación de Campañas

```python
def create_campaign(self, name, objective='OUTCOME_AWARENESS', status='PAUSED', special_ad_categories=None, daily_budget=None):
    """Crea una campaña publicitaria en Meta Ads."""
    # Implementación...
```

#### 2. Creación de Conjuntos de Anuncios (Ad Sets)

```python
def create_ad_set(self, campaign_id, name, optimization_goal='REACH', billing_event='IMPRESSIONS', 
                 bid_amount=None, targeting=None, status='PAUSED', daily_budget=None):
    """Crea un conjunto de anuncios en Meta Ads."""
    # Implementación...
```

#### 3. Creación de Anuncios

```python
def create_ad(self, ad_set_id, name, creative_id=None, status='PAUSED'):
    """Crea un anuncio en Meta Ads."""
    # Implementación...
```

#### 4. Creación de Creativos

```python
def create_ad_creative(self, name, page_id, message, headline, description=None, 
                      image_url=None, image_hash=None, link_url=None):
    """Crea un creativo publicitario en Meta Ads."""
    # Implementación...
```

#### 5. Obtención de Métricas (Insights)

```python
def get_insights(self, object_id, object_type='CAMPAIGN', fields=None, 
                date_preset='LAST_30_DAYS', time_increment=1):
    """Obtiene métricas de rendimiento de una entidad publicitaria."""
    # Implementación...
```

### 📝 Ejemplo de Uso

```python
# Inicializar cliente
meta_client = MetaApiClient()
meta_client.initialize()

# Crear campaña
campaign_result = meta_client.create_campaign(
    name="Oferta de Trabajo: Desarrollador Python",
    objective="OUTCOME_AWARENESS",
    daily_budget=500  # $5.00
)

# Crear conjunto de anuncios
ad_set_result = meta_client.create_ad_set(
    campaign_id=campaign_result['id'],
    name="Desarrolladores en Medellín",
    targeting={
        "geo_locations": {
            "cities": [
                {"key": "2486340", "name": "Medellín", "region": "Antioquia", "country": "CO"}
            ]
        },
        "interests": [
            {"id": "6003139266461", "name": "Programación"}
        ]
    },
    daily_budget=500  # $5.00
)

# Crear creativo
creative_result = meta_client.create_ad_creative(
    name="Creativo para Desarrollador Python",
    page_id=meta_client.page_id,
    message="¿Buscas trabajo como desarrollador Python? ¡Tenemos la oportunidad perfecta para ti!",
    headline="Desarrollador Python Senior",
    description="Únete a nuestro equipo en Medellín",
    link_url="https://magneto365.com/jobs/python-developer"
)

# Crear anuncio
ad_result = meta_client.create_ad(
    ad_set_id=ad_set_result['id'],
    name="Anuncio Desarrollador Python",
    creative_id=creative_result['id']
)
```

### ⚠️ Manejo de Errores

AdFlux implementa un manejo robusto de errores para las llamadas a la API de Meta:

```python
def handle_meta_api_error(func):
    """Decorador para manejar errores de la API de Meta."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FacebookRequestError as e:
            error_message = f"Error de Meta API: {e.api_error_message()}"
            logger.error(error_message)
            # Manejo específico según el código de error
            if e.api_error_code() == 190:
                logger.error("Token de acceso inválido o expirado")
            # ... otros manejos específicos
            raise
        except Exception as e:
            logger.error(f"Error inesperado en Meta API: {str(e)}")
            raise
    return wrapper
```

## 🔍 Google Ads API

AdFlux se integra con la API de Google Ads para crear y gestionar campañas publicitarias en la red de Google.

### 🔑 Configuración y Autenticación

```python
class GoogleAdsApiClient:
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        developer_token=None,
        refresh_token=None,
        login_customer_id=None,
        config_path=None
    ):
        self.client_id = client_id or os.getenv('GOOGLE_ADS_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('GOOGLE_ADS_CLIENT_SECRET')
        self.developer_token = developer_token or os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
        self.refresh_token = refresh_token or os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
        self.login_customer_id = login_customer_id or os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
        self.client = None
        self.initialized = False
```

**Requisitos de Configuración:**
- `GOOGLE_ADS_CLIENT_ID`: ID de cliente de OAuth
- `GOOGLE_ADS_CLIENT_SECRET`: Secreto de cliente de OAuth
- `GOOGLE_ADS_DEVELOPER_TOKEN`: Token de desarrollador de Google Ads
- `GOOGLE_ADS_REFRESH_TOKEN`: Token de actualización de OAuth
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`: ID de cliente de inicio de sesión
- `GOOGLE_ADS_TARGET_CUSTOMER_ID`: ID de cliente objetivo para operaciones

### 📊 Funcionalidades Principales

#### 1. Creación de Campañas

```python
def create_campaign(self, customer_id, name, budget_amount_micros, 
                   advertising_channel_type='SEARCH', status='PAUSED'):
    """Crea una campaña publicitaria en Google Ads."""
    # Implementación...
```

#### 2. Creación de Grupos de Anuncios

```python
def create_ad_group(self, customer_id, campaign_id, name, status='PAUSED'):
    """Crea un grupo de anuncios en Google Ads."""
    # Implementación...
```

#### 3. Creación de Anuncios

```python
def create_responsive_search_ad(self, customer_id, ad_group_id, headlines, descriptions, 
                               final_urls, path1=None, path2=None):
    """Crea un anuncio de búsqueda responsive en Google Ads."""
    # Implementación...
```

#### 4. Gestión de Palabras Clave

```python
def add_keywords(self, customer_id, ad_group_id, keywords, match_type='BROAD'):
    """Añade palabras clave a un grupo de anuncios."""
    # Implementación...
```

#### 5. Obtención de Métricas

```python
def get_campaign_metrics(self, customer_id, campaign_id=None, date_range='LAST_30_DAYS'):
    """Obtiene métricas de rendimiento de campañas."""
    # Implementación...
```

### 📝 Ejemplo de Uso

```python
# Inicializar cliente
google_client = GoogleAdsApiClient()
google_client.initialize()

# Crear campaña
campaign_result = google_client.create_campaign(
    customer_id=os.getenv('GOOGLE_ADS_TARGET_CUSTOMER_ID'),
    name="Oferta de Trabajo: Desarrollador Python",
    budget_amount_micros=500000  # $5.00
)

# Crear grupo de anuncios
ad_group_result = google_client.create_ad_group(
    customer_id=os.getenv('GOOGLE_ADS_TARGET_CUSTOMER_ID'),
    campaign_id=campaign_result.id,
    name="Desarrollador Python"
)

# Crear anuncio
ad_result = google_client.create_responsive_search_ad(
    customer_id=os.getenv('GOOGLE_ADS_TARGET_CUSTOMER_ID'),
    ad_group_id=ad_group_result.id,
    headlines=[
        "Desarrollador Python Senior",
        "Oportunidad para Programadores",
        "Empleo en Tecnología"
    ],
    descriptions=[
        "Únete a nuestro equipo en Medellín. Excelentes beneficios y ambiente de trabajo.",
        "Buscamos talento en programación Python. Aplica ahora."
    ],
    final_urls=["https://magneto365.com/jobs/python-developer"]
)

# Añadir palabras clave
keyword_result = google_client.add_keywords(
    customer_id=os.getenv('GOOGLE_ADS_TARGET_CUSTOMER_ID'),
    ad_group_id=ad_group_result.id,
    keywords=["desarrollador python", "trabajo programación", "empleo python medellín"],
    match_type="PHRASE"
)
```

### ⚠️ Manejo de Errores

```python
def handle_google_ads_api_error(func):
    """Decorador para manejar errores de la API de Google Ads."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GoogleAdsException as e:
            error_message = f"Error de Google Ads API: {e.failure.errors[0].message}"
            logger.error(error_message)
            # Manejo específico según el código de error
            # ... manejos específicos
            raise
        except Exception as e:
            logger.error(f"Error inesperado en Google Ads API: {str(e)}")
            raise
    return wrapper
```

## 🧠 Gemini AI API

AdFlux utiliza la API de Gemini AI de Google para generar contenido creativo para anuncios y simular datos para pruebas.

### 🔑 Configuración y Autenticación

```python
class GeminiApiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.initialized = False
        
    def initialize(self):
        if not GEMINI_SDK_AVAILABLE:
            logger.error("El SDK de Google Generative AI no está disponible.")
            return False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Error al inicializar Gemini API: {str(e)}")
            return False
```

**Requisitos de Configuración:**
- `GEMINI_API_KEY`: Clave de API de Google Gemini

### 📊 Funcionalidades Principales

#### 1. Generación de Texto

```python
def generate_text(self, prompt, temperature=0.7, max_output_tokens=1024):
    """Genera texto utilizando el modelo Gemini."""
    # Implementación...
```

#### 2. Generación de Contenido Creativo para Anuncios

```python
def generate_ad_content(self, job_title, job_description, company_name, location):
    """Genera contenido creativo para anuncios basado en información de trabajo."""
    # Implementación...
```

#### 3. Simulación de Datos

```python
def generate_candidate_profile():
    """Genera un perfil de candidato simulado."""
    # Implementación...
```

### 📝 Ejemplo de Uso

```python
# Inicializar cliente
gemini_client = GeminiApiClient()
gemini_client.initialize()

# Generar contenido para anuncio
ad_content = gemini_client.generate_ad_content(
    job_title="Desarrollador Python Senior",
    job_description="Buscamos un desarrollador con experiencia en Flask, SQLAlchemy y APIs REST...",
    company_name="Magneto365",
    location="Medellín, Colombia"
)

print(f"Headline: {ad_content['headline']}")
print(f"Primary Text: {ad_content['primary_text']}")
print(f"Description: {ad_content['description']}")

# Generar datos simulados
candidate_profile = gemini_client.generate_candidate_profile()
print(f"Candidato generado: {candidate_profile['name']}")
print(f"Habilidades: {', '.join(candidate_profile['skills'])}")
```

### ⚠️ Manejo de Errores

```python
def handle_gemini_api_error(func):
    """Decorador para manejar errores de la API de Gemini."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en Gemini API: {str(e)}")
            # Intentar extraer detalles específicos del error
            if hasattr(e, 'status_code'):
                logger.error(f"Código de estado: {e.status_code}")
            raise
    return wrapper
```

## 🔄 Sincronización de Datos

AdFlux implementa tareas programadas para sincronizar datos con las plataformas externas:

### Sincronización de Meta Ads

```python
@celery.task
def sync_meta_campaigns():
    """Sincroniza el estado y métricas de campañas de Meta Ads."""
    # Implementación...
```

### Sincronización de Google Ads

```python
@celery.task
def sync_google_campaigns():
    """Sincroniza el estado y métricas de campañas de Google Ads."""
    # Implementación...
```

## 🔒 Seguridad y Mejores Prácticas

### Almacenamiento Seguro de Credenciales

- Las credenciales de API se almacenan en variables de entorno, no en el código.
- Se utiliza un archivo `.env` para desarrollo local (no se incluye en el control de versiones).
- Para producción, se recomienda utilizar servicios de gestión de secretos.

### Limitación de Tasa (Rate Limiting)

- Implementación de retrasos y reintentos para respetar los límites de las APIs.
- Monitoreo de cuotas y uso de APIs.

### Validación y Sanitización

- Validación de datos antes de enviarlos a las APIs externas.
- Sanitización de respuestas para prevenir vulnerabilidades.

## 📈 Monitoreo y Logging

AdFlux implementa un sistema de logging detallado para las interacciones con APIs:

```python
def get_logger(name):
    """Configura y devuelve un logger con el nombre especificado."""
    logger = logging.getLogger(name)
    # Configuración adicional...
    return logger
```

Cada llamada a API se registra con:
- Timestamp
- Detalles de la solicitud
- Respuesta o error
- Tiempo de respuesta

## 🔮 Extensibilidad

La arquitectura de AdFlux está diseñada para facilitar la integración con nuevas plataformas publicitarias:

1. Crear un nuevo módulo en `adflux/api/` para la plataforma.
2. Implementar una clase cliente similar a las existentes.
3. Añadir las funcionalidades específicas de la plataforma.
4. Integrar con el sistema de tareas para sincronización.

## 📝 Consideraciones Adicionales

### Manejo de Tokens de Acceso

- Para Meta, se utilizan tokens de acceso de larga duración que deben renovarse manualmente.
- Para Google, se utilizan tokens de actualización que permiten obtener nuevos tokens de acceso automáticamente.

### Compatibilidad con Versiones de API

- Las integraciones están diseñadas para trabajar con versiones específicas de las APIs.
- Se incluyen comentarios sobre la compatibilidad y posibles cambios futuros.

### Pruebas de Integración

- Se incluyen pruebas para verificar la conectividad con las APIs.
- Se utilizan mocks para pruebas unitarias sin depender de las APIs reales.
