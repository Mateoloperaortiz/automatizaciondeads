"""
Train audience segmentation model using simulated candidate data.

This script trains and saves a K-means clustering model for audience segmentation,
which can be used to target job ads more effectively.
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.segmentation import AudienceSegmentation
from app import create_app, db
from app.models.candidate import Candidate

def load_data_from_db():
    """Load candidate data from database.
    
    Returns:
        pandas.DataFrame: DataFrame with candidate data
    """
    # Create app context for database operations
    app = create_app()
    with app.app_context():
        # Query all candidates
        candidates = Candidate.query.all()
        
        # Convert to dict for pandas
        data = []
        for c in candidates:
            data.append({
                'id': c.id,
                'age': c.age,
                'years_experience': c.years_of_experience,  # Fixed field name
                'location': c.location,
                'education_level': c.education_level,
                'job_preferences': ','.join(c.job_preferences) if c.job_preferences else '',
                'skills': ','.join(c.skills) if c.skills else ''
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} candidates from database")
        return df

def encode_categorical_features(df):
    """Encode categorical features for clustering.
    
    Args:
        df (pandas.DataFrame): DataFrame with candidate data
        
    Returns:
        pandas.DataFrame: DataFrame with encoded features
    """
    # Make a copy to avoid modifying the original
    df_encoded = df.copy()
    
    # Create encoders
    label_enc = LabelEncoder()
    
    # Encode location
    if 'location' in df.columns:
        df_encoded['location_encoded'] = label_enc.fit_transform(df['location'])
    else:
        df_encoded['location_encoded'] = 0
    
    # Encode education level
    if 'education_level' in df.columns:
        df_encoded['education_level_encoded'] = label_enc.fit_transform(df['education_level'])
    else:
        df_encoded['education_level_encoded'] = 0
    
    # Extract and encode job preferences (create dummy variables)
    if 'job_preferences' in df.columns:
        # Get all unique preferences
        all_prefs = set()
        for prefs in df['job_preferences']:
            if isinstance(prefs, str) and prefs:
                all_prefs.update(prefs.split(','))
        
        # Create binary columns for each preference
        for pref in all_prefs:
            df_encoded[f'pref_{pref.lower().replace(" ", "_")}'] = df['job_preferences'].apply(
                lambda x: 1 if isinstance(x, str) and pref in x else 0
            )
        
        # Add summary column for preference count
        df_encoded['job_preferences_encoded'] = df['job_preferences'].apply(
            lambda x: len(x.split(',')) if isinstance(x, str) and x else 0
        )
    else:
        df_encoded['job_preferences_encoded'] = 0
    
    # Extract industry from preferences or job title
    df_encoded['industry_encoded'] = 0  # Default placeholder
    
    return df_encoded

def visualize_clusters(df, labels, n_clusters):
    """Visualize clusters.
    
    Args:
        df (pandas.DataFrame): DataFrame with candidate data
        labels (ndarray): Cluster labels
        n_clusters (int): Number of clusters
    """
    # Create directories for visualizations and models
    os.makedirs('ml/visualizations', exist_ok=True)
    os.makedirs('ml/models', exist_ok=True)
    
    # Add cluster labels to dataframe
    df_viz = df.copy()
    df_viz['cluster'] = labels
    
    # Standardize column names
    if 'years_of_experience' in df_viz.columns and 'years_experience' not in df_viz.columns:
        df_viz['years_experience'] = df_viz['years_of_experience']
    elif 'years_experience' not in df_viz.columns:
        df_viz['years_experience'] = 0
        print("Warning: No experience column found, using zeros")
    
    # Create a combined visualization
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Age distribution
    plt.subplot(2, 2, 1)
    if 'age' in df_viz.columns:
        sns.boxplot(x='cluster', y='age', data=df_viz)
        plt.title('Age Distribution by Cluster')
    else:
        plt.text(0.5, 0.5, 'Age data not available', ha='center', va='center')
        plt.title('Age Distribution (No Data)')
    
    # Plot 2: Experience distribution
    plt.subplot(2, 2, 2)
    try:
        sns.boxplot(x='cluster', y='years_experience', data=df_viz)
        plt.title('Years of Experience by Cluster')
    except Exception as e:
        print(f"Error plotting experience: {str(e)}")
        plt.text(0.5, 0.5, 'Experience plot error', ha='center', va='center')
        plt.title('Experience Distribution (Error)')
    
    # Plot 3: Education level
    plt.subplot(2, 2, 3)
    if 'education_level' in df_viz.columns:
        education_counts = df_viz.groupby(['cluster', 'education_level']).size().unstack().fillna(0)
        if not education_counts.empty:
            education_counts.plot(kind='bar', stacked=True, ax=plt.gca())
            plt.title('Education Level by Cluster')
        else:
            plt.text(0.5, 0.5, 'No education data to plot', ha='center', va='center')
            plt.title('Education (No Data)')
    else:
        plt.text(0.5, 0.5, 'Education data not available', ha='center', va='center')
        plt.title('Education (No Data)')
    
    # Plot 4: Cluster sizes
    plt.subplot(2, 2, 4)
    cluster_sizes = df_viz['cluster'].value_counts().sort_index()
    sns.barplot(x=cluster_sizes.index, y=cluster_sizes.values)
    plt.title('Cluster Sizes')
    plt.xlabel('Cluster')
    plt.ylabel('Number of Candidates')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('ml/models/segment_visualization.png')
    
    # Print cluster summaries
    print("\nCluster Summaries:")
    for i in range(n_clusters):
        cluster_data = df_viz[df_viz['cluster'] == i]
        print(f"\nCluster {i} ({len(cluster_data)} candidates):")
        
        if 'age' in cluster_data.columns:
            print(f"  Age: {cluster_data['age'].mean():.1f} years (avg)")
        
        if 'years_experience' in cluster_data.columns:
            print(f"  Experience: {cluster_data['years_experience'].mean():.1f} years (avg)")
        
        # Most common education level
        if 'education_level' in cluster_data.columns:
            edu_counts = cluster_data['education_level'].value_counts()
            top_edu = edu_counts.index[0] if not edu_counts.empty else 'Unknown'
            print(f"  Education: {top_edu} (most common)")

def save_cluster_descriptions(df, labels, n_clusters):
    """Generate and save human-readable cluster descriptions.
    
    Args:
        df (pandas.DataFrame): DataFrame with candidate data
        labels (ndarray): Cluster labels
        n_clusters (int): Number of clusters
    """
    # Create directory for descriptions
    os.makedirs('ml/models', exist_ok=True)
    
    # Add cluster labels to dataframe
    df_desc = df.copy()
    df_desc['cluster'] = labels
    
    # Standardize column names
    if 'years_of_experience' in df_desc.columns and 'years_experience' not in df_desc.columns:
        df_desc['years_experience'] = df_desc['years_of_experience']
    elif 'years_experience' not in df_desc.columns:
        df_desc['years_experience'] = 0
    
    # Generate descriptions
    descriptions = []
    
    for i in range(n_clusters):
        cluster_data = df_desc[df_desc['cluster'] == i]
        count = len(cluster_data)
        
        # Get average age and experience with error handling
        if 'age' in cluster_data.columns:
            age_avg = cluster_data['age'].mean()
        else:
            age_avg = 30  # Default value
            
        if 'years_experience' in cluster_data.columns:
            exp_avg = cluster_data['years_experience'].mean()
        else:
            exp_avg = 5  # Default value
        
        # Get most common education level
        if 'education_level' in cluster_data.columns:
            edu_counts = cluster_data['education_level'].value_counts()
            top_edu = edu_counts.index[0] if not edu_counts.empty else 'Unknown'
        else:
            top_edu = 'Unknown'
        
        # Get most common location
        if 'location' in cluster_data.columns:
            loc_counts = cluster_data['location'].value_counts()
            top_loc = loc_counts.index[0] if not loc_counts.empty else 'Unknown'
        else:
            top_loc = 'Unknown'
        
        # Generate job preference insights
        job_prefs = []
        if 'job_preferences' in cluster_data.columns:
            all_prefs = []
            for prefs in cluster_data['job_preferences']:
                if isinstance(prefs, str) and prefs:
                    all_prefs.extend(prefs.split(','))
            
            if all_prefs:
                # Count occurrences of each preference
                from collections import Counter
                pref_counts = Counter(all_prefs)
                top_prefs = [pref for pref, _ in pref_counts.most_common(3)]
                job_prefs = top_prefs
        
        # Create human-readable description
        description = {
            'id': i,
            'size': count,
            'name': f"Segment {i}",
            'description': (
                f"Professionals with {exp_avg:.1f} years experience on average, "
                f"typically with {top_edu} education"
            ),
            'characteristics': {
                'age_avg': round(age_avg, 1),
                'experience_avg': round(exp_avg, 1),
                'education': top_edu,
                'location': top_loc,
                'job_preferences': job_prefs
            }
        }
        
        descriptions.append(description)
    
    # Save descriptions to file
    joblib.dump(descriptions, 'ml/models/cluster_descriptions.joblib')
    print(f"Saved cluster descriptions to ml/models/cluster_descriptions.joblib")
    
    # Also print them
    print("\nCluster Descriptions:")
    for desc in descriptions:
        print(f"\nSegment {desc['id']} ({desc['size']} candidates):")
        print(f"  {desc['description']}")
        print(f"  Top location: {desc['characteristics']['location']}")
        print(f"  Job preferences: {', '.join(desc['characteristics']['job_preferences'])}")

def main(n_clusters=5, visualize=True):
    """Train and save the audience segmentation model.
    
    Args:
        n_clusters (int): Number of clusters to create
        visualize (bool): Whether to generate visualizations
    """
    print("Starting audience segmentation model training...")
    print(f"Using {n_clusters} clusters for segmentation")
    
    # Ensure model directory exists
    os.makedirs('ml/models', exist_ok=True)
    
    # Load data from database (or generated files)
    try:
        df = load_data_from_db()
    except ImportError as e:
        print(f"Required database library missing: {str(e)}")
        print("Trying to load from CSV file...")
        fallback_to_csv = True
    except (OSError, IOError) as e:
        print(f"Database connection error: {str(e)}")
        print("Trying to load from CSV file...")
        fallback_to_csv = True
    except ValueError as e:
        print(f"Invalid database configuration: {str(e)}")
        print("Trying to load from CSV file...")
        fallback_to_csv = True
    except Exception as e:
        print(f"Unexpected error loading from database: {e.__class__.__name__}: {str(e)}")
        print("Trying to load from CSV file...")
        fallback_to_csv = True
    else:
        fallback_to_csv = False
        
    # Try to load from CSV file if database loading failed
    if fallback_to_csv:
        csv_path = 'ml/data/candidates.csv'
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                print(f"Loaded {len(df)} candidates from CSV")
            except pd.errors.EmptyDataError:
                print("CSV file is empty. Please run generate_data.py first.")
                return
            except pd.errors.ParserError as e:
                print(f"Error parsing CSV file: {str(e)}")
                return
            except (OSError, IOError) as e:
                print(f"Error reading CSV file: {str(e)}")
                return
        else:
            print("No candidate data found. Please run generate_data.py first.")
            return
    
    # Check for column name mismatches and standardize
    if 'years_of_experience' in df.columns and 'years_experience' not in df.columns:
        df['years_experience'] = df['years_of_experience']
    elif 'years_experience' not in df.columns:
        df['years_experience'] = 0
        print("Warning: No experience column found, adding with zeros")
    
    # Encode categorical features
    try:
        df_encoded = encode_categorical_features(df)
        print(f"Encoded {len(df_encoded.columns)} features for clustering")
    except KeyError as e:
        print(f"Missing required column for feature encoding: {str(e)}")
        print("Using original data as fallback")
        df_encoded = df.copy()  # Fallback to original data
    except TypeError as e:
        print(f"Type error during feature encoding: {str(e)}")
        print("Using original data as fallback")
        df_encoded = df.copy()  # Fallback to original data
    except ValueError as e:
        print(f"Value error during feature encoding: {str(e)}")
        print("Using original data as fallback")
        df_encoded = df.copy()  # Fallback to original data
    except Exception as e:
        print(f"Unexpected error in feature encoding: {e.__class__.__name__}: {str(e)}")
        print("Using original data as fallback")
        df_encoded = df.copy()  # Fallback to original data
    
    # Initialize and train segmentation model
    try:
        segmentation = AudienceSegmentation(n_clusters=n_clusters)
        
        # Train model
        segmentation.train(df_encoded)
        
        # Get cluster labels
        labels = segmentation.model.labels_
        
        # Save model
        segmentation.save_model()
        
        # Create a simple JSON version of cluster descriptions for the API
        cluster_descriptions = []
        for i in range(n_clusters):
            cluster_descriptions.append({
                "id": i,
                "name": f"Segment {i}",
                "description": f"Audience segment {i} with {np.sum(labels == i)} candidates"
            })
        
        # Save as JSON
        import json
        try:
            with open('ml/models/cluster_descriptions.json', 'w') as f:
                json.dump(cluster_descriptions, f, indent=2)
            print("Saved cluster descriptions to JSON file")
        except (OSError, IOError) as e:
            print(f"Error writing cluster descriptions JSON: {str(e)}")
        except TypeError as e:
            print(f"JSON serialization error: {str(e)}")
        
        # Visualize clusters if requested
        if visualize:
            try:
                print("Generating cluster visualizations...")
                visualize_clusters(df, labels, n_clusters)
            except ImportError as e:
                print(f"Required visualization library missing: {str(e)}")
            except ValueError as e:
                print(f"Invalid data for visualization: {str(e)}")
            except (OSError, IOError) as e:
                print(f"Error saving visualization files: {str(e)}")
            except Exception as e:
                print(f"Unexpected error in visualization: {e.__class__.__name__}: {str(e)}")
        
        # Save cluster descriptions
        try:
            save_cluster_descriptions(df, labels, n_clusters)
        except (OSError, IOError) as e:
            print(f"Error writing cluster descriptions file: {str(e)}")
        except ValueError as e:
            print(f"Invalid data for cluster descriptions: {str(e)}")
        except KeyError as e:
            print(f"Missing key in data for cluster descriptions: {str(e)}")
        except Exception as e:
            print(f"Unexpected error saving cluster descriptions: {e.__class__.__name__}: {str(e)}")
        
        print("Audience segmentation model training complete!")
        
    except ValueError as e:
        print(f"Invalid parameter or data for model training: {str(e)}")
    except AttributeError as e:
        print(f"Missing attribute or method: {str(e)}")
    except ImportError as e:
        print(f"Required library missing: {str(e)}")
    except (OSError, IOError) as e:
        print(f"File I/O error during model training: {str(e)}")
    except MemoryError as e:
        print(f"Out of memory during model training: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in model training: {e.__class__.__name__}: {str(e)}")

if __name__ == '__main__':
    main()
