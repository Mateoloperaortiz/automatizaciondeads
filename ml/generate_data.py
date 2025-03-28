"""
Generate simulated data for development and testing.

This script creates simulated data for job openings and candidates,
which can be used for development and testing of the Ad Automation P-01 system.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
import numpy as np

# Add the project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import models after setting path
from app import create_app, db
from app.models.job_opening import JobOpening
from app.models.candidate import Candidate

# Initialize Faker
fake = Faker('es_CO')  # Colombian Spanish locale

def generate_job_openings(count=20):
    """Generate simulated job openings.
    
    Args:
        count (int): Number of job openings to generate
        
    Returns:
        list: List of generated JobOpening instances
    """
    # Define job types and experience levels
    job_types = ['Full-time', 'Part-time', 'Contract', 'Internship']
    experience_levels = ['Entry', 'Mid-level', 'Senior', 'Executive']
    companies = [
        'Magneto365', 'TechCorp', 'Digital Solutions',
        'Colombian Innovations', 'Data Analytics SA',
        'Global Systems', 'Software Solutions', 'Cloud Services'
    ]
    locations = [
        'Bogotá', 'Medellín', 'Cali', 'Barranquilla',
        'Cartagena', 'Bucaramanga', 'Pereira', 'Remote'
    ]
    
    job_openings = []
    
    for _ in range(count):
        job_title = fake.job()
        company = random.choice(companies)
        location = random.choice(locations)
        
        # Generate a descriptive job description
        description = f"We are looking for a talented {job_title} to join our team at {company}. "
        description += fake.paragraph(nb_sentences=5)
        
        # Generate requirements
        requirements = "Requirements:\n- " + "\n- ".join(fake.paragraphs(nb=3))
        
        # Generate salary range (in Colombian Pesos)
        min_salary = random.choice([1000000, 1500000, 2000000, 2500000, 3000000])
        max_salary = min_salary + random.choice([500000, 1000000, 1500000, 2000000])
        salary_range = f"${min_salary/1000000:.1f}M - ${max_salary/1000000:.1f}M COP"
        
        # Create job opening
        job_opening = JobOpening(
            title=job_title,
            company=company,
            location=location,
            description=description,
            requirements=requirements,
            salary_range=salary_range,
            job_type=random.choice(job_types),
            experience_level=random.choice(experience_levels),
            created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            active=random.random() > 0.2  # 80% active
        )
        
        job_openings.append(job_opening)
    
    return job_openings

def generate_candidates(count=200):
    """Generate simulated candidates.
    
    Args:
        count (int): Number of candidates to generate
        
    Returns:
        list: List of generated Candidate instances
    """
    # Define education levels and other characteristics
    education_levels = ['High School', 'Technical', 'Bachelor', 'Master', 'PhD']
    job_preferences = [
        'Technology', 'Finance', 'Marketing', 'Sales',
        'Customer Service', 'Healthcare', 'Education', 'Manufacturing'
    ]
    locations = [
        'Bogotá', 'Medellín', 'Cali', 'Barranquilla',
        'Cartagena', 'Bucaramanga', 'Pereira', 'Remote'
    ]
    skills = [
        'Python', 'JavaScript', 'SQL', 'Data Analysis',
        'Marketing', 'Sales', 'Communication', 'Management',
        'Excel', 'Project Management', 'Design', 'Customer Service'
    ]
    
    candidates = []
    
    for _ in range(count):
        # Generate age between 18 and 65
        age = random.randint(18, 65)
        
        # Generate years of experience based on age
        max_experience = min(age - 18, 40)  # Max experience is age-18 or 40, whichever is less
        years_experience = random.randint(0, max_experience)
        
        # Adjust education level based on age and experience
        if age < 22:
            possible_education = education_levels[:2]  # Only high school or technical for younger candidates
        elif age < 25:
            possible_education = education_levels[:3]  # Up to bachelor for mid-20s
        else:
            possible_education = education_levels  # All possibilities for older candidates
        
        education_level = random.choice(possible_education)
        
        # Determine skills based on education and experience
        num_skills = random.randint(2, 8)
        candidate_skills = random.sample(skills, num_skills)
        
        # Create candidate
        candidate = Candidate(
            name=fake.name(),
            age=age,
            gender=random.choice(['Male', 'Female', 'Other']),
            location=random.choice(locations),
            education_level=education_level,
            field_of_study=fake.bs() if random.random() > 0.3 else None,
            years_of_experience=years_experience,
            desired_job_type=random.choice(['Full-time', 'Part-time', 'Contract', 'Remote']),
            desired_industry=random.choice(['Technology', 'Finance', 'Healthcare', 'Education', 'Manufacturing', 'Retail']),
            desired_role=fake.job(),
            desired_salary=random.randint(1000000, 10000000),
            created_at=datetime.now() - timedelta(days=random.randint(0, 90))
        )
        
        # Set skills and job preferences using property
        candidate.skills = candidate_skills
        candidate.job_preferences = random.sample(job_preferences, random.randint(1, 3))
        
        candidates.append(candidate)
    
    return candidates

def save_to_csv(job_openings, candidates):
    """Save generated data to CSV files.
    
    Args:
        job_openings (list): List of JobOpening instances
        candidates (list): List of Candidate instances
    """
    # Create directory if it doesn't exist
    os.makedirs('ml/data', exist_ok=True)
    
    # Convert job openings to dataframe and save
    job_data = [{
        'id': i + 1,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'description': job.description,
        'requirements': job.requirements,
        'salary_range': job.salary_range,
        'job_type': job.job_type,
        'experience_level': job.experience_level,
        'created_at': job.created_at,
        'active': job.active
    } for i, job in enumerate(job_openings)]
    
    jobs_df = pd.DataFrame(job_data)
    jobs_df.to_csv('ml/data/job_openings.csv', index=False)
    
    # Convert candidates to dataframe and save
    candidate_data = [{
        'id': i + 1,
        'name': candidate.name,
        'email': candidate.email,
        'phone': candidate.phone,
        'age': candidate.age,
        'location': candidate.location,
        'education_level': candidate.education_level,
        'years_experience': candidate.years_experience,
        'job_preferences': ','.join(candidate.job_preferences) if candidate.job_preferences else '',
        'skills': ','.join(candidate.skills) if candidate.skills else '',
        'created_at': candidate.created_at
    } for i, candidate in enumerate(candidates)]
    
    candidates_df = pd.DataFrame(candidate_data)
    candidates_df.to_csv('ml/data/candidates.csv', index=False)
    
    print(f"Data saved to CSV files in ml/data directory")

def save_to_database(job_openings, candidates):
    """Save generated data to the database.
    
    Args:
        job_openings (list): List of JobOpening instances
        candidates (list): List of Candidate instances
    """
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.session.query(JobOpening).delete()
        db.session.query(Candidate).delete()
        
        # Add new data
        db.session.add_all(job_openings)
        db.session.add_all(candidates)
        
        # Commit changes
        db.session.commit()
        
        print(f"Added {len(job_openings)} job openings and {len(candidates)} candidates to database")

def main():
    """Generate and save simulated data."""
    # Generate data
    print("Generating job openings...")
    job_openings = generate_job_openings(count=20)
    
    print("Generating candidates...")
    candidates = generate_candidates(count=200)
    
    # Save to CSV
    save_to_csv(job_openings, candidates)
    
    # Ask if should save to database
    save_db = input("Do you want to save the data to the database? (y/n): ")
    if save_db.lower() == 'y':
        save_to_database(job_openings, candidates)
    
    print("Data generation complete")

if __name__ == '__main__':
    main() 