# Guías de Desarrollo

Esta sección contiene documentación detallada para desarrolladores que deseen contribuir al proyecto AdFlux o extender su funcionalidad.

## Contenido

- [Configuración del Entorno](./configuracion.md): Instrucciones para configurar el entorno de desarrollo.
- [Arquitectura del Código](./arquitectura-codigo.md): Descripción detallada de la estructura del código.
- [Guía de Contribución](./contribucion.md): Directrices para contribuir al proyecto.
- [Estándares de Código](./estandares-codigo.md): Estándares y convenciones de codificación.
- [Pruebas](./pruebas.md): Guía para escribir y ejecutar pruebas.
- [Integración Continua](./integracion-continua.md): Información sobre el pipeline de CI/CD.
- [Extensiones](./extensiones/): Guías para extender la funcionalidad de AdFlux.

## Primeros Pasos

Si eres nuevo en el desarrollo de AdFlux, te recomendamos comenzar con:

1. [Configuración del Entorno](./configuracion.md)
2. [Arquitectura del Código](./arquitectura-codigo.md)
3. [Guía de Contribución](./contribucion.md)

## Flujo de Trabajo de Desarrollo

El flujo de trabajo típico para desarrollar en AdFlux es:

1. Configurar el entorno de desarrollo
2. Crear una rama de feature desde `main`
3. Implementar cambios siguiendo los estándares de código
4. Escribir pruebas para los cambios
5. Ejecutar pruebas localmente
6. Enviar un pull request
7. Revisar y abordar comentarios
8. Fusionar cambios a `main`

## Extensiones

AdFlux está diseñado para ser extensible. Puedes crear:

- [Nuevos Conectores de API](./extensiones/conectores-api.md): Para integrar con nuevas plataformas publicitarias.
- [Nuevos Modelos de ML](./extensiones/modelos-ml.md): Para implementar nuevos algoritmos de machine learning.
- [Nuevos Generadores de Contenido](./extensiones/generadores-contenido.md): Para crear contenido para diferentes formatos de anuncios.
- [Nuevos Proveedores de Datos](./extensiones/proveedores-datos.md): Para integrar con fuentes de datos externas.

## Recursos Adicionales

- [API de Referencia](../referencia/api/): Documentación detallada de la API interna.
- [Modelos de Datos](../arquitectura/modelos-datos.md): Descripción de los modelos de datos.
- [Decisiones de Arquitectura](../arquitectura/decisiones/): Registro de decisiones de arquitectura (ADRs).

## Soporte para Desarrolladores

Si tienes preguntas o necesitas ayuda:

- Abre un issue en el [repositorio de GitHub](https://github.com/adflux/adflux)
- Únete al [canal de Slack para desarrolladores](https://slack.adflux.example.com)
- Contacta al [equipo de desarrollo](mailto:dev@adflux.example.com)
