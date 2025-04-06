"""
Funciones de evaluación y análisis para el módulo de machine learning de AdFlux.
"""

import pandas as pd
import numpy as np
from flask import current_app
from typing import Dict, Any, List

from .preprocessing import load_candidate_data
from .prediction import predict_candidate_segments
from .utils import load_segmentation_model


def analyze_segments_from_db() -> Dict[str, Any]:
    """
    Obtiene candidatos de la BD, analiza segmentos y devuelve resultados como un diccionario.
    Esta función requiere un contexto de aplicación Flask activo.
    
    Returns:
        Diccionario con resultados del análisis de segmentos.
    """
    from ..models import Candidate  # Importar dentro de la función para evitar dependencia circular a nivel de módulo

    analysis_results = {}
    try:
        candidates = Candidate.query.all()
        if not candidates:
            current_app.logger.info("No se encontraron candidatos para el análisis de segmentos.")
            return {'error': 'No se encontraron candidatos para el análisis.'}
            
        current_app.logger.info(f"Analizando segmentos para {len(candidates)} candidatos...")
        
        # Cargar datos de candidatos
        candidate_df = load_candidate_data(candidates=candidates)
        if candidate_df.empty:
            current_app.logger.warning("DataFrame de candidatos vacío después de la carga.")
            return {'error': 'Error al cargar datos de candidatos.'}
            
        # Cargar modelo y preprocesador
        model, preprocessor = load_segmentation_model()
        if model is None or preprocessor is None:
            current_app.logger.error("No se pudo cargar el modelo de segmentación para el análisis.")
            return {'error': 'No se pudo cargar el modelo de segmentación.'}
            
        # Predecir segmentos si no están ya en el DataFrame
        if 'segment' not in candidate_df.columns:
            candidate_df = predict_candidate_segments(candidate_df, model, preprocessor)
            
        # Verificar que la predicción fue exitosa
        if 'segment' not in candidate_df.columns or (candidate_df['segment'] == -1).all():
            current_app.logger.error("Fallo en la predicción de segmentos para el análisis.")
            return {'error': 'Fallo en la predicción de segmentos.'}
            
        # Obtener número de segmentos
        n_segments = len(candidate_df['segment'].unique())
        if -1 in candidate_df['segment'].unique():  # Si hay errores de predicción
            n_segments -= 1  # No contar el segmento de error
            
        current_app.logger.info(f"Analizando {n_segments} segmentos...")
        
        # Inicializar resultados
        analysis_results = {
            'total_candidates': len(candidate_df),
            'n_segments': n_segments,
            'segments': {}
        }
        
        # Analizar cada segmento
        for segment_id in sorted(candidate_df['segment'].unique()):
            if segment_id == -1:  # Omitir segmento de error
                continue
                
            # Filtrar candidatos de este segmento
            segment_df = candidate_df[candidate_df['segment'] == segment_id]
            segment_size = len(segment_df)
            
            # Inicializar datos del segmento
            segment_data = {
                'id': int(segment_id),
                'size': segment_size,
                'percentage': round((segment_size / len(candidate_df)) * 100, 1)
            }
            
            # Calcular estadísticas de experiencia
            if 'years_experience' in segment_df.columns and not segment_df['years_experience'].isnull().all():
                segment_data['avg_experience'] = round(segment_df['years_experience'].mean(), 1)
                segment_data['min_experience'] = int(segment_df['years_experience'].min())
                segment_data['max_experience'] = int(segment_df['years_experience'].max())
            else:
                segment_data['avg_experience'] = None
                segment_data['min_experience'] = None
                segment_data['max_experience'] = None
                
            # Calcular estadísticas de salario
            if 'desired_salary' in segment_df.columns and not segment_df['desired_salary'].isnull().all():
                segment_data['avg_salary'] = int(segment_df['desired_salary'].mean())
                segment_data['min_salary'] = int(segment_df['desired_salary'].min())
                segment_data['max_salary'] = int(segment_df['desired_salary'].max())
            else:
                segment_data['avg_salary'] = None
                segment_data['min_salary'] = None
                segment_data['max_salary'] = None
                
            # Habilidades Primarias Top
            if 'primary_skill' in segment_df.columns and not segment_df['primary_skill'].isnull().all():
                top_primary = segment_df['primary_skill'].value_counts().nlargest(5)
                segment_data['top_primary_skills'] = list(top_primary.items())
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
            if 'years_experience' in segment_df.columns and not segment_df['years_experience'].isnull().all():
                exp_data = segment_df['years_experience']
                # Definir rangos (ajustar según sea necesario)
                bins = [0, 5, 10, 15, 20, 26]  # Rangos: 0-4, 5-9, 10-14, 15-19, 20-25
                labels = ['0-4 yrs', '5-9 yrs', '10-14 yrs', '15-19 yrs', '20+ yrs']
                # Usar pandas.cut para categorizar la experiencia
                exp_binned = pd.cut(exp_data, bins=bins, labels=labels, right=False)  # right=False incluye 0 en el primer rango
                # Contar ocurrencias en cada rango
                exp_counts = exp_binned.value_counts().sort_index()
                segment_data['experience_chart'] = {
                    'labels': list(exp_counts.index.astype(str)),  # Asegurar que las etiquetas sean strings
                    'data': list(exp_counts.values.astype(float))  # Asegurar que los datos sean floats
                }
            else:
                segment_data['experience_chart'] = {'labels': [], 'data': []}  # Vacío si no hay datos
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

            # --- Preparar Datos para Gráfico de Habilidades Generales --- #
            if segment_data['top_overall_skills']:
                chart_labels = [item[0] for item in segment_data['top_overall_skills']]
                chart_data = [item[1] for item in segment_data['top_overall_skills']]
                segment_data['overall_skills_chart'] = {
                    'labels': chart_labels,
                    'data': chart_data
                }
            else:
                segment_data['overall_skills_chart'] = {'labels': [], 'data': []}
            # --- Fin Preparación Datos de Gráfico --- #

            # Niveles de Educación
            if 'education_level' in segment_df.columns and not segment_df['education_level'].isnull().all():
                education_counts = segment_df['education_level'].value_counts()
                segment_data['education_levels'] = list(education_counts.items())
                
                # --- Preparar Datos para Gráfico de Educación --- #
                chart_labels = [item[0] for item in segment_data['education_levels']]
                chart_data = [item[1] for item in segment_data['education_levels']]
                segment_data['education_chart'] = {
                    'labels': chart_labels,
                    'data': chart_data
                }
            else:
                segment_data['education_levels'] = []
                segment_data['education_chart'] = {'labels': [], 'data': []}

            # Añadir datos del segmento a los resultados
            analysis_results['segments'][str(segment_id)] = segment_data

        current_app.logger.info("Análisis de segmentos completado exitosamente.")
        return analysis_results

    except Exception as e:
        current_app.logger.error(f"Error durante la función de análisis de segmentos: {e}", exc_info=True)
        return {'error': str(e)}  # Devolver información de error
