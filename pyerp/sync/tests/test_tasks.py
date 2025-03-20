from unittest import mock

from django.test import TestCase

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget
from pyerp.sync.tasks import (
    run_entity_sync,
    run_all_mappings,
    run_incremental_sync,
    run_full_sync,
)


class TestSyncTasks(TestCase):
    """Tests for the sync tasks."""

    def setUp(self):
        """Set up test data with mocks instead of real DB objects."""
        # Mock source and target
        self.source = mock.MagicMock(spec=SyncSource)
        self.source.name = "test_source"
        self.source.description = "Test source"
        self.source.config = {"api_url": "http://example.com/api"}

        self.target = mock.MagicMock(spec=SyncTarget)
        self.target.name = "test_target"
        self.target.description = "Test target"
        self.target.config = {"model_class": "app.models.TestModel"}

        # Mock mappings
        self.mapping1 = mock.MagicMock(spec=SyncMapping)
        self.mapping1.id = 1
        self.mapping1.source = self.source
        self.mapping1.target = self.target
        self.mapping1.entity_type = "products"
        self.mapping1.mapping_config = {}
        self.mapping1.active = True

        self.mapping2 = mock.MagicMock(spec=SyncMapping)
        self.mapping2.id = 2
        self.mapping2.source = self.source
        self.mapping2.target = self.target
        self.mapping2.entity_type = "customers"
        self.mapping2.mapping_config = {}
        self.mapping2.active = True

        # Create inactive mapping
        self.inactive_mapping = mock.MagicMock(spec=SyncMapping)
        self.inactive_mapping.id = 3
        self.inactive_mapping.source = self.source
        self.inactive_mapping.target = self.target
        self.inactive_mapping.entity_type = "inactive"
        self.inactive_mapping.mapping_config = {}
        self.inactive_mapping.active = False

    @mock.patch("pyerp.sync.tasks.PipelineFactory")
    @mock.patch("pyerp.sync.tasks.SyncMapping.objects.get")
    @mock.patch("pyerp.sync.tasks.log_data_sync_event")
    def test_run_entity_sync(self, mock_log_event, mock_get_mapping, mock_factory):
        """Test the run_entity_sync task."""
        # Set up mock mapping
        mock_mapping = mock.MagicMock(spec=SyncMapping)
        mock_mapping.source.name = "test_source"
        mock_mapping.target.name = "test_target"
        mock_mapping.entity_type = "products"
        mock_get_mapping.return_value = mock_mapping

        # Set up mock pipeline
        mock_pipeline = mock.MagicMock()
        mock_factory.create_pipeline.return_value = mock_pipeline

        # Set up mock sync log
        mock_log = mock.MagicMock()
        mock_log.id = 123
        mock_log.status = "completed"
        mock_log.records_processed = 10
        mock_log.records_succeeded = 8
        mock_log.records_failed = 2
        mock_pipeline.run.return_value = mock_log

        # Run the task
        result = run_entity_sync(
            self.mapping1.id,
            incremental=True,
            batch_size=50,
            query_params={"modified_after": "2023-01-01"},
        )

        # Check that mapping was fetched correctly
        mock_get_mapping.assert_called_once_with(id=self.mapping1.id, active=True)

        # Check that pipeline was created and run
        mock_factory.create_pipeline.assert_called_once_with(mock_mapping)
        mock_pipeline.run.assert_called_once_with(
            incremental=True,
            batch_size=50,
            query_params={"modified_after": "2023-01-01"},
        )

        # Check that log event was called
        mock_log_event.assert_called_once()

        # Check result
        self.assertEqual(result["sync_log_id"], 123)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["records_processed"], 10)
        self.assertEqual(result["records_succeeded"], 8)
        self.assertEqual(result["records_failed"], 2)

    @mock.patch("pyerp.sync.tasks.run_entity_sync")
    @mock.patch("pyerp.sync.tasks.SyncMapping.objects.filter")
    @mock.patch("pyerp.sync.tasks.log_data_sync_event")
    def test_run_all_mappings(self, mock_log_event, mock_filter, mock_run_entity_sync):
        """Test the run_all_mappings task."""
        # Set up a task result mock for run_entity_sync.delay
        class MockAsyncResult:
            def __init__(self):
                self.id = "async-task-id"

        mock_run_entity_sync.delay.return_value = MockAsyncResult()
        
        # Set up mock for SyncMapping.objects.filter
        mock_queryset = mock.MagicMock()
        mock_queryset.__iter__.return_value = [self.mapping1, self.mapping2]
        mock_filter.return_value = mock_queryset

        # Run the task
        results = run_all_mappings(incremental=True)

        # Check filter was called correctly
        mock_filter.assert_called_once_with(active=True)

        # Check that run_entity_sync.delay was called for each active mapping
        self.assertEqual(mock_run_entity_sync.delay.call_count, 2)

        # Check that it was called with the right mapping IDs
        mapping_ids = [
            call_args[0][0] for call_args in mock_run_entity_sync.delay.call_args_list
        ]
        self.assertIn(self.mapping1.id, mapping_ids)
        self.assertIn(self.mapping2.id, mapping_ids)
        self.assertNotIn(self.inactive_mapping.id, mapping_ids)

        # Check log event was called
        mock_log_event.assert_called_once()

        # Check results
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result["task_id"], "async-task-id")
            # Check that mapping_id is one of our active mappings
            self.assertIn(result["mapping_id"], [self.mapping1.id, self.mapping2.id])

    @mock.patch("pyerp.sync.tasks.run_all_mappings")
    @mock.patch("pyerp.sync.tasks.log_data_sync_event")
    def test_run_incremental_sync(self, mock_log_event, mock_run_all_mappings):
        """Test the run_incremental_sync task."""
        # Set up mock return value
        mock_run_all_mappings.return_value = [
            {"mapping_id": 1, "entity_type": "products", "task_id": "task-1"},
            {"mapping_id": 2, "entity_type": "customers", "task_id": "task-2"},
        ]

        # Run the task
        results = run_incremental_sync()

        # Check log event was called
        mock_log_event.assert_called_once()

        # Check that run_all_mappings was called with incremental=True
        mock_run_all_mappings.assert_called_once_with(incremental=True)

        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["mapping_id"], 1)
        self.assertEqual(results[1]["mapping_id"], 2)

    @mock.patch("pyerp.sync.tasks.run_all_mappings")
    @mock.patch("pyerp.sync.tasks.log_data_sync_event")
    def test_run_full_sync(self, mock_log_event, mock_run_all_mappings):
        """Test the run_full_sync task."""
        # Set up mock return value
        mock_run_all_mappings.return_value = [
            {"mapping_id": 1, "entity_type": "products", "task_id": "task-1"},
            {"mapping_id": 2, "entity_type": "customers", "task_id": "task-2"},
        ]

        # Run the task
        results = run_full_sync()

        # Check log event was called
        mock_log_event.assert_called_once()

        # Check that run_all_mappings was called with incremental=False
        mock_run_all_mappings.assert_called_once_with(incremental=False)

        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["mapping_id"], 1)
        self.assertEqual(results[1]["mapping_id"], 2)
