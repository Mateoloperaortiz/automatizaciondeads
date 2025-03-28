"""
Service for integrating audience segmentation with the Flask application.

This module provides services to use the trained audience segmentation model
to create and manage audience segments for ad targeting.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
from typing import List, Dict, Any, Optional

# Add the project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.segmentation import AudienceSegmentation
from app.models.segment import Segment
from app.models.candidate import Candidate
from app import db

class SegmentationService:
    """Service for audience segmentation operations."""
    
    def __init__(self):
        """Initialize segmentation service with trained model."""
        self.segmentation = AudienceSegmentation()
        
        # Try to load existing model
        self.model_loaded = self.segmentation.load_model()
        
        # Load cluster descriptions if available
        self.cluster_descriptions = []
        try:
            self.cluster_descriptions = joblib.load('ml/models/cluster_descriptions.joblib')
        except FileNotFoundError:
            print("Cluster descriptions file not found. Run train_model.py to generate them.")
        except (OSError, IOError) as e:
            print(f"Error reading cluster descriptions file: {str(e)}")
        except Exception as e:
            print(f"Unexpected error loading cluster descriptions: {e.__class__.__name__}: {str(e)}")
    
    def ensure_model_exists(self) -> bool:
        """Ensure that a trained model exists, training if necessary.
        
        Returns:
            bool: True if model exists or was trained successfully
        """
        if self.model_loaded and self.segmentation.model is not None:
            return True
        
        # Try to train a new model
        from ml.train_model import main as train_model
        try:
            train_model()
            self.model_loaded = self.segmentation.load_model()
            
            # Reload cluster descriptions
            try:
                self.cluster_descriptions = joblib.load('ml/models/cluster_descriptions.joblib')
            except FileNotFoundError:
                print("Cluster descriptions file not found after model training.")
            except (OSError, IOError) as e:
                print(f"Error reading cluster descriptions file after model training: {str(e)}")
            except Exception as e:
                print(f"Unexpected error loading cluster descriptions after model training: {e.__class__.__name__}: {str(e)}")
                
            return self.model_loaded
        except ImportError as e:
            print(f"Required library missing for model training: {str(e)}")
            return False
        except (OSError, IOError) as e:
            print(f"File I/O error during model training: {str(e)}")
            return False
        except ValueError as e:
            print(f"Invalid parameter or data format for model training: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error during model training: {e.__class__.__name__}: {str(e)}")
            return False
    
    def get_candidate_features(self, candidate_id: int = None) -> pd.DataFrame:
        """Extract features from a candidate for segmentation.
        
        Args:
            candidate_id (int, optional): Specific candidate ID to fetch.
            
        Returns:
            pandas.DataFrame: Features for segmentation model
        """
        # Query candidates from database
        candidates = []
        
        if candidate_id:
            # Get specific candidate
            candidate = Candidate.query.get(candidate_id)
            if candidate:
                candidates = [candidate]
        else:
            # Get all candidates
            candidates = Candidate.query.all()
        
        # Extract features
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
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Encode categorical features
        from ml.train_model import encode_categorical_features
        df_encoded = encode_categorical_features(df)
        
        return df_encoded
    
    def create_segments(self) -> List[Dict[str, Any]]:
        """Create or update segments in the database based on clustering.
        
        Returns:
            list: List of segment information dictionaries
        """
        # Ensure model exists
        if not self.ensure_model_exists():
            return [{"error": "Failed to load or train segmentation model"}]
        
        # Get candidate features
        df = self.get_candidate_features()
        if df.empty:
            return [{"error": "No candidates found in database"}]
        
        # Get cluster predictions
        cluster_labels = self.segmentation.predict(df)
        
        # Add cluster labels to dataframe
        df['cluster'] = cluster_labels
        
        # Process each cluster
        created_segments = []
        
        for cluster_id in range(self.segmentation.n_clusters):
            # Get candidates in this cluster
            cluster_df = df[df['cluster'] == cluster_id]
            
            if cluster_df.empty:
                continue
                
            # Get candidate IDs in this cluster
            candidate_ids = cluster_df['id'].tolist()
            
            # Get or create segment in database
            segment = Segment.query.filter_by(segment_code=f"CLUSTER_{cluster_id}").first()
            
            if not segment:
                # Create new segment
                description = ""
                name = f"Segment {cluster_id}"
                
                # Use description from pre-trained analysis if available
                for desc in self.cluster_descriptions:
                    if desc['id'] == cluster_id:
                        name = desc['name']
                        description = desc['description']
                        break
                
                segment = Segment(
                    name=name,
                    description=description,
                    segment_code=f"CLUSTER_{cluster_id}",
                    criteria=str({
                        "cluster_id": cluster_id,
                        "size": len(candidate_ids),
                        "characteristics": self._get_cluster_characteristics(cluster_id)
                    })
                )
                db.session.add(segment)
            else:
                # Update existing segment
                segment.criteria = str({
                    "cluster_id": cluster_id,
                    "size": len(candidate_ids),
                    "characteristics": self._get_cluster_characteristics(cluster_id),
                    "updated_at": pd.Timestamp.now().isoformat()
                })
            
            # Update segment with candidate IDs
            segment.candidate_ids = candidate_ids
            
            db.session.commit()
            
            created_segments.append({
                "id": segment.id,
                "name": segment.name,
                "description": segment.description,
                "segment_code": segment.segment_code,
                "size": len(candidate_ids)
            })
        
        return created_segments
    
    def get_segment_details(self, segment_id: int) -> Dict[str, Any]:
        """Get detailed information about a segment.
        
        Args:
            segment_id (int): Segment ID
            
        Returns:
            dict: Segment details
        """
        segment = Segment.query.get(segment_id)
        if not segment:
            return {"error": "Segment not found"}
        
        # Get characteristics from pre-trained analysis if available
        characteristics = {}
        
        # Extract cluster_id from segment code
        try:
            cluster_id = int(segment.segment_code.split('_')[1])
            
            # Look up characteristics in pre-computed descriptions
            for desc in self.cluster_descriptions:
                if desc['id'] == cluster_id:
                    characteristics = desc['characteristics']
                    break
        except ValueError as e:
            print(f"Could not parse cluster ID from segment code: {str(e)}")
        except IndexError as e:
            print(f"Invalid segment code format: {str(e)}")
        except AttributeError as e:
            print(f"Missing attribute in segment or description: {str(e)}")
        except Exception as e:
            print(f"Unexpected error extracting segment characteristics: {e.__class__.__name__}: {str(e)}")
        
        # Get a sample of candidates in this segment
        candidate_sample = []
        if segment.candidate_ids:
            # Get up to 5 sample candidates
            sample_ids = segment.candidate_ids[:5]
            sample_candidates = Candidate.query.filter(Candidate.id.in_(sample_ids)).all()
            
            for candidate in sample_candidates:
                candidate_sample.append({
                    "id": candidate.id,
                    "name": candidate.name,
                    "location": candidate.location,
                    "education": candidate.education_level,
                    "experience": candidate.years_experience
                })
        
        # Calculate benchmark data
        benchmark_data = self.get_segment_benchmarks()
        
        # Calculate percentiles for this segment's characteristics
        percentiles = self.calculate_segment_percentiles(segment_id, characteristics)
        
        return {
            "id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "segment_code": segment.segment_code,
            "size": len(segment.candidate_ids) if segment.candidate_ids else 0,
            "characteristics": characteristics,
            "sample_candidates": candidate_sample,
            "benchmark": benchmark_data,
            "percentiles": percentiles
        }
    
    def _get_cluster_characteristics(self, cluster_id: int) -> Dict[str, Any]:
        """Get characteristics for a specific cluster.
        
        Args:
            cluster_id (int): Cluster ID
            
        Returns:
            dict: Characteristics of the cluster
        """
        # Try to get from pre-computed descriptions first
        for desc in self.cluster_descriptions:
            if desc['id'] == cluster_id:
                return desc['characteristics']
        
        # Default characteristics if not found
        return {
            "age_avg": 0,
            "experience_avg": 0,
            "education": "Unknown",
            "location": "Unknown",
            "job_preferences": []
        }
        
    def get_segment_benchmarks(self) -> Dict[str, Any]:
        """Calculate benchmark averages across all segments.
        
        Returns:
            dict: Benchmark data with averages and ranges for segment characteristics
        """
        # Get all segments
        segments = Segment.query.all()
        if not segments:
            return {}
            
        # Collect all characteristics
        all_characteristics = []
        for segment in segments:
            try:
                # Extract characteristics from segment's criteria
                if segment.criteria:
                    criteria = segment.criteria
                    if isinstance(criteria, str):
                        try:
                            import json
                            criteria = json.loads(criteria)
                        except Exception as e:
                            print(f"Error parsing segment criteria: {str(e)}")
                            continue
                            
                    # Get characteristics
                    if 'characteristics' in criteria:
                        all_characteristics.append(criteria['characteristics'])
                    elif isinstance(criteria, dict):
                        # Try to find any characteristics-like data
                        char_keys = ['age_avg', 'experience_avg', 'salary_avg', 
                                    'education', 'location', 'industry']
                        has_chars = any(key in criteria for key in char_keys)
                        if has_chars:
                            all_characteristics.append(criteria)
            except Exception as e:
                print(f"Error extracting characteristics for segment {segment.id}: {str(e)}")
                
        if not all_characteristics:
            return {}
            
        # Calculate benchmarks
        benchmarks = {}
        
        # Numerical benchmarks
        numerical_fields = ['age_avg', 'experience_avg', 'salary_avg']
        for field in numerical_fields:
            values = [char.get(field, 0) for char in all_characteristics if field in char]
            if values:
                benchmarks[field] = {
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'median': sorted(values)[len(values)//2]
                }
                
        # Top education levels
        education_values = [char.get('education', '') for char in all_characteristics if 'education' in char]
        if education_values:
            from collections import Counter
            education_counter = Counter(education_values)
            benchmarks['education'] = {
                'most_common': education_counter.most_common(3),
                'count': len(education_values)
            }
            
        # Top locations
        location_values = [char.get('location', '') for char in all_characteristics if 'location' in char]
        if location_values:
            from collections import Counter
            location_counter = Counter(location_values)
            benchmarks['location'] = {
                'most_common': location_counter.most_common(3),
                'count': len(location_values)
            }
            
        # Top industries
        industry_values = [char.get('industry', '') for char in all_characteristics if 'industry' in char]
        if industry_values:
            from collections import Counter
            industry_counter = Counter(industry_values)
            benchmarks['industry'] = {
                'most_common': industry_counter.most_common(3),
                'count': len(industry_values)
            }
            
        # Add segment metadata
        benchmarks['_meta'] = {
            'total_segments': len(segments),
            'segments_with_characteristics': len(all_characteristics),
            'generated_at': pd.Timestamp.now().isoformat()
        }
        
        return benchmarks
        
    def calculate_segment_percentiles(self, segment_id: int, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate percentile ranks for a segment's characteristics.
        
        Args:
            segment_id (int): ID of the segment to calculate percentiles for
            characteristics (dict): Segment characteristics
            
        Returns:
            dict: Percentile data for each characteristic
        """
        if not characteristics:
            return {}
            
        # Get all segments except this one
        segments = Segment.query.filter(Segment.id != segment_id).all()
        if not segments:
            return {}
            
        # Collect all characteristics
        all_characteristics = []
        for segment in segments:
            try:
                # Extract characteristics from segment's criteria
                if segment.criteria:
                    criteria = segment.criteria
                    if isinstance(criteria, str):
                        try:
                            import json
                            criteria = json.loads(criteria)
                        except Exception as e:
                            print(f"Error parsing segment criteria: {str(e)}")
                            continue
                            
                    # Get characteristics
                    if 'characteristics' in criteria:
                        all_characteristics.append(criteria['characteristics'])
                    elif isinstance(criteria, dict):
                        # Try to find any characteristics-like data
                        char_keys = ['age_avg', 'experience_avg', 'salary_avg']
                        has_chars = any(key in criteria for key in char_keys)
                        if has_chars:
                            all_characteristics.append(criteria)
            except Exception as e:
                print(f"Error extracting characteristics for segment {segment.id}: {str(e)}")
                
        if not all_characteristics:
            return {}
            
        # Calculate percentiles for numerical values
        percentiles = {}
        
        for key, value in characteristics.items():
            if not isinstance(value, (int, float)):
                continue
                
            # Get values for this characteristic from all segments
            all_values = [char.get(key, 0) for char in all_characteristics if key in char]
            
            if not all_values:
                continue
                
            # Add current segment's value
            all_values.append(value)
            
            # Sort values
            all_values.sort()
            
            # Find rank of current segment's value
            rank = all_values.index(value)
            
            # Calculate percentile
            percentile = (rank / len(all_values)) * 100
            
            # Store percentile information
            percentiles[key] = {
                'value': value,
                'percentile': percentile,
                'rank': rank + 1,  # 1-based rank
                'total': len(all_values),
                'is_highest': rank == len(all_values) - 1,
                'is_lowest': rank == 0
            }
            
        return percentiles
    
    def assign_segment_to_candidate(self, candidate_id: int) -> Dict[str, Any]:
        """Determine the segment for a specific candidate.
        
        Args:
            candidate_id (int): Candidate ID
            
        Returns:
            dict: Segment assignment result
        """
        # Ensure model exists
        if not self.ensure_model_exists():
            return {"error": "Failed to load or train segmentation model"}
        
        # Get candidate features
        df = self.get_candidate_features(candidate_id)
        if df.empty:
            return {"error": "Candidate not found"}
        
        # Predict cluster
        cluster_label = self.segmentation.predict(df)[0]
        
        # Find matching segment
        segment = Segment.query.filter_by(segment_code=f"CLUSTER_{cluster_label}").first()
        
        if not segment:
            return {
                "candidate_id": candidate_id,
                "cluster": int(cluster_label),
                "error": "No matching segment found in database"
            }
        
        # Add candidate to segment if not already included
        if candidate_id not in segment.candidate_ids:
            segment.candidate_ids = segment.candidate_ids + [candidate_id]
            db.session.commit()
        
        return {
            "candidate_id": candidate_id,
            "segment_id": segment.id,
            "segment_name": segment.name,
            "cluster": int(cluster_label)
        }


# Singleton instance for app-wide use
segmentation_service = SegmentationService()
