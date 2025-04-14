# Simulación de Datos

Este documento describe cómo AdFlux utiliza técnicas de simulación y generación de datos sintéticos para pruebas, desarrollo y entrenamiento de modelos.

## Contenido

1. [Introducción](#introducción)
2. [Simulación de Ofertas de Trabajo](#simulación-de-ofertas-de-trabajo)
3. [Simulación de Perfiles de Candidatos](#simulación-de-perfiles-de-candidatos)
4. [Simulación de Campañas](#simulación-de-campañas)
5. [Simulación de Métricas](#simulación-de-métricas)
6. [Uso en Pruebas](#uso-en-pruebas)
7. [Uso en Desarrollo](#uso-en-desarrollo)

## Introducción

La simulación de datos es un componente clave en AdFlux que permite generar datos realistas para:

- Desarrollo y prueba de nuevas funcionalidades
- Entrenamiento de modelos de machine learning
- Demostración de la plataforma
- Pruebas de rendimiento y escalabilidad

AdFlux utiliza una combinación de técnicas estadísticas y generación basada en IA para crear datos sintéticos que reflejan las características del mundo real.

## Simulación de Ofertas de Trabajo

AdFlux puede generar ofertas de trabajo realistas utilizando Gemini AI:

```python
def simulate_job_opening(industry=None, company_size=None, location=None, api_key=None):
    """
    Simula una oferta de trabajo realista.
    
    Args:
        industry: Industria (Technology, Healthcare, Finance, etc.)
        company_size: Tamaño de la empresa (Small, Medium, Large)
        location: Ubicación geográfica
        api_key: Clave de API de Gemini (opcional)
        
    Returns:
        Diccionario con la oferta de trabajo simulada
    """
    client = GeminiApiClient(api_key=api_key)
    
    # Valores por defecto
    industry = industry or random.choice([
        "Technology", "Healthcare", "Finance", "Education", 
        "Retail", "Manufacturing", "Marketing", "Hospitality"
    ])
    
    company_size = company_size or random.choice(["Small", "Medium", "Large"])
    
    location = location or random.choice([
        "New York, NY", "San Francisco, CA", "Austin, TX", "Chicago, IL",
        "Seattle, WA", "Boston, MA", "Los Angeles, CA", "Denver, CO",
        "Madrid, Spain", "London, UK", "Berlin, Germany", "Paris, France",
        "Toronto, Canada", "Sydney, Australia", "Tokyo, Japan", "Singapore"
    ])
    
    # Construir prompt
    prompt = f"""
    Genera una oferta de trabajo realista para una empresa de {industry} de tamaño {company_size} en {location}.
    
    La oferta debe incluir:
    - Título del puesto
    - Nombre de la empresa
    - Ubicación
    - Rango salarial (en USD o moneda local)
    - Tipo de empleo (Full-time, Part-time, Contract)
    - Descripción detallada del puesto
    - Requisitos (educación, experiencia, habilidades)
    - Beneficios ofrecidos
    
    Devuelve el resultado en formato JSON con los siguientes campos:
    - title: Título del puesto
    - company: Nombre de la empresa
    - location: Ubicación
    - salary_range: Objeto con campos min y max
    - employment_type: Tipo de empleo
    - description: Descripción del puesto
    - requirements: Lista de requisitos
    - benefits: Lista de beneficios
    
    Solo devuelve el JSON, sin explicaciones adicionales.
    """
    
    # Generar oferta
    response = client.generate_content(prompt, max_tokens=1000, temperature=0.8)
    
    # Parsear respuesta JSON
    try:
        job_opening = json.loads(response.text)
        return job_opening
    except json.JSONDecodeError:
        # Intentar extraer JSON
        match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        if match:
            try:
                job_opening = json.loads(match.group(1))
                return job_opening
            except json.JSONDecodeError:
                raise ValueError("No se pudo parsear la respuesta como JSON")
        else:
            raise ValueError("No se pudo parsear la respuesta como JSON")
```

## Simulación de Perfiles de Candidatos

AdFlux puede generar perfiles de candidatos realistas:

```python
def simulate_candidate_profile(job_title=None, experience_level=None, location=None, api_key=None):
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
    
    # Valores por defecto
    job_title = job_title or random.choice([
        "Software Engineer", "Data Scientist", "Product Manager",
        "Marketing Specialist", "Sales Representative", "HR Manager",
        "Financial Analyst", "Customer Support Specialist", "UX Designer"
    ])
    
    experience_level = experience_level or random.choice(["junior", "mid-level", "senior"])
    
    location = location or random.choice([
        "New York, NY", "San Francisco, CA", "Austin, TX", "Chicago, IL",
        "Seattle, WA", "Boston, MA", "Los Angeles, CA", "Denver, CO",
        "Madrid, Spain", "London, UK", "Berlin, Germany", "Paris, France",
        "Toronto, Canada", "Sydney, Australia", "Tokyo, Japan", "Singapore"
    ])
    
    # Construir prompt
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
    
    # Generar perfil
    response = client.generate_content(prompt, max_tokens=1000, temperature=0.8)
    
    # Parsear respuesta JSON
    try:
        profile = json.loads(response.text)
        return profile
    except json.JSONDecodeError:
        # Intentar extraer JSON
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

## Simulación de Campañas

AdFlux puede generar campañas publicitarias simuladas:

```python
def simulate_campaign(job_opening_id=None, platform=None, budget_range=None):
    """
    Simula una campaña publicitaria.
    
    Args:
        job_opening_id: ID de la oferta de trabajo (opcional)
        platform: Plataforma publicitaria (META, GOOGLE, TIKTOK, SNAPCHAT)
        budget_range: Rango de presupuesto (min, max)
        
    Returns:
        Diccionario con la campaña simulada
    """
    # Valores por defecto
    platform = platform or random.choice(["META", "GOOGLE", "TIKTOK", "SNAPCHAT"])
    
    budget_range = budget_range or (50, 500)
    daily_budget = round(random.uniform(budget_range[0], budget_range[1]), 2)
    
    # Obtener oferta de trabajo
    if job_opening_id:
        job_opening = JobOpening.query.get(job_opening_id)
        if not job_opening:
            raise ValueError(f"Oferta de trabajo con ID {job_opening_id} no encontrada")
    else:
        # Crear oferta simulada
        job_data = simulate_job_opening()
        job_opening = JobOpening(
            title=job_data['title'],
            company=job_data['company'],
            location=job_data['location'],
            description=job_data['description'],
            requirements=job_data['requirements'],
            employment_type=job_data['employment_type'],
            salary_min=job_data['salary_range']['min'],
            salary_max=job_data['salary_range']['max'],
            status='ACTIVE',
            created_at=datetime.utcnow(),
            created_by=1  # Usuario admin por defecto
        )
        db.session.add(job_opening)
        db.session.commit()
    
    # Generar fechas
    start_date = datetime.utcnow() + timedelta(days=random.randint(1, 7))
    end_date = start_date + timedelta(days=random.randint(14, 30))
    
    # Generar objetivo
    objective = random.choice(["AWARENESS", "CONSIDERATION", "CONVERSION"])
    
    # Generar segmentación
    targeting = {
        'age_min': random.randint(18, 25),
        'age_max': random.randint(35, 65),
        'genders': random.choice([
            [1],  # Hombres
            [2],  # Mujeres
            [1, 2]  # Ambos
        ]),
        'locations': [
            {'id': '2421', 'name': 'New York, United States'},
            {'id': '2436', 'name': 'Los Angeles, United States'}
        ],
        'interests': [
            {'id': '6003139266461', 'name': 'Software development'},
            {'id': '6003139266456', 'name': 'Technology'}
        ]
    }
    
    # Generar contenido creativo
    ad_creative = {
        'headline': f"Join {job_opening.company} as {job_opening.title}",
        'description': f"Great opportunity in {job_opening.location}. Apply now!",
        'image_url': 'https://example.com/image.jpg',
        'call_to_action': 'APPLY_NOW',
        'website_url': 'https://example.com/careers'
    }
    
    # Crear campaña
    campaign = {
        'name': f"{job_opening.title} - {platform} Campaign",
        'objective': objective,
        'platform': platform,
        'status': 'DRAFT',
        'daily_budget': daily_budget,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'targeting': targeting,
        'ad_creative': ad_creative,
        'job_opening_id': job_opening.id
    }
    
    return campaign
```

## Simulación de Métricas

AdFlux puede generar métricas simuladas para campañas:

```python
def simulate_campaign_metrics(campaign_id, days=30):
    """
    Simula métricas para una campaña.
    
    Args:
        campaign_id: ID de la campaña
        days: Número de días a simular
        
    Returns:
        Diccionario con métricas simuladas
    """
    # Obtener campaña
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        raise ValueError(f"Campaña con ID {campaign_id} no encontrada")
    
    # Parámetros base según plataforma
    platform_params = {
        'META': {
            'ctr_base': 0.015,  # 1.5%
            'cpc_base': 1.20,   # $1.20
            'cpa_base': 25.0    # $25.00
        },
        'GOOGLE': {
            'ctr_base': 0.025,  # 2.5%
            'cpc_base': 1.50,   # $1.50
            'cpa_base': 30.0    # $30.00
        },
        'TIKTOK': {
            'ctr_base': 0.010,  # 1.0%
            'cpc_base': 0.80,   # $0.80
            'cpa_base': 20.0    # $20.00
        },
        'SNAPCHAT': {
            'ctr_base': 0.008,  # 0.8%
            'cpc_base': 0.70,   # $0.70
            'cpa_base': 18.0    # $18.00
        }
    }
    
    # Obtener parámetros para la plataforma
    params = platform_params.get(campaign.platform, platform_params['META'])
    
    # Generar métricas diarias
    daily_metrics = []
    
    start_date = datetime.strptime(campaign.start_date, '%Y-%m-%d')
    
    for day in range(days):
        date = start_date + timedelta(days=day)
        
        # Simular variación diaria
        daily_variation = random.uniform(0.8, 1.2)
        
        # Calcular métricas base
        impressions = int(campaign.daily_budget / params['cpc_base'] * 1000 * daily_variation)
        ctr = params['ctr_base'] * random.uniform(0.9, 1.1)
        clicks = int(impressions * ctr)
        cpc = params['cpc_base'] * random.uniform(0.9, 1.1)
        spend = clicks * cpc
        
        # Limitar gasto al presupuesto diario
        if spend > campaign.daily_budget:
            spend = campaign.daily_budget
            clicks = int(spend / cpc)
        
        # Calcular conversiones (aplicaciones)
        cpa = params['cpa_base'] * random.uniform(0.9, 1.1)
        applications = int(spend / cpa)
        
        # Calcular métricas adicionales
        cpm = (spend / impressions) * 1000 if impressions > 0 else 0
        
        # Añadir a métricas diarias
        daily_metrics.append({
            'date': date.strftime('%Y-%m-%d'),
            'impressions': impressions,
            'clicks': clicks,
            'ctr': ctr,
            'cpc': cpc,
            'spend': spend,
            'applications': applications,
            'cpa': cpa,
            'cpm': cpm
        })
    
    # Calcular métricas totales
    total_impressions = sum(day['impressions'] for day in daily_metrics)
    total_clicks = sum(day['clicks'] for day in daily_metrics)
    total_spend = sum(day['spend'] for day in daily_metrics)
    total_applications = sum(day['applications'] for day in daily_metrics)
    
    avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
    avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
    avg_cpa = total_spend / total_applications if total_applications > 0 else 0
    avg_cpm = (total_spend / total_impressions) * 1000 if total_impressions > 0 else 0
    
    return {
        'daily': daily_metrics,
        'total': {
            'impressions': total_impressions,
            'clicks': total_clicks,
            'spend': total_spend,
            'applications': total_applications,
            'ctr': avg_ctr,
            'cpc': avg_cpc,
            'cpa': avg_cpa,
            'cpm': avg_cpm
        }
    }
```

## Uso en Pruebas

La simulación de datos es especialmente útil para pruebas:

```python
def setup_test_data():
    """
    Configura datos de prueba para el entorno de testing.
    
    Returns:
        Diccionario con IDs de los datos creados
    """
    # Crear usuarios de prueba
    admin_user = User(
        username='admin_test',
        email='admin@test.com',
        name='Admin Test',
        password_hash='hashed_password',
        active=True
    )
    db.session.add(admin_user)
    
    regular_user = User(
        username='user_test',
        email='user@test.com',
        name='User Test',
        password_hash='hashed_password',
        active=True
    )
    db.session.add(regular_user)
    
    db.session.commit()
    
    # Crear ofertas de trabajo simuladas
    job_openings = []
    for _ in range(5):
        job_data = simulate_job_opening()
        job_opening = JobOpening(
            title=job_data['title'],
            company=job_data['company'],
            location=job_data['location'],
            description=job_data['description'],
            requirements=job_data['requirements'],
            employment_type=job_data['employment_type'],
            salary_min=job_data['salary_range']['min'],
            salary_max=job_data['salary_range']['max'],
            status='ACTIVE',
            created_at=datetime.utcnow(),
            created_by=admin_user.id
        )
        db.session.add(job_opening)
        job_openings.append(job_opening)
    
    db.session.commit()
    
    # Crear candidatos simulados
    candidates = []
    for _ in range(20):
        candidate_data = simulate_candidate_profile()
        candidate = Candidate(
            name=candidate_data['name'],
            email=candidate_data['email'],
            phone=candidate_data['phone'],
            location=candidate_data['location'],
            skills=candidate_data['skills'],
            experience=candidate_data['experience'],
            education=candidate_data['education'],
            status='ACTIVE',
            created_at=datetime.utcnow()
        )
        db.session.add(candidate)
        candidates.append(candidate)
    
    db.session.commit()
    
    # Crear campañas simuladas
    campaigns = []
    for job_opening in job_openings:
        for platform in ['META', 'GOOGLE']:
            campaign_data = simulate_campaign(job_opening.id, platform)
            campaign = Campaign(
                name=campaign_data['name'],
                objective=campaign_data['objective'],
                platform=campaign_data['platform'],
                status=campaign_data['status'],
                daily_budget=campaign_data['daily_budget'],
                start_date=campaign_data['start_date'],
                end_date=campaign_data['end_date'],
                targeting=campaign_data['targeting'],
                ad_creative=campaign_data['ad_creative'],
                created_at=datetime.utcnow(),
                created_by=admin_user.id,
                job_opening_id=job_opening.id
            )
            db.session.add(campaign)
            campaigns.append(campaign)
    
    db.session.commit()
    
    # Crear aplicaciones simuladas
    applications = []
    for candidate in candidates[:10]:
        for job_opening in job_openings[:2]:
            application = Application(
                job_opening_id=job_opening.id,
                candidate_id=candidate.id,
                status=random.choice(['PENDING', 'REVIEWED', 'INTERVIEWED', 'REJECTED', 'HIRED']),
                source=random.choice(['META', 'GOOGLE', 'DIRECT']),
                created_at=datetime.utcnow()
            )
            db.session.add(application)
            applications.append(application)
    
    db.session.commit()
    
    return {
        'users': {
            'admin': admin_user.id,
            'regular': regular_user.id
        },
        'job_openings': [job.id for job in job_openings],
        'candidates': [candidate.id for candidate in candidates],
        'campaigns': [campaign.id for campaign in campaigns],
        'applications': [application.id for application in applications]
    }
```

## Uso en Desarrollo

La simulación de datos también es útil durante el desarrollo:

```python
def generate_development_data(num_job_openings=10, num_candidates=50, num_campaigns=20):
    """
    Genera datos para el entorno de desarrollo.
    
    Args:
        num_job_openings: Número de ofertas de trabajo a generar
        num_candidates: Número de candidatos a generar
        num_campaigns: Número de campañas a generar
        
    Returns:
        Diccionario con estadísticas de los datos generados
    """
    # Verificar usuario admin
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@adflux.example.com',
            name='Admin User',
            password_hash='hashed_password',
            active=True
        )
        db.session.add(admin_user)
        db.session.commit()
    
    # Generar ofertas de trabajo
    job_openings_created = 0
    for _ in range(num_job_openings):
        try:
            job_data = simulate_job_opening()
            job_opening = JobOpening(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                description=job_data['description'],
                requirements=job_data['requirements'],
                employment_type=job_data['employment_type'],
                salary_min=job_data['salary_range']['min'],
                salary_max=job_data['salary_range']['max'],
                status='ACTIVE',
                created_at=datetime.utcnow(),
                created_by=admin_user.id
            )
            db.session.add(job_opening)
            job_openings_created += 1
        except Exception as e:
            logger.error(f"Error al generar oferta de trabajo: {str(e)}")
    
    db.session.commit()
    
    # Generar candidatos
    candidates_created = 0
    for _ in range(num_candidates):
        try:
            candidate_data = simulate_candidate_profile()
            candidate = Candidate(
                name=candidate_data['name'],
                email=candidate_data['email'],
                phone=candidate_data['phone'],
                location=candidate_data['location'],
                skills=candidate_data['skills'],
                experience=candidate_data['experience'],
                education=candidate_data['education'],
                status='ACTIVE',
                created_at=datetime.utcnow()
            )
            db.session.add(candidate)
            candidates_created += 1
        except Exception as e:
            logger.error(f"Error al generar candidato: {str(e)}")
    
    db.session.commit()
    
    # Generar campañas
    campaigns_created = 0
    job_openings = JobOpening.query.all()
    
    for _ in range(num_campaigns):
        if not job_openings:
            break
        
        try:
            job_opening = random.choice(job_openings)
            platform = random.choice(['META', 'GOOGLE', 'TIKTOK', 'SNAPCHAT'])
            
            campaign_data = simulate_campaign(job_opening.id, platform)
            campaign = Campaign(
                name=campaign_data['name'],
                objective=campaign_data['objective'],
                platform=campaign_data['platform'],
                status=random.choice(['DRAFT', 'ACTIVE', 'PAUSED', 'COMPLETED']),
                daily_budget=campaign_data['daily_budget'],
                start_date=campaign_data['start_date'],
                end_date=campaign_data['end_date'],
                targeting=campaign_data['targeting'],
                ad_creative=campaign_data['ad_creative'],
                created_at=datetime.utcnow(),
                created_by=admin_user.id,
                job_opening_id=job_opening.id
            )
            db.session.add(campaign)
            campaigns_created += 1
        except Exception as e:
            logger.error(f"Error al generar campaña: {str(e)}")
    
    db.session.commit()
    
    # Generar métricas para campañas activas
    metrics_created = 0
    active_campaigns = Campaign.query.filter_by(status='ACTIVE').all()
    
    for campaign in active_campaigns:
        try:
            metrics = simulate_campaign_metrics(campaign.id)
            
            # Guardar métricas diarias
            for daily in metrics['daily']:
                if campaign.platform == 'META':
                    insight = MetaInsight(
                        meta_campaign_id=campaign.meta_campaign.id if campaign.meta_campaign else None,
                        date_start=daily['date'],
                        date_stop=daily['date'],
                        impressions=daily['impressions'],
                        clicks=daily['clicks'],
                        spend=daily['spend'],
                        reach=int(daily['impressions'] * 0.8),  # Estimación
                        cpm=daily['cpm'],
                        ctr=daily['ctr']
                    )
                    db.session.add(insight)
            
            metrics_created += 1
        except Exception as e:
            logger.error(f"Error al generar métricas para campaña {campaign.id}: {str(e)}")
    
    db.session.commit()
    
    return {
        'job_openings_created': job_openings_created,
        'candidates_created': candidates_created,
        'campaigns_created': campaigns_created,
        'metrics_created': metrics_created
    }
```

La simulación de datos es una herramienta poderosa que permite a los desarrolladores y testers trabajar con datos realistas sin depender de datos reales, lo que acelera el desarrollo y mejora la calidad de las pruebas.
