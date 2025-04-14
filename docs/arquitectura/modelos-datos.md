# Modelos de Datos

Este documento describe los modelos de datos utilizados en AdFlux, sus relaciones y estructura.

## Diagrama de Entidad-Relación

El siguiente diagrama muestra las principales entidades del sistema y sus relaciones:

![Diagrama ER](./diagramas/diagrama-er.png)

## Modelos Principales

### User

Representa a los usuarios del sistema.

```python
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    
    # Métodos para gestión de contraseñas
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### Role y Permission

Modelos para el control de acceso basado en roles (RBAC).

```python
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relaciones
    permissions = db.relationship('Permission', secondary='role_permissions', 
                                 backref=db.backref('roles', lazy='dynamic'))

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
```

### JobOpening

Representa una oferta de trabajo.

```python
class JobOpening(db.Model):
    __tablename__ = 'job_openings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    employment_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, CLOSED, DRAFT
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relaciones
    applications = db.relationship('Application', backref='job_opening', lazy='dynamic')
    campaigns = db.relationship('Campaign', backref='job_opening', lazy='dynamic')
```

### Candidate

Representa a un candidato para puestos de trabajo.

```python
class Candidate(db.Model):
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    resume_url = db.Column(db.String(255))
    skills = db.Column(db.JSON)  # Lista de habilidades
    experience = db.Column(db.JSON)  # Experiencia laboral
    education = db.Column(db.JSON)  # Formación académica
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, INACTIVE, HIRED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    applications = db.relationship('Application', backref='candidate', lazy='dynamic')
    
    # Cluster asignado por ML
    cluster_id = db.Column(db.Integer, nullable=True)
```

### Application

Representa una solicitud de un candidato a una oferta de trabajo.

```python
class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_opening_id = db.Column(db.Integer, db.ForeignKey('job_openings.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, REVIEWED, INTERVIEWED, REJECTED, HIRED
    cover_letter = db.Column(db.Text)
    source = db.Column(db.String(50))  # Fuente de la aplicación: META, GOOGLE, DIRECT, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notas y evaluaciones
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5
```

### Campaign

Representa una campaña publicitaria.

```python
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    objective = db.Column(db.String(50), nullable=False)  # AWARENESS, TRAFFIC, CONVERSIONS, etc.
    status = db.Column(db.String(20), default='DRAFT')  # DRAFT, PENDING, ACTIVE, PAUSED, COMPLETED
    platform = db.Column(db.String(20), nullable=False)  # META, GOOGLE, TIKTOK, SNAPCHAT
    daily_budget = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    targeting = db.Column(db.JSON)  # Configuración de segmentación
    ad_creative = db.Column(db.JSON)  # Contenido creativo del anuncio
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    job_opening_id = db.Column(db.Integer, db.ForeignKey('job_openings.id'))
    
    # Relaciones específicas por plataforma
    meta_campaign = db.relationship('MetaCampaign', backref='campaign', uselist=False)
    google_campaign = db.relationship('GoogleCampaign', backref='campaign', uselist=False)
    tiktok_campaign = db.relationship('TikTokCampaign', backref='campaign', uselist=False)
    snapchat_campaign = db.relationship('SnapchatCampaign', backref='campaign', uselist=False)
```

## Modelos Específicos por Plataforma

### Meta (Facebook/Instagram)

```python
class MetaCampaign(db.Model):
    __tablename__ = 'meta_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    external_id = db.Column(db.String(50), nullable=False)  # ID en la API de Meta
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    ad_sets = db.relationship('MetaAdSet', backref='meta_campaign', lazy='dynamic')
    insights = db.relationship('MetaInsight', backref='meta_campaign', lazy='dynamic')

class MetaAdSet(db.Model):
    __tablename__ = 'meta_ad_sets'
    
    id = db.Column(db.Integer, primary_key=True)
    meta_campaign_id = db.Column(db.Integer, db.ForeignKey('meta_campaigns.id'), nullable=False)
    external_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    targeting = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    ads = db.relationship('MetaAd', backref='meta_ad_set', lazy='dynamic')

class MetaAd(db.Model):
    __tablename__ = 'meta_ads'
    
    id = db.Column(db.Integer, primary_key=True)
    meta_ad_set_id = db.Column(db.Integer, db.ForeignKey('meta_ad_sets.id'), nullable=False)
    external_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    creative_id = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MetaInsight(db.Model):
    __tablename__ = 'meta_insights'
    
    id = db.Column(db.Integer, primary_key=True)
    meta_campaign_id = db.Column(db.Integer, db.ForeignKey('meta_campaigns.id'), nullable=False)
    date_start = db.Column(db.Date, nullable=False)
    date_stop = db.Column(db.Date, nullable=False)
    impressions = db.Column(db.Integer)
    clicks = db.Column(db.Integer)
    spend = db.Column(db.Float)
    reach = db.Column(db.Integer)
    cpm = db.Column(db.Float)
    ctr = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Google Ads

```python
class GoogleCampaign(db.Model):
    __tablename__ = 'google_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    external_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    ad_groups = db.relationship('GoogleAdGroup', backref='google_campaign', lazy='dynamic')
    insights = db.relationship('GoogleInsight', backref='google_campaign', lazy='dynamic')
```

## Índices y Optimizaciones

Para mejorar el rendimiento de las consultas, se han definido los siguientes índices:

```python
# Índices para Campaign
__table_args__ = (
    db.Index('ix_campaigns_platform_status', 'platform', 'status'),
    db.Index('ix_campaigns_created_at', 'created_at'),
    db.Index('ix_campaigns_job_opening_id', 'job_opening_id'),
)

# Índices para Application
__table_args__ = (
    db.Index('ix_applications_job_candidate', 'job_opening_id', 'candidate_id'),
    db.Index('ix_applications_status', 'status'),
)

# Índices para MetaInsight
__table_args__ = (
    db.Index('ix_meta_insights_date_campaign_id', 'date_start', 'meta_campaign_id'),
)
```

## Relaciones Polimórficas

Para algunos casos, se utilizan relaciones polimórficas para manejar entidades que pueden estar relacionadas con diferentes tipos de modelos:

```python
class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    
    # Relación polimórfica
    entity_type = db.Column(db.String(50))  # 'job_opening', 'candidate', 'application'
    entity_id = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
```

## Soft Delete

Para algunos modelos, se implementa soft delete para mantener un historial de registros eliminados:

```python
class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def soft_delete(self, user_id):
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
    
    @classmethod
    def not_deleted(cls):
        return cls.query.filter_by(deleted_at=None)
```

## Migraciones

Las migraciones de base de datos se gestionan con Flask-Migrate (Alembic). Cada cambio en los modelos debe ir acompañado de una migración para mantener la consistencia de la base de datos.

## Consideraciones de Rendimiento

- **Lazy Loading vs. Eager Loading**: Las relaciones utilizan lazy loading por defecto, pero se recomienda usar `joinedload()` o `selectinload()` para consultas que necesiten acceder a relaciones para evitar el problema N+1.
- **Paginación**: Para consultas que devuelven muchos resultados, se recomienda usar paginación para limitar el consumo de memoria.
- **Consultas Compuestas**: Utilizar joins y subconsultas para reducir el número de consultas a la base de datos.

## Evolución del Esquema

El esquema de base de datos ha evolucionado a lo largo del tiempo para adaptarse a nuevos requisitos. Los cambios significativos están documentados en las migraciones y en el registro de decisiones de arquitectura.
