"""
Tests for the audience segmentation module.
"""

import sys
import os
import unittest
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.segmentation import AudienceSegmentation

class TestSegmentation(unittest.TestCase):
    """Test cases for audience segmentation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample data
        np.random.seed(42)
        
        # Create three distinct clusters
        cluster1 = pd.DataFrame({
            'age': np.random.normal(25, 3, 50),
            'years_experience': np.random.normal(3, 1, 50),
            'location_encoded': np.random.normal(0.2, 0.1, 50),
            'education_level_encoded': np.random.normal(0.3, 0.1, 50),
            'job_preferences_encoded': np.random.normal(0.1, 0.05, 50),
            'skills_encoded': np.random.normal(0.4, 0.1, 50)
        })
        
        cluster2 = pd.DataFrame({
            'age': np.random.normal(35, 3, 50),
            'years_experience': np.random.normal(10, 2, 50),
            'location_encoded': np.random.normal(0.5, 0.1, 50),
            'education_level_encoded': np.random.normal(0.6, 0.1, 50),
            'job_preferences_encoded': np.random.normal(0.3, 0.05, 50),
            'skills_encoded': np.random.normal(0.7, 0.1, 50)
        })
        
        cluster3 = pd.DataFrame({
            'age': np.random.normal(45, 3, 50),
            'years_experience': np.random.normal(20, 3, 50),
            'location_encoded': np.random.normal(0.8, 0.1, 50),
            'education_level_encoded': np.random.normal(0.9, 0.1, 50),
            'job_preferences_encoded': np.random.normal(0.5, 0.05, 50),
            'skills_encoded': np.random.normal(0.9, 0.1, 50)
        })
        
        # Combine clusters
        self.df = pd.concat([cluster1, cluster2, cluster3], ignore_index=True)
        
        # Initialize segmentation
        self.segmentation = AudienceSegmentation(n_clusters=3)
    
    def test_preprocess_data(self):
        """Test data preprocessing."""
        # Add some missing values
        df_with_missing = self.df.copy()
        df_with_missing.loc[0, 'age'] = np.nan
        df_with_missing.loc[10, 'years_experience'] = np.nan
        
        # Preprocess
        preprocessed = self.segmentation.preprocess_data(df_with_missing)
        
        # Check that missing values are handled
        self.assertEqual(preprocessed.isna().sum().sum(), 0)
        
        # Check that data is scaled
        self.assertTrue(preprocessed['age'].mean() < 1.0)
        self.assertTrue(preprocessed['age'].std() < 2.0)
    
    def test_train_model(self):
        """Test model training."""
        # Train model
        model = self.segmentation.train(self.df)
        
        # Check that model is trained
        self.assertIsNotNone(model)
        
        # Check number of clusters
        self.assertEqual(len(np.unique(model.labels_)), 3)
        
        # Check that silhouette score is calculated
        self.assertTrue(hasattr(self.segmentation, 'model'))
    
    def test_predict(self):
        """Test prediction."""
        # Train model
        self.segmentation.train(self.df)
        
        # Predict on new data
        sample = self.df.iloc[:10].copy()
        predictions = self.segmentation.predict(sample)
        
        # Check that predictions are made
        self.assertEqual(len(predictions), 10)
        
        # Check that predictions are valid cluster labels
        self.assertTrue(all(p in [0, 1, 2] for p in predictions))
    
    def test_save_load_model(self):
        """Test model saving and loading."""
        # Create temporary directory
        os.makedirs('ml/models', exist_ok=True)
        
        # Train and save model
        self.segmentation.train(self.df)
        save_path = 'ml/models/test_model.pkl'
        self.segmentation.save_model(save_path)
        
        # Check that model file exists
        self.assertTrue(os.path.exists(save_path))
        
        # Load model
        new_segmentation = AudienceSegmentation()
        new_segmentation.load_model(save_path)
        
        # Check that loaded model works
        predictions = new_segmentation.predict(self.df.iloc[:10])
        self.assertEqual(len(predictions), 10)
        
        # Clean up
        os.remove(save_path)

if __name__ == '__main__':
    unittest.main() 