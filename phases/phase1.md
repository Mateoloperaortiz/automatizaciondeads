# Fase 1

## Historias de Usuario para Recopilación de Requisitos

Dado que Magneto es el dueño del producto y los candidatos son los usuarios, pero el sistema es utilizado por el equipo de Magneto, aquí hay ejemplos de historias de usuario para requisitos funcionales y no funcionales:

- **Historias de Usuario Funcionales:**
  - Como gerente de marketing, quiero ver una lista de las ofertas de trabajo disponibles en el sistema para poder seleccionar cuáles anunciar.
  - Como gerente de marketing, quiero seleccionar plataformas de redes sociales para publicar anuncios de una oferta de trabajo específica.
  - Como gerente de marketing, quiero que el sistema cree y publique automáticamente anuncios en las plataformas seleccionadas para una oferta de trabajo.
  - Como gerente de marketing, quiero que el sistema segmente a los candidatos en grupos según sus perfiles para dirigir los anuncios de manera más efectiva.
  - Como gerente de marketing, quiero dirigir anuncios a segmentos específicos de candidatos.

- **Historias de Usuario No Funcionales:**
  - Como usuario del sistema, quiero que el sistema maneje al menos 100 ofertas de trabajo y 1,000 perfiles de candidatos para garantizar la escalabilidad.
  - Como usuario del sistema, quiero que el sistema responda a las interacciones del usuario en 5 segundos para una experiencia fluida.
  - Como administrador del sistema, quiero que el sistema almacene de forma segura las claves API y las credenciales para proteger los datos sensibles.

Estas historias aseguran que el sistema cumpla tanto con lo que hace como con su rendimiento, adaptado para un proyecto universitario.

---

### Definición del Alcance

Como proyecto universitario con fecha límite en mayo de 2025, comenzando ahora a fines de marzo de 2025, tienes aproximadamente dos meses. Concéntrate en las características principales:

- Configurar un backend con Python y Flask, usando PostgreSQL para el almacenamiento de datos.
- Simular ofertas de trabajo y perfiles de candidatos ya que no tendrás acceso a los datos de Magneto365.
- Implementar aprendizaje automático para la segmentación de audiencias usando Scikit-learn, probablemente clustering K-means.
- Integrar con al menos dos API principales de redes sociales (por ejemplo, Meta, Google Ads) utilizando cuentas de prueba o entornos sandbox.
- Proporcionar una Interfaz de Línea de Comandos (CLI) básica para gestionar campañas publicitarias y ver datos.
- Desplegar en una plataforma en la nube como AWS o Google Cloud para la presentación.

Excluye características avanzadas como monitoreo en tiempo real o analíticas complejas para mantenerte dentro del cronograma.

---

### Creación del Plan de Proyecto

Dado el enfoque ágil y sprints de dos semanas, aquí hay un plan para cuatro sprints, ajustándose al cronograma:

| Sprint | Área de Enfoque                | Actividades Clave                                    |
|--------|--------------------------------|----------------------------------------------------|
| 1      | Infraestructura y Conf. Núcleo | Configurar GitHub (ya hecho), estructura de app Flask, PostgreSQL, modelos de datos básicos, README inicial. |
| 2      | Gestión y Simulación de Datos  | Desarrollar script de generación de datos, generar y cargar datos simulados de trabajos/candidatos. |
| 3      | Aprendizaje Automático y APIs Núcleo | Preprocesar datos, entrenar modelo K-means, integrar ML en Flask, implementar API núcleo 1 (ej., Meta). |
| 4      | API Núcleo 2 y CLI             | Implementar API núcleo 2 (ej., Google Ads), desarrollar CLI básica, pruebas iniciales. |

Después de los sprints, asigna tiempo para pruebas, depuración, despliegue y documentación, asegurando la preparación para mayo de 2025.

---

---

### Nota de la Encuesta: Documentación Detallada para Recopilación de Requisitos, Definición del Alcance, Creación del Plan de Proyecto e Identificación de Fuentes de Datos

Esta sección proporciona un análisis exhaustivo y documentación detallada para las fases de Recopilación de Requisitos, Definición del Alcance, Creación del Plan de Proyecto e Identificación de Fuentes de Datos del proyecto universitario Ad Automation P-01, destinado a automatizar la publicación de anuncios de ofertas de trabajo en plataformas de redes sociales y segmentar audiencias para publicidad dirigida. El sistema está diseñado para integrarse con al menos dos API principales de redes sociales y está previsto que forme parte del ecosistema de Magneto, una empresa colombiana especializada en la búsqueda de empleo ([Magneto365](https://www.magneto365.com/)). Sin embargo, dadas las restricciones del proyecto, el usuario trabajará con datos simulados y se centrará en un sistema de prueba de concepto con fecha límite en mayo de 2025.

#### Antecedentes y Contexto

El proyecto aborda el proceso manual y lento de publicar anuncios para ofertas de trabajo en plataformas de redes sociales, lo cual es costoso en términos de tiempo y dinero. El objetivo es automatizar este proceso, permitiendo publicidad dirigida para los candidatos de Magneto y publicitando vacantes críticas. Los desafíos técnicos clave incluyen el consumo de API de redes sociales y la segmentación de poblaciones, con ideas de solución que involucran clasificación mediante métodos no supervisados e integración con las API de Google y Meta. Dado el rol del usuario como estudiante universitario, Magneto es el dueño del producto y los candidatos son los usuarios finales, pero el sistema es utilizado principalmente por el equipo de Magneto (por ejemplo, gerentes de marketing). El usuario tiene un proyecto de GitHub configurado y no tendrá acceso a los datos de Magneto365, lo que requiere el uso de datos simulados. El proyecto vence en mayo de 2025, comenzando ahora el 24 de marzo de 2025, lo que proporciona aproximadamente dos meses para el desarrollo.

#### Recopilación de Requisitos

El usuario necesita crear historias de usuario para requisitos funcionales y no funcionales, centrándose en el equipo de Magneto como los usuarios principales del sistema. Las historias de usuario se capturan en un formato ágil, asegurando flexibilidad y alineación con la naturaleza iterativa del proyecto, según lo informado por recursos como [Gestión Ágil de Proyectos](https://www.atlassian.com/agile).

##### Historias de Usuario Funcionales

Los requisitos funcionales describen lo que el sistema debe hacer. Dado el enfoque del proyecto en la automatización y la segmentación, se proponen las siguientes historias de usuario, escritas desde la perspectiva de un gerente de marketing en Magneto:

- **Historia de Usuario 1:** Como gerente de marketing, quiero ver una lista de las ofertas de trabajo disponibles en el sistema para poder seleccionar cuáles anunciar.
  - **Criterios de Aceptación:** El sistema muestra una lista de ofertas de trabajo con títulos e información básica, obtenida de la base de datos.
- **Historia de Usuario 2:** Como gerente de marketing, quiero seleccionar plataformas de redes sociales para publicar anuncios de una oferta de trabajo específica.
  - **Criterios de Aceptación:** El sistema permite la selección de al menos dos plataformas (por ejemplo, Meta, Google Ads), y la selección se guarda para cada oferta de trabajo.
- **Historia de Usuario 3:** Como gerente de marketing, quiero que el sistema cree y publique automáticamente anuncios en las plataformas seleccionadas para una oferta de trabajo.
  - **Criterios de Aceptación:** El sistema utiliza los detalles de la oferta de trabajo para crear contenido publicitario y publica anuncios utilizando las API de las plataformas en modo de prueba.
- **Historia de Usuario 4:** Como gerente de marketing, quiero que el sistema segmente a los candidatos en grupos según sus perfiles para dirigir los anuncios de manera más efectiva.
  - **Criterios de Aceptación:** El sistema aplica un algoritmo de clustering a los datos de los candidatos y asigna a cada candidato a un segmento.
- **Historia de Usuario 5:** Como gerente de marketing, quiero dirigir anuncios a segmentos específicos de candidatos.
  - **Criterios de Aceptación:** El sistema permite la selección de segmentos para cada campaña publicitaria, segmentando donde sea posible según las capacidades de la plataforma.

Estas historias aseguran que el sistema aborde las necesidades centrales de automatización y segmentación, adaptadas para un proyecto universitario con datos simulados.

##### Historias de Usuario No Funcionales

Los requisitos no funcionales se centran en cómo funciona el sistema. Dadas las restricciones del proyecto, se proponen los siguientes:

- **Historia de Usuario 6:** Como usuario del sistema, quiero que el sistema maneje al menos 100 ofertas de trabajo y 1,000 perfiles de candidatos para garantizar la escalabilidad.
  - **Criterios de Aceptación:** El sistema puede almacenar y procesar los volúmenes de datos especificados sin degradación del rendimiento.
- **Historia de Usuario 7:** Como usuario del sistema, quiero que el sistema responda a las interacciones del usuario en 5 segundos para una experiencia fluida.
  - **Criterios de Aceptación:** Las acciones de la interfaz de usuario, como ver ofertas de trabajo o seleccionar plataformas, se completan en 5 segundos.
- **Historia de Usuario 8:** Como administrador del sistema, quiero que el sistema almacene de forma segura las claves API y las credenciales para proteger los datos sensibles.
  - **Criterios de Aceptación:** Las claves API se almacenan utilizando variables de entorno o una bóveda segura, con acceso restringido a usuarios autorizados.

Estos requisitos no funcionales aseguran que el sistema sea eficiente y seguro, alineándose con las expectativas de un proyecto universitario.

#### Definición del Alcance

El usuario necesita definir los límites del proyecto, considerando que es un proyecto universitario con fecha límite en mayo de 2025, comenzando el 24 de marzo de 2025, lo que proporciona aproximadamente dos meses para el desarrollo. Dadas las limitaciones de tiempo y recursos, el alcance se centra en un sistema de prueba de concepto, de la siguiente manera:

- **Inclusiones:**
  - Desarrollar un backend utilizando Python con Flask para servicios API, gestionando campañas publicitarias y datos.
  - Usar PostgreSQL para almacenar ofertas de trabajo y perfiles de candidatos simulados, dado que no hay acceso a los datos de Magneto365.
  - Implementar aprendizaje automático para la segmentación de audiencias usando Scikit-learn, probablemente clustering K-means, sobre datos de candidatos simulados.
  - Integrar con al menos dos API principales de redes sociales (por ejemplo, Meta, Google Ads) utilizando cuentas de prueba o entornos sandbox, según lo informado por [Documentación de Flask](https://flask.palletsprojects.com/) y [Guía del Usuario de Scikit-learn](https://scikit-learn.org/stable/user_guide.html). La integración con una tercera API (por ejemplo, X) se considerará un objetivo ambicioso si el tiempo lo permite.
  - Proporcionar una Interfaz de Línea de Comandos (CLI) básica para gestionar campañas publicitarias y ver datos, adecuada para demostración.
  - Desplegar el sistema en una plataforma en la nube como AWS o Google Cloud para la presentación.

- **Exclusiones:**
  - Características avanzadas como monitoreo de rendimiento de anuncios en tiempo real o analíticas complejas, dado el cronograma.
  - Integración con cuentas de redes sociales activas que requieran gasto publicitario real, centrándose en cambio en modos de prueba.
  - Gestión de usuarios extensa o autenticación más allá del acceso básico de administrador, para simplificar el desarrollo.

Este alcance asegura la manejabilidad dentro de dos meses, centrándose en funcionalidades básicas y alineándose con las expectativas de un proyecto universitario.

#### Creación del Plan de Proyecto

Dado el enfoque ágil con sprints de dos semanas y el cronograma hasta mayo de 2025, el plan del proyecto se estructura en cuatro sprints, aprovechando el proyecto de GitHub configurado por el usuario para el control de versiones. Una visión general de alto nivel:

| Sprint | Área de Enfoque                | Actividades Clave                                    | Duración            |
|--------|--------------------------------|----------------------------------------------------|---------------------|
| 1      | Infraestructura y Conf. Núcleo | Configurar esqueleto del proyecto Flask, base de datos PostgreSQL, definir modelos de datos para ofertas de trabajo y candidatos, implementar operaciones CRUD básicas, README inicial. | 24 Mar - 6 Abr, 2025 |
| 2      | Gestión y Simulación de Datos  | Desarrollar script de generación de datos, generar y cargar datos simulados de trabajos/candidatos. | 7 Abr - 20 Abr, 2025 |
| 3      | Aprendizaje Automático y APIs Núcleo | Preprocesar datos, entrenar modelo K-means, integrar ML en Flask, implementar API núcleo 1 (ej., Meta). | 21 Abr - 4 May, 2025 |
| 4      | API Núcleo 2 y CLI             | Implementar API núcleo 2 (ej., Google Ads), desarrollar CLI básica, pruebas iniciales. | 5 May - 18 May, 2025 |

Después de los sprints, asignar el tiempo restante (19 de mayo - 31 de mayo de 2025) para pruebas de integración, depuración, despliegue en la nube, documentación y preparación para la presentación, asegurando la preparación antes de la fecha límite.

Este plan asegura un progreso iterativo, donde cada sprint se basa en el anterior, y se alinea con la metodología ágil, según lo respaldado por [Gestión Ágil de Proyectos](https://www.atlassian.com/agile).

#### Identificación de Fuentes de Datos

Dado que el usuario no tendrá acceso a los datos en vivo de Magneto365 para este proyecto universitario, el sistema dependerá de **datos simulados** tanto para las ofertas de trabajo como para los perfiles de candidatos.

- **Estrategia de Simulación de Datos:**
  - Se creará un script de Python (`utils/data_generator.py` o similar) al principio del proyecto (Sprint 2).
  - Este script utilizará bibliotecas como `Faker` para generar datos de aspecto realista.
  - **Ofertas de Trabajo (Objetivo: ~100):** Simular campos como `titulo`, `descripcion`, `ubicacion`, `requisitos`.
  - **Perfiles de Candidatos (Objetivo: ~1000):** Simular campos relevantes para la segmentación, como `edad`, `ubicacion`, `nivel_educativo`, `habilidades` (lista), `preferencias_laborales` (lista).
  - Los datos generados se almacenarán en la base de datos PostgreSQL.

Este enfoque asegura datos suficientes y relevantes para el desarrollo, las pruebas y la demostración de las funcionalidades principales del sistema, en particular la segmentación mediante aprendizaje automático.

#### Consideraciones de Implementación

Un detalle inesperado es la posible variabilidad en el soporte de API entre las plataformas de redes sociales, con Meta, Google Ads y X ofreciendo bibliotecas oficiales de Python, mientras que otras pueden requerir envoltorios no oficiales o solicitudes HTTP directas. Esta variabilidad requiere un diseño de backend flexible, potencialmente utilizando una capa de abstracción unificada para manejar las diferencias de API, lo que añade complejidad pero asegura una automatización integral para las plataformas elegidas.

#### Conclusión

El enfoque recomendado para la Recopilación de Requisitos, Definición del Alcance, Creación del Plan de Proyecto e Identificación de Fuentes de Datos proporciona un camino estructurado para el proyecto universitario Ad Automation P-01. Asegura que las historias de usuario cubran las necesidades funcionales y no funcionales, define un alcance manejable dentro del plazo de mayo de 2025, planifica sprints para el desarrollo iterativo y utiliza datos simulados para la viabilidad. Este enfoque se alinea con las metodologías ágiles y las restricciones de un proyecto universitario, asegurando una entrega exitosa.

### Citas Clave

- [Gestión Ágil de Proyectos](https://www.atlassian.com/agile)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Guía del Usuario de Scikit-learn](https://scikit-learn.org/stable/user_guide.html)
- [Documentación de Faker](https://faker.readthedocs.io/en/master/)
