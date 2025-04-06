# 📊 Modelos de Datos

Este documento describe la estructura de la base de datos de AdFlux, los modelos principales y sus relaciones.

## 🗃️ Visión General

AdFlux utiliza SQLAlchemy como ORM (Object-Relational Mapping) para interactuar con la base de datos. Los modelos están organizados en módulos según su funcionalidad y representan las entidades principales del sistema.

## 📋 Modelos Principales

### JobOpening (Oferta de Trabajo)

Representa una oferta de trabajo publicada en la plataforma.

```python
class JobOpening(db.Model):
    __tablename__ = 'job_openings'
    
    job_id = db.Column(String(50), primary_key=True)  # ej., JOB-0001
    title = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    location = db.Column(String(100), nullable=True)
    company_name = db.Column(String(100), nullable=True)
    required_skills = db.Column(JSON, nullable=True)
    salary_min = db.Column(Integer, nullable=True)
    salary_max = db.Column(Integer, nullable=True)
    posted_date = db.Column(Date, nullable=True)
    status = db.Column(String(50), nullable=True, default='open')
    # ... otros campos
```

**Campos importantes:**
- `job_id`: Identificador único de la oferta de trabajo
- `title`: Título del puesto
- `description`: Descripción detallada del trabajo
- `required_skills`: Habilidades requeridas (almacenadas como JSON)
- `status`: Estado de la oferta (abierta, cerrada, etc.)

**Relaciones:**
- `applications`: Relación uno a muchos con aplicaciones de candidatos
- `campaigns`: Relación uno a muchos con campañas publicitarias
- `candidates`: Relación uno a muchos con candidatos

### Candidate (Candidato)

Representa a una persona que busca empleo y puede aplicar a ofertas de trabajo.

```python
class Candidate(db.Model):
    __tablename__ = 'candidates'
    
    candidate_id = db.Column(String(50), primary_key=True)  # ej., CAND-00001
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(100), nullable=True)
    phone = db.Column(String(20), nullable=True)
    location = db.Column(String(100), nullable=True)
    years_experience = db.Column(Integer, nullable=True)
    education_level = db.Column(String(50), nullable=True)
    skills = db.Column(JSON, nullable=True)
    # ... otros campos
```

**Campos importantes:**
- `candidate_id`: Identificador único del candidato
- `name`: Nombre completo del candidato
- `skills`: Habilidades del candidato (almacenadas como JSON)
- `segment_id`: Segmento asignado por el algoritmo de ML

**Relaciones:**
- `applications`: Relación uno a muchos con aplicaciones a trabajos
- `job`: Relación muchos a uno con ofertas de trabajo
- `segment`: Relación muchos a uno con segmentos

### Application (Aplicación)

Representa la aplicación de un candidato a una oferta de trabajo específica.

```python
class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(Integer, primary_key=True)
    job_id = db.Column(String(50), db.ForeignKey('job_openings.job_id'), nullable=False)
    candidate_id = db.Column(String(50), db.ForeignKey('candidates.candidate_id'), nullable=False)
    application_date = db.Column(DateTime, default=datetime.utcnow)
    status = db.Column(String(50), default='pending')
    # ... otros campos
```

**Campos importantes:**
- `id`: Identificador único de la aplicación
- `job_id`: Referencia a la oferta de trabajo
- `candidate_id`: Referencia al candidato
- `status`: Estado de la aplicación (pendiente, revisada, aceptada, rechazada)

**Relaciones:**
- `job`: Relación muchos a uno con ofertas de trabajo
- `candidate`: Relación muchos a uno con candidatos

### Campaign (Campaña)

Representa una campaña publicitaria para promocionar una oferta de trabajo.

```python
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    platform = db.Column(String(50), nullable=False)  # 'meta', 'google', etc.
    status = db.Column(String(50), nullable=False, default='draft')
    daily_budget = db.Column(Integer, nullable=True)
    job_opening_id = db.Column(String(50), db.ForeignKey('job_openings.job_id'), nullable=True)
    # ... otros campos
```

**Campos importantes:**
- `id`: Identificador único de la campaña
- `platform`: Plataforma donde se publica la campaña (Meta, Google, etc.)
- `status`: Estado de la campaña (borrador, activa, pausada, etc.)
- `job_opening_id`: Referencia a la oferta de trabajo asociada

**Relaciones:**
- `job_opening`: Relación muchos a uno con ofertas de trabajo

### Segment (Segmento)

Representa un grupo de candidatos con características similares, creado por el algoritmo de ML.

```python
class Segment(db.Model):
    __tablename__ = 'segments'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text, nullable=True)
    criteria = db.Column(JSON, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    # ... otros campos
```

**Campos importantes:**
- `id`: Identificador único del segmento
- `name`: Nombre descriptivo del segmento
- `criteria`: Criterios que definen el segmento (almacenados como JSON)

**Relaciones:**
- `candidates`: Relación uno a muchos con candidatos

### Modelos específicos de Meta

#### MetaCampaign

```python
class MetaCampaign(db.Model):
    __tablename__ = 'meta_campaigns'
    
    id = db.Column(Integer, primary_key=True)
    campaign_id = db.Column(String(255), nullable=False, unique=True)
    name = db.Column(String(255), nullable=False)
    status = db.Column(String(50), nullable=False)
    # ... otros campos
```

#### MetaAdSet

```python
class MetaAdSet(db.Model):
    __tablename__ = 'meta_ad_sets'
    
    id = db.Column(Integer, primary_key=True)
    ad_set_id = db.Column(String(255), nullable=False, unique=True)
    campaign_id = db.Column(String(255), db.ForeignKey('meta_campaigns.campaign_id'))
    name = db.Column(String(255), nullable=False)
    # ... otros campos
```

#### MetaAd

```python
class MetaAd(db.Model):
    __tablename__ = 'meta_ads'
    
    id = db.Column(Integer, primary_key=True)
    ad_id = db.Column(String(255), nullable=False, unique=True)
    ad_set_id = db.Column(String(255), db.ForeignKey('meta_ad_sets.ad_set_id'))
    name = db.Column(String(255), nullable=False)
    # ... otros campos
```

#### MetaInsight

```python
class MetaInsight(db.Model):
    __tablename__ = 'meta_insights'
    
    id = db.Column(Integer, primary_key=True)
    object_id = db.Column(String(255), nullable=False)
    object_type = db.Column(String(50), nullable=False)  # 'campaign', 'ad_set', 'ad'
    date = db.Column(Date, nullable=False)
    impressions = db.Column(Integer, nullable=True)
    clicks = db.Column(Integer, nullable=True)
    spend = db.Column(Integer, nullable=True)  # en centavos
    # ... otros campos
```

## 🔄 Relaciones entre Modelos

![Diagrama de Relaciones](https://via.placeholder.com/800x600?text=Diagrama+de+Relaciones+de+Modelos)

### Relaciones Principales:

1. **JobOpening ↔ Candidate**:
   - Un trabajo puede tener muchos candidatos
   - Un candidato puede estar asociado a un trabajo

2. **JobOpening ↔ Application ↔ Candidate**:
   - Un trabajo puede tener muchas aplicaciones
   - Un candidato puede tener muchas aplicaciones
   - Una aplicación pertenece a un trabajo y a un candidato

3. **JobOpening ↔ Campaign**:
   - Un trabajo puede tener muchas campañas
   - Una campaña está asociada a un trabajo

4. **Candidate ↔ Segment**:
   - Un segmento puede contener muchos candidatos
   - Un candidato pertenece a un segmento

5. **Campaign ↔ Modelos Meta**:
   - Una campaña puede estar relacionada con entidades específicas de Meta

## 📝 Migraciones de Base de Datos

AdFlux utiliza Alembic (a través de Flask-Migrate) para gestionar las migraciones de la base de datos. Las migraciones se encuentran en el directorio `migrations/versions/`.

### Migraciones Importantes:

1. **Migración Inicial**: Crea el esquema base de la base de datos.
   - Archivo: `e8c30a0e1c82_initial_schema_based_on_current_models.py`

2. **Adición de IDs Externos**: Agrega campos para almacenar IDs de plataformas externas.
   - Archivo: `a2d2c9206410_add_external_ids_to_campaign_and_remove_.py`

## 🔍 Consideraciones de Diseño

1. **Uso de JSON para Campos Complejos**:
   - Campos como `skills`, `required_skills`, `targeting_spec` se almacenan como JSON para mayor flexibilidad.
   - Esto permite compatibilidad con SQLite durante el desarrollo.

2. **Identificadores Únicos**:
   - Los trabajos y candidatos utilizan identificadores de cadena con prefijos (`JOB-`, `CAND-`) para mayor legibilidad.
   - Las campañas y otras entidades utilizan IDs numéricos autoincrementales.

3. **Relaciones Flexibles**:
   - El diseño permite que un candidato pueda aplicar a múltiples trabajos.
   - Una oferta de trabajo puede tener múltiples campañas en diferentes plataformas.

4. **Auditoría y Seguimiento**:
   - Campos como `created_at` y `updated_at` para seguimiento de cambios.
   - Estados explícitos para seguimiento del ciclo de vida de entidades.

## 🛠️ Uso de los Modelos

### Ejemplo de Creación de Entidades:

```python
# Crear una oferta de trabajo
job = JobOpening(
    job_id="JOB-0001",
    title="Desarrollador Python Senior",
    description="Buscamos un desarrollador Python con experiencia...",
    location="Medellín, Colombia",
    company_name="Magneto365",
    required_skills=["Python", "Flask", "SQLAlchemy", "REST API"]
)
db.session.add(job)

# Crear un candidato
candidate = Candidate(
    candidate_id="CAND-00001",
    name="Juan Pérez",
    email="juan.perez@example.com",
    skills=["Python", "Django", "JavaScript", "React"]
)
db.session.add(candidate)

# Crear una aplicación
application = Application(
    job_id=job.job_id,
    candidate_id=candidate.candidate_id,
    status="pending"
)
db.session.add(application)

db.session.commit()
```

### Ejemplo de Consultas:

```python
# Obtener todas las ofertas de trabajo activas
active_jobs = JobOpening.query.filter_by(status='open').all()

# Obtener candidatos con habilidades específicas (ejemplo simplificado)
python_candidates = Candidate.query.filter(
    Candidate.skills.contains(["Python"])
).all()

# Obtener aplicaciones para un trabajo específico
job_applications = Application.query.filter_by(job_id="JOB-0001").all()

# Obtener campañas activas en Meta
meta_campaigns = Campaign.query.filter_by(
    platform='meta',
    status='active'
).all()
```

## 📈 Escalabilidad y Rendimiento

- **Índices**: Se han definido índices en campos clave para mejorar el rendimiento de las consultas.
- **Lazy Loading**: Las relaciones utilizan `lazy=True` para cargar datos relacionados solo cuando se necesitan.
- **Cascadas**: Se utilizan cascadas para operaciones como eliminación para mantener la integridad referencial.

## 🔒 Seguridad de Datos

- **Validación**: Los modelos incluyen restricciones de integridad a nivel de base de datos.
- **Sanitización**: Los datos se validan y sanitizan antes de almacenarse.
- **Protección de Información Sensible**: Campos sensibles como tokens de API no se almacenan en la base de datos.
