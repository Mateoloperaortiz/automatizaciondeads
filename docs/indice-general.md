# Índice General de la Documentación de AdFlux

Este índice proporciona una visión general de toda la documentación disponible para AdFlux, organizada por secciones.

## Introducción

- [README](./README.md): Introducción general a la documentación de AdFlux.

## Arquitectura

- [Visión General](./arquitectura/README.md): Introducción a la arquitectura de AdFlux.
- [Overview](./arquitectura/overview.md): Descripción general de la arquitectura del sistema.
- [Modelos de Datos](./arquitectura/modelos-datos.md): Estructura y relaciones de los modelos de datos.
- [Patrones de Diseño](./arquitectura/patrones-diseno.md): Patrones de diseño utilizados en AdFlux.
- [Servicios](./arquitectura/servicios.md): Descripción de los servicios principales del sistema.
- [Flujos de Trabajo](./arquitectura/flujos-trabajo.md): Diagramas y explicaciones de los flujos de trabajo principales.
- [Integración con APIs Externas](./arquitectura/integracion-apis.md): Arquitectura de integración con APIs de terceros.
- [Decisiones de Arquitectura](./arquitectura/decisiones/): Registro de decisiones de arquitectura (ADRs).

## APIs

- [Visión General](./apis/README.md): Introducción a las APIs utilizadas en AdFlux.
- [API Interna](./apis/interna/): Documentación de la API RESTful de AdFlux.
- [Meta API](./apis/meta/overview.md): Integración con la API de Meta (Facebook/Instagram).
- [Google Ads API](./apis/google/): Integración con la API de Google Ads.
- [TikTok API](./apis/tiktok/): Integración con la API de TikTok Ads.
- [Snapchat API](./apis/snapchat/): Integración con la API de Snapchat Ads.
- [Gemini API](./apis/gemini/overview.md): Integración con la API de Gemini AI.

## Guías de Usuario

- [Introducción](./usuario/README.md): Introducción a las guías de usuario.
- [Introducción a AdFlux](./usuario/introduccion.md): Introducción general a AdFlux.
- [Inicio Rápido](./usuario/inicio-rapido.md): Guía para comenzar a utilizar AdFlux rápidamente.
- [Conceptos Clave](./usuario/conceptos-clave.md): Conceptos fundamentales para entender AdFlux.
- [Tutoriales](./usuario/tutoriales/): Tutoriales paso a paso para diferentes funcionalidades.
  - [Creación de Campañas](./usuario/tutoriales/crear-campana.md): Cómo crear una campaña publicitaria.
  - [Segmentación de Audiencias](./usuario/tutoriales/segmentacion.md): Cómo segmentar audiencias para campañas.
  - [Creación de Anuncios](./usuario/tutoriales/crear-anuncios.md): Cómo crear anuncios efectivos.
  - [Análisis de Métricas](./usuario/tutoriales/analisis-metricas.md): Cómo analizar el rendimiento de campañas.
- [Preguntas Frecuentes](./usuario/faq.md): Respuestas a preguntas comunes.
- [Solución de Problemas](./usuario/solucion-problemas.md): Guía para resolver problemas comunes.

## Desarrollo

- [Visión General](./desarrollo/README.md): Introducción a las guías de desarrollo.
- [Configuración del Entorno](./desarrollo/configuracion.md): Instrucciones para configurar el entorno de desarrollo.
- [Arquitectura del Código](./desarrollo/arquitectura-codigo.md): Descripción detallada de la estructura del código.
- [Guía de Contribución](./desarrollo/contribucion.md): Directrices para contribuir al proyecto.
- [Estándares de Código](./desarrollo/estandares-codigo.md): Estándares y convenciones de codificación.
- [Pruebas](./desarrollo/pruebas.md): Guía para escribir y ejecutar pruebas.
- [Integración Continua](./desarrollo/integracion-continua.md): Información sobre el pipeline de CI/CD.
- [Extensiones](./desarrollo/extensiones/): Guías para extender la funcionalidad de AdFlux.

## Machine Learning

- [Visión General](./machine-learning/README.md): Introducción a los componentes de ML en AdFlux.
- [Segmentación de Audiencias](./machine-learning/segmentacion-audiencias.md): Algoritmos para segmentar candidatos.
- [Optimización de Contenido](./machine-learning/optimizacion-contenido.md): Generación y optimización de contenido para anuncios.
- [Predicción de Rendimiento](./machine-learning/prediccion-rendimiento.md): Modelos para predecir el rendimiento de campañas.
- [Integración con Gemini AI](./machine-learning/integracion-gemini.md): Detalles sobre la integración con Gemini AI.
- [Simulación de Datos](./machine-learning/simulacion-datos.md): Generación de datos sintéticos para pruebas.

## Seguridad

- [Visión General](./seguridad/README.md): Introducción al modelo de seguridad de AdFlux.
- [Autenticación y Autorización](./seguridad/autenticacion-autorizacion.md): Información sobre el sistema de autenticación y control de acceso.
- [Protección de Datos](./seguridad/proteccion-datos.md): Medidas para proteger datos sensibles.
- [Seguridad de APIs](./seguridad/seguridad-apis.md): Medidas de seguridad para las APIs internas y externas.
- [Auditoría y Cumplimiento](./seguridad/auditoria-cumplimiento.md): Información sobre auditoría, logging y cumplimiento normativo.
- [Guía de Respuesta a Incidentes](./seguridad/respuesta-incidentes.md): Procedimientos para responder a incidentes de seguridad.
- [Mejores Prácticas](./seguridad/mejores-practicas.md): Recomendaciones para mantener la seguridad del sistema.

## Despliegue

- [Visión General](./despliegue/README.md): Introducción a las guías de despliegue.
- [Requisitos](./despliegue/requisitos.md): Requisitos de sistema para desplegar AdFlux.
- [Despliegue Local](./despliegue/local.md): Instrucciones para desplegar AdFlux en un entorno local.
- [Despliegue en Producción](./despliegue/produccion.md): Guía completa para desplegar AdFlux en un entorno de producción.
- [Despliegue con Docker](./despliegue/docker.md): Instrucciones para desplegar AdFlux utilizando Docker y Docker Compose.
- [Despliegue en la Nube](./despliegue/nube/): Guías para desplegar AdFlux en diferentes proveedores de nube.
- [Configuración](./despliegue/configuracion.md): Opciones de configuración para diferentes entornos.
- [Escalabilidad](./despliegue/escalabilidad.md): Estrategias para escalar AdFlux.
- [Monitorización](./despliegue/monitorizacion.md): Configuración de monitorización y alertas.
- [Copias de Seguridad](./despliegue/copias-seguridad.md): Estrategias para realizar copias de seguridad.
- [Actualización](./despliegue/actualizacion.md): Procedimientos para actualizar AdFlux.

## Referencia

- [Visión General](./referencia/README.md): Introducción a la documentación de referencia.
- [API](./referencia/api/): Documentación detallada de la API de AdFlux.
- [Modelos de Datos](./referencia/modelos/): Documentación de los modelos de datos de AdFlux.
- [Servicios](./referencia/servicios/): Documentación de los servicios de AdFlux.
- [Utilidades](./referencia/utilidades/): Documentación de las utilidades y helpers.
- [Configuración](./referencia/configuracion.md): Opciones de configuración disponibles.
- [Glosario](./referencia/glosario.md): Términos y definiciones utilizados en AdFlux.
- [Changelog](./referencia/changelog.md): Historial de cambios de AdFlux.

## Pruebas

- [Visión General](./tests/README.md): Introducción a las pruebas en AdFlux.
- [Pruebas Unitarias](./tests/unit/): Pruebas para componentes individuales.
- [Pruebas de Integración](./tests/integration/): Pruebas para la interacción entre componentes.
- [Pruebas Funcionales](./tests/functional/): Pruebas para flujos completos de la aplicación.
- [Pruebas de Seguridad](./tests/security/): Pruebas para verificar la seguridad del sistema.
- [Pruebas de Rendimiento](./tests/performance/): Pruebas para verificar el rendimiento del sistema.

## Contribución

Si deseas contribuir a la documentación de AdFlux, consulta la [Guía de Contribución](./desarrollo/contribucion.md) para obtener información sobre cómo hacerlo.
