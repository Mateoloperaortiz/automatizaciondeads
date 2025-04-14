# AdFlux Tests

Este directorio contiene pruebas para el proyecto AdFlux, organizadas en diferentes categorías para facilitar su ejecución y mantenimiento.

## Estructura de Pruebas

```
tests/
├── unit/               # Pruebas unitarias
├── integration/        # Pruebas de integración
├── functional/         # Pruebas funcionales
├── security/           # Pruebas de seguridad
├── performance/        # Pruebas de rendimiento
├── conftest.py         # Configuración y fixtures para pytest
└── README.md           # Este archivo
```

## Tipos de Pruebas

### Pruebas Unitarias

Las pruebas unitarias verifican componentes individuales de la aplicación de forma aislada. Se encuentran en el directorio `unit/` y están marcadas con `@pytest.mark.unit`.

### Pruebas de Integración

Las pruebas de integración verifican la interacción entre diferentes componentes de la aplicación. Se encuentran en el directorio `integration/` y están marcadas con `@pytest.mark.integration`.

### Pruebas Funcionales

Las pruebas funcionales verifican flujos completos de la aplicación, simulando la interacción del usuario. Se encuentran en el directorio `functional/` y están marcadas con `@pytest.mark.functional`.

### Pruebas de Seguridad

Las pruebas de seguridad verifican las características de seguridad implementadas en la aplicación. Se encuentran en el directorio `security/` y están marcadas con `@pytest.mark.security`.

### Pruebas de Rendimiento

Las pruebas de rendimiento verifican el rendimiento y la escalabilidad de la aplicación bajo diferentes condiciones de carga. Se encuentran en el directorio `performance/` y están marcadas con `@pytest.mark.performance`.

## Ejecución de Pruebas

### Ejecutar todas las pruebas

```bash
python -m pytest
```

### Ejecutar un tipo específico de pruebas

```bash
# Pruebas unitarias
python -m pytest -m unit

# Pruebas de integración
python -m pytest -m integration

# Pruebas funcionales
python -m pytest -m functional

# Pruebas de seguridad
python -m pytest -m security

# Pruebas de rendimiento
python -m pytest -m performance
```

### Ejecutar pruebas con cobertura

```bash
python -m pytest --cov=adflux --cov-report=term --cov-report=html
```

### Ejecutar pruebas con script personalizado

```bash
python scripts/run_tests.py --unit      # Pruebas unitarias
python scripts/run_tests.py --integration  # Pruebas de integración
python scripts/run_tests.py --functional   # Pruebas funcionales
python scripts/run_tests.py --security     # Pruebas de seguridad
python scripts/run_tests.py --performance  # Pruebas de rendimiento
python scripts/run_tests.py --all          # Todas las pruebas
python scripts/run_tests.py --coverage     # Con informe de cobertura
```

## Fixtures

Los fixtures para las pruebas se definen en `conftest.py`. Estos fixtures proporcionan objetos y configuraciones comunes para las pruebas, como:

- `app`: Instancia de la aplicación Flask
- `db`: Sesión de base de datos
- `client`: Cliente de prueba Flask
- `admin_user`: Usuario administrador
- `regular_user`: Usuario regular
- `admin_token`: Token JWT para usuario administrador
- `user_token`: Token JWT para usuario regular
- `auth_client`: Cliente autenticado como administrador
- `user_auth_client`: Cliente autenticado como usuario regular
- `sample_campaign`: Campaña de ejemplo
- `mock_redis`: Mock de Redis
- `mock_celery`: Mock de Celery

## Buenas Prácticas

1. **Organización**: Mantener las pruebas organizadas por tipo y funcionalidad.
2. **Aislamiento**: Cada prueba debe ser independiente y no depender del estado de otras pruebas.
3. **Fixtures**: Utilizar fixtures para configurar el entorno de prueba y evitar duplicación de código.
4. **Mocks**: Utilizar mocks para simular servicios externos y evitar llamadas reales a APIs.
5. **Cobertura**: Mantener una alta cobertura de código, especialmente en componentes críticos.
6. **Documentación**: Documentar el propósito de cada prueba y los escenarios que cubre.
7. **Mantenimiento**: Actualizar las pruebas cuando cambie la funcionalidad de la aplicación.

## Requisitos para Ejecutar las Pruebas

- Python 3.8+
- pytest
- pytest-cov
- pytest-flask
- pytest-mock
- responses (para simular respuestas HTTP)
- Todas las dependencias de AdFlux

## Configuración de CI/CD

Las pruebas se ejecutan automáticamente en cada commit y pull request a través de GitHub Actions. La configuración se encuentra en `.github/workflows/tests.yml`.

## Solución de Problemas

Si las pruebas fallan, verificar:

1. Que todas las dependencias estén instaladas
2. Que la base de datos de prueba esté configurada correctamente
3. Que los mocks estén configurados correctamente
4. Que los fixtures estén funcionando correctamente
5. Que las pruebas sean independientes entre sí
