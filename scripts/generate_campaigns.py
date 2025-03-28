"""
Script to generate fake ad campaigns for testing and development.
"""
import os
import sys
from datetime import datetime, timedelta
from faker import Faker
from random import choice, randint, uniform

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.job_opening import JobOpening
from app.models.segment import Segment
from app.services.campaign_manager import CampaignManager

def generate_job_openings(fake, num_jobs=5):
    """Generate fake job openings."""
    jobs = []
    companies = [fake.company() for _ in range(3)]  # Use a few companies repeatedly
    
    for _ in range(num_jobs):
        company = choice(companies)
        title = fake.job()
        job = JobOpening(
            title=title,
            company=company,
            description=fake.paragraph(nb_sentences=5),
            location=fake.city(),
            salary_range=f"${randint(50,150)}k - ${randint(150,200)}k",
            requirements="\n".join([f"- {fake.bs()}" for _ in range(5)]),
            application_url=fake.url(),
            created_at=datetime.now() - timedelta(days=randint(0, 30))
        )
        jobs.append(job)
    
    return jobs

def generate_segments(fake, num_segments=3):
    """Generate fake audience segments."""
    segments = []
    
    for i in range(num_segments):
        # Create segment with realistic targeting criteria
        criteria = {
            'age_range': [
                choice([18, 22, 25, 30]),
                choice([35, 45, 55, 65])
            ],
            'location': [fake.city() for _ in range(randint(1, 3))],
            'interests': [
                'Software Development',
                'Data Science',
                'Cloud Computing',
                'Machine Learning',
                'Web Development',
                'DevOps'
            ][:randint(2, 4)],
            'keywords': [fake.word() for _ in range(5)]
        }
        
        segment = Segment(
            name=f"Segment {i + 1}: {' & '.join(criteria['interests'][:2])}",
            description=f"Professionals aged {criteria['age_range'][0]}-{criteria['age_range'][1]} "
                       f"interested in {', '.join(criteria['interests'])}",
            criteria=criteria
        )
        segments.append(segment)
    
    return segments

def create_fake_campaigns():
    """Create fake campaigns across platforms."""
    fake = Faker()
    app = create_app()
    
    with app.app_context():
        # Generate and save job openings
        jobs = generate_job_openings(fake)
        for job in jobs:
            db.session.add(job)
        db.session.commit()
        
        # Generate and save segments
        segments = generate_segments(fake)
        for segment in segments:
            db.session.add(segment)
        db.session.commit()
        
        # Create campaign manager
        manager = CampaignManager()
        
        # Create campaigns for each job
        platforms = ['meta', 'google', 'twitter']
        for job in jobs:
            # Randomly select platforms and segment
            selected_platforms = platforms[:randint(1, len(platforms))]
            segment = choice(segments) if randint(0, 1) else None
            
            # Create campaign with random budget
            result = manager.create_campaign(
                job_opening_id=job.id,
                platforms=selected_platforms,
                segment_id=segment.id if segment else None,
                budget=round(uniform(500, 2000), 2),  # Random budget between $500-$2000
                status='PAUSED'
            )
            
            print(f"\nCreated campaigns for job: {job.title}")
            print(f"Platforms: {', '.join(selected_platforms)}")
            print(f"Segment: {segment.name if segment else 'None'}")
            print("Results:", result)

if __name__ == '__main__':
    create_fake_campaigns()
