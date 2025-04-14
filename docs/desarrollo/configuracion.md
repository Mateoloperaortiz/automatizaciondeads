# Configuración del Entorno de Desarrollo

Esta guía te ayudará a configurar un entorno de desarrollo local para AdFlux.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git
- Redis (para tareas en segundo plano y caché)
- PostgreSQL (base de datos)
- Node.js y npm (para assets frontend)

### Sistemas Operativos Soportados

- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 34+
- **macOS**: Catalina (10.15)+ 
- **Windows**: 10+ con WSL2 (recomendado) o Git Bash

## Paso 1: Clonar el Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/adflux/adflux.git
cd adflux
```

## Paso 2: Configurar el Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/macOS
source venv/bin/activate
# En Windows
venv\Scripts\activate
```

## Paso 3: Instalar Dependencias

```bash
# Instalar dependencias de Python
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependencias de desarrollo

# Instalar dependencias de frontend
npm install
```

## Paso 4: Configurar la Base de Datos

### Opción A: PostgreSQL Local

```bash
# Crear base de datos
createdb adflux

# Configurar variables de entorno
export DATABASE_URL="postgresql://usuario:contraseña@localhost/adflux"
```

### Opción B: SQLite (para desarrollo rápido)

```bash
# Configurar variables de entorno
export DATABASE_URL="sqlite:///adflux.db"
```

## Paso 5: Configurar Redis

```bash
# Iniciar Redis (si no está ejecutándose como servicio)
redis-server

# Configurar variables de entorno
export REDIS_URL="redis://localhost:6379/0"
```

## Paso 6: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Configuración de la aplicación
FLASK_APP=adflux
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True

# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost/adflux

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# APIs externas (opcional para desarrollo)
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=your_access_token

GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

GEMINI_API_KEY=your_gemini_api_key

# Configuración de correo (opcional para desarrollo)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_username
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=noreply@adflux.example.com
```

## Paso 7: Inicializar la Base de Datos

```bash
# Crear tablas y aplicar migraciones
flask db upgrade

# Cargar datos iniciales (opcional)
flask seed
```

## Paso 8: Compilar Assets Frontend

```bash
# Compilar assets con Webpack
npm run dev
```

## Paso 9: Iniciar Servicios

### Terminal 1: Servidor Flask

```bash
# Iniciar servidor de desarrollo
flask run
```

### Terminal 2: Worker de Celery

```bash
# Iniciar worker de Celery
celery -A adflux.celery worker --loglevel=info
```

### Terminal 3: Beat de Celery (opcional, para tareas programadas)

```bash
# Iniciar beat de Celery
celery -A adflux.celery beat --loglevel=info
```

## Paso 10: Acceder a la Aplicación

Abre tu navegador y visita:

- **Aplicación web**: http://localhost:5000
- **Documentación de API**: http://localhost:5000/api/docs

## Configuración para Desarrollo Avanzado

### Pre-commit Hooks

AdFlux utiliza pre-commit hooks para verificar la calidad del código antes de cada commit.

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install
```

### Configuración de IDE

#### Visual Studio Code

Configuración recomendada para `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.nosetestsEnabled": false,
  "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm

- Instala los plugins para Black y Flake8
- Configura el intérprete de Python para usar el entorno virtual
- Configura el estilo de código para usar PEP 8 con longitud máxima de línea de 100

### Docker (Opcional)

AdFlux también puede ejecutarse en Docker para un entorno de desarrollo más aislado.

```bash
# Construir imagen
docker-compose build

# Iniciar servicios
docker-compose up

# Ejecutar comandos dentro del contenedor
docker-compose exec web flask db upgrade
docker-compose exec web flask seed
```

## Solución de Problemas Comunes

### Error al conectar con la base de datos

- Verifica que PostgreSQL esté en ejecución
- Comprueba las credenciales en `.env`
- Asegúrate de que la base de datos existe

```bash
# Verificar estado de PostgreSQL
sudo service postgresql status

# Crear base de datos si no existe
createdb adflux
```

### Error al conectar con Redis

- Verifica que Redis esté en ejecución
- Comprueba la URL de Redis en `.env`

```bash
# Verificar estado de Redis
redis-cli ping  # Debería responder PONG
```

### Errores de dependencias

- Actualiza pip y reinstala las dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Errores de migración de base de datos

- Elimina la base de datos y vuelve a crearla

```bash
dropdb adflux
createdb adflux
flask db upgrade
```

## Próximos Pasos

Una vez configurado tu entorno de desarrollo, puedes:

1. Explorar la [arquitectura del código](./arquitectura-codigo.md)
2. Revisar la [guía de contribución](./contribucion.md)
3. Aprender sobre los [estándares de código](./estandares-codigo.md)
4. Comenzar a [escribir pruebas](./pruebas.md)

## Recursos Adicionales

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación de Celery](https://docs.celeryproject.org/)
- [Documentación de Redis](https://redis.io/documentation)
