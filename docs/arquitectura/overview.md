# Visión General de la Arquitectura

AdFlux sigue una arquitectura modular basada en Flask, diseñada para ser escalable, mantenible y extensible. Esta página proporciona una visión general de la arquitectura del sistema.

## Arquitectura de Alto Nivel

AdFlux está estructurado como una aplicación monolítica modular, con componentes claramente separados por responsabilidad. La aplicación sigue un patrón de arquitectura en capas:

![Arquitectura de Alto Nivel](./diagramas/arquitectura-alto-nivel.png)

### Capas Principales

1. **Capa de Presentación**: Interfaces de usuario y APIs.
2. **Capa de Aplicación**: Servicios y lógica de negocio.
3. **Capa de Dominio**: Modelos y reglas de negocio.
4. **Capa de Infraestructura**: Acceso a datos y servicios externos.

## Componentes Principales

### Módulo Web (Flask)

El núcleo de la aplicación es un servidor web Flask que maneja las solicitudes HTTP y renderiza las vistas. Utiliza Jinja2 como motor de plantillas y Tailwind CSS para los estilos.

```python
def create_app(config=None):
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config or Config)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Registrar blueprints
    from adflux.views import register_blueprints
    register_blueprints(app)
    
    return app
```

### Módulos de APIs Externas

AdFlux se integra con varias APIs externas para publicar anuncios en diferentes plataformas:

- **Meta API**: Integración con Facebook e Instagram Ads.
- **Google Ads API**: Integración con Google Ads.
- **TikTok API**: Integración con TikTok Ads.
- **Snapchat API**: Integración con Snapchat Ads.
- **Gemini API**: Integración con Gemini AI para generación de contenido.

Cada módulo de API sigue un patrón similar:

```
meta/
├── __init__.py
├── client.py          # Cliente base para la API
├── campaigns.py       # Operaciones de campañas
├── ad_sets.py         # Operaciones de conjuntos de anuncios
├── ads.py             # Operaciones de anuncios
├── ad_creatives.py    # Operaciones de creativos
├── insights.py        # Obtención de métricas
└── utils.py           # Utilidades comunes
```

### Modelos de Datos

Los modelos de datos están implementados utilizando SQLAlchemy ORM y representan las entidades principales del sistema:

- **User**: Usuarios del sistema.
- **Role/Permission**: Roles y permisos para RBAC.
- **JobOpening**: Ofertas de trabajo.
- **Candidate**: Candidatos para puestos de trabajo.
- **Application**: Solicitudes de candidatos a ofertas.
- **Campaign**: Campañas publicitarias.
- **Modelos específicos por plataforma**: MetaCampaign, GoogleCampaign, etc.

### Servicios

Los servicios implementan la lógica de negocio y actúan como intermediarios entre los controladores y los modelos:

- **CampaignService**: Gestión de campañas publicitarias.
- **JobService**: Gestión de ofertas de trabajo.
- **CandidateService**: Gestión de candidatos.
- **MetricsService**: Obtención y análisis de métricas.
- **ReportService**: Generación de informes.
- **MLService**: Servicios de machine learning.

### Tareas en Segundo Plano

AdFlux utiliza Celery con Redis como broker para ejecutar tareas en segundo plano:

- **Publicación de campañas**: Tareas para publicar campañas en diferentes plataformas.
- **Sincronización de datos**: Tareas para sincronizar datos con APIs externas.
- **Generación de informes**: Tareas para generar informes complejos.
- **Entrenamiento de modelos ML**: Tareas para entrenar modelos de machine learning.

### Machine Learning

AdFlux incorpora componentes de machine learning para:

- **Segmentación de audiencias**: Clustering de candidatos para campañas dirigidas.
- **Optimización de contenido**: Generación y optimización de contenido para anuncios.
- **Predicción de rendimiento**: Modelos para predecir el rendimiento de campañas.

## Patrones de Diseño Utilizados

AdFlux implementa varios patrones de diseño para mejorar la mantenibilidad y extensibilidad:

- **Factory Pattern**: Para la creación de la aplicación Flask.
- **Repository Pattern**: Para el acceso a datos.
- **Service Pattern**: Para encapsular la lógica de negocio.
- **Strategy Pattern**: Para diferentes estrategias de publicación de anuncios.
- **Observer Pattern**: Para notificaciones y eventos.
- **Decorator Pattern**: Para aspectos transversales como logging y caché.

## Flujo de Datos

El flujo de datos típico en AdFlux sigue estos pasos:

1. El usuario interactúa con la interfaz web o API.
2. Los controladores (routes) reciben la solicitud y la validan.
3. Los controladores llaman a los servicios apropiados.
4. Los servicios implementan la lógica de negocio y utilizan repositorios para acceder a los datos.
5. Los servicios pueden llamar a APIs externas o encolar tareas en Celery.
6. Los resultados se devuelven al controlador, que renderiza la vista o devuelve una respuesta JSON.

## Consideraciones de Escalabilidad

La arquitectura de AdFlux está diseñada para escalar horizontalmente:

- **Stateless**: Los componentes son stateless, permitiendo múltiples instancias.
- **Caché**: Implementación de caché para reducir la carga en la base de datos.
- **Tareas asíncronas**: Uso de Celery para operaciones pesadas.
- **Optimización de base de datos**: Índices y consultas optimizadas.

## Próximos Pasos en la Evolución de la Arquitectura

La arquitectura de AdFlux está evolucionando hacia:

1. **Microservicios**: Dividir componentes en servicios independientes.
2. **API Gateway**: Implementar un gateway para gestionar solicitudes a microservicios.
3. **Event-Driven Architecture**: Mayor uso de eventos para comunicación entre componentes.
4. **Contenedorización**: Despliegue completo en contenedores con Kubernetes.
