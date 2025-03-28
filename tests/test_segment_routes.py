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


class TestSegmentRoutes(unittest.TestCase):
    """Test cases for the segment routes functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self.create_test_data()
        
        # Set up test client
        self.client = self.app.test_client()
        self.client.testing = True
    
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
    
    def test_view_segment_with_benchmark(self):
        """Test viewing segment details with benchmark data."""
        # Get segment 1
        segment = Segment.query.filter_by(segment_code="CLUSTER_0").first()
        
        # Make request
        response = self.client.get(f'/segments/{segment.id}')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check that template variables are passed
        # Note: In a real test, you'd parse the HTML and check content
        # This is simplified for this example
        with self.app.test_request_context():
            with patch('app.routes.segments.render_template') as mock_render:
                from app.routes.segments import view_segment
                view_segment(segment.id)
                
                # Check that benchmark and percentile data are passed to template
                args, kwargs = mock_render.call_args
                self.assertIn('segment_benchmark', kwargs)
                self.assertIn('segment_percentiles', kwargs)
    
    def test_edit_segment_with_reset(self):
        """Test editing segment with reset functionality."""
        # Get segment 1
        segment = Segment.query.filter_by(segment_code="CLUSTER_0").first()
        
        # Modify a characteristic
        data = {
            'name': segment.name,
            'description': segment.description,
            'criteria_age_avg': '40',  # Changed from 30
            'reset_experience_avg': 'on'  # Reset this field
        }
        
        # Make POST request
        response = self.client.post(
            f'/segments/{segment.id}/edit',
            data=data,
            follow_redirects=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check that changes were applied
        updated_segment = Segment.query.get(segment.id)
        criteria = updated_segment.criteria
        
        if isinstance(criteria, str):
            import json
            criteria = json.loads(criteria)
        
        # Age should be updated to new value
        self.assertEqual(criteria['characteristics']['age_avg'], 40)
        
        # Experience should be reset to original value
        self.assertEqual(criteria['characteristics']['experience_avg'], 5)
    
    def test_reset_characteristic_api(self):
        """Test API endpoint for resetting a characteristic."""
        # Get segment 1
        segment = Segment.query.filter_by(segment_code="CLUSTER_0").first()
        
        # First, update a characteristic
        segment.criteria['characteristics']['age_avg'] = 45
        db.session.commit()
        
        # Now reset it via API
        response = self.client.post(
            f'/api/segments/{segment.id}/reset_characteristic',
            json={'characteristic': 'age_avg'},
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        
        # Check that characteristic was reset
        updated_segment = Segment.query.get(segment.id)
        criteria = updated_segment.criteria
        
        if isinstance(criteria, str):
            import json
            criteria = json.loads(criteria)
        
        # Age should be reset to original value
        self.assertEqual(criteria['characteristics']['age_avg'], 30)
    
    def test_benchmark_api(self):
        """Test API endpoint for getting benchmark data."""
        # Get segment 1
        segment = Segment.query.filter_by(segment_code="CLUSTER_0").first()
        
        # Make request
        response = self.client.get(f'/api/segments/{segment.id}/benchmark')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        
        # Check benchmark data structure
        self.assertIn('benchmark', data['data'])
        self.assertIn('percentiles', data['data'])
        self.assertEqual(data['data']['segment_id'], segment.id)
        self.assertEqual(data['data']['segment_name'], "Test Segment 1")


if __name__ == '__main__':
    unittest.main()