import joblib
import numpy as np
import json
import os
from umap import UMAP
from sklearn.cluster import KMeans

# Configuration from main.py (ensure these match)
MODEL_DIR = "./models"
UMAP_MODEL_PATH = os.path.join(MODEL_DIR, "fitted_umap.pkl")
KMEANS_MODEL_PATH = os.path.join(MODEL_DIR, "fitted_kmeans.pkl")
CLUSTER_PROFILES_PATH = os.path.join(MODEL_DIR, "cluster_profiles.json")

SBERT_DIM = 384  # Dimension of all-MiniLM-L6-v2 embeddings
UMAP_N_COMPONENTS = 50
KMEANS_N_CLUSTERS = 3 # Dummy number of clusters

def create_and_save_dummy_models():
    print(f"Creating dummy models in {MODEL_DIR}...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Create and save dummy UMAP model
    print("Creating dummy UMAP model...")
    # Further increased number of samples and adjusted n_neighbors logic
    n_dummy_samples_umap = 100 
    dummy_sbert_embeddings = np.random.rand(n_dummy_samples_umap, SBERT_DIM)
    
    try:
        # Explicitly setting n_neighbors lower than n_samples and a bit smaller
        current_n_neighbors = min(10, n_dummy_samples_umap - 1) if n_dummy_samples_umap > 1 else 1
        if current_n_neighbors <= 0: current_n_neighbors = 1 # Ensure positive

        print(f"Using n_neighbors={current_n_neighbors} for UMAP with {n_dummy_samples_umap} samples.")
        dummy_umap = UMAP(
            n_components=UMAP_N_COMPONENTS, 
            n_neighbors=current_n_neighbors, 
            min_dist=0.1, 
            random_state=42, 
            n_jobs=1,
            # low_memory=True, # Might help with very small N
            # verbose=True # For more UMAP output if still failing
        )
        dummy_umap.fit(dummy_sbert_embeddings) # Fit on dummy data
        joblib.dump(dummy_umap, UMAP_MODEL_PATH)
        print(f"Dummy UMAP model saved to {UMAP_MODEL_PATH}")
    except Exception as e:
        print(f"Error creating/saving dummy UMAP model: {e}")
        print("Ensure UMAP dependencies like pynndescent are correctly installed.")
        return # Stop if UMAP fails, as K-Means depends on it

    # 2. Create and save dummy K-Means model
    print("\nCreating dummy K-Means model...")
    # Transform dummy SBERT embeddings with the dummy UMAP
    try:
        dummy_reduced_embeddings = dummy_umap.transform(dummy_sbert_embeddings)
        print(f"Dummy reduced embeddings shape for K-Means: {dummy_reduced_embeddings.shape}")
    except Exception as e:
        print(f"Error transforming data with dummy UMAP: {e}")
        return

    if dummy_reduced_embeddings.shape[0] < KMEANS_N_CLUSTERS:
        print(f"Warning: Number of dummy samples ({dummy_reduced_embeddings.shape[0]}) is less than KMEANS_N_CLUSTERS ({KMEANS_N_CLUSTERS}). Adjusting KMEANS_N_CLUSTERS for dummy model.")
        actual_kmeans_clusters = max(1, dummy_reduced_embeddings.shape[0])
    else:
        actual_kmeans_clusters = KMEANS_N_CLUSTERS

    try:
        dummy_kmeans = KMeans(n_clusters=actual_kmeans_clusters, random_state=42, n_init='auto')
        dummy_kmeans.fit(dummy_reduced_embeddings) # Fit on dummy reduced data
        joblib.dump(dummy_kmeans, KMEANS_MODEL_PATH)
        print(f"Dummy K-Means model saved to {KMEANS_MODEL_PATH}")
    except Exception as e:
        print(f"Error creating/saving dummy K-Means model: {e}")
        return

    # 3. Create dummy cluster_profiles.json
    print("\nCreating dummy cluster_profiles.json...")
    dummy_profiles = {}
    for i in range(actual_kmeans_clusters):
        dummy_profiles[str(i)] = {
            "name": f"Dummy Cluster {i+1}",
            "description": f"This is a placeholder profile for cluster {i}.",
            "industry": "General",
            "skills": ["Communication", "Teamwork"],
            "keywords": [f"dummy_keyword_{i*2+1}", f"dummy_keyword_{i*2+2}"]
        }
    
    try:
        with open(CLUSTER_PROFILES_PATH, 'w') as f:
            json.dump(dummy_profiles, f, indent=2)
        print(f"Dummy cluster_profiles.json saved to {CLUSTER_PROFILES_PATH}")
    except Exception as e:
        print(f"Error creating/saving dummy cluster_profiles.json: {e}")

    print("\nDummy model creation complete.")

if __name__ == "__main__":
    create_and_save_dummy_models() 