import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import joblib
import os

class AudienceSegmentation:
    """Class for audience segmentation using K-means clustering."""
    
    def __init__(self, n_clusters=5, random_state=42):
        """Initialize segmentation model with parameters."""
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'age', 'years_experience', 'location_encoded', 'education_level_encoded',
            'job_preferences_encoded', 'industry_encoded'
        ]
    
    def preprocess_data(self, df):
        """Preprocess candidate data for clustering."""
        # Ensure all required columns exist
        for col in self.feature_columns:
            if col not in df.columns:
                print(f"Warning: Column {col} not found, adding with zeros")
                df[col] = 0
        
        # Handle missing values
        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            df[col] = df[col].fillna(df[col].median() if not df[col].isna().all() else 0)
        
        # Make sure we're using only the columns we need
        df_filtered = df[self.feature_columns].copy()
        
        # Scale numerical features
        df_scaled = pd.DataFrame(
            self.scaler.fit_transform(df_filtered),
            columns=self.feature_columns,
            index=df.index
        )
        
        return df_scaled
    
    def train(self, df):
        """Train K-means clustering model on preprocessed data."""
        # Make a copy to avoid modifying the original dataframe
        df_copy = df.copy()
        
        # Remove non-feature columns if they exist
        for col in ['id', 'candidate_id']:
            if col in df_copy.columns:
                df_copy = df_copy.drop(columns=[col])
        
        # Preprocess data
        df_processed = self.preprocess_data(df_copy)
        
        # Find optimal number of clusters using silhouette score if not specified
        if self.n_clusters is None:
            best_score = -1
            best_k = 2
            
            for k in range(2, min(11, len(df) // 10)):  # Try up to 10 clusters or 1/10 of data points
                kmeans = KMeans(n_clusters=k, random_state=self.random_state)
                labels = kmeans.fit_predict(df_processed)
                
                score = silhouette_score(df_processed, labels)
                print(f"Silhouette score for k={k}: {score}")
                
                if score > best_score:
                    best_score = score
                    best_k = k
            
            self.n_clusters = best_k
            print(f"Selected optimal number of clusters: {self.n_clusters}")
        
        # Train the model with selected number of clusters
        self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        self.model.fit(df_processed)
        
        # Evaluate model
        labels = self.model.labels_
        if len(set(labels)) > 1:  # Only calculate silhouette if we have more than one cluster
            score = silhouette_score(df_processed, labels)
            print(f"Final model silhouette score: {score}")
        else:
            print("Warning: Only one cluster was created. Silhouette score requires at least 2 clusters.")
        
        return self.model
    
    def predict(self, df):
        """Predict cluster for new data."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Make a copy to avoid modifying the original dataframe
        df_copy = df.copy()
        
        # Remove non-feature columns if they exist
        for col in ['id', 'candidate_id']:
            if col in df_copy.columns:
                df_copy = df_copy.drop(columns=[col])
        
        # Preprocess data
        df_processed = self.preprocess_data(df_copy)
        
        # Predict cluster
        return self.model.predict(df_processed)
    
    def save_model(self, path='ml/models/kmeans_model.pkl'):
        """Save trained model to file."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create directories if they don't exist
        model_dir = os.path.dirname(path)
        os.makedirs(model_dir, exist_ok=True)
        
        # Create __init__.py if needed to make it a proper package
        init_file = os.path.join(model_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Machine Learning models directory\n')
        
        # Save model and scaler
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'n_clusters': self.n_clusters,
            'feature_columns': self.feature_columns
        }, path)
        
        print(f"Model saved to {path}")
    
    def load_model(self, path='ml/models/kmeans_model.pkl'):
        """Load trained model from file."""
        if not os.path.exists(path):
            print(f"Model file not found: {path}")
            print("Will train a new model when needed.")
            return None
        
        try:
            # Load model and scaler
            data = joblib.load(path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.n_clusters = data['n_clusters']
            self.feature_columns = data['feature_columns']
            
            print(f"Model loaded from {path}")
            return self
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            print("Will train a new model when needed.")
            return None
    
    def generate_demo_candidates(self, count=50):
        """Generate demo candidates for development and testing.
        
        Args:
            count (int): Number of candidates to generate
            
        Returns:
            list: Generated candidate objects
        """
        from app.models.candidate import Candidate
        from app import db
        import random
        from datetime import datetime, timedelta
        from faker import Faker
        import time
        from sqlalchemy import inspect
        
        # Initialize faker with a seed for reproducibility
        seed = int(time.time())
        fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
        
        # Define demo data - use tuples for slightly better performance
        education_levels = ('High School', 'Bachelor', 'Master', 'PhD')
        job_roles = ('Software Engineer', 'Data Scientist', 'Product Manager', 
                    'UX Designer', 'Marketing Specialist', 'Sales Representative',
                    'HR Manager', 'Financial Analyst', 'Project Manager')
        locations = ('New York', 'San Francisco', 'Chicago', 'Seattle', 'Austin',
                     'Boston', 'Los Angeles', 'Miami', 'Denver', 'Remote')
        industries = ('Technology', 'Finance', 'Healthcare', 'Education', 'Retail')
        job_types = ('Full-time', 'Part-time', 'Contract')
        fields_of_study = ('Computer Science', 'Business', 'Engineering', 'Marketing', 'Psychology')
        genders = ('Male', 'Female', 'Non-binary', 'Prefer not to say')
        
        # Generate data more efficiently in batches
        print(f"Generating {count} demo candidates...")
        candidates = []
        
        # Get the actual table columns to avoid setting attributes that don't exist
        inspector = inspect(Candidate)
        column_names = set(c.key for c in inspector.columns)
        
        # Generate in batches of 100 or less
        batch_size = min(100, count)
        total_created = 0
        batch_number = 0
        
        while total_created < count:
            batch_number += 1
            current_batch_size = min(batch_size, count - total_created)
            
            batch_candidates = []
            now = datetime.now()
            
            for i in range(current_batch_size):
                # Generate random candidate attributes
                age = random.randint(22, 55)
                experience = random.randint(0, 20)
                
                # Only create attributes that exist in the database table
                candidate_data = {
                    'age': age,
                    'years_of_experience': experience,
                    'desired_salary': random.randint(40000, 120000),
                    'created_at': now - timedelta(days=random.randint(1, 90))
                }
                
                # Add optional fields if they exist in the database
                if 'gender' in column_names:
                    candidate_data['gender'] = random.choice(genders)
                if 'location' in column_names:
                    candidate_data['location'] = random.choice(locations)
                if 'education_level' in column_names:
                    candidate_data['education_level'] = random.choice(education_levels)
                if 'field_of_study' in column_names:
                    candidate_data['field_of_study'] = random.choice(fields_of_study)
                if 'desired_job_type' in column_names:
                    candidate_data['desired_job_type'] = random.choice(job_types)
                if 'desired_industry' in column_names:
                    candidate_data['desired_industry'] = random.choice(industries)
                if 'desired_role' in column_names:
                    candidate_data['desired_role'] = random.choice(job_roles)
                
                # Create candidate object
                candidate = Candidate(**candidate_data)
                batch_candidates.append(candidate)
            
            # Save batch to database
            try:
                with db.session.begin():
                    db.session.bulk_save_objects(batch_candidates)
                
                total_created += len(batch_candidates)
                candidates.extend(batch_candidates)
                print(f"Batch {batch_number}: Added {len(batch_candidates)} candidates (Total: {total_created})")
                
            except Exception as e:
                print(f"Error adding candidates batch {batch_number}: {str(e)}")
                # Continue with next batch instead of failing completely
        
        print(f"Added {len(candidates)} demo candidates to the database")
        return candidates
            
    def visualize_clusters(self, df, save_path=None):
        """Visualize clusters using PCA for dimensionality reduction."""
        import matplotlib.pyplot as plt
        import gc  # For garbage collection
        
        # Process the dataframe more efficiently - operate on the original data 
        # without making unnecessary copies
        df_vis = df.copy() if len(df) < 5000 else df.sample(n=5000, random_state=42)
        print(f"Visualizing {len(df_vis)} data points (sampled from {len(df)})")
        
        # Drop non-feature columns if they exist (more efficient than copy+drop)
        df_vis = df_vis.drop(columns=['id', 'candidate_id'], errors='ignore')
        
        # Ensure all feature columns exist more efficiently
        for col in self.feature_columns:
            if col not in df_vis.columns:
                print(f"Warning: Column {col} not found, adding with zeros")
                df_vis[col] = 0
        
        # Filter to only needed columns before preprocessing to reduce memory
        df_vis = df_vis[self.feature_columns]
        
        # Preprocess data (without additional copying)
        df_processed = self.preprocess_data(df_vis)
        
        # Clean up to free memory
        del df_vis
        gc.collect()
        
        # Predict clusters
        labels = self.model.predict(df_processed)
        
        # Reduce dimensions for visualization using only 2 components
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(df_processed)
        
        # Clean up to free memory
        del df_processed
        gc.collect()
        
        # Plot clusters with reduced memory footprint
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, 
                              cmap='viridis', alpha=0.8, s=20)  # Smaller point size
        plt.colorbar(scatter, label='Cluster')
        plt.title('Audience Segments')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        
        # Add cluster centers
        centers = pca.transform(self.model.cluster_centers_)
        plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='x', s=100, linewidths=2)
        
        # Save plot if path is provided
        if save_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Use a memory-efficient format and DPI setting
            plt.savefig(save_path, dpi=100, bbox_inches='tight', format='png')
            print(f"Visualization saved to {save_path}")
        
        plt.show()
        
        # Final cleanup
        plt.close()
        gc.collect()
        
    def run_segmentation(self, candidates_df=None):
        """Run the entire segmentation process on the candidate data.
        If no dataframe is provided, it will fetch data from the database.
        
        Returns:
            dict: A dictionary with segmentation results.
        """
        from app.models.candidate import Candidate
        from app.models.segment import Segment, candidate_segments
        from app import db
        from sqlalchemy import text, func
        import pandas as pd
        from sqlalchemy.orm import joinedload
        
        print("Starting audience segmentation process...")
        
        # Get candidates data if not provided
        if candidates_df is None:
            print("Fetching candidates from database...")
            # Use optimized query with limit and selective column loading
            # Note: Only fetch columns needed for segmentation to reduce memory usage
            query = db.session.query(
                Candidate.id,
                Candidate.age,
                Candidate.years_of_experience,
                Candidate.location,
                Candidate.education_level,
                Candidate.desired_role,
                Candidate.desired_industry
            )
            
            # Execute query and get results
            candidates_result = query.all()
            
            if not candidates_result:
                print("No candidates found in database, generating demo candidates...")
                # Generate demo candidates for development purposes
                self.generate_demo_candidates(50)  # Generate 50 demo candidates
                
                # Fetch again after generating - this time with the limited columns
                candidates_result = query.all()
                
                if not candidates_result:
                    raise ValueError("Failed to create demo candidates")
            
            # Convert to DataFrame more efficiently
            # Define education level mapping once
            education_mapping = {
                'High School': 1,
                'Bachelor': 2,
                'Master': 3,
                'PhD': 4
            }
            
            # Pre-compute candidate features in a more optimized way
            candidates_data = []
            for c in candidates_result:
                # Create dictionary with candidate features (exclude ID from features)
                candidates_data.append({
                    'candidate_id': c.id,
                    'age': c.age or 30,  # Default age if missing
                    'years_experience': int(c.years_of_experience or 0),
                    'location_encoded': hash(c.location) % 100 if c.location else 0,  # Simple encoding for demo
                    'education_level_encoded': education_mapping.get(c.education_level, 0),
                    'job_preferences_encoded': hash(c.desired_role) % 100 if c.desired_role else 0,  # Simple encoding for demo
                    'industry_encoded': hash(c.desired_industry) % 100 if c.desired_industry else 0  # Simple encoding for industry
                })
                
            candidates_df = pd.DataFrame(candidates_data)
        
        print(f"Processing {len(candidates_df)} candidates...")
        
        # Clear existing segments using more efficient SQL
        print("Clearing existing segments...")
        # Use a single transaction for all deletions
        with db.session.begin():
            # Delete association table records first (due to foreign key constraints)
            db.session.execute(text("DELETE FROM candidate_segments"))
            # Then delete segments
            db.session.execute(text("DELETE FROM segments"))
        
        # Train model
        print(f"Training segmentation model with {self.n_clusters} clusters...")
        self.train(candidates_df)
        
        # Save the trained model
        self.save_model()
        
        # Get cluster assignments
        cluster_labels = self.model.labels_
        
        # Create segments based on clusters
        print("Creating segments based on clustering results...")
        segments = []
        segment_candidates_count = {}
        segment_candidate_map = {}  # Will store segment_id -> list of candidate_ids
        
        # Create all segments in a batch
        for i in range(self.n_clusters):
            # Analyze cluster to generate description
            cluster_indices = [idx for idx, label in enumerate(cluster_labels) if label == i]
            cluster_size = len(cluster_indices)
            segment_candidates_count[i] = cluster_size
            
            # Extract sample data for description (limit calculations to what's needed)
            description = "Empty segment with no candidates."
            if cluster_indices:
                # Only compute statistics if cluster has members
                cluster_df = candidates_df.iloc[cluster_indices]
                avg_age = cluster_df['age'].mean() if 'age' in cluster_df else 0
                avg_exp = cluster_df['years_experience'].mean() if 'years_experience' in cluster_df else 0
                
                description = f"Age: Average {avg_age:.1f} years. Experience: Average {avg_exp:.1f} years."
                
                if len(cluster_indices) > 10:
                    description += f" This is a {'large' if cluster_size > 30 else 'medium-sized'} segment with {cluster_size} candidates."
                else:
                    description += f" This is a small segment with only {cluster_size} candidates."
                
                # Build the list of candidate IDs for this segment
                if 'candidate_id' in cluster_df.columns:
                    segment_candidate_map[i] = cluster_df['candidate_id'].tolist()
            
            # Create segment
            segment = Segment(
                name=f"Segment {i+1}",
                segment_code=f"CLUSTER_{i}",
                description=description,
                criteria={
                    "cluster_id": i,
                    "algorithm": "KMeans",
                    "parameters": {
                        "n_clusters": self.n_clusters,
                        "random_state": self.random_state
                    }
                }
            )
            segments.append(segment)
        
        # Bulk add all segments at once
        db.session.add_all(segments)
        db.session.flush()  # Flush to get the segment IDs without committing
        
        # Assign candidates to segments using bulk operations
        print("Assigning candidates to segments...")
        
        # Use batch insertion for the candidate_segments association
        if 'candidate_id' in candidates_df.columns:
            candidate_segment_records = []
            
            # First, prepare the association records
            for segment_index, segment in enumerate(segments):
                if segment_index in segment_candidate_map:
                    candidate_ids = segment_candidate_map[segment_index]
                    for candidate_id in candidate_ids:
                        # Store the candidate ID in the segment's candidate_ids JSON field
                        if segment._candidate_ids is None:
                            segment._candidate_ids = []
                        if segment._candidate_ids is not None and candidate_id not in segment._candidate_ids:
                            segment._candidate_ids.append(candidate_id)
                        
                        # Create association record for the many-to-many relationship
                        candidate_segment_records.append({
                            "candidate_id": candidate_id, 
                            "segment_id": segment.id
                        })
            
            # Execute a bulk insert for the association records (if any)
            if candidate_segment_records:
                db.session.execute(
                    candidate_segments.insert(),
                    candidate_segment_records
                )
        
        # Commit all changes at once
        db.session.commit()
        
        print("Segmentation process completed successfully!")
        
        # Prepare data for silhouette score
        try:
            # Make a copy of the dataframe excluding non-feature columns more efficiently
            df_for_silhouette = candidates_df.drop(columns=['candidate_id'], errors='ignore')
            
            # Calculate silhouette score if we have more than one cluster
            silhouette = 0
            if len(set(cluster_labels)) > 1:
                # Only transform the features we actually need
                feature_data = df_for_silhouette[self.feature_columns]
                silhouette = silhouette_score(self.scaler.transform(feature_data), cluster_labels)
        except Exception as e:
            print(f"Error calculating silhouette score: {str(e)}")
            silhouette = 0
        
        # Return segmentation results
        return {
            'success': True,
            'segments_count': len(segments),
            'segments': [{'id': s.id, 'name': s.name, 'candidate_count': segment_candidates_count.get(i, 0)} 
                         for i, s in enumerate(segments)],
            'silhouette_score': silhouette
        } 