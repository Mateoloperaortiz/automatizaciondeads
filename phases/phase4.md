# Fase 4: Pruebas

## Estado Actual: EN PROGRESO (40% Completo)

## Puntos Clave

- El sistema AdFlux requiere pruebas exhaustivas para garantizar la fiabilidad, funcionalidad y seguridad.
- Se han implementado pruebas unitarias básicas para los componentes principales, y se están realizando pruebas más completas.
- Se han desarrollado pruebas de integración para los endpoints de la API, centrándose en la validación de datos y el manejo de errores.
- Las pruebas de extremo a extremo y las pruebas de seguridad están planificadas pero aún no se han implementado por completo.
- Todas las pruebas utilizan entornos sandbox/de prueba para las API de redes sociales para evitar afectar los datos reales.

## Estrategia de Pruebas

La estrategia de pruebas para AdFlux sigue un enfoque de múltiples capas para garantizar que todos los aspectos del sistema se validen a fondo. Esto incluye pruebas unitarias para componentes individuales, pruebas de integración para las interacciones de los componentes, pruebas de extremo a extremo para flujos de trabajo completos y pruebas de seguridad para la evaluación de vulnerabilidades.

## Implementación Actual

### Pruebas Unitarias

- **Pruebas de Modelos**: Pruebas básicas para modelos de base de datos y relaciones
- **Pruebas de Clientes API**: Pruebas para funciones de clientes API de Meta y Google Ads usando mocks
- **Pruebas de Modelos ML**: Pruebas para el algoritmo de clustering K-means y funciones de predicción
- **Pruebas de Funciones de Utilidad**: Pruebas para funciones auxiliares y utilidades de procesamiento de datos

### Pruebas de Integración

- **Pruebas de Endpoints API**: Pruebas para endpoints de API RESTful usando el cliente de prueba de Flask
- **Pruebas de Integración de Base de Datos**: Pruebas para operaciones y transacciones de base de datos
- **Pruebas de Validación de Formularios**: Pruebas para validación y procesamiento de formularios web

### Pruebas de Extremo a Extremo

- **Script de Prueba**: Script de prueba inicial para la integración de la API de Google Ads (`test_google_ads.py`)
- **Prueba de Endpoint API**: Prueba básica para la funcionalidad del endpoint de la API (`test_endpoint.py`)

## Infraestructura de Pruebas

### Herramientas de Prueba

- **pytest**: Framework principal de pruebas para todos los tipos de pruebas
- **unittest.mock**: Para simular dependencias y servicios externos
- **Flask Test Client**: Para probar rutas y vistas de Flask
- **SQLAlchemy Test Utilities**: Para pruebas de base de datos

### Entorno de Prueba

- **Base de Datos SQLite**: Base de datos en memoria para pruebas
- **Respuestas API Mock**: Respuestas simuladas para llamadas a API externas
- **Credenciales API Sandbox**: Credenciales de prueba para las API de Meta y Google Ads

## Mejoras Planificadas

### Pruebas Unitarias

- **Pruebas de Controladores**: Pruebas para la lógica de negocio en funciones de controlador
- **Pruebas de Tareas**: Pruebas para tareas asíncronas de Celery
- **Pruebas de Esquemas**: Pruebas para serialización y validación de datos
- **Pruebas de Comandos**: Pruebas para comandos CLI

### Pruebas de Integración

- **Pruebas de Integración de Servicios**: Pruebas para interacciones de la capa de servicio
- **Pruebas de Integración de API Externas**: Pruebas para interacciones con las API de Meta y Google Ads
- **Pruebas de Integración de Tareas Celery**: Pruebas para operaciones de la cola de tareas

### Pruebas de Extremo a Extremo

- **Flujo de Trabajo de Creación de Campañas**: Probar el proceso completo de creación y publicación de campañas
- **Flujo de Trabajo de Segmentación de Candidatos**: Probar el proceso de segmentación de extremo a extremo
- **Flujo de Trabajo de Sincronización de Datos**: Probar la sincronización con plataformas externas

### Pruebas de Seguridad

- **Pruebas de Autenticación**: Pruebas para la autenticación y autorización de usuarios
- **Pruebas de Validación de Entradas**: Pruebas para protección contra ataques de inyección
- **Pruebas de Seguridad de Claves API**: Pruebas para el manejo seguro de credenciales API
- **Pruebas de Protección CSRF**: Pruebas para protección contra falsificación de solicitudes entre sitios

## Casos de Prueba

Aquí hay ejemplos de casos de prueba implementados y planificados para cada nivel de prueba:

### Pruebas Unitarias

**Implementado:**
- Probar si el modelo JobOpening valida correctamente los campos requeridos
- Probar si el modelo de clustering K-means segmenta correctamente datos de candidatos de muestra
- Probar si el cliente API de Meta formatea correctamente las solicitudes de creación de campañas

**Planificado:**
- Probar si el endpoint API GET /api/v1/jobs devuelve un código de estado 200 y una lista de ofertas de trabajo
- Probar si las consultas a la base de datos filtran correctamente las ofertas de trabajo por ubicación o habilidades
- Probar si la validación de formularios maneja correctamente entradas inválidas

### Pruebas de Integración

**Implementado:**
- Probar si el sistema puede autenticarse con el entorno sandbox de Meta
- Probar si el cliente de la API de Google Ads puede crear una campaña de prueba

**Planificado:**
- Probar si el sistema puede obtener ofertas de trabajo de la base de datos y crear un objeto de campaña
- Probar si el modelo de aprendizaje automático puede segmentar candidatos y el sistema puede dirigirse a estos segmentos
- Probar si las tareas de Celery procesan correctamente las operaciones en segundo plano

### Pruebas de Extremo a Extremo

**Implementado:**
- Script de prueba básico para la integración de la API de Google Ads
- Prueba simple para la funcionalidad del endpoint de la API

**Planificado:**
- Probar el proceso completo de seleccionar una oferta de trabajo, segmentar candidatos, crear una campaña publicitaria y publicarla
- Probar el proceso de programar múltiples campañas publicitarias para diferentes ofertas de trabajo
- Probar la recuperación de métricas de rendimiento de campañas desde plataformas de redes sociales

### Pruebas de Seguridad

**Implementado:**
- Validación básica de variables de entorno para credenciales API

**Planificado:**
- Probar si las claves API y los tokens se almacenan de forma segura y no se exponen en logs o respuestas
- Probar si los mecanismos de autenticación previenen el acceso no autorizado a funciones de administrador
- Probar si la validación de entradas previene ataques de inyección SQL o cross-site scripting

## Infraestructura de Pruebas

### Configuración del Entorno de Pruebas

```python
# Ejemplo de configuración de prueba (tests/conftest.py)
import pytest
from adflux.core import create_app
from adflux.extensions import db as _db
from adflux.config import TestConfig

@pytest.fixture(scope='session')
def app():
    """Crear y configurar una aplicación Flask para pruebas."""
    app = create_app(TestConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Crear y configurar una base de datos para pruebas."""
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Crear un cliente de prueba para la aplicación."""
    with app.test_client() as client:
        yield client
```

### Configuración de Mock

```python
# Ejemplo de configuración de mock para la API de Meta (tests/test_meta_api.py)
import unittest.mock as mock
import pytest
from adflux.api_clients import create_meta_campaign

def test_create_meta_campaign():
    # Simular los objetos FacebookAdsApi y Campaign
    with mock.patch('facebook_business.api.FacebookAdsApi') as mock_api, \
         mock.patch('facebook_business.adobjects.campaign.Campaign') as mock_campaign:
        # Configurar los mocks
        mock_campaign.return_value.api_create.return_value = {'id': '123456789'}

        # Llamar a la función bajo prueba
        result = create_meta_campaign('act_123456', 'Campaña de Prueba', 'PAUSADA', 1000)

        # Afirmar el resultado esperado
        assert result['id'] == '123456789'
        # Afirmar que la función llamó a la API correctamente
        mock_campaign.return_value.api_create.assert_called_once()
```

## Integración Continua

Se planea una canalización básica de integración continua (CI) utilizando GitHub Actions para ejecutar automáticamente las pruebas cada vez que se envía código al repositorio. Esto asegurará que los nuevos cambios no rompan la funcionalidad existente.

### Flujo de Trabajo Planificado de GitHub Actions

```yaml
name: AdFlux CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Configurar Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Instalar dependencias
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Ejecutar pruebas
      run: |
        pytest
    - name: Ejecutar linting
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

#### Estrategia de Pruebas

La estrategia de pruebas abarca múltiples niveles de pruebas para validar diferentes aspectos del sistema, asegurando que cumpla con los requisitos funcionales y no funcionales, como escalabilidad, rendimiento y seguridad. La estrategia incluye:

1.  **Pruebas Unitarias:** Se centra en componentes individuales como endpoints API, modelos de aprendizaje automático y consultas a la base de datos para asegurar que funcionen como se espera de forma aislada. Esto es crítico para verificar la corrección de cada parte antes de integrarlas.

2.  **Pruebas de Integración:** Verifica las interacciones entre diferentes componentes, como la capacidad del backend para obtener datos de la base de datos y comunicarse con las API de redes sociales. Esto asegura que el sistema funcione de manera cohesiva en su conjunto.

3.  **Pruebas de Extremo a Extremo:** Simula todo el proceso desde la obtención de ofertas de trabajo hasta la publicación de anuncios en plataformas de redes sociales utilizando entornos sandbox. Esto valida el flujo de trabajo del sistema y asegura que cumpla con las expectativas del usuario para el proceso completo.

4.  **Pruebas de Seguridad:** Asegura que las medidas de seguridad estén implementadas, como el almacenamiento seguro de claves API, mecanismos de autenticación adecuados y encriptación de datos, para prevenir el acceso no autorizado y proteger la información sensible.

Dados los límites del proyecto universitario, las pruebas utilizarán datos simulados y se centrarán en las funcionalidades principales, con énfasis en el uso de entornos sandbox para las API de redes sociales para evitar afectar datos reales o incurrir en costos.

#### Pruebas Unitarias

**Componentes a Probar:**

-   Endpoints API, como GET /job_openings, POST /ad_campaigns y GET /segments, para asegurar que manejen las solicitudes correctamente y devuelvan las respuestas esperadas.
-   Funciones del modelo de aprendizaje automático, como el algoritmo de clustering, para verificar que segmenta a los candidatos con precisión según los datos de entrada.
-   Funciones de consulta a la base de datos, como obtener ofertas de trabajo o recuperar perfiles de candidatos, para asegurar que recuperen los datos correctos de PostgreSQL.

**Herramientas:**

-   Pytest: Un robusto framework de pruebas para Python que soporta fixtures, pruebas parametrizadas y mocking, elegido por su simplicidad e integración con la pila Python del proyecto.

**Enfoque:**

-   Escribir casos de prueba para cada función o método para verificar el comportamiento correcto bajo diversas condiciones, incluyendo casos límite y escenarios de error. Por ejemplo, probar endpoints API con entradas inválidas para asegurar un manejo adecuado de errores.
-   Usar mocking donde sea necesario para aislar dependencias, como simular llamadas a la base de datos usando unittest.mock o pytest-mock, o simular respuestas de API externas para probar sin llamadas API reales.
-   Asegurar la cobertura de pruebas para rutas críticas, como crear y recuperar ofertas de trabajo, segmentar candidatos y gestionar campañas publicitarias, alineándose con las historias de usuario de la Fase 1.

**Ejemplo de Caso de Prueba:**

-   **ID de Prueba:** UT-001
-   **Descripción de la Prueba:** Verificar que GET /job_openings devuelve una lista de ofertas de trabajo.
-   **Precondiciones:** La base de datos contiene al menos una oferta de trabajo.
-   **Pasos de Prueba:**
    1.  Enviar una solicitud GET a /job_openings.
-   **Resultados Esperados:** Código de estado de respuesta 200 y una lista JSON de ofertas de trabajo.
-   **Resultados Reales:** [A completar durante las pruebas]
-   **Estado Pasa/Falla:** [A completar durante las pruebas]

Este enfoque asegura que los componentes individuales se prueben a fondo, proporcionando una base sólida para las pruebas de integración.

#### Pruebas de Integración

**Componentes a Probar:**

-   Interacción entre el backend y la base de datos, como obtener ofertas de trabajo y almacenar campañas publicitarias, para asegurar que los datos fluyan correctamente.
-   Interacción entre el backend y las API de redes sociales, como crear anuncios en Meta, X o Google, para verificar la capacidad del sistema para publicar anuncios.
-   Interacción entre el backend y el módulo de aprendizaje automático, como segmentar candidatos y usar segmentos para la segmentación, para asegurar una integración sin problemas.

**Herramientas:**

-   Pytest con bibliotecas de mocking como unittest.mock o pytest-mock para simular dependencias externas, como las API de redes sociales, asegurando que las pruebas puedan ejecutarse sin llamadas API en vivo.
-   Herramientas de prueba de base de datos si es necesario, como las utilidades de prueba incorporadas de SQLAlchemy, para verificar las interacciones con la base de datos.

**Enfoque:**

-   Escribir pruebas que verifiquen la correcta integración de los componentes, asegurando que los datos fluyan correctamente entre ellos. Por ejemplo, probar si una oferta de trabajo obtenida de la base de datos se puede usar para crear una campaña publicitaria a través de la API de redes sociales (simulada).
-   Usar mocking para simular respuestas de API externas, asegurando que el sistema se comporte como se espera bajo diversas condiciones, como límites de tasa de API o errores.
-   Probar puntos críticos de integración, como la capacidad del backend para obtener datos de candidatos, segmentarlos y usar los segmentos para la segmentación de anuncios, alineándose con el flujo de trabajo del sistema.

**Ejemplo de Caso de Prueba:**

-   **ID de Prueba:** IT-001
-   **Descripción de la Prueba:** Verificar que el backend puede obtener una oferta de trabajo y crear un anuncio en Meta (simulado).
-   **Precondiciones:** La base de datos contiene una oferta de trabajo con ID 1.
-   **Pasos de Prueba:**
    1.  Simular la respuesta de la API de Meta.
    2.  Llamar a la función para crear un anuncio para el trabajo ID 1 en Meta.
-   **Resultados Esperados:** La función devuelve éxito, y la llamada API simulada se realiza con los parámetros correctos.
-   **Resultados Reales:** [A completar durante las pruebas]
-   **Estado Pasa/Falla:** [A completar durante las pruebas]

Este enfoque asegura que los componentes del sistema funcionen juntos sin problemas, validando los puntos de integración críticos para la funcionalidad del sistema.

#### Pruebas de Extremo a Extremo

**Proceso a Probar:**

-   Todo el flujo de trabajo desde la selección de una oferta de trabajo, elección de plataformas, segmentación de audiencias, creación de anuncios y publicación en entornos sandbox. Esto incluye:
    -   Obtener ofertas de trabajo de la base de datos.
    -   Usar el módulo de aprendizaje automático para segmentar candidatos basados en datos simulados.
    -   Crear campañas publicitarias para plataformas seleccionadas usando sus API en modo de prueba.
    -   Publicar anuncios y verificar que el proceso se complete con éxito.

**Herramientas:**

-   La biblioteca requests de Python para pruebas API, enviando solicitudes HTTP a los endpoints del sistema para simular interacciones de usuario.
-   Selenium o similar si hay una interfaz web, pero dada la interfaz simple del proyecto, las pruebas API podrían ser suficientes.
-   Entornos sandbox de las plataformas de redes sociales, como el Administrador de Anuncios de Prueba de Meta, el Sandbox de Desarrolladores de X y las Cuentas de Prueba de Google Ads, para asegurar que las pruebas no afecten los datos reales.

**Enfoque:**

-   Simular acciones del usuario a través de las interfaces del sistema para asegurar que el proceso completo funcione como se espera. Por ejemplo, enviar una secuencia de llamadas API para seleccionar una oferta de trabajo, elegir plataformas e iniciar la publicación, verificando cada paso.
-   Usar entornos sandbox para las API de redes sociales para crear y publicar anuncios sin impacto en el mundo real, asegurando la rentabilidad y el cumplimiento de las políticas de la plataforma.
-   Verificar que el sistema registre el proceso y devuelva mensajes apropiados de éxito o error, alineándose con las expectativas del usuario para el flujo de extremo a extremo.

**Ejemplo de Caso de Prueba:**

-   **ID de Prueba:** E2E-001
-   **Descripción de la Prueba:** Simular la publicación de un anuncio para una oferta de trabajo en Meta en modo sandbox.
-   **Precondiciones:** Sistema configurado con una oferta de trabajo de prueba y cuenta sandbox de Meta.
-   **Pasos de Prueba:**
    1.  Iniciar sesión en el sistema (si aplica).
    2.  Seleccionar la oferta de trabajo de prueba.
    3.  Elegir Meta como plataforma.
    4.  Iniciar la publicación del anuncio.
-   **Resultados Esperados:** El anuncio se crea en el entorno sandbox de Meta, y el sistema registra el éxito.
-   **Resultados Reales:** [A completar durante las pruebas]
-   **Estado Pasa/Falla:** [A completar durante las pruebas]

Este enfoque asegura que el sistema funcione como un todo, validando el flujo de trabajo completo y preparándolo para el despliegue.

#### Pruebas de Seguridad

**Aspectos a Probar:**

-   Almacenamiento seguro de claves API y credenciales, asegurando que no estén hardcodeadas y se almacenen en variables de entorno o bóvedas seguras como AWS Secrets Manager.
-   Mecanismos de autenticación y autorización, verificando que solo los usuarios autorizados puedan acceder a recursos protegidos, como endpoints API para la publicación de anuncios.
-   Encriptación de datos en tránsito y en reposo, asegurando que se use HTTPS para las comunicaciones API y que los datos de la base de datos estén encriptados usando la encriptación de RDS.
-   Vulnerabilidad a ataques comunes, como inyección SQL (si aplica), cross-site scripting (XSS) si hay una interfaz web, y asegurar que la validación de entradas prevenga tales problemas.

**Herramientas:**

-   Inspección manual y revisiones de código para verificar prácticas de seguridad, como almacenamiento seguro de credenciales y autenticación adecuada.
-   Herramientas automatizadas como Bandit para análisis de seguridad de código Python, escaneando vulnerabilidades comunes como secretos hardcodeados o configuraciones inseguras.
-   OWASP ZAP o similar para pruebas de seguridad de aplicaciones web si hay un frontend, pero dado el alcance del proyecto, las verificaciones manuales podrían ser suficientes.

**Enfoque:**

-   Asegurar que toda la información sensible se almacene de forma segura, usando variables de entorno o AWS Secrets Manager, y verificar esto a través de revisiones de código.
-   Verificar que se requiera autenticación para acceder a recursos protegidos, como enviar solicitudes no autorizadas a endpoints API y verificar respuestas 401 Unauthorized.
-   Verificar que los datos estén encriptados donde sea necesario, como usar HTTPS para comunicaciones API, y asegurar que la encriptación de la base de datos esté habilitada en RDS.
-   Probar vulnerabilidades comunes intentando inyectar entradas maliciosas y verificando que el sistema las maneje apropiadamente, alineándose con las mejores prácticas de seguridad.

**Ejemplo de Caso de Prueba:**

-   **ID de Prueba:** SEC-001
-   **Descripción de la Prueba:** Verificar que los endpoints API requieran autenticación.
-   **Precondiciones:** El usuario no está autenticado.
-   **Pasos de Prueba:**
    1.  Enviar una solicitud GET a /ad_campaigns sin autenticación.
-   **Resultados Esperados:** Código de estado de respuesta 401 Unauthorized.
-   **Resultados Reales:** [A completar durante las pruebas]
-   **Estado Pasa/Falla:** [A completar durante las pruebas]

Este enfoque asegura que el sistema sea seguro, protegiendo datos sensibles y previniendo accesos no autorizados, crítico para un despliegue robusto.

#### Desarrollo de Casos de Prueba

Se deben desarrollar casos de prueba para cada tipo de prueba, cubriendo escenarios tanto positivos como negativos. Cada caso de prueba debe incluir:

-   ID de Prueba
-   Descripción de la Prueba
-   Precondiciones
-   Pasos de Prueba
-   Resultados Esperados
-   Resultados Reales
-   Estado Pasa/Falla

Se proporcionan ejemplos arriba para cada tipo de prueba, asegurando una cobertura completa. Los casos de prueba se documentarán en un repositorio de casos de prueba, como un repositorio de GitHub, para seguimiento y referencia durante las pruebas.

#### Seguimiento y Resolución de Incidencias

Cualquier error o incidencia identificada durante las pruebas se documentará en un sistema de seguimiento de incidencias, como GitHub Issues, con detalles que incluyan:

-   ID de Incidencia
-   Descripción
-   Pasos para reproducir
-   Comportamiento esperado
-   Comportamiento real
-   Severidad
-   Asignado a
-   Estado

El equipo de desarrollo priorizará y abordará estas incidencias, asegurando que los errores críticos se corrijan antes del despliegue. Se realizarán repruebas para verificar las correcciones, utilizando los mismos casos de prueba para asegurar que la incidencia se haya resuelto. Por ejemplo, si se encuentra un error en el endpoint API para publicar anuncios, se registrará, corregirá y volverá a probar para asegurar que el endpoint ahora funcione como se espera.

#### Consideraciones de Implementación

Un detalle inesperado es la variabilidad en el soporte API entre las plataformas de redes sociales, con Meta, X y Google ofreciendo bibliotecas Python oficiales, mientras que TikTok y Snapchat pueden requerir wrappers no oficiales o solicitudes HTTP directas. Esta variabilidad necesita un enfoque de prueba flexible, asegurando que las pruebas de integración tengan en cuenta las posibles diferencias en el comportamiento de la API, especialmente en entornos sandbox. Dado el cronograma del proyecto universitario, céntrate en las tres plataformas principales para gestionar el alcance, pero documenta cualquier desafío encontrado para referencia futura.

#### Tabla: Resumen de Actividades y Herramientas de Prueba

| Tipo de Prueba        | Componentes Probados                              | Herramientas Usadas                     | ID Ejemplo Caso Prueba |
|--------------------|-----------------------------------------------|--------------------------------|---------------------|
| Pruebas Unitarias       | Endpoints API, modelos ML, consultas BD     | Pytest, unittest.mock          | UT-001              |
| Pruebas Integración| Backend-BD, backend-APIs, backend-ML     | Pytest, pytest-mock            | IT-001              |
| Pruebas E2E        | Flujo completo, publicación anuncios sandbox | requests, sandboxes redes soc.| E2E-001             |
| Pruebas Seguridad   | Alm. claves API, autenticación, encriptación | Bandit, revisiones manuales    | SEC-001             |

Esta tabla resume las actividades clave de prueba, herramientas y ejemplos de casos de prueba, asegurando claridad para la ejecución.

#### Conclusión

El enfoque de prueba recomendado para la Fase 4 proporciona un proceso estructurado para asegurar que el sistema Ad Automation P-01 funcione correctamente, cumpla con los requisitos y sea fiable y seguro. Incluye pruebas unitarias, pruebas de integración, pruebas de extremo a extremo y pruebas de seguridad, utilizando herramientas apropiadas y entornos sandbox, resultando en un sistema probado con casos de prueba documentados e incidencias resueltas, listo para el despliegue en mayo de 2025. La documentación tiene en cuenta las restricciones del proyecto universitario, utilizando datos simulados y centrándose en las funcionalidades principales, con pasos detallados para cada tipo de prueba.

### Citas Clave

-   [Framework Robusto de Pruebas para Python](https://docs.pytest.org/en/stable/)
-   [Biblioteca de Mocking para Python](https://docs.python.org/3/library/unittest.mock.html)
-   [Biblioteca de Solicitudes HTTP para Python](https://requests.readthedocs.io/en/latest/)
-   [Selenium WebDriver](https://www.selenium.dev/documentation/)
-   [Escáner de Seguridad Bandit para Python](https://bandit.readthedocs.io/en/latest/)
-   [Herramienta de Seguridad OWASP ZAP](https://www.zap.org.uk/)
-   [Facebook Business SDK for Python](https://github.com/facebook/facebook-python-business-sdk)
-   [Twitter Ads API SDK for Python](https://github.com/xdevplatform/twitter-python-ads-sdk)
-   [Google Ads API Client Library for Python](https://github.com/googleads/google-ads-python)
-   [Página PyPI para python-tiktok](https://pypi.org/project/python-tiktok/)
-   [Página GitHub para davidteather/TikTok-Api](https://github.com/davidteather/TikTok-Api)
-   [Página GitHub para rbnali/easy-snapchat-api](https://github.com/rbnali/easy-snapchat-api)
-   [Sitio web oficial de Magneto365](https://www.magneto365.com/)
