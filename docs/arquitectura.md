# 🏗️ Arquitectura del Sistema

Este documento describe la arquitectura general de AdFlux, sus componentes principales y cómo interactúan entre sí.

## 📊 Visión General

AdFlux es una aplicación web basada en Flask que automatiza la publicación de anuncios de trabajo en diferentes plataformas de redes sociales. La arquitectura sigue un patrón MVC (Modelo-Vista-Controlador) adaptado al framework Flask.

![Arquitectura General](https://via.placeholder.com/800x400?text=Diagrama+de+Arquitectura+AdFlux)

## 🧩 Componentes Principales

### 1. Capa de Presentación

- **Flask**: Framework web que maneja las solicitudes HTTP y renderiza las vistas.
- **Jinja2**: Motor de plantillas para generar HTML dinámico.
- **Blueprints**: Organización modular de rutas y vistas por funcionalidad.
- **WTForms**: Manejo y validación de formularios.

### 2. Capa de Lógica de Negocio

- **Controladores**: Implementados como funciones de vista en los blueprints.
- **Servicios de API**: Módulos que interactúan con APIs externas (Meta, Google, Gemini).
- **Machine Learning**: Módulo para segmentación de candidatos mediante K-means.
- **Tareas Asíncronas**: Procesamiento en segundo plano con Celery.

### 3. Capa de Datos

- **SQLAlchemy ORM**: Mapeo objeto-relacional para interactuar con la base de datos.
- **Modelos**: Representaciones de las entidades del sistema (trabajos, candidatos, campañas).
- **Migraciones**: Gestión de cambios en el esquema de la base de datos con Alembic.

### 4. Servicios Externos

- **Meta Ads API**: Para crear y gestionar campañas en Facebook e Instagram.
- **Google Ads API**: Para crear y gestionar campañas en Google.
- **Gemini AI API**: Para generar contenido creativo y simular datos.

## 🔄 Flujo de Datos

### Flujo de Creación de Campaña

1. El usuario crea una nueva campaña a través de la interfaz web.
2. El controlador procesa la solicitud y crea un registro en la base de datos.
3. Se inicia una tarea de Celery para publicar la campaña en la plataforma seleccionada.
4. El cliente de API correspondiente (Meta o Google) envía la solicitud a la API externa.
5. La respuesta de la API se procesa y se actualiza el estado de la campaña en la base de datos.
6. Se programan tareas periódicas para sincronizar métricas y estados.

### Flujo de Segmentación de Candidatos

1. Los datos de candidatos se cargan desde la base de datos.
2. El módulo de ML preprocesa los datos (normalización, codificación, etc.).
3. El algoritmo K-means agrupa a los candidatos en segmentos.
4. Los resultados se almacenan en la base de datos.
5. Las campañas pueden dirigirse a segmentos específicos.

## 🔌 Integraciones

### Meta (Facebook/Instagram) Ads API

- **Autenticación**: OAuth 2.0 con token de acceso de larga duración.
- **Funcionalidades**: Creación de campañas, conjuntos de anuncios, anuncios y obtención de métricas.
- **Módulos**: `adflux.api.meta.*`

### Google Ads API

- **Autenticación**: OAuth 2.0 con token de actualización.
- **Funcionalidades**: Creación de campañas, grupos de anuncios, anuncios y obtención de métricas.
- **Módulos**: `adflux.api.google.*`

### Gemini AI API

- **Autenticación**: Clave de API.
- **Funcionalidades**: Generación de texto creativo, simulación de datos.
- **Módulos**: `adflux.api.gemini.*`

## 🧠 Procesamiento en Segundo Plano

AdFlux utiliza Celery con Redis como broker para ejecutar tareas en segundo plano:

- **Publicación de Campañas**: Procesos que pueden tardar debido a las llamadas a APIs externas.
- **Sincronización de Métricas**: Actualización periódica de datos de rendimiento.
- **Generación de Informes**: Creación de informes complejos sin bloquear la interfaz de usuario.
- **Entrenamiento de Modelos ML**: Procesos intensivos de cómputo para segmentación.

## 🛡️ Seguridad

- **CSRF Protection**: Protección contra ataques de falsificación de solicitudes entre sitios.
- **Manejo Seguro de Credenciales**: Variables de entorno y almacenamiento seguro.
- **Validación de Entrada**: Validación de formularios y datos de API.
- **Manejo de Errores**: Captura y registro adecuado de excepciones.

## 📈 Escalabilidad

La arquitectura de AdFlux está diseñada para escalar:

- **Modularidad**: Componentes independientes que pueden escalarse por separado.
- **Procesamiento Asíncrono**: Tareas intensivas desacopladas de la interfaz de usuario.
- **Caching**: Implementación de caché para reducir llamadas a APIs externas.
- **Diseño Stateless**: Facilita la implementación en múltiples servidores.

## 🔍 Monitoreo y Logging

- **Logging Estructurado**: Registro detallado de eventos y errores.
- **Monitoreo de Tareas**: Seguimiento del estado de tareas de Celery.
- **Alertas**: Notificaciones sobre errores críticos o problemas de integración.

## 📝 Consideraciones de Diseño

- **Separación de Responsabilidades**: Cada módulo tiene una función específica.
- **Extensibilidad**: Facilidad para agregar nuevas plataformas publicitarias.
- **Mantenibilidad**: Código organizado y documentado.
- **Experiencia de Usuario**: Interfaz intuitiva y responsive.

## 🔮 Evolución Futura

La arquitectura permite futuras mejoras como:

- Integración con más plataformas publicitarias.
- Implementación de algoritmos de ML más avanzados.
- Desarrollo de una API más completa para integración con otros sistemas.
- Implementación de análisis predictivo para optimización de campañas.
