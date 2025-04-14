# Gemini API - Visión General

AdFlux se integra con la API de Gemini AI para generar contenido creativo para anuncios y simular datos para pruebas. Esta página proporciona una visión general de la integración.

## Introducción

Gemini AI es un modelo de lenguaje grande (LLM) desarrollado por Google. AdFlux utiliza la API de Gemini para:

1. Generar contenido creativo para anuncios de trabajo
2. Optimizar descripciones de puestos de trabajo
3. Simular perfiles de candidatos para pruebas
4. Simular ofertas de trabajo para pruebas

## Versión del Modelo

AdFlux utiliza el modelo `gemini-2.5-pro-exp-03-25`, que ofrece un buen equilibrio entre calidad y rendimiento para las tareas requeridas.

## Autenticación

La autenticación con la API de Gemini se realiza mediante una clave de API. 

### Requisitos

Para utilizar la API de Gemini, se necesita:

- **API Key**: Clave de API de Gemini AI.

### Configuración

La clave de API se configura en el archivo `.env`:

```
GEMINI_API_KEY=your_api_key
```

## Cliente de la API

AdFlux implementa un cliente personalizado para la API de Gemini en `adflux/gemini/client.py`:

```python
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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

## Estructura de la Integración

La integración con la API de Gemini está organizada en módulos:

- **client.py**: Cliente base para la API.
- **generation.py**: Funciones para generar contenido.
- **simulation.py**: Funciones para simular datos.
- **utils.py**: Utilidades comunes.

## Casos de Uso

### Generación de Contenido para Anuncios

AdFlux utiliza Gemini para generar contenido creativo para anuncios de trabajo, incluyendo:

- Títulos atractivos
- Descripciones persuasivas
- Llamadas a la acción efectivas

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

### Optimización de Descripciones de Puestos

AdFlux utiliza Gemini para optimizar descripciones de puestos de trabajo, haciéndolas más atractivas y efectivas:

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

### Simulación de Datos para Pruebas

AdFlux utiliza Gemini para simular datos realistas para pruebas, incluyendo perfiles de candidatos y ofertas de trabajo:

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

## Manejo de Errores

La integración con Gemini incluye manejo de errores para diferentes situaciones:

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

## Limitaciones y Consideraciones

- **Límites de Tasa**: La API de Gemini tiene límites de tasa que varían según el plan.
- **Costos**: El uso de la API de Gemini tiene costos asociados basados en el número de tokens.
- **Calidad de las Respuestas**: La calidad de las respuestas puede variar, por lo que es importante validar y filtrar el contenido generado.
- **Sesgo y Equidad**: Los modelos de lenguaje pueden reflejar sesgos presentes en los datos de entrenamiento, por lo que es importante revisar el contenido generado.

## Mejores Prácticas

1. **Prompts Específicos**: Proporcionar prompts claros y específicos para obtener mejores resultados.
2. **Validación de Salida**: Validar siempre la salida del modelo antes de utilizarla.
3. **Control de Temperatura**: Ajustar la temperatura según la tarea (valores más bajos para tareas más deterministas, valores más altos para tareas creativas).
4. **Manejo de Errores**: Implementar un manejo robusto de errores con reintentos para errores transitorios.
5. **Caché**: Implementar caché para respuestas frecuentes para reducir costos y mejorar el rendimiento.

## Recursos Adicionales

- [Documentación oficial de la API de Gemini](https://ai.google.dev/docs)
- [Guía de mejores prácticas para prompts](https://ai.google.dev/docs/prompting)
- [Políticas de uso de Gemini AI](https://ai.google.dev/docs/safety_guidance)
