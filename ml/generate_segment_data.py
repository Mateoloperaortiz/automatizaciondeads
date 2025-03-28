"""
Generate test data for audience segmentation.

This script creates test data for the audience segmentation feature,
including candidates with appropriate attributes for clustering.
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from faker import Faker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after setting path
from app import create_app, db
from app.models.candidate import Candidate
from app.models.segment import Segment

# Initialize Faker
fake = Faker()

def generate_candidates(count=50):
    """Generate candidates with attributes suitable for segmentation.
    
    Args:
        count (int): Number of candidates to generate
        
    Returns:
        list: List of generated candidates
    """
    # Define data distributions
    age_groups = [
        (22, 30, 0.4),  # 40% young professionals
        (31, 45, 0.4),  # 40% mid-career
        (46, 65, 0.2)   # 20% senior professionals
    ]
    
    education_levels = [
        'High School', 'Associate Degree', 'Bachelor\'s Degree', 
        'Master\'s Degree', 'PhD'
    ]
    
    fields_of_study = [
        'Computer Science', 'Business', 'Marketing', 'Engineering',
        'Healthcare', 'Education', 'Finance', 'Design'
    ]
    
    job_types = ['Full-time', 'Part-time', 'Contract', 'Remote']
    
    industries = [
        'Technology', 'Finance', 'Healthcare', 'Education', 
        'Manufacturing', 'Retail', 'Media', 'Consulting'
    ]
    
    roles = [
        'Software Developer', 'Data Scientist', 'Product Manager',
        'Marketing Specialist', 'Financial Analyst', 'HR Specialist',
        'Sales Representative', 'Customer Support'
    ]
    
    locations = [
        'New York', 'San Francisco', 'Chicago', 'Boston', 
        'Seattle', 'Austin', 'Remote', 'Denver'
    ]
    
    salary_ranges = [
        (40000, 60000, 0.3),    # 30% entry-level
        (60001, 100000, 0.4),   # 40% mid-level
        (100001, 150000, 0.2),  # 20% senior
        (150001, 250000, 0.1)   # 10% executive
    ]
    
    all_skills = [
        'Python', 'Java', 'JavaScript', 'SQL', 'Data Analysis',
        'Machine Learning', 'Project Management', 'Communication',
        'Leadership', 'Sales', 'Marketing', 'Design', 'UI/UX',
        'Customer Support', 'Technical Writing', 'Product Management'
    ]
    
    job_preference_options = [
        'Remote Work', 'Flexible Hours', 'Professional Development',
        'Team Collaboration', 'Work-Life Balance', 'Career Growth',
        'Challenging Projects', 'Innovative Environment', 'Benefits Package'
    ]
    
    candidates = []
    
    for i in range(count):
        # Determine age based on distribution
        age_group = random.choices([0, 1, 2], [g[2] for g in age_groups])[0]
        age = random.randint(age_groups[age_group][0], age_groups[age_group][1])
        
        # Education level tends to correlate with age
        if age < 25:
            education_weights = [0.4, 0.3, 0.3, 0, 0]
        elif age < 35:
            education_weights = [0.1, 0.2, 0.5, 0.2, 0]
        elif age < 45:
            education_weights = [0.05, 0.15, 0.5, 0.25, 0.05]
        else:
            education_weights = [0.05, 0.1, 0.4, 0.35, 0.1]
            
        education_level = random.choices(education_levels, education_weights)[0]
        
        # Experience correlates with age
        min_exp = max(0, age - 22)  # Assume education until 22
        max_exp = max(0, age - 18)  # Assume can start working at 18
        years_of_experience = random.randint(min_exp, max_exp)
        
        # Salary based on distribution
        salary_group = random.choices([0, 1, 2, 3], [r[2] for r in salary_ranges])[0]
        desired_salary = random.randint(
            salary_ranges[salary_group][0], 
            salary_ranges[salary_group][1]
        )
        
        # Create candidate
        candidate = Candidate(
            name=fake.name(),
            age=age,
            gender=random.choice(['Male', 'Female', 'Other']),
            location=random.choice(locations),
            education_level=education_level,
            field_of_study=random.choice(fields_of_study) if random.random() > 0.1 else None,
            years_of_experience=years_of_experience,
            desired_job_type=random.choice(job_types),
            desired_industry=random.choice(industries),
            desired_role=random.choice(roles),
            desired_salary=desired_salary,
            created_at=datetime.now() - timedelta(days=random.randint(0, 60)),
            updated_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        
        # Add skills - more experienced candidates tend to have more skills
        skill_count = min(random.randint(2, 10), len(all_skills))
        skill_count = min(skill_count, 3 + int(years_of_experience / 3))  # More experience, more skills
        candidate.skills = random.sample(all_skills, skill_count)
        
        # Add job preferences - typically 2-5
        pref_count = random.randint(2, min(5, len(job_preference_options)))
        candidate.job_preferences = random.sample(job_preference_options, pref_count)
        
        candidates.append(candidate)
    
    return candidates

def generate_segments(count=5):
    """Generate initial empty segments.
    
    Args:
        count (int): Number of segments to generate
        
    Returns:
        list: List of generated segments
    """
    segments = []
    
    segment_names = [
        'Young Professionals', 
        'Mid-Career Specialists',
        'Senior Experts', 
        'Technical Talents',
        'Business Professionals',
        'Entry-Level Candidates',
        'Remote Workers',
        'Leadership Potential'
    ]
    
    # Create more descriptive names than just Cluster X
    selected_names = random.sample(segment_names, min(count, len(segment_names)))
    
    for i in range(count):
        name = selected_names[i] if i < len(selected_names) else f"Segment {i+1}"
        
        segment = Segment(
            name=name,
            segment_code=f"CLUSTER_{i}",
            description=f"Automatically generated segment: {name}",
            criteria={"auto_generated": True, "cluster_id": i},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        segments.append(segment)
    
    return segments

def save_to_database(candidates, segments=None):
    """Save generated data to the database.
    
    Args:
        candidates (list): List of Candidate instances
        segments (list, optional): List of Segment instances
    """
    app = create_app()
    
    with app.app_context():
        print(f"Saving {len(candidates)} candidates to database...")
        
        # Add candidates
        for candidate in candidates:
            db.session.add(candidate)
        
        # Add segments if provided
        if segments:
            print(f"Saving {len(segments)} segments to database...")
            for segment in segments:
                db.session.add(segment)
        
        # Commit changes
        db.session.commit()
        
        print("Database save complete!")

def main(candidate_count=50, segment_count=5):
    """Generate and save data for segmentation."""
    print(f"Generating {candidate_count} candidates and {segment_count} segments...")
    
    candidates = generate_candidates(candidate_count)
    segments = generate_segments(segment_count)
    
    save_to_database(candidates, segments)
    
    print("Data generation complete.")

if __name__ == '__main__':
    # Allow command-line arguments
    candidate_count = 50
    segment_count = 5
    
    if len(sys.argv) > 1:
        candidate_count = int(sys.argv[1])
    if len(sys.argv) > 2:
        segment_count = int(sys.argv[2])
    
    main(candidate_count, segment_count)
