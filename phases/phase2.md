# Fase 2

## Puntos Clave

- Parece probable que el diseño del sistema para el proyecto Ad Automation P-01 involucre un backend con Python y Flask, una base de datos PostgreSQL, aprendizaje automático usando Scikit-learn e integraciones API con plataformas de redes sociales.
- La investigación sugiere usar AWS para el despliegue en la nube, con servicios como EC2 para cómputo y RDS para bases de datos, asegurando escalabilidad y fiabilidad.
- La evidencia se inclina hacia la inclusión opcional de Celery para tareas en segundo plano y el enfoque en medidas de seguridad como HTTPS y almacenamiento seguro de credenciales.

#### Visión General del Sistema

El sistema Ad Automation P-01 está diseñado para automatizar la publicación de anuncios de ofertas de trabajo y segmentar audiencias para publicidad dirigida. Utilizará un backend construido con Python y Flask para manejar solicitudes API, gestionar datos e integrar con modelos de aprendizaje automático y APIs de redes sociales.

#### Diseño de Componentes

- **Backend:** La aplicación Flask gestionará campañas publicitarias, obtendrá ofertas de trabajo e interactuará con el aprendizaje automático para la segmentación. Expondrá APIs RESTful para interacciones de usuario.
- **Base de Datos:** PostgreSQL almacenará ofertas de trabajo, perfiles de candidatos, campañas publicitarias y logs, con un esquema diseñado para la escalabilidad.
- **Aprendizaje Automático:** Se usará Scikit-learn para clustering no supervisado, como K-means, para segmentar candidatos basados en datos simulados.
- **Integraciones API:** Conectar a Meta, X y Google Ads usando bibliotecas Python específicas de la plataforma, con planes para TikTok y Snapchat si el tiempo lo permite.
- **Despliegue en la Nube:** Desplegar en AWS usando EC2, RDS y S3, con balanceo de carga para escalabilidad.

#### Detalle Inesperado

Un aspecto interesante es la variabilidad en el soporte de API, con bibliotecas oficiales para Meta, X y Google, pero métodos no oficiales para TikTok y Snapchat, lo que requiere un diseño flexible para manejar estas diferencias.

---

---

### Documento de Arquitectura del Sistema para la Fase 2: Diseño del Sistema

Esta sección proporciona un análisis exhaustivo y documentación detallada para la Fase 2: Diseño del Sistema del proyecto universitario Ad Automation P-01, destinado a automatizar la publicación de anuncios de ofertas de trabajo en plataformas de redes sociales y segmentar audiencias para publicidad dirigida. El sistema está diseñado para integrarse con al menos tres de los siguientes canales: Meta, X, Google, TikTok y Snapchat, y está previsto que forme parte del ecosistema de Magneto, una empresa colombiana especializada en la búsqueda de empleo ([Magneto365](https://www.magneto365.com/)). Sin embargo, dadas las restricciones del proyecto, el usuario trabajará con datos simulados y se centrará en un sistema de prueba de concepto con fecha límite en mayo de 2025, comenzando el 24 de marzo de 2025.

#### Introducción

Este documento describe la arquitectura del sistema para el proyecto Ad Automation P-01, que tiene como objetivo automatizar la publicación de anuncios de ofertas de trabajo en plataformas de redes sociales y segmentar audiencias para publicidad dirigida. El sistema está diseñado para garantizar la escalabilidad, la fiabilidad y la integración con los sistemas existentes, utilizando datos simulados para fines de desarrollo y prueba. El objetivo es diseñar una arquitectura de sistema que pueda manejar las funcionalidades principales dentro del cronograma del proyecto universitario, centrándose en el desarrollo del backend, el diseño de la base de datos, el aprendizaje automático, las integraciones de API y el despliegue en la nube.

#### Arquitectura de Alto Nivel

El sistema consta de los siguientes componentes principales, diseñados para funcionar juntos sin problemas:

- **Interfaz de Usuario:** Una **Interfaz de Línea de Comandos (CLI)** construida utilizando una biblioteca como `click` o `argparse` en Python. Esto permite a los gerentes de marketing (simulados por el usuario/demostrador) gestionar campañas publicitarias, ver ofertas de trabajo, seleccionar plataformas e iniciar la publicación de anuncios mediante comandos simples. Esta elección prioriza la funcionalidad sobre una interfaz de usuario web compleja dentro del cronograma del proyecto.

- **Servidor Backend:** Construido con Python y el framework Flask, manejando solicitudes API, lógica de negocio, acceso a datos e interacciones con el módulo de aprendizaje automático y las API de redes sociales. El backend expondrá APIs RESTful para gestionar ofertas de trabajo, perfiles de candidatos, campañas publicitarias y segmentos de audiencia.

- **Base de Datos:** PostgreSQL para almacenar datos estructurados, incluyendo ofertas de trabajo, perfiles de candidatos, detalles de campañas publicitarias y logs del sistema. La base de datos está diseñada para soportar la escalabilidad y garantizar una gestión de datos fiable.

- **Módulo de Aprendizaje Automático:** Usando Scikit-learn para aprendizaje no supervisado, como clustering K-means, para segmentar audiencias basadas en datos de candidatos. Este módulo se integrará en el backend para segmentación en tiempo real durante la orientación de anuncios.

- **Integraciones de API de Redes Sociales:** Conexiones a APIs externas para **Meta y Google Ads (núcleo)** usando bibliotecas Python específicas de la plataforma, con **X (objetivo ambicioso)** y exploración potencial de TikTok/Snapchat si queda tiempo significativo. Estas integraciones manejarán la creación, publicación y monitoreo de anuncios en modo de prueba.

- **Cola de Tareas (Opcional):** Celery para gestionar tareas en segundo plano, como programar publicaciones de anuncios y procesar grandes conjuntos de datos, mejorando la capacidad de respuesta y la eficiencia del sistema.

- **Infraestructura en la Nube:** AWS para alojamiento y despliegue, utilizando servicios como EC2 para cómputo, RDS para bases de datos, S3 para almacenamiento, Elastic Load Balancer para distribución de tráfico y Auto Scaling para manejar variaciones de carga.

El diagrama de arquitectura de alto nivel debe ilustrar estos componentes y sus interacciones, mostrando la interfaz de usuario conectándose al servidor backend, que a su vez interactúa con la base de datos, el módulo de aprendizaje automático, las API de redes sociales y los servicios en la nube. Si se usa Celery, mostrarlo como un componente separado que maneja tareas de forma asíncrona.

#### Arquitectura del Backend

El backend está construido usando Python con el framework Flask, elegido por su naturaleza ligera y adecuación para servicios API. La arquitectura del backend incluye:

- **Rutas API:** Endpoints RESTful para:
  - Obtener y gestionar ofertas de trabajo (GET /job_openings, POST /job_openings).
  - Gestionar perfiles de candidatos (GET /candidates, POST /candidates).
  - Crear y gestionar campañas publicitarias (POST /ad_campaigns, GET /ad_campaigns/{id}).
  - Recuperar segmentos de audiencia (GET /segments, POST /segments).
  - Publicar anuncios en plataformas de redes sociales (POST /publish_ad).

- **Lógica de Negocio:** Maneja la autenticación para las API de redes sociales, procesa solicitudes para la creación de anuncios e interactúa con el módulo de aprendizaje automático para la segmentación. Por ejemplo, cuando un gerente de marketing selecciona una oferta de trabajo y plataformas a través de la CLI, el backend obtendrá datos de candidatos, obtendrá segmentos y activará la publicación de anuncios. Se implementará un **manejo robusto de errores** para las llamadas a API externas, incluyendo el registro de errores específicos de la API, el manejo de excepciones comunes (por ejemplo, tiempos de espera, límites de tasa) y potencialmente la implementación de lógica de reintento simple para problemas de red transitorios.

- **Puntos de Integración:** El backend se conectará a la base de datos para almacenamiento y recuperación de datos, llamará al módulo de aprendizaje automático para la segmentación y utilizará bibliotecas API para interacciones con redes sociales. También manejará tareas opcionales de Celery para procesamiento en segundo plano.

Este diseño asegura que el backend sea modular, escalable y mantenible, alineándose con los requisitos del proyecto de automatización e integración.

#### Diseño de la Base de Datos

El esquema de la base de datos se diseña utilizando PostgreSQL, elegido por su robustez y soporte para la gestión de datos estructurados. Las tablas clave incluyen:

- **JobOpenings:** Almacena detalles de las ofertas de trabajo, con campos como id, titulo, descripcion, requisitos, ubicacion y created_at.
- **Candidates:** Almacena perfiles de candidatos, con campos como id, nombre, edad, genero, ubicacion, educacion, experiencia_laboral, preferencias_laborales y segment_id (después del clustering).
- **AdCampaigns:** Almacena detalles de campañas publicitarias, con campos como id, job_opening_id, plataformas (array o tabla relacionada), estado, created_at y updated_at.
- **Logs:** Almacena logs del sistema para rastrear actividades y errores, con campos como id, timestamp, mensaje, nivel y fuente.

Las relaciones son las siguientes:

- Un JobOpening puede tener múltiples AdCampaigns (uno a muchos).
- Cada Candidate puede estar asociado con un Segment (muchos a uno, después del clustering).
- Los Logs son independientes pero pueden hacer referencia a otras tablas para contexto.

[Insertar Diagrama ER o Descripción del Esquema]

Por ejemplo, el diagrama ER mostraría JobOpenings conectado a AdCampaigns, Candidates conectado a Segments (a través del módulo de aprendizaje automático), y Logs como una tabla independiente para auditoría.

Dado el uso de datos simulados, el esquema debe soportar al menos 100 ofertas de trabajo y 1,000 perfiles de candidatos, asegurando datos suficientes para demostración y pruebas.

#### Pipeline de Aprendizaje Automático

El pipeline de aprendizaje automático está diseñado para segmentar audiencias basadas en datos de candidatos, utilizando Scikit-learn para aprendizaje no supervisado. El pipeline incluye:

- **Recopilación de Datos:** Obtener datos de candidatos de la base de datos PostgreSQL, incluyendo campos como edad, ubicacion, educacion y preferencias_laborales.

- **Preprocesamiento de Datos:** Limpiar los datos, manejar valores faltantes, codificar variables categóricas (por ejemplo, ubicacion como codificación one-hot) y normalizar características numéricas para el clustering.

- **Selección de Características:** Elegir características relevantes para la segmentación, como demográficas (edad, genero) y atributos relacionados con el trabajo (educacion, experiencia laboral), basadas en su impacto en la calidad del clustering.

- **Entrenamiento del Modelo:** Usar clustering K-means para segmentar candidatos en grupos, con el número de clusters determinado por el método del codo o el puntaje de silueta para evaluación. Por ejemplo, apuntar a 5-10 segmentos para equilibrar granularidad y usabilidad.

- **Evaluación del Modelo:** Evaluar la calidad del clustering usando métricas como el puntaje de silueta. Además, realizar **evaluación cualitativa** examinando las distribuciones de características dentro de los clusters generados para asegurar que representan segmentos prácticamente significativos. Documentar el número elegido de clusters y la justificación. Considerar alternativas como DBSCAN o reducción de dimensionalidad (PCA) solo si K-means resulta insuficiente y el tiempo permite la exploración.

- **Despliegue del Modelo:** Guardar el modelo entrenado usando joblib o pickle, e integrarlo en el backend. El backend llamará a este modelo para asignar segmentos a los candidatos durante la orientación de anuncios, con un endpoint API como GET /segments para recuperar información de segmentos.

Este pipeline asegura que el sistema pueda proporcionar segmentos de audiencia para publicidad dirigida, alineándose con los objetivos del proyecto.

#### Planes de Integración API

El sistema se integrará con las API de las plataformas de redes sociales para la publicación de anuncios, centrándose en **Meta y Google Ads como requisitos principales**, con X como objetivo ambicioso, dado el cronograma del proyecto universitario. Los planes son los siguientes:

- **Meta (Facebook):**
  - Usar el `facebook-python-business-sdk` ([Facebook Business SDK for Python](https://github.com/facebook/facebook-python-business-sdk)) para la gestión de anuncios.
  - Configurar una aplicación de Facebook y obtener tokens de acceso usando OAuth.
  - Implementar funciones para crear campañas publicitarias, conjuntos de anuncios y anuncios, usando el modo de prueba para demostración.

- **X (Twitter - Objetivo Ambicioso):**
  - Usar el `twitter-python-ads-sdk` ([GitHub - xdevplatform/twitter-python-ads-sdk](https://github.com/xdevplatform/twitter-python-ads-sdk)) si el tiempo lo permite.
  - Configurar la autenticación usando OAuth 1.0a o 2.0 dependiendo del endpoint.
  - Implementar funciones para crear campañas, segmentación y gestionar tweets/anuncios en modo de prueba.

- **Google Ads:**
  - Usar la biblioteca `google-ads-python` ([Google Ads API Client Library for Python](https://github.com/googleads/google-ads-python)) para Google Ads.
  - Configurar una cuenta de Google Ads y obtener credenciales.
  - Implementar funciones para crear campañas, grupos de anuncios y anuncios, usando cuentas de prueba para demostración.

Para TikTok y Snapchat, si el tiempo lo permite, usar envoltorios no oficiales como `python-tiktok` ([Página PyPI para python-tiktok](https://pypi.org/project/python-tiktok/)) o solicitudes HTTP directas, haciendo referencia a proyectos como [Página GitHub para davidteather/TikTok-Api](https://github.com/davidteather/TikTok-Api) para TikTok, y [Página GitHub para rbnali/easy-snapchat-api](https://github.com/rbnali/easy-snapchat-api) para Snapchat. Sin embargo, dado el cronograma, centrarse en las tres plataformas principales.

La autenticación usará OAuth donde sea requerido, y las claves API se almacenarán de forma segura usando variables de entorno o AWS Secrets Manager. El backend manejará límites de tasa y manejo de errores para las llamadas API, asegurando la fiabilidad.

#### Arquitectura de Despliegue

El sistema se desplegará en AWS, elegido por su uso generalizado y precios amigables para estudiantes, con los siguientes servicios:

- **EC2:** Para alojar la aplicación Flask, usando instancias t2.micro por su rentabilidad, con grupos de auto-scaling para manejar variaciones de carga.

- **RDS:** Para la base de datos PostgreSQL, usando instancias db.t3.micro, con réplicas de lectura para escalabilidad si es necesario.

- **S3:** Para almacenar archivos estáticos, copias de seguridad o cualquier conjunto de datos grande, asegurando durabilidad y disponibilidad.

- **Elastic Load Balancer:** Para distribuir el tráfico entrante entre las instancias EC2, mejorando la disponibilidad y la tolerancia a fallos.

- **Auto Scaling:** Configurar para añadir instancias basadas en la utilización de CPU, asegurando que el sistema pueda manejar un aumento del tráfico durante los momentos pico.

Alternativamente, usar AWS Elastic Beanstalk para un despliegue y gestión más fáciles, que abstrae gran parte de la configuración de la infraestructura.

[Insertar Diagrama de Arquitectura de Despliegue]

El diagrama debe mostrar el balanceador de carga dirigiendo el tráfico a las instancias EC2, que se conectan a RDS para acceso a la base de datos y a S3 para almacenamiento, con grupos de auto-scaling gestionando el escalado de instancias.

Esta arquitectura asegura escalabilidad, fiabilidad y rentabilidad, alineándose con las necesidades del proyecto universitario.

#### Medidas de Seguridad

Para garantizar la seguridad del sistema, se implementarán las siguientes medidas:

- Usar HTTPS para todas las comunicaciones entre la interfaz de usuario, el backend y las API externas, usando AWS Certificate Manager para certificados SSL/TLS.

- Almacenar claves API, credenciales de base de datos y otra información sensible en AWS Secrets Manager o variables de entorno, asegurando acceso seguro y rotación.

- Implementar autenticación para la interfaz de usuario, potencialmente usando JSON Web Tokens (JWT) para sesiones de usuario, restringiendo el acceso a gerentes de marketing autorizados.

- Asegurar la privacidad de los datos, especialmente para la información de los candidatos, aunque sea simulada, encriptando datos en reposo usando encriptación RDS y en tránsito usando SSL.

- Actualizar regularmente las dependencias, como Flask, Scikit-learn y bibliotecas API, para parchear vulnerabilidades de seguridad, usando herramientas como Dependabot para monitoreo.

- Monitorear los logs del sistema en busca de actividades sospechosas, usando AWS CloudWatch para logging y alertas, asegurando una gestión proactiva de la seguridad.

Estas medidas aseguran que el sistema sea seguro y cumpla con las mejores prácticas, protegiendo tanto el sistema como sus datos.

#### Consideraciones de Implementación

Un detalle inesperado es la variabilidad en el soporte y la complejidad de las API entre las plataformas de redes sociales. Centrarse en dos API principales y bien soportadas (Meta, Google Ads) mitiga el riesgo, mientras que reconocer los posibles desafíos con otras como X (SDK oficial pero potencialmente complejo) o TikTok/Snapchat (métodos no oficiales) permite tomar decisiones informadas si se persiguen objetivos ambiciosos. Un manejo robusto de errores dentro de los módulos de integración será crucial.

#### Tabla: Resumen de Componentes del Sistema y Tecnologías

| Componente             | Tecnología                | Propósito                                                                 |
|-----------------------|---------------------------|-------------------------------------------------------------------------|
| Backend               | Python con Flask         | Servicios API para gestionar campañas publicitarias, obtener ofertas de trabajo e interactuar con modelos de aprendizaje automático |
| Base de Datos              | PostgreSQL                | Almacenar y gestionar datos estructurados como ofertas de trabajo, perfiles de candidatos y campañas publicitarias |
| Aprendizaje Automático      | Scikit-learn              | Aprendizaje no supervisado para segmentación de audiencias, como clustering K-means |
| Integraciones API      | Varias bibliotecas Python  | Interactuar con las API de Meta, X, Google y opcionalmente TikTok y Snapchat para publicación de anuncios |
| Cola de Tareas (Opcional) | Celery                    | Gestionar tareas en segundo plano como programar publicaciones de anuncios y procesar grandes conjuntos de datos |
| Plataforma en la Nube        | AWS (EC2, RDS, S3, ELB)   | Escalabilidad y alojamiento para el sistema, asegurando fiabilidad y rendimiento |

Esta tabla resume las tecnologías clave y sus propósitos, asegurando claridad para la implementación.

#### Conclusión

El diseño de sistema recomendado para la Fase 2 proporciona un enfoque estructurado para la arquitectura del sistema Ad Automation P-01, aprovechando eficazmente la pila tecnológica recomendada. Asegura escalabilidad, fiabilidad e integración, centrándose en el desarrollo del backend, diseño de base de datos, aprendizaje automático, integraciones API y despliegue en la nube. El diseño tiene en cuenta las restricciones del proyecto universitario, utilizando datos simulados y centrándose en un sistema de prueba de concepto con fecha límite en mayo de 2025, con documentación detallada para la implementación.

### Citas Clave

- [Facebook Business SDK for Python](https://github.com/facebook/facebook-python-business-sdk)
- [Twitter Ads API SDK for Python](https://github.com/xdevplatform/twitter-python-ads-sdk)
- [Google Ads API Client Library for Python](https://github.com/googleads/google-ads-python)
- [Página PyPI para python-tiktok](https://pypi.org/project/python-tiktok/)
- [Página GitHub para davidteather/TikTok-Api](https://github.com/davidteather/TikTok-Api)
- [Página GitHub para rbnali/easy-snapchat-api](https://github.com/rbnali/easy-snapchat-api)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Guía del Usuario de Scikit-learn](https://scikit-learn.org/stable/user_guide.html)
- [Documentación de AWS](https://docs.aws.amazon.com/)
- [Documentación de Celery](https://docs.celeryproject.org/en/stable/)
