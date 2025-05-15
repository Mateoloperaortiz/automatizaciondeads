import joblib
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from umap import UMAP
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# --- Configuration (should match or be consistent with main.py and create_dummy_models.py) --- #
MODEL_DIR = "./models"
UMAP_MODEL_PATH = os.path.join(MODEL_DIR, "fitted_umap.pkl")
KMEANS_MODEL_PATH = os.path.join(MODEL_DIR, "fitted_kmeans.pkl")
CLUSTER_PROFILES_PATH = os.path.join(MODEL_DIR, "cluster_profiles.json") # For reference, though this script might help generate data for it
SBERT_MODEL_NAME = 'all-MiniLM-L6-v2'

# UMAP Parameters (tune these based on your data and experimentation)
UMAP_N_COMPONENTS = 50
UMAP_N_NEIGHBORS = 15 # Default, can be tuned
UMAP_MIN_DIST = 0.1   # Default, can be tuned
UMAP_RANDOM_STATE = 42

# K-Means Parameters
KMEANS_K_RANGE = range(2, 7) # k will be tested from 2 to 6 (inclusive of 2, exclusive of 7)
KMEANS_RANDOM_STATE = 42

# --- Helper Functions --- # 
def load_job_ad_corpus(filepath="./data/job_ads_corpus.json"):
    """
    Placeholder function to load your job ad dataset.
    Expects a JSON file where each entry has a field like 'text' or 'description'.
    Adjust to your actual data format.
    """
    print(f"Loading job ad corpus from {filepath}...")
    if not os.path.exists(filepath):
        print(f"Error: Corpus file not found at {filepath}")
        print("Please create a job ad corpus file. Example format:")
        print("[{ \"id\": 1, \"text\": \"Software engineer job description...\" }, ...]")
        return None
    try:
        with open(filepath, 'r') as f:
            corpus_data = json.load(f)
        # Assuming each item in corpus_data is a dict and has a 'text' field
        job_texts = [item['text'] for item in corpus_data if 'text' in item and item['text']]
        if not job_texts:
            print("Error: No job texts found in the corpus file. Ensure items have a 'text' field with content.")
            return None
        print(f"Loaded {len(job_texts)} job ad texts from corpus.")
        return job_texts
    except Exception as e:
        print(f"Error loading or parsing corpus: {e}")
        return None

# --- Main Training Pipeline --- #
def train_pipeline():
    print("Starting offline model training pipeline...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Load Corpus
    job_ad_texts = load_job_ad_corpus()
    if not job_ad_texts:
        print("Halting pipeline due to corpus loading issues.")
        return

    # 2. Load SBERT and Generate Embeddings
    print(f"Loading SBERT model ({SBERT_MODEL_NAME}) for embedding generation...")
    try:
        sbert_model = SentenceTransformer(SBERT_MODEL_NAME)
        print("SBERT model loaded. Generating embeddings for corpus (this may take a while)...")
        corpus_sbert_embeddings = sbert_model.encode(job_ad_texts, show_progress_bar=True)
        print(f"Generated {corpus_sbert_embeddings.shape[0]} SBERT embeddings with dimension {corpus_sbert_embeddings.shape[1]}.")
    except Exception as e:
        print(f"Error during SBERT model loading or embedding generation: {e}")
        return

    # 3. Train and Save UMAP Model
    print("\nTraining UMAP model...")
    try:
        num_samples = corpus_sbert_embeddings.shape[0]
        # Drastically reduce n_neighbors for small N and try random initialization
        current_umap_n_neighbors = min(5, num_samples - 1) if num_samples > 1 else 1
        if current_umap_n_neighbors <= 1: # Needs at least 2 for some default UMAP logic if not random init
            print(f"Warning: n_neighbors is very small ({current_umap_n_neighbors}). This may affect UMAP quality.")
            # If using init='spectral', n_neighbors often needs to be > 1. For random, 1 might be okay.
            current_umap_n_neighbors = max(2, current_umap_n_neighbors) if num_samples > 2 else 1

        print(f"Using n_neighbors={current_umap_n_neighbors}, init='random' for UMAP with {num_samples} samples.")

        umap_trainer = UMAP(
            n_components=UMAP_N_COMPONENTS,
            n_neighbors=current_umap_n_neighbors,
            min_dist=UMAP_MIN_DIST,
            init='random',  # Change from 'spectral' to 'random' for initialization
            random_state=UMAP_RANDOM_STATE,
            n_jobs=1,
            densmap=False # Explicitly false, though it is the default
        )
        print(f"Fitting UMAP on {corpus_sbert_embeddings.shape[0]} embeddings...")
        fitted_umap_model = umap_trainer.fit(corpus_sbert_embeddings)
        joblib.dump(fitted_umap_model, UMAP_MODEL_PATH)
        print(f"UMAP model trained and saved to {UMAP_MODEL_PATH}")
        
        # Transform corpus with the fitted UMAP for K-Means training
        print("Transforming corpus embeddings with fitted UMAP...")
        corpus_reduced_embeddings = fitted_umap_model.transform(corpus_sbert_embeddings)
        print(f"Reduced embeddings shape: {corpus_reduced_embeddings.shape}")
    except Exception as e:
        print(f"Error during UMAP training or saving: {e}")
        return

    # 4. Train and Save K-Means Model (with Auto-K using Silhouette Score)
    print("\nTraining K-Means model with auto-k selection...")
    best_k = -1
    best_silhouette_score = -1 # Silhouette scores range from -1 to 1
    best_kmeans_model = None

    if corpus_reduced_embeddings.shape[0] <= max(KMEANS_K_RANGE): # Ensure enough samples for max k
        print(f"Warning: Number of samples ({corpus_reduced_embeddings.shape[0]}) is small for K-Means range up to {max(KMEANS_K_RANGE)}. Adjust KMEANS_K_RANGE or increase corpus size.")
        # Potentially adjust KMEANS_K_RANGE here if too few samples

    print(f"Testing k values in {list(KMEANS_K_RANGE)} for K-Means...")
    for k_val in KMEANS_K_RANGE:
        if corpus_reduced_embeddings.shape[0] <= k_val:
            print(f"Skipping k={k_val}, not enough samples ({corpus_reduced_embeddings.shape[0]}).")
            continue
        try:
            print(f"  Fitting K-Means with k={k_val}...")
            kmeans_temp = KMeans(n_clusters=k_val, random_state=KMEANS_RANDOM_STATE, n_init='auto')
            cluster_labels = kmeans_temp.fit_predict(corpus_reduced_embeddings)
            
            # Silhouette score requires at least 2 labels and less than n_samples-1 labels if all points are not in one cluster
            if len(set(cluster_labels)) > 1 and len(set(cluster_labels)) < corpus_reduced_embeddings.shape[0]:
                silhouette_avg = silhouette_score(corpus_reduced_embeddings, cluster_labels)
                print(f"  For k={k_val}, Silhouette Score: {silhouette_avg:.4f}")
                if silhouette_avg > best_silhouette_score:
                    best_silhouette_score = silhouette_avg
                    best_k = k_val
                    best_kmeans_model = kmeans_temp # Keep the fitted model
            else:
                print(f"  For k={k_val}, could not calculate silhouette score (num_labels={len(set(cluster_labels))}).")
        except Exception as e:
            print(f"  Error during K-Means for k={k_val}: {e}")

    if best_kmeans_model and best_k != -1:
        print(f"Best k found: {best_k} with Silhouette Score: {best_silhouette_score:.4f}")
        joblib.dump(best_kmeans_model, KMEANS_MODEL_PATH)
        print(f"Optimal K-Means model (k={best_k}) trained and saved to {KMEANS_MODEL_PATH}")
        # You can now assign all corpus ads to their clusters using best_kmeans_model.predict(corpus_reduced_embeddings)
        # and use this for generating the initial cluster_profiles.json
    else:
        print("Could not determine optimal K-Means model. K-Means model not saved.")
        print("Consider checking your KMEANS_K_RANGE, corpus size, or data characteristics.")

    # 5. Guidance for Cluster Profiles (cluster_profiles.json)
    print("\n--- Guidance for Cluster Profiles --- ")
    print(f"K-Means model was trained with k={best_k if best_k != -1 else 'N/A'}.")
    print("To create 'cluster_profiles.json':")
    print("  1. If K-Means saved, load it and predict cluster labels for your corpus_reduced_embeddings.")
    print("  2. For each cluster label (0 to k-1):")
    print("     a. Gather all job ad texts that belong to this cluster.")
    print("     b. Analyze these texts (e.g., common n-grams, topics via zero-shot classification) to define a profile.")
    print(f"     c. Create an entry in {CLUSTER_PROFILES_PATH} like: \"0\": {{ \"name\": \"Cluster 0 Profile\", \"industry\": \"X\", ... }}")

    print("\nOffline training pipeline finished.")

if __name__ == "__main__":
    # Before running, ensure you have a corpus file, e.g., ./data/job_ads_corpus.json
    # You might need to create the ./data directory and the file.
    # Example: os.makedirs("./data", exist_ok=True)
    # with open("./data/job_ads_corpus.json", 'w') as f: json.dump([{"id":1, "text":"sample job ad"}], f)
    train_pipeline() 