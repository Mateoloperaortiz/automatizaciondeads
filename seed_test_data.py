"""
Script para inicializar la base de datos de AdFlux con datos de prueba.

Este script crea datos de prueba sin depender de la API de Gemini.
"""

from adflux.core import create_app
from adflux.extensions import db
from adflux.models.job import JobOpening
from adflux.models.candidate import Candidate
from adflux.models.segment import Segment
from adflux.models.campaign import Campaign
from adflux.models.payment import PaymentMethod, BudgetPlan, Transaction
import datetime
import random

def seed_test_data():
    """Crea datos de prueba para la aplicación."""
    app = create_app()
    with app.app_context():
        existing_jobs = JobOpening.query.count()
        if existing_jobs > 0:
            print(f"Ya existen {existing_jobs} trabajos en la base de datos. Omitiendo creación de trabajos.")
            jobs = JobOpening.query.all()
        else:
            jobs = []
            for i in range(1, 6):
                job = JobOpening(
                    job_id=f"JOB-{i:04d}",
                    title=f"Trabajo de prueba {i}",
                    description=f"Descripción del trabajo de prueba {i}",
                    location=random.choice(["Medellín", "Bogotá", "Cali", "Barranquilla"]),
                    company_name=f"Empresa {i}",
                    required_skills=["Python", "JavaScript", "React"],
                    salary_min=random.randint(1000000, 2000000),
                    salary_max=random.randint(2000001, 4000000),
                    status="open",
                    posted_date=datetime.date.today()
                )
                db.session.add(job)
                jobs.append(job)
            
            db.session.commit()
            print(f"Creados {len(jobs)} trabajos de prueba.")
        
        existing_candidates = Candidate.query.count()
        if existing_candidates > 0:
            print(f"Ya existen {existing_candidates} candidatos en la base de datos. Omitiendo creación de candidatos.")
            candidates = Candidate.query.all()
        else:
            candidates = []
            skills = ["Python", "JavaScript", "React", "Angular", "Node.js", "Django", "Flask", "SQL", "NoSQL", "AWS"]
            for i in range(1, 21):
                candidate = Candidate(
                    candidate_id=f"CAND-{i:05d}",
                    name=f"Candidato {i}",
                    email=f"candidato{i}@example.com",
                    phone=f"+57 300 {random.randint(1000000, 9999999)}",
                    location=random.choice(["Medellín", "Bogotá", "Cali", "Barranquilla"]),
                    years_experience=random.randint(0, 10),
                    education_level=random.choice(["Bachiller", "Técnico", "Profesional", "Especialización", "Maestría"]),
                    skills=random.sample(skills, k=random.randint(2, 5)),
                    primary_skill=random.choice(skills),
                    desired_salary=random.randint(1000000, 5000000)
                )
                db.session.add(candidate)
                candidates.append(candidate)
            
            db.session.commit()
            print(f"Creados {len(candidates)} candidatos de prueba.")
        
        existing_segments = Segment.query.count()
        if existing_segments > 0:
            print(f"Ya existen {existing_segments} segmentos en la base de datos. Omitiendo creación de segmentos.")
            segments = Segment.query.all()
        else:
            segments = []
            for i in range(1, 4):
                segment = Segment(
                    name=f"Segmento {i}",
                    description=f"Descripción del segmento {i}"
                )
                db.session.add(segment)
                segments.append(segment)
            
            db.session.commit()
            print(f"Creados {len(segments)} segmentos de prueba.")
            
            for candidate in candidates:
                if not candidate.segment_id:
                    segment = random.choice(segments)
                    candidate.segment_id = segment.id
            
            db.session.commit()
            print("Candidatos asignados a segmentos.")
        
        existing_campaigns = Campaign.query.count()
        if existing_campaigns > 0:
            print(f"Ya existen {existing_campaigns} campañas en la base de datos. Omitiendo creación de campañas.")
            campaigns = Campaign.query.all()
        else:
            campaigns = []
            platforms = ["meta", "google", "tiktok", "snapchat"]
            for i in range(1, 11):
                campaign = Campaign(
                    name=f"Campaña {i}",
                    description=f"Descripción de la campaña {i}",
                    platform=random.choice(platforms),
                    job_opening_id=random.choice(jobs).job_id,
                    target_segment_ids=[random.choice(segments).id] if random.random() > 0.3 else None,
                    status=random.choice(["draft", "active", "paused", "archived"]),
                    daily_budget=random.randint(100000, 1000000),
                    start_date=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30)),
                    end_date=datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 30)),
                    primary_text=f"Texto principal para la campaña {i}",
                    headline=f"Título para la campaña {i}",
                    link_description=f"Descripción del enlace para la campaña {i}",
                    landing_page_url=f"https://example.com/jobs/{i}"
                )
                db.session.add(campaign)
                campaigns.append(campaign)
            
            db.session.commit()
            print(f"Creadas {len(campaigns)} campañas de prueba.")
        
        existing_payment_methods = PaymentMethod.query.count()
        if existing_payment_methods > 0:
            print(f"Ya existen {existing_payment_methods} métodos de pago en la base de datos. Omitiendo creación de métodos de pago.")
            payment_methods = PaymentMethod.query.all()
        else:
            payment_methods = []
            for i in range(1, 4):
                payment_method = PaymentMethod(
                    user_id=1,  # Usuario de prueba
                    stripe_payment_method_id=f"pm_test_{i}_{random.randint(10000, 99999)}",
                    stripe_customer_id=f"cus_test_{random.randint(10000, 99999)}",
                    type="card",
                    last_four=f"{random.randint(1000, 9999)}",
                    brand=random.choice(["visa", "mastercard", "amex"]),
                    exp_month=random.randint(1, 12),
                    exp_year=random.randint(2025, 2030),
                    is_default=i == 1,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now()
                )
                db.session.add(payment_method)
                payment_methods.append(payment_method)
            
            db.session.commit()
            print(f"Creados {len(payment_methods)} métodos de pago de prueba.")
        
        existing_budget_plans = BudgetPlan.query.count()
        if existing_budget_plans > 0:
            print(f"Ya existen {existing_budget_plans} planes de presupuesto en la base de datos. Omitiendo creación de planes de presupuesto.")
            budget_plans = BudgetPlan.query.all()
        else:
            budget_plans = []
            for i in range(1, 3):
                campaign_ids = [campaign.id for campaign in random.sample(campaigns, k=random.randint(2, 5))]
                budget_plan = BudgetPlan(
                    user_id=1,  # Usuario de prueba
                    name=f"Plan de presupuesto {i}",
                    description=f"Descripción del plan de presupuesto {i}",
                    total_budget=random.randint(500000, 2000000),
                    distribution_type=random.choice(["manual", "automatic", "performance_based"]),
                    distribution_config={"strategy": "balanced"},
                    daily_spend_limit=random.randint(10000, 50000),
                    alert_threshold=0.8,
                    status=random.choice(["active", "paused", "completed"]),
                    start_date=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 15)),
                    end_date=datetime.datetime.now() + datetime.timedelta(days=random.randint(15, 45)),
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now()
                )
                selected_campaigns = random.sample(campaigns, k=random.randint(2, 5))
                for campaign in selected_campaigns:
                    budget_plan.campaigns.append(campaign)
                db.session.add(budget_plan)
                budget_plans.append(budget_plan)
            
            db.session.commit()
            print(f"Creados {len(budget_plans)} planes de presupuesto de prueba.")
        
        existing_transactions = Transaction.query.count()
        if existing_transactions > 0:
            print(f"Ya existen {existing_transactions} transacciones en la base de datos. Omitiendo creación de transacciones.")
            transactions = Transaction.query.all()
        else:
            transactions = []
            for i in range(1, 21):
                budget_plan = random.choice(budget_plans)
                if budget_plan.campaigns:
                    campaign = random.choice(list(budget_plan.campaigns))
                    transaction = Transaction(
                        user_id=1,  # Usuario de prueba
                        transaction_type="charge",
                        amount=random.randint(10000, 100000),
                        currency="COP",
                        status=random.choice(["pending", "completed", "failed", "refunded"]),
                        payment_method_id=random.choice(payment_methods).id,
                        budget_plan_id=budget_plan.id,
                        stripe_transaction_id=f"txn_test_{i}_{random.randint(10000, 99999)}",
                        stripe_receipt_url=f"https://stripe.com/receipts/test/{random.randint(10000, 99999)}",
                        description=f"Transacción de prueba {i} para campaña {campaign.name}",
                        transaction_metadata={"test": True, "automatic": True}
                    )
                    db.session.add(transaction)
                    transactions.append(transaction)
            
            db.session.commit()
            print(f"Creadas {len(transactions)} transacciones de prueba.")
        
        print("Datos de prueba creados exitosamente.")

if __name__ == "__main__":
    seed_test_data()
