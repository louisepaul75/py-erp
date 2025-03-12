from collections import namedtuple
from datetime import datetime, timezone
import unittest
from unittest import mock

from django.utils import timezone as django_timezone

from pyerp.sync.pipeline import SyncPipeline
from pyerp.sync.models import SyncMapping
from pyerp.sync.extractors.base import BaseExtractor
from pyerp.sync.transformers.base import BaseTransformer
from pyerp.sync.loaders.base import BaseLoader, LoadResult


class MockExtractor(BaseExtractor):
    """Mock extractor for testing."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.extract_called = False
        self.query_params = None
        self.extract_results = []
    
    def get_required_config_fields(self):
        return []
        
    def connect(self):
        pass
        
    def extract(self, query_params=None):
        self.extract_called = True
        self.query_params = query_params
        return self.extract_results


class MockTransformer(BaseTransformer):
    """Mock transformer for testing."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.transform_called = False
        self.transform_input = None
        self.transform_results = []
    
    def transform(self, source_data):
        self.transform_called = True
        self.transform_input = source_data
        return self.transform_results


class MockLoader(BaseLoader):
    """Mock loader for testing."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.load_called = False
        self.load_input = None
        self.load_result = LoadResult()
    
    def get_required_config_fields(self):
        return []
        
    def prepare_record(self, record):
        return {"id": record.get("id")}, record
        
    def load_record(self, lookup_criteria, record, update_existing=True):
        return None
        
    def load(self, records, update_existing=True):
        self.load_called = True
        self.load_input = records
        return self.load_result


class TestSyncPipeline(unittest.TestCase):
    """Tests for the SyncPipeline class."""

    def setUp(self):
        """Set up test data."""
        # Create a mock SyncMapping
        self.mapping = mock.MagicMock(spec=SyncMapping)
        self.mapping.name = "test_mapping"
        self.mapping.entity_type = "test"
        self.mapping.mapping_config = {}
        
        # Create mock components
        self.extractor = MockExtractor()
        self.transformer = MockTransformer()
        self.loader = MockLoader()
        
        # Mock SyncState.objects.get_or_create
        self.mock_sync_state = mock.MagicMock()
        self.sync_state_patcher = mock.patch('pyerp.sync.pipeline.SyncState')
        self.mock_sync_state_class = self.sync_state_patcher.start()
        self.mock_sync_state_class.objects.get_or_create.return_value = (self.mock_sync_state, False)
        
        # Create a SyncPipeline instance for testing
        self.pipeline = SyncPipeline(
            mapping=self.mapping,
            extractor=self.extractor,
            transformer=self.transformer,
            loader=self.loader
        )

    def tearDown(self):
        """Clean up after tests."""
        self.sync_state_patcher.stop()

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

    @mock.patch('pyerp.sync.pipeline.SyncLog')
    def test_run_creates_sync_log(self, mock_sync_log_class):
        """Test that run creates a sync log."""
        # Set up mock
        mock_log = mock.MagicMock()
        mock_sync_log_class.objects.create.return_value = mock_log
        
        # Run the pipeline
        self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that SyncLog was created with correct parameters
        mock_sync_log_class.objects.create.assert_called_once()
        call_kwargs = mock_sync_log_class.objects.create.call_args[1]
        self.assertEqual(call_kwargs['mapping'], self.mapping)
        self.assertEqual(call_kwargs['status'], 'started')
        self.assertEqual(call_kwargs['is_full_sync'], False)
        
        # Check that sync_log was set on the pipeline
        self.assertEqual(self.pipeline.sync_log, mock_log)

    @mock.patch('pyerp.sync.pipeline.SyncState')
    def test_run_updates_sync_state(self, mock_sync_state_class):
        """Test that run updates the sync state."""
        # Set up mock
        mock_state = mock.MagicMock()
        mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
        
        # Run the pipeline
        self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that sync state was updated
        mock_state.update_sync_started.assert_called_once()

    def test_run_calls_extract_transform_load(self):
        """Test that run calls extract, transform, and load."""
        # Set up test data
        self.extractor.extract_results = [{"id": 1}, {"id": 2}]
        self.transformer.transform_results = [{"id": 1, "name": "Test"}]
        
        # Mock SyncLog and SyncState
        with mock.patch('pyerp.sync.pipeline.SyncLog') as mock_sync_log_class:
            with mock.patch('pyerp.sync.pipeline.SyncState') as mock_sync_state_class:
                # Set up mocks
                mock_log = mock.MagicMock()
                mock_sync_log_class.objects.create.return_value = mock_log
                
                mock_state = mock.MagicMock()
                mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
                
                # Run the pipeline
                self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that components were called
        self.assertTrue(self.extractor.extract_called)
        self.assertTrue(self.transformer.transform_called)
        self.assertTrue(self.loader.load_called)
        
        # Check that data was passed correctly
        self.assertEqual(
            self.transformer.transform_input, 
            self.extractor.extract_results
        )
        self.assertEqual(
            self.loader.load_input, 
            self.transformer.transform_results
        )

    def test_run_with_query_params(self):
        """Test that run passes query params to extractor."""
        # Set up test data
        query_params = {"modified_after": "2023-01-01"}
        
        # Mock SyncLog and SyncState
        with mock.patch('pyerp.sync.pipeline.SyncLog') as mock_sync_log_class:
            with mock.patch('pyerp.sync.pipeline.SyncState') as mock_sync_state_class:
                # Set up mocks
                mock_log = mock.MagicMock()
                mock_sync_log_class.objects.create.return_value = mock_log
                
                mock_state = mock.MagicMock()
                mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
                
                # Run the pipeline
                self.pipeline.run(
                    incremental=True, 
                    batch_size=10, 
                    query_params=query_params
                )
        
        # Check that query params were passed to extractor
        self.assertEqual(self.extractor.query_params, query_params)

    def test_run_with_incremental_false(self):
        """Test that run with incremental=False creates a full sync log."""
        # Mock SyncLog and SyncState
        with mock.patch('pyerp.sync.pipeline.SyncLog') as mock_sync_log_class:
            with mock.patch('pyerp.sync.pipeline.SyncState') as mock_sync_state_class:
                # Set up mocks
                mock_log = mock.MagicMock()
                mock_log.is_full_sync = True
                mock_sync_log_class.objects.create.return_value = mock_log
                
                mock_state = mock.MagicMock()
                mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
                
                # Run the pipeline
                result = self.pipeline.run(incremental=False, batch_size=10)
        
        # Check that sync log has is_full_sync=True
        self.assertTrue(result.is_full_sync)

    @mock.patch('pyerp.sync.pipeline.SyncLog')
    def test_run_marks_log_completed_on_success(self, mock_sync_log_class):
        """Test that run marks the sync log as completed on success."""
        # Set up mocks
        mock_log = mock.MagicMock()
        mock_sync_log_class.objects.create.return_value = mock_log
        
        # Set up test data
        self.extractor.extract_results = [{"id": 1}, {"id": 2}]
        self.transformer.transform_results = [{"id": 1, "name": "Test"}]
        self.loader.load_result = LoadResult(created=1, updated=0, skipped=0, errors=0)
        
        # Mock SyncState
        with mock.patch('pyerp.sync.pipeline.SyncState') as mock_sync_state_class:
            mock_state = mock.MagicMock()
            mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
            
            # Run the pipeline
            self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that mark_completed was called with correct parameters
        mock_log.mark_completed.assert_called_once_with(
            records_succeeded=1, 
            records_failed=0
        )

    @mock.patch('pyerp.sync.pipeline.SyncLog')
    def test_run_marks_log_completed_with_errors(self, mock_sync_log_class):
        """Test that run marks the sync log as completed with errors."""
        # Set up mocks
        mock_log = mock.MagicMock()
        mock_sync_log_class.objects.create.return_value = mock_log
        
        # Set up test data
        self.extractor.extract_results = [{"id": 1}, {"id": 2}]
        self.transformer.transform_results = [{"id": 1, "name": "Test"}]
        self.loader.load_result = LoadResult(created=1, updated=0, skipped=0, errors=1)
        
        # Mock SyncState
        with mock.patch('pyerp.sync.pipeline.SyncState') as mock_sync_state_class:
            mock_state = mock.MagicMock()
            mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
            
            # Run the pipeline
            self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that mark_completed was called with correct parameters
        mock_log.mark_completed.assert_called_once_with(
            records_succeeded=1, 
            records_failed=1
        )

    @mock.patch('pyerp.sync.pipeline.SyncLog')
    @mock.patch('pyerp.sync.pipeline.SyncState')
    def test_run_updates_sync_state_on_success(
        self, mock_sync_state_class, mock_sync_log_class
    ):
        """Test that run updates the sync state on success."""
        # Set up mocks
        mock_log = mock.MagicMock()
        mock_sync_log_class.objects.create.return_value = mock_log
        
        mock_state = mock.MagicMock()
        mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
        
        # Set up test data
        self.extractor.extract_results = [{"id": 1}, {"id": 2}]
        self.transformer.transform_results = [{"id": 1, "name": "Test"}]
        self.loader.load_result = LoadResult(created=1, updated=0, skipped=0, errors=0)
        
        # Run the pipeline
        self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that update_sync_completed was called with success=True
        mock_state.update_sync_completed.assert_called_once_with(success=True)

    @mock.patch('pyerp.sync.pipeline.SyncLog')
    @mock.patch('pyerp.sync.pipeline.SyncState')
    def test_run_updates_sync_state_on_failure(
        self, mock_sync_state_class, mock_sync_log_class
    ):
        """Test that run updates the sync state on failure."""
        # Set up mocks
        mock_log = mock.MagicMock()
        mock_sync_log_class.objects.create.return_value = mock_log
        
        mock_state = mock.MagicMock()
        mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
        
        # Set up test data
        self.extractor.extract_results = [{"id": 1}, {"id": 2}]
        self.transformer.transform_results = [{"id": 1, "name": "Test"}]
        self.loader.load_result = LoadResult(created=0, updated=0, skipped=0, errors=2)
        
        # Run the pipeline
        self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that update_sync_completed was called with success=False
        mock_state.update_sync_completed.assert_called_once_with(success=False)

    @mock.patch('pyerp.sync.pipeline.SyncLog')
    def test_run_handles_exception(self, mock_sync_log_class):
        """Test that run handles exceptions properly."""
        # Set up mocks
        mock_log = mock.MagicMock()
        mock_sync_log_class.objects.create.return_value = mock_log
        
        # Make the extractor raise an exception
        self.extractor.extract = mock.MagicMock(
            side_effect=Exception("Test exception")
        )
        
        # Mock SyncState
        with mock.patch('pyerp.sync.pipeline.SyncState') as mock_sync_state_class:
            mock_state = mock.MagicMock()
            mock_sync_state_class.objects.get_or_create.return_value = (mock_state, False)
            
            # Run the pipeline
            with self.assertRaises(Exception):
                self.pipeline.run(incremental=True, batch_size=10)
        
        # Check that mark_failed was called
        mock_log.mark_failed.assert_called_once()
        # Check that the error message contains our exception message
        self.assertIn(
            "Test exception", 
            mock_log.mark_failed.call_args[1]['error_message']
        ) 