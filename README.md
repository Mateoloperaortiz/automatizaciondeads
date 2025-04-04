# AdFlux - Sistema Automatizado de Publicación de Anuncios

![ChatGPT Image 3 abr 2025, 09_10_29 p m](https://github.com/user-attachments/assets/9d7e8d06-6355-48ef-bca7-007bfe333dcf)

## Descripción General del Proyecto

AdFlux es un proyecto universitario que automatiza la publicación de anuncios de ofertas de trabajo en plataformas de redes sociales. Está diseñado como una prueba de concepto inspirada en las necesidades de plataformas como Magneto365, centrándose en obtener ofertas de trabajo, segmentar audiencias potenciales de candidatos utilizando aprendizaje automático y crear campañas publicitarias dirigidas en plataformas seleccionadas a través de sus API (utilizando entornos sandbox/de prueba).

**Objetivo del Proyecto:** Construir un sistema funcional que demuestre la publicación automatizada de anuncios en plataformas de redes sociales (Meta, Google Ads) basada en datos de trabajos y candidatos, con una interfaz web y una Interfaz de Línea de Comandos (CLI).

**Restricción:** Debido a las limitaciones del proyecto universitario, este sistema utiliza **datos simulados** e interactúa con las API de redes sociales **solo en modos de prueba/sandbox**. No se conecta a sistemas Magneto365 en vivo ni utiliza presupuestos publicitarios reales.

**Cronograma del Proyecto:** Febrero 2025 - Mayo 2025

## Características Clave

- **Gestión de Ofertas de Trabajo**: Crear, ver y gestionar listados de trabajos
- **Gestión de Candidatos**: Realizar seguimiento de perfiles de candidatos y aplicaciones
- **Segmentación con Aprendizaje Automático**: Segmentar automáticamente candidatos utilizando clustering K-means
- **Creación de Campañas**: Crear campañas publicitarias dirigidas para ofertas de trabajo específicas
- **Integración Multiplataforma**: Publicar campañas en Meta (Facebook/Instagram) y Google Ads
- **Seguimiento del Rendimiento**: Monitorear métricas de rendimiento de campañas
- **Interfaz Web**: Panel de control fácil de usar para gestionar todos los aspectos del sistema
- **Herramientas CLI**: Utilidades de línea de comandos para automatización y operaciones por lotes
- **Procesamiento en Segundo Plano**: Manejo asíncrono de tareas para operaciones de larga duración
- **Tareas Programadas**: Operaciones periódicas automatizadas como sincronización de datos y reentrenamiento de modelos

## Tech Stack

### Backend
* **Framework:** Python 3.9+ con Flask
* **API:** Flask-RESTX (con documentación Swagger)
* **Base de Datos:** PostgreSQL (SQLite para desarrollo)
* **ORM:** SQLAlchemy con Flask-SQLAlchemy y Flask-Migrate
* **Cola de Tareas:** Celery con Redis
* **Programador:** Flask-APScheduler
* **Formularios:** Flask-WTF
* **Serialización:** Marshmallow con Flask-Marshmallow

### Machine Learning
* **Framework:** Scikit-learn
* **Algoritmo:** Clustering K-means
* **Procesamiento de Datos:** Pandas, NumPy
* **Persistencia de Modelos:** Joblib

### Integraciones API
* **Meta Ads:** `facebook-python-business-sdk`
* **Google Ads:** `google-ads-python`
* **Generación de Datos:** API de Google Gemini

### Frontend
* **Plantillas:** Jinja2
* **Framework CSS:** Tailwind CSS

### Desarrollo y Despliegue
* **CLI:** Click
* **Entorno:** python-dotenv
* **Pruebas:** Pytest
* **Control de Versiones:** Git y GitHub
* **Objetivo de Despliegue:** Google Cloud Platform

## Estructura del Proyecto

```
AdFlux/
│
├── adflux/                   # Paquete principal de la aplicación
│   ├── __init__.py           # Inicialización del paquete
│   ├── app.py                # Fábrica de la aplicación
│   ├── models.py             # Modelos de datos SQLAlchemy
│   ├── schemas.py            # Esquemas de serialización Marshmallow
│   ├── forms.py              # Definiciones de WTForms
│   ├── config.py             # Configuraciones
│   ├── extensions.py         # Inicialización de extensiones Flask
│   ├── commands.py           # Comandos CLI
│   ├── cli.py                # Funcionalidad CLI adicional
│   ├── api_clients.py        # Funciones cliente API de redes sociales
│   ├── ml_model.py           # Implementación del modelo de aprendizaje automático
│   ├── data_simulation.py    # Generación de datos simulados
│   ├── tasks.py              # Tareas asíncronas Celery
│   ├── sync_tasks.py         # Tareas de sincronización programadas
│   ├── resources.py          # Recursos API
│   ├── main.py               # Punto de entrada
│   │
│   ├── routes/               # Definiciones de rutas
│   │   ├── __init__.py
│   │   ├── main_routes.py    # Rutas de la interfaz web
│   │   ├── job_routes.py     # Rutas API relacionadas con trabajos
│   │   ├── candidate_routes.py # Rutas API relacionadas con candidatos
│   │   ├── application_routes.py # Rutas API relacionadas con aplicaciones
│   │   ├── meta_routes.py    # Rutas API de Meta
│   │   └── task_routes.py    # Rutas de gestión de tareas
│   │
│   ├── static/               # Activos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/          # Imágenes cargadas
│   │
│   └── templates/            # Plantillas HTML Jinja2
│       ├── base.html         # Plantilla base con diseño
│       ├── dashboard.html    # Panel de control principal
│       ├── campaigns_list.html # Listado de campañas
│       ├── campaign_form.html # Formulario de creación de campañas
│       ├── campaign_detail.html # Detalles de la campaña
│       ├── jobs_list.html    # Listado de trabajos
│       ├── job_detail.html   # Detalles del trabajo
│       ├── candidates_list.html # Listado de candidatos
│       ├── candidate_detail.html # Detalles del candidato
│       ├── segmentation.html # Interfaz de segmentación ML
│       └── settings.html     # Configuraciones de la aplicación
│
├── migrations/               # Migraciones de base de datos Flask-Migrate
├── tests/                    # Suite de pruebas
├── phases/                   # Documentos de planificación del proyecto
│   ├── phase1.md            # Fase 1: Análisis de Requisitos
│   ├── phase2.md            # Fase 2: Diseño del Sistema
│   ├── phase3.md            # Fase 3: Implementación
│   ├── phase4.md            # Fase 4: Pruebas
│   ├── phase5.md            # Fase 5: Despliegue
│   ├── phase6.md            # Fase 6: Mantenimiento
│   └── project_plan.md      # Plan general del proyecto
│
├── images/                   # Activos de imágenes para anuncios
├── instance/                 # Datos específicos de la instancia
│   └── ml_models/           # Modelos ML guardados
│
├── .env                      # Variables de entorno
├── .gitignore               # Archivo git ignore
├── populate_db.py           # Script de población de la base de datos
├── requirements.txt         # Dependencias de Python
├── run.py                   # Ejecutor de la aplicación
├── tailwind.config.js       # Configuración de Tailwind CSS
└── README.md                # Esta documentación
```

## Configuración de Desarrollo Local

### Prerrequisitos

* Python 3.9+ y `pip`
* Git
* PostgreSQL (opcional, SQLite funciona para desarrollo)
* Redis (para la cola de tareas Celery)

### Instalación

1. **Clonar Repositorio:**
   ```bash
   git clone https://github.com/Mateoloperaortiz/automatizaciondeads.git
   cd AdFlux
   ```

2. **Crear Entorno Virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # O
   venv\Scripts\activate    # Windows
   ```

3. **Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno:**
   * Copia `.env.example` a `.env`
   * Edita `.env` y completa la configuración requerida:
     ```ini
     # Configuración de Base de Datos
     DATABASE_URL=sqlite:///instance/adflux.db  # Para SQLite (desarrollo)
     # DATABASE_URL=postgresql://<usuario>:<contraseña>@localhost:5432/<nombre_db>  # Para PostgreSQL

     # Configuración de Flask
     FLASK_APP=run.py
     FLASK_ENV=development
     SECRET_KEY=genera_una_clave_aleatoria_segura_aqui

     # Configuración de API Meta (Facebook)
     META_APP_ID=tu_meta_app_id
     META_APP_SECRET=tu_meta_app_secret
     META_ACCESS_TOKEN=tu_meta_access_token
     META_AD_ACCOUNT_ID=act_tu_ad_account_id
     META_PAGE_ID=tu_page_id

     # Configuración de API Google Ads
     GOOGLE_ADS_DEVELOPER_TOKEN=tu_developer_token
     GOOGLE_ADS_CLIENT_ID=tu_client_id
     GOOGLE_ADS_CLIENT_SECRET=tu_client_secret
     GOOGLE_ADS_REFRESH_TOKEN=tu_refresh_token
     GOOGLE_ADS_LOGIN_CUSTOMER_ID=tu_login_customer_id
     GOOGLE_ADS_TARGET_CUSTOMER_ID=tu_target_customer_id
     GOOGLE_ADS_USE_PROTO_PLUS=True

     # API Gemini para Simulación de Datos
     GEMINI_API_KEY=tu_gemini_api_key
     GEMINI_MODEL=models/gemini-2.5-pro-exp-03-25

     # Configuración de Celery
     CELERY_BROKER_URL=redis://localhost:6379/0
     CELERY_RESULT_BACKEND=redis://localhost:6379/0
     ```

5. **Configurar Base de Datos:**
   * Para SQLite (desarrollo):
     ```bash
     flask data_ops create  # Crea las tablas de la base de datos
     ```
   * Para PostgreSQL:
     * Asegúrate de que tu servidor PostgreSQL esté ejecutándose
     * Crea la base de datos especificada en tu archivo `.env`
     * Ejecuta las migraciones de la base de datos:
       ```bash
       flask db upgrade
       ```

6. **Generar Datos Simulados:**
   ```bash
   flask data_ops seed --jobs 20 --candidates 50
   ```
   Este comando poblará la base de datos con 20 ofertas de trabajo simuladas y 50 perfiles de candidatos.

7. **Iniciar Servidor Redis (para Celery):**
   * En Linux/macOS:
     ```bash
     redis-server
     ```
   * En Windows, usa [Redis para Windows](https://github.com/tporadowski/redis/releases) o Docker

## Ejecución de la Aplicación

### Iniciando la Aplicación

1. **Iniciar el Servidor de Desarrollo Flask:**
   ```bash
   flask run
   ```
   La interfaz web será accesible en `http://127.0.0.1:5000`

2. **Iniciar Trabajador Celery (en una terminal separada):**
   ```bash
   celery -A adflux.extensions.celery worker --loglevel=info
   ```
   Esto procesará tareas en segundo plano como la publicación de campañas y la sincronización de datos.

3. **Iniciar Celery Beat para Tareas Programadas (opcional, en una terminal separada):**
   ```bash
   celery -A adflux.extensions.celery beat --loglevel=info
   ```
   Esto manejará tareas programadas como el reentrenamiento periódico de modelos y la sincronización de datos.

### Usando la Interfaz Web

La interfaz web proporciona un panel de control completo para gestionar todos los aspectos del sistema:

1. **Panel de Control** (`/`): Vista general de campañas, trabajos y candidatos
2. **Campañas** (`/campaigns`): Crear, ver y gestionar campañas publicitarias
3. **Trabajos** (`/jobs`): Ver y gestionar ofertas de trabajo
4. **Candidatos** (`/candidates`): Ver y gestionar perfiles de candidatos
5. **Segmentación** (`/segmentation`): Ver y gestionar segmentos de candidatos
6. **Configuración** (`/settings`): Configurar credenciales API y otras configuraciones

### Usando la CLI

La aplicación proporciona varios comandos CLI para automatización y operaciones por lotes:

```bash
# Operaciones de Base de Datos
flask data_ops create  # Crear tablas de base de datos
flask data_ops seed --jobs 20 --candidates 50  # Poblar base de datos con datos de ejemplo

# Gestión de Trabajos
flask jobs list  # Listar todas las ofertas de trabajo
flask jobs view --id JOB-0001  # Ver detalles de un trabajo específico

# Gestión de Candidatos
flask candidates list  # Listar todos los candidatos
flask candidates view --id CAND-0001  # Ver detalles de un candidato específico
flask candidates segment  # Ejecutar segmentación en todos los candidatos

# Gestión de Campañas
flask campaigns list  # Listar todas las campañas
flask campaigns create --job-id JOB-0001 --platform meta  # Crear una campaña
flask campaigns publish --id 1  # Publicar una campaña en la plataforma especificada
flask campaigns sync --platform meta  # Sincronizar datos de campaña desde Meta

# Operaciones ML
flask ml train  # Entrenar el modelo de segmentación
flask ml predict  # Aplicar el modelo para segmentar candidatos
```

## Pruebas

### Ejecutando Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar módulos de prueba específicos
pytest tests/test_models.py

# Ejecutar con salida detallada
pytest -v

# Ejecutar con informe de cobertura
pytest --cov=adflux
```

### Estructura de Pruebas

La suite de pruebas está organizada en las siguientes categorías:

* **Pruebas Unitarias**: Probar componentes individuales de forma aislada
* **Pruebas de Integración**: Probar interacciones entre componentes
* **Pruebas API**: Probar endpoints API
* **Pruebas ML**: Probar funcionalidad del modelo de aprendizaje automático
* **Pruebas End-to-End**: Probar flujos de trabajo completos

## Despliegue

### Google Cloud Platform (GCP)

1. **Prerrequisitos:**
   * Google Cloud SDK instalado y configurado
   * Proyecto GCP creado con facturación habilitada
   * API requeridas habilitadas (App Engine, Cloud SQL, etc.)

2. **Configuración de Base de Datos:**
   * Crear una instancia de Cloud SQL PostgreSQL
   * Crear una base de datos y un usuario con los permisos adecuados
   * Anotar los detalles de conexión para los próximos pasos

3. **Configuración:**
   * Crear un archivo `app.yaml` con el siguiente contenido:
     ```yaml
     runtime: python39
     entrypoint: gunicorn -b :$PORT run:app

     env_variables:
       DATABASE_URL: postgresql+pg8000://USUARIO:CONTRASEÑA@/BASEDATOS?unix_sock=/cloudsql/NOMBRE_CONEXION_INSTANCIA/.s.PGSQL.5432
       SECRET_KEY: tu_clave_secreta_de_produccion
       META_APP_ID: tu_meta_app_id
       META_APP_SECRET: tu_meta_app_secret
       META_ACCESS_TOKEN: tu_meta_access_token
       META_AD_ACCOUNT_ID: tu_meta_ad_account_id
       META_PAGE_ID: tu_meta_page_id
       GOOGLE_ADS_DEVELOPER_TOKEN: tu_google_ads_developer_token
       GOOGLE_ADS_CLIENT_ID: tu_google_ads_client_id
       GOOGLE_ADS_CLIENT_SECRET: tu_google_ads_client_secret
       GOOGLE_ADS_REFRESH_TOKEN: tu_google_ads_refresh_token
       GOOGLE_ADS_LOGIN_CUSTOMER_ID: tu_google_ads_login_customer_id
       GOOGLE_ADS_TARGET_CUSTOMER_ID: tu_google_ads_target_customer_id
       GOOGLE_ADS_USE_PROTO_PLUS: "True"
       GEMINI_API_KEY: tu_gemini_api_key
       GEMINI_MODEL: models/gemini-2.5-pro-exp-03-25
       CELERY_BROKER_URL: redis://10.0.0.1:6379/0
       CELERY_RESULT_BACKEND: redis://10.0.0.1:6379/0

     beta_settings:
       cloud_sql_instances: NOMBRE_CONEXION_INSTANCIA
     ```

4. **Desplegar la Aplicación:**
   ```bash
   # Autenticar (si es necesario)
   gcloud auth login

   # Establecer el proyecto
   gcloud config set project TU_ID_PROYECTO_GCP

   # Desplegar la aplicación
   gcloud app deploy app.yaml
   ```

5. **Migraciones de Base de Datos:**
   ```bash
   # Establecer variables de entorno para la migración
   export DATABASE_URL=postgresql+pg8000://USUARIO:CONTRASEÑA@/BASEDATOS?unix_sock=/cloudsql/NOMBRE_CONEXION_INSTANCIA/.s.PGSQL.5432

   # Ejecutar migraciones
   flask db upgrade
   ```

6. **Configurar Trabajadores Celery:**
   * Desplegar trabajadores Celery usando Cloud Run o Compute Engine
   * Configurar Redis usando Memorystore o un proveedor Redis de terceros

### Otras Opciones de Despliegue

* **Docker**: Contenerizar la aplicación usando Docker y desplegar en cualquier plataforma de orquestación de contenedores
* **Heroku**: Desplegar usando la CLI de Heroku con add-ons de PostgreSQL y Redis
* **AWS**: Desplegar usando Elastic Beanstalk con RDS para PostgreSQL y ElastiCache para Redis

## Componente de Aprendizaje Automático

AdFlux utiliza aprendizaje automático para segmentar candidatos en grupos para publicidad dirigida. La implementación utiliza clustering K-means para agrupar candidatos según sus perfiles.

### Proceso de Segmentación

1. **Preparación de Datos**:
   * Los perfiles de los candidatos se cargan desde la base de datos
   * Se extraen características como ubicación, años de experiencia, nivel educativo, habilidades y salario deseado
   * Las características categóricas se codifican mediante one-hot
   * Las características numéricas se estandarizan

2. **Entrenamiento del Modelo**:
   * Se aplica el algoritmo de clustering K-means a los datos procesados
   * El número de clústeres (segmentos) es configurable (predeterminado: 5)
   * El modelo se entrena para minimizar la distancia intra-clúster

3. **Asignación de Segmentos**:
   * Cada candidato es asignado a un segmento según los resultados del clustering
   * La información del segmento se almacena en la base de datos
   * A los segmentos se les dan nombres descriptivos basados en sus características

4. **Segmentación Dirigida**:
   * Al crear campañas publicitarias, se pueden dirigir segmentos específicos
   * Esto permite una publicidad más relevante y efectiva

### Usando el Componente ML

```bash
# Entrenar el modelo de segmentación
flask ml train --clusters 5

# Aplicar el modelo para segmentar candidatos
flask ml predict

# Analizar características del segmento
flask ml analyze
```

## Integraciones API

AdFlux se integra con múltiples plataformas de publicidad en redes sociales a través de sus API.

### API de Anuncios Meta (Facebook/Instagram)

* Utiliza la biblioteca `facebook-python-business-sdk`
* Admite la creación de campañas, conjuntos de anuncios, anuncios y audiencias personalizadas
* Maneja autenticación, manejo de errores y sincronización de datos
* Proporciona insights y métricas de rendimiento

### API de Google Ads

* Utiliza la biblioteca `google-ads-python`
* Admite la creación de campañas, grupos de anuncios y anuncios
* Maneja autenticación y manejo de errores
* Proporciona informes de rendimiento

### Simulación de Datos con API Gemini

* Utiliza la API Gemini de Google para generar datos realistas de trabajos y candidatos
* Crea títulos de trabajo, descripciones y requisitos variados
* Genera perfiles de candidatos diversos con diferentes habilidades y niveles de experiencia

## Documentación del Proyecto

### Documentación del Código

* Los docstrings siguen la Guía de Estilo Python de Google
* Los endpoints API están documentados usando Swagger a través de Flask-RESTX
* Las funciones complejas incluyen explicaciones detalladas y ejemplos

### Planificación del Proyecto

Los documentos de planificación detallados para cada fase se encuentran en el directorio `/phases`:

* `project_plan.md`: Plan general del proyecto y enfoque
* `phase1.md`: Análisis de Requisitos y Planificación
* `phase2.md`: Diseño del Sistema
* `phase3.md`: Implementación
* `phase4.md`: Pruebas
* `phase5.md`: Despliegue
* `phase6.md`: Mantenimiento y Monitoreo

## Contribuyendo

1. Haz un fork del repositorio
2. Crea una rama de característica: `git checkout -b feature/tu-nombre-de-caracteristica`
3. Confirma tus cambios: `git commit -am 'Añadir alguna característica'`
4. Empuja a la rama: `git push origin feature/tu-nombre-de-caracteristica`
5. Envía una pull request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## Agradecimientos

* Este proyecto fue desarrollado por Mateo Lopera, Maria Fernanda Alvarez, Emmanuel Hernandez y Yesid Rivera como parte de Ingenieria de Software 2025-1.
