"""
Machine learning module for candidate clustering and audience segmentation.
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import silhouette_score
import joblib
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CandidateClusteringModel:
    """
    Machine learning model for clustering candidates into audience segments.
    Uses K-means clustering with preprocessed features.
    """
    
    def __init__(self, n_clusters=5):
        """
        Initialize the clustering model.
        
        Args:
            n_clusters (int): Number of clusters to create.
        """
        self.n_clusters = n_clusters
        self.model = None
        self.preprocessor = None
        self.model_path = 'ml/models/candidate_clustering_model.joblib'
        self.preprocessor_path = 'ml/models/candidate_preprocessor.joblib'
        
        # Ensure model directory exists
        os.makedirs('ml/models', exist_ok=True)
    
    def preprocess_data(self, candidates_df):
        """
        Preprocess candidate data for clustering.
        
        Args:
            candidates_df (DataFrame): DataFrame containing candidate data.
            
        Returns:
            ndarray: Preprocessed features ready for clustering.
        """
        # Define numeric features
        numeric_features = ['age', 'years_of_experience', 'desired_salary']
        
        # Define categorical features
        categorical_features = ['gender', 'education_level', 'desired_job_type', 'desired_industry']
        
        # Create preprocessor
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])
        
        # Save the preprocessor for future use
        self.preprocessor = preprocessor
        
        # Fit and transform the data
        X_processed = preprocessor.fit_transform(candidates_df[numeric_features + categorical_features])
        
        return X_processed
    
    def find_optimal_clusters(self, X_processed, max_clusters=10):
        """
        Find the optimal number of clusters using silhouette score.
        
        Args:
            X_processed (ndarray): Preprocessed features.
            max_clusters (int): Maximum number of clusters to consider.
            
        Returns:
            int: Optimal number of clusters.
        """
        silhouette_scores = []
        for n_clusters in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_processed)
            silhouette_avg = silhouette_score(X_processed, cluster_labels)
            silhouette_scores.append(silhouette_avg)
            print(f"Silhouette score for n_clusters = {n_clusters}: {silhouette_avg}")
        
        # Find the optimal number of clusters (highest silhouette score)
        optimal_clusters = np.argmax(silhouette_scores) + 2  # +2 because we start from 2 clusters
        
        return optimal_clusters
    
    def train(self, candidates_df, find_optimal=True, max_clusters=10):
        """
        Train the clustering model on candidate data.
        
        Args:
            candidates_df (DataFrame): DataFrame containing candidate data.
            find_optimal (bool): Whether to find the optimal number of clusters.
            max_clusters (int): Maximum number of clusters to consider if find_optimal is True.
            
        Returns:
            self: The trained model instance.
        """
        # Preprocess the data
        X_processed = self.preprocess_data(candidates_df)
        
        # Find optimal number of clusters if requested
        if find_optimal:
            self.n_clusters = self.find_optimal_clusters(X_processed, max_clusters)
            print(f"Selected optimal number of clusters: {self.n_clusters}")
        
        # Train the K-means model
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        kmeans.fit(X_processed)
        self.model = kmeans
        
        # Save the model and preprocessor
        self.save_model()
        
        return self
    
    def predict(self, candidates_df):
        """
        Predict cluster assignments for candidates.
        
        Args:
            candidates_df (DataFrame): DataFrame containing candidate data.
            
        Returns:
            ndarray: Cluster assignments for each candidate.
        """
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model or preprocessor not initialized. Train or load the model first.")
        
        # Get relevant features
        numeric_features = ['age', 'years_of_experience', 'desired_salary']
        categorical_features = ['gender', 'education_level', 'desired_job_type', 'desired_industry']
        
        # Use the same preprocessor from training
        X_processed = self.preprocessor.transform(candidates_df[numeric_features + categorical_features])
        
        # Predict clusters
        clusters = self.model.predict(X_processed)
        
        return clusters
    
    def save_model(self):
        """Save the trained model and preprocessor to disk."""
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model or preprocessor not initialized. Train the model first.")
        
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.preprocessor, self.preprocessor_path)
        
        print(f"Model saved to {self.model_path}")
        print(f"Preprocessor saved to {self.preprocessor_path}")
    
    def load_model(self):
        """Load a trained model and preprocessor from disk."""
        try:
            self.model = joblib.load(self.model_path)
            self.preprocessor = joblib.load(self.preprocessor_path)
            self.n_clusters = self.model.n_clusters
            
            print(f"Model loaded from {self.model_path}")
            print(f"Preprocessor loaded from {self.preprocessor_path}")
            print(f"Number of clusters: {self.n_clusters}")
            
            return True
        except FileNotFoundError as e:
            print(f"Model or preprocessor file not found: {e.filename}. Train the model first.")
            return False
        except AttributeError as e:
            print(f"Invalid model format: {str(e)}. The model might be corrupted or incompatible.")
            return False
        except (OSError, IOError) as e:
            print(f"I/O error loading model: {str(e)}")
            return False
        except ValueError as e:
            print(f"Invalid model data: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error loading model: {e.__class__.__name__}: {str(e)}")
            return False
    
    def get_cluster_characteristics(self, candidates_df, clusters):
        """
        Get characteristics of each cluster.
        
        Args:
            candidates_df (DataFrame): DataFrame containing candidate data.
            clusters (ndarray): Cluster assignments for each candidate.
            
        Returns:
            dict: Characteristics of each cluster.
        """
        # Add cluster assignments to the dataframe
        candidates_df = candidates_df.copy()
        candidates_df['cluster'] = clusters
        
        # Get characteristics for each cluster
        cluster_chars = {}
        
        for cluster_id in range(self.n_clusters):
            cluster_data = candidates_df[candidates_df['cluster'] == cluster_id]
            
            if len(cluster_data) == 0:
                continue
            
            # Calculate numeric feature averages
            avg_age = cluster_data['age'].mean()
            avg_experience = cluster_data['years_of_experience'].mean()
            avg_salary = cluster_data['desired_salary'].mean()
            
            # Calculate categorical feature distributions
            gender_dist = cluster_data['gender'].value_counts(normalize=True).to_dict()
            education_dist = cluster_data['education_level'].value_counts(normalize=True).to_dict()
            job_type_dist = cluster_data['desired_job_type'].value_counts(normalize=True).to_dict()
            industry_dist = cluster_data['desired_industry'].value_counts(normalize=True).to_dict()
            
            # Combine characteristics
            cluster_chars[cluster_id] = {
                'size': len(cluster_data),
                'avg_age': avg_age,
                'avg_experience': avg_experience,
                'avg_salary': avg_salary,
                'gender_distribution': gender_dist,
                'education_distribution': education_dist,
                'job_type_distribution': job_type_dist,
                'industry_distribution': industry_dist
            }
        
        return cluster_chars
    
    def update_candidate_segments(self, candidates_df):
        """
        Update the segment_id field for candidates in the database.
        
        Args:
            candidates_df (DataFrame): DataFrame containing candidate data with IDs.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Predict clusters
            clusters = self.predict(candidates_df)
            
            # Add cluster assignments to the dataframe
            candidates_df = candidates_df.copy()
            candidates_df['segment_id'] = clusters
            
            # Connect to the database
            db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/ad_automation')
            engine = create_engine(db_url)
            
            # Update segment_id in the database
            for index, row in candidates_df.iterrows():
                candidate_id = row['id']
                segment_id = row['segment_id']
                
                # Update the segment_id in the database
                update_query = f"""
                UPDATE candidates
                SET segment_id = {segment_id}
                WHERE id = {candidate_id}
                """
                
                engine.execute(update_query)
            
            print(f"Updated segment_id for {len(candidates_df)} candidates")
            return True
            
        except ValueError as e:
            print(f"Prediction error - invalid input data: {str(e)}")
            return False
        except KeyError as e:
            print(f"Missing required column in DataFrame: {str(e)}")
            return False
        except ImportError as e:
            print(f"SQLAlchemy database library not available: {str(e)}")
            return False
        except (OSError, IOError) as e:
            print(f"Database connection error: {str(e)}")
            return False
        except Exception as e:
            print(f"Error updating candidate segments: {e.__class__.__name__}: {str(e)}")
            return False
    
    @staticmethod
    def load_candidates_from_db():
        """
        Load candidate data from the database.
        
        Returns:
            DataFrame: DataFrame containing candidate data.
        """
        try:
            # Connect to the database
            db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/ad_automation')
            engine = create_engine(db_url)
            
            # Query the database
            query = """
            SELECT id, age, gender, location, education_level, field_of_study,
                   years_of_experience, desired_job_type, desired_industry,
                   desired_role, desired_salary, segment_id
            FROM candidates
            """
            
            candidates_df = pd.read_sql(query, engine)
            
            print(f"Loaded {len(candidates_df)} candidates from the database")
            return candidates_df
            
        except ImportError as e:
            print(f"Required database library not available: {str(e)}")
            return None
        except (OSError, IOError) as e:
            print(f"Database connection error: {str(e)}")
            return None
        except pd.io.sql.DatabaseError as e:
            print(f"SQL query error: {str(e)}")
            return None
        except ValueError as e:
            print(f"Value error in database connection parameters: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error loading candidates from database: {e.__class__.__name__}: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    # Load candidate data
    candidates_df = CandidateClusteringModel.load_candidates_from_db()
    
    if candidates_df is not None and len(candidates_df) > 0:
        # Initialize and train the model
        model = CandidateClusteringModel(n_clusters=5)
        model.train(candidates_df, find_optimal=True)
        
        # Predict clusters
        clusters = model.predict(candidates_df)
        
        # Get cluster characteristics
        characteristics = model.get_cluster_characteristics(candidates_df, clusters)
        
        # Print characteristics
        for cluster_id, chars in characteristics.items():
            print(f"\nCluster {cluster_id} ({chars['size']} candidates):")
            print(f"Average age: {chars['avg_age']:.1f}")
            print(f"Average experience: {chars['avg_experience']:.1f} years")
            print(f"Average desired salary: ${chars['avg_salary']:,.2f}")
            
            print("\nTop education levels:")
            for edu, pct in sorted(chars['education_distribution'].items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"  - {edu}: {pct*100:.1f}%")
            
            print("\nTop desired industries:")
            for ind, pct in sorted(chars['industry_distribution'].items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"  - {ind}: {pct*100:.1f}%")
        
        # Update segments in the database
        model.update_candidate_segments(candidates_df)
    else:
        print("No candidate data available. Please ensure the database is populated.") 