# Optimización de Contenido con IA

Este documento describe cómo AdFlux utiliza inteligencia artificial para generar y optimizar contenido para anuncios de trabajo en diferentes plataformas publicitarias.

## Contenido

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Integración con Gemini AI](#integración-con-gemini-ai)
4. [Generación de Contenido](#generación-de-contenido)
5. [Adaptación por Plataforma](#adaptación-por-plataforma)
6. [Optimización Basada en Datos](#optimización-basada-en-datos)
7. [Evaluación de Calidad](#evaluación-de-calidad)
8. [Flujo de Trabajo Completo](#flujo-de-trabajo-completo)
9. [Mejores Prácticas](#mejores-prácticas)
10. [Limitaciones y Consideraciones](#limitaciones-y-consideraciones)

## Introducción

La creación de anuncios efectivos para ofertas de trabajo es un desafío que requiere creatividad, conocimiento del mercado laboral y adaptación a diferentes plataformas publicitarias. AdFlux automatiza este proceso utilizando modelos avanzados de IA para generar contenido persuasivo y relevante para cada oferta de trabajo.

El sistema de optimización de contenido de AdFlux:

- Genera títulos, descripciones y llamadas a la acción para anuncios
- Adapta el contenido a diferentes plataformas (Meta, Google Ads, TikTok, Snapchat)
- Optimiza el contenido basándose en datos históricos de rendimiento
- Personaliza el tono y estilo según la audiencia objetivo
- Garantiza el cumplimiento de las políticas publicitarias de cada plataforma

## Arquitectura del Sistema

La arquitectura del sistema de optimización de contenido sigue un enfoque modular:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Extracción de  │────▶│  Generación de  │────▶│  Adaptación de  │
│   Información   │     │    Contenido    │     │    Contenido    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                       │
        │                       │                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Datos de la    │     │    Gemini AI    │     │  Optimización   │
│    Oferta       │     │                 │     │   y Validación  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Componentes Principales

1. **Extracción de Información**: Analiza la oferta de trabajo para identificar aspectos clave como requisitos, beneficios y responsabilidades.
2. **Generación de Contenido**: Utiliza Gemini AI para crear diferentes variantes de contenido creativo.
3. **Adaptación de Contenido**: Ajusta el contenido generado para cada plataforma publicitaria específica.
4. **Optimización y Validación**: Evalúa y refina el contenido basándose en datos históricos y políticas publicitarias.

## Integración con Gemini AI

AdFlux utiliza la API de Gemini AI para generar contenido creativo. La integración se realiza a través del módulo `adflux.gemini.client`:

```python
class GeminiApiClient:
    def __init__(self, api_key=None, model_name="gemini-2.5-pro-exp-03-25"):
        """
        Inicializa el cliente de la API de Gemini.
        
        Args:
            api_key: Clave de API de Gemini (opcional, por defecto usa la variable de entorno)
            model_name: Nombre del modelo a utilizar
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.model_name = model_name
        
        # Configurar la API
        genai.configure(api_key=self.api_key)
        
        # Inicializar modelo
        self.model = genai.GenerativeModel(self.model_name)
        
        # Configurar safety settings por defecto
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
```

### Configuración del Modelo

AdFlux utiliza el modelo `gemini-2.5-pro-exp-03-25` por su capacidad para generar contenido creativo de alta calidad. La configuración del modelo se puede ajustar según las necesidades específicas:

```python
def generate_content(self, prompt, max_tokens=None, temperature=0.7, top_p=0.95, top_k=40):
    """
    Genera contenido utilizando el modelo de Gemini.
    
    Args:
        prompt: Prompt para la generación
        max_tokens: Número máximo de tokens a generar
        temperature: Temperatura para la generación (0.0-1.0)
        top_p: Valor de top-p para la generación
        top_k: Valor de top-k para la generación
        
    Returns:
        Respuesta generada
    """
    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
    }
    
    if max_tokens:
        generation_config["max_output_tokens"] = max_tokens
    
    response = self.model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=self.safety_settings
    )
    
    return response
```

## Generación de Contenido

El proceso de generación de contenido comienza con la extracción de información relevante de la oferta de trabajo:

```python
def extract_job_information(job_opening):
    """
    Extrae información relevante de una oferta de trabajo.
    
    Args:
        job_opening: Objeto JobOpening
        
    Returns:
        Diccionario con información estructurada
    """
    # Extraer información básica
    info = {
        'title': job_opening.title,
        'company': job_opening.company,
        'location': job_opening.location,
        'employment_type': job_opening.employment_type,
        'description': job_opening.description,
        'requirements': job_opening.requirements,
        'benefits': []
    }
    
    # Extraer beneficios
    if job_opening.benefits:
        if isinstance(job_opening.benefits, list):
            info['benefits'] = job_opening.benefits
        elif isinstance(job_opening.benefits, str):
            # Intentar extraer beneficios del texto
            benefits = []
            for line in job_opening.benefits.split('\n'):
                line = line.strip()
                if line and not line.endswith(':'):
                    benefits.append(line)
            info['benefits'] = benefits
    
    # Extraer rango salarial si existe
    if job_opening.salary_min and job_opening.salary_max:
        info['salary_range'] = f"{job_opening.salary_min}-{job_opening.salary_max}"
    elif job_opening.salary_min:
        info['salary_range'] = f"From {job_opening.salary_min}"
    elif job_opening.salary_max:
        info['salary_range'] = f"Up to {job_opening.salary_max}"
    else:
        info['salary_range'] = None
    
    return info
```

### Generación de Anuncios para Meta

Para generar contenido para anuncios en Meta (Facebook/Instagram):

```python
def generate_meta_ad_content(job_info, format="feed", audience=None):
    """
    Genera contenido para anuncios de Meta.
    
    Args:
        job_info: Información de la oferta de trabajo
        format: Formato del anuncio (feed, story, carousel)
        audience: Información sobre la audiencia objetivo
        
    Returns:
        Diccionario con contenido generado
    """
    client = GeminiApiClient()
    
    # Construir prompt
    prompt = f"""
    Genera contenido creativo para un anuncio de trabajo en Meta ({format}) con las siguientes características:
    
    Puesto: {job_info['title']}
    Empresa: {job_info['company']}
    Ubicación: {job_info['location']}
    Tipo de empleo: {job_info['employment_type']}
    
    Descripción breve:
    {job_info['description'][:500]}...
    
    Requisitos principales:
    {job_info['requirements'][:300]}...
    
    {"Beneficios: " + ", ".join(job_info['benefits'][:5]) if job_info['benefits'] else ""}
    {"Rango salarial: " + job_info['salary_range'] if job_info['salary_range'] else ""}
    
    {"Audiencia objetivo: " + audience if audience else ""}
    
    El contenido debe ser persuasivo, atractivo y optimizado para Meta {format}.
    
    Devuelve el resultado en formato JSON con los siguientes campos:
    - headline: Título principal del anuncio (máximo 40 caracteres)
    - primary_text: Texto principal del anuncio (máximo 125 caracteres)
    - description: Descripción adicional (máximo 30 caracteres)
    - cta: Llamada a la acción (una de las siguientes: APPLY_NOW, LEARN_MORE, SIGN_UP, CONTACT_US)
    
    Solo devuelve el JSON, sin explicaciones adicionales.
    """
    
    # Generar contenido
    response = client.generate_content(prompt, max_tokens=500, temperature=0.7)
    
    # Parsear respuesta JSON
    try:
        content = json.loads(response.text)
        return content
    except json.JSONDecodeError:
        # Si la respuesta no es JSON válido, intentar extraer JSON de la respuesta
        match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        if match:
            try:
                content = json.loads(match.group(1))
                return content
            except json.JSONDecodeError:
                raise ValueError("No se pudo parsear la respuesta como JSON")
        else:
            raise ValueError("No se pudo parsear la respuesta como JSON")
```

### Generación de Anuncios para Google Ads

Para generar contenido para anuncios en Google Ads:

```python
def generate_google_ads_content(job_info, ad_type="responsive_search_ad"):
    """
    Genera contenido para anuncios de Google Ads.
    
    Args:
        job_info: Información de la oferta de trabajo
        ad_type: Tipo de anuncio (responsive_search_ad, display_ad)
        
    Returns:
        Diccionario con contenido generado
    """
    client = GeminiApiClient()
    
    # Construir prompt
    prompt = f"""
    Genera contenido para un anuncio de trabajo en Google Ads ({ad_type}) con las siguientes características:
    
    Puesto: {job_info['title']}
    Empresa: {job_info['company']}
    Ubicación: {job_info['location']}
    Tipo de empleo: {job_info['employment_type']}
    
    Descripción breve:
    {job_info['description'][:300]}...
    
    {"Beneficios: " + ", ".join(job_info['benefits'][:3]) if job_info['benefits'] else ""}
    {"Rango salarial: " + job_info['salary_range'] if job_info['salary_range'] else ""}
    
    El contenido debe ser conciso, relevante y optimizado para búsquedas en Google.
    
    Devuelve el resultado en formato JSON con los siguientes campos:
    - headlines: Lista de 5 títulos (máximo 30 caracteres cada uno)
    - descriptions: Lista de 4 descripciones (máximo 90 caracteres cada una)
    - path1: Primera parte de la URL de visualización (máximo 15 caracteres)
    - path2: Segunda parte de la URL de visualización (máximo 15 caracteres)
    
    Solo devuelve el JSON, sin explicaciones adicionales.
    """
    
    # Generar contenido
    response = client.generate_content(prompt, max_tokens=800, temperature=0.7)
    
    # Parsear respuesta JSON
    try:
        content = json.loads(response.text)
        return content
    except json.JSONDecodeError:
        # Intentar extraer JSON
        match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        if match:
            try:
                content = json.loads(match.group(1))
                return content
            except json.JSONDecodeError:
                raise ValueError("No se pudo parsear la respuesta como JSON")
        else:
            raise ValueError("No se pudo parsear la respuesta como JSON")
```

## Adaptación por Plataforma

Cada plataforma publicitaria tiene requisitos específicos para el contenido de los anuncios. AdFlux adapta automáticamente el contenido generado para cada plataforma:

### Adaptación para Meta

```python
def adapt_content_for_meta(content, format="feed"):
    """
    Adapta el contenido generado para Meta.
    
    Args:
        content: Contenido generado
        format: Formato del anuncio (feed, story, carousel)
        
    Returns:
        Contenido adaptado
    """
    adapted = content.copy()
    
    # Verificar longitudes
    if len(adapted['headline']) > 40:
        adapted['headline'] = adapted['headline'][:37] + '...'
    
    if len(adapted['primary_text']) > 125:
        adapted['primary_text'] = adapted['primary_text'][:122] + '...'
    
    if len(adapted.get('description', '')) > 30:
        adapted['description'] = adapted['description'][:27] + '...'
    
    # Verificar CTA válido
    valid_ctas = ['APPLY_NOW', 'LEARN_MORE', 'SIGN_UP', 'CONTACT_US']
    if adapted.get('cta') not in valid_ctas:
        adapted['cta'] = 'APPLY_NOW'
    
    # Adaptaciones específicas por formato
    if format == "story":
        # Para stories, el texto debe ser más corto
        if len(adapted['primary_text']) > 60:
            adapted['primary_text'] = adapted['primary_text'][:57] + '...'
    
    return adapted
```

### Adaptación para Google Ads

```python
def adapt_content_for_google_ads(content, ad_type="responsive_search_ad"):
    """
    Adapta el contenido generado para Google Ads.
    
    Args:
        content: Contenido generado
        ad_type: Tipo de anuncio
        
    Returns:
        Contenido adaptado
    """
    adapted = content.copy()
    
    # Verificar longitudes de títulos
    adapted['headlines'] = [headline[:30] for headline in adapted['headlines']]
    
    # Verificar longitudes de descripciones
    adapted['descriptions'] = [desc[:90] for desc in adapted['descriptions']]
    
    # Verificar longitudes de paths
    if 'path1' in adapted and len(adapted['path1']) > 15:
        adapted['path1'] = adapted['path1'][:15]
    
    if 'path2' in adapted and len(adapted['path2']) > 15:
        adapted['path2'] = adapted['path2'][:15]
    
    # Limitar número de elementos
    adapted['headlines'] = adapted['headlines'][:15]  # Google permite hasta 15 títulos
    adapted['descriptions'] = adapted['descriptions'][:4]  # Google permite hasta 4 descripciones
    
    return adapted
```

## Optimización Basada en Datos

AdFlux utiliza datos históricos de rendimiento para optimizar el contenido de los anuncios:

```python
def optimize_content_with_historical_data(content, platform, job_category, metrics_data):
    """
    Optimiza el contenido basándose en datos históricos de rendimiento.
    
    Args:
        content: Contenido generado
        platform: Plataforma publicitaria
        job_category: Categoría de la oferta de trabajo
        metrics_data: Datos históricos de métricas
        
    Returns:
        Contenido optimizado
    """
    optimized = content.copy()
    
    # Analizar patrones de alto rendimiento
    if platform == 'META':
        # Analizar palabras clave de alto rendimiento en títulos
        high_performing_headlines = metrics_data.get('high_performing_headlines', [])
        if high_performing_headlines:
            # Verificar si el título actual contiene palabras clave de alto rendimiento
            current_headline = optimized['headline'].lower()
            contains_high_performing = any(kw.lower() in current_headline for kw in high_performing_headlines)
            
            if not contains_high_performing:
                # Sugerir mejora del título
                client = GeminiApiClient()
                prompt = f"""
                Mejora el siguiente título de anuncio para Meta incorporando alguna de estas palabras o frases de alto rendimiento:
                {', '.join(high_performing_headlines)}
                
                Título actual: {optimized['headline']}
                
                El nuevo título debe tener máximo 40 caracteres y mantener la esencia del puesto.
                Devuelve solo el título mejorado, sin explicaciones.
                """
                
                response = client.generate_content(prompt, max_tokens=100, temperature=0.3)
                new_headline = response.text.strip()
                
                if len(new_headline) <= 40:
                    optimized['headline'] = new_headline
    
    elif platform == 'GOOGLE':
        # Optimizar títulos basados en CTR histórico
        high_ctr_patterns = metrics_data.get('high_ctr_patterns', [])
        
        if high_ctr_patterns and 'headlines' in optimized:
            # Reordenar títulos para poner primero los que contienen patrones de alto CTR
            scored_headlines = []
            for headline in optimized['headlines']:
                score = sum(1 for pattern in high_ctr_patterns if pattern.lower() in headline.lower())
                scored_headlines.append((headline, score))
            
            # Ordenar por puntuación descendente
            scored_headlines.sort(key=lambda x: x[1], reverse=True)
            optimized['headlines'] = [h[0] for h in scored_headlines]
    
    return optimized
```

## Evaluación de Calidad

AdFlux evalúa la calidad del contenido generado antes de utilizarlo en campañas:

```python
def evaluate_content_quality(content, platform):
    """
    Evalúa la calidad del contenido generado.
    
    Args:
        content: Contenido generado
        platform: Plataforma publicitaria
        
    Returns:
        Puntuación de calidad y recomendaciones
    """
    score = 100
    recommendations = []
    
    if platform == 'META':
        # Evaluar título
        if len(content['headline']) < 20:
            score -= 10
            recommendations.append("El título es demasiado corto, considera hacerlo más descriptivo")
        
        # Evaluar texto principal
        if len(content['primary_text']) < 60:
            score -= 10
            recommendations.append("El texto principal es demasiado corto, añade más detalles sobre el puesto")
        
        # Verificar palabras clave relevantes
        if 'job' not in content['primary_text'].lower() and 'position' not in content['primary_text'].lower():
            score -= 5
            recommendations.append("Considera incluir palabras como 'job' o 'position' en el texto principal")
        
        # Verificar llamada a la acción
        if content.get('cta') != 'APPLY_NOW':
            score -= 5
            recommendations.append("Para anuncios de trabajo, 'APPLY_NOW' suele tener mejor rendimiento como CTA")
    
    elif platform == 'GOOGLE':
        # Evaluar títulos
        if len(content['headlines']) < 3:
            score -= 15
            recommendations.append("Proporciona al menos 3 variantes de títulos para optimizar el rendimiento")
        
        # Evaluar descripciones
        if len(content['descriptions']) < 2:
            score -= 15
            recommendations.append("Proporciona al menos 2 variantes de descripciones")
        
        # Verificar palabras clave en títulos
        keywords_in_headlines = False
        for headline in content['headlines']:
            if 'job' in headline.lower() or 'career' in headline.lower() or 'position' in headline.lower():
                keywords_in_headlines = True
                break
        
        if not keywords_in_headlines:
            score -= 10
            recommendations.append("Incluye palabras clave como 'job', 'career' o 'position' en al menos un título")
    
    return {
        'score': score,
        'recommendations': recommendations,
        'quality': 'high' if score >= 80 else 'medium' if score >= 60 else 'low'
    }
```

## Flujo de Trabajo Completo

El flujo de trabajo completo para la generación y optimización de contenido es:

```python
def generate_optimized_ad_content(job_opening_id, platform, format=None, audience=None):
    """
    Genera contenido optimizado para anuncios.
    
    Args:
        job_opening_id: ID de la oferta de trabajo
        platform: Plataforma publicitaria (META, GOOGLE, TIKTOK, SNAPCHAT)
        format: Formato del anuncio (específico de la plataforma)
        audience: Información sobre la audiencia objetivo
        
    Returns:
        Contenido optimizado para anuncios
    """
    # Obtener oferta de trabajo
    job_opening = JobOpening.query.get(job_opening_id)
    if not job_opening:
        raise ValueError(f"Oferta de trabajo con ID {job_opening_id} no encontrada")
    
    # Extraer información
    job_info = extract_job_information(job_opening)
    
    # Obtener datos históricos para optimización
    metrics_data = get_historical_metrics(platform, job_opening.category)
    
    # Generar contenido según plataforma
    if platform == 'META':
        content = generate_meta_ad_content(job_info, format=format or 'feed', audience=audience)
        content = adapt_content_for_meta(content, format=format or 'feed')
    elif platform == 'GOOGLE':
        content = generate_google_ads_content(job_info, ad_type=format or 'responsive_search_ad')
        content = adapt_content_for_google_ads(content, ad_type=format or 'responsive_search_ad')
    elif platform == 'TIKTOK':
        content = generate_tiktok_ad_content(job_info, format=format or 'feed')
        content = adapt_content_for_tiktok(content, format=format or 'feed')
    elif platform == 'SNAPCHAT':
        content = generate_snapchat_ad_content(job_info, format=format or 'single_image')
        content = adapt_content_for_snapchat(content, format=format or 'single_image')
    else:
        raise ValueError(f"Plataforma no soportada: {platform}")
    
    # Optimizar contenido con datos históricos
    optimized_content = optimize_content_with_historical_data(content, platform, job_opening.category, metrics_data)
    
    # Evaluar calidad
    quality_evaluation = evaluate_content_quality(optimized_content, platform)
    
    # Si la calidad es baja, intentar mejorar
    if quality_evaluation['quality'] == 'low':
        # Intentar regenerar con las recomendaciones
        recommendations = quality_evaluation['recommendations']
        improved_content = improve_content_based_on_recommendations(optimized_content, platform, recommendations)
        
        # Evaluar nuevamente
        new_quality = evaluate_content_quality(improved_content, platform)
        
        # Usar el contenido mejorado si tiene mejor puntuación
        if new_quality['score'] > quality_evaluation['score']:
            optimized_content = improved_content
            quality_evaluation = new_quality
    
    # Guardar contenido generado
    ad_content = AdContent(
        job_opening_id=job_opening_id,
        platform=platform,
        format=format,
        content=optimized_content,
        quality_score=quality_evaluation['score'],
        recommendations=quality_evaluation['recommendations'],
        created_at=datetime.utcnow()
    )
    db.session.add(ad_content)
    db.session.commit()
    
    return {
        'content': optimized_content,
        'quality': quality_evaluation,
        'content_id': ad_content.id
    }
```

## Mejores Prácticas

Para obtener los mejores resultados con la generación y optimización de contenido:

1. **Descripciones Detalladas**: Proporciona descripciones completas y detalladas de las ofertas de trabajo.
2. **Beneficios Claros**: Destaca los beneficios para los candidatos de manera clara y específica.
3. **Audiencia Definida**: Define claramente la audiencia objetivo para personalizar el contenido.
4. **Variedad de Formatos**: Genera contenido para diferentes formatos de anuncios en cada plataforma.
5. **Pruebas A/B**: Utiliza pruebas A/B para comparar diferentes variantes de contenido.
6. **Actualización Regular**: Actualiza el contenido regularmente basándote en el rendimiento.

## Limitaciones y Consideraciones

- **Calidad de Entrada**: La calidad del contenido generado depende de la calidad de la información de entrada.
- **Políticas Publicitarias**: El contenido debe cumplir con las políticas publicitarias de cada plataforma.
- **Limitaciones de Tokens**: La generación de contenido está limitada por el número de tokens disponibles.
- **Variabilidad**: La generación de contenido puede variar con diferentes ejecuciones.
- **Supervisión Humana**: Se recomienda revisar y aprobar el contenido generado antes de publicarlo.
