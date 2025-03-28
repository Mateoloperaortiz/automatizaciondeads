"""
Data generator for simulated candidate and job opening data.
"""
import pandas as pd
import numpy as np
from faker import Faker
import random
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility
random.seed(42)
np.random.seed(42)

class DataGenerator:
    """Class for generating simulated data for Ad Automation P-01 project."""
    
    def __init__(self):
        """Initialize the data generator."""
        self.db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/ad_automation')
        self.engine = create_engine(self.db_url)
        
        # Define constants for generation
        self.education_levels = [
            'High School', 'Associate Degree', "Bachelor's Degree", 
            "Master's Degree", 'PhD', 'Vocational Training'
        ]
        
        self.fields_of_study = [
            'Computer Science', 'Business Administration', 'Engineering',
            'Marketing', 'Finance', 'Psychology', 'Data Science',
            'Graphic Design', 'Healthcare', 'Education'
        ]
        
        self.job_types = [
            'Full-time', 'Part-time', 'Contract', 'Freelance',
            'Remote', 'Hybrid', 'Internship'
        ]
        
        self.industries = [
            'Technology', 'Finance', 'Healthcare', 'Education',
            'Retail', 'Manufacturing', 'Entertainment', 'Hospitality',
            'Construction', 'Transportation'
        ]
        
        self.roles = [
            'Software Engineer', 'Data Scientist', 'Project Manager',
            'Marketing Specialist', 'Financial Analyst', 'HR Manager',
            'Customer Support Specialist', 'Sales Representative',
            'Product Manager', 'UX Designer', 'Operations Manager',
            'Administrative Assistant', 'Business Analyst'
        ]
        
        self.company_domains = [
            'tech', 'finance', 'health', 'edu', 'retail', 'media',
            'industrial', 'services', 'consulting', 'ai'
        ]
        
        self.company_types = [
            'Inc.', 'LLC', 'Corp.', 'Co.', 'Ltd.', 'Group',
            'Solutions', 'Systems', 'Technologies', 'Partners'
        ]
        
        self.experience_levels = [
            'Entry-level', 'Mid-level', 'Senior', 'Manager',
            'Director', 'Executive'
        ]
        
        self.locations = [
            'New York, NY', 'San Francisco, CA', 'Austin, TX',
            'Chicago, IL', 'Seattle, WA', 'Boston, MA',
            'Los Angeles, CA', 'Denver, CO', 'Atlanta, GA',
            'Miami, FL', 'Dallas, TX', 'Portland, OR'
        ]
        
        self.platform_names = [
            'Meta', 'Facebook', 'Instagram', 'Twitter', 'X',
            'Google', 'LinkedIn', 'TikTok', 'Snapchat'
        ]
    
    def generate_candidates(self, n_candidates=100):
        """
        Generate simulated candidate data.
        
        Args:
            n_candidates (int): Number of candidates to generate.
            
        Returns:
            DataFrame: DataFrame containing simulated candidate data.
        """
        candidates = []
        
        for _ in range(n_candidates):
            candidate = {
                'age': random.randint(18, 65),
                'gender': random.choice(['Male', 'Female', 'Non-binary', 'Prefer not to say']),
                'location': random.choice(self.locations),
                'education_level': random.choice(self.education_levels),
                'field_of_study': random.choice(self.fields_of_study),
                'years_of_experience': random.randint(0, 25),
                'desired_job_type': random.choice(self.job_types),
                'desired_industry': random.choice(self.industries),
                'desired_role': random.choice(self.roles),
                'desired_salary': random.randint(30000, 150000)
            }
            
            candidates.append(candidate)
        
        return pd.DataFrame(candidates)
    
    def generate_job_openings(self, n_jobs=20):
        """
        Generate simulated job opening data.
        
        Args:
            n_jobs (int): Number of job openings to generate.
            
        Returns:
            DataFrame: DataFrame containing simulated job opening data.
        """
        job_openings = []
        
        for _ in range(n_jobs):
            role = random.choice(self.roles)
            industry = random.choice(self.industries)
            company_name = f"{fake.last_name()} {random.choice(self.company_domains).title()} {random.choice(self.company_types)}"
            location = random.choice(self.locations)
            job_type = random.choice(self.job_types)
            experience_level = random.choice(self.experience_levels)
            
            min_salary = random.randint(30000, 90000)
            max_salary = min_salary + random.randint(10000, 60000)
            salary_range = f"${min_salary // 1000}k - ${max_salary // 1000}k"
            
            # Generate a more detailed description
            description = f"{role} position at {company_name}. "
            description += f"We are seeking a motivated {experience_level} {role} to join our growing team. "
            description += f"The ideal candidate will have experience in {industry} industry and be comfortable in a {job_type} position. "
            description += fake.paragraph(nb_sentences=5)
            
            # Generate requirements
            requirements = f"- {experience_level} experience as a {role} or similar role\n"
            requirements += f"- Knowledge of {industry} industry\n"
            requirements += f"- Strong communication and teamwork skills\n"
            requirements += f"- {random.choice(self.education_levels)} in {random.choice(self.fields_of_study)} or related field\n"
            requirements += f"- Proficiency in relevant tools and technologies\n"
            
            job_opening = {
                'title': role,
                'company': company_name,
                'location': location,
                'description': description,
                'requirements': requirements,
                'salary_range': salary_range,
                'job_type': job_type,
                'experience_level': experience_level,
                'active': True
            }
            
            job_openings.append(job_opening)
        
        return pd.DataFrame(job_openings)
    
    def generate_social_media_platforms(self):
        """
        Generate social media platform data.
        
        Returns:
            DataFrame: DataFrame containing simulated social media platform data.
        """
        platforms = []
        
        for name in self.platform_names:
            platform = {
                'name': name,
                'api_key': fake.uuid4(),
                'api_secret': fake.uuid4(),
                'access_token': fake.uuid4(),
                'active': True
            }
            
            platforms.append(platform)
        
        return pd.DataFrame(platforms)
    
    def insert_candidates_to_db(self, candidates_df):
        """
        Insert candidate data into the database.
        
        Args:
            candidates_df (DataFrame): DataFrame containing candidate data.
            
        Returns:
            int: Number of records inserted.
        """
        try:
            # Create a connection to the database
            with self.engine.connect() as connection:
                # Insert data
                for index, row in candidates_df.iterrows():
                    query = """
                    INSERT INTO candidates (
                        age, gender, location, education_level, field_of_study,
                        years_of_experience, desired_job_type, desired_industry,
                        desired_role, desired_salary, created_at, updated_at
                    ) VALUES (
                        :age, :gender, :location, :education_level, :field_of_study,
                        :years_of_experience, :desired_job_type, :desired_industry,
                        :desired_role, :desired_salary, NOW(), NOW()
                    )
                    """
                    
                    connection.execute(query, row.to_dict())
            
            print(f"Inserted {len(candidates_df)} candidates into the database")
            return len(candidates_df)
            
        except Exception as e:
            print(f"Error inserting candidates: {str(e)}")
            return 0
    
    def insert_job_openings_to_db(self, job_openings_df):
        """
        Insert job opening data into the database.
        
        Args:
            job_openings_df (DataFrame): DataFrame containing job opening data.
            
        Returns:
            int: Number of records inserted.
        """
        try:
            # Create a connection to the database
            with self.engine.connect() as connection:
                # Insert data
                for index, row in job_openings_df.iterrows():
                    query = """
                    INSERT INTO job_openings (
                        title, company, location, description, requirements,
                        salary_range, job_type, experience_level, active,
                        created_at, updated_at
                    ) VALUES (
                        :title, :company, :location, :description, :requirements,
                        :salary_range, :job_type, :experience_level, :active,
                        NOW(), NOW()
                    )
                    """
                    
                    connection.execute(query, row.to_dict())
            
            print(f"Inserted {len(job_openings_df)} job openings into the database")
            return len(job_openings_df)
            
        except Exception as e:
            print(f"Error inserting job openings: {str(e)}")
            return 0
    
    def insert_platforms_to_db(self, platforms_df):
        """
        Insert social media platform data into the database.
        
        Args:
            platforms_df (DataFrame): DataFrame containing platform data.
            
        Returns:
            int: Number of records inserted.
        """
        try:
            # Create a connection to the database
            with self.engine.connect() as connection:
                # Insert data
                for index, row in platforms_df.iterrows():
                    # Check if platform already exists
                    check_query = f"SELECT id FROM social_media_platforms WHERE name = '{row['name']}'"
                    result = connection.execute(check_query).fetchone()
                    
                    if result:
                        print(f"Platform {row['name']} already exists in the database")
                        continue
                    
                    query = """
                    INSERT INTO social_media_platforms (
                        name, api_key, api_secret, access_token, active
                    ) VALUES (
                        :name, :api_key, :api_secret, :access_token, :active
                    )
                    """
                    
                    connection.execute(query, row.to_dict())
            
            print(f"Inserted {len(platforms_df)} social media platforms into the database")
            return len(platforms_df)
            
        except Exception as e:
            print(f"Error inserting platforms: {str(e)}")
            return 0

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate simulated data for Ad Automation P-01 project')
    parser.add_argument('--candidates', type=int, default=100, help='Number of candidates to generate')
    parser.add_argument('--jobs', type=int, default=20, help='Number of job openings to generate')
    parser.add_argument('--no-insert', action='store_true', help='Do not insert data into the database')
    args = parser.parse_args()
    
    generator = DataGenerator()
    
    # Generate data
    candidates_df = generator.generate_candidates(args.candidates)
    job_openings_df = generator.generate_job_openings(args.jobs)
    platforms_df = generator.generate_social_media_platforms()
    
    # Save to CSV
    candidates_df.to_csv('ml/data/candidates.csv', index=False)
    job_openings_df.to_csv('ml/data/job_openings.csv', index=False)
    platforms_df.to_csv('ml/data/platforms.csv', index=False)
    
    print(f"Generated {len(candidates_df)} candidates")
    print(f"Generated {len(job_openings_df)} job openings")
    print(f"Generated {len(platforms_df)} social media platforms")
    print(f"Data saved to CSV files in ml/data/")
    
    # Create data directory if it doesn't exist
    os.makedirs('ml/data', exist_ok=True)
    
    # Insert data into the database
    if not args.no_insert:
        generator.insert_candidates_to_db(candidates_df)
        generator.insert_job_openings_to_db(job_openings_df)
        generator.insert_platforms_to_db(platforms_df) 