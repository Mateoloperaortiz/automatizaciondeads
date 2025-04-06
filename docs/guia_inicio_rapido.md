# 🚀 Guía de Inicio Rápido

¡Bienvenido a AdFlux! Esta guía te ayudará a configurar y comenzar a usar la aplicación rápidamente.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Redis (para tareas en segundo plano con Celery)
- Git (para clonar el repositorio)

## 🔧 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Mateoloperaortiz/automatizaciondeads.git
cd automatizaciondeads
```

### 2. Crear y Activar Entorno Virtual

```bash
# En Windows
python -m venv .venv
.venv\Scripts\activate

# En macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Configuración de Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui

# Configuración de Base de Datos
DATABASE_URL=sqlite:///adflux.db

# Configuración de Meta (Facebook) API
META_APP_ID=tu_app_id
META_APP_SECRET=tu_app_secret
META_ACCESS_TOKEN=tu_access_token
META_AD_ACCOUNT_ID=tu_ad_account_id
META_PAGE_ID=tu_page_id

# Configuración de Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=tu_developer_token
GOOGLE_ADS_CLIENT_ID=tu_client_id
GOOGLE_ADS_CLIENT_SECRET=tu_client_secret
GOOGLE_ADS_REFRESH_TOKEN=tu_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=tu_login_customer_id
GOOGLE_ADS_TARGET_CUSTOMER_ID=tu_target_customer_id

# Configuración de Gemini API
GEMINI_API_KEY=tu_api_key
```

### 5. Inicializar la Base de Datos

```bash
python reset_db.py
```

### 6. Iniciar Redis (para Celery)

```bash
# En una terminal separada
redis-server
```

### 7. Iniciar Celery Worker (opcional, para tareas en segundo plano)

```bash
# En una terminal separada
celery -A adflux.extensions.celery worker --loglevel=info
```

### 8. Ejecutar la Aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5003`.

## 🏗️ Estructura del Proyecto

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

## 🧪 Simulación de Datos

Para generar datos de prueba y explorar la aplicación:

```bash
# Generar datos de trabajos
flask data generate-jobs 10

# Generar datos de candidatos
flask data generate-candidates 50

# Generar aplicaciones de candidatos a trabajos
flask data generate-applications 30
```

## 🚀 Primeros Pasos

Una vez que la aplicación esté en funcionamiento, puedes:

1. Acceder al panel de control en `http://localhost:5003/dashboard`
2. Explorar las ofertas de trabajo en `http://localhost:5003/jobs`
3. Ver los perfiles de candidatos en `http://localhost:5003/candidates`
4. Crear y gestionar campañas publicitarias en `http://localhost:5003/campaigns`
5. Configurar la integración con Meta y Google en `http://localhost:5003/settings`

## 🔍 ¿Qué Sigue?

Ahora que tienes AdFlux funcionando, puedes:

- Explorar la [Arquitectura del Sistema](./arquitectura.md) para entender cómo funciona
- Aprender sobre los [Modelos de Datos](./modelos_datos.md) para comprender la estructura de la información
- Revisar las [APIs e Integraciones](./apis_integraciones.md) para conocer cómo se conecta con servicios externos

¡Disfruta usando AdFlux! 🎉
