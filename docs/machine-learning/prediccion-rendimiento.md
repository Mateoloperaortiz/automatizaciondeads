# Predicción de Rendimiento de Campañas

Este documento describe los modelos y técnicas utilizados en AdFlux para predecir el rendimiento de campañas publicitarias de reclutamiento.

## Contenido

1. [Introducción](#introducción)
2. [Modelos de Predicción](#modelos-de-predicción)
3. [Características Utilizadas](#características-utilizadas)
4. [Entrenamiento de Modelos](#entrenamiento-de-modelos)
5. [Evaluación de Modelos](#evaluación-de-modelos)
6. [Implementación en Producción](#implementación-en-producción)
7. [Mejores Prácticas](#mejores-prácticas)

## Introducción

La predicción de rendimiento es un componente clave de AdFlux que permite estimar métricas importantes como CTR (Click-Through Rate), CPC (Cost Per Click), y tasa de conversión antes de lanzar una campaña. Esto ayuda a optimizar el presupuesto y mejorar la eficacia de las campañas publicitarias.

El sistema de predicción de rendimiento utiliza modelos de machine learning entrenados con datos históricos de campañas anteriores para hacer predicciones precisas sobre nuevas campañas.

## Modelos de Predicción

AdFlux implementa varios modelos de predicción para diferentes métricas y plataformas:

### Predicción de CTR

```python
class CTRPredictor:
    """Predictor de Click-Through Rate (CTR) para campañas publicitarias."""
    
    def __init__(self, platform):
        """
        Inicializa el predictor de CTR.
        
        Args:
            platform: Plataforma publicitaria (META, GOOGLE, TIKTOK, SNAPCHAT)
        """
        self.platform = platform
        self.model = None
        self.feature_names = None
        self.scaler = None
    
    def train(self, campaigns_data):
        """
        Entrena el modelo con datos históricos de campañas.
        
        Args:
            campaigns_data: DataFrame con datos de campañas
            
        Returns:
            Métricas de entrenamiento
        """
        # Preparar datos
        X, y, feature_names = self._prepare_data(campaigns_data)
        
        # Dividir en conjuntos de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar características
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelo
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        self.feature_names = feature_names
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test_scaled)
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
        
        return metrics
    
    def predict(self, campaign_data):
        """
        Predice el CTR para una campaña.
        
        Args:
            campaign_data: Diccionario con datos de la campaña
            
        Returns:
            CTR predicho
        """
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado")
        
        # Preparar datos
        X = self._prepare_prediction_data(campaign_data)
        
        # Escalar características
        X_scaled = self.scaler.transform(X)
        
        # Predecir
        ctr_pred = self.model.predict(X_scaled)[0]
        
        # Asegurar que el CTR esté en el rango [0, 1]
        ctr_pred = max(0, min(1, ctr_pred))
        
        return ctr_pred
    
    def _prepare_data(self, campaigns_data):
        """
        Prepara los datos para entrenamiento.
        
        Args:
            campaigns_data: DataFrame con datos de campañas
            
        Returns:
            Tupla (X, y, feature_names)
        """
        # Filtrar por plataforma
        data = campaigns_data[campaigns_data['platform'] == self.platform].copy()
        
        # Verificar datos suficientes
        if len(data) < 10:
            raise ValueError(f"Datos insuficientes para la plataforma {self.platform}")
        
        # Preparar características
        features = []
        
        # Características numéricas
        numeric_features = ['daily_budget', 'duration_days']
        
        # Características categóricas
        categorical_features = ['objective', 'job_category', 'employment_type']
        
        # Codificar variables categóricas
        for feature in categorical_features:
            dummies = pd.get_dummies(data[feature], prefix=feature)
            data = pd.concat([data, dummies], axis=1)
            features.extend(dummies.columns.tolist())
        
        # Añadir características numéricas
        features.extend(numeric_features)
        
        # Preparar X e y
        X = data[features].values
        y = data['ctr'].values
        
        return X, y, features
    
    def _prepare_prediction_data(self, campaign_data):
        """
        Prepara los datos para predicción.
        
        Args:
            campaign_data: Diccionario con datos de la campaña
            
        Returns:
            Array de características
        """
        # Crear DataFrame con una fila
        data = pd.DataFrame([campaign_data])
        
        # Preparar características
        X = np.zeros((1, len(self.feature_names)))
        
        # Características numéricas
        numeric_features = ['daily_budget', 'duration_days']
        for i, feature in enumerate(numeric_features):
            if feature in data.columns and feature in self.feature_names:
                idx = self.feature_names.index(feature)
                X[0, idx] = data[feature].values[0]
        
        # Características categóricas
        categorical_features = ['objective', 'job_category', 'employment_type']
        for feature in categorical_features:
            if feature in data.columns:
                value = data[feature].values[0]
                feature_col = f"{feature}_{value}"
                if feature_col in self.feature_names:
                    idx = self.feature_names.index(feature_col)
                    X[0, idx] = 1
        
        return X
```

### Predicción de Coste por Aplicación (CPA)

```python
class CPAPredictor:
    """Predictor de Cost Per Application (CPA) para campañas publicitarias."""
    
    def __init__(self, platform):
        """
        Inicializa el predictor de CPA.
        
        Args:
            platform: Plataforma publicitaria (META, GOOGLE, TIKTOK, SNAPCHAT)
        """
        self.platform = platform
        self.model = None
        self.feature_names = None
        self.scaler = None
    
    def train(self, campaigns_data):
        """
        Entrena el modelo con datos históricos de campañas.
        
        Args:
            campaigns_data: DataFrame con datos de campañas
            
        Returns:
            Métricas de entrenamiento
        """
        # Similar a CTRPredictor.train pero para CPA
        # ...
        
    def predict(self, campaign_data):
        """
        Predice el CPA para una campaña.
        
        Args:
            campaign_data: Diccionario con datos de la campaña
            
        Returns:
            CPA predicho
        """
        # Similar a CTRPredictor.predict pero para CPA
        # ...
```

## Características Utilizadas

Los modelos de predicción utilizan diversas características para hacer predicciones precisas:

### Características de la Campaña

- **Objetivo**: Objetivo de la campaña (awareness, consideration, conversion)
- **Presupuesto Diario**: Cantidad asignada por día
- **Duración**: Duración de la campaña en días
- **Plataforma**: Plataforma publicitaria (META, GOOGLE, TIKTOK, SNAPCHAT)
- **Formato**: Formato del anuncio (feed, story, search, etc.)

### Características de la Oferta de Trabajo

- **Categoría**: Categoría del puesto (IT, marketing, ventas, etc.)
- **Nivel de Experiencia**: Nivel requerido (junior, mid-level, senior)
- **Tipo de Empleo**: Tipo de contrato (tiempo completo, parcial, freelance)
- **Ubicación**: Ubicación geográfica
- **Rango Salarial**: Rango de salario ofrecido

### Características de Segmentación

- **Tamaño de Audiencia**: Tamaño estimado de la audiencia
- **Especificidad**: Qué tan específica es la segmentación
- **Demografía**: Características demográficas de la audiencia objetivo

### Características de Contenido

- **Longitud del Título**: Número de caracteres en el título
- **Longitud de la Descripción**: Número de caracteres en la descripción
- **Presencia de Palabras Clave**: Presencia de palabras clave relevantes
- **Llamada a la Acción**: Tipo de CTA utilizada

## Entrenamiento de Modelos

El proceso de entrenamiento de modelos incluye:

1. **Recopilación de Datos**: Obtención de datos históricos de campañas
2. **Preprocesamiento**: Limpieza y transformación de datos
3. **Ingeniería de Características**: Creación de características relevantes
4. **Selección de Modelo**: Elección del algoritmo adecuado
5. **Entrenamiento**: Ajuste de parámetros del modelo
6. **Validación**: Evaluación del rendimiento en datos no vistos
7. **Ajuste de Hiperparámetros**: Optimización de parámetros del modelo

```python
def train_prediction_models(platform=None):
    """
    Entrena modelos de predicción para una o todas las plataformas.
    
    Args:
        platform: Plataforma específica o None para todas
        
    Returns:
        Diccionario con modelos entrenados y métricas
    """
    # Cargar datos históricos
    campaigns_data = load_historical_campaigns_data()
    
    # Determinar plataformas a procesar
    platforms = [platform] if platform else ['META', 'GOOGLE', 'TIKTOK', 'SNAPCHAT']
    
    results = {}
    
    for platform in platforms:
        platform_data = campaigns_data[campaigns_data['platform'] == platform]
        
        if len(platform_data) < 10:
            logger.warning(f"Datos insuficientes para entrenar modelos de {platform}")
            continue
        
        # Entrenar modelo de CTR
        ctr_predictor = CTRPredictor(platform)
        ctr_metrics = ctr_predictor.train(platform_data)
        
        # Entrenar modelo de CPC
        cpc_predictor = CPCPredictor(platform)
        cpc_metrics = cpc_predictor.train(platform_data)
        
        # Entrenar modelo de CPA
        cpa_predictor = CPAPredictor(platform)
        cpa_metrics = cpa_predictor.train(platform_data)
        
        # Guardar modelos
        save_model(ctr_predictor, f"ctr_predictor_{platform.lower()}")
        save_model(cpc_predictor, f"cpc_predictor_{platform.lower()}")
        save_model(cpa_predictor, f"cpa_predictor_{platform.lower()}")
        
        # Registrar resultados
        results[platform] = {
            'ctr': {
                'model': ctr_predictor,
                'metrics': ctr_metrics
            },
            'cpc': {
                'model': cpc_predictor,
                'metrics': cpc_metrics
            },
            'cpa': {
                'model': cpa_predictor,
                'metrics': cpa_metrics
            }
        }
    
    return results
```

## Evaluación de Modelos

Los modelos se evalúan utilizando varias métricas:

- **MAE (Mean Absolute Error)**: Error absoluto medio
- **MSE (Mean Squared Error)**: Error cuadrático medio
- **R² (Coefficient of Determination)**: Coeficiente de determinación
- **RMSE (Root Mean Squared Error)**: Raíz del error cuadrático medio

```python
def evaluate_prediction_model(model, test_data):
    """
    Evalúa un modelo de predicción.
    
    Args:
        model: Modelo a evaluar
        test_data: Datos de prueba
        
    Returns:
        Diccionario con métricas de evaluación
    """
    # Preparar datos
    X_test, y_test = model._prepare_data(test_data)[0:2]
    X_test_scaled = model.scaler.transform(X_test)
    
    # Hacer predicciones
    y_pred = model.model.predict(X_test_scaled)
    
    # Calcular métricas
    metrics = {
        'mae': mean_absolute_error(y_test, y_pred),
        'mse': mean_squared_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'r2': r2_score(y_test, y_pred)
    }
    
    # Calcular métricas adicionales según el tipo de modelo
    if isinstance(model, CTRPredictor):
        # Para CTR, calcular AUC-ROC
        metrics['auc_roc'] = roc_auc_score(y_test > np.median(y_test), y_pred)
    
    return metrics
```

## Implementación en Producción

Los modelos entrenados se implementan en producción para hacer predicciones en tiempo real:

```python
def predict_campaign_performance(campaign_data):
    """
    Predice el rendimiento de una campaña.
    
    Args:
        campaign_data: Datos de la campaña
        
    Returns:
        Diccionario con predicciones
    """
    platform = campaign_data['platform']
    
    # Cargar modelos
    ctr_predictor = load_model(f"ctr_predictor_{platform.lower()}")
    cpc_predictor = load_model(f"cpc_predictor_{platform.lower()}")
    cpa_predictor = load_model(f"cpa_predictor_{platform.lower()}")
    
    # Hacer predicciones
    ctr = ctr_predictor.predict(campaign_data)
    cpc = cpc_predictor.predict(campaign_data)
    cpa = cpa_predictor.predict(campaign_data)
    
    # Calcular métricas adicionales
    daily_budget = campaign_data['daily_budget']
    duration_days = campaign_data['duration_days']
    total_budget = daily_budget * duration_days
    
    # Estimar impresiones
    estimated_impressions = (daily_budget / cpc) * 1000 if cpc > 0 else 0
    
    # Estimar clics
    estimated_clicks = estimated_impressions * ctr
    
    # Estimar aplicaciones
    estimated_applications = total_budget / cpa if cpa > 0 else 0
    
    return {
        'ctr': ctr,
        'cpc': cpc,
        'cpa': cpa,
        'estimated_impressions_daily': estimated_impressions,
        'estimated_clicks_daily': estimated_clicks,
        'estimated_applications_total': estimated_applications,
        'total_budget': total_budget
    }
```

## Mejores Prácticas

Para obtener los mejores resultados con la predicción de rendimiento:

1. **Datos Suficientes**: Asegúrate de tener suficientes datos históricos para entrenar modelos precisos.
2. **Actualización Regular**: Actualiza los modelos regularmente con nuevos datos para mantener su precisión.
3. **Validación Cruzada**: Utiliza validación cruzada para evaluar la robustez de los modelos.
4. **Monitoreo Continuo**: Monitorea el rendimiento de los modelos en producción y compara predicciones con resultados reales.
5. **Interpretabilidad**: Utiliza técnicas como SHAP o LIME para entender qué características influyen más en las predicciones.
6. **Calibración**: Calibra las predicciones para que reflejen probabilidades reales.
7. **Ensemble**: Considera utilizar ensambles de modelos para mejorar la precisión.
