"""
Funciones de preprocesamiento de datos para el módulo de machine learning de AdFlux.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from typing import List, Optional


def load_candidate_data(candidates: Optional[List] = None) -> pd.DataFrame:
    """
    Carga datos de candidatos en un DataFrame de pandas.
    Si se proporciona la lista de candidatos (instancias del modelo SQLAlchemy), la utiliza.
    De lo contrario, intenta consultar a todos los candidatos (requiere contexto de aplicación).
    
    Args:
        candidates: Lista opcional de objetos Candidate.
        
    Returns:
        DataFrame de pandas con los datos de los candidatos.
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
        # from ..models import Candidate
        # all_candidates = Candidate.query.all()
        # data = [...] # Convertir all_candidates como arriba
        print("Advertencia: No se proporcionaron candidatos y no se puede consultar la base de datos fuera del contexto de la aplicación.")
        return pd.DataFrame()  # Devolver DataFrame vacío
    
    # Establecer candidate_id como índice
    if 'candidate_id' in df.columns:
        df.set_index('candidate_id', inplace=True)
    
    # Preprocesar datos
    # 1. Convertir skills a texto para vectorización
    if 'skills' in df.columns:
        df['skills_text'] = df['skills'].apply(lambda x: ' '.join(x) if x else '')
    
    # 2. Convertir years_experience a numérico si es posible
    if 'years_experience' in df.columns:
        df['years_experience'] = pd.to_numeric(df['years_experience'], errors='coerce')
    
    # 3. Convertir desired_salary a numérico si es posible
    if 'desired_salary' in df.columns:
        df['desired_salary'] = pd.to_numeric(df['desired_salary'], errors='coerce')
    
    return df


def create_preprocessor() -> ColumnTransformer:
    """
    Crea un preprocesador para los datos de candidatos.
    
    Returns:
        ColumnTransformer configurado para preprocesar datos de candidatos.
    """
    # Definir transformadores para diferentes tipos de columnas
    
    # 1. Transformador para características numéricas
    numeric_features = ['years_experience', 'desired_salary']
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),  # Imputar valores faltantes con la mediana
        ('scaler', StandardScaler())  # Escalar características numéricas
    ])
    
    # 2. Transformador para características categóricas
    categorical_features = ['location', 'education_level', 'primary_skill']
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),  # Imputar valores faltantes con 'unknown'
        ('onehot', OneHotEncoder(handle_unknown='ignore'))  # Codificación one-hot
    ])
    
    # 3. Transformador para texto (skills)
    text_features = ['skills_text']
    text_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='')),  # Imputar valores faltantes con cadena vacía
        ('tfidf', TfidfVectorizer(max_features=100))  # Vectorización TF-IDF con máximo 100 características
    ])
    
    # Combinar todos los transformadores en un ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features),
            ('txt', text_transformer, text_features)
        ],
        remainder='drop'  # Descartar columnas no especificadas
    )
    
    return preprocessor
