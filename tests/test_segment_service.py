import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.segment import Segment
from app.models.candidate import Candidate
from ml.segment_service import SegmentationService, segmentation_service


class TestSegmentService(unittest.TestCase):
    """Test cases for the segment service functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self.create_test_data()
        
        # Initialize service
        self.service = SegmentationService()
    
    def tearDown(self):
        """Tear down test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_data(self):
        """Create test segments and candidates."""
        # Create candidates
        candidates = [
            Candidate(
                name=f"Test Candidate {i}", 
                age=25 + i, 
                location="Test Location",
                education_level="Bachelor",
                years_of_experience=i,
                desired_salary=50000 + i * 1000
            )
            for i in range(5)
        ]
        db.session.add_all(candidates)
        db.session.commit()
        
        # Create segments
        segment1 = Segment(
            name="Test Segment 1",
            description="Test Description 1",
            segment_code="CLUSTER_0",
            criteria={
                "cluster_id": 0,
                "characteristics": {
                    "age_avg": 30,
                    "experience_avg": 5,
                    "education": "Bachelor",
                    "location": "New York"
                },
                "original_values": {
                    "age_avg": 30,
                    "experience_avg": 5,
                    "education": "Bachelor",
                    "location": "New York"
                }
            }
        )
        
        segment2 = Segment(
            name="Test Segment 2",
            description="Test Description 2",
            segment_code="CLUSTER_1",
            criteria={
                "cluster_id": 1,
                "characteristics": {
                    "age_avg": 35,
                    "experience_avg": 8,
                    "education": "Master",
                    "location": "San Francisco"
                }
            }
        )
        
        db.session.add_all([segment1, segment2])
        db.session.commit()
        
        # Assign candidates to segments
        candidate_ids = [c.id for c in candidates]
        segment1.candidate_ids = candidate_ids[:3]  # First 3 candidates
        segment2.candidate_ids = candidate_ids[3:]  # Last 2 candidates
        db.session.commit()
    
    def test_get_segment_benchmarks(self):
        """Test calculating benchmark data across segments."""
        benchmarks = self.service.get_segment_benchmarks()
        
        # Verify benchmark structure
        self.assertIn('age_avg', benchmarks)
        self.assertIn('experience_avg', benchmarks)
        self.assertIn('_meta', benchmarks)
        
        # Verify numerical benchmark calculations
        self.assertEqual(benchmarks['age_avg']['average'], 32.5)  # (30 + 35) / 2
        self.assertEqual(benchmarks['age_avg']['min'], 30)
        self.assertEqual(benchmarks['age_avg']['max'], 35)
        
        self.assertEqual(benchmarks['experience_avg']['average'], 6.5)  # (5 + 8) / 2
        self.assertEqual(benchmarks['experience_avg']['min'], 5)
        self.assertEqual(benchmarks['experience_avg']['max'], 8)
        
        # Verify metadata
        self.assertEqual(benchmarks['_meta']['total_segments'], 2)
    
    def test_calculate_segment_percentiles(self):
        """Test calculating percentile ranks for segment characteristics."""
        # Get segment 1
        segment = Segment.query.filter_by(segment_code="CLUSTER_0").first()
        
        # Extract characteristics
        characteristics = segment.criteria['characteristics']
        
        # Calculate percentiles
        percentiles = self.service.calculate_segment_percentiles(segment.id, characteristics)
        
        # Verify percentile data
        self.assertIn('age_avg', percentiles)
        self.assertIn('experience_avg', percentiles)
        
        # Verify age_avg percentile (should be 0 percentile as it's lower than segment 2)
        self.assertEqual(percentiles['age_avg']['percentile'], 0)
        self.assertEqual(percentiles['age_avg']['is_lowest'], True)
        
        # Verify experience_avg percentile (should be 0 percentile as it's lower than segment 2)
        self.assertEqual(percentiles['experience_avg']['percentile'], 0)
        self.assertEqual(percentiles['experience_avg']['is_lowest'], True)
    
    def test_get_segment_details(self):
        """Test getting detailed segment information with benchmarks and percentiles."""
        # Get segment 1
        segment = Segment.query.filter_by(segment_code="CLUSTER_0").first()
        
        # Get segment details
        details = self.service.get_segment_details(segment.id)
        
        # Verify details structure
        self.assertEqual(details['id'], segment.id)
        self.assertEqual(details['name'], "Test Segment 1")
        self.assertEqual(details['size'], 3)  # 3 candidates assigned
        
        # Verify benchmark and percentile data are included
        self.assertIn('benchmark', details)
        self.assertIn('percentiles', details)
        self.assertIn('characteristics', details)
        
        # Verify sample candidates
        self.assertIn('sample_candidates', details)
        self.assertEqual(len(details['sample_candidates']), 3)


if __name__ == '__main__':
    unittest.main()