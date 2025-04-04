# Fase 5: Despliegue

## Estado Actual: FASE DE PLANIFICACIÓN (10% Completo)

## Puntos Clave

- El sistema AdFlux se desplegará en Google Cloud Platform (GCP), aprovechando sus servicios para aplicaciones Flask, alojamiento de bases de datos y procesamiento en segundo plano.
- La configuración inicial de despliegue se ha documentado en el archivo README.md, con instrucciones detalladas para configurar los recursos necesarios de GCP.
- El plan de despliegue incluye consideraciones para migraciones de bases de datos, variables de entorno y medidas de seguridad.
- Se han documentado opciones de despliegue adicionales para mayor flexibilidad, incluida la contenerización con Docker y proveedores de nube alternativos.

## Estrategia de Despliegue

El sistema AdFlux se desplegará en Google Cloud Platform (GCP), elegido por sus servicios completos, facilidad de uso para aplicaciones Flask y capacidades de escalado automático. Esta estrategia de despliegue garantiza que el sistema sea accesible, escalable y seguro para fines de demostración.

## Implementación Actual

### Documentación de Despliegue

- **README.md**: Se agregaron instrucciones completas de despliegue para Google Cloud Platform
- **Variables de Entorno**: Se documentaron todas las variables de entorno requeridas para el despliegue en producción
- **Configuración de Base de Datos**: Se proporcionaron instrucciones para configurar Cloud SQL para PostgreSQL
- **Opciones de Despliegue Alternativas**: Se agregó documentación para Docker y otros proveedores de nube

### Entorno de Desarrollo Local

- **Servidor de Desarrollo**: Se implementó la configuración del servidor de desarrollo de Flask
- **Soporte SQLite**: Se agregó soporte para la base de datos SQLite para desarrollo local
- **Variables de Entorno**: Se creó una plantilla de archivo .env para la configuración local
- **Configuración de Celery**: Se configuró Celery para el procesamiento de tareas locales

## Arquitectura de Despliegue

### Componentes de la Aplicación

- **Aplicación Web**: Aplicación Flask que sirve la interfaz web y la API
- **Base de Datos**: Base de datos PostgreSQL para almacenar datos de la aplicación
- **Cola de Tareas**: Workers de Celery para procesamiento en segundo plano
- **Planificador**: Celery Beat para tareas programadas
- **Archivos Estáticos**: CSS, JavaScript e imágenes cargadas

### Servicios de Google Cloud Platform

- **App Engine**: Aloja la aplicación Flask
- **Cloud SQL**: Proporciona una base de datos PostgreSQL gestionada
- **Cloud Storage**: Almacena archivos estáticos y cargas
- **Cloud Run**: Ejecuta los workers de Celery (planificado)
- **Memorystore**: Proporciona Redis para el broker de Celery (planificado)
- **Cloud Logging**: Centraliza los logs de la aplicación (planificado)
- **Cloud Monitoring**: Rastrea el rendimiento de la aplicación (planificado)

---

## Plan de Implementación

### Fase 5.1: Configuración de Infraestructura (Semanas 1-2)

**Estado Actual: PLANIFICACIÓN**

- Crear proyecto en Google Cloud Platform
- Configurar instancia de Cloud SQL PostgreSQL
- Configurar buckets de Cloud Storage
- Configurar instancia de Memorystore Redis
- Configurar reglas de red y firewall

### Fase 5.2: Despliegue de la Aplicación (Semanas 3-4)

**Estado Actual: PLANIFICACIÓN**

- Crear archivo de configuración app.yaml
- Configurar variables de entorno en App Engine
- Desplegar aplicación Flask en App Engine
- Ejecutar migraciones de base de datos
- Configurar el servicio de archivos estáticos

### Fase 5.3: Configuración de Procesamiento en Segundo Plano (Semanas 5-6)

**Estado Actual: PLANIFICACIÓN**

- Desplegar workers de Celery en Cloud Run
- Configurar Celery Beat para tareas programadas
- Configurar monitoreo de tareas
- Probar procesamiento asíncrono
- Optimizar configuración de workers

### Fase 5.4: Monitoreo y Logging (Semanas 7-8)

**Estado Actual: PLANIFICACIÓN**

- Configurar Cloud Logging para logs de aplicación
- Configurar Cloud Monitoring para seguimiento de rendimiento
- Crear paneles personalizados para métricas clave
- Configurar alertas para problemas críticos
- Probar monitoreo y alertas

## Lista de Verificación de Despliegue

### Pre-Despliegue

- [ ] Revisar y actualizar requirements.txt
- [ ] Ejecutar todas las pruebas y asegurar que pasen
- [ ] Verificar vulnerabilidades de seguridad en dependencias
- [ ] Preparar scripts de migración de base de datos
- [ ] Crear archivos de configuración específicos para despliegue
- [ ] Documentar todas las variables de entorno
- [ ] Preparar plan de rollback

### Despliegue

- [ ] Crear y configurar recursos de GCP
- [ ] Configurar variables de entorno
- [ ] Desplegar código de la aplicación
- [ ] Ejecutar migraciones de base de datos
- [ ] Desplegar workers de Celery
- [ ] Configurar tareas programadas
- [ ] Configurar monitoreo y logging
- [ ] Configurar copias de seguridad

### Post-Despliegue

- [ ] Verificar funcionalidad de la aplicación
- [ ] Verificar todas las integraciones (Meta, Google Ads)
- [ ] Probar procesamiento en segundo plano
- [ ] Verificar monitoreo y alertas
- [ ] Documentar configuración de despliegue
- [ ] Actualizar documentación con URLs de producción
- [ ] Capacitar a miembros del equipo sobre el proceso de despliegue

#### Introducción

Este documento describe el proceso de despliegue para el sistema Ad Automation P-01 en Google Cloud Platform (GCP), asegurando escalabilidad y fiabilidad. El despliegue aprovecha Google App Engine para la aplicación Flask y Google Cloud SQL para la base de datos PostgreSQL, elegidos por su facilidad de uso, escalado automático y capacidades de integración. El objetivo es lanzar el sistema para uso en producción, haciéndolo accesible a los usuarios mientras se mantiene la seguridad y el rendimiento, alineándose con el cronograma y las restricciones del proyecto universitario.

#### Elección de la Plataforma Cloud

Después de evaluar tanto AWS como Google Cloud, se seleccionó Google Cloud por su simplicidad para desplegar aplicaciones Flask a través de App Engine y su integración perfecta con Cloud SQL para PostgreSQL. La decisión se basó en varios factores:

- **Facilidad de Despliegue:** App Engine ofrece un modelo de plataforma como servicio (PaaS), simplificando el despliegue en comparación con AWS, donde se requeriría la configuración manual de instancias EC2 y balanceadores de carga. Esto está respaldado por tutoriales como [Desplegar una aplicación Flask en Google App Engine](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab), que destacan el proceso sencillo.

- **Costo:** Google Cloud proporciona $300 en créditos para nuevos usuarios, que pueden cubrir los costos de despliegue para un proyecto universitario. El nivel gratuito de App Engine, que ofrece 28 horas de instancia por día, es suficiente para aplicaciones de bajo tráfico, reduciendo aún más los costos. Esto se detalla en [Construir una aplicación Python en App Engine](https://cloud.google.com/appengine/docs/standard/python3/building-app).

- **Escalabilidad y Fiabilidad:** App Engine escala automáticamente según el tráfico, manejando el balanceo de carga y el autoescalado de forma nativa, lo que se alinea con las necesidades del proyecto de escalabilidad durante los momentos pico de demostración. Esto se menciona en [Desplegar una Aplicación Web Python Flask en App Engine Flexible](https://www.cloudskillsboost.google/focuses/3339?parent=catalog).

- **Experiencia del Equipo:** Aunque el proyecto menciona considerar la experiencia del equipo, para un proyecto universitario, aprender GCP es beneficioso, y la documentación es extensa, haciéndolo accesible.

Comparaciones como [Google Cloud vs. AWS: ¿Cuál es mejor para ti?](https://www.prosperops.com/blog/google-cloud-vs-aws/) y [Google Cloud vs AWS: Comparando las Soluciones DBaaS](https://logz.io/blog/google-cloud-vs-aws/) muestran que ambas plataformas son competitivas, pero los servicios gestionados de App Engine reducen la sobrecarga operativa, ajustándose al cronograma.

#### Configuración del Proyecto de Google Cloud

La configuración inicial implica crear y configurar un proyecto GCP:

1.  **Crear un Nuevo Proyecto:**
    -   Navega a la [Consola de Google Cloud](https://console.cloud.google.com/).
    -   Haz clic en "Seleccionar un proyecto" y luego en "Nuevo Proyecto".
    -   Ingresa un nombre de proyecto (p. ej., "AdAutomationP01") y haz clic en "Crear".
    -   Anota el ID del proyecto para usarlo más tarde.

2.  **Habilitar Facturación:**
    -   Asegúrate de que la facturación esté habilitada para el proyecto para usar recursos en la nube. Los nuevos usuarios reciben $300 en créditos, válidos por 90 días, que deberían cubrir la duración del proyecto hasta mayo de 2025. Esto es accesible a través de la sección de Facturación en la consola.

3.  **Habilitar APIs Necesarias:**
    -   Habilita la API de App Engine y la API de Administración de Cloud SQL desde la Biblioteca de APIs para permitir que el proyecto use estos servicios. Esto se puede hacer a través de la sección "APIs y Servicios" > "Biblioteca".

#### Configuración de Cloud SQL para PostgreSQL

La base de datos es crucial para almacenar ofertas de trabajo, perfiles de candidatos y campañas publicitarias. Los pasos de implementación son los siguientes:

1.  **Crear una Instancia de Cloud SQL:**
    -   En la sección Cloud SQL de la consola, haz clic en "Crear Instancia".
    -   Elige "PostgreSQL" como motor de base de datos.
    -   Selecciona la región y zona (p. ej., us-central1) según las necesidades del proyecto, asegurando baja latencia para la demostración.
    -   Elige un ID de instancia (p. ej., "ad-automation-db") y establece una contraseña de root.
    -   Para un proyecto universitario, selecciona un tamaño de instancia pequeño como "db-f1-micro" para minimizar costos, teniendo en cuenta que las instancias de PostgreSQL comienzan en este nivel sin un nivel gratuito pero dentro del límite de crédito.
    -   Haz clic en "Crear" y espera a que la instancia esté lista.

2.  **Configurar Base de Datos:**
    -   Una vez creada la instancia, crea una nueva base de datos dentro de ella (p. ej., "ad_automation_db").
    -   Crea un usuario con los permisos apropiados para la aplicación Flask, estableciendo un nombre de usuario y contraseña.
    -   Anota los detalles de conexión, como el nombre de conexión de la instancia (p. ej., "proyecto:region:instancia").

3.  **Autorizar App Engine:**
    -   En la configuración de la instancia de Cloud SQL, en "Conexiones", agrega la cuenta de servicio predeterminada de App Engine para permitir conexiones desde App Engine. Esto asegura que la aplicación Flask pueda acceder a la base de datos de forma segura.

Esta configuración asegura que la base de datos sea gestionada, escalable e integrada con la aplicación, alineándose con los requisitos del proyecto.

#### Preparación y Despliegue de la Aplicación Flask

La aplicación Flask, desarrollada en fases anteriores, necesita ser desplegada en App Engine para accesibilidad:

1.  **Configuración de Conexión a la Base de Datos:**
    -   Asegúrate de que la aplicación Flask esté configurada para conectarse a Cloud SQL usando el socket Unix para el despliegue en App Engine:

    ```python
    import os
    if os.environ.get('GAE_ENV', '').startswith('standard'):
        db_user = os.environ['DB_USER']
        db_pass = os.environ['DB_PASS']
        db_name = os.environ['DB_NAME']
        db_connection_name = os.environ['DB_CONNECTION_NAME']
        db_config = {
            'user': db_user,
            'password': db_pass,
            'database': db_name,
            'unix_socket': f'/cloudsql/{db_connection_name}'
        }
    else:
        # Configuración de desarrollo local
        db_config = {
            'user': 'local_user',
            'password': 'local_pass',
            'database': 'local_db',
            'host': 'localhost',
            'port': 5432
        }
    ```

    -   Esta configuración asegura que la aplicación se conecte a Cloud SQL en producción y use una base de datos local durante el desarrollo, como se muestra en [Configurar una API usando Flask, Cloud SQL de Google y App Engine](https://www.smashingmagazine.com/2020/08/api-flask-google-cloudsql-app-engine/).

2.  **Archivo de Requisitos:**
    -   Asegúrate de que todas las dependencias estén listadas en `requirements.txt`, incluyendo `psycopg2` para la conexión PostgreSQL, `flask`, `scikit-learn` y cualquier biblioteca API como `facebook-python-business-sdk`. Por ejemplo:

    ```text
    Flask==2.0.1
    psycopg2-binary==2.9.3
    scikit-learn==1.0.2
    facebook-python-business-sdk==14.0.0
    ```

3.  **Configuración de App.yaml:**
    -   Crea un archivo `app.yaml` en la raíz del proyecto para especificar la configuración del runtime:

    ```yaml
    runtime: python39
    entrypoint: gunicorn -b :$PORT main:app
    env_variables:
      DB_USER: 'your_db_user'
      DB_PASS: 'your_db_pass'
      DB_NAME: 'your_db_name'
      DB_CONNECTION_NAME: 'proyecto:region:instancia'
    ```

    -   Reemplaza los placeholders con los valores reales de Cloud SQL. Este archivo configura las variables de entorno para la conexión a la base de datos, como se detalla en [Desplegar Aplicaciones Flask en Google App Engine: Paso a Paso para Principiantes](https://medium.com/@alfininfo/deploy-flask-apps-to-google-app-engine-step-by-step-for-beginners-41ee07e6b2f7).

4.  **Desplegar la Aplicación:**
    -   Instala el SDK de Google Cloud si aún no está instalado, siguiendo la [Guía de Instalación del SDK de Google Cloud](https://cloud.google.com/sdk/docs/install).
    -   Inicializa el proyecto ejecutando `gcloud init`, seleccionando el proyecto creado anteriormente.
    -   Desde el directorio del proyecto, despliega la aplicación:

    ```bash
    gcloud app deploy
    ```

    -   Este comando sube la aplicación a App Engine y la despliega, haciéndola accesible a través de `https://<project-id>.appspot.com`.

5.  **Verificar Despliegue:**
    -   Después del despliegue, accede a la aplicación a través de la URL proporcionada y verifica que todos los endpoints, como GET /job_openings y POST /ad_campaigns, funcionen como se espera.

Este proceso asegura que la aplicación Flask esté desplegada y accesible, aprovechando las características de escalado automático y gestión de App Engine.

#### Configuración de Monitoreo y Logging

El monitoreo y el logging son esenciales para rastrear el rendimiento y detectar problemas, asegurando la fiabilidad:

1.  **Cloud Logging:**
    -   App Engine registra automáticamente solicitudes, errores y logs de aplicación en Cloud Logging, accesible a través de la [Consola Cloud](https://console.cloud.google.com/logging).
    -   Asegúrate de que la aplicación Flask use bibliotecas de logging, como el módulo `logging` de Python, para capturar errores y métricas de rendimiento:

    ```python
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    ```

    -   Visualiza los logs en la consola para monitorear la salud del sistema, alineándose con las mejores prácticas de [Construir una aplicación Python en App Engine](https://cloud.google.com/appengine/docs/standard/python3/building-app).

2.  **Cloud Monitoring:**
    -   Configura paneles de monitoreo en Cloud Monitoring para rastrear métricas como latencia de solicitud, tasas de error y uso de instancias.
    -   Crea alertas para problemas críticos, como altas tasas de error o baja disponibilidad de instancias, a través de la sección de Alertas en Cloud Monitoring.
    -   Esto asegura la detección proactiva de problemas, mejorando la fiabilidad del sistema para la demostración.

#### Configuración de Seguridad

La seguridad es primordial para proteger el sistema y sus datos, especialmente dado el uso de información sensible simulada:

1.  **Conexiones Seguras a la Base de Datos:**
    -   Asegúrate de que Cloud SQL esté configurado para requerir conexiones SSL, habilitado por defecto en Cloud SQL.
    -   Usa el Proxy Cloud SQL para desarrollo local para simular conexiones seguras, asegurando consistencia con producción.

2.  **Roles IAM:**
    -   Asigna roles IAM apropiados a los miembros del equipo, limitando el acceso a los recursos necesarios. Por ejemplo, otorga el rol "App Engine Deployer" para despliegue y "Cloud SQL Client" para acceso a la base de datos.
    -   Usa cuentas de servicio para que App Engine acceda a Cloud SQL y otros servicios, asegurando autenticación segura.

3.  **Reglas de Firewall:**
    -   Configura reglas de firewall VPC para restringir el acceso a la instancia de Cloud SQL, permitiendo solo conexiones desde App Engine. Esto se hace en la sección VPC Network, asegurando que la instancia no sea públicamente accesible.

4.  **HTTPS:**
    -   App Engine aplica HTTPS por defecto para todo el tráfico, asegurando comunicaciones seguras entre usuarios y la aplicación, simplificando la configuración de seguridad en comparación con configuraciones manuales en otras plataformas.

Estas medidas aseguran que el sistema sea seguro, protegiendo datos sensibles y previniendo accesos no autorizados, crítico para un despliegue robusto.

#### Consideraciones de Implementación

Un aspecto interesante es que App Engine maneja automáticamente HTTPS, simplificando la configuración de seguridad en comparación con configuraciones manuales en otras plataformas, lo cual fue inesperado dada la necesidad típica de configuración manual de SSL en despliegues en la nube. Esta variabilidad en la facilidad de despliegue, con los servicios gestionados de App Engine reduciendo la sobrecarga operativa, se alinea con las necesidades del proyecto universitario de un despliegue rápido y fiable para mayo de 2025.

#### Tabla: Resumen de Actividades y Herramientas de Despliegue

| Actividad                          | Descripción                                                                 | Herramientas Usadas                     |
|-----------------------------------|-----------------------------------------------------------------------------|--------------------------------|
| Configurar Proyecto Google Cloud  | Crear proyecto, habilitar facturación y APIs                               | Consola Google Cloud           |
| Configurar Cloud SQL PostgreSQL   | Crear instancia, configurar base de datos, autorizar App Engine             | Cloud SQL, Google Cloud SDK    |
| Desplegar Aplicación Flask       | Preparar app, configurar `app.yaml`, desplegar usando SDK                  | Google Cloud SDK, App Engine   |
| Configurar Monitoreo y Logging   | Configurar Cloud Logging y Monitoring, establecer alertas                   | Cloud Logging, Cloud Monitoring|
| Configurar Seguridad              | Asegurar base de datos, establecer roles IAM, configurar reglas firewall  | IAM, VPC Firewall, Cloud SQL   |

Esta tabla resume las actividades clave de despliegue y herramientas, asegurando claridad para la ejecución.

#### Conclusión

El enfoque de despliegue recomendado para la Fase 5 proporciona un proceso estructurado para lanzar el sistema Ad Automation P-01 en Google Cloud Platform, asegurando escalabilidad, fiabilidad y seguridad. Incluye configurar un proyecto, configurar Cloud SQL y App Engine, desplegar la aplicación Flask, configurar monitoreo y logging, y asegurar medidas de seguridad, resultando en un sistema desplegado accesible a los usuarios para mayo de 2025. La documentación tiene en cuenta las restricciones del proyecto universitario, utilizando datos simulados y centrándose en las funcionalidades principales, con pasos detallados para cada actividad.

### Citas Clave

-   [Construir una aplicación Python en App Engine](https://cloud.google.com/appengine/docs/standard/python3/building-app)
-   [Desplegar una aplicación Flask en Google App Engine](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab)
-   [Desplegar una Aplicación Web Python Flask en App Engine Flexible](https://www.cloudskillsboost.google/focuses/3339?parent=catalog)
-   [Cómo construir una aplicación web usando Flask de Python y Google App Engine](https://www.freecodecamp.org/news/how-to-build-a-web-app-using-pythons-flask-and-google-app-engine-52b1bb82b221)
-   [Configurar una API usando Flask, Cloud SQL de Google y App Engine](https://www.smashingmagazine.com/2020/08/api-flask-google-cloudsql-app-engine/)
-   [Desplegar Aplicaciones Flask en Google App Engine: Paso a Paso para Principiantes](https://medium.com/@alfininfo/deploy-flask-apps-to-google-app-engine-step-by-step-for-beginners-41ee07e6b2f7)
-   [Guía de Instalación del SDK de Google Cloud](https://cloud.google.com/sdk/docs/install)
-   [Google Cloud vs. AWS: ¿Cuál es mejor para ti?](https://www.prosperops.com/blog/google-cloud-vs-aws/)
-   [Google Cloud vs AWS: Comparando las Soluciones DBaaS](https://logz.io/blog/google-cloud-vs-aws/)
-   [Sitio web oficial de Magneto365](https://www.magneto365.com/)
