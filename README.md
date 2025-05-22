# 🚀 AdFlux - ¡Automatiza tus Anuncios de Empleo como un Pro

<div align="center">

![AdFlux Logo](https://github.com/user-attachments/assets/aefa1ea3-5a20-4930-8127-f858f2ce0a8b)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Meta API](https://img.shields.io/badge/Meta%20API-Integrado-blue.svg?logo=facebook&logoColor=white)](https://developers.facebook.com/docs/marketing-apis/)
[![Google Ads](https://img.shields.io/badge/Google%20Ads-Integrado-red.svg?logo=google&logoColor=white)](https://developers.google.com/google-ads/api/docs/start)
[![ML](https://img.shields.io/badge/Machine%20Learning-K--means-green.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

</div>

## 💡 ¿Qué es AdFlux?

**AdFlux** es tu aliado para revolucionar la forma en que publicas ofertas de trabajo en redes sociales. ¿Cansado de publicar anuncios manualmente? ¡Olvídate de eso! Con AdFlux, automatizas todo el proceso desde la creación hasta el seguimiento de tus campañas.

Desarrollado como proyecto universitario inspirado en las necesidades de plataformas como Magneto365, AdFlux te permite:

- 📊 **Gestionar ofertas de trabajo** de forma centralizada
- 🧠 **Segmentar candidatos automáticamente** con inteligencia artificial
- 📱 **Publicar anuncios** en Meta (Facebook/Instagram) y Google Ads con un solo clic
- 📈 **Analizar el rendimiento** de tus campañas en tiempo real

> **Nota:** Este proyecto utiliza **datos simulados** y APIs en modo sandbox/prueba. No conecta con sistemas reales de Magneto365 ni utiliza presupuestos publicitarios reales.

**Proyecto desarrollado:** Febrero 2025 - Mayo 2025

## ✨ Características Alucinantes

<div class="features-grid">

### 🏢 Gestión de Empleos

- Crea y gestiona ofertas de trabajo con descripciones detalladas
- Organiza tus vacantes por categoría, ubicación y nivel de experiencia
- Visualiza el estado de cada oferta en tiempo real

### 👥 Gestión de Talentos

- Mantiene una base de datos organizada de candidatos
- Realiza seguimiento de aplicaciones y entrevistas
- Filtra candidatos por habilidades, experiencia y ubicación

### 🧠 IA para Segmentación

- Agrupa automáticamente candidatos usando clustering K-means
- Identifica patrones ocultos en los perfiles de candidatos
- Optimiza tus campañas según características de cada segmento
- Incorpora algoritmos adicionales como DBSCAN para segmentación avanzada

### 📱 Publicación Multi-Plataforma

- Publica anuncios en Meta (Facebook/Instagram) con un clic
- Crea campañas en Google Ads sin salir de la aplicación
- Gestiona todas tus campañas desde un solo lugar

### 📊 Análisis en Tiempo Real

- Monitorea el rendimiento de tus campañas al instante
- Visualiza métricas clave con gráficos interactivos
- Genera informes personalizados para tomar mejores decisiones

### ⚡ Automatización Total

- Tareas en segundo plano con Celery y Redis
- Sincronización automática de datos con las plataformas
- Programación de tareas recurrentes sin intervención manual

### 💰 Automatización de Presupuesto con Stripe
- Gestiona métodos de pago y planes de presupuesto para campañas
- Redistribuye automáticamente presupuestos basado en rendimiento
- Monitorea transacciones y generación de informes de gastos
- Envía alertas cuando se alcanzan umbrales de presupuesto configurados

### 🧠 Recomendaciones Inteligentes
- Genera recomendaciones personalizadas para optimizar campañas
- Sugiere distribuciones de presupuesto según rendimiento histórico
- Analiza patrones de plataformas para recomendar canales efectivos
- Proporciona insights sobre mejoras de segmentación y creatividades

</div>

## 💻 Tech Stack

<div class="tech-stack">

<div class="tech-category">

### 🔥 Backend

- **Framework:** ![Python](https://img.shields.io/badge/Python%203.9+-3776AB?style=flat-square&logo=python&logoColor=white) + ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
- **API:** ![Flask-RESTX](https://img.shields.io/badge/Flask--RESTX-009688?style=flat-square&logo=flask&logoColor=white) con documentación Swagger
- **Base de Datos:** ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) (SQLite para desarrollo)
- **ORM:** ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
- **Cola de Tareas:** ![Celery](https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white) con ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)

</div>

<div class="tech-category">

### 🧠 Machine Learning

- **Framework:** ![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
- **Algoritmo:** Clustering K-means
- **Procesamiento:** ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) + ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)

</div>

<div class="tech-category">

### 🔗 Integraciones API

- **Meta Ads:** `facebook-python-business-sdk`
- **Google Ads:** `google-ads-python`
- **IA Generativa:** ![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=flat-square&logo=google&logoColor=white)
- **Pagos:** ![Stripe](https://img.shields.io/badge/Stripe-008CDD?style=flat-square&logo=stripe&logoColor=white)

</div>

<div class="tech-category">

### 📺 Frontend

- **Plantillas:** ![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=flat-square&logo=jinja&logoColor=white)
- **CSS:** ![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)

</div>

<div class="tech-category">

### 🛠️ Herramientas de Desarrollo

- **CLI:** ![Click](https://img.shields.io/badge/Click-4B48EF?style=flat-square&logo=python&logoColor=white)
- **Pruebas:** ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
- **Despliegue:** ![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=flat-square&logo=google-cloud&logoColor=white)

</div>

</div>

## Estructura del Proyecto

```
AdFlux/
│
├── adflux/                   # Paquete principal de la aplicación
│   ├── __init__.py           # Inicialización del paquete
│   ├── core/                 # Componentes principales de la aplicación
│   │   ├── __init__.py       # Inicialización del paquete core
│   │   ├── factory.py        # Fábrica de la aplicación
│   ├── models/               # Modelos de datos
│   │   ├── __init__.py       # Inicialización del paquete models
│   │   ├── job.py            # Modelos relacionados con empleos
│   │   ├── candidate.py      # Modelos relacionados con candidatos
│   │   ├── campaign.py       # Modelos relacionados con campañas
│   │   ├── payment.py        # Modelos relacionados con pagos y presupuestos
│   ├── services/             # Servicios de lógica de negocio
│   │   ├── campaign_service.py # Servicio de campañas
│   │   ├── payment_service.py  # Servicio de pagos y presupuestos
│   │   ├── recommendation_service.py # Servicio de recomendaciones
│   ├── api/                  # Componentes API externos
│   │   ├── meta/             # Integración con Meta Ads API
│   │   ├── google/           # Integración con Google Ads API
│   │   ├── gemini/           # Integración con API de Gemini
│   │   │   ├── content_generation.py # Generación de creatividades
│   ├── ml/                   # Componentes de machine learning
│   │   ├── segmentation/     # Algoritmos de segmentación
│   │   │   ├── kmeans_segmentation.py # Segmentación con K-means
│   │   │   ├── dbscan_segmentation.py # Segmentación con DBSCAN
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

- Python 3.9+ y `pip`
- Git
- PostgreSQL (opcional, SQLite funciona para desarrollo)
- Redis (para la cola de tareas Celery)

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
   - Copia `.env.example` a `.env`
   - Edita `.env` y completa la configuración requerida:

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
     
     # Configuración de Stripe
     STRIPE_API_KEY=tu_stripe_api_key
     STRIPE_WEBHOOK_SECRET=tu_stripe_webhook_secret
     STRIPE_PUBLIC_KEY=tu_stripe_public_key
     
     # Configuración de Celery
     CELERY_BROKER_URL=redis://localhost:6379/0
     CELERY_RESULT_BACKEND=redis://localhost:6379/0
     ```

5. **Configurar Base de Datos:**
   - Para SQLite (desarrollo):

     ```bash
     flask data_ops create  # Crea las tablas de la base de datos
     ```

   - Para PostgreSQL:
     - Asegúrate de que tu servidor PostgreSQL esté ejecutándose
     - Crea la base de datos especificada en tu archivo `.env`
     - Ejecuta las migraciones de la base de datos:

       ```bash
       flask db upgrade
       ```

6. **Generar Datos Simulados:**

   ```bash
   flask data_ops seed --jobs 20 --candidates 50
   ```

   Este comando poblará la base de datos con 20 ofertas de trabajo simuladas y 50 perfiles de candidatos.

7. **Iniciar Servidor Redis (para Celery):**
   - En Linux/macOS:

     ```bash
     redis-server
     ```

   - En Windows, usa [Redis para Windows](https://github.com/tporadowski/redis/releases) o Docker

## Ejecución de la Aplicación

### Iniciando la Aplicación

1. **Iniciar el Servidor de Desarrollo Flask:**

   ```bash
   python run.py
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

# Gestión de Pagos y Presupuestos
flask payments list  # Listar métodos de pago registrados
flask budgets list   # Listar planes de presupuesto
flask budgets redistribute --id 1  # Redistribuir presupuesto basado en rendimiento

# Operaciones ML
flask ml train  # Entrenar el modelo de segmentación
flask ml predict  # Aplicar el modelo para segmentar candidatos
```

## Calidad de Código y Pruebas

### Linting y Formateo

AdFlux utiliza varias herramientas para mantener la calidad y consistencia del código:

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar todas las herramientas de linting
python lint.py --all

# Formatear código automáticamente
python lint.py --black-fix

# Verificar tipos con mypy
python lint.py --mypy

# Verificar estilo de documentación
python lint.py --pydocstyle
```

También puedes configurar pre-commit para ejecutar estas verificaciones automáticamente antes de cada commit:

```bash
pre-commit install
```

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

- **Pruebas Unitarias**: Probar componentes individuales de forma aislada
- **Pruebas de Integración**: Probar interacciones entre componentes
- **Pruebas API**: Probar endpoints API
- **Pruebas ML**: Probar funcionalidad del modelo de aprendizaje automático
- **Pruebas End-to-End**: Probar flujos de trabajo completos

## Despliegue

### Google Cloud Platform (GCP)

1. **Prerrequisitos:**
   - Google Cloud SDK instalado y configurado
   - Proyecto GCP creado con facturación habilitada
   - API requeridas habilitadas (App Engine, Cloud SQL, etc.)

2. **Configuración de Base de Datos:**
   - Crear una instancia de Cloud SQL PostgreSQL
   - Crear una base de datos y un usuario con los permisos adecuados
   - Anotar los detalles de conexión para los próximos pasos

3. **Configuración:**
   - Crear un archivo `app.yaml` con el siguiente contenido:

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
   - Desplegar trabajadores Celery usando Cloud Run o Compute Engine
   - Configurar Redis usando Memorystore o un proveedor Redis de terceros

### Otras Opciones de Despliegue

- **Docker**: Contenerizar la aplicación usando Docker y desplegar en cualquier plataforma de orquestación de contenedores
- **Heroku**: Desplegar usando la CLI de Heroku con add-ons de PostgreSQL y Redis
- **AWS**: Desplegar usando Elastic Beanstalk con RDS para PostgreSQL y ElastiCache para Redis

## Automatización de Presupuesto con Stripe

AdFlux incorpora una integración completa con Stripe para automatizar la gestión de presupuesto de campañas publicitarias.

### Características Principales

1. **Gestión de Métodos de Pago**:
   - Registro y gestión de tarjetas y otros métodos de pago
   - Configuración de método de pago predeterminado
   - Procesamiento seguro mediante Stripe Elements

2. **Planes de Presupuesto**:
   - Creación de planes con presupuestos diarios o totales
   - Asignación de campañas a planes de presupuesto
   - Configuración de límites y alertas de gasto

3. **Redistribución Inteligente**:
   - Análisis de rendimiento de campañas (CTR, CPC, conversiones)
   - Reasignación automática basada en métricas de rendimiento
   - Optimización continua del gasto publicitario

4. **Informes de Gastos**:
   - Seguimiento detallado de transacciones
   - Generación de informes por período, campaña o plataforma
   - Exportación de datos para análisis externos

## Componente de Aprendizaje Automático

AdFlux utiliza aprendizaje automático para segmentar candidatos en grupos para publicidad dirigida. La implementación incluye múltiples algoritmos de clustering para adaptarse a diferentes tipos de datos y casos de uso.

### Proceso de Segmentación

1. **Preparación de Datos**:
   - Los perfiles de los candidatos se cargan desde la base de datos
   - Se extraen características como ubicación, años de experiencia, nivel educativo, habilidades y salario deseado
   - Las características categóricas se codifican mediante one-hot
   - Las características numéricas se estandarizan

2. **Entrenamiento de Modelos**:
   - **K-Means**: Se aplica para segmentación general de candidatos (configuración predeterminada: 5 clusters)
   - **DBSCAN**: Se utiliza para detectar grupos de densidad variable y valores atípicos
   - El número óptimo de clusters se determina automáticamente mediante métricas de evaluación
   - Se generan perfiles detallados para cada segmento

3. **Asignación de Segmentos**:
   - Cada candidato es asignado a un segmento según los resultados del clustering
   - La información del segmento se almacena en la base de datos
   - A los segmentos se les dan nombres descriptivos basados en sus características

4. **Segmentación Dirigida**:
   - Al crear campañas publicitarias, se pueden dirigir segmentos específicos
   - Esto permite una publicidad más relevante y efectiva

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

- Utiliza la biblioteca `facebook-python-business-sdk`
- Admite la creación de campañas, conjuntos de anuncios, anuncios y audiencias personalizadas
- Maneja autenticación, manejo de errores y sincronización de datos
- Proporciona insights y métricas de rendimiento

### API de Google Ads

- Utiliza la biblioteca `google-ads-python`
- Admite la creación de campañas, grupos de anuncios y anuncios
- Maneja autenticación y manejo de errores
- Proporciona informes de rendimiento

### Simulación de Datos con API Gemini

- Utiliza la API Gemini de Google para generar datos realistas de trabajos y candidatos
- Crea títulos de trabajo, descripciones y requisitos variados
- Genera perfiles de candidatos diversos con diferentes habilidades y niveles de experiencia

### Generación de Contenido con Gemini

- Utiliza la API Gemini de Google para generar contenido creativo para anuncios
- Crea títulos principales, subtítulos y descripciones optimizadas para anuncios
- Genera descripciones completas de trabajo con responsabilidades y requisitos
- Personaliza el contenido según diferentes plataformas y audiencias objetivo
- Permite configurar parámetros como temperatura para controlar creatividad

## Documentación del Proyecto

### Documentación del Código

- Los docstrings siguen la Guía de Estilo Python de Google
- Los endpoints API están documentados usando Swagger a través de Flask-RESTX
- Las funciones complejas incluyen explicaciones detalladas y ejemplos

### Planificación del Proyecto

Los documentos de planificación detallados para cada fase se encuentran en el directorio `/phases`:

- `project_plan.md`: Plan general del proyecto y enfoque
- `phase1.md`: Análisis de Requisitos y Planificación
- `phase2.md`: Diseño del Sistema
- `phase3.md`: Implementación
- `phase4.md`: Pruebas
- `phase5.md`: Despliegue
- `phase6.md`: Mantenimiento y Monitoreo

## Contribuyendo

1. Haz un fork del repositorio
2. Crea una rama de característica: `git checkout -b feature/tu-nombre-de-caracteristica`
3. Confirma tus cambios: `git commit -am 'Añadir alguna característica'`
4. Empuja a la rama: `git push origin feature/tu-nombre-de-caracteristica`
5. Envía una pull request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## 👏 Agradecimientos

<div align="center">

### ✨ Desarrollado con 💜 por

| ![Mateo](https://img.shields.io/badge/Mateo%20Lopera-Developer-blue) | ![Maria](https://img.shields.io/badge/Maria%20Fernanda%20Alvarez-Developer-pink) | ![Emmanuel](https://img.shields.io/badge/Emmanuel%20Hernandez-Developer-green) | ![Yesid](https://img.shields.io/badge/Yesid%20Rivera-Developer-orange) |
|:---:|:---:|:---:|:---:|

**Proyecto Universitario de Ingeniería de Software 2025-1**

[![Universidad](https://img.shields.io/badge/Universidad-EAFIT-red?style=for-the-badge&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAEQSURBVHgBjZLNTcNAEIXfrJMGkCgAUQG4AqACTAdJB0kHpAPSQUIFQAXYqQBKgA7sVEDm24myJpF50tPOz36z4/XKRCfqdf0sZ9c9pZS+Igs5B7mFLKVSI8ySPJGpCgGdYGYpheQOnIRUJTLJcMptCKjAA/lJjGNoSzLJ8MhNDOjAA/lZjGNoRzLJ8MpNE9CBB/KrGMfQnmSS4Y2bNqADD+Q3MY6hA8kkwwc3XUAHHsjvYhxDR5JJhk9uTgEdeCB/iHEM/ZJMMnxx0wd04IH8KcYx9EcyyfDNzRDQgQfylxjH0JlkkuGHmzGgAw/kbzGOoQvJJMMvNz6gAw/kixjH0D/JJEPxMPQBdOCB/CPGMfQgmWQo/gGRzU6YQJy6SQAAAABJRU5ErkJggg==)](https://www.eafit.edu.co/)

</div>
