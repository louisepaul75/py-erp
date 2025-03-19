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
        """Set up test data."""
        # Create source and target
        self.source = SyncSource.objects.create(
            name="test_source",
            description="Test source",
            config={"api_url": "http://example.com/api"},
        )

        self.target = SyncTarget.objects.create(
            name="test_target",
            description="Test target",
            config={"model_class": "app.models.TestModel"},
        )

        # Create mappings
        self.mapping1 = SyncMapping.objects.create(
            source=self.source,
            target=self.target,
            entity_type="products",
            mapping_config={},
            active=True,
        )

        self.mapping2 = SyncMapping.objects.create(
            source=self.source,
            target=self.target,
            entity_type="customers",
            mapping_config={},
            active=True,
        )

        # Create inactive mapping
        self.inactive_mapping = SyncMapping.objects.create(
            source=self.source,
            target=self.target,
            entity_type="inactive",
            mapping_config={},
            active=False,
        )

    @mock.patch("pyerp.sync.tasks.PipelineFactory")
    def test_run_entity_sync(self, mock_factory):
        """Test the run_entity_sync task."""
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

        # Check that pipeline was created and run
        mock_factory.create_pipeline.assert_called_once_with(self.mapping1)
        mock_pipeline.run.assert_called_once_with(
            incremental=True,
            batch_size=50,
            query_params={"modified_after": "2023-01-01"},
        )

        # Check result
        self.assertEqual(result["sync_log_id"], 123)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["records_processed"], 10)
        self.assertEqual(result["records_succeeded"], 8)
        self.assertEqual(result["records_failed"], 2)

    @mock.patch("pyerp.sync.tasks.run_entity_sync")
    def test_run_all_mappings(self, mock_run_entity_sync):
        """Test the run_all_mappings task."""
        # Set up mock return values
        mock_run_entity_sync.return_value = {"sync_log_id": 123, "status": "completed"}

        # Run the task
        results = run_all_mappings(incremental=True)

        # Check that run_entity_sync was called for each active mapping
        self.assertEqual(mock_run_entity_sync.call_count, 2)

        # Check that it was called with the right mapping IDs
        mapping_ids = [
            call_args[0][0] for call_args in mock_run_entity_sync.call_args_list
        ]
        self.assertIn(self.mapping1.id, mapping_ids)
        self.assertIn(self.mapping2.id, mapping_ids)
        self.assertNotIn(self.inactive_mapping.id, mapping_ids)

        # Check results
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result["sync_log_id"], 123)
            self.assertEqual(result["status"], "completed")

    @mock.patch("pyerp.sync.tasks.run_all_mappings")
    def test_run_incremental_sync(self, mock_run_all_mappings):
        """Test the run_incremental_sync task."""
        # Set up mock return value
        mock_run_all_mappings.return_value = [
            {"sync_log_id": 123, "status": "completed"},
            {"sync_log_id": 124, "status": "completed"},
        ]

        # Run the task
        results = run_incremental_sync()

        # Check that run_all_mappings was called with incremental=True
        mock_run_all_mappings.assert_called_once_with(
            incremental=True, source_name=None
        )

        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["sync_log_id"], 123)
        self.assertEqual(results[1]["sync_log_id"], 124)

    @mock.patch("pyerp.sync.tasks.run_all_mappings")
    def test_run_full_sync(self, mock_run_all_mappings):
        """Test the run_full_sync task."""
        # Set up mock return value
        mock_run_all_mappings.return_value = [
            {"sync_log_id": 123, "status": "completed"},
            {"sync_log_id": 124, "status": "completed"},
        ]

        # Run the task
        results = run_full_sync()

        # Check that run_all_mappings was called with incremental=False
        mock_run_all_mappings.assert_called_once_with(
            incremental=False, source_name=None
        )

        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["sync_log_id"], 123)
        self.assertEqual(results[1]["sync_log_id"], 124)
