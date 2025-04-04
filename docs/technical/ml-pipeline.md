# Machine Learning Pipeline

This document describes the machine learning pipeline used in AdFlux for candidate segmentation.

## Overview

The machine learning pipeline in AdFlux is responsible for segmenting candidates into groups based on their profiles. This segmentation is used to target job opening advertisements to relevant candidate segments.

The pipeline uses K-means clustering, an unsupervised learning algorithm that groups similar candidates together based on their features. The resulting segments can then be targeted with specific job opening advertisements.

## Pipeline Architecture

The ML pipeline consists of the following components:

1. **Data Loading**: Loads candidate data from the database
2. **Feature Engineering**: Extracts and transforms features from candidate profiles
3. **Preprocessing**: Scales and normalizes features
4. **Model Training**: Trains the K-means clustering model
5. **Prediction**: Assigns segments to candidates
6. **Persistence**: Saves and loads trained models

```
+----------------+       +-------------------+       +----------------+
| Data Loading   | ----> | Feature           | ----> | Preprocessing  |
| (Database)     |       | Engineering       |       | (Scaling)      |
+----------------+       +-------------------+       +----------------+
                                                            |
                                                            v
+----------------+       +-------------------+       +----------------+
| Persistence    | <---- | Prediction        | <---- | Model Training |
| (Joblib)       |       | (Segment          |       | (K-means)      |
+----------------+       |  Assignment)      |       +----------------+
                         +-------------------+
```

## Implementation Details

### Data Loading

Candidate data is loaded from the database using SQLAlchemy ORM. The `load_candidates` function retrieves candidate profiles with relevant attributes:

```python
def load_candidates():
    """Load candidate data from the database.
    
    Returns:
        List of Candidate objects
    """
    return Candidate.query.all()
```

### Feature Engineering

The feature engineering component extracts and transforms features from candidate profiles. This includes:

1. **Categorical Features**: Location, education level, primary skill
2. **Numerical Features**: Years of experience, desired salary
3. **Text Features**: Skills (converted to a bag-of-words representation)

```python
def extract_features(candidates):
    """Extract features from candidate profiles.
    
    Args:
        candidates: List of Candidate objects
        
    Returns:
        DataFrame with extracted features
    """
    features = []
    for candidate in candidates:
        feature_dict = {
            'years_experience': candidate.years_experience,
            'desired_salary': candidate.desired_salary,
            'location': candidate.location,
            'education_level': candidate.education_level,
            'primary_skill': candidate.primary_skill,
        }
        
        # Add skills as individual features
        for skill in candidate.skills:
            feature_dict[f'skill_{skill}'] = 1
            
        features.append(feature_dict)
        
    return pd.DataFrame(features)
```

### Preprocessing

The preprocessing component scales and normalizes features to ensure they contribute equally to the clustering:

1. **One-Hot Encoding**: Converts categorical features to binary features
2. **Standard Scaling**: Normalizes numerical features to have zero mean and unit variance

```python
def preprocess_features(features_df):
    """Preprocess features for clustering.
    
    Args:
        features_df: DataFrame with extracted features
        
    Returns:
        Tuple of (preprocessed features array, preprocessor object)
    """
    # Separate numerical and categorical features
    numerical_features = ['years_experience', 'desired_salary']
    categorical_features = ['location', 'education_level', 'primary_skill']
    skill_features = [col for col in features_df.columns if col.startswith('skill_')]
    
    # Create preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('skill', 'passthrough', skill_features)
        ])
    
    # Apply preprocessing
    X_processed = preprocessor.fit_transform(features_df)
    
    return X_processed, preprocessor
```

### Model Training

The model training component uses the K-means clustering algorithm to group candidates based on their preprocessed features:

```python
def train_model(X, num_clusters=5):
    """Train K-means clustering model.
    
    Args:
        X: Preprocessed feature array
        num_clusters: Number of clusters to create
        
    Returns:
        Trained K-means model
    """
    model = KMeans(
        n_clusters=num_clusters,
        init='k-means++',
        n_init=10,
        max_iter=300,
        tol=1e-4,
        random_state=42
    )
    
    model.fit(X)
    
    return model
```

### Prediction

The prediction component assigns segments to candidates based on the trained model:

```python
def predict_segments(model, X, candidates):
    """Predict segments for candidates.
    
    Args:
        model: Trained K-means model
        X: Preprocessed feature array
        candidates: List of Candidate objects
        
    Returns:
        Dictionary mapping candidate IDs to segment IDs
    """
    # Predict cluster labels
    labels = model.predict(X)
    
    # Create mapping from candidate ID to segment
    segment_mapping = {}
    for i, candidate in enumerate(candidates):
        segment_mapping[candidate.candidate_id] = int(labels[i])
    
    return segment_mapping
```

### Persistence

The persistence component saves and loads trained models using joblib:

```python
def save_model(model, preprocessor, file_path):
    """Save model and preprocessor to file.
    
    Args:
        model: Trained K-means model
        preprocessor: Fitted preprocessor object
        file_path: Path to save the model
    """
    model_data = {
        'model': model,
        'preprocessor': preprocessor,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    joblib.dump(model_data, file_path)

def load_model(file_path):
    """Load model and preprocessor from file.
    
    Args:
        file_path: Path to the saved model
        
    Returns:
        Tuple of (model, preprocessor)
    """
    model_data = joblib.load(file_path)
    
    return model_data['model'], model_data['preprocessor']
```

## Integration with AdFlux

The ML pipeline is integrated with AdFlux through the `ml_model.py` module, which provides a high-level interface for training models and segmenting candidates:

```python
def train_segmentation_model(num_clusters=5):
    """Train a new segmentation model.
    
    Args:
        num_clusters: Number of clusters to create
        
    Returns:
        Dictionary with training results
    """
    # Load candidates
    candidates = load_candidates()
    
    # Extract features
    features_df = extract_features(candidates)
    
    # Preprocess features
    X, preprocessor = preprocess_features(features_df)
    
    # Train model
    model = train_model(X, num_clusters)
    
    # Save model
    model_path = os.path.join(current_app.instance_path, 'ml_models', 'segmentation_model.joblib')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    save_model(model, preprocessor, model_path)
    
    # Return training results
    return {
        'num_candidates': len(candidates),
        'num_clusters': num_clusters,
        'inertia': model.inertia_,
        'model_path': model_path
    }

def segment_candidates():
    """Segment candidates using the trained model.
    
    Returns:
        Dictionary with segmentation results
    """
    # Load model
    model_path = os.path.join(current_app.instance_path, 'ml_models', 'segmentation_model.joblib')
    model, preprocessor = load_model(model_path)
    
    # Load candidates
    candidates = load_candidates()
    
    # Extract features
    features_df = extract_features(candidates)
    
    # Preprocess features
    X = preprocessor.transform(features_df)
    
    # Predict segments
    segment_mapping = predict_segments(model, X, candidates)
    
    # Update candidates in database
    for candidate_id, segment_id in segment_mapping.items():
        candidate = Candidate.query.get(candidate_id)
        if candidate:
            candidate.segment_id = segment_id
    
    db.session.commit()
    
    # Count candidates per segment
    segment_counts = {}
    for segment_id in set(segment_mapping.values()):
        segment_counts[segment_id] = list(segment_mapping.values()).count(segment_id)
    
    return {
        'num_candidates': len(candidates),
        'segments': segment_counts
    }
```

## CLI Commands

The ML pipeline can be accessed through CLI commands:

```python
@click.group(name='ml')
def ml_commands():
    """Machine learning commands."""
    pass

@ml_commands.command(name='train')
@click.option('--clusters', default=5, help='Number of clusters')
def train_command(clusters):
    """Train the segmentation model."""
    result = train_segmentation_model(num_clusters=clusters)
    click.echo(f"Model trained with {result['num_candidates']} candidates and {result['num_clusters']} clusters")
    click.echo(f"Model saved to {result['model_path']}")

@ml_commands.command(name='predict')
def predict_command():
    """Apply the model to segment candidates."""
    result = segment_candidates()
    click.echo(f"Segmented {result['num_candidates']} candidates")
    for segment_id, count in result['segments'].items():
        click.echo(f"Segment {segment_id}: {count} candidates")
```

## Web Interface

The ML pipeline is also accessible through the web interface:

1. **Segmentation Page**: Displays current segments and allows retraining the model
2. **Candidate Page**: Shows segment assignments for candidates
3. **Campaign Creation**: Allows targeting specific segments when creating campaigns

## Performance Considerations

### Scalability

The current implementation works well for thousands of candidates, but for larger datasets, consider:

1. **Batch Processing**: Process candidates in batches
2. **Dimensionality Reduction**: Apply PCA before clustering
3. **Mini-Batch K-means**: Use MiniBatchKMeans for larger datasets

### Optimization

To optimize the ML pipeline:

1. **Feature Selection**: Identify and use only the most relevant features
2. **Hyperparameter Tuning**: Find optimal number of clusters using silhouette score
3. **Caching**: Cache intermediate results for faster processing

## Future Enhancements

Potential enhancements to the ML pipeline include:

1. **Advanced Algorithms**: Explore other clustering algorithms (DBSCAN, Hierarchical Clustering)
2. **Natural Language Processing**: Improve processing of text data (skills, job descriptions)
3. **Segment Naming**: Automatically generate descriptive names for segments
4. **Explainability**: Provide explanations for why candidates are assigned to specific segments
5. **Incremental Learning**: Update the model incrementally as new candidates are added
6. **Anomaly Detection**: Identify unusual candidate profiles
7. **Recommendation System**: Recommend job openings to candidates based on their segment
