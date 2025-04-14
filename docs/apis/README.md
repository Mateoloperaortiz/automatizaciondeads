# Documentación de APIs

Esta sección contiene documentación detallada sobre las APIs utilizadas en AdFlux, tanto internas como externas.

## Contenido

- [API Interna](./interna/): Documentación de la API RESTful de AdFlux.
- [Meta API](./meta/): Integración con la API de Meta (Facebook/Instagram).
- [Google Ads API](./google/): Integración con la API de Google Ads.
- [TikTok API](./tiktok/): Integración con la API de TikTok Ads.
- [Snapchat API](./snapchat/): Integración con la API de Snapchat Ads.
- [Gemini API](./gemini/): Integración con la API de Gemini AI.

## API Interna

AdFlux proporciona una API RESTful para permitir la integración con sistemas externos. La API está documentada utilizando Swagger/OpenAPI y está disponible en `/api/docs` cuando la aplicación está en ejecución.

## APIs Externas

AdFlux se integra con varias APIs externas para publicar anuncios en diferentes plataformas. Cada integración está documentada en su respectiva sección, incluyendo:

- Configuración y autenticación
- Endpoints utilizados
- Modelos de datos
- Ejemplos de uso
- Manejo de errores
- Limitaciones y consideraciones

## Autenticación

La API interna de AdFlux utiliza autenticación JWT (JSON Web Tokens). Para obtener un token, se debe hacer una solicitud POST a `/api/auth/login` con las credenciales de usuario.

Las APIs externas utilizan diferentes métodos de autenticación, que están documentados en sus respectivas secciones.

## Versionado

La API interna de AdFlux sigue un esquema de versionado semántico. La versión actual es v1, accesible en `/api/v1/`.

## Límites de Tasa

Para proteger los recursos del sistema, la API interna de AdFlux implementa límites de tasa. Los límites actuales son:

- 1000 solicitudes por hora por IP
- 100 solicitudes por minuto por usuario autenticado

Las APIs externas también tienen sus propios límites de tasa, que están documentados en sus respectivas secciones.

## Errores

La API interna de AdFlux devuelve errores en formato JSON con los siguientes campos:

```json
{
  "error": "string",
  "message": "string",
  "status_code": 400,
  "details": {}
}
```

## Ejemplos de Uso

Cada sección de API incluye ejemplos de uso con curl, Python y JavaScript.
