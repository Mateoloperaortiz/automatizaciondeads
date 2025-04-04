# Fase 6: Mantenimiento y Monitoreo

## Estado Actual: FASE DE PLANIFICACIÓN

## Puntos Clave

- El sistema AdFlux requiere mantenimiento y monitoreo continuos para garantizar un rendimiento, seguridad y fiabilidad óptimos.
- Hemos implementado capacidades iniciales de monitoreo y estamos planificando un monitoreo exhaustivo utilizando herramientas de Google Cloud.
- Se planean actualizaciones regulares, correcciones de errores y mejoras de funciones basadas en comentarios y métricas de rendimiento.
- El reentrenamiento del modelo de aprendizaje automático se programa periódicamente para mejorar la precisión de la segmentación.

## Descripción General del Mantenimiento del Sistema

El sistema AdFlux, que actualmente se está preparando para su despliegue en Google Cloud Platform, requiere un enfoque de mantenimiento estructurado para garantizar que funcione sin problemas. Esto incluye monitorear métricas de rendimiento, abordar problemas con prontitud, mantener las dependencias actualizadas e implementar mejoras planificadas.

## Implementación Actual

### Monitoreo y Logging

- **Logging de Aplicación**: Se implementó un logging exhaustivo en toda la aplicación utilizando el módulo de logging de Python
- **Seguimiento de Errores**: Se configuró el manejo de errores con mensajes de error detallados y seguimientos de pila
- **Monitoreo de Tareas**: Se implementó el seguimiento del estado de las tareas de Celery con informes de progreso
- **Métricas de Rendimiento**: Se agregaron métricas básicas de tiempo para operaciones críticas

### Mantenimiento de Base de Datos

- **Framework de Migración**: Se implementó Flask-Migrate para cambios en el esquema de la base de datos
- **Estrategia de Backup**: Se diseñaron procedimientos de backup automatizados para el despliegue en producción
- **Limpieza de Datos**: Se implementaron utilidades para eliminar datos obsoletos o de prueba

### Gestión de Dependencias

- **Archivo de Requisitos**: Se mantuvo actualizado el archivo requirements.txt con versiones específicas
- **Entorno Virtual**: Se utilizaron entornos virtuales para aislamiento y reproducibilidad

## Mejoras Planificadas

### Monitoreo y Rendimiento

- **Google Cloud Monitoring**: Implementaremos Cloud Monitoring para rastrear métricas de salud del sistema:
  - Latencia y rendimiento de solicitudes
  - Tasas y tipos de error
  - Utilización de recursos (CPU, memoria, disco)
  - Rendimiento de la base de datos

- **Seguimiento del Rendimiento de Campañas**: Incluso con datos simulados, rastrearemos métricas de rendimiento de campañas publicitarias:
  - Impresiones, clics y conversiones
  - Costo por clic (CPC) y costo por adquisición (CPA)
  - Alcance y participación de la audiencia
  - Comparación del rendimiento de segmentos

- **Sistema de Alertas**: Configuraremos alertas para problemas críticos:
  - Problemas de disponibilidad del servicio
  - Tasas de error inusuales
  - Degradación del rendimiento
  - Limitaciones de cuota de API

### Resolución de Problemas y Actualizaciones

- **Seguimiento de Problemas**: Todos los errores y solicitudes de funciones se registrarán en GitHub Issues
- **Integración Continua**: Implementar pipeline CI/CD utilizando GitHub Actions o Google Cloud Build
- **Actualizaciones de Dependencias**: Programa regular para actualizar bibliotecas y dependencias de Python
- **Parches de Seguridad**: Sistema de prioridad para abordar vulnerabilidades de seguridad

### Mantenimiento del Aprendizaje Automático

- **Reentrenamiento del Modelo**: Programar reentrenamiento periódico del modelo de segmentación:
  - Reentrenamiento mensual con nuevos datos de candidatos
  - Evaluación del rendimiento utilizando el puntaje de silueta y otras métricas
  - Control de versiones para modelos ML

- **Mejoras en Ingeniería de Características**: Planificar la mejora del conjunto de características basada en el análisis de rendimiento
- **Monitoreo del Modelo**: Rastrear la deriva del modelo y la calidad de la segmentación a lo largo del tiempo

### Documentación y Base de Conocimiento

- **Documentación del Sistema**: Mantener documentación exhaustiva de la arquitectura y componentes del sistema
- **Documentación de API**: Mantener la documentación de Swagger actualizada con cualquier cambio en la API
- **Guías de Usuario**: Crear y actualizar guías para administradores de sistemas y usuarios finales
- **Guía de Solución de Problemas**: Desarrollar una base de conocimiento de problemas comunes y sus soluciones

---

## Plan de Implementación

### Fase 6.1: Configuración de Monitoreo (Semanas 1-2)

**Estado Actual: PLANIFICACIÓN**

- Configurar Google Cloud Monitoring para la aplicación desplegada
- Configurar métricas personalizadas para la funcionalidad específica de AdFlux
- Implementar agregación y análisis de logs
- Crear paneles para indicadores clave de rendimiento
- Configurar alertas para problemas críticos

### Fase 6.2: Procedimientos de Mantenimiento (Semanas 3-4)

**Estado Actual: PLANIFICACIÓN**

- Establecer un programa regular de mantenimiento
- Implementar procedimientos de mantenimiento de base de datos
- Crear procesos de backup y restauración
- Documentar procedimientos de solución de problemas
- Configurar escaneo de seguridad y actualizaciones

### Fase 6.3: Optimización del Rendimiento (Semanas 5-6)

**Estado Actual: PLANIFICACIÓN**

- Analizar métricas de rendimiento de la aplicación
- Identificar y abordar cuellos de botella de rendimiento
- Optimizar consultas de base de datos
- Implementar caché donde sea apropiado
- Ajustar el procesamiento de tareas de Celery

### Fase 6.4: Mantenimiento del Modelo ML (Semanas 7-8)

**Estado Actual: PLANIFICACIÓN**

- Implementar reentrenamiento automatizado del modelo
- Configurar monitoreo del rendimiento del modelo
- Crear sistema de control de versiones del modelo
- Documentar procedimientos de actualización del modelo
- Desarrollar mejoras en la ingeniería de características

## Lista de Verificación de Mantenimiento

### Mantenimiento Diario

- [ ] Verificar el panel de salud del sistema
- [ ] Revisar logs de errores en busca de problemas críticos
- [ ] Monitorear el uso de cuotas de API
- [ ] Verificar el estado de los workers de Celery
- [ ] Verificar la salud de la conexión a la base de datos

### Mantenimiento Semanal

- [ ] Revisar métricas de rendimiento
- [ ] Verificar avisos de seguridad para dependencias
- [ ] Analizar datos de rendimiento de campañas
- [ ] Hacer backup de la base de datos
- [ ] Limpiar archivos temporales y logs

### Mantenimiento Mensual

- [ ] Actualizar dependencias
- [ ] Reentrenar modelo ML con nuevos datos
- [ ] Revisar y optimizar índices de base de datos
- [ ] Realizar escaneo de seguridad
- [ ] Actualizar documentación con nuevos hallazgos

### Mantenimiento Trimestral

- [ ] Revisión exhaustiva del sistema
- [ ] Optimización del rendimiento
- [ ] Planificación de mejoras de funciones
- [ ] Recopilación y análisis de comentarios de usuarios
- [ ] Optimización del almacenamiento a largo plazo

#### Introducción

Este documento describe los procedimientos y herramientas para mantener y monitorear el sistema Ad Automation P-01 después del despliegue. Aunque el sistema es un proyecto universitario con datos simulados, esta documentación describe las mejores prácticas que se aplicarían en un entorno de producción para garantizar que el sistema continúe cumpliendo con los requisitos comerciales y funcione de manera fiable. Las actividades de mantenimiento y monitoreo incluyen verificaciones de salud del sistema, análisis del rendimiento de campañas publicitarias, resolución de problemas, actualizaciones de dependencias, planificación de mejoras y documentación exhaustiva.

#### Monitoreo de la Salud del Sistema

Para garantizar que el sistema funcione sin problemas, utilizamos las herramientas de monitoreo de Google Cloud:

- **Cloud Monitoring:** Rastrea métricas clave como:
  - **Rendimiento de la Aplicación:**
    - Recuento de solicitudes
    - Latencia de respuesta
    - Recuento de errores
    - Recuento de instancias
  - **Rendimiento de la Base de Datos:**
    - Utilización de CPU
    - Uso de memoria
    - Uso de disco
    - Recuento de consultas
    - Latencia de consultas
- **Cloud Logging:** Captura logs de aplicación, errores y eventos del sistema para depuración y análisis.

**Configuración de Alertas:**

- Configurar alertas en Cloud Monitoring para umbrales críticos, como:
  - Tasas de error altas (>5% de las solicitudes)
  - Latencia elevada (>2 segundos de tiempo de respuesta promedio)
  - Uso de CPU de la base de datos (>80%)
- Estas alertas notifican al equipo de mantenimiento por correo electrónico o SMS, permitiendo una acción rápida para resolver problemas.

En un entorno de producción, estas herramientas aseguran un monitoreo proactivo, permitiendo al equipo abordar cuellos de botella de rendimiento o fallos antes de que impacten a los usuarios. Para el proyecto universitario, configurar estos paneles y alertas proporciona una demostración de las mejores prácticas, incluso con datos simulados.

#### Monitoreo del Rendimiento de Campañas Publicitarias

En un entorno de producción, monitorear el rendimiento de las campañas publicitarias es crucial. El sistema debería:

- Obtener periódicamente métricas de rendimiento de las plataformas de redes sociales utilizando sus API (p. ej., API de Marketing de Meta, API de Google Ads). Por ejemplo, la API de Marketing de Meta proporciona insights como impresiones, clics y conversiones, como se detalla en [Insights de la API de Marketing de Meta](https://developers.facebook.com/docs/marketing-api/insights). De manera similar, la API de Google Ads ofrece funciones de informes para métricas como costo y clics, como se indica en [Informes de la API de Google Ads](https://developers.google.com/google-ads/api/docs/reporting/overview).
- Almacenar métricas como impresiones, clics, CTR, CPC y conversiones en la base de datos.
- Proporcionar paneles o informes para que los gerentes de marketing analicen la efectividad de las campañas, potencialmente utilizando paneles de Cloud Monitoring o visualizaciones personalizadas.

Para el proyecto universitario, esta funcionalidad se puede simular generando datos de rendimiento ficticios, asegurando que el sistema pueda manejar y mostrar estas métricas para fines de demostración. Este enfoque se alinea con el objetivo del proyecto de mostrar una prueba de concepto funcional.

#### Seguimiento y Resolución de Problemas

Para gestionar errores y solicitudes de funciones:

- **GitHub Issues:** Rastrear problemas con etiquetas de prioridad (p. ej., alta, media, baja) y tipo (p. ej., error, mejora), aprovechando el proyecto GitHub existente configurado por el usuario. Esto está respaldado por la [Documentación de GitHub Issues](https://docs.github.com/en/issues), que proporciona orientación sobre la gestión de problemas.
- **Priorización:** Los problemas de alta prioridad que afectan la funcionalidad del sistema, como fallos en la publicación de anuncios, se abordan primero, asegurando una interrupción mínima.
- **Pipeline CI/CD:** Usar Google Cloud Build o GitHub Actions para desplegar automáticamente correcciones en App Engine al fusionar pull requests en la rama principal. Esto asegura una rápida respuesta para las actualizaciones y mantiene la estabilidad del sistema, como se detalla en la [Documentación de Google Cloud Build](https://cloud.google.com/build).

Para el proyecto universitario, este proceso asegura que cualquier problema identificado durante las pruebas o la demostración pueda ser registrado y resuelto, manteniendo la preparación del sistema para la presentación en mayo de 2025.

#### Actualización de Dependencias

Actualizar regularmente las dependencias es esencial para la seguridad y el rendimiento:

- **Bibliotecas Python:** Usar `pip list --outdated` para verificar actualizaciones de bibliotecas como Flask, Scikit-learn y bibliotecas API de redes sociales como `facebook-python-business-sdk`. Esto se puede automatizar usando herramientas como Dependabot, integradas con GitHub, como parte de las mejores prácticas de gestión de dependencias.
- **Gestión de Dependencias:** Mantener un archivo `requirements.txt` con versiones fijadas o usar Poetry para la resolución de dependencias, asegurando consistencia y reproducibilidad, como lo respalda [Gestión de Dependencias con Poetry](https://python-poetry.org/).
- **Pruebas de Actualizaciones:** Antes de actualizar en producción, probar las nuevas versiones de bibliotecas en un entorno de staging para asegurar la compatibilidad con la aplicación y otras dependencias. Esto se puede hacer desplegando en una versión separada de App Engine y probando los endpoints.

Para la base de datos, Cloud SQL gestiona las actualizaciones de PostgreSQL, asegurando que el motor de la base de datos esté actualizado sin intervención manual, como se indica en la [Documentación de Google Cloud SQL](https://cloud.google.com/sql/docs/postgresql).

Para el proyecto universitario, asegurar que las dependencias estén actualizadas para mayo de 2025 es crucial para una demostración segura y de alto rendimiento, alineándose con los estándares académicos.

#### Planificación de Mejoras Futuras

Para mantener el sistema alineado con las necesidades comerciales en evolución:

- **Reentrenamiento del Modelo:**
  - Programar reentrenamiento periódico del modelo de aprendizaje automático utilizando nuevos datos de candidatos para mejorar la precisión de la segmentación. En un entorno de producción, esto implicaría obtener perfiles de candidatos actualizados de la base de datos y reentrenar el modelo K-means utilizando Scikit-learn.
  - Usar Cloud Scheduler para activar una Cloud Function o una tarea de App Engine mensualmente para obtener nuevos datos, entrenar un nuevo modelo, evaluarlo usando métricas como el puntaje de silueta y desplegarlo si el rendimiento mejora. Esto está respaldado por la [Documentación de Cloud Scheduler](https://cloud.google.com/scheduler) y la [Documentación de Cloud Functions](https://cloud.google.com/functions).
  - Versionar modelos almacenándolos en Cloud Storage con números de versión, permitiendo revertir si es necesario. Por ejemplo, almacenar modelos como `model_v1.pkl`, `model_v2.pkl`, etc., y actualizar la aplicación Flask para cargar la última versión, asegurando transiciones sin problemas.

- **Adiciones de Funciones:**
  - Basado en comentarios de usuarios y requisitos comerciales, planificar e implementar nuevas funciones, como soporte para plataformas de redes sociales adicionales (p. ej., TikTok, Snapchat) o capacidades analíticas avanzadas como modelado predictivo para el rendimiento de anuncios.
  - Usar metodologías ágiles para priorizar y desarrollar estas funciones en sprints, asegurando mejoras iterativas, como se detalla en [Gestión Ágil de Proyectos](https://www.atlassian.com/agile).

Para el proyecto universitario, planificar estas mejoras demuestra previsión, incluso si no se implementan, preparando el sistema para un posible uso futuro más allá del ámbito académico.

#### Documentación

Una documentación exhaustiva asegura una operación y mantenimiento fluidos:

- **Manual de Usuario:**
  - Una guía para gerentes de marketing sobre el uso del sistema, incluyendo pasos para ver ofertas de trabajo, seleccionar plataformas, crear campañas publicitarias y analizar el rendimiento. Puede incluir capturas de pantalla o instrucciones paso a paso, alojadas en la carpeta `docs` del repositorio de GitHub como `USER_GUIDE.md`.
  - Contenido de ejemplo: "Para ver las ofertas de trabajo, navega al endpoint /job_openings y envía una solicitud GET. La respuesta listará todas las ofertas disponibles con sus detalles."

- **Documentación Técnica:**
  - Información detallada para desarrolladores sobre la arquitectura del sistema, procedimientos de despliegue, configuración de monitoreo y tareas de mantenimiento.
  - **README.md:** Un archivo `README.md` completo en la raíz del repositorio de GitHub, cubriendo:
    - Visión general y propósito del proyecto.
    - Pila tecnológica utilizada.
    - Instrucciones de configuración para desarrollo local (dependencias, variables de entorno, configuración de base de datos).
    - Cómo ejecutar la aplicación localmente.
    - Cómo usar la CLI.
    - Instrucciones de despliegue (mencionando brevemente los pasos de GCP).
    - Instrucciones de prueba.
  - Esta documentación técnica (README y potencialmente otros archivos como `TECHNICAL_DOCS.md` si se necesita profundizar) asegura que el proyecto sea comprensible, reproducible y mantenible.

- **Procedimientos de Mantenimiento:**
  - Procesos documentados para tareas de mantenimiento de rutina, tales como:
    - Verificar y aplicar actualizaciones de dependencias usando `pip list --outdated` y probando en staging.
    - Monitorear la salud del sistema y responder a alertas revisando Cloud Logging en busca de errores.
    - Realizar backups de la base de datos usando la función de backup automatizado de Cloud SQL, configurada en los ajustes de la instancia.
    - Asegurar el versionamiento y despliegue del modelo almacenando modelos en Cloud Storage y actualizando la configuración de la aplicación Flask.

Para el proyecto universitario, estos documentos pueden ser parte de la entrega final, asegurando que el sistema esté bien documentado para la calificación y posible uso futuro.

#### Tabla Resumen: Actividades de Mantenimiento y Monitoreo

| Actividad                          | Descripción                                                                 | Herramientas Usadas                     |
|-----------------------------------|-----------------------------------------------------------------------------|--------------------------------|
| Monitorear Salud del Sistema      | Rastrear rendimiento de aplicación y BD usando herramientas cloud           | Cloud Monitoring, Cloud Logging|
| Monitorear Rendimiento Campañas   | Obtener y analizar métricas de anuncios de APIs redes sociales (simulado)    | APIs redes sociales, base datos |
| Seguimiento y Resolución Problemas | Rastrear y corregir errores usando GitHub Issues y CI/CD                     | GitHub Issues, Google Cloud Build|
| Actualizar Dependencias           | Actualizar regularmente bibliotecas Python y asegurar compatibilidad        | pip, Poetry                    |
| Planificar Mejoras Futuras        | Programar reentrenamiento modelo y adiciones funciones                      | Cloud Scheduler, Cloud Functions|
| Documentación                     | Crear documentación técnica y de usuario                                    | Markdown, GitHub Wiki          |

#### Conclusión

La fase de mantenimiento y monitoreo es crítica para asegurar que el sistema Ad Automation P-01 siga siendo performante, fiable y alineado con los objetivos comerciales. Implementando un monitoreo robusto, resolución eficiente de problemas, actualizaciones regulares, mejoras planificadas y documentación exhaustiva, el sistema puede continuar entregando valor y adaptarse a las necesidades cambiantes. Aunque este es un proyecto universitario, estas prácticas simulan operaciones del mundo real, proporcionando una valiosa experiencia en la gestión de sistemas de producción.

### Citas Clave

-   [Documentación de Google Cloud Monitoring](https://cloud.google.com/monitoring)
-   [Documentación de Google Cloud Logging](https://cloud.google.com/logging)
-   [Insights de la API de Marketing de Meta](https://developers.facebook.com/docs/marketing-api/insights)
-   [Informes de la API de Google Ads](https://developers.google.com/google-ads/api/docs/reporting/overview)
-   [Documentación de GitHub Issues](https://docs.github.com/en/issues)
-   [Documentación de Google Cloud Build](https://cloud.google.com/build)
-   [Gestión de Dependencias con Poetry](https://python-poetry.org/)
-   [Documentación de Cloud Scheduler](https://cloud.google.com/scheduler)
-   [Documentación de Cloud Functions](https://cloud.google.com/functions)
-   [Documentación de MkDocs](https://www.mkdocs.org/)
-   [Gestión Ágil de Proyectos](https://www.atlassian.com/agile)
