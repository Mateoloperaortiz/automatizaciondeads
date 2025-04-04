# Fase 3: Documentación de Implementación

Esta sección proporciona un análisis exhaustivo y documentación detallada para la Fase 3: Implementación del proyecto universitario Ad Automation P-01, destinado a automatizar la publicación de anuncios de ofertas de trabajo en plataformas de redes sociales y segmentar audiencias para publicidad dirigida. El sistema está diseñado para integrarse con al menos tres de los siguientes canales: Meta, X, Google, TikTok y Snapchat, y está previsto que forme parte del ecosistema de Magneto, una empresa colombiana especializada en la búsqueda de empleo ([Magneto365](https://www.magneto365.com/)). Sin embargo, dadas las restricciones del proyecto, el usuario trabajará con datos simulados y se centrará en un sistema de prueba de concepto con fecha límite en mayo de 2025, comenzando el 24 de marzo de 2025.

### Introducción

Este documento describe el proceso de implementación para el sistema Ad Automation P-01, utilizando la pila tecnológica recomendada para desarrollar un sistema completamente funcional listo para pruebas. La implementación se desglosa por cada componente de la pila tecnológica, asegurando que todas las partes funcionen juntas sin problemas. Dado el cronograma del proyecto universitario, el enfoque está en las funcionalidades principales, utilizando datos simulados para el desarrollo y las pruebas, y asegurando que el sistema sea desplegable para mayo de 2025.

### Desarrollo del Backend con Python y Flask

El backend es el núcleo del sistema, manejando solicitudes API, lógica de negocio e integraciones. Los pasos de implementación son los siguientes:

- **Configuración de la Aplicación Flask:**
  - Instala Flask y las extensiones necesarias:

    ```bash
    pip install flask flask-restful flask-sqlalchemy flask-migrate
    ```

  - Crea una nueva instancia de aplicación Flask y configúrala:

    ```python
    from flask import Flask
    from flask_restful import Api
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:port/dbname'
    app.config['SECRET_KEY'] = 'your_secret_key'
    db = SQLAlchemy(app)
    api = Api(app)
    ```

  - Organiza la estructura del proyecto con directorios para modelos, vistas, plantillas (si es necesario) y archivos estáticos, asegurando la mantenibilidad.

- **Implementación de APIs RESTful:**
  - Define rutas API usando la clase Resource de Flask-RESTful, creando recursos para ofertas de trabajo, campañas publicitarias y resultados de segmentación. Por ejemplo:

    ```python
    from flask_restful import Resource, reqparse

    class JobOpeningResource(Resource):
        def get(self, id):
            # Obtener oferta de trabajo por id
            pass

        def post(self):
            parser = reqparse.RequestParser()
            parser.add_argument('title', type=str, required=True)
            # Añadir otros campos
            args = parser.parse_args()
            # Crear nueva oferta de trabajo
            pass
    ```

  - Implementa el análisis y la validación de solicitudes para asegurar que los datos entrantes cumplan con el formato esperado, manejando errores con códigos de estado HTTP apropiados y respuestas JSON.
  - Crea endpoints para obtener ofertas de trabajo, gestionar campañas publicitarias y proporcionar resultados de segmentación, alineándose con historias de usuario como ver ofertas de trabajo o iniciar la publicación de anuncios.

- **Comunicación con APIs de Redes Sociales:**
  - Integra bibliotecas de redes sociales en la aplicación Flask para las **plataformas principales (Meta, Google Ads)**. Ejemplo para Meta:
    ```python
    from facebook_business.api import FacebookAdsApi
    FacebookAdsApi.init(access_token='your_access_token')
    ```

  - Gestiona la autenticación almacenando tokens de acceso de forma segura, posiblemente utilizando variables de entorno o AWS Secrets Manager, asegurando el cumplimiento de las mejores prácticas de seguridad.
  - Crea funciones o clases que encapsulen la lógica para crear y gestionar anuncios en cada plataforma, realizando llamadas API según sea necesario. Por ejemplo, implementa una función para crear una campaña publicitaria en Meta, que puede ser llamada desde un endpoint API cuando un usuario inicia la publicación.

Esta implementación asegura que el backend sea modular, escalable y capaz de manejar interacciones de usuario y comunicaciones API externas, alineándose con los requisitos del proyecto de automatización e integración.

### Desarrollo de la CLI

- Implementa una Interfaz de Línea de Comandos (CLI) usando una biblioteca como `click` o `argparse`.
- Define comandos para acciones clave del usuario identificadas en las historias de usuario:
  - `adflux view-jobs`: Lista las ofertas de trabajo simuladas disponibles.
  - `adflux view-candidates [--segment-id ID]`: Lista los candidatos (opcionalmente filtrados por segmento).
  - `adflux view-segments`: Lista los segmentos de ML generados y sus características.
  - `adflux create-campaign --job-id ID --platforms meta,google [--segment-ids S1,S2]`: Inicia la creación de anuncios para un trabajo en plataformas especificadas, dirigiéndose a segmentos específicos.
  - `adflux view-campaigns [--status STATUS]`: Lista las campañas publicitarias creadas.
- Los comandos de la CLI interactuarán con los endpoints API del backend de Flask.

### Gestión de la Base de Datos con PostgreSQL

La base de datos es crucial para almacenar y gestionar datos, asegurando fiabilidad y escalabilidad. Los pasos de implementación son los siguientes:

- **Diseño del Esquema de la Base de Datos:**
  - Define el esquema de la base de datos usando modelos SQLAlchemy, basados en el diseño de la Fase 2. Por ejemplo:

    ```python
    class JobOpening(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        location = db.Column(db.String(100))
        created_at = db.Column(db.DateTime, default=db.func.now())
    ```

  - De manera similar, define modelos para Candidates, AdCampaigns y Logs, estableciendo relaciones como uno a muchos entre JobOpening y AdCampaign.
  - Usa migraciones con Flask-Migrate para gestionar cambios de esquema, asegurando el control de versiones para la base de datos:

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

- **Configuración de PostgreSQL en AWS RDS:**
  - Inicia sesión en la Consola de Administración de AWS y navega a RDS, creando una nueva instancia de base de datos con PostgreSQL como motor.
  - Configura el tamaño de la instancia (p. ej., db.t3.micro para rentabilidad), almacenamiento y ajustes de seguridad, incluyendo la habilitación de la encriptación en reposo.
  - Configura grupos de seguridad para permitir conexiones desde las instancias EC2 donde se ejecuta la aplicación Flask, asegurando la seguridad de la red.
  - Anota el endpoint de la base de datos, el nombre de usuario y la contraseña para la conexión, almacenando las credenciales de forma segura.

- **Conexión desde Flask:**
  - En la aplicación Flask, configura el URI de la base de datos SQLAlchemy con el endpoint y las credenciales de RDS:

    ```python
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@rds-endpoint:5432/dbname'
    ```

  - Usa el ORM de SQLAlchemy para realizar operaciones CRUD en los modelos, asegurando el pooling de conexiones para eficiencia y la gestión de transacciones para la integridad de los datos.
  - Prueba la conexión y realiza operaciones como crear una oferta de trabajo u obtener candidatos, asegurando que la base de datos soporte consultas complejas como la recuperación de datos de audiencia segmentada.

Esta implementación asegura que la base de datos sea robusta, escalable e integrada con el backend de Flask, soportando las necesidades de gestión de datos del sistema.

### Aprendizaje Automático con Scikit-learn

El componente de aprendizaje automático es esencial para la segmentación de audiencias, utilizando aprendizaje no supervisado para agrupar candidatos para publicidad dirigida. Los pasos de implementación son los siguientes:

- **Recopilación y Preprocesamiento de Datos:**
  - Obtén datos de candidatos de la base de datos PostgreSQL usando consultas SQLAlchemy:

    ```python
    candidates = Candidate.query.all()
    df = pd.DataFrame([c.as_dict() for c in candidates])
    ```

  - Preprocesa los datos manejando valores faltantes (p. ej., usando imputación de media para campos numéricos), codificando variables categóricas (p. ej., codificación one-hot para ubicación usando pandas.get_dummies) y escalando características numéricas si es necesario (p. ej., usando StandardScaler de Scikit-learn):

    ```python
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df.select_dtypes(include=['float64', 'int64']))
    ```

- **Selección de Características:**
  - Selecciona características relevantes para la segmentación, como edad, ubicación, nivel educativo y preferencias laborales, basadas en su impacto potencial en la calidad del clustering.
  - Excluye características irrelevantes o redundantes, como IDs internos, para mejorar el rendimiento del modelo, asegurando que las características seleccionadas se alineen con los datos simulados generados en fases anteriores.

- **Entrenamiento del Modelo:**
  - Usa la clase KMeans de Scikit-learn para entrenar un modelo de clustering:

    ```python
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(df_selected)
    ```

  - Determina el número óptimo de clusters usando métodos como el método del codo o el análisis de silueta, iterando para encontrar el mejor ajuste para los datos:

    ```python
    from sklearn.metrics import silhouette_score
    score = silhouette_score(df_selected, kmeans.labels_)
    print(f"Puntuación de Silueta: {score}")
    ```

- **Evaluación del Modelo:**
  - Evalúa el modelo usando métricas como el puntaje de silueta para evaluar qué tan bien separados están los clusters, apuntando a un puntaje cercano a 1 para una buena separación.
  - Opcionalmente, visualiza los clusters usando técnicas de reducción de dimensionalidad como PCA para graficar en 2D, asegurando que los segmentos sean significativos para la segmentación:

    ```python
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    reduced_data = pca.fit_transform(df_selected)
    ```

- **Integración en Flask:**
  - Guarda el modelo entrenado usando joblib para persistencia:

    ```python
    import joblib
    joblib.dump(kmeans, 'kmeans_model.pkl')
    ```

  - Crea una función en la aplicación Flask que cargue el modelo y lo use para predecir el cluster para candidatos nuevos o existentes, integrándolo en un endpoint API:

    ```python
    @app.route('/segment/<int:candidate_id>', methods=['GET'])
    def get_segment(candidate_id):
        model = joblib.load('kmeans_model.pkl')
        candidate = Candidate.query.get_or_404(candidate_id)
        # Preparar datos y predecir cluster
        return jsonify({'segment': model.predict([candidate.features])[0]})
    ```

Esta implementación asegura que el componente de aprendizaje automático esté integrado en el sistema, proporcionando capacidades de segmentación para publicidad dirigida, utilizando datos simulados para el desarrollo.

### Integraciones API con Varias Bibliotecas Python

La implementación se centra en las **dos plataformas principales (Meta, Google Ads)**, con X como objetivo ambicioso.

- **Meta (Facebook):**
  - Usa el `facebook-python-business-sdk` ([Facebook Business SDK for Python](https://github.com/facebook/facebook-python-business-sdk)) para la gestión de anuncios:

    ```python
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount

    FacebookAdsApi.init(access_token='your_access_token')
    account = AdAccount('act_<AD_ACCOUNT_ID>')
    # Crear campaña, etc.
    ```

- **Google Ads:**
  - Usa la biblioteca `google-ads-python` ([Google Ads API Client Library for Python](https://github.com/googleads/google-ads-python)) para manejar operaciones de anuncios:

    ```python
    from google.ads.googleads.client import GoogleAdsClient
    client = GoogleAdsClient.load_from_storage('path/to/config.yaml')
    # Crear campaña, etc.
    ```

- **X (Twitter - Objetivo Ambicioso):**
  - Si el tiempo lo permite después de que las funcionalidades principales estén estables, instala e integra el `twitter-python-ads-sdk`.
  - Implementa autenticación y funciones básicas de creación de anuncios en modo de prueba.

- **TikTok y Snapchat:**
  - Debido a la dependencia de wrappers no oficiales o solicitudes HTTP directas y al apretado cronograma, estos están **fuera de alcance** para la implementación, pero se señalan como posibles mejoras futuras.

- **Implementación General:**
  - Asegura el manejo seguro de claves/tokens API (usando variables de entorno cargadas a través de `app.yaml` en App Engine).
  - Implementa un manejo robusto de errores para llamadas API (tiempos de espera, límites de tasa, errores específicos de API).
  - Estructura las integraciones de forma modular (p. ej., módulos Python separados por plataforma).
  - Céntrate en usar **cuentas de prueba y entornos sandbox** proporcionados por las plataformas.

### Cola de Tareas con Celery (Opcional)

Dado el carácter opcional y el cronograma del proyecto universitario, implementa Celery para tareas en segundo plano para mejorar la capacidad de respuesta del sistema. Los pasos de implementación son los siguientes:

- **Configuración de Celery:**
  - Instala Celery y un message broker como Redis:

    ```bash
    pip install celery redis
    ```

  - Configura Celery con la aplicación Flask, inicializándolo con la URL del broker:

    ```python
    from celery import Celery
    app = Celery('tasks', broker='redis://localhost:6379/0')
    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    ```

- **Definición de Tareas:**
  - Usa el decorador `@celery.task` para definir tareas, como para publicar anuncios:

    ```python
    @app.task
    def publish_ad(job_id, platforms):
        # Obtener oferta de trabajo
        job = JobOpening.query.get(job_id)
        # Lógica para publicar anuncio en cada plataforma
        for platform in platforms:
            if platform == 'meta':
                meta_api.publish_ad(job)
        # Actualizar base de datos
        return True
    ```

  - Define otras tareas para procesar modelos de aprendizaje automático o manejar grandes lotes de datos, asegurando una operación asíncrona.

- **Integración con Flask:**
  - Desde las rutas de Flask, llama a las tareas de Celery usando el método `.delay()`:

    ```python
    from tasks import publish_ad
    @app.route('/publish/<int:job_id>', methods=['POST'])
    def publish_job_ad(job_id):
        platforms = request.json.get('platforms', [])
        publish_ad.delay(job_id, platforms)
        return jsonify({'status': 'processing'}), 202
    ```

  - Asegura que la aplicación Flask pueda manejar los resultados de las tareas, posiblemente usando el backend de resultados de Celery para seguimiento, mejorando la capacidad de respuesta del sistema para las interacciones del usuario.

Esta implementación asegura que las tareas en segundo plano se gestionen eficientemente, descargando operaciones que consumen mucho tiempo y mejorando la experiencia del usuario.

### Consideraciones de Implementación

Un detalle inesperado es la variabilidad en el soporte API entre las plataformas de redes sociales, con Meta y Google Ads ofreciendo bibliotecas Python oficiales, mientras que X puede requerir wrappers no oficiales o solicitudes HTTP directas. Esta variabilidad necesita un diseño de backend flexible, potencialmente usando una capa de abstracción unificada para manejar las diferencias de API, lo que añade complejidad pero asegura una automatización completa para las plataformas elegidas. Dado el cronograma del proyecto universitario, céntrate en las dos plataformas principales para gestionar el alcance.

### Tabla: Resumen de Pasos de Implementación por Componente

| Componente             | Pasos Clave                                                                 | Código/Configuración de Ejemplo                                      |
|-----------------------|---------------------------------------------------------------------------|-----------------------------------------------------------------|
| Backend (Flask)       | Configurar app, implementar APIs, integrar con APIs principales de redes sociales         | `app = Flask(__name__); api.add_resource(JobOpeningResource, '/job_openings')` |
| Base de Datos (PostgreSQL) | Diseñar esquema, configurar Cloud SQL, conectar vía SQLAlchemy                   | `class JobOpening(db.Model): id = db.Column(db.Integer, primary_key=True)` |
| Aprendizaje Automático      | Preprocesar datos, entrenar K-means, integrar en Flask                      | `kmeans = KMeans(n_clusters=5); joblib.dump(kmeans, 'kmeans_model.pkl')` |
| Integraciones API      | Instalar bibliotecas (Meta, Google), autenticar, implementar funciones de anuncio (modo prueba) | `FacebookAdsApi.init(...)` / `GoogleAdsClient.load_from_env()` |
| **CLI**               | **Desarrollar comandos CLI usando `click` o `argparse` para interactuar con la API**   | `adflux create-campaign --job-id 1 --platforms meta,google`     |
| Cola de Tareas (Celery)   | Opcional: Configurar Celery, definir tareas, integrar con Flask             | `celery = Celery(app.name, broker='redis://localhost')`         |

Esta tabla resume los pasos clave de implementación y ejemplos, asegurando claridad para el desarrollo.

### Conclusión

La implementación recomendada para la Fase 3 proporciona un enfoque estructurado para desarrollar el sistema Ad Automation P-01, aprovechando eficazmente la pila tecnológica recomendada. Asegura que todos los componentes estén integrados, desde el backend de Flask hasta el aprendizaje automático, las integraciones API y las tareas opcionales de Celery, resultando en un sistema completamente funcional listo para pruebas para mayo de 2025. La documentación tiene en cuenta las restricciones del proyecto universitario, utilizando datos simulados y centrándose en las funcionalidades principales, con pasos detallados para cada componente.

#### Citas Clave

- [Facebook Business SDK for Python](https://github.com/facebook/facebook-python-business-sdk)
- [Google Ads API Client Library for Python](https://github.com/googleads/google-ads-python)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Guía del Usuario de Scikit-learn](https://scikit-learn.org/stable/user_guide.html)
- [Documentación de AWS](https://docs.aws.amazon.com/)
- [Documentación de Celery](https://docs.celeryproject.org/en/stable/)
