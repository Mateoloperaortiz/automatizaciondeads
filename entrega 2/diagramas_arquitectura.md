# Diagramas de Arquitectura - AdFlux

## Vista Lógica - Diagrama de Clases de Diseño

```mermaid
classDiagram
    class Application {
        -Flask app
        +create_app()
        +configure_scheduled_jobs()
    }
    
    class Config {
        +SECRET_KEY: str
        +SQLALCHEMY_DATABASE_URI: str
        +CELERY_BROKER_URL: str
        +META_APP_ID: str
        +GEMINI_API_KEY: str
    }
    
    class JobOpening {
        +id: int
        +title: str
        +description: str
        +requirements: str
        +location: str
        +salary_range: str
        +status: str
        +created_at: datetime
        +updated_at: datetime
        +get_active_jobs()
        +to_dict()
    }
    
    class Candidate {
        +id: int
        +name: str
        +email: str
        +phone: str
        +resume_url: str
        +skills: str
        +experience: str
        +education: str
        +segment_id: int
        +created_at: datetime
        +updated_at: datetime
        +to_dict()
    }
    
    class Campaign {
        +id: int
        +name: str
        +description: str
        +job_id: int
        +target_segment_id: int
        +budget: float
        +start_date: datetime
        +end_date: datetime
        +status: str
        +meta_campaign_id: str
        +created_at: datetime
        +updated_at: datetime
        +to_dict()
    }
    
    class Segment {
        +id: int
        +name: str
        +description: str
        +criteria: str
        +created_at: datetime
        +updated_at: datetime
        +to_dict()
    }
    
    class MetaInsight {
        +id: int
        +account_id: str
        +metric_name: str
        +metric_value: float
        +date: datetime
        +created_at: datetime
        +to_dict()
    }
    
    class MetaAdSet {
        +id: int
        +campaign_id: int
        +meta_adset_id: str
        +name: str
        +status: str
        +daily_budget: float
        +targeting: str
        +created_at: datetime
        +updated_at: datetime
        +to_dict()
    }
    
    class MLModel {
        +train_segmentation_model()
        +predict_segment()
        +analyze_segments_from_db()
        +save_model()
        +load_model()
    }
    
    class APIClient {
        +test_meta_api_connection()
        +create_meta_campaign()
        +get_meta_insights()
        +generate_job_description()
    }
    
    class CeleryTasks {
        +publish_campaign_to_meta()
        +sync_meta_insights()
        +run_candidate_segmentation()
    }
    
    JobOpening "1" -- "many" Campaign: has
    Campaign "1" -- "1" Segment: targets
    Candidate "many" -- "1" Segment: belongs to
    Campaign "1" -- "many" MetaAdSet: contains
    Application -- Config: uses
    Application -- CeleryTasks: schedules
    CeleryTasks -- APIClient: uses
    CeleryTasks -- MLModel: uses
```

El diagrama de clases muestra los componentes principales del sistema AdFlux y sus relaciones:

- **Application**: Representa la aplicación Flask y su configuración
- **Config**: Contiene la configuración del sistema
- **Modelos de datos**: JobOpening, Candidate, Campaign, Segment, MetaInsight, MetaAdSet
- **MLModel**: Componente de aprendizaje automático para segmentación de candidatos
- **APIClient**: Integración con APIs externas (Meta, Google Gemini)
- **CeleryTasks**: Tareas asíncronas para procesamiento en segundo plano

## Vista Lógica - Diagrama Entidad-Relación (Modelo de datos)

```mermaid
erDiagram
    JOB_OPENING {
        int id PK
        string title
        text description
        text requirements
        string location
        string salary_range
        string status
        datetime created_at
        datetime updated_at
    }
    
    CANDIDATE {
        int id PK
        string name
        string email
        string phone
        string resume_url
        text skills
        text experience
        text education
        int segment_id FK
        datetime created_at
        datetime updated_at
    }
    
    SEGMENT {
        int id PK
        string name
        text description
        text criteria
        datetime created_at
        datetime updated_at
    }
    
    CAMPAIGN {
        int id PK
        string name
        text description
        int job_id FK
        int target_segment_id FK
        float budget
        datetime start_date
        datetime end_date
        string status
        string meta_campaign_id
        datetime created_at
        datetime updated_at
    }
    
    META_AD_SET {
        int id PK
        int campaign_id FK
        string meta_adset_id
        string name
        string status
        float daily_budget
        text targeting
        datetime created_at
        datetime updated_at
    }
    
    META_INSIGHT {
        int id PK
        string account_id
        string metric_name
        float metric_value
        datetime date
        datetime created_at
    }
    
    APPLICATION {
        int id PK
        int candidate_id FK
        int job_id FK
        string status
        text notes
        datetime applied_at
        datetime created_at
        datetime updated_at
    }
    
    JOB_OPENING ||--o{ CAMPAIGN : "has"
    JOB_OPENING ||--o{ APPLICATION : "receives"
    CANDIDATE ||--o{ APPLICATION : "submits"
    CANDIDATE }o--|| SEGMENT : "belongs to"
    CAMPAIGN }o--|| SEGMENT : "targets"
    CAMPAIGN ||--o{ META_AD_SET : "contains"
```

El diagrama entidad-relación muestra la estructura de la base de datos relacional de AdFlux:

- **JOB_OPENING**: Almacena información sobre ofertas de trabajo
- **CANDIDATE**: Contiene datos de candidatos
- **SEGMENT**: Define segmentos de candidatos para targeting
- **CAMPAIGN**: Campañas publicitarias asociadas a ofertas de trabajo
- **META_AD_SET**: Conjuntos de anuncios en Meta Ads
- **META_INSIGHT**: Métricas y estadísticas de campañas en Meta
- **APPLICATION**: Aplicaciones de candidatos a ofertas de trabajo

## Vista Física - Diagrama de Despliegue

```mermaid
graph TD
    subgraph "Entorno de Producción"
        A[Cliente Web] -->|HTTPS| B[Servidor Web - Nginx]
        B -->|WSGI| C[Aplicación Flask]
        C -->|SQL| D[(Base de Datos PostgreSQL)]
        C -->|Redis| E[Cola de Tareas Redis]
        E -->|Consume| F[Trabajadores Celery]
        F -->|API| G[Meta Ads API]
        F -->|API| H[Google Gemini API]
        C -->|Almacena| I[Sistema de Archivos]
        I -->|Modelos ML| J[Modelos Entrenados]
        I -->|Uploads| K[Archivos de Usuario]
    end
    
    subgraph "Servicios Externos"
        G
        H
    end
```

El diagrama de despliegue muestra cómo se distribuyen los componentes de AdFlux en la infraestructura física:

- **Cliente Web**: Interfaz de usuario accesible a través de navegadores
- **Servidor Web (Nginx)**: Maneja las solicitudes HTTP y sirve archivos estáticos
- **Aplicación Flask**: Implementa la lógica de negocio y las APIs
- **Base de Datos PostgreSQL**: Almacena datos persistentes
- **Cola de Tareas Redis**: Gestiona tareas asíncronas
- **Trabajadores Celery**: Procesan tareas en segundo plano
- **APIs Externas**: Meta Ads y Google Gemini
- **Sistema de Archivos**: Almacena modelos ML y archivos subidos por usuarios

Este diseño permite una arquitectura escalable y modular, donde cada componente puede escalar independientemente según las necesidades.
