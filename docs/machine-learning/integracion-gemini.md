# Integración con Gemini AI

Este documento describe en detalle cómo AdFlux se integra con Gemini AI para generar contenido creativo, optimizar descripciones de trabajo y simular datos para pruebas.

## Contenido

1. [Introducción](#introducción)
2. [Configuración de la Integración](#configuración-de-la-integración)
3. [Cliente de Gemini AI](#cliente-de-gemini-ai)
4. [Casos de Uso](#casos-de-uso)
5. [Diseño de Prompts](#diseño-de-prompts)
6. [Manejo de Respuestas](#manejo-de-respuestas)
7. [Control de Calidad](#control-de-calidad)
8. [Gestión de Costos](#gestión-de-costos)
9. [Mejores Prácticas](#mejores-prácticas)
10. [Solución de Problemas](#solución-de-problemas)

## Introducción

Gemini AI es un modelo de lenguaje grande (LLM) desarrollado por Google que ofrece capacidades avanzadas de generación de texto y comprensión de contexto. AdFlux utiliza Gemini AI para:

1. **Generación de Contenido Creativo**: Crear títulos, descripciones y llamadas a la acción para anuncios de trabajo.
2. **Optimización de Descripciones**: Mejorar las descripciones de puestos de trabajo para hacerlas más atractivas.
3. **Simulación de Datos**: Generar perfiles de candidatos y ofertas de trabajo realistas para pruebas.
4. **Análisis de Texto**: Extraer información relevante de descripciones de trabajo y perfiles de candidatos.

## Configuración de la Integración

### Requisitos Previos

Para integrar Gemini AI en AdFlux, necesitas:

1. **Cuenta de Google AI Studio**: Para acceder a la API de Gemini.
2. **API Key**: Clave de API para autenticar solicitudes.
3. **Python 3.8+**: Para utilizar la biblioteca cliente de Gemini.

### Instalación de Dependencias

```bash
pip install google-generativeai
```

### Configuración de Variables de Entorno

En el archivo `.env`:

```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-pro-exp-03-25
```

## Cliente de Gemini AI

AdFlux implementa un cliente personalizado para interactuar con la API de Gemini:

```python
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiApiClient:
    def __init__(self, api_key=None, model_name=None):
        """
        Inicializa el cliente de la API de Gemini.
        
        Args:
            api_key: Clave de API de Gemini (opcional, por defecto usa la variable de entorno)
            model_name: Nombre del modelo a utilizar (opcional, por defecto usa la variable de entorno)
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.model_name = model_name or os.environ.get('GEMINI_MODEL_NAME', 'gemini-2.5-pro-exp-03-25')
        
        if not self.api_key:
            raise ValueError("Se requiere una clave de API de Gemini. Proporciona api_key o configura GEMINI_API_KEY.")
        
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
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            return response
        except Exception as e:
            logger.error(f"Error al generar contenido con Gemini: {str(e)}")
            raise
```

## Casos de Uso

### 1. Generación de Contenido para Anuncios

```python
def generate_ad_content(job_title, company_name, job_description, platform, format, api_key=None):
    """
    Genera contenido para un anuncio de trabajo.
    
    Args:
        job_title: Título del puesto
        company_name: Nombre de la empresa
        job_description: Descripción del puesto
        platform: Plataforma publicitaria (META, GOOGLE, etc.)
        format: Formato del anuncio (feed, story, etc.)
        api_key: Clave de API de Gemini (opcional)
        
    Returns:
        Diccionario con el contenido generado
    """
    client = GeminiApiClient(api_key=api_key)
    
    prompt = f"""
    Genera contenido creativo para un anuncio de trabajo con las siguientes características:
    
    Puesto: {job_title}
    Empresa: {company_name}
    Descripción: {job_description}
    Plataforma: {platform}
    Formato: {format}
    
    El contenido debe ser persuasivo, atractivo y optimizado para la plataforma {platform}.
    
    Devuelve el resultado en formato JSON con los siguientes campos:
    - headline: Título principal del anuncio (máximo 40 caracteres)
    - description: Descripción del anuncio (máximo 125 caracteres)
    - cta: Llamada a la acción (máximo 20 caracteres)
    
    Solo devuelve el JSON, sin explicaciones adicionales.
    """
    
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

### 2. Optimización de Descripciones de Trabajo

```python
def optimize_job_description(job_description, target_audience, tone="professional", api_key=None):
    """
    Optimiza una descripción de puesto de trabajo.
    
    Args:
        job_description: Descripción original del puesto
        target_audience: Audiencia objetivo (ej. "desarrolladores senior")
        tone: Tono de la descripción (professional, casual, enthusiastic)
        api_key: Clave de API de Gemini (opcional)
        
    Returns:
        Descripción optimizada
    """
    client = GeminiApiClient(api_key=api_key)
    
    prompt = f"""
    Optimiza la siguiente descripción de puesto de trabajo para hacerla más atractiva y efectiva.
    
    Descripción original:
    {job_description}
    
    Audiencia objetivo: {target_audience}
    Tono deseado: {tone}
    
    La descripción optimizada debe:
    1. Ser clara y concisa
    2. Destacar los beneficios para el candidato
    3. Incluir palabras clave relevantes para SEO
    4. Tener un tono {tone}
    5. Ser atractiva para {target_audience}
    
    Devuelve solo la descripción optimizada, sin explicaciones adicionales.
    """
    
    response = client.generate_content(prompt, max_tokens=1000, temperature=0.5)
    
    return response.text
```

### 3. Simulación de Perfiles de Candidatos

```python
def simulate_candidate_profile(job_title, experience_level, location, api_key=None):
    """
    Simula un perfil de candidato realista.
    
    Args:
        job_title: Título del puesto
        experience_level: Nivel de experiencia (junior, mid-level, senior)
        location: Ubicación geográfica
        api_key: Clave de API de Gemini (opcional)
        
    Returns:
        Diccionario con el perfil del candidato
    """
    client = GeminiApiClient(api_key=api_key)
    
    prompt = f"""
    Genera un perfil de candidato realista para un puesto de {job_title} con nivel {experience_level} en {location}.
    
    El perfil debe incluir:
    - Nombre completo
    - Email
    - Teléfono
    - Ubicación
    - Educación (lista de objetos con: degree, field, institution, year)
    - Experiencia laboral (lista de objetos con: title, company, years, description)
    - Habilidades (lista de strings)
    
    Devuelve el resultado en formato JSON, sin explicaciones adicionales.
    """
    
    response = client.generate_content(prompt, max_tokens=1000, temperature=0.8)
    
    # Parsear respuesta JSON
    try:
        profile = json.loads(response.text)
        return profile
    except json.JSONDecodeError:
        # Si la respuesta no es JSON válido, intentar extraer JSON de la respuesta
        match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        if match:
            try:
                profile = json.loads(match.group(1))
                return profile
            except json.JSONDecodeError:
                raise ValueError("No se pudo parsear la respuesta como JSON")
        else:
            raise ValueError("No se pudo parsear la respuesta como JSON")
```

### 4. Análisis de Texto

```python
def extract_job_skills(job_description, api_key=None):
    """
    Extrae habilidades requeridas de una descripción de trabajo.
    
    Args:
        job_description: Descripción del puesto
        api_key: Clave de API de Gemini (opcional)
        
    Returns:
        Lista de habilidades extraídas
    """
    client = GeminiApiClient(api_key=api_key)
    
    prompt = f"""
    Extrae todas las habilidades técnicas y blandas mencionadas en la siguiente descripción de trabajo:
    
    {job_description}
    
    Devuelve el resultado como una lista JSON de strings, donde cada string es una habilidad.
    Solo devuelve el JSON, sin explicaciones adicionales.
    """
    
    response = client.generate_content(prompt, max_tokens=500, temperature=0.3)
    
    # Parsear respuesta JSON
    try:
        skills = json.loads(response.text)
        return skills
    except json.JSONDecodeError:
        # Si la respuesta no es JSON válido, intentar extraer JSON de la respuesta
        match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        if match:
            try:
                skills = json.loads(match.group(1))
                return skills
            except json.JSONDecodeError:
                raise ValueError("No se pudo parsear la respuesta como JSON")
        else:
            raise ValueError("No se pudo parsear la respuesta como JSON")
```

## Diseño de Prompts

El diseño efectivo de prompts es crucial para obtener resultados de alta calidad de Gemini AI. AdFlux sigue estas pautas para el diseño de prompts:

### Estructura de Prompts

```
1. Instrucción clara y específica
2. Contexto relevante
3. Ejemplos (si es necesario)
4. Formato de salida esperado
5. Restricciones o limitaciones
```

### Ejemplos de Prompts Efectivos

#### Para Generación de Anuncios

```
Genera contenido creativo para un anuncio de trabajo en Meta (feed) con las siguientes características:

Puesto: Desarrollador Full Stack
Empresa: TechInnovate
Ubicación: Madrid, España
Tipo de empleo: Tiempo completo

Descripción breve:
Buscamos un Desarrollador Full Stack con experiencia en React y Node.js para unirse a nuestro equipo de desarrollo de productos. Trabajarás en proyectos innovadores y desafiantes en un ambiente colaborativo.

Requisitos principales:
- 3+ años de experiencia con React y Node.js
- Conocimiento de bases de datos SQL y NoSQL
- Experiencia con metodologías ágiles

Beneficios: Horario flexible, trabajo remoto, plan de carrera, seguro médico
Rango salarial: 45,000€-60,000€

Audiencia objetivo: Desarrolladores con experiencia media-senior en Madrid o remotos

El contenido debe ser persuasivo, atractivo y optimizado para Meta feed.

Devuelve el resultado en formato JSON con los siguientes campos:
- headline: Título principal del anuncio (máximo 40 caracteres)
- primary_text: Texto principal del anuncio (máximo 125 caracteres)
- description: Descripción adicional (máximo 30 caracteres)
- cta: Llamada a la acción (una de las siguientes: APPLY_NOW, LEARN_MORE, SIGN_UP, CONTACT_US)

Solo devuelve el JSON, sin explicaciones adicionales.
```

#### Para Optimización de Descripciones

```
Optimiza la siguiente descripción de puesto de trabajo para hacerla más atractiva y efectiva.

Descripción original:
Buscamos un analista de datos para unirse a nuestro equipo. El candidato debe tener experiencia en SQL, Python y visualización de datos. Responsabilidades incluyen análisis de datos, creación de informes y colaboración con otros equipos. Se requiere licenciatura en campo relacionado.

Audiencia objetivo: Analistas de datos con 2-5 años de experiencia
Tono deseado: professional

La descripción optimizada debe:
1. Ser clara y concisa
2. Destacar los beneficios para el candidato
3. Incluir palabras clave relevantes para SEO
4. Tener un tono professional
5. Ser atractiva para analistas de datos con 2-5 años de experiencia

Devuelve solo la descripción optimizada, sin explicaciones adicionales.
```

### Ajuste de Parámetros

AdFlux ajusta los parámetros de generación según el caso de uso:

| Caso de Uso | Temperature | Top-p | Top-k | Max Tokens |
|-------------|------------|-------|-------|------------|
| Anuncios | 0.7 | 0.95 | 40 | 500 |
| Descripciones | 0.5 | 0.95 | 40 | 1000 |
| Simulación | 0.8 | 0.95 | 40 | 1000 |
| Análisis | 0.3 | 0.95 | 40 | 500 |

## Manejo de Respuestas

AdFlux implementa un manejo robusto de las respuestas de Gemini AI:

### Parsing de JSON

```python
def parse_gemini_json_response(response_text):
    """
    Parsea una respuesta JSON de Gemini.
    
    Args:
        response_text: Texto de respuesta de Gemini
        
    Returns:
        Objeto JSON parseado
    """
    # Intentar parsear directamente
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Intentar extraer JSON de bloques de código
        match = re.search(r'```(?:json)?\n(.*?)\n```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Intentar extraer JSON sin formato de código
        match = re.search(r'({.*})', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Si todo falla, lanzar error
        raise ValueError(f"No se pudo parsear la respuesta como JSON: {response_text[:100]}...")
```

### Manejo de Errores

```python
def handle_gemini_api_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except genai.types.generation_types.BlockedPromptException as e:
                # Error de seguridad, no reintentar
                logger.error(f"Gemini API blocked prompt: {str(e)}")
                raise GeminiSafetyError(f"Prompt blocked by safety filters: {str(e)}")
            
            except genai.types.generation_types.StopCandidateException as e:
                # Generación detenida, no reintentar
                logger.error(f"Gemini API stopped generation: {str(e)}")
                raise GeminiGenerationError(f"Generation stopped: {str(e)}")
            
            except (genai.types.generation_types.GenerationException, 
                   genai.types.generation_types.InternalServerException) as e:
                if attempt < max_retries - 1:
                    # Error transitorio, reintentar
                    logger.warning(f"Gemini API error (attempt {attempt+1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay * (2 ** attempt))  # Backoff exponencial
                    continue
                
                logger.error(f"Gemini API error after {max_retries} attempts: {str(e)}")
                raise GeminiApiError(f"API error: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise
    
    return wrapper
```

## Control de Calidad

AdFlux implementa varias medidas para garantizar la calidad del contenido generado por Gemini AI:

### Validación de Contenido

```python
def validate_generated_content(content, content_type):
    """
    Valida el contenido generado.
    
    Args:
        content: Contenido generado
        content_type: Tipo de contenido (ad, description, profile)
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if content_type == 'ad':
        # Validar anuncio
        if 'headline' not in content:
            return False, "Falta el título del anuncio"
        
        if len(content['headline']) > 40:
            return False, f"Título demasiado largo: {len(content['headline'])} caracteres (máximo 40)"
        
        if 'description' not in content:
            return False, "Falta la descripción del anuncio"
        
        if len(content['description']) > 125:
            return False, f"Descripción demasiado larga: {len(content['description'])} caracteres (máximo 125)"
        
        if 'cta' not in content:
            return False, "Falta la llamada a la acción"
        
        valid_ctas = ['APPLY_NOW', 'LEARN_MORE', 'SIGN_UP', 'CONTACT_US']
        if content['cta'] not in valid_ctas:
            return False, f"CTA no válida: {content['cta']}. Debe ser una de: {', '.join(valid_ctas)}"
    
    elif content_type == 'description':
        # Validar descripción
        if not content or len(content) < 100:
            return False, "Descripción demasiado corta"
        
        if len(content) > 5000:
            return False, "Descripción demasiado larga"
    
    elif content_type == 'profile':
        # Validar perfil
        required_fields = ['name', 'email', 'skills', 'experience']
        for field in required_fields:
            if field not in content:
                return False, f"Falta el campo requerido: {field}"
        
        if not isinstance(content.get('skills', []), list):
            return False, "El campo 'skills' debe ser una lista"
        
        if not isinstance(content.get('experience', []), list):
            return False, "El campo 'experience' debe ser una lista"
    
    return True, ""
```

### Detección de Contenido Inapropiado

```python
def detect_inappropriate_content(text):
    """
    Detecta contenido inapropiado en el texto generado.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Tupla (contiene_inapropiado, razón)
    """
    # Lista de términos inapropiados
    inappropriate_terms = [
        # Discriminación
        'solo hombres', 'solo mujeres', 'jóvenes', 'mayores',
        # Lenguaje ofensivo
        'estúpido', 'idiota', 'tonto',
        # Términos políticos o religiosos
        'conservador', 'liberal', 'cristiano', 'musulmán', 'judío'
    ]
    
    # Verificar términos inapropiados
    text_lower = text.lower()
    for term in inappropriate_terms:
        if term in text_lower:
            return True, f"Contiene término inapropiado: '{term}'"
    
    # Verificar patrones de discriminación por edad
    age_patterns = [
        r'\b\d{2}\s*-\s*\d{2}\s*años\b',
        r'\bmenor\s*de\s*\d{2}\b',
        r'\bmayor\s*de\s*\d{2}\b'
    ]
    
    for pattern in age_patterns:
        if re.search(pattern, text_lower):
            return True, "Contiene posible discriminación por edad"
    
    return False, ""
```

## Gestión de Costos

AdFlux implementa estrategias para optimizar el uso de la API de Gemini y controlar los costos:

### Caché de Respuestas

```python
def get_cached_or_generate(cache_key, generation_func, *args, **kwargs):
    """
    Obtiene una respuesta cacheada o genera una nueva.
    
    Args:
        cache_key: Clave de caché
        generation_func: Función de generación
        *args, **kwargs: Argumentos para la función de generación
        
    Returns:
        Respuesta generada o cacheada
    """
    # Verificar caché
    cached_response = cache.get(cache_key)
    if cached_response:
        logger.info(f"Usando respuesta cacheada para {cache_key}")
        return cached_response
    
    # Generar nueva respuesta
    response = generation_func(*args, **kwargs)
    
    # Guardar en caché
    cache.set(cache_key, response, timeout=3600 * 24 * 7)  # 1 semana
    
    return response
```

### Monitoreo de Uso

```python
def log_gemini_api_usage(prompt_tokens, completion_tokens, model_name):
    """
    Registra el uso de la API de Gemini.
    
    Args:
        prompt_tokens: Número de tokens en el prompt
        completion_tokens: Número de tokens en la respuesta
        model_name: Nombre del modelo utilizado
    """
    # Calcular costo aproximado
    # Nota: Estos valores son ejemplos y deben actualizarse según los precios reales
    cost_per_1k_prompt_tokens = 0.0005  # $0.0005 por 1K tokens de prompt
    cost_per_1k_completion_tokens = 0.0015  # $0.0015 por 1K tokens de respuesta
    
    prompt_cost = (prompt_tokens / 1000) * cost_per_1k_prompt_tokens
    completion_cost = (completion_tokens / 1000) * cost_per_1k_completion_tokens
    total_cost = prompt_cost + completion_cost
    
    # Registrar uso
    usage_log = GeminiUsageLog(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        model=model_name,
        estimated_cost=total_cost,
        timestamp=datetime.utcnow()
    )
    
    db.session.add(usage_log)
    db.session.commit()
    
    # Actualizar contadores diarios
    today = datetime.utcnow().date()
    daily_usage = GeminiDailyUsage.query.filter_by(date=today).first()
    
    if daily_usage:
        daily_usage.prompt_tokens += prompt_tokens
        daily_usage.completion_tokens += completion_tokens
        daily_usage.total_tokens += prompt_tokens + completion_tokens
        daily_usage.estimated_cost += total_cost
    else:
        daily_usage = GeminiDailyUsage(
            date=today,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=total_cost
        )
        db.session.add(daily_usage)
    
    db.session.commit()
```

## Mejores Prácticas

Para obtener los mejores resultados con la integración de Gemini AI:

1. **Prompts Específicos**: Proporciona instrucciones claras y específicas en los prompts.
2. **Contexto Relevante**: Incluye suficiente contexto para que el modelo comprenda la tarea.
3. **Formato Estructurado**: Solicita respuestas en formatos estructurados como JSON para facilitar el procesamiento.
4. **Caché Inteligente**: Implementa caché para respuestas que no cambian frecuentemente.
5. **Manejo de Errores**: Implementa un manejo robusto de errores con reintentos para errores transitorios.
6. **Validación de Salida**: Valida siempre la salida del modelo antes de utilizarla.
7. **Monitoreo de Costos**: Monitorea y optimiza el uso de la API para controlar los costos.

## Solución de Problemas

### Problemas Comunes y Soluciones

#### Respuestas No Estructuradas

**Problema**: Gemini no devuelve el formato JSON solicitado.

**Solución**:
- Especifica claramente el formato esperado en el prompt.
- Utiliza ejemplos para mostrar el formato deseado.
- Implementa parsers robustos que puedan extraer JSON de respuestas no estructuradas.

#### Contenido Bloqueado

**Problema**: El prompt es bloqueado por los filtros de seguridad de Gemini.

**Solución**:
- Revisa el prompt para eliminar contenido que pueda activar los filtros.
- Reformula el prompt de manera más neutral.
- Divide prompts complejos en partes más pequeñas y específicas.

#### Respuestas Inconsistentes

**Problema**: Gemini genera respuestas diferentes para el mismo prompt.

**Solución**:
- Reduce la temperatura para obtener respuestas más deterministas.
- Utiliza un sistema de semillas para mantener la consistencia.
- Implementa validación y post-procesamiento para normalizar las respuestas.

#### Límites de Tokens

**Problema**: El prompt o la respuesta exceden los límites de tokens.

**Solución**:
- Acorta los prompts eliminando información no esencial.
- Divide tareas grandes en subtareas más pequeñas.
- Implementa truncamiento inteligente para respuestas largas.

#### Errores de API

**Problema**: La API de Gemini devuelve errores.

**Solución**:
- Implementa reintentos con backoff exponencial para errores transitorios.
- Monitorea el estado de la API y reduce la carga durante interrupciones.
- Mantén un sistema de fallback para funcionalidades críticas.
