from collections import namedtuple
from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from pyerp.sync.pipeline import SyncPipeline
from pyerp.sync.models import SyncMapping


class TestSyncPipeline(TestCase):
    """Tests for the SyncPipeline class."""

    def setUp(self):
        """Set up test data."""
        # Create a mock SyncMapping
        self.mapping = SyncMapping.objects.create(
            name="test_mapping",
            entity_type="test",
            mapping_config={}
        )
        
        # Create a minimal SyncPipeline instance for testing
        self.pipeline = SyncPipeline(
            mapping=self.mapping,
            extractor=None,
            transformer=None,
            loader=None
        )

    def test_clean_for_json_with_namedtuple(self):
        """Test that _clean_for_json can handle NamedTuple objects."""
        # Create a NamedTuple similar to LoadResult
        TestResult = namedtuple(
            'TestResult', 
            ['created', 'updated', 'skipped', 'errors', 'error_details']
        )
        
        # Create a test instance
        test_result = TestResult(
            created=5,
            updated=3,
            skipped=2,
            errors=1,
            error_details=[{'error': 'Test error'}]
        )
        
        # Clean the NamedTuple for JSON
        cleaned = self.pipeline._clean_for_json(test_result)
        
        # Verify the result is a dict with the expected values
        self.assertIsInstance(cleaned, dict)
        self.assertEqual(cleaned['created'], 5)
        self.assertEqual(cleaned['updated'], 3)
        self.assertEqual(cleaned['skipped'], 2)
        self.assertEqual(cleaned['errors'], 1)
        self.assertEqual(cleaned['error_details'], [{'error': 'Test error'}])

    def test_clean_for_json_with_datetime(self):
        """Test that _clean_for_json can handle datetime objects."""
        # Create a test datetime
        test_datetime = datetime(2025, 3, 9, 12, 0, 0, tzinfo=timezone.utc)
        
        # Clean the datetime for JSON
        cleaned = self.pipeline._clean_for_json(test_datetime)
        
        # Verify the result is an ISO format string
        self.assertIsInstance(cleaned, str)
        self.assertEqual(cleaned, '2025-03-09T12:00:00+00:00')

    def test_clean_for_json_with_nested_data(self):
        """Test that _clean_for_json can handle nested data structures."""
        # Create a test data structure with nested elements
        TestResult = namedtuple('TestResult', ['created', 'updated'])
        test_data = {
            'string': 'test',
            'int': 42,
            'float': 3.14,
            'bool': True,
            'none': None,
            'list': [1, 'two', 3.0],
            'dict': {'key': 'value'},
            'datetime': datetime(2025, 3, 9, 12, 0, 0, tzinfo=timezone.utc),
            'namedtuple': TestResult(created=5, updated=3)
        }
        
        # Clean the nested data for JSON
        cleaned = self.pipeline._clean_for_json(test_data)
        
        # Verify the result has the expected structure
        self.assertIsInstance(cleaned, dict)
        self.assertEqual(cleaned['string'], 'test')
        self.assertEqual(cleaned['int'], 42)
        self.assertEqual(cleaned['float'], 3.14)
        self.assertEqual(cleaned['bool'], True)
        self.assertIsNone(cleaned['none'])
        self.assertEqual(cleaned['list'], [1, 'two', 3.0])
        self.assertEqual(cleaned['dict'], {'key': 'value'})
        self.assertEqual(cleaned['datetime'], '2025-03-09T12:00:00+00:00')
        self.assertEqual(cleaned['namedtuple'], {'created': 5, 'updated': 3}) 