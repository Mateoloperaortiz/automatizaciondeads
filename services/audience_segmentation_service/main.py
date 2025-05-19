from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np
import joblib # For loading/saving pre-trained scikit-learn models (UMAP, KMeans)
import os

from sentence_transformers import SentenceTransformer
from umap import UMAP # We'll use this for type hinting, but load a fitted one
from sklearn.cluster import KMeans # For type hinting and potentially for the dummy model
from sklearn.metrics.pairwise import euclidean_distances # For distance to centroid

# --- Configuration --- #
MODEL_DIR = "./models" # Directory to store/load pre-trained models
SBERT_MODEL_NAME = 'all-MiniLM-L6-v2'
UMAP_MODEL_PATH = os.path.join(MODEL_DIR, "fitted_umap.pkl")
KMEANS_MODEL_PATH = os.path.join(MODEL_DIR, "fitted_kmeans.pkl")
CLUSTER_PROFILES_PATH = os.path.join(MODEL_DIR, "cluster_profiles.json") # Placeholder for pre-computed profiles

app = FastAPI(
    title="Audience Segmentation Service",
    description="A microservice for real-time audience segmentation of job ads using pre-trained models.",
    version="0.1.1" # Incremented version
)

# --- Globals for Loaded Models & Data --- #
sbert_model: Optional[SentenceTransformer] = None
fitted_umap: Optional[UMAP] = None
fitted_kmeans: Optional[KMeans] = None
cluster_profiles: Optional[Dict[str, dict]] = None # e.g., {"0": {"name": "Profile A"}, "1": ...}

# --- Lifespan Events for Model Loading --- #
@app.on_event("startup")
async def load_models():
    global sbert_model, fitted_umap, fitted_kmeans, cluster_profiles
    print(f"Loading Sentence-BERT model ({SBERT_MODEL_NAME})...")
    try:
        sbert_model = SentenceTransformer(SBERT_MODEL_NAME)
        print("Sentence-BERT model loaded successfully.")
    except Exception as e:
        print(f"CRITICAL: Error loading Sentence-BERT model: {e}")
        # App might not be usable without SBERT, consider raising an error or specific handling

    # Ensure model directory exists (for dummy model creation if paths don't exist)
    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"Loading pre-fitted UMAP model from {UMAP_MODEL_PATH}...")
    if os.path.exists(UMAP_MODEL_PATH):
        try:
            fitted_umap = joblib.load(UMAP_MODEL_PATH)
            print("Pre-fitted UMAP model loaded successfully.")
        except Exception as e:
            print(f"WARNING: Error loading pre-fitted UMAP model: {e}. Placeholder will not be effective.")
    else:
        print(f"WARNING: UMAP model not found at {UMAP_MODEL_PATH}. Live UMAP transformation will be attempted (not ideal for production). Consider training and saving a UMAP model.")
        # Fallback to initializing a new UMAP for `fit_transform` per call if no model found
        # This is NOT the recommended production approach for Option B but allows code to run.
        try:
            fitted_umap = UMAP(n_components=50, n_neighbors=15, min_dist=0.1, random_state=42, n_jobs=1)
            print("Initialized a new UMAP transformer as a fallback.")
        except Exception as e:
            print(f"CRITICAL: Error initializing fallback UMAP: {e}")

    print(f"Loading pre-fitted K-Means model from {KMEANS_MODEL_PATH}...")
    if os.path.exists(KMEANS_MODEL_PATH):
        try:
            fitted_kmeans = joblib.load(KMEANS_MODEL_PATH)
            print("Pre-fitted K-Means model loaded successfully.")
        except Exception as e:
            print(f"WARNING: Error loading pre-fitted K-Means model: {e}. Placeholder will not be effective.")
    else:
        print(f"WARNING: K-Means model not found at {KMEANS_MODEL_PATH}. Clustering will not be effective. Consider training and saving a K-Means model.")
        # We cannot effectively run K-Means predict without a fitted model on a single new instance.
        # For a dummy, one might create a KMeans with 1 cluster, but it won't be meaningful.

    print(f"Loading cluster profiles from {CLUSTER_PROFILES_PATH}...")
    if os.path.exists(CLUSTER_PROFILES_PATH):
        import json
        try:
            with open(CLUSTER_PROFILES_PATH, 'r') as f:
                cluster_profiles = json.load(f)
            print("Cluster profiles loaded successfully.")
        except Exception as e:
            print(f"WARNING: Error loading cluster profiles: {e}")
    else:
        print(f"WARNING: Cluster profiles not found at {CLUSTER_PROFILES_PATH}. Profiles will be empty.")
        cluster_profiles = {} # Default to empty if not found

# --- Pydantic Models --- #
class JobAdInput(BaseModel):
    job_ad_text: str

class AudiencePrimitive(BaseModel):
    category: str 
    value: str
    confidence: Optional[float] = None

class SegmentationOutput(BaseModel):
    job_ad_input: JobAdInput
    derived_audience_primitives: List[AudiencePrimitive]
    assigned_cluster_id: Optional[str] = None # Changed from cluster_id to assigned_cluster_id
    cluster_assignment_confidence: Optional[float] = None # e.g., 1 - normalized_distance_to_centroid
    # silhouette_score is for overall clustering quality (offline), not per-instance assignment

# --- API Endpoints --- #
@app.post("/segment", response_model=SegmentationOutput)
async def segment_audience(job_ad_data: JobAdInput):
    if not sbert_model:
        raise HTTPException(status_code=503, detail="Sentence-BERT model not available.")
    # Not strictly necessary to check umap/kmeans here if we have fallbacks or error handling below

    # Stage 2: Vectorizer (Sentence-BERT)
    print("Generating SBERT embedding...")
    try:
        sbert_embedding = sbert_model.encode(job_ad_data.job_ad_text)
        print(f"SBERT embedding shape: {sbert_embedding.shape}")
    except Exception as e:
        print(f"Error during SBERT encoding: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate text embedding.")

    # Stage 3: Dimensionality Reduction (UMAP)
    reduced_embedding = None
    if fitted_umap:
        print("Applying pre-fitted UMAP...")
        try:
            reshaped_sbert_embedding = sbert_embedding.reshape(1, -1)
            reduced_embedding = fitted_umap.transform(reshaped_sbert_embedding) # Use transform with fitted model
            print(f"UMAP reduced embedding shape: {reduced_embedding.shape}")
        except Exception as e:
            print(f"Error during UMAP transform: {e}. Check if UMAP was fitted correctly.")
            # Fallback or error if UMAP transform fails even with a loaded model
            # For now, we'll allow it to proceed to K-Means with unreduced if this happens & K-Means can handle it or has its own error
            pass # Or raise HTTPException
    else:
        print("WARN: No pre-fitted UMAP model. UMAP stage will be ineffective or skipped.")
        # If UMAP is critical, raise HTTPException here
        # If proceeding with original sbert_embedding for K-Means (if K-Means was trained on that):
        # reduced_embedding = sbert_embedding.reshape(1, -1) # Use SBERT if UMAP fails/missing

    if reduced_embedding is None:
        # This means UMAP failed and we didn't set a fallback to sbert_embedding for KMeans
        # Or if UMAP is essential and not loaded, it's an issue.
        # For now, assume K-Means might expect the UMAP-reduced dimension or handle original if trained that way.
        # We will default to using SBERT embedding if UMAP failed and K-Means is present.
        print("UMAP transformation resulted in None, attempting to use SBERT embedding for K-Means.")
        reduced_embedding_for_kmeans = sbert_embedding.reshape(1, -1)
    else:
        reduced_embedding_for_kmeans = reduced_embedding

    # Stage 4: Clustering/Assignment (K-Means)
    assigned_cluster_label: Optional[str] = None
    cluster_assignment_confidence: Optional[float] = None
    actual_distance_to_centroid: Optional[float] = None # For logging/info

    if fitted_kmeans and reduced_embedding_for_kmeans is not None:
        print("Assigning to pre-fitted K-Means cluster...")
        try:
            cluster_prediction = fitted_kmeans.predict(reduced_embedding_for_kmeans)
            assigned_cluster_label = str(cluster_prediction[0])
            print(f"Assigned to K-Means cluster: {assigned_cluster_label}")

            if hasattr(fitted_kmeans, 'cluster_centers_'):
                centroid = fitted_kmeans.cluster_centers_[cluster_prediction[0]]
                distance = euclidean_distances(reduced_embedding_for_kmeans, centroid.reshape(1, -1))[0,0]
                actual_distance_to_centroid = float(distance)
                print(f"Distance to centroid: {actual_distance_to_centroid:.4f}")
                
                # Revised Confidence Calculation (using characteristic_distance from profile)
                if cluster_profiles and assigned_cluster_label in cluster_profiles:
                    cluster_profile_data = cluster_profiles[assigned_cluster_label]
                    char_dist = cluster_profile_data.get('characteristic_distance')
                    if isinstance(char_dist, (int, float)) and char_dist > 0:
                        # Normalize confidence: 1 if at centroid, 0 if at characteristic_distance, negative if beyond
                        # Cap at 0 and 1.
                        confidence_raw = 1.0 - (actual_distance_to_centroid / char_dist)
                        cluster_assignment_confidence = max(0.0, min(1.0, confidence_raw))
                        print(f"Characteristic distance for cluster {assigned_cluster_label}: {char_dist:.2f}, Confidence: {cluster_assignment_confidence:.4f}")
                    else:
                        print(f"WARN: Characteristic distance not found or invalid for cluster {assigned_cluster_label}. Using fallback confidence.")
                        # Fallback to simpler confidence if characteristic_distance is missing
                        cluster_assignment_confidence = 1.0 / (1.0 + actual_distance_to_centroid) 
                else:
                    # Fallback if profile or label is somehow missing after assignment
                    cluster_assignment_confidence = 1.0 / (1.0 + actual_distance_to_centroid)
                    print(f"WARN: Cluster profile not found for assigned label {assigned_cluster_label}. Using basic confidence.")

                if cluster_assignment_confidence is not None and cluster_assignment_confidence < 0.25: # Example threshold
                    print(f"Low assignment confidence ({cluster_assignment_confidence:.2f}), may need fallback in calling service.")
            else:
                print("K-Means model does not have cluster_centers_. Cannot calculate distance-based confidence.")
        except Exception as e:
            print(f"Error during K-Means prediction or confidence calculation: {e}")
    else:
        print("WARN: No pre-fitted K-Means model or input embedding missing. Clustering stage skipped.")

    # Stage 5 & 6: Cluster Profiling (using assigned_cluster_label) & Taxonomy Mapping
    derived_primitives: List[AudiencePrimitive] = []
    if assigned_cluster_label and cluster_profiles and assigned_cluster_label in cluster_profiles:
        print(f"Using profile for cluster {assigned_cluster_label}: {cluster_profiles[assigned_cluster_label]}")
        profile = cluster_profiles[assigned_cluster_label]
        
        if profile.get('industry'):
            derived_primitives.append(AudiencePrimitive(category='industry', value=profile['industry']))
        
        for skill in profile.get('skills', []):
             derived_primitives.append(AudiencePrimitive(category='skill_keyword', value=skill))
        
        if profile.get('seniority'): # Added seniority
            derived_primitives.append(AudiencePrimitive(category='seniority', value=profile['seniority']))

        for keyword in profile.get('keywords', []): # Added keywords
            derived_primitives.append(AudiencePrimitive(category='generic_keyword', value=keyword))
        
        # You can add more logic here to extract other fields from your cluster_profiles.json if needed
        # For example, if your profiles had a "target_audience_description_text":
        # if profile.get('target_audience_description_text'):
        #     derived_primitives.append(AudiencePrimitive(category='audience_description', value=profile['target_audience_description_text']))

    else:
        print("No specific cluster profile found or clustering skipped, using default primitives.")
        derived_primitives = [
            AudiencePrimitive(category="industry", value="General", confidence=0.5),
            AudiencePrimitive(category="skill_keyword", value="Communication", confidence=0.5),
        ]
    
    if not derived_primitives:
         derived_primitives = [AudiencePrimitive(category="status", value="Segmentation incomplete")]

    return SegmentationOutput(
        job_ad_input=job_ad_data,
        derived_audience_primitives=derived_primitives,
        assigned_cluster_id=assigned_cluster_label,
        cluster_assignment_confidence=cluster_assignment_confidence
    )

@app.get("/health")
async def health_check():
    model_status = []
    loaded_models_count = 0
    if sbert_model is not None:
        model_status.append("SBERT:OK")
        loaded_models_count +=1
    else:
        model_status.append("SBERT:FAIL")
    
    if fitted_umap is not None:
        # Check if it's a fitted UMAP or the fallback un-fitted one
        if hasattr(fitted_umap, 'embedding_'): # A property of fitted UMAP
            model_status.append("UMAP:OK (Fitted)")
            loaded_models_count +=1
        elif isinstance(fitted_umap, UMAP): # Fallback un-fitted UMAP
            model_status.append("UMAP:OK (Unfitted Fallback)")
            loaded_models_count +=1 # Still counts as loaded for basic operation
        else:
            model_status.append("UMAP:FAIL") # Should not happen if logic is correct
    else:
        model_status.append("UMAP:FAIL")

    if fitted_kmeans is not None:
        if hasattr(fitted_kmeans, 'cluster_centers_'):
            model_status.append("KMeans:OK (Fitted)")
            loaded_models_count +=1
        else:
             model_status.append("KMeans:WARN (Not properly fitted/dummy?)")
    else:
        model_status.append("KMeans:FAIL")
        
    if cluster_profiles is not None:
        model_status.append(f"Profiles:OK ({len(cluster_profiles)} loaded)")
    else:
        model_status.append("Profiles:FAIL")

    # App is healthy if SBERT is loaded. UMAP/KMeans/Profiles are for segmentation quality.
    is_healthy = sbert_model is not None 
    return {
        "status": "healthy" if is_healthy else "degraded", 
        "sbert_model": "Loaded" if sbert_model else "Not Loaded",
        "umap_model": "Loaded/Initialized" if fitted_umap else "Not Loaded",
        "kmeans_model": "Loaded/Initialized" if fitted_kmeans else "Not Loaded",
        "cluster_profiles": f"{len(cluster_profiles) if cluster_profiles else 0} Loaded",
        "details": "; ".join(model_status)
    }

# Note on pre-trained models:
# You would train UMAP and K-Means offline on a representative dataset of job ad embeddings.
# 1. Get SBERT embeddings for all ads in your dataset.
# 2. Fit UMAP on these embeddings: umap_model = UMAP(...).fit(sbert_embeddings)
#    joblib.dump(umap_model, UMAP_MODEL_PATH)
# 3. Transform embeddings with fitted UMAP: reduced_embeddings = umap_model.transform(sbert_embeddings)
# 4. Fit K-Means on reduced_embeddings (find optimal k, then fit final model):
#    kmeans_model = KMeans(n_clusters=optimal_k, ...).fit(reduced_embeddings)
#    joblib.dump(kmeans_model, KMEANS_MODEL_PATH)
# 5. Create cluster_profiles.json based on an analysis of ads in each cluster.

# To run this app (after installing dependencies):
# uvicorn services.audience_segmentation_service.main:app --reload --reload-dir . 