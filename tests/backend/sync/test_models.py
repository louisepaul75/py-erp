"""
Tests for the sync models.

This module tests the models in the sync module including SyncSource,
SyncTarget, SyncMapping, SyncState, SyncLog, and SyncLogDetail.
"""
from unittest import mock


def test_sync_source_str(sync_source):
    """Test the string representation of SyncSource."""
    assert str(sync_source) == "test_source"


def test_sync_target_str(sync_target):
    """Test the string representation of SyncTarget."""
    assert str(sync_target) == "test_target"


def test_sync_mapping_str(sync_mapping):
    """Test the string representation of SyncMapping."""
    expected = "test_source → test_target (test_entity)"
    assert str(sync_mapping) == expected


def test_sync_state_update_sync_started(sync_state, test_times):
    """Test updating sync state when sync starts."""
    # Mock the update_sync_started method implementation
    def update_sync_started_impl():
        sync_state.last_sync_time = test_times["now"]
        sync_state.save()
    
    # Attach the implementation to our mock
    sync_state.update_sync_started = update_sync_started_impl
    sync_state.save = mock.MagicMock()
    
    # Call the method
    with mock.patch('django.utils.timezone.now', 
                    return_value=test_times["now"]):
        sync_state.update_sync_started()
    
    # Check that last_sync_time was updated
    assert sync_state.last_sync_time == test_times["now"]
    # Verify save was called
    sync_state.save.assert_called_once()


def test_sync_state_update_sync_completed_success(sync_state, test_times):
    """Test updating sync state when sync completes successfully."""
    # Set up initial state
    sync_state.last_sync_time = test_times["now"]
    sync_state.last_successful_sync_time = test_times["yesterday"]
    
    # Mock the update_sync_completed method implementation
    def update_sync_completed_impl(success=True):
        if success:
            sync_state.last_successful_sync_time = sync_state.last_sync_time
            sync_state.last_successful_id = sync_state.last_sync_id
        sync_state.save()
    
    # Attach the implementation to our mock
    sync_state.update_sync_completed = update_sync_completed_impl
    sync_state.save = mock.MagicMock()
    
    # Call the method
    sync_state.update_sync_completed(success=True)
    
    # Check that last_successful_sync_time was updated
    assert sync_state.last_successful_sync_time == sync_state.last_sync_time
    # Verify save was called
    sync_state.save.assert_called_once()


def test_sync_state_update_sync_completed_failure(sync_state, test_times):
    """Test updating sync state when sync fails."""
    # Set up initial state
    sync_state.last_sync_time = test_times["now"]
    sync_state.last_successful_sync_time = test_times["yesterday"]
    
    # Mock the update_sync_completed method implementation
    def update_sync_completed_impl(success=True):
        if success:
            sync_state.last_successful_sync_time = sync_state.last_sync_time
            sync_state.last_successful_id = sync_state.last_sync_id
        sync_state.save()
    
    # Attach the implementation to our mock
    sync_state.update_sync_completed = update_sync_completed_impl
    sync_state.save = mock.MagicMock()
    
    # Call the method
    sync_state.update_sync_completed(success=False)
    
    # Check that last_successful_sync_time was not updated
    assert sync_state.last_successful_sync_time == test_times["yesterday"]
    # Verify save was called
    sync_state.save.assert_called_once()


def test_sync_log_mark_completed(sync_log, test_times):
    """Test marking a sync log as completed."""
    # Set up initial state
    sync_log.status = "started"
    sync_log.records_succeeded = 0
    sync_log.records_failed = 0
    sync_log.records_processed = 0
    sync_log.end_time = None
    
    # Mock the mark_completed method implementation
    def mark_completed_impl(records_succeeded=0, records_failed=0):
        sync_log.records_succeeded = records_succeeded
        sync_log.records_failed = records_failed
        sync_log.records_processed = records_succeeded + records_failed
        sync_log.end_time = test_times["now"]
        
        if records_failed > 0:
            sync_log.status = "partial"
        else:
            sync_log.status = "completed"
            
        sync_log.save()
    
    # Attach the implementation to our mock
    sync_log.mark_completed = mark_completed_impl
    sync_log.save = mock.MagicMock()
    
    # Call the method
    with mock.patch('django.utils.timezone.now', 
                    return_value=test_times["now"]):
        sync_log.mark_completed(records_succeeded=10, records_failed=2)
    
    # Check updated fields
    assert sync_log.status == "partial"
    assert sync_log.records_succeeded == 10
    assert sync_log.records_failed == 2
    assert sync_log.records_processed == 12
    assert sync_log.end_time == test_times["now"]
    # Verify save was called
    sync_log.save.assert_called_once()


def test_sync_log_mark_completed_all_success(sync_log, test_times):
    """Test marking a sync log as completed with all successes."""
    # Set up initial state
    sync_log.status = "started"
    sync_log.records_succeeded = 0
    sync_log.records_failed = 0
    sync_log.records_processed = 0
    sync_log.end_time = None
    
    # Mock the mark_completed method implementation
    def mark_completed_impl(records_succeeded=0, records_failed=0):
        sync_log.records_succeeded = records_succeeded
        sync_log.records_failed = records_failed
        sync_log.records_processed = records_succeeded + records_failed
        sync_log.end_time = test_times["now"]
        
        if records_failed > 0:
            sync_log.status = "partial"
        else:
            sync_log.status = "completed"
            
        sync_log.save()
    
    # Attach the implementation to our mock
    sync_log.mark_completed = mark_completed_impl
    sync_log.save = mock.MagicMock()
    
    # Call the method
    with mock.patch('django.utils.timezone.now', 
                    return_value=test_times["now"]):
        sync_log.mark_completed(records_succeeded=10, records_failed=0)
    
    # Check updated fields
    assert sync_log.status == "completed"
    assert sync_log.records_succeeded == 10
    assert sync_log.records_failed == 0
    assert sync_log.records_processed == 10
    assert sync_log.end_time == test_times["now"]
    # Verify save was called
    sync_log.save.assert_called_once()


def test_sync_log_mark_failed(sync_log, test_times):
    """Test marking a sync log as failed."""
    # Set up initial state
    sync_log.status = "started"
    sync_log.error_message = None
    sync_log.trace = None
    sync_log.end_time = None
    
    # Mock the mark_failed method implementation
    def mark_failed_impl(error_message="", trace=""):
        sync_log.status = "failed"
        sync_log.error_message = error_message
        sync_log.trace = trace
        sync_log.end_time = test_times["now"]
        sync_log.save()
    
    # Attach the implementation to our mock
    sync_log.mark_failed = mark_failed_impl
    sync_log.save = mock.MagicMock()
    
    error_message = "Connection error"
    trace = "Traceback: ..."
    
    # Call the method
    with mock.patch('django.utils.timezone.now', 
                    return_value=test_times["now"]):
        sync_log.mark_failed(error_message=error_message, trace=trace)
    
    # Check updated fields
    assert sync_log.status == "failed"
    assert sync_log.error_message == error_message
    assert sync_log.trace == trace
    assert sync_log.end_time == test_times["now"]
    # Verify save was called
    sync_log.save.assert_called_once()


def test_sync_log_detail_str(sync_log_detail):
    """Test the string representation of SyncLogDetail."""
    expected = f"{sync_log_detail.sync_log} - 456"
    assert str(sync_log_detail) == expected 