# 🧠 Machine Learning

Este documento describe el módulo de Machine Learning de AdFlux, que se utiliza principalmente para la segmentación de candidatos mediante técnicas de clustering.

## 🎯 Objetivo

El objetivo principal del módulo de ML en AdFlux es agrupar a los candidatos en segmentos significativos basados en sus habilidades, experiencia, educación y otros atributos. Estos segmentos permiten:

1. **Dirigir campañas publicitarias** a grupos específicos de candidatos
2. **Recomendar candidatos** para ofertas de trabajo específicas
3. **Analizar tendencias** en el mercado laboral
4. **Optimizar el presupuesto publicitario** enfocándose en segmentos de alto valor

## 🧩 Componentes Principales

### 1. Preprocesamiento de Datos

El módulo `preprocessing.py` contiene funciones para preparar los datos de candidatos para el análisis:

```python
def create_preprocessor():
    """
    Crea un preprocesador para transformar datos de candidatos.
    
    Returns:
        ColumnTransformer: Preprocesador configurado para datos de candidatos.
    """
    # Transformadores numéricos
    numeric_features = ['years_experience', 'desired_salary']
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Transformadores categóricos
    categorical_features = ['education_level', 'location']
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Transformador de texto para habilidades
    text_features = ['skills_text']  # Campo concatenado de habilidades
    text_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='')),
        ('vectorizer', TfidfVectorizer(max_features=100))
    ])
    
    # Combinar todos los transformadores
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features),
            ('txt', text_transformer, text_features)
        ],
        remainder='drop'  # Ignorar otras columnas
    )
    
    return preprocessor
```

**Características clave del preprocesamiento:**

- **Datos numéricos**: Se imputan valores faltantes con la mediana y se escalan usando `StandardScaler`.
- **Datos categóricos**: Se imputan valores faltantes con "unknown" y se codifican usando `OneHotEncoder`.
- **Datos de texto (habilidades)**: Se vectorizan usando `TfidfVectorizer` para capturar la importancia de diferentes habilidades.

### 2. Modelo de Clustering

El módulo `models.py` contiene funciones para entrenar y aplicar el modelo de clustering:

```python
def train_segmentation_model(
    df: pd.DataFrame, 
    n_clusters: int = DEFAULT_N_CLUSTERS,
    model_path: str = DEFAULT_MODEL_PATH, 
    preprocessor_path: str = DEFAULT_PREPROCESSOR_PATH
) -> Tuple[KMeans, ColumnTransformer]:
    """
    Preprocesa datos de candidatos, entrena un modelo K-means y guarda ambos.
    
    Args:
        df: DataFrame con datos de candidatos.
        n_clusters: Número de segmentos a crear.
        model_path: Ruta para guardar el modelo entrenado.
        preprocessor_path: Ruta para guardar el preprocesador.

    Returns:
        Tupla con el modelo KMeans y el preprocesador.
    """
    # Implementación...
```

**Características clave del modelo:**

- **Algoritmo**: K-means para clustering no supervisado
- **Número de clusters**: Configurable, por defecto 5
- **Inicialización**: k-means++ para mejor convergencia
- **Persistencia**: El modelo entrenado se guarda en disco para uso futuro

### 3. Predicción y Asignación de Segmentos

El módulo `prediction.py` contiene funciones para asignar candidatos a segmentos:

```python
def assign_segments_to_candidates(
    candidates_df: pd.DataFrame,
    model_path: str = DEFAULT_MODEL_PATH,
    preprocessor_path: str = DEFAULT_PREPROCESSOR_PATH
) -> pd.DataFrame:
    """
    Asigna segmentos a candidatos usando un modelo entrenado.
    
    Args:
        candidates_df: DataFrame con datos de candidatos.
        model_path: Ruta del modelo K-means guardado.
        preprocessor_path: Ruta del preprocesador guardado.
        
    Returns:
        DataFrame con candidatos y sus segmentos asignados.
    """
    # Implementación...
```

### 4. Evaluación del Modelo

El módulo `evaluation.py` contiene funciones para evaluar la calidad del clustering:

```python
def evaluate_clustering(
    df: pd.DataFrame,
    labels: np.ndarray,
    preprocessor: ColumnTransformer
) -> Dict[str, float]:
    """
    Evalúa la calidad del clustering usando varias métricas.
    
    Args:
        df: DataFrame original con datos de candidatos.
        labels: Etiquetas de cluster asignadas.
        preprocessor: Preprocesador utilizado.
        
    Returns:
        Diccionario con métricas de evaluación.
    """
    # Implementación...
```

**Métricas de evaluación:**

- **Silhouette Score**: Mide qué tan similares son los objetos dentro de su propio cluster en comparación con otros clusters
- **Davies-Bouldin Index**: Mide la separación promedio entre clusters
- **Calinski-Harabasz Index**: Mide la relación entre la dispersión dentro del cluster y entre clusters

## 🔄 Flujo de Trabajo

### 1. Preparación de Datos

```python
def prepare_candidate_data(candidates):
    """
    Prepara datos de candidatos para el modelo de ML.
    
    Args:
        candidates: Lista de objetos Candidate.
        
    Returns:
        DataFrame con datos preparados.
    """
    # Convertir a DataFrame
    data = []
    for candidate in candidates:
        # Extraer datos relevantes
        candidate_data = {
            'candidate_id': candidate.candidate_id,
            'years_experience': candidate.years_experience,
            'education_level': candidate.education_level,
            'location': candidate.location,
            'desired_salary': candidate.desired_salary,
            'skills': candidate.skills
        }
        data.append(candidate_data)
    
    df = pd.DataFrame(data)
    
    # Procesar habilidades (convertir de JSON a texto)
    df['skills_text'] = df['skills'].apply(
        lambda x: ' '.join(x) if isinstance(x, list) else ''
    )
    
    return df
```

### 2. Entrenamiento del Modelo

```python
# Obtener datos de candidatos
candidates = Candidate.query.all()
candidates_df = prepare_candidate_data(candidates)

# Entrenar modelo
kmeans, preprocessor = train_segmentation_model(
    candidates_df, 
    n_clusters=5
)

# Evaluar modelo
evaluation_metrics = evaluate_clustering(
    candidates_df,
    kmeans.labels_,
    preprocessor
)
print(f"Silhouette Score: {evaluation_metrics['silhouette_score']:.3f}")
```

### 3. Asignación de Segmentos

```python
# Asignar segmentos a candidatos
candidates_df = assign_segments_to_candidates(candidates_df)

# Actualizar base de datos
for _, row in candidates_df.iterrows():
    candidate = Candidate.query.get(row['candidate_id'])
    if candidate:
        candidate.segment_id = int(row['segment'])
        
db.session.commit()
```

### 4. Uso en Campañas

```python
# Crear campaña dirigida a un segmento específico
campaign = Campaign(
    name="Campaña para Desarrolladores Senior",
    platform="meta",
    job_opening_id="JOB-0001",
    target_segment_ids=[2, 3]  # Segmentos objetivo
)
db.session.add(campaign)
db.session.commit()
```

## 📊 Interpretación de Segmentos

AdFlux incluye funcionalidades para interpretar y nombrar automáticamente los segmentos generados:

```python
def interpret_segments(
    df: pd.DataFrame,
    labels: np.ndarray,
    preprocessor: ColumnTransformer,
    n_features: int = 5
) -> Dict[int, Dict[str, Any]]:
    """
    Interpreta los segmentos generados por el clustering.
    
    Args:
        df: DataFrame original con datos de candidatos.
        labels: Etiquetas de cluster asignadas.
        preprocessor: Preprocesador utilizado.
        n_features: Número de características principales a mostrar.
        
    Returns:
        Diccionario con interpretaciones de cada segmento.
    """
    # Implementación...
```

**Ejemplo de interpretación:**

```
Segmento 0: "Desarrolladores Junior"
- Años de experiencia: 0-2
- Educación: Bachelor's
- Habilidades principales: HTML, CSS, JavaScript
- Salario deseado: 1.5M-2.5M COP

Segmento 1: "Desarrolladores Senior Full-Stack"
- Años de experiencia: 5-10
- Educación: Master's
- Habilidades principales: React, Node.js, Python, AWS
- Salario deseado: 6M-10M COP
```

## 🔄 Integración con Celery

El entrenamiento del modelo y la asignación de segmentos se ejecutan como tareas de Celery para no bloquear la aplicación principal:

```python
@celery.task
def train_segmentation_model_task():
    """Tarea Celery para entrenar el modelo de segmentación."""
    from ..models import Candidate
    from ..ml.models import train_segmentation_model
    from ..ml.utils import prepare_candidate_data
    
    # Obtener candidatos
    candidates = Candidate.query.all()
    if not candidates:
        return {"status": "error", "message": "No hay candidatos para entrenar el modelo"}
    
    # Preparar datos
    candidates_df = prepare_candidate_data(candidates)
    
    # Entrenar modelo
    try:
        kmeans, preprocessor = train_segmentation_model(candidates_df)
        return {
            "status": "success", 
            "message": f"Modelo entrenado con {len(candidates)} candidatos",
            "n_clusters": kmeans.n_clusters
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## 📈 Visualización de Segmentos

AdFlux incluye funcionalidades para visualizar los segmentos generados:

```python
def visualize_segments(
    df: pd.DataFrame,
    labels: np.ndarray,
    preprocessor: ColumnTransformer,
    output_path: str = None
) -> None:
    """
    Genera visualizaciones de los segmentos.
    
    Args:
        df: DataFrame original con datos de candidatos.
        labels: Etiquetas de cluster asignadas.
        preprocessor: Preprocesador utilizado.
        output_path: Ruta para guardar las visualizaciones.
    """
    # Implementación...
```

Las visualizaciones incluyen:

1. **Gráfico de dispersión PCA**: Reducción de dimensionalidad a 2D para visualizar clusters
2. **Gráfico de barras de características**: Muestra las características más importantes de cada segmento
3. **Distribución de candidatos**: Muestra la cantidad de candidatos en cada segmento

## 🛠️ Comandos CLI

AdFlux incluye comandos CLI para gestionar el módulo de ML:

```python
@click.command('train-model')
@click.option('--clusters', default=5, help='Número de clusters a crear')
@with_appcontext
def train_model_command(clusters):
    """Entrena el modelo de segmentación de candidatos."""
    # Implementación...
    
@click.command('assign-segments')
@with_appcontext
def assign_segments_command():
    """Asigna segmentos a todos los candidatos."""
    # Implementación...
    
@click.command('evaluate-model')
@with_appcontext
def evaluate_model_command():
    """Evalúa el modelo de segmentación actual."""
    # Implementación...
```

## 🔍 Consideraciones Técnicas

### Escalabilidad

- Para conjuntos de datos grandes, se implementa procesamiento por lotes
- Se utilizan algoritmos eficientes como MiniBatchKMeans cuando es necesario

### Manejo de Datos Faltantes

- Estrategias de imputación configurables (media, mediana, moda, valor constante)
- Monitoreo de la calidad de los datos

### Actualización del Modelo

- Reentrenamiento periódico programado
- Detección de cambios significativos en los datos

### Almacenamiento de Modelos

- Los modelos se guardan en formato pickle
- Se mantiene un historial de versiones de modelos

## 🔮 Mejoras Futuras

1. **Algoritmos Avanzados**:
   - Implementar DBSCAN para detectar clusters de forma irregular
   - Explorar técnicas de clustering jerárquico

2. **Características Adicionales**:
   - Incorporar análisis de texto más avanzado para habilidades
   - Incluir datos de comportamiento de candidatos

3. **Optimización Automática**:
   - Implementar búsqueda de hiperparámetros
   - Selección automática del número óptimo de clusters

4. **Explicabilidad**:
   - Mejorar la interpretación de segmentos
   - Generar descripciones en lenguaje natural

5. **Recomendaciones**:
   - Desarrollar un sistema de recomendación de trabajos basado en segmentos
   - Implementar matching entre segmentos de candidatos y requisitos de trabajos
