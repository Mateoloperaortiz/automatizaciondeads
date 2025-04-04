# Lógica del modelo de Machine Learning (agrupación K-means)

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
import joblib
import os
from typing import List, Optional, Tuple

# Asumiendo que db y el modelo Candidate pueden ser importados cuando se ejecuta dentro del contexto de la aplicación
# Si se ejecuta de forma independiente, estas importaciones fallarían a menos que se configuren de manera diferente.
# from .extensions import db 
# from .models import Candidate

DEFAULT_MODEL_DIR = 'instance/ml_models' # Guardar modelos en la carpeta instance
DEFAULT_MODEL_PATH = os.path.join(DEFAULT_MODEL_DIR, 'kmeans_model.joblib')
DEFAULT_PREPROCESSOR_PATH = os.path.join(DEFAULT_MODEL_DIR, 'kmeans_preprocessor.joblib')
DEFAULT_N_CLUSTERS = 5


def load_candidate_data(candidates: Optional[List] = None) -> pd.DataFrame:
    """
    Carga datos de candidatos en un DataFrame de pandas.
    Si se proporciona la lista de candidatos (instancias del modelo SQLAlchemy), la utiliza.
    De lo contrario, intenta consultar a todos los candidatos (requiere contexto de aplicación).
    """
    if candidates:
        # Convertir lista de objetos Candidate a lista de diccionarios
        data = [{
            'candidate_id': c.candidate_id,
            'location': c.location,
            'years_experience': c.years_experience,
            'education_level': c.education_level,
            # Asegurar que skills sea una lista, por defecto lista vacía si es None
            'skills': c.skills if isinstance(c.skills, list) else [], 
            'primary_skill': c.primary_skill,
            'desired_salary': c.desired_salary
        } for c in candidates]
        df = pd.DataFrame(data)
    else:
        # Marcador de posición: En un escenario real, consultar la base de datos
        # Esto requiere contexto de aplicación si se usa Flask-SQLAlchemy directamente
        # from .models import Candidate
        # all_candidates = Candidate.query.all()
        # data = [...] # Convertir all_candidates como arriba
        # df = pd.DataFrame(data)
        # Por ahora, devolver un DataFrame vacío si no se pasan candidatos
        print("Advertencia: No se proporcionaron datos de candidatos y la consulta a la BD no está implementada aquí. Devolviendo DataFrame vacío.")
        return pd.DataFrame(columns=[
            'candidate_id', 'location', 'years_experience', 'education_level', 
            'skills', 'primary_skill', 'desired_salary'
        ])

    if 'candidate_id' in df.columns:
        df.set_index('candidate_id', inplace=True)
        
    # Unir la lista de skills en una sola cadena para TfidfVectorizer
    df['skills_text'] = df['skills'].apply(lambda x: ' '.join(x) if x else '')
    
    return df

def create_preprocessor() -> ColumnTransformer:
    """Crea el ColumnTransformer para preprocesar datos de candidatos."""
    
    # Definir transformadores para diferentes tipos de columnas
    numerical_features = ['years_experience', 'desired_salary']
    categorical_features = ['location', 'education_level', 'primary_skill']
    text_features = 'skills_text' # Nombre de columna único después de la transformación
    
    # Pipeline para características numéricas: Imputar faltantes con la mediana, luego escalar
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Pipeline para características categóricas: Imputar faltantes con 'Desconocido', luego OneHotEncode
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore')) # Ignorar categorías no vistas durante el ajuste
    ])
    
    # Pipeline para características de texto (skills): Vectorizador TF-IDF
    # No se necesita imputación ya que asignamos por defecto una cadena vacía a las skills
    text_transformer = TfidfVectorizer(stop_words='english', max_features=100) # Limitar características
    
    # Crear el ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features),
            ('text', text_transformer, text_features)
        ],
        remainder='drop' # Eliminar columnas no especificadas (como la lista original 'skills')
    )
    
    return preprocessor

def train_segmentation_model(
    df: pd.DataFrame, 
    n_clusters: int = DEFAULT_N_CLUSTERS,
    model_path: str = DEFAULT_MODEL_PATH, 
    preprocessor_path: str = DEFAULT_PREPROCESSOR_PATH
) -> Tuple[KMeans, ColumnTransformer]:
    """
    Preprocesa datos de candidatos, entrena un modelo K-means y guarda ambos.
    
    Args:
        df: DataFrame con datos de candidatos (debe incluir características y 'skills_text').
        n_clusters: Número de segmentos (clústeres) a crear.
        model_path: Ruta para guardar el modelo K-means entrenado.
        preprocessor_path: Ruta para guardar el preprocesador ajustado.

    Returns:
        Tupla que contiene el modelo KMeans ajustado y el ColumnTransformer ajustado.
    """
    if df.empty:
        print("Error: El DataFrame de entrada está vacío. No se puede entrenar el modelo.")
        # O lanzar un error
        raise ValueError("No se puede entrenar el modelo en un DataFrame vacío")
        
    print(f"Iniciando preprocesamiento y entrenamiento para {len(df)} candidatos...")
    preprocessor = create_preprocessor()
    
    # Ajustar el preprocesador y transformar los datos
    print("Ajustando preprocesador...")
    X_processed = preprocessor.fit_transform(df)
    print(f"Preprocesamiento completo. Forma de los datos procesados: {X_processed.shape}")

    # Entrenar el modelo K-means
    print(f"Entrenando modelo K-means con {n_clusters} clústeres...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10) # Establecer n_init explícitamente
    kmeans.fit(X_processed)
    print("Entrenamiento K-means completo.")

    # Asegurar que el directorio del modelo exista
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(preprocessor_path), exist_ok=True)

    # Guardar el modelo y el preprocesador
    try:
        joblib.dump(kmeans, model_path)
        joblib.dump(preprocessor, preprocessor_path)
        print(f"Modelo guardado en {model_path}")
        print(f"Preprocesador guardado en {preprocessor_path}")
    except Exception as e:
        print(f"Error guardando modelo/preprocesador: {e}")
        # Opcionalmente, volver a lanzar la excepción

    return kmeans, preprocessor

def load_segmentation_model(
    model_path: str = DEFAULT_MODEL_PATH, 
    preprocessor_path: str = DEFAULT_PREPROCESSOR_PATH
) -> Tuple[Optional[KMeans], Optional[ColumnTransformer]]:
    """
    Carga el modelo K-means y el preprocesador guardados.
    
    Returns:
        Tupla que contiene el modelo y el preprocesador cargados, o (None, None) si no se encuentran los archivos.
    """
    model = None
    preprocessor = None
    try:
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"Modelo cargado desde {model_path}")
        else:
             print(f"Advertencia: Archivo del modelo no encontrado en {model_path}")
             
        if os.path.exists(preprocessor_path):
            preprocessor = joblib.load(preprocessor_path)
            print(f"Preprocesador cargado desde {preprocessor_path}")
        else:
            print(f"Advertencia: Archivo del preprocesador no encontrado en {preprocessor_path}")
            
    except Exception as e:
        print(f"Error cargando modelo/preprocesador: {e}")
        # Devolver None si la carga falla
        return None, None
        
    return model, preprocessor

def predict_candidate_segments(df: pd.DataFrame, 
                               model: Optional[KMeans] = None, 
                               preprocessor: Optional[ColumnTransformer] = None) -> pd.DataFrame:
    """
    Predice segmentos de clúster para candidatos en el DataFrame.
    Carga el modelo y el preprocesador si no se proporcionan.
    """
    if df.empty:
        print("Advertencia: El DataFrame de entrada está vacío. No hay predicciones que hacer.")
        df['segment'] = np.nan # Añadir columna de segmento con NaNs
        return df
        
    if model is None or preprocessor is None:
        print("Modelo o preprocesador no proporcionado, intentando cargar desde rutas predeterminadas...")
        model, preprocessor = load_segmentation_model()
        
    if model is None or preprocessor is None:
        print("Error: No se pudo cargar el modelo o el preprocesador. No se pueden predecir segmentos.")
        # O lanzar un error
        df['segment'] = -1 # Indicar fallo
        return df

    # Asegurar que 'skills_text' exista si no está presente (podría ocurrir si se predice sobre datos nuevos)
    if 'skills_text' not in df.columns and 'skills' in df.columns:
         df['skills_text'] = df['skills'].apply(lambda x: ' '.join(x) if x else '')
    elif 'skills_text' not in df.columns:
         print("Error: Falta la columna 'skills' o 'skills_text' para la predicción.")
         df['segment'] = -1
         return df
         
    try:
        print(f"Preprocesando {len(df)} candidatos para predicción...")
        # Usar el preprocesador *cargado* para transformar los datos
        X_processed = preprocessor.transform(df)
        print("Prediciendo segmentos...")
        # Predecir etiquetas de clúster
        segments = model.predict(X_processed)
        df['segment'] = segments
        print("Predicción de segmentos completa.")
    except Exception as e:
        print(f"Error durante la predicción: {e}")
        # Asignar segmento por defecto/error
        df['segment'] = -1 

    return df

# Ejemplo de Uso (se puede ejecutar de forma independiente si los datos son simulados o se usa CSV)

# --- Nueva Función de Análisis ---

def analyze_segments_from_db():
    """
    Obtiene candidatos de la BD, analiza segmentos y devuelve resultados como un diccionario.
    Esta función requiere un contexto de aplicación Flask activo.
    """
    from .models import Candidate # Importar dentro de la función para evitar dependencia circular a nivel de módulo
    from flask import current_app # Para logging

    analysis_results = {}
    try:
        candidates = Candidate.query.all()
        if not candidates:
            current_app.logger.info("No se encontraron candidatos para el análisis de segmentos.")
            return {}

        # Convertir a DataFrame (reutilizar la lógica existente tanto como sea posible)
        df = pd.DataFrame([{
            'id': c.candidate_id,
            'name': c.name,
            'title': c.primary_skill,
            'skills': c.skills if isinstance(c.skills, list) else [], # Asegurar lista, por defecto vacía
            'experience_years': c.years_experience,
            'location': c.location,
            'segment': c.segment
        } for c in candidates])

        df['segment'] = df['segment'].astype('category') 
        df['experience_years'] = pd.to_numeric(df['experience_years'], errors='coerce')

        if df['segment'].isnull().all():
            current_app.logger.info("La columna de segmento no está poblada para ningún candidato.")
            return {}
            
        segments = sorted(df['segment'].dropna().unique())
        current_app.logger.info(f"Analizando {len(segments)} segmentos: {segments}")

        for segment_id in segments:
            segment_df = df[df['segment'] == segment_id].copy() # Usar .copy() para evitar SettingWithCopyWarning
            segment_data = {}
            segment_data['count'] = len(segment_df)

            # Estadísticas de Experiencia
            if 'experience_years' in segment_df.columns and not segment_df['experience_years'].isnull().all():
                stats = segment_df['experience_years'].describe()
                # Convertir tipos numpy a tipos estándar de Python para serialización JSON
                segment_data['experience_stats'] = {
                    'mean': float(stats.get('mean', 0)),
                    'std': float(stats.get('std', 0)),
                    'min': float(stats.get('min', 0)),
                    'max': float(stats.get('max', 0)),
                    'median': float(stats.get('50%', 0))
                }
            else:
                 segment_data['experience_stats'] = {} # Vacío si no hay datos

            # Habilidades Principales Top
            if 'title' in segment_df.columns and not segment_df['title'].isnull().all():
                top_primary = segment_df['title'].value_counts().nlargest(5)
                segment_data['top_primary_skills'] = list(top_primary.items()) # Convertir a lista de tuplas
            else:
                 segment_data['top_primary_skills'] = []

            # --- Preparar Datos para Gráfico de Habilidades Principales --- #
            if segment_data['top_primary_skills']:
                chart_labels = [item[0] for item in segment_data['top_primary_skills']]
                chart_data = [item[1] for item in segment_data['top_primary_skills']]
                segment_data['primary_skills_chart'] = {
                    'labels': chart_labels,
                    'data': chart_data
                }
            else:
                segment_data['primary_skills_chart'] = {'labels': [], 'data': []}
            # --- Fin Preparación Datos de Gráfico --- #

            # Ubicaciones Top
            if 'location' in segment_df.columns and not segment_df['location'].isnull().all():
                top_locations = segment_df['location'].value_counts().nlargest(5)
                segment_data['locations'] = list(top_locations.items())
            else:
                segment_data['locations'] = []

            # --- Preparar Datos para Gráfico de Experiencia --- #
            if 'experience_years' in segment_df.columns and not segment_df['experience_years'].isnull().all():
                exp_data = segment_df['experience_years']
                # Definir rangos (ajustar según sea necesario)
                bins = [0, 5, 10, 15, 20, 26] # Rangos: 0-4, 5-9, 10-14, 15-19, 20-25
                labels = ['0-4 yrs', '5-9 yrs', '10-14 yrs', '15-19 yrs', '20+ yrs']
                # Usar pandas.cut para categorizar la experiencia
                exp_binned = pd.cut(exp_data, bins=bins, labels=labels, right=False) # right=False incluye 0 en el primer rango
                # Contar ocurrencias en cada rango
                exp_counts = exp_binned.value_counts().sort_index()
                segment_data['experience_chart'] = {
                    'labels': list(exp_counts.index.astype(str)), # Asegurar que las etiquetas sean strings
                    'data': list(exp_counts.values.astype(float)) # Asegurar que los datos sean floats
                }
            else:
                 segment_data['experience_chart'] = {'labels': [], 'data': []} # Vacío si no hay datos
            # --- Fin Preparación Datos de Gráfico --- #

            # Habilidades Generales Top
            if 'skills' in segment_df.columns and not segment_df['skills'].isnull().all():
                skills_series = segment_df['skills'].dropna()
                skills_series = skills_series[skills_series.apply(lambda x: isinstance(x, list))]
                if not skills_series.empty:
                    exploded_skills = skills_series.explode()
                    valid_skills = exploded_skills.astype(str).str.strip()
                    valid_skills = valid_skills[valid_skills != '']
                    if not valid_skills.empty:
                        top_overall = valid_skills.value_counts().nlargest(10)
                        segment_data['top_overall_skills'] = list(top_overall.items())
                    else:
                        segment_data['top_overall_skills'] = []
                else:
                     segment_data['top_overall_skills'] = []
            else:
                 segment_data['top_overall_skills'] = []
                 
            analysis_results[segment_id] = segment_data
        # --- Fin Bucle --- #

        # --- Calcular Datos de Gráfico Generales --- # 

        # Distribución General de Experiencia
        overall_experience_chart_data = {'labels': [], 'datasets': []}
        if 'experience_years' in df.columns and not df['experience_years'].isnull().all():
            exp_data = df['experience_years']
            bins = [0, 5, 10, 15, 20, 26]
            labels = ['0-4 yrs', '5-9 yrs', '10-14 yrs', '15-19 yrs', '20+ yrs']
            exp_binned = pd.cut(exp_data, bins=bins, labels=labels, right=False)
            exp_counts = exp_binned.value_counts().sort_index()
            overall_experience_chart_data = {
                'labels': list(exp_counts.index.astype(str)), 
                'datasets': [{
                    'label': 'Candidate Count', # Etiqueta añadida
                    'data': list(exp_counts.values.astype(float)),
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)', # Color de ejemplo
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                }]
            }

        # Distribución General de Habilidades Principales Top
        overall_primary_skills_chart_data = {'labels': [], 'datasets': []}
        if 'title' in df.columns and not df['title'].isnull().all():
            top_primary_overall = df['title'].value_counts().nlargest(5)
            overall_primary_skills_chart_data = {
                'labels': list(top_primary_overall.index),
                'datasets': [{
                    'label': 'Candidate Count', # Etiqueta añadida
                    'data': list(top_primary_overall.values.astype(float)),
                    'backgroundColor': 'rgba(255, 159, 64, 0.6)', # Color de ejemplo
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1
                }]
            }

        # Añadir datos del gráfico general al diccionario final de resultados
        analysis_results['overall_experience_chart_data'] = overall_experience_chart_data
        analysis_results['overall_primary_skills_chart_data'] = overall_primary_skills_chart_data

        current_app.logger.info(f"Análisis de segmentos completo. Claves de la estructura de resultados: {list(analysis_results.keys())}")
        return analysis_results

    except Exception as e:
        current_app.logger.error(f"Error durante la función de análisis de segmentos: {e}", exc_info=True)
        return {'error': str(e)} # Devolver información de error

# --- Fin Función de Análisis ---

if __name__ == '__main__':
    print("Ejecutando ejemplo de script del Modelo ML...")
    # --- Datos Simulados --- 
    # En un escenario real, reemplazar esto con load_candidate_data(candidates=...) llamado desde Flask
    mock_data = [
        {'candidate_id': 'C1', 'location': 'New York', 'years_experience': 5, 'education_level': 'Masters', 'skills': ['python', 'sql', 'aws'], 'primary_skill': 'python', 'desired_salary': 120000},
        {'candidate_id': 'C2', 'location': 'San Francisco', 'years_experience': 3, 'education_level': 'Bachelors', 'skills': ['javascript', 'react', 'node'], 'primary_skill': 'javascript', 'desired_salary': 110000},
        {'candidate_id': 'C3', 'location': 'New York', 'years_experience': 6, 'education_level': 'Masters', 'skills': ['python', 'pandas', 'scikit-learn'], 'primary_skill': 'python', 'desired_salary': 130000},
        {'candidate_id': 'C4', 'location': 'Chicago', 'years_experience': 2, 'education_level': 'Bachelors', 'skills': ['java', 'spring'], 'primary_skill': 'java', 'desired_salary': 90000},
        {'candidate_id': 'C5', 'location': 'San Francisco', 'years_experience': 4, 'education_level': 'Masters', 'skills': ['react', 'typescript', 'graphql'], 'primary_skill': 'react', 'desired_salary': 125000},
        {'candidate_id': 'C6', 'location': 'New York', 'years_experience': 5, 'education_level': 'PhD', 'skills': ['machine learning', 'python', 'tensorflow'], 'primary_skill': 'machine learning', 'desired_salary': 150000},
        # Añadir un candidato con datos faltantes
        {'candidate_id': 'C7', 'location': 'Chicago', 'years_experience': None, 'education_level': 'Bachelors', 'skills': ['java', 'sql'], 'primary_skill': 'java', 'desired_salary': None},
        # Añadir un candidato con skills None
        {'candidate_id': 'C8', 'location': 'Austin', 'years_experience': 1, 'education_level': 'Bachelors', 'skills': None, 'primary_skill': 'python', 'desired_salary': 80000},
    ]
    candidate_df = load_candidate_data(candidates=[type('obj', (object,), item)() for item in mock_data]) # Creación rápida de objeto simulado
    
    if not candidate_df.empty:
        # --- Entrenar --- 
        print("\n--- Entrenando Modelo ---")
        model, preprocessor = train_segmentation_model(candidate_df, n_clusters=3) # Entrenar con 3 clústeres para ejemplo
        
        # --- Predecir (sobre datos de entrenamiento) ---
        print("\n--- Prediciendo Segmentos (sobre datos de entrenamiento) ---")
        df_with_segments = predict_candidate_segments(candidate_df, model, preprocessor)
        print("Candidatos con segmentos predichos:")
        print(df_with_segments[['segment']])
        
        # --- Predecir (cargando modelo) ---
        print("\n--- Prediciendo Segmentos (cargando modelo) ---")
        # Simular carga posterior
        loaded_model, loaded_preprocessor = load_segmentation_model()
        if loaded_model and loaded_preprocessor:
            # Predecir sobre datos nuevos o los mismos
            df_predicted_again = predict_candidate_segments(candidate_df.copy(), loaded_model, loaded_preprocessor)
            print("Predicciones después de cargar el modelo:")
            print(df_predicted_again[['segment']])
        else:
            print("No se pudo cargar el modelo/preprocesador para el ejemplo de predicción.")
    else:
        print("Omitiendo entrenamiento/predicción debido a un DataFrame vacío.")
