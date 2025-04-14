# Machine Learning en AdFlux

Esta sección contiene documentación detallada sobre los componentes de Machine Learning implementados en AdFlux para optimizar campañas publicitarias y mejorar la segmentación de audiencias.

## Contenido

- [Visión General](./vision-general.md): Descripción general de la arquitectura de ML en AdFlux.
- [Segmentación de Audiencias](./segmentacion-audiencias.md): Algoritmos para segmentar candidatos.
- [Optimización de Contenido](./optimizacion-contenido.md): Generación y optimización de contenido para anuncios.
- [Predicción de Rendimiento](./prediccion-rendimiento.md): Modelos para predecir el rendimiento de campañas.
- [Entrenamiento de Modelos](./entrenamiento-modelos.md): Guía para entrenar y actualizar modelos.
- [Evaluación de Modelos](./evaluacion-modelos.md): Métricas y métodos para evaluar modelos.
- [Integración con Gemini AI](./integracion-gemini.md): Detalles sobre la integración con Gemini AI.
- [Simulación de Datos](./simulacion-datos.md): Generación de datos sintéticos para pruebas.

## Introducción

AdFlux utiliza técnicas avanzadas de Machine Learning para mejorar la eficacia de las campañas publicitarias de reclutamiento. Los componentes de ML están diseñados para:

1. **Segmentar audiencias**: Identificar grupos de candidatos potenciales con características similares para dirigir anuncios de manera más efectiva.
2. **Optimizar contenido**: Generar y adaptar contenido creativo para diferentes plataformas y audiencias.
3. **Predecir rendimiento**: Estimar el rendimiento de campañas antes de su lanzamiento y durante su ejecución.
4. **Recomendar mejoras**: Sugerir cambios en la configuración de campañas para mejorar su rendimiento.

## Arquitectura de ML

La arquitectura de ML en AdFlux sigue un enfoque modular:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Preprocesador  │────▶│     Modelos     │────▶│  Postprocesador │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                       │
        │                       │                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Fuentes de     │     │  Entrenamiento  │     │  Servicios de   │
│     Datos       │     │                 │     │   Aplicación    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Componentes Principales

1. **Preprocesador**: Limpia, transforma y normaliza los datos antes de alimentarlos a los modelos.
2. **Modelos**: Implementaciones de algoritmos de ML como K-means, Random Forest, y redes neuronales.
3. **Postprocesador**: Transforma las salidas de los modelos en formatos utilizables por la aplicación.
4. **Fuentes de Datos**: Datos históricos de campañas, perfiles de candidatos, y métricas de rendimiento.
5. **Entrenamiento**: Pipelines para entrenar y actualizar modelos periódicamente.
6. **Servicios de Aplicación**: Interfaces para que otros componentes de AdFlux utilicen los modelos de ML.

## Modelos Implementados

AdFlux implementa varios modelos de ML para diferentes propósitos:

### Segmentación de Candidatos

- **K-means Clustering**: Agrupa candidatos en segmentos basados en características como habilidades, experiencia, ubicación y educación.
- **Hierarchical Clustering**: Crea una jerarquía de segmentos para campañas con múltiples niveles de segmentación.

### Optimización de Contenido

- **Modelos de Lenguaje**: Integración con Gemini AI para generar y optimizar contenido de anuncios.
- **Análisis de Sentimiento**: Evalúa el tono y sentimiento del contenido generado.

### Predicción de Rendimiento

- **Regresión**: Predice métricas como CTR, CPC y tasa de conversión basándose en configuraciones de campaña.
- **Series Temporales**: Analiza tendencias y patrones en el rendimiento de campañas a lo largo del tiempo.

## Flujo de Trabajo Típico

1. **Recopilación de Datos**: Obtención de datos históricos de campañas y perfiles de candidatos.
2. **Preprocesamiento**: Limpieza y transformación de datos para su uso en modelos.
3. **Entrenamiento**: Entrenamiento de modelos con datos históricos.
4. **Inferencia**: Uso de modelos entrenados para hacer predicciones o recomendaciones.
5. **Evaluación**: Medición del rendimiento de los modelos y ajuste según sea necesario.
6. **Despliegue**: Integración de modelos en el flujo de trabajo de la aplicación.

## Tecnologías Utilizadas

AdFlux utiliza las siguientes tecnologías para sus componentes de ML:

- **Scikit-learn**: Para algoritmos clásicos de ML como clustering y regresión.
- **TensorFlow/Keras**: Para modelos de deep learning cuando es necesario.
- **Pandas**: Para manipulación y análisis de datos.
- **NumPy**: Para operaciones numéricas eficientes.
- **Gemini AI API**: Para generación de contenido y procesamiento de lenguaje natural.
- **MLflow**: Para seguimiento de experimentos y gestión de modelos.
- **Celery**: Para ejecutar tareas de entrenamiento e inferencia en segundo plano.

## Próximos Pasos

Para comenzar a utilizar los componentes de ML de AdFlux, consulta:

1. [Segmentación de Audiencias](./segmentacion-audiencias.md): Para entender cómo se segmentan los candidatos.
2. [Optimización de Contenido](./optimizacion-contenido.md): Para aprender sobre la generación de contenido.
3. [Entrenamiento de Modelos](./entrenamiento-modelos.md): Para entrenar tus propios modelos.

## Recursos Adicionales

- [Documentación de scikit-learn](https://scikit-learn.org/stable/documentation.html)
- [Documentación de TensorFlow](https://www.tensorflow.org/api_docs)
- [Documentación de Gemini AI](https://ai.google.dev/docs)
- [Mejores prácticas de ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
