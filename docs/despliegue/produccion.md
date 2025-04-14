# Despliegue en Producción

Esta guía proporciona instrucciones detalladas para desplegar AdFlux en un entorno de producción, asegurando alta disponibilidad, rendimiento y seguridad.

## Requisitos Previos

Antes de comenzar, asegúrate de tener:

- Servidor(es) con sistema operativo Linux (Ubuntu 20.04+ recomendado)
- PostgreSQL 12+ configurado con replicación
- Redis 6+ configurado con persistencia
- Nginx o similar como proxy inverso
- Certificados SSL válidos
- Acceso a las APIs externas (Meta, Google Ads, etc.)
- Dominio configurado con registros DNS

### Requisitos de Hardware Recomendados

| Componente | Mínimo | Recomendado | Alta Carga |
|------------|--------|-------------|------------|
| CPU | 4 cores | 8 cores | 16+ cores |
| RAM | 8 GB | 16 GB | 32+ GB |
| Almacenamiento | 50 GB SSD | 100 GB SSD | 500+ GB SSD |
| Red | 100 Mbps | 1 Gbps | 10 Gbps |

## Arquitectura de Producción

Para un entorno de producción robusto, se recomienda la siguiente arquitectura:

![Arquitectura de Producción](./diagramas/arquitectura-produccion.png)

1. **Balanceador de Carga**: Nginx o HAProxy
2. **Servidores Web**: 2+ instancias de AdFlux
3. **Workers de Celery**: 2+ instancias
4. **Base de Datos**: PostgreSQL con replicación primario-secundario
5. **Redis**: Cluster con persistencia
6. **Almacenamiento**: Sistema de archivos compartido o servicio de almacenamiento en la nube
7. **CDN**: Para archivos estáticos

## Paso 1: Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git redis-server

# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash adflux
sudo usermod -aG sudo adflux

# Crear directorios
sudo mkdir -p /opt/adflux
sudo mkdir -p /var/log/adflux
sudo mkdir -p /var/run/adflux
sudo chown -R adflux:adflux /opt/adflux /var/log/adflux /var/run/adflux
```

## Paso 2: Clonar el Repositorio

```bash
# Cambiar al usuario adflux
sudo su - adflux

# Clonar repositorio
git clone https://github.com/adflux/adflux.git /opt/adflux/app
cd /opt/adflux/app

# Checkout de la versión estable
git checkout v1.0.0  # Reemplazar con la versión actual
```

## Paso 3: Configurar el Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv /opt/adflux/venv

# Activar entorno virtual
source /opt/adflux/venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

## Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en `/opt/adflux/app`:

```
# Configuración de la aplicación
FLASK_APP=adflux
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
DEBUG=False

# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/adflux

# Redis
REDIS_URL=redis://host:puerto/0

# Celery
CELERY_BROKER_URL=redis://host:puerto/1
CELERY_RESULT_BACKEND=redis://host:puerto/1

# APIs externas
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=your_access_token

GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

GEMINI_API_KEY=your_gemini_api_key

# Configuración de correo
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_username
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=noreply@adflux.example.com

# Configuración de seguridad
RATE_LIMIT_GLOBAL=1000
RATE_LIMIT_PERIOD=3600
```

Asegúrate de que el archivo tenga permisos restrictivos:

```bash
chmod 600 /opt/adflux/app/.env
```

## Paso 5: Inicializar la Base de Datos

```bash
# Activar entorno virtual
source /opt/adflux/venv/bin/activate

# Aplicar migraciones
cd /opt/adflux/app
flask db upgrade

# Cargar datos iniciales (opcional)
flask seed --production
```

## Paso 6: Compilar Assets Frontend

```bash
# Instalar dependencias de Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar dependencias frontend
cd /opt/adflux/app
npm install

# Compilar assets para producción
npm run build
```

## Paso 7: Configurar Gunicorn

Crea un archivo de configuración para Gunicorn en `/opt/adflux/app/gunicorn_config.py`:

```python
# Configuración de Gunicorn para AdFlux

# Servidor
bind = "127.0.0.1:8000"
workers = 4  # 2 * núcleos + 1 es una buena regla
worker_class = "gevent"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/adflux/gunicorn-access.log"
errorlog = "/var/log/adflux/gunicorn-error.log"
loglevel = "info"

# Proceso
daemon = False
pidfile = "/var/run/adflux/gunicorn.pid"
user = "adflux"
group = "adflux"

# SSL (si no se usa proxy inverso)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Hooks
def on_starting(server):
    server.log.info("Starting AdFlux server")

def on_exit(server):
    server.log.info("Stopping AdFlux server")
```

## Paso 8: Configurar Supervisor

Crea archivos de configuración para Supervisor:

### Aplicación Web

Crea `/etc/supervisor/conf.d/adflux-web.conf`:

```ini
[program:adflux-web]
command=/opt/adflux/venv/bin/gunicorn -c /opt/adflux/app/gunicorn_config.py "adflux:create_app()"
directory=/opt/adflux/app
user=adflux
group=adflux
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/adflux/web.log
stderr_logfile=/var/log/adflux/web-error.log
environment=PATH="/opt/adflux/venv/bin:%(ENV_PATH)s"
```

### Worker de Celery

Crea `/etc/supervisor/conf.d/adflux-worker.conf`:

```ini
[program:adflux-worker]
command=/opt/adflux/venv/bin/celery -A adflux.celery worker --loglevel=info --concurrency=4
directory=/opt/adflux/app
user=adflux
group=adflux
numprocs=1
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/adflux/worker.log
stderr_logfile=/var/log/adflux/worker-error.log
environment=PATH="/opt/adflux/venv/bin:%(ENV_PATH)s"
```

### Beat de Celery

Crea `/etc/supervisor/conf.d/adflux-beat.conf`:

```ini
[program:adflux-beat]
command=/opt/adflux/venv/bin/celery -A adflux.celery beat --loglevel=info
directory=/opt/adflux/app
user=adflux
group=adflux
numprocs=1
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/adflux/beat.log
stderr_logfile=/var/log/adflux/beat-error.log
environment=PATH="/opt/adflux/venv/bin:%(ENV_PATH)s"
```

Recarga la configuración de Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

## Paso 9: Configurar Nginx

Crea un archivo de configuración para Nginx en `/etc/nginx/sites-available/adflux`:

```nginx
upstream adflux_app {
    server 127.0.0.1:8000;
    # Añadir más servidores si se escala horizontalmente
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name adflux.example.com;
    
    # Redireccionar HTTP a HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name adflux.example.com;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/adflux.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/adflux.example.com/privkey.pem;
    
    # Configuración SSL optimizada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Cabeceras de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;
    
    # Archivos estáticos
    location /static/ {
        alias /opt/adflux/app/adflux/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Archivos de usuario
    location /uploads/ {
        alias /opt/adflux/app/uploads/;
        expires 1d;
        add_header Cache-Control "public, max-age=86400";
    }
    
    # Proxy para la aplicación
    location / {
        proxy_pass http://adflux_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering on;
        proxy_buffer_size 16k;
        proxy_buffers 4 16k;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Configuración para WebSockets (si se utilizan)
    location /socket.io {
        proxy_pass http://adflux_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Logs
    access_log /var/log/nginx/adflux-access.log;
    error_log /var/log/nginx/adflux-error.log;
}
```

Habilita el sitio y reinicia Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/adflux /etc/nginx/sites-enabled/
sudo nginx -t  # Verificar configuración
sudo systemctl restart nginx
```

## Paso 10: Configurar Certificados SSL

Utiliza Certbot para obtener certificados SSL gratuitos de Let's Encrypt:

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d adflux.example.com

# Configurar renovación automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Paso 11: Configurar Firewall

```bash
# Instalar UFW si no está instalado
sudo apt install -y ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Habilitar firewall
sudo ufw enable
```

## Paso 12: Configurar Monitorización

### Prometheus y Grafana

Instala Prometheus para monitorización:

```bash
# Descargar Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.30.3/prometheus-2.30.3.linux-amd64.tar.gz
tar xvfz prometheus-2.30.3.linux-amd64.tar.gz
sudo mv prometheus-2.30.3.linux-amd64 /opt/prometheus

# Crear usuario para Prometheus
sudo useradd -rs /bin/false prometheus
sudo chown -R prometheus:prometheus /opt/prometheus

# Configurar Prometheus
sudo mkdir -p /etc/prometheus
sudo cp /opt/prometheus/prometheus.yml /etc/prometheus/
```

Edita `/etc/prometheus/prometheus.yml` para incluir los targets de AdFlux.

Configura Prometheus como servicio:

```bash
sudo tee /etc/systemd/system/prometheus.service > /dev/null << EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/prometheus/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/opt/prometheus/data \
    --web.console.templates=/opt/prometheus/consoles \
    --web.console.libraries=/opt/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
```

Instala Grafana para visualización:

```bash
# Añadir repositorio de Grafana
sudo apt-get install -y apt-transport-https software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update

# Instalar Grafana
sudo apt-get install -y grafana

# Iniciar Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

## Paso 13: Configurar Copias de Seguridad

Configura copias de seguridad automáticas para la base de datos y archivos:

```bash
# Crear directorio para scripts de backup
sudo mkdir -p /opt/adflux/backup
sudo chown adflux:adflux /opt/adflux/backup

# Crear script de backup
sudo tee /opt/adflux/backup/backup.sh > /dev/null << 'EOF'
#!/bin/bash

# Configuración
BACKUP_DIR="/opt/adflux/backup/data"
DB_NAME="adflux"
DB_USER="adflux_user"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db_$TIMESTAMP.sql.gz"
FILES_BACKUP="$BACKUP_DIR/files_$TIMESTAMP.tar.gz"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de la base de datos
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Backup de archivos
tar -czf $FILES_BACKUP /opt/adflux/app/uploads

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "files_*.tar.gz" -mtime +7 -delete

# Opcional: Sincronizar con almacenamiento externo
# rsync -avz $BACKUP_DIR user@remote:/path/to/backup
EOF

# Hacer ejecutable el script
sudo chmod +x /opt/adflux/backup/backup.sh

# Configurar cron para ejecutar el backup diariamente
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/adflux/backup/backup.sh") | crontab -
```

## Paso 14: Verificar Despliegue

Realiza las siguientes verificaciones:

1. **Verificar servicios**:
   ```bash
   sudo supervisorctl status
   sudo systemctl status nginx
   ```

2. **Verificar logs**:
   ```bash
   tail -f /var/log/adflux/*.log
   ```

3. **Verificar acceso web**:
   Abre `https://adflux.example.com` en un navegador

4. **Verificar API**:
   ```bash
   curl -k https://adflux.example.com/api/health
   ```

## Paso 15: Configurar Escalabilidad

Para escalar horizontalmente, puedes:

1. **Añadir más servidores web**:
   - Configura servidores adicionales siguiendo los pasos 1-7
   - Actualiza la configuración de Nginx para incluir los nuevos servidores en el upstream

2. **Añadir más workers de Celery**:
   - Configura servidores adicionales para workers
   - Ajusta la concurrencia según la capacidad del servidor

3. **Escalar la base de datos**:
   - Configura réplicas de lectura para PostgreSQL
   - Considera utilizar un servicio gestionado como Amazon RDS o Google Cloud SQL

4. **Escalar Redis**:
   - Configura un cluster de Redis para alta disponibilidad
   - Considera utilizar un servicio gestionado como Amazon ElastiCache o Google Cloud Memorystore

## Solución de Problemas

### La aplicación no inicia

Verifica los logs:
```bash
tail -f /var/log/adflux/web-error.log
```

Verifica la configuración:
```bash
source /opt/adflux/venv/bin/activate
cd /opt/adflux/app
flask config --check
```

### Errores de base de datos

Verifica la conexión:
```bash
psql -U adflux_user -h localhost -d adflux
```

Verifica las migraciones:
```bash
source /opt/adflux/venv/bin/activate
cd /opt/adflux/app
flask db current
```

### Errores de Celery

Verifica los logs:
```bash
tail -f /var/log/adflux/worker-error.log
```

Verifica la conexión a Redis:
```bash
redis-cli ping
```

### Errores de Nginx

Verifica la configuración:
```bash
sudo nginx -t
```

Verifica los logs:
```bash
tail -f /var/log/nginx/adflux-error.log
```

## Mantenimiento

### Actualizaciones de Seguridad

Actualiza regularmente el sistema:
```bash
sudo apt update
sudo apt upgrade -y
```

### Actualizaciones de AdFlux

Para actualizar AdFlux:
```bash
# Cambiar al usuario adflux
sudo su - adflux

# Actualizar código
cd /opt/adflux/app
git fetch
git checkout v1.0.1  # Reemplazar con la nueva versión

# Activar entorno virtual
source /opt/adflux/venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt

# Aplicar migraciones
flask db upgrade

# Compilar assets
npm install
npm run build

# Reiniciar servicios
sudo supervisorctl restart all
```

## Recursos Adicionales

- [Documentación de Gunicorn](https://docs.gunicorn.org/)
- [Documentación de Supervisor](http://supervisord.org/configuration.html)
- [Documentación de Nginx](https://nginx.org/en/docs/)
- [Documentación de Let's Encrypt](https://letsencrypt.org/docs/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación de Redis](https://redis.io/documentation)
