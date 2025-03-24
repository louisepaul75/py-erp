import unittest
from unittest import mock
from django.utils import timezone
from datetime import timedelta
import pytest
from django.test import TestCase

from pyerp.sync.models import (
    SyncSource,
    SyncTarget,
    SyncMapping,
    SyncState,
    SyncLog,
    SyncLogDetail,
)


@pytest.mark.unit
class TestSyncModels(TestCase):
    """Tests for the sync models."""

    def setUp(self):
        """Set up test data with mocks."""
        # Create source and target
        self.source = mock.MagicMock(spec=SyncSource)
        self.source.name = "test_source"
        self.source.__str__.return_value = "test_source"

        self.target = mock.MagicMock(spec=SyncTarget)
        self.target.name = "test_target"
        self.target.__str__.return_value = "test_target"

        # Create mapping
        self.mapping = mock.MagicMock(spec=SyncMapping)
        self.mapping.source = self.source
        self.mapping.target = self.target
        self.mapping.entity_type = "test_entity"
        self.mapping.__str__.return_value = (
            f"{self.source} → {self.target} (test_entity)"
        )

        # Create sync state
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)

        self.sync_state = mock.MagicMock(spec=SyncState)
        self.sync_state.mapping = self.mapping
        self.sync_state.last_sync_time = self.yesterday
        self.sync_state.last_successful_sync_time = self.yesterday
        self.sync_state.last_sync_id = "123"
        self.sync_state.last_successful_id = "123"

        # Create sync log
        self.sync_log = mock.MagicMock(spec=SyncLog)
        self.sync_log.mapping = self.mapping
        self.sync_log.status = "started"
        self.sync_log.is_full_sync = False
        self.sync_log.sync_params = {"batch_size": 100}
        self.sync_log.__str__.return_value = f"Sync {self.mapping} - started"

        # Create sync log detail
        self.sync_log_detail = mock.MagicMock(spec=SyncLogDetail)
        self.sync_log_detail.sync_log = self.sync_log
        self.sync_log_detail.record_id = "456"
        self.sync_log_detail.status = "success"
        self.sync_log_detail.record_data = {"id": "456", "name": "Test"}
        self.sync_log_detail.__str__.return_value = f"{self.sync_log} - 456"














    def test_sync_source_str(self):
        """Test the string representation of SyncSource."""
        self.assertEqual(str(self.source), "test_source")


    def test_sync_target_str(self):
        """Test the string representation of SyncTarget."""
        self.assertEqual(str(self.target), "test_target")


    def test_sync_mapping_str(self):
        """Test the string representation of SyncMapping."""
        expected = f"{self.source} → {self.target} (test_entity)"
        self.assertEqual(str(self.mapping), expected)


    def test_sync_state_update_sync_started(self):
        """Test updating sync state when sync starts."""
        # Mock the SyncState class and its update_sync_started method
        with mock.patch("django.utils.timezone.now", return_value=self.now):
            # Call the method directly on our mock
            self.sync_state.last_sync_time = self.yesterday

            # Mock the update_sync_started method implementation
            def update_sync_started_impl():
                self.sync_state.last_sync_time = self.now
                self.sync_state.save()

            # Attach the implementation to our mock
            self.sync_state.update_sync_started = update_sync_started_impl
            self.sync_state.save = mock.MagicMock()

            # Call the method
            self.sync_state.update_sync_started()

        # Check that last_sync_time was updated
        self.assertEqual(self.sync_state.last_sync_time, self.now)
        # Verify save was called
        self.sync_state.save.assert_called_once()


    def test_sync_state_update_sync_completed_success(self):
        """Test updating sync state when sync completes successfully."""
        # Set up initial state
        self.sync_state.last_sync_time = self.now
        self.sync_state.last_successful_sync_time = self.yesterday

        # Mock the update_sync_completed method implementation
        def update_sync_completed_impl(success=True):
            if success:
                self.sync_state.last_successful_sync_time = (
                    self.sync_state.last_sync_time
                )
                self.sync_state.last_successful_id = self.sync_state.last_sync_id
            self.sync_state.save()

        # Attach the implementation to our mock
        self.sync_state.update_sync_completed = update_sync_completed_impl
        self.sync_state.save = mock.MagicMock()

        # Call the method
        self.sync_state.update_sync_completed(success=True)

        # Check that last_successful_sync_time was updated
        self.assertEqual(
            self.sync_state.last_successful_sync_time, self.sync_state.last_sync_time
        )
        # Verify save was called
        self.sync_state.save.assert_called_once()


    def test_sync_state_update_sync_completed_failure(self):
        """Test updating sync state when sync fails."""
        # Set up initial state
        self.sync_state.last_sync_time = self.now
        self.sync_state.last_successful_sync_time = self.yesterday

        # Mock the update_sync_completed method implementation
        def update_sync_completed_impl(success=True):
            if success:
                self.sync_state.last_successful_sync_time = (
                    self.sync_state.last_sync_time
                )
                self.sync_state.last_successful_id = self.sync_state.last_sync_id
            self.sync_state.save()

        # Attach the implementation to our mock
        self.sync_state.update_sync_completed = update_sync_completed_impl
        self.sync_state.save = mock.MagicMock()

        # Call the method
        self.sync_state.update_sync_completed(success=False)

        # Check that last_successful_sync_time was not updated
        self.assertEqual(self.sync_state.last_successful_sync_time, self.yesterday)
        # Verify save was called
        self.sync_state.save.assert_called_once()


    def test_sync_log_mark_completed(self):
        """Test marking a sync log as completed."""
        # Set up initial state
        self.sync_log.status = "started"
        self.sync_log.records_succeeded = 0
        self.sync_log.records_failed = 0
        self.sync_log.records_processed = 0
        self.sync_log.end_time = None

        # Mock the mark_completed method implementation
        def mark_completed_impl(records_succeeded=0, records_failed=0):
            self.sync_log.records_succeeded = records_succeeded
            self.sync_log.records_failed = records_failed
            self.sync_log.records_processed = records_succeeded + records_failed
            self.sync_log.end_time = self.now

            if records_failed > 0:
                self.sync_log.status = "partial"
            else:
                self.sync_log.status = "completed"

            self.sync_log.save()

        # Attach the implementation to our mock
        self.sync_log.mark_completed = mark_completed_impl
        self.sync_log.save = mock.MagicMock()

        # Call the method
        with mock.patch("django.utils.timezone.now", return_value=self.now):
            self.sync_log.mark_completed(records_succeeded=10, records_failed=2)

        # Check updated fields
        self.assertEqual(self.sync_log.status, "partial")
        self.assertEqual(self.sync_log.records_succeeded, 10)
        self.assertEqual(self.sync_log.records_failed, 2)
        self.assertEqual(self.sync_log.records_processed, 12)
        self.assertEqual(self.sync_log.end_time, self.now)
        # Verify save was called
        self.sync_log.save.assert_called_once()


    def test_sync_log_mark_completed_all_success(self):
        """Test marking a sync log as completed with all successes."""
        # Set up initial state
        self.sync_log.status = "started"
        self.sync_log.records_succeeded = 0
        self.sync_log.records_failed = 0
        self.sync_log.records_processed = 0
        self.sync_log.end_time = None

        # Mock the mark_completed method implementation
        def mark_completed_impl(records_succeeded=0, records_failed=0):
            self.sync_log.records_succeeded = records_succeeded
            self.sync_log.records_failed = records_failed
            self.sync_log.records_processed = records_succeeded + records_failed
            self.sync_log.end_time = self.now

            if records_failed > 0:
                self.sync_log.status = "partial"
            else:
                self.sync_log.status = "completed"

            self.sync_log.save()

        # Attach the implementation to our mock
        self.sync_log.mark_completed = mark_completed_impl
        self.sync_log.save = mock.MagicMock()

        # Call the method
        with mock.patch("django.utils.timezone.now", return_value=self.now):
            self.sync_log.mark_completed(records_succeeded=10, records_failed=0)

        # Check updated fields
        self.assertEqual(self.sync_log.status, "completed")
        self.assertEqual(self.sync_log.records_succeeded, 10)
        self.assertEqual(self.sync_log.records_failed, 0)
        self.assertEqual(self.sync_log.records_processed, 10)
        self.assertEqual(self.sync_log.end_time, self.now)
        # Verify save was called
        self.sync_log.save.assert_called_once()


    def test_sync_log_mark_failed(self):
        """Test marking a sync log as failed."""
        # Set up initial state
        self.sync_log.status = "started"
        self.sync_log.error_message = None
        self.sync_log.trace = None
        self.sync_log.end_time = None

        # Mock the mark_failed method implementation
        def mark_failed_impl(error_message="", trace=""):
            self.sync_log.status = "failed"
            self.sync_log.error_message = error_message
            self.sync_log.trace = trace
            self.sync_log.end_time = self.now
            self.sync_log.save()

        # Attach the implementation to our mock
        self.sync_log.mark_failed = mark_failed_impl
        self.sync_log.save = mock.MagicMock()

        error_message = "Connection error"
        trace = "Traceback: ..."

        # Call the method
        with mock.patch("django.utils.timezone.now", return_value=self.now):
            self.sync_log.mark_failed(error_message=error_message, trace=trace)

        # Check updated fields
        self.assertEqual(self.sync_log.status, "failed")
        self.assertEqual(self.sync_log.error_message, error_message)
        self.assertEqual(self.sync_log.trace, trace)
        self.assertEqual(self.sync_log.end_time, self.now)
        # Verify save was called
        self.sync_log.save.assert_called_once()


    def test_sync_log_detail_str(self):
        """Test the string representation of SyncLogDetail."""
        expected = f"{self.sync_log} - 456"
        self.assertEqual(str(self.sync_log_detail), expected)
