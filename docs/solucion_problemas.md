# 🔧 Solución de Problemas

Esta guía te ayudará a identificar y resolver problemas comunes que puedes encontrar al usar AdFlux.

## 🚀 Problemas de Inicio y Configuración

### La aplicación no inicia

**Síntoma**: Al ejecutar `python run.py`, la aplicación no inicia o muestra errores.

**Posibles causas y soluciones**:

1. **Entorno virtual no activado**
   ```bash
   # En Windows
   .venv\Scripts\activate
   
   # En macOS/Linux
   source .venv/bin/activate
   ```

2. **Dependencias faltantes**
   ```bash
   pip install -r requirements.txt
   ```

3. **Variables de entorno no configuradas**
   - Verifica que existe un archivo `.env` en la raíz del proyecto
   - Asegúrate de que contiene todas las variables necesarias

4. **Puerto en uso**
   - Cambia el puerto en `run.py`:
     ```python
     app.run(debug=True, host='0.0.0.0', port=5004)  # Cambia a otro puerto
     ```

### Error de conexión a la base de datos

**Síntoma**: La aplicación muestra errores relacionados con la base de datos al iniciar.

**Posibles causas y soluciones**:

1. **URL de base de datos incorrecta**
   - Verifica la variable `DATABASE_URL` en el archivo `.env`
   - Para desarrollo local, usa: `sqlite:///adflux.db`

2. **Tablas no creadas**
   ```bash
   flask db upgrade
   ```

3. **Base de datos corrupta**
   - Elimina el archivo de base de datos SQLite y vuelve a crear las tablas:
     ```bash
     rm adflux.db
     flask db upgrade
     ```

4. **Migraciones desactualizadas**
   ```bash
   flask db stamp head
   flask db migrate
   flask db upgrade
   ```

### Celery no funciona

**Síntoma**: Las tareas en segundo plano no se ejecutan o muestran errores.

**Posibles causas y soluciones**:

1. **Redis no está en ejecución**
   ```bash
   # Verificar si Redis está en ejecución
   redis-cli ping  # Debería responder "PONG"
   
   # Iniciar Redis si no está en ejecución
   redis-server
   ```

2. **Configuración de Celery incorrecta**
   - Verifica las variables `CELERY_BROKER_URL` y `CELERY_RESULT_BACKEND` en `.env`
   - Para desarrollo local, usa: `redis://localhost:6379/0`

3. **Worker de Celery no iniciado**
   ```bash
   celery -A adflux.extensions.celery worker --loglevel=info
   ```

4. **Errores en las tareas**
   - Revisa los logs del worker de Celery para identificar errores específicos

## 🔌 Problemas de Integración con APIs

### Error de autenticación con Meta API

**Síntoma**: Las campañas de Meta no se pueden crear o sincronizar, con errores de autenticación.

**Posibles causas y soluciones**:

1. **Token de acceso expirado**
   - Los tokens de acceso de Meta suelen expirar después de 60 días
   - Genera un nuevo token de acceso en [Meta for Developers](https://developers.facebook.com/)
   - Actualiza la variable `META_ACCESS_TOKEN` en `.env`

2. **Permisos insuficientes**
   - Verifica que el token tenga los permisos necesarios:
     - `ads_management`
     - `ads_read`
     - `business_management`
   - Solicita un token con los permisos adecuados

3. **ID de cuenta de anuncios incorrecto**
   - Verifica que `META_AD_ACCOUNT_ID` en `.env` sea correcto
   - El formato debe ser `act_XXXXXXXXXX`

4. **Límite de API alcanzado**
   - Meta tiene límites de tasa para las llamadas a la API
   - Espera unos minutos e intenta nuevamente
   - Implementa un sistema de reintentos con backoff exponencial

### Error de autenticación con Google Ads API

**Síntoma**: Las campañas de Google Ads no se pueden crear o sincronizar, con errores de autenticación.

**Posibles causas y soluciones**:

1. **Credenciales incorrectas**
   - Verifica todas las variables de Google Ads en `.env`:
     - `GOOGLE_ADS_DEVELOPER_TOKEN`
     - `GOOGLE_ADS_CLIENT_ID`
     - `GOOGLE_ADS_CLIENT_SECRET`
     - `GOOGLE_ADS_REFRESH_TOKEN`
     - `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

2. **Token de actualización expirado**
   - Genera un nuevo token de actualización siguiendo la [documentación oficial](https://developers.google.com/google-ads/api/docs/oauth/overview)

3. **Cuenta de cliente incorrecta**
   - Verifica que `GOOGLE_ADS_TARGET_CUSTOMER_ID` sea correcto
   - Asegúrate de tener permisos para acceder a esa cuenta

4. **Token de desarrollador no aprobado**
   - Los tokens de desarrollador requieren aprobación para producción
   - Para desarrollo, usa una cuenta de prueba

### Error con Gemini API

**Síntoma**: La generación de contenido o simulación de datos falla.

**Posibles causas y soluciones**:

1. **Clave de API incorrecta**
   - Verifica la variable `GEMINI_API_KEY` en `.env`
   - Genera una nueva clave en [Google AI Studio](https://makersuite.google.com/)

2. **Límite de API alcanzado**
   - Gemini tiene límites de uso para cuentas gratuitas
   - Espera hasta que se restablezca tu cuota o actualiza a un plan de pago

3. **Modelo no disponible**
   - Verifica que estés usando un modelo disponible en tu región
   - Cambia a un modelo alternativo si es necesario

## 💾 Problemas de Datos

### Datos duplicados

**Síntoma**: Aparecen registros duplicados de trabajos, candidatos o campañas.

**Posibles causas y soluciones**:

1. **Generación múltiple de datos de simulación**
   - Usa el comando de reinicio de base de datos antes de generar nuevos datos:
     ```bash
     flask reset-db --yes
     flask data generate-jobs 10
     flask data generate-candidates 50
     ```

2. **Sincronización duplicada**
   - Verifica la lógica de sincronización para evitar duplicados
   - Implementa verificaciones de existencia antes de crear nuevos registros

### Datos inconsistentes

**Síntoma**: Los datos mostrados en la interfaz no coinciden con los datos reales o hay inconsistencias entre diferentes secciones.

**Posibles causas y soluciones**:

1. **Caché desactualizada**
   - Limpia la caché del navegador
   - Implementa invalidación de caché después de actualizaciones

2. **Sincronización parcial**
   - Ejecuta una sincronización completa:
     ```bash
     flask sync all
     ```

3. **Transacciones incompletas**
   - Verifica que todas las operaciones de base de datos estén dentro de transacciones
   - Implementa rollbacks en caso de errores

### Errores en la segmentación de candidatos

**Síntoma**: Los candidatos no se asignan a segmentos o se asignan incorrectamente.

**Posibles causas y soluciones**:

1. **Modelo no entrenado**
   - Entrena el modelo de segmentación:
     ```bash
     flask ml train-model
     ```

2. **Datos insuficientes**
   - Asegúrate de tener suficientes candidatos con datos completos
   - Genera más datos de simulación si es necesario

3. **Características faltantes**
   - Verifica que los candidatos tengan todas las características necesarias (habilidades, experiencia, etc.)
   - Completa los datos faltantes

## 🖥️ Problemas de Interfaz de Usuario

### Elementos de la interfaz no se muestran correctamente

**Síntoma**: Botones, formularios o secciones de la interfaz no se muestran o funcionan incorrectamente.

**Posibles causas y soluciones**:

1. **Archivos estáticos no cargados**
   - Verifica que la carpeta `static` esté en la ubicación correcta
   - Comprueba las rutas en las plantillas HTML

2. **Problemas de CSS**
   - Actualiza Tailwind CSS:
     ```bash
     npm run build-css
     ```

3. **Errores de JavaScript**
   - Revisa la consola del navegador para identificar errores
   - Verifica que todos los archivos JS estén incluidos correctamente

4. **Incompatibilidad de navegador**
   - Prueba en diferentes navegadores (Chrome, Firefox, Safari)
   - Implementa polyfills para funcionalidades no soportadas

### Formularios no funcionan

**Síntoma**: Los formularios no se envían o muestran errores al enviar.

**Posibles causas y soluciones**:

1. **Protección CSRF**
   - Asegúrate de incluir el token CSRF en todos los formularios:
     ```html
     <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
     ```

2. **Validación de formularios**
   - Verifica los mensajes de error de validación
   - Asegúrate de que todos los campos requeridos estén completos

3. **Errores en el backend**
   - Revisa los logs del servidor para identificar errores al procesar el formulario

## 🔄 Problemas de Tareas en Segundo Plano

### Las tareas quedan atascadas

**Síntoma**: Las tareas de Celery se inician pero nunca se completan.

**Posibles causas y soluciones**:

1. **Worker bloqueado**
   - Reinicia el worker de Celery:
     ```bash
     pkill -f "celery worker"
     celery -A adflux.extensions.celery worker --loglevel=info
     ```

2. **Tareas con bucles infinitos**
   - Implementa timeouts en todas las tareas:
     ```python
     @celery.task(time_limit=300)  # 5 minutos
     def my_task():
         # ...
     ```

3. **Recursos insuficientes**
   - Verifica el uso de CPU y memoria
   - Aumenta los recursos disponibles o reduce la concurrencia:
     ```bash
     celery -A adflux.extensions.celery worker --loglevel=info --concurrency=2
     ```

### Las tareas programadas no se ejecutan

**Síntoma**: Las tareas programadas con Celery Beat no se ejecutan en los momentos esperados.

**Posibles causas y soluciones**:

1. **Beat no está en ejecución**
   ```bash
   celery -A adflux.extensions.celery beat --loglevel=info
   ```

2. **Configuración de programación incorrecta**
   - Verifica la configuración de `beat_schedule` en `celery_utils.py`
   - Asegúrate de que los horarios estén en UTC

3. **Zona horaria incorrecta**
   - Verifica la configuración de zona horaria de Celery:
     ```python
     celery.conf.update(
         timezone='UTC',
         enable_utc=True
     )
     ```

## 🔒 Problemas de Seguridad y Permisos

### Errores de permisos

**Síntoma**: No se pueden crear archivos o directorios.

**Posibles causas y soluciones**:

1. **Permisos de sistema de archivos**
   ```bash
   # Dar permisos de escritura a directorios clave
   chmod -R 755 adflux/static/uploads
   ```

2. **Usuario incorrecto**
   - Asegúrate de que la aplicación se ejecute con el usuario correcto
   - Verifica los permisos de los archivos y directorios

### Errores de CORS

**Síntoma**: Solicitudes AJAX fallan con errores de CORS.

**Posibles causas y soluciones**:

1. **Configuración de CORS incorrecta**
   - Verifica la configuración de CORS en `app.py`:
     ```python
     CORS(app, resources={r"/api/*": {"origins": "*"}})
     ```

2. **Solicitudes desde dominios no permitidos**
   - Añade los dominios necesarios a la lista de orígenes permitidos

## 📊 Problemas de Rendimiento

### La aplicación es lenta

**Síntoma**: La aplicación tarda mucho en cargar o responder.

**Posibles causas y soluciones**:

1. **Consultas de base de datos ineficientes**
   - Optimiza las consultas con índices adecuados
   - Utiliza eager loading para relaciones:
     ```python
     jobs = JobOpening.query.options(joinedload(JobOpening.campaigns)).all()
     ```

2. **Demasiados datos cargados**
   - Implementa paginación en todas las listas:
     ```python
     page = request.args.get('page', 1, type=int)
     per_page = request.args.get('per_page', 20, type=int)
     jobs = JobOpening.query.paginate(page=page, per_page=per_page)
     ```

3. **Archivos estáticos grandes**
   - Minimiza y comprime archivos CSS y JS
   - Utiliza CDN para bibliotecas externas

4. **Caché insuficiente**
   - Implementa caché para datos que no cambian frecuentemente:
     ```python
     @cache.cached(timeout=300)  # 5 minutos
     def get_dashboard_stats():
         # ...
     ```

### Uso excesivo de memoria

**Síntoma**: La aplicación consume mucha memoria o se cierra inesperadamente.

**Posibles causas y soluciones**:

1. **Fugas de memoria**
   - Verifica que los recursos se liberen correctamente
   - Implementa límites de tamaño para cargas y resultados

2. **Demasiados workers**
   - Reduce el número de workers de Celery:
     ```bash
     celery -A adflux.extensions.celery worker --loglevel=info --concurrency=2
     ```

3. **Procesamiento de datos ineficiente**
   - Procesa datos en lotes en lugar de todos a la vez
   - Utiliza generadores para procesar grandes conjuntos de datos

## 🔍 Herramientas de Diagnóstico

### Logs de la Aplicación

Los logs son la primera fuente de información para diagnosticar problemas:

```bash
# Ver logs de Flask
tail -f flask.log

# Ver logs de Celery
tail -f celery.log
```

### Depuración con Flask

Activa el modo de depuración para obtener información detallada:

```python
# En run.py
app.run(debug=True)
```

### Depuración de Celery

Ejecuta Celery con nivel de log detallado:

```bash
celery -A adflux.extensions.celery worker --loglevel=debug
```

### Monitoreo de Celery con Flower

Flower proporciona una interfaz web para monitorear tareas de Celery:

```bash
celery -A adflux.extensions.celery flower --port=5555
```

Accede a `http://localhost:5555` para ver:
- Estado de los workers
- Tareas activas, pendientes y completadas
- Estadísticas de rendimiento

### Depuración de Base de Datos

Utiliza herramientas SQL para examinar la base de datos directamente:

```bash
# Para SQLite
sqlite3 adflux.db

# Comandos útiles
.tables
.schema job_openings
SELECT * FROM job_openings LIMIT 10;
```

## 📚 Recursos Adicionales

### Documentación Oficial

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación de Celery](https://docs.celeryq.dev/)
- [Documentación de Meta Marketing API](https://developers.facebook.com/docs/marketing-apis/)
- [Documentación de Google Ads API](https://developers.google.com/google-ads/api/docs/start)

### Comunidad y Soporte

- Crea un issue en el repositorio de GitHub
- Contacta al equipo de desarrollo
- Consulta la documentación interna

## 🔄 Procedimientos de Recuperación

### Recuperación de Base de Datos

Si la base de datos se corrompe o necesitas reiniciarla:

```bash
# Hacer copia de seguridad (opcional)
cp adflux.db adflux.db.backup

# Reiniciar base de datos
flask reset-db --yes

# Generar datos de prueba
flask data generate-jobs 10
flask data generate-candidates 50
flask data generate-applications 30
```

### Recuperación de Configuración

Si la configuración se pierde o corrompe:

1. Crea un nuevo archivo `.env` basado en `.env.example`
2. Configura todas las variables necesarias
3. Reinicia la aplicación

### Recuperación de Tareas Atascadas

Si hay tareas de Celery atascadas:

1. Detén todos los workers y beat:
   ```bash
   pkill -f "celery worker"
   pkill -f "celery beat"
   ```

2. Limpia la cola de Redis:
   ```bash
   redis-cli
   > FLUSHDB
   ```

3. Reinicia los workers y beat:
   ```bash
   celery -A adflux.extensions.celery worker --loglevel=info
   celery -A adflux.extensions.celery beat --loglevel=info
   ```

## 🔮 Problemas Conocidos y Soluciones Temporales

### Problema: Inconsistencia en estados de campañas entre plataformas

**Síntoma**: Los estados de las campañas en AdFlux no coinciden con los estados en las plataformas externas.

**Solución temporal**: Sincroniza manualmente las campañas:
```bash
flask sync meta-campaigns
flask sync google-campaigns
```

### Problema: Errores al cargar imágenes grandes

**Síntoma**: Las imágenes grandes no se pueden cargar o causan errores.

**Solución temporal**: Reduce el tamaño de las imágenes antes de cargarlas (máximo 1MB).

### Problema: Segmentación no funciona con pocos candidatos

**Síntoma**: El modelo de segmentación falla o produce resultados pobres con pocos candidatos.

**Solución temporal**: Genera más datos de candidatos simulados:
```bash
flask data generate-candidates 100
```

## 📝 Reporte de Problemas

Si encuentras un problema que no está cubierto en esta guía:

1. Recopila información detallada:
   - Descripción exacta del problema
   - Pasos para reproducirlo
   - Logs relevantes
   - Capturas de pantalla si es aplicable

2. Crea un issue en el repositorio de GitHub con toda la información

3. Etiqueta el issue apropiadamente:
   - `bug` para errores
   - `enhancement` para mejoras
   - `question` para preguntas

4. El equipo de desarrollo revisará y responderá a tu issue lo antes posible
