# 🔄 Simulación de Datos

Este documento describe el módulo de simulación de datos de AdFlux, que permite generar datos realistas para pruebas y desarrollo sin depender de datos reales de producción.

## 🎯 Objetivo

El objetivo principal del módulo de simulación es proporcionar un conjunto de datos realista y coherente para:

1. **Desarrollo y pruebas** sin necesidad de datos reales
2. **Demostración** de las funcionalidades de AdFlux
3. **Entrenamiento** de los modelos de machine learning
4. **Pruebas de carga** para evaluar el rendimiento del sistema

## 🧩 Componentes Principales

### 1. Generación de Ofertas de Trabajo

El módulo `job_data.py` contiene funciones para generar datos simulados de ofertas de trabajo:

```python
def generate_job_opening(job_id: int) -> Optional[Dict[str, Any]]:
    """
    Genera datos simulados para una oferta de trabajo utilizando Gemini.
    
    Args:
        job_id: ID único para la oferta de trabajo.
        
    Returns:
        Dict o None: Datos de la oferta de trabajo como diccionario, o None si ocurre un error.
    """
    # Asegurar que el cliente de Gemini esté configurado
    if not setup_gemini_client():
        log.error("No se pudo configurar el cliente de Gemini para generar datos de trabajo.")
        return None
    
    # Prompt para Gemini
    prompt = f"""
    Eres un asistente especializado en recursos humanos. Tu tarea es generar datos realistas para una oferta de trabajo en Colombia.
    
    Genera un objeto JSON con los siguientes campos:
    - job_id: "JOB-{job_id:04d}" (string)
    - title: título del puesto (string)
    - description: descripción detallada del trabajo (string, al menos 200 palabras)
    - location: ciudad en Colombia (string)
    - company_name: nombre de empresa colombiana (string)
    - required_skills: lista de habilidades requeridas (array de strings, al menos 5 habilidades)
    - salary_min: salario mínimo en pesos colombianos (entero entre 1,000,000 y 5,000,000)
    - salary_max: salario máximo en pesos colombianos (entero entre el salario mínimo y 15,000,000)
    - employment_type: tipo de empleo (string: "Full-time", "Part-time", "Contract", "Temporary", "Internship")
    - experience_level: nivel de experiencia (string: "Entry-level", "Mid-level", "Senior", "Executive")
    - education_level: nivel educativo requerido (string: "High School", "Technical", "Bachelor's", "Master's", "PhD")
    - department: departamento de la empresa (string)
    - remote: si es trabajo remoto (booleano)
    - benefits: lista de beneficios (array de strings)
    
    Asegúrate de que los datos sean coherentes entre sí. Por ejemplo, si el título es "Desarrollador Senior", la experiencia debería ser "Senior" y las habilidades deberían incluir tecnologías de desarrollo.
    """
    
    # Generar datos con Gemini
    try:
        response = generate_with_gemini(prompt)
        job_data = json.loads(response)
        
        # Validar y ajustar datos
        if not job_data.get('job_id'):
            job_data['job_id'] = f"JOB-{job_id:04d}"
            
        # Convertir fechas si es necesario
        if 'posted_date' in job_data and isinstance(job_data['posted_date'], str):
            try:
                job_data['posted_date'] = datetime.strptime(job_data['posted_date'], '%Y-%m-%d').date()
            except ValueError:
                job_data['posted_date'] = datetime.now().date()
                
        # Asegurar que salary_max > salary_min
        if 'salary_min' in job_data and 'salary_max' in job_data:
            if job_data['salary_min'] > job_data['salary_max']:
                job_data['salary_max'] = job_data['salary_min'] * 1.5
                
        return job_data
        
    except Exception as e:
        log.error(f"Error al generar datos de trabajo con Gemini: {str(e)}")
        return None
```

### 2. Generación de Perfiles de Candidatos

El módulo `candidate_data.py` contiene funciones para generar datos simulados de perfiles de candidatos:

```python
def generate_candidate_profile(candidate_id: int) -> Optional[Dict[str, Any]]:
    """
    Genera datos simulados para un perfil de candidato utilizando Gemini.
    
    Args:
        candidate_id: ID único para el candidato.
        
    Returns:
        Dict o None: Datos del perfil de candidato como diccionario, o None si ocurre un error.
    """
    # Asegurar que el cliente de Gemini esté configurado
    if not setup_gemini_client():
        log.error("No se pudo configurar el cliente de Gemini para generar datos de candidato.")
        return None
    
    # Prompt para Gemini
    prompt = f"""
    Eres un asistente especializado en recursos humanos. Tu tarea es generar datos realistas para un perfil de candidato de trabajo en Colombia.
    
    Genera un objeto JSON con los siguientes campos:
    - candidate_id: "CAND-{candidate_id:05d}" (string)
    - name: nombre completo colombiano realista (string)
    - email: email ficticio basado en el nombre (string)
    - phone: número de teléfono colombiano ficticio (string)
    - location: ciudad en Colombia (string)
    - years_experience: años de experiencia laboral (entero entre 0 y 25)
    - education_level: nivel educativo (string: "High School", "Technical", "Bachelor's", "Master's", "PhD")
    - skills: lista de habilidades profesionales (array de strings, al menos 5 habilidades)
    - primary_skill: habilidad principal, debe ser una de las listadas en skills (string)
    - desired_salary: salario deseado en pesos colombianos (entero entre 1,000,000 y 15,000,000)
    - desired_position: puesto deseado (string)
    - summary: breve resumen profesional (string)
    - availability: disponibilidad (string: "Immediate", "2 weeks", "1 month", "3 months")
    - languages: lista de idiomas y niveles (array de objetos con "language" y "level")
    
    Asegúrate de que los datos sean coherentes entre sí. Por ejemplo, si el candidato tiene 0-2 años de experiencia, su nivel educativo debería ser acorde y su salario deseado no debería ser demasiado alto.
    """
    
    # Generar datos con Gemini
    try:
        response = generate_with_gemini(prompt)
        candidate_data = json.loads(response)
        
        # Validar y ajustar datos
        if not candidate_data.get('candidate_id'):
            candidate_data['candidate_id'] = f"CAND-{candidate_id:05d}"
            
        # Asegurar que primary_skill esté en skills
        if 'primary_skill' in candidate_data and 'skills' in candidate_data:
            if candidate_data['primary_skill'] not in candidate_data['skills']:
                if candidate_data['skills']:
                    candidate_data['primary_skill'] = candidate_data['skills'][0]
                else:
                    candidate_data['skills'] = [candidate_data['primary_skill']]
                    
        return candidate_data
        
    except Exception as e:
        log.error(f"Error al generar datos de candidato con Gemini: {str(e)}")
        return None
```

### 3. Generación de Aplicaciones

El módulo `application_data.py` contiene funciones para generar datos simulados de aplicaciones de candidatos a ofertas de trabajo:

```python
def generate_applications(count: int) -> List[Dict[str, Any]]:
    """
    Genera datos simulados para aplicaciones de candidatos a ofertas de trabajo.
    
    Args:
        count: Número de aplicaciones a generar.
        
    Returns:
        Lista de diccionarios con datos de aplicaciones.
    """
    from ..models import JobOpening, Candidate
    
    # Obtener trabajos y candidatos existentes
    jobs = JobOpening.query.all()
    candidates = Candidate.query.all()
    
    if not jobs or not candidates:
        log.error("No hay trabajos o candidatos en la base de datos para generar aplicaciones.")
        return []
    
    applications = []
    existing_pairs = set()
    
    # Generar aplicaciones únicas (un candidato no puede aplicar dos veces al mismo trabajo)
    for _ in range(min(count, len(jobs) * len(candidates))):
        # Seleccionar trabajo y candidato aleatorios
        job = random.choice(jobs)
        candidate = random.choice(candidates)
        
        # Verificar que esta combinación no exista ya
        pair = (job.job_id, candidate.candidate_id)
        if pair in existing_pairs:
            continue
        
        existing_pairs.add(pair)
        
        # Generar fecha de aplicación (entre la fecha de publicación del trabajo y hoy)
        if job.posted_date:
            min_date = job.posted_date
        else:
            min_date = datetime.now().date() - timedelta(days=30)
            
        max_date = datetime.now().date()
        days_diff = (max_date - min_date).days
        random_days = random.randint(0, max(0, days_diff))
        application_date = min_date + timedelta(days=random_days)
        
        # Generar estado de la aplicación
        status_options = ['pending', 'reviewed', 'interview', 'offer', 'rejected', 'hired']
        status_weights = [0.3, 0.25, 0.2, 0.1, 0.1, 0.05]  # Más probabilidad de estar pendiente o en revisión
        status = random.choices(status_options, weights=status_weights, k=1)[0]
        
        # Crear aplicación
        application = {
            'job_id': job.job_id,
            'candidate_id': candidate.candidate_id,
            'application_date': application_date,
            'status': status,
            'cover_letter': generate_cover_letter(candidate, job) if random.random() > 0.3 else None
        }
        
        applications.append(application)
    
    return applications
```

### 4. Utilidades de Simulación

El módulo `utils.py` contiene funciones de utilidad para la generación de datos:

```python
def setup_gemini_client() -> bool:
    """
    Configura el cliente de Gemini para la generación de datos.
    
    Returns:
        bool: True si la configuración fue exitosa, False en caso contrario.
    """
    from ..api.gemini.client import GeminiApiClient
    
    client = GeminiApiClient()
    return client.initialize()

def generate_with_gemini(prompt: str) -> str:
    """
    Genera texto utilizando la API de Gemini.
    
    Args:
        prompt: Prompt para Gemini.
        
    Returns:
        str: Texto generado por Gemini.
        
    Raises:
        Exception: Si ocurre un error al generar el texto.
    """
    from ..api.gemini.client import GeminiApiClient
    
    client = GeminiApiClient()
    if not client.initialized:
        client.initialize()
        
    response = client.generate_text(prompt)
    return response
```

### 5. Reinicio de Base de Datos

El módulo `db_reset.py` contiene funciones para reiniciar la base de datos y poblarla con datos simulados:

```python
def reset_database():
    """
    Elimina todas las tablas de la base de datos y las vuelve a crear.
    """
    from ..models import db, create_tables
    
    db.drop_all()
    create_tables()
    
def populate_database(jobs_count=10, candidates_count=50, applications_count=30):
    """
    Puebla la base de datos con datos simulados.
    
    Args:
        jobs_count: Número de ofertas de trabajo a generar.
        candidates_count: Número de candidatos a generar.
        applications_count: Número de aplicaciones a generar.
    """
    from ..models import db, JobOpening, Candidate, Application
    from .job_data import generate_job_openings
    from .candidate_data import generate_candidate_profiles
    from .application_data import generate_applications
    
    # Generar ofertas de trabajo
    jobs_data = generate_job_openings(jobs_count)
    for job_data in jobs_data:
        job = JobOpening(**job_data)
        db.session.add(job)
    
    db.session.commit()
    
    # Generar candidatos
    candidates_data = generate_candidate_profiles(candidates_count)
    for candidate_data in candidates_data:
        candidate = Candidate(**candidate_data)
        db.session.add(candidate)
    
    db.session.commit()
    
    # Generar aplicaciones
    applications_data = generate_applications(applications_count)
    for app_data in applications_data:
        application = Application(**app_data)
        db.session.add(application)
    
    db.session.commit()
```

## 🔄 Flujo de Trabajo

### 1. Configuración del Cliente Gemini

```python
def setup_gemini_client():
    """Configura el cliente de Gemini para la generación de datos."""
    from adflux.api.gemini.client import GeminiApiClient
    
    client = GeminiApiClient()
    success = client.initialize()
    
    if not success:
        print("Error: No se pudo inicializar el cliente de Gemini.")
        print("Asegúrate de tener configurada la variable de entorno GEMINI_API_KEY.")
        return False
        
    return True
```

### 2. Generación de Datos

```python
# Generar ofertas de trabajo
jobs_data = []
for i in range(1, jobs_count + 1):
    job_data = generate_job_opening(i)
    if job_data:
        jobs_data.append(job_data)
        print(f"Generado trabajo {i}/{jobs_count}: {job_data['title']}")
    else:
        print(f"Error al generar trabajo {i}/{jobs_count}")

# Generar candidatos
candidates_data = []
for i in range(1, candidates_count + 1):
    candidate_data = generate_candidate_profile(i)
    if candidate_data:
        candidates_data.append(candidate_data)
        print(f"Generado candidato {i}/{candidates_count}: {candidate_data['name']}")
    else:
        print(f"Error al generar candidato {i}/{candidates_count}")
```

### 3. Almacenamiento en Base de Datos

```python
# Guardar ofertas de trabajo en la base de datos
for job_data in jobs_data:
    job = JobOpening(**job_data)
    db.session.add(job)

db.session.commit()
print(f"Guardados {len(jobs_data)} trabajos en la base de datos.")

# Guardar candidatos en la base de datos
for candidate_data in candidates_data:
    candidate = Candidate(**candidate_data)
    db.session.add(candidate)

db.session.commit()
print(f"Guardados {len(candidates_data)} candidatos en la base de datos.")
```

## 🛠️ Comandos CLI

AdFlux incluye comandos CLI para gestionar la simulación de datos:

```python
@click.command('generate-jobs')
@click.argument('count', type=int)
@with_appcontext
def generate_jobs_command(count):
    """Genera y guarda ofertas de trabajo simuladas."""
    from adflux.simulation.job_data import generate_job_openings
    from adflux.models import db, JobOpening
    
    click.echo(f"Generando {count} ofertas de trabajo simuladas...")
    
    jobs_data = generate_job_openings(count)
    
    for job_data in jobs_data:
        job = JobOpening(**job_data)
        db.session.add(job)
    
    db.session.commit()
    click.echo(f"Se han generado y guardado {len(jobs_data)} ofertas de trabajo.")

@click.command('generate-candidates')
@click.argument('count', type=int)
@with_appcontext
def generate_candidates_command(count):
    """Genera y guarda perfiles de candidatos simulados."""
    # Implementación similar...

@click.command('generate-applications')
@click.argument('count', type=int)
@with_appcontext
def generate_applications_command(count):
    """Genera y guarda aplicaciones simuladas."""
    # Implementación similar...

@click.command('reset-db')
@click.option('--yes', is_flag=True, help='Confirmar sin preguntar')
@with_appcontext
def reset_db_command(yes):
    """Reinicia la base de datos y la puebla con datos simulados."""
    if not yes:
        click.confirm('¿Estás seguro de que quieres reiniciar la base de datos? Todos los datos existentes se perderán.', abort=True)
    
    from adflux.simulation.db_reset import reset_database, populate_database
    
    click.echo("Reiniciando base de datos...")
    reset_database()
    
    click.echo("Poblando base de datos con datos simulados...")
    populate_database(jobs_count=10, candidates_count=50, applications_count=30)
    
    click.echo("Base de datos reiniciada y poblada con éxito.")
```

## 🧠 Integración con Gemini AI

La simulación de datos utiliza la API de Gemini AI para generar contenido realista:

### Configuración de Gemini

```python
def setup_gemini_client():
    """Configura el cliente de Gemini para la generación de datos."""
    from adflux.api.gemini.client import GeminiApiClient
    
    client = GeminiApiClient()
    return client.initialize()
```

### Generación de Texto con Gemini

```python
def generate_with_gemini(prompt):
    """Genera texto utilizando la API de Gemini."""
    from adflux.api.gemini.client import GeminiApiClient
    
    client = GeminiApiClient()
    if not client.initialized:
        client.initialize()
        
    return client.generate_text(prompt)
```

### Ejemplos de Prompts para Gemini

#### Prompt para Generar Oferta de Trabajo

```
Eres un asistente especializado en recursos humanos. Tu tarea es generar datos realistas para una oferta de trabajo en Colombia.

Genera un objeto JSON con los siguientes campos:
- job_id: "JOB-0001" (string)
- title: título del puesto (string)
- description: descripción detallada del trabajo (string, al menos 200 palabras)
- location: ciudad en Colombia (string)
- company_name: nombre de empresa colombiana (string)
- required_skills: lista de habilidades requeridas (array de strings, al menos 5 habilidades)
- salary_min: salario mínimo en pesos colombianos (entero entre 1,000,000 y 5,000,000)
- salary_max: salario máximo en pesos colombianos (entero entre el salario mínimo y 15,000,000)
...
```

#### Prompt para Generar Perfil de Candidato

```
Eres un asistente especializado en recursos humanos. Tu tarea es generar datos realistas para un perfil de candidato de trabajo en Colombia.

Genera un objeto JSON con los siguientes campos:
- candidate_id: "CAND-00001" (string)
- name: nombre completo colombiano realista (string)
- email: email ficticio basado en el nombre (string)
- phone: número de teléfono colombiano ficticio (string)
- location: ciudad en Colombia (string)
- years_experience: años de experiencia laboral (entero entre 0 y 25)
...
```

## 🔍 Consideraciones Técnicas

### Coherencia de Datos

- Se implementan validaciones para asegurar que los datos generados sean coherentes entre sí
- Se ajustan automáticamente valores inconsistentes (por ejemplo, si el salario mínimo es mayor que el máximo)

### Manejo de Errores

- Reintentos automáticos en caso de fallos en la API de Gemini
- Fallback a generación aleatoria simple si Gemini no está disponible

### Rendimiento

- Generación en lotes para mejorar el rendimiento
- Caché de respuestas de Gemini para evitar llamadas repetidas

### Personalización

- Parámetros configurables para controlar la cantidad y tipo de datos generados
- Posibilidad de especificar semillas aleatorias para reproducibilidad

## 🔮 Mejoras Futuras

1. **Generación de Datos Más Específicos**:
   - Perfiles de candidatos por industria o especialidad
   - Ofertas de trabajo para sectores específicos

2. **Datos Relacionados**:
   - Generación de historiales laborales completos para candidatos
   - Generación de procesos de selección completos

3. **Datos para Pruebas de Rendimiento**:
   - Generación de conjuntos de datos masivos para pruebas de carga
   - Simulación de patrones de uso realistas

4. **Integración con Otras Fuentes**:
   - Uso de datos públicos para mejorar el realismo
   - Integración con APIs de información laboral

5. **Interfaz de Usuario**:
   - Panel de control para la generación de datos
   - Visualización de datos generados
