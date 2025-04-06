# 🔄 Tareas en Segundo Plano

Este documento describe el sistema de tareas en segundo plano de AdFlux, que utiliza Celery con Redis para ejecutar procesos asíncronos y programados.

## 🎯 Objetivo

El objetivo principal del sistema de tareas en segundo plano es:

1. **Ejecutar procesos largos** sin bloquear la interfaz de usuario
2. **Programar tareas periódicas** para sincronización y mantenimiento
3. **Distribuir la carga** de trabajo en múltiples trabajadores
4. **Mejorar la escalabilidad** del sistema
5. **Garantizar la fiabilidad** mediante reintentos automáticos

## 🧩 Componentes Principales

### 1. Celery

Celery es un sistema de colas de tareas distribuido que AdFlux utiliza para gestionar tareas asíncronas.

```python
# Configuración de Celery en extensions.py
celery = Celery(__name__)

# Configuración de Celery en core/celery_utils.py
def make_celery(app):
    """
    Configura Celery con la aplicación Flask.
    
    Args:
        app: Aplicación Flask.
    """
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=3600,  # 1 hora
        worker_max_tasks_per_child=200,
        worker_prefetch_multiplier=1
    )
    
    # Configurar Beat para tareas programadas
    celery.conf.beat_schedule = {
        'sync-meta-campaigns': {
            'task': 'adflux.tasks.sync_tasks.sync_meta_campaigns',
            'schedule': crontab(minute='*/30'),  # Cada 30 minutos
        },
        'sync-google-campaigns': {
            'task': 'adflux.tasks.sync_tasks.sync_google_campaigns',
            'schedule': crontab(minute='*/30'),  # Cada 30 minutos
        },
        'update-campaign-metrics': {
            'task': 'adflux.tasks.campaign_tasks.update_all_campaign_metrics',
            'schedule': crontab(hour='*/6'),  # Cada 6 horas
        },
        'train-ml-model': {
            'task': 'adflux.tasks.ml_tasks.train_segmentation_model_task',
            'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Lunes a las 3 AM
        }
    }
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
```

### 2. Redis

Redis actúa como broker de mensajes y backend de resultados para Celery.

```python
# Configuración de Redis en config/base.py
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
```

### 3. Tareas de Campaña

El módulo `tasks/campaign_tasks.py` contiene tareas relacionadas con la creación y gestión de campañas publicitarias.

```python
@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def create_meta_campaign_task(self, campaign_id):
    """
    Tarea para crear una campaña en Meta Ads.
    
    Args:
        campaign_id: ID de la campaña en la base de datos.
    
    Returns:
        Dict con el resultado de la operación.
    """
    try:
        # Obtener la campaña de la base de datos
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return {"status": "error", "message": f"Campaña con ID {campaign_id} no encontrada"}
        
        # Obtener el trabajo asociado
        job = campaign.job_opening
        if not job:
            return {"status": "error", "message": "No hay trabajo asociado a esta campaña"}
        
        # Inicializar cliente de Meta
        from adflux.api.meta.client import MetaApiClient
        meta_client = MetaApiClient()
        if not meta_client.initialize():
            return {"status": "error", "message": "No se pudo inicializar el cliente de Meta"}
        
        # Crear campaña en Meta
        from adflux.api.meta.campaigns import create_campaign_flow
        result = create_campaign_flow(meta_client, campaign, job)
        
        # Actualizar campaña en la base de datos
        if result.get("status") == "success":
            campaign.status = "active"
            campaign.external_id = result.get("campaign_id")
            campaign.meta_campaign_id = result.get("campaign_id")
            campaign.meta_ad_set_id = result.get("ad_set_id")
            campaign.meta_ad_id = result.get("ad_id")
            campaign.external_ids = {
                "campaign_id": result.get("campaign_id"),
                "ad_set_id": result.get("ad_set_id"),
                "ad_id": result.get("ad_id")
            }
            db.session.commit()
            
        return result
        
    except Exception as e:
        # Registrar error y reintentar
        current_app.logger.error(f"Error al crear campaña Meta: {str(e)}")
        self.retry(exc=e)
```

### 4. Tareas de Sincronización

El módulo `tasks/sync_tasks.py` contiene tareas para sincronizar datos con plataformas externas.

```python
@celery.task
def sync_meta_campaigns():
    """
    Sincroniza el estado y métricas de campañas de Meta Ads.
    
    Returns:
        Dict con el resultado de la sincronización.
    """
    try:
        # Inicializar cliente de Meta
        from adflux.api.meta.client import MetaApiClient
        meta_client = MetaApiClient()
        if not meta_client.initialize():
            return {"status": "error", "message": "No se pudo inicializar el cliente de Meta"}
        
        # Obtener campañas de Meta en la base de datos
        campaigns = Campaign.query.filter_by(platform='meta').all()
        if not campaigns:
            return {"status": "success", "message": "No hay campañas de Meta para sincronizar"}
        
        results = {
            "total": len(campaigns),
            "updated": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # Sincronizar cada campaña
        for campaign in campaigns:
            if not campaign.external_id:
                results["skipped"] += 1
                continue
                
            try:
                # Obtener estado de la campaña
                from adflux.api.meta.campaigns import get_campaign_status
                status = get_campaign_status(meta_client, campaign.external_id)
                
                # Actualizar estado en la base de datos
                if status and status != campaign.status:
                    campaign.status = status
                    db.session.commit()
                
                # Obtener métricas
                from adflux.api.meta.insights import get_campaign_insights
                insights = get_campaign_insights(meta_client, campaign.external_id)
                
                # Guardar métricas en la base de datos
                if insights:
                    from adflux.api.meta.insights import save_insights_to_db
                    save_insights_to_db(insights, campaign.external_id, 'campaign')
                
                results["updated"] += 1
                
            except Exception as e:
                current_app.logger.error(f"Error al sincronizar campaña {campaign.id}: {str(e)}")
                results["failed"] += 1
        
        return {
            "status": "success",
            "message": f"Sincronización completada: {results['updated']} actualizadas, {results['failed']} fallidas, {results['skipped']} omitidas",
            "details": results
        }
        
    except Exception as e:
        current_app.logger.error(f"Error en sincronización de campañas Meta: {str(e)}")
        return {"status": "error", "message": str(e)}
```

### 5. Tareas de Machine Learning

El módulo `tasks/ml_tasks.py` contiene tareas relacionadas con el entrenamiento y aplicación de modelos de machine learning.

```python
@celery.task
def train_segmentation_model_task():
    """
    Tarea para entrenar el modelo de segmentación de candidatos.
    
    Returns:
        Dict con el resultado del entrenamiento.
    """
    try:
        from adflux.models import Candidate
        from adflux.ml.models import train_segmentation_model
        from adflux.ml.utils import prepare_candidate_data
        
        # Obtener candidatos
        candidates = Candidate.query.all()
        if not candidates:
            return {"status": "error", "message": "No hay candidatos para entrenar el modelo"}
        
        # Preparar datos
        candidates_df = prepare_candidate_data(candidates)
        
        # Entrenar modelo
        kmeans, preprocessor = train_segmentation_model(candidates_df)
        
        # Evaluar modelo
        from adflux.ml.evaluation import evaluate_clustering
        metrics = evaluate_clustering(candidates_df, kmeans.labels_, preprocessor)
        
        return {
            "status": "success", 
            "message": f"Modelo entrenado con {len(candidates)} candidatos",
            "metrics": metrics,
            "n_clusters": kmeans.n_clusters
        }
        
    except Exception as e:
        current_app.logger.error(f"Error al entrenar modelo de segmentación: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery.task
def assign_segments_task():
    """
    Tarea para asignar segmentos a todos los candidatos.
    
    Returns:
        Dict con el resultado de la asignación.
    """
    try:
        from adflux.models import Candidate, db
        from adflux.ml.prediction import assign_segments_to_candidates
        from adflux.ml.utils import prepare_candidate_data
        
        # Obtener candidatos
        candidates = Candidate.query.all()
        if not candidates:
            return {"status": "error", "message": "No hay candidatos para asignar segmentos"}
        
        # Preparar datos
        candidates_df = prepare_candidate_data(candidates)
        
        # Asignar segmentos
        result_df = assign_segments_to_candidates(candidates_df)
        
        # Actualizar base de datos
        updated = 0
        for _, row in result_df.iterrows():
            candidate = Candidate.query.get(row['candidate_id'])
            if candidate:
                candidate.segment_id = int(row['segment'])
                updated += 1
                
        db.session.commit()
        
        return {
            "status": "success",
            "message": f"Segmentos asignados a {updated} candidatos",
            "total_candidates": len(candidates),
            "updated_candidates": updated
        }
        
    except Exception as e:
        current_app.logger.error(f"Error al asignar segmentos: {str(e)}")
        return {"status": "error", "message": str(e)}
```

## 🔄 Flujo de Trabajo

### 1. Definición de Tareas

Las tareas se definen como funciones decoradas con `@celery.task`:

```python
@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def my_task(self, arg1, arg2):
    """Documentación de la tarea."""
    try:
        # Implementación de la tarea
        result = do_something(arg1, arg2)
        return {"status": "success", "result": result}
    except Exception as e:
        # Registrar error y reintentar
        self.retry(exc=e)
```

### 2. Ejecución de Tareas

Las tareas se pueden ejecutar de forma asíncrona desde cualquier parte de la aplicación:

```python
# Ejecutar tarea asíncrona
task = my_task.delay(arg1, arg2)

# Ejecutar tarea con argumentos específicos
task = my_task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': value1})

# Ejecutar tarea con opciones adicionales
task = my_task.apply_async(
    args=[arg1, arg2],
    countdown=10,  # Retrasar 10 segundos
    expires=300,   # Expirar después de 5 minutos
    retry=True,    # Reintentar en caso de fallo
    retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.5,
    }
)
```

### 3. Monitoreo de Tareas

Las tareas se pueden monitorear para conocer su estado y resultado:

```python
# Verificar estado de la tarea
task_id = task.id
task_result = my_task.AsyncResult(task_id)

# Obtener estado
state = task_result.state  # 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE', etc.

# Obtener resultado (bloqueante)
try:
    result = task_result.get(timeout=10)  # Esperar hasta 10 segundos
    print(f"Resultado: {result}")
except celery.exceptions.TimeoutError:
    print("La tarea aún está en ejecución")
```

### 4. Tareas Programadas

Las tareas programadas se configuran en `celery.conf.beat_schedule`:

```python
celery.conf.beat_schedule = {
    'task-name': {
        'task': 'module.path.to.task',
        'schedule': crontab(minute='*/15'),  # Cada 15 minutos
        'args': (arg1, arg2),
        'kwargs': {'kwarg1': value1},
        'options': {'queue': 'high-priority'}
    }
}
```

## 🛠️ Comandos CLI

AdFlux incluye comandos CLI para gestionar las tareas en segundo plano:

```python
@click.command('run-worker')
@click.option('--queues', default='celery', help='Colas a procesar (separadas por comas)')
@click.option('--concurrency', default=4, help='Número de procesos de trabajo')
def run_worker_command(queues, concurrency):
    """Ejecuta un worker de Celery."""
    os.environ.setdefault('FLASK_APP', 'run.py')
    
    click.echo(f"Iniciando worker de Celery para las colas: {queues}")
    click.echo(f"Concurrencia: {concurrency}")
    
    args = [
        'celery',
        '-A', 'adflux.extensions.celery',
        'worker',
        '--loglevel=info',
        f'--concurrency={concurrency}',
        f'--queues={queues}'
    ]
    
    subprocess.run(args)

@click.command('run-beat')
def run_beat_command():
    """Ejecuta el programador de tareas de Celery (beat)."""
    os.environ.setdefault('FLASK_APP', 'run.py')
    
    click.echo("Iniciando programador de tareas de Celery (beat)")
    
    args = [
        'celery',
        '-A', 'adflux.extensions.celery',
        'beat',
        '--loglevel=info'
    ]
    
    subprocess.run(args)

@click.command('run-task')
@click.argument('task_name')
@click.option('--args', help='Argumentos para la tarea (formato JSON)')
@click.option('--kwargs', help='Argumentos con nombre para la tarea (formato JSON)')
@with_appcontext
def run_task_command(task_name, args, kwargs):
    """Ejecuta una tarea específica."""
    try:
        # Importar la tarea
        module_path, task_func = task_name.rsplit('.', 1)
        module = importlib.import_module(module_path)
        task = getattr(module, task_func)
        
        # Parsear argumentos
        task_args = json.loads(args) if args else []
        task_kwargs = json.loads(kwargs) if kwargs else {}
        
        # Ejecutar tarea
        click.echo(f"Ejecutando tarea: {task_name}")
        result = task.delay(*task_args, **task_kwargs)
        
        click.echo(f"Tarea iniciada con ID: {result.id}")
        
    except Exception as e:
        click.echo(f"Error al ejecutar la tarea: {str(e)}", err=True)
```

## 🔍 Consideraciones Técnicas

### Configuración de Celery

AdFlux configura Celery con las siguientes opciones:

- **Serialización**: JSON para compatibilidad y legibilidad
- **Timezone**: UTC para consistencia global
- **Límites de tiempo**: 1 hora por tarea para evitar bloqueos
- **Prefetch**: Multiplicador 1 para distribución equitativa
- **Reintentos**: Configurables por tarea para mayor fiabilidad

### Colas de Tareas

AdFlux utiliza múltiples colas para priorizar diferentes tipos de tareas:

```python
# Definición de colas
task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'high_priority': {
        'exchange': 'high_priority',
        'routing_key': 'high_priority',
    },
    'low_priority': {
        'exchange': 'low_priority',
        'routing_key': 'low_priority',
    },
}

# Asignación de tareas a colas
task_routes = {
    'adflux.tasks.campaign_tasks.create_meta_campaign_task': {'queue': 'high_priority'},
    'adflux.tasks.campaign_tasks.create_google_campaign_task': {'queue': 'high_priority'},
    'adflux.tasks.sync_tasks.*': {'queue': 'low_priority'},
    'adflux.tasks.ml_tasks.*': {'queue': 'low_priority'},
}
```

### Manejo de Errores

AdFlux implementa un manejo robusto de errores en las tareas:

```python
@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def error_handling_example(self, arg):
    try:
        # Intentar ejecutar la tarea
        result = risky_operation(arg)
        return result
    except (TemporaryError, ConnectionError) as e:
        # Reintentar para errores temporales
        current_app.logger.warning(f"Error temporal, reintentando: {str(e)}")
        self.retry(exc=e)
    except Exception as e:
        # Registrar errores permanentes
        current_app.logger.error(f"Error permanente: {str(e)}")
        # Notificar si es crítico
        if is_critical_error(e):
            notify_admin(f"Error crítico en tarea {self.name}: {str(e)}")
        # Re-lanzar para marcar la tarea como fallida
        raise
```

### Contexto de Aplicación

AdFlux asegura que todas las tareas se ejecuten dentro del contexto de la aplicación Flask:

```python
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
```

## 📊 Monitoreo y Logging

### Logging de Tareas

AdFlux implementa un sistema de logging detallado para las tareas:

```python
@celery.task
def logged_task():
    """Tarea con logging detallado."""
    logger = get_task_logger(__name__)
    
    logger.info("Iniciando tarea")
    
    # Registrar pasos importantes
    logger.info("Paso 1: Obteniendo datos")
    data = get_data()
    
    logger.info("Paso 2: Procesando datos")
    result = process_data(data)
    
    logger.info(f"Tarea completada con resultado: {result}")
    return result
```

### Monitoreo con Flower

AdFlux puede utilizar Flower para monitorear las tareas de Celery:

```bash
# Iniciar Flower
celery -A adflux.extensions.celery flower --port=5555
```

Flower proporciona una interfaz web que muestra:
- Estado de los workers
- Tareas activas, pendientes y completadas
- Estadísticas de rendimiento
- Gráficos y métricas

## 🔄 Integración con la Interfaz de Usuario

### Inicio de Tareas desde la UI

AdFlux permite iniciar tareas desde la interfaz de usuario:

```python
@campaign_bp.route('/campaigns/<int:campaign_id>/publish', methods=['POST'])
@login_required
def publish_campaign(campaign_id):
    """Publica una campaña en la plataforma seleccionada."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Verificar que la campaña esté en estado borrador
    if campaign.status != 'draft':
        flash('Solo se pueden publicar campañas en estado borrador.', 'warning')
        return redirect(url_for('campaign.view', campaign_id=campaign_id))
    
    # Iniciar tarea según la plataforma
    if campaign.platform == 'meta':
        task = create_meta_campaign_task.delay(campaign_id)
    elif campaign.platform == 'google':
        task = create_google_campaign_task.delay(campaign_id)
    else:
        flash(f'Plataforma no soportada: {campaign.platform}', 'error')
        return redirect(url_for('campaign.view', campaign_id=campaign_id))
    
    # Guardar ID de tarea para seguimiento
    campaign.task_id = task.id
    campaign.status = 'publishing'  # Estado intermedio
    db.session.commit()
    
    flash('La campaña se está publicando. Este proceso puede tardar unos minutos.', 'info')
    return redirect(url_for('campaign.view', campaign_id=campaign_id))
```

### Seguimiento de Tareas

AdFlux proporciona endpoints para verificar el estado de las tareas:

```python
@api_bp.route('/tasks/<task_id>/status')
def task_status(task_id):
    """Obtiene el estado de una tarea."""
    # Importar AsyncResult de Celery
    from celery.result import AsyncResult
    
    # Obtener resultado de la tarea
    task_result = AsyncResult(task_id)
    
    # Preparar respuesta
    response = {
        'task_id': task_id,
        'state': task_result.state,
        'info': str(task_result.info) if task_result.info else None,
    }
    
    # Añadir resultado si está disponible
    if task_result.successful():
        response['result'] = task_result.get()
    
    return jsonify(response)
```

### Notificaciones de Tareas

AdFlux utiliza WebSockets para notificar a los usuarios sobre el estado de las tareas:

```python
# En el cliente (JavaScript)
const socket = io.connect('/tasks');

socket.on('task_update', function(data) {
    const { task_id, state, result } = data;
    
    // Actualizar UI según el estado de la tarea
    if (state === 'SUCCESS') {
        showSuccess(`Tarea completada: ${result.message}`);
        updateCampaignStatus(result.campaign_id, result.status);
    } else if (state === 'FAILURE') {
        showError(`Error en la tarea: ${result.message}`);
    } else if (state === 'PROGRESS') {
        updateProgressBar(result.percent);
    }
});

// En el servidor (Python con Flask-SocketIO)
@socketio.on('connect', namespace='/tasks')
def connect():
    """Cliente conectado a WebSocket."""
    current_app.logger.info(f"Cliente conectado: {request.sid}")

def send_task_update(task_id, state, result=None):
    """Envía actualización de tarea a los clientes conectados."""
    socketio.emit('task_update', {
        'task_id': task_id,
        'state': state,
        'result': result
    }, namespace='/tasks')
```

## 🔮 Mejoras Futuras

1. **Monitoreo Avanzado**:
   - Implementación de dashboards de monitoreo
   - Alertas automáticas para tareas fallidas
   - Métricas de rendimiento detalladas

2. **Escalabilidad**:
   - Configuración de múltiples workers por cola
   - Balanceo de carga entre workers
   - Priorización dinámica de tareas

3. **Manejo de Fallos**:
   - Políticas de reintento más sofisticadas
   - Fallback automático a alternativas
   - Recuperación de tareas interrumpidas

4. **Optimización**:
   - Ajuste fino de parámetros de rendimiento
   - Compresión de mensajes para reducir tráfico
   - Caché de resultados para tareas repetitivas
