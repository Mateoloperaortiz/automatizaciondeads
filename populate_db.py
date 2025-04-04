from adflux.app import create_app
from adflux.models import JobOpening, Campaign, Candidate, Segment, db
from datetime import datetime, timedelta
from adflux.data_simulation import generate_multiple_jobs, generate_multiple_candidates
import random

# --- Definiciones de Segmentos Predeterminados --- #
DEFAULT_SEGMENTS = {
    0: ("General Profile", "Segmento predeterminado para candidatos que no coinciden con criterios específicos."),
    1: ("High-Potential Match", "Candidatos que coinciden estrechamente con los requisitos del trabajo o muestran un gran potencial."),
    2: ("Specialized Skillset", "Candidatos con habilidades técnicas específicas, en demanda o de nicho."),
}

def populate_database():
    app = create_app()
    with app.app_context():
        # Limpiar registros existentes - Asegurar que Segment se elimine primero debido a FK
        print("Limpiando registros existentes...")
        Campaign.query.delete()
        Candidate.query.delete() # Candidate depende de Segment y Job
        JobOpening.query.delete()
        Segment.query.delete()   # Eliminar Segmentos primero
        db.session.commit()
        print("Registros existentes eliminados")

        # Crear Segmentos predeterminados
        print("Creando segmentos predeterminados...")
        segments_by_id = {}
        for seg_id, (name, description) in DEFAULT_SEGMENTS.items():
            segment = Segment(id=seg_id, name=name, description=description)
            db.session.add(segment)
            segments_by_id[seg_id] = segment # Almacenar para vincular más tarde
        db.session.commit()
        print(f"Creados {len(segments_by_id)} segmentos predeterminados")

        # Generar y crear trabajos usando data_simulation
        jobs_data = generate_multiple_jobs(count=5) 
        jobs = []
        for job_data in jobs_data:
            job = JobOpening(
                job_id=job_data['job_id'],
                title=job_data['title'],
                description=job_data['description'],
                location=job_data['location'],
                company=job_data['company'],
                required_skills=job_data['required_skills'],
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                posted_date=datetime.strptime(job_data['posted_date'], '%Y-%m-%d').date(),
                status=job_data['status']
            )
            db.session.add(job)
            jobs.append(job)
        db.session.commit()
        print(f"Creados {len(jobs)} trabajos")

        # Generar y crear candidatos usando data_simulation
        candidates_data = generate_multiple_candidates(count=20) 
        candidates = []
        for candidate_data in candidates_data:
            # Asignar un segment_id aleatorio (0, 1 o 2) por ahora
            # En un escenario real, esto vendría del modelo ML
            assigned_segment_id = random.choice(list(DEFAULT_SEGMENTS.keys()))
            
            candidate = Candidate(
                candidate_id=candidate_data['candidate_id'],
                name=candidate_data['name'],
                location=candidate_data['location'],
                years_experience=candidate_data['years_experience'],
                education_level=candidate_data['education_level'],
                skills=candidate_data['skills'],
                primary_skill=candidate_data['primary_skill'],
                desired_salary=candidate_data['desired_salary'],
                segment_id=assigned_segment_id # Asignar el ID de la clave foránea
            )
            db.session.add(candidate)
            candidates.append(candidate)
        db.session.commit()
        print(f"Creados {len(candidates)} candidatos con asignaciones de segmento aleatorias")

        # Crear una campaña para el primer trabajo
        if jobs:
            campaign = Campaign(
                name=f"Campaña para {jobs[0].title}",
                description=f"Campaña para promocionar nuestro puesto de {jobs[0].title}",
                platform='meta',
                status='draft',
                daily_budget=5000, 
                job_opening_id=jobs[0].job_id,
                primary_text=f"¡Únete a nuestro equipo como {jobs[0].title}!",
                headline=f"Puesto de {jobs[0].title}",
                link_description='Postula ahora'
            )
            db.session.add(campaign)
            db.session.commit()
            print(f"Campaña creada: {campaign.name}")

if __name__ == '__main__':
    populate_database() 