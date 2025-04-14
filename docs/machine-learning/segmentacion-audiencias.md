# Segmentación de Audiencias

Este documento describe los algoritmos y técnicas utilizados en AdFlux para segmentar audiencias de candidatos potenciales para campañas publicitarias de reclutamiento.

## Introducción

La segmentación de audiencias es un componente crítico de AdFlux que permite dirigir anuncios de trabajo a los candidatos más relevantes. Utilizando técnicas de clustering y aprendizaje no supervisado, AdFlux identifica grupos de candidatos con características similares, permitiendo campañas más efectivas y personalizadas.

## Arquitectura de Segmentación

![Arquitectura de Segmentación](./diagramas/arquitectura-segmentacion.png)

El sistema de segmentación de audiencias consta de los siguientes componentes:

1. **Preprocesamiento de Datos**: Limpieza y transformación de perfiles de candidatos.
2. **Extracción de Características**: Conversión de datos de candidatos en vectores numéricos.
3. **Algoritmos de Clustering**: Agrupación de candidatos en segmentos.
4. **Evaluación de Clusters**: Medición de la calidad de los segmentos.
5. **Interpretación de Segmentos**: Asignación de etiquetas significativas a los segmentos.
6. **Integración con Plataformas**: Conversión de segmentos en audiencias para plataformas publicitarias.

## Preprocesamiento de Datos

Antes de aplicar algoritmos de clustering, los datos de los candidatos pasan por varias etapas de preprocesamiento:

```python
def preprocess_candidate_data(candidates):
    """
    Preprocesa los datos de candidatos para clustering.
    
    Args:
        candidates: Lista de perfiles de candidatos
        
    Returns:
        DataFrame con datos preprocesados
    """
    # Convertir a DataFrame
    df = pd.DataFrame(candidates)
    
    # Manejar valores faltantes
    df['experience_years'].fillna(0, inplace=True)
    df['education_level'].fillna('unknown', inplace=True)
    
    # Normalizar campos numéricos
    scaler = StandardScaler()
    numeric_cols = ['experience_years', 'age']
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    
    # Codificar variables categóricas
    categorical_cols = ['education_level', 'industry', 'job_title']
    for col in categorical_cols:
        df = pd.concat([df, pd.get_dummies(df[col], prefix=col)], axis=1)
        df.drop(col, axis=1, inplace=True)
    
    # Procesar habilidades (lista de strings)
    vectorizer = TfidfVectorizer(max_features=100)
    skills_matrix = vectorizer.fit_transform(df['skills'].apply(lambda x: ' '.join(x)))
    skills_df = pd.DataFrame(skills_matrix.toarray(), 
                            columns=[f'skill_{i}' for i in range(skills_matrix.shape[1])])
    
    # Combinar todo
    df = pd.concat([df.drop('skills', axis=1), skills_df], axis=1)
    
    return df
```

## Extracción de Características

La extracción de características convierte los perfiles de candidatos en vectores numéricos que pueden ser utilizados por algoritmos de ML:

### Características Principales

1. **Demográficas**: Edad, género, ubicación.
2. **Educación**: Nivel educativo, campo de estudio, instituciones.
3. **Experiencia**: Años de experiencia, industrias, roles.
4. **Habilidades**: Habilidades técnicas y blandas.
5. **Comportamiento**: Interacciones previas con anuncios, aplicaciones a trabajos.

### Reducción de Dimensionalidad

Para mejorar el rendimiento y reducir el ruido, aplicamos técnicas de reducción de dimensionalidad:

```python
def reduce_dimensions(features, n_components=50):
    """
    Reduce la dimensionalidad de las características.
    
    Args:
        features: Matriz de características
        n_components: Número de componentes a mantener
        
    Returns:
        Matriz de características reducida
    """
    # Aplicar PCA
    pca = PCA(n_components=n_components)
    reduced_features = pca.fit_transform(features)
    
    # Información sobre varianza explicada
    explained_variance = sum(pca.explained_variance_ratio_)
    logger.info(f"Varianza explicada con {n_components} componentes: {explained_variance:.2f}")
    
    return reduced_features, pca
```

## Algoritmos de Clustering

AdFlux implementa varios algoritmos de clustering para diferentes escenarios:

### K-means Clustering

El algoritmo principal utilizado para segmentación de candidatos es K-means, que agrupa candidatos en un número predefinido de clusters:

```python
def kmeans_clustering(features, n_clusters=5):
    """
    Aplica K-means clustering a las características de candidatos.
    
    Args:
        features: Matriz de características
        n_clusters: Número de clusters a crear
        
    Returns:
        Modelo K-means entrenado y etiquetas de cluster
    """
    # Determinar número óptimo de clusters si no se especifica
    if n_clusters is None:
        n_clusters = determine_optimal_clusters(features)
    
    # Aplicar K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(features)
    
    return kmeans, cluster_labels
```

### Determinación del Número Óptimo de Clusters

Para determinar automáticamente el número óptimo de clusters, utilizamos el método del codo y el coeficiente de silueta:

```python
def determine_optimal_clusters(features, max_clusters=20):
    """
    Determina el número óptimo de clusters usando el método del codo y silueta.
    
    Args:
        features: Matriz de características
        max_clusters: Número máximo de clusters a considerar
        
    Returns:
        Número óptimo de clusters
    """
    # Calcular inercia (método del codo)
    inertias = []
    silhouette_scores = []
    
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(features)
        inertias.append(kmeans.inertia_)
        
        # Calcular coeficiente de silueta
        labels = kmeans.labels_
        silhouette_scores.append(silhouette_score(features, labels))
    
    # Encontrar punto de inflexión (método del codo)
    kl = KneeLocator(range(2, max_clusters + 1), inertias, curve='convex', direction='decreasing')
    elbow_k = kl.elbow
    
    # Encontrar máximo coeficiente de silueta
    silhouette_k = np.argmax(silhouette_scores) + 2
    
    # Promediar ambos métodos
    optimal_k = int((elbow_k + silhouette_k) / 2)
    
    logger.info(f"Número óptimo de clusters: {optimal_k} (codo: {elbow_k}, silueta: {silhouette_k})")
    
    return optimal_k
```

### Clustering Jerárquico

Para casos que requieren una estructura jerárquica de segmentos:

```python
def hierarchical_clustering(features, n_clusters=None, distance_threshold=None):
    """
    Aplica clustering jerárquico a las características de candidatos.
    
    Args:
        features: Matriz de características
        n_clusters: Número de clusters a crear
        distance_threshold: Umbral de distancia para cortar el dendrograma
        
    Returns:
        Modelo de clustering jerárquico y etiquetas de cluster
    """
    # Configurar parámetros
    params = {}
    if n_clusters is not None:
        params['n_clusters'] = n_clusters
    if distance_threshold is not None:
        params['distance_threshold'] = distance_threshold
    
    # Aplicar clustering jerárquico
    hierarchical = AgglomerativeClustering(linkage='ward', **params)
    cluster_labels = hierarchical.fit_predict(features)
    
    return hierarchical, cluster_labels
```

### DBSCAN para Detección de Outliers

Para identificar candidatos atípicos que podrían requerir tratamiento especial:

```python
def dbscan_clustering(features, eps=0.5, min_samples=5):
    """
    Aplica DBSCAN para clustering y detección de outliers.
    
    Args:
        features: Matriz de características
        eps: Distancia máxima entre dos muestras para considerarlas vecinas
        min_samples: Número mínimo de muestras en un vecindario para un punto central
        
    Returns:
        Modelo DBSCAN y etiquetas de cluster (-1 para outliers)
    """
    # Aplicar DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = dbscan.fit_predict(features)
    
    # Contar outliers
    n_outliers = np.sum(cluster_labels == -1)
    logger.info(f"Número de outliers detectados: {n_outliers}")
    
    return dbscan, cluster_labels
```

## Evaluación de Clusters

Para evaluar la calidad de los clusters generados, utilizamos varias métricas:

```python
def evaluate_clusters(features, labels):
    """
    Evalúa la calidad de los clusters.
    
    Args:
        features: Matriz de características
        labels: Etiquetas de cluster
        
    Returns:
        Diccionario con métricas de evaluación
    """
    # Filtrar outliers si existen
    if -1 in labels:
        mask = labels != -1
        features = features[mask]
        labels = labels[mask]
    
    # Calcular métricas
    metrics = {
        'silhouette_score': silhouette_score(features, labels),
        'calinski_harabasz_score': calinski_harabasz_score(features, labels),
        'davies_bouldin_score': davies_bouldin_score(features, labels)
    }
    
    # Interpretación
    logger.info(f"Silhouette Score: {metrics['silhouette_score']:.3f} (más cercano a 1 es mejor)")
    logger.info(f"Calinski-Harabasz Index: {metrics['calinski_harabasz_score']:.3f} (más alto es mejor)")
    logger.info(f"Davies-Bouldin Index: {metrics['davies_bouldin_score']:.3f} (más bajo es mejor)")
    
    return metrics
```

## Interpretación de Segmentos

Una vez creados los clusters, es importante asignarles etiquetas significativas:

```python
def interpret_clusters(features, labels, feature_names, n_top_features=10):
    """
    Interpreta los clusters identificando características distintivas.
    
    Args:
        features: Matriz de características
        labels: Etiquetas de cluster
        feature_names: Nombres de las características
        n_top_features: Número de características principales a mostrar
        
    Returns:
        Diccionario con interpretaciones de clusters
    """
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    cluster_centers = np.zeros((n_clusters, features.shape[1]))
    
    # Calcular centros de cluster
    for i in range(n_clusters):
        cluster_centers[i] = features[labels == i].mean(axis=0)
    
    # Interpretar cada cluster
    interpretations = {}
    for i in range(n_clusters):
        # Encontrar características más distintivas
        center = cluster_centers[i]
        importance = np.abs(center - np.mean(cluster_centers, axis=0))
        top_indices = importance.argsort()[-n_top_features:][::-1]
        
        # Crear interpretación
        cluster_size = np.sum(labels == i)
        cluster_percentage = 100 * cluster_size / len(labels)
        
        top_features = []
        for idx in top_indices:
            feature_name = feature_names[idx]
            feature_value = center[idx]
            direction = "alto" if feature_value > 0 else "bajo"
            top_features.append(f"{feature_name} ({direction})")
        
        interpretations[f"Cluster {i}"] = {
            'size': cluster_size,
            'percentage': cluster_percentage,
            'top_features': top_features
        }
    
    return interpretations
```

## Integración con Plataformas Publicitarias

Los segmentos generados se convierten en audiencias para plataformas publicitarias:

### Meta (Facebook/Instagram)

```python
def create_meta_custom_audience(cluster_id, candidate_ids, account_id, audience_name=None):
    """
    Crea una audiencia personalizada en Meta basada en un cluster.
    
    Args:
        cluster_id: ID del cluster
        candidate_ids: IDs de candidatos en el cluster
        account_id: ID de la cuenta publicitaria de Meta
        audience_name: Nombre de la audiencia (opcional)
        
    Returns:
        ID de la audiencia creada
    """
    # Obtener emails de los candidatos
    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    emails = [c.email for c in candidates if c.email]
    
    # Generar nombre de audiencia si no se proporciona
    if audience_name is None:
        audience_name = f"AdFlux Cluster {cluster_id} - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Crear audiencia en Meta
    client = MetaApiClient()
    response = client.post(
        f"act_{account_id}/customaudiences",
        data={
            "name": audience_name,
            "subtype": "CUSTOM",
            "description": f"Candidatos del cluster {cluster_id} generado por AdFlux",
            "customer_file_source": "USER_PROVIDED_ONLY"
        }
    )
    
    audience_id = response['id']
    
    # Añadir usuarios a la audiencia
    if emails:
        # Hashear emails para privacidad
        hashed_emails = [hashlib.sha256(email.lower().encode()).hexdigest() for email in emails]
        
        client.post(
            f"{audience_id}/users",
            data={
                "payload": {
                    "schema": ["EMAIL"],
                    "data": [[email] for email in hashed_emails]
                }
            }
        )
    
    return audience_id
```

### Google Ads

```python
def create_google_customer_match_audience(cluster_id, candidate_ids, customer_id, audience_name=None):
    """
    Crea una audiencia de Customer Match en Google Ads basada en un cluster.
    
    Args:
        cluster_id: ID del cluster
        candidate_ids: IDs de candidatos en el cluster
        customer_id: ID del cliente de Google Ads
        audience_name: Nombre de la audiencia (opcional)
        
    Returns:
        ID de la audiencia creada
    """
    # Obtener emails de los candidatos
    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    emails = [c.email for c in candidates if c.email]
    
    # Generar nombre de audiencia si no se proporciona
    if audience_name is None:
        audience_name = f"AdFlux Cluster {cluster_id} - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Crear cliente de Google Ads
    client = GoogleAdsApiClient()
    
    # Crear audiencia
    user_list_service = client.get_service("UserListService")
    user_list_operation = client.get_type("UserListOperation")
    user_list = user_list_operation.create
    
    user_list.name = audience_name
    user_list.description = f"Candidatos del cluster {cluster_id} generado por AdFlux"
    user_list.crm_based_user_list.upload_key_type = client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
    
    # Crear la audiencia
    response = user_list_service.mutate_user_lists(
        customer_id=customer_id,
        operations=[user_list_operation]
    )
    
    user_list_id = response.results[0].resource_name
    
    # Añadir usuarios a la audiencia
    if emails:
        offline_user_data_job_service = client.get_service("OfflineUserDataJobService")
        
        # Crear trabajo de carga de datos
        create_job_response = offline_user_data_job_service.create_offline_user_data_job(
            customer_id=customer_id,
            job={"type_": client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST,
                 "customer_match_user_list_metadata": {"user_list": user_list_id}}
        )
        
        job_resource_name = create_job_response.resource_name
        
        # Preparar datos de usuario
        user_data_operations = []
        for email in emails:
            user_data_operation = client.get_type("OfflineUserDataJobOperation")
            user_data = user_data_operation.create
            
            user_identifier = client.get_type("UserIdentifier")
            user_identifier.hashed_email = hashlib.sha256(email.lower().encode()).hexdigest()
            
            user_data.user_identifiers.append(user_identifier)
            user_data_operations.append(user_data_operation)
        
        # Añadir datos de usuario
        offline_user_data_job_service.add_offline_user_data_job_operations(
            resource_name=job_resource_name,
            operations=user_data_operations
        )
        
        # Ejecutar trabajo
        offline_user_data_job_service.run_offline_user_data_job(resource_name=job_resource_name)
    
    return user_list_id
```

## Flujo de Trabajo Completo

El flujo de trabajo completo para la segmentación de audiencias es:

```python
def segment_candidates(job_opening_id, n_clusters=None):
    """
    Segmenta candidatos para una oferta de trabajo.
    
    Args:
        job_opening_id: ID de la oferta de trabajo
        n_clusters: Número de clusters a crear (opcional)
        
    Returns:
        Diccionario con información de segmentación
    """
    # Obtener oferta de trabajo
    job_opening = JobOpening.query.get(job_opening_id)
    if not job_opening:
        raise ValueError(f"Oferta de trabajo con ID {job_opening_id} no encontrada")
    
    # Obtener candidatos relevantes
    candidates = get_relevant_candidates(job_opening)
    if len(candidates) < 10:
        logger.warning(f"Pocos candidatos ({len(candidates)}) para segmentación efectiva")
        return {'error': 'Insuficientes candidatos para segmentación'}
    
    # Preprocesar datos
    preprocessed_data = preprocess_candidate_data(candidates)
    
    # Extraer características
    features = preprocessed_data.values
    feature_names = preprocessed_data.columns.tolist()
    
    # Reducir dimensionalidad
    reduced_features, pca = reduce_dimensions(features)
    
    # Aplicar clustering
    kmeans, labels = kmeans_clustering(reduced_features, n_clusters)
    
    # Evaluar clusters
    metrics = evaluate_clusters(reduced_features, labels)
    
    # Interpretar clusters
    interpretations = interpret_clusters(reduced_features, labels, feature_names)
    
    # Asignar candidatos a clusters
    candidate_clusters = {}
    for i, candidate in enumerate(candidates):
        cluster_id = int(labels[i])
        if cluster_id not in candidate_clusters:
            candidate_clusters[cluster_id] = []
        candidate_clusters[cluster_id].append(candidate['id'])
    
    # Guardar resultados
    segmentation = Segmentation(
        job_opening_id=job_opening_id,
        algorithm='kmeans',
        n_clusters=len(set(labels)),
        metrics=metrics,
        interpretations=interpretations,
        created_at=datetime.utcnow()
    )
    db.session.add(segmentation)
    db.session.commit()
    
    # Crear segmentos
    segments = []
    for cluster_id, candidate_ids in candidate_clusters.items():
        segment = Segment(
            segmentation_id=segmentation.id,
            cluster_id=cluster_id,
            name=f"Cluster {cluster_id}",
            description=get_cluster_description(interpretations, cluster_id),
            size=len(candidate_ids),
            candidate_ids=candidate_ids,
            created_at=datetime.utcnow()
        )
        db.session.add(segment)
        segments.append(segment)
    
    db.session.commit()
    
    return {
        'segmentation_id': segmentation.id,
        'n_clusters': len(segments),
        'metrics': metrics,
        'segments': [{'id': s.id, 'cluster_id': s.cluster_id, 'name': s.name, 'size': s.size} for s in segments]
    }
```

## Mejores Prácticas

Para obtener los mejores resultados con la segmentación de audiencias:

1. **Datos de Calidad**: Asegúrate de tener perfiles de candidatos completos y actualizados.
2. **Tamaño de Muestra**: Utiliza al menos 100 candidatos para una segmentación efectiva.
3. **Características Relevantes**: Incluye características relevantes para el puesto específico.
4. **Evaluación Regular**: Evalúa y ajusta los segmentos periódicamente basándote en el rendimiento de las campañas.
5. **Combinación con Reglas Manuales**: Complementa la segmentación automática con reglas manuales basadas en conocimiento del dominio.

## Limitaciones y Consideraciones

- **Calidad de Datos**: La segmentación es tan buena como los datos de entrada.
- **Interpretabilidad**: Los clusters pueden ser difíciles de interpretar en espacios de alta dimensionalidad.
- **Estabilidad**: Los resultados pueden variar con diferentes inicializaciones aleatorias.
- **Escalabilidad**: K-means puede tener problemas con conjuntos de datos muy grandes.
- **Privacidad**: Asegúrate de cumplir con regulaciones de privacidad al utilizar datos de candidatos.

## Recursos Adicionales

- [Documentación de scikit-learn sobre clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [Guía de Meta para Custom Audiences](https://developers.facebook.com/docs/marketing-api/audiences/guides/custom-audiences/)
- [Guía de Google Ads para Customer Match](https://developers.google.com/google-ads/api/docs/remarketing/audience-types/customer-match)
