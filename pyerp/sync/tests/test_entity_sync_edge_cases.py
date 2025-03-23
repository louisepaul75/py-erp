"""
Tests for entity sync edge cases.

This module contains tests for edge cases and error handling in entity sync tasks.
"""

import pytest
from unittest import mock
import datetime
from django.utils import timezone

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget, SyncLog
from pyerp.sync.tasks import run_entity_sync, run_all_mappings
from pyerp.sync.exceptions import ExtractError, TransformError, LoadError


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.PipelineFactory")
@mock.patch("pyerp.sync.tasks.log_data_sync_event")
@mock.patch("pyerp.sync.tasks.SyncMapping.objects.get")
def test_run_entity_sync_extract_error(mock_get_mapping, mock_log_event, mock_pipeline_factory):
    """Test run_entity_sync task when extraction fails."""
    # Setup mock models
    mock_source = mock.MagicMock(spec=SyncSource)
    mock_source.name = "test_source"
    mock_source.config = {"type": "api"}

    mock_target = mock.MagicMock(spec=SyncTarget)
    mock_target.name = "test_target"
    mock_target.config = {"type": "django"}
    
    # Mock mapping
    mock_mapping = mock.MagicMock(spec=SyncMapping)
    mock_mapping.id = 1
    mock_mapping.source = mock_source
    mock_mapping.target = mock_target
    mock_mapping.entity_type = "test_entity"
    mock_mapping.active = True
    mock_mapping.mapping_config = {"test": "config"}
    
    # Configure get to return our mock mapping
    mock_get_mapping.return_value = mock_mapping
    
    # Create a mock pipeline
    mock_pipeline = mock.MagicMock()
    mock_pipeline.run.side_effect = ExtractError("Failed to extract data")
    
    # Configure the factory to return our mock pipeline
    mock_pipeline_factory.create_pipeline.return_value = mock_pipeline
    
    # Execute
    with pytest.raises(ExtractError) as excinfo:
        run_entity_sync(1)  # using the mapping ID
    
    # Verify
    assert "Failed to extract data" in str(excinfo.value)
    
    # Verify logging was called with error details
    mock_log_event.assert_called_once()
    log_call_args = mock_log_event.call_args[1]
    assert log_call_args["status"] == "failed"
    assert "Failed to extract data" in log_call_args["details"]["error"]


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.PipelineFactory")
@mock.patch("pyerp.sync.tasks.log_data_sync_event")
@mock.patch("pyerp.sync.tasks.SyncMapping.objects.get")
def test_run_entity_sync_transform_error(mock_get_mapping, mock_log_event, mock_pipeline_factory):
    """Test run_entity_sync task when transformation fails."""
    # Setup mock models
    mock_source = mock.MagicMock(spec=SyncSource)
    mock_source.name = "test_source"
    mock_source.config = {"type": "api"}

    mock_target = mock.MagicMock(spec=SyncTarget)
    mock_target.name = "test_target"
    mock_target.config = {"type": "django"}
    
    # Mock mapping
    mock_mapping = mock.MagicMock(spec=SyncMapping)
    mock_mapping.id = 1
    mock_mapping.source = mock_source
    mock_mapping.target = mock_target
    mock_mapping.entity_type = "test_entity"
    mock_mapping.active = True
    mock_mapping.mapping_config = {"test": "config"}
    
    # Configure get to return our mock mapping
    mock_get_mapping.return_value = mock_mapping
    
    # Create a mock pipeline
    mock_pipeline = mock.MagicMock()
    mock_pipeline.run.side_effect = TransformError("Failed to transform data")
    
    # Configure the factory to return our mock pipeline
    mock_pipeline_factory.create_pipeline.return_value = mock_pipeline
    
    # Execute
    with pytest.raises(TransformError) as excinfo:
        run_entity_sync(1)
    
    # Verify
    assert "Failed to transform data" in str(excinfo.value)
    
    # Verify logging was called with error details
    mock_log_event.assert_called_once()
    log_call_args = mock_log_event.call_args[1]
    assert log_call_args["status"] == "failed"
    assert "Failed to transform data" in log_call_args["details"]["error"]


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.PipelineFactory")
@mock.patch("pyerp.sync.tasks.log_data_sync_event")
@mock.patch("pyerp.sync.tasks.SyncMapping.objects.get")
def test_run_entity_sync_load_error(mock_get_mapping, mock_log_event, mock_pipeline_factory):
    """Test run_entity_sync task when loading fails."""
    # Setup mock models
    mock_source = mock.MagicMock(spec=SyncSource)
    mock_source.name = "test_source"
    mock_source.config = {"type": "api"}

    mock_target = mock.MagicMock(spec=SyncTarget)
    mock_target.name = "test_target"
    mock_target.config = {"type": "django"}
    
    # Mock mapping
    mock_mapping = mock.MagicMock(spec=SyncMapping)
    mock_mapping.id = 1
    mock_mapping.source = mock_source
    mock_mapping.target = mock_target
    mock_mapping.entity_type = "test_entity"
    mock_mapping.active = True
    mock_mapping.mapping_config = {"test": "config"}
    
    # Configure get to return our mock mapping
    mock_get_mapping.return_value = mock_mapping
    
    # Create a mock pipeline
    mock_pipeline = mock.MagicMock()
    mock_pipeline.run.side_effect = LoadError("Failed to load data")
    
    # Configure the factory to return our mock pipeline
    mock_pipeline_factory.create_pipeline.return_value = mock_pipeline
    
    # Execute
    with pytest.raises(LoadError) as excinfo:
        run_entity_sync(1)
    
    # Verify
    assert "Failed to load data" in str(excinfo.value)
    
    # Verify logging was called with error details
    mock_log_event.assert_called_once()
    log_call_args = mock_log_event.call_args[1]
    assert log_call_args["status"] == "failed"
    assert "Failed to load data" in log_call_args["details"]["error"]


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.PipelineFactory")
@mock.patch("pyerp.sync.tasks.log_data_sync_event")
@mock.patch("pyerp.sync.tasks.SyncMapping.objects.get")
def test_run_entity_sync_with_zero_records(mock_get_mapping, mock_log_event, mock_pipeline_factory):
    """Test run_entity_sync task when no records are processed."""
    # Setup mock models
    mock_source = mock.MagicMock(spec=SyncSource)
    mock_source.name = "test_source"
    mock_source.config = {"type": "api"}

    mock_target = mock.MagicMock(spec=SyncTarget)
    mock_target.name = "test_target"
    mock_target.config = {"type": "django"}
    
    # Mock mapping
    mock_mapping = mock.MagicMock(spec=SyncMapping)
    mock_mapping.id = 1
    mock_mapping.source = mock_source
    mock_mapping.target = mock_target
    mock_mapping.entity_type = "test_entity"
    mock_mapping.active = True
    mock_mapping.mapping_config = {"test": "config"}
    
    # Configure get to return our mock mapping
    mock_get_mapping.return_value = mock_mapping
    
    # Create a mock pipeline
    mock_pipeline = mock.MagicMock()
    
    # Create a mock SyncLog with zero records
    mock_sync_log = mock.MagicMock(spec=SyncLog)
    mock_sync_log.id = 1
    mock_sync_log.status = "success"
    mock_sync_log.records_processed = 0
    mock_sync_log.records_succeeded = 0
    mock_sync_log.records_failed = 0
    
    mock_pipeline.run.return_value = mock_sync_log
    
    # Configure the factory to return our mock pipeline
    mock_pipeline_factory.create_pipeline.return_value = mock_pipeline
    
    # Execute
    result = run_entity_sync(1)
    
    # Verify
    assert result["status"] == "success"
    assert result["records_processed"] == 0
    assert result["records_succeeded"] == 0
    assert result["records_failed"] == 0
    
    # Verify logging was called with zero records
    mock_log_event.assert_called_once()
    log_call_args = mock_log_event.call_args[1]
    assert log_call_args["record_count"] == 0


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.PipelineFactory")
@mock.patch("pyerp.sync.tasks.log_data_sync_event")
@mock.patch("pyerp.sync.tasks.SyncMapping.objects.get")
def test_run_entity_sync_with_modified_config(mock_get_mapping, mock_log_event, mock_pipeline_factory):
    """Test run_entity_sync task with modified query params."""
    # Setup mock models
    mock_source = mock.MagicMock(spec=SyncSource)
    mock_source.name = "test_source"
    mock_source.config = {"type": "api"}

    mock_target = mock.MagicMock(spec=SyncTarget)
    mock_target.name = "test_target"
    mock_target.config = {"type": "django"}
    
    # Mock mapping with custom config
    mock_mapping = mock.MagicMock(spec=SyncMapping)
    mock_mapping.id = 1
    mock_mapping.source = mock_source
    mock_mapping.target = mock_target
    mock_mapping.entity_type = "test_entity"
    mock_mapping.active = True
    mock_mapping.mapping_config = {
        "extractor_config": {
            "api_url": "https://example.com/api",
            "auth_token": "secret_token"
        }
    }
    
    # Configure get to return our mock mapping
    mock_get_mapping.return_value = mock_mapping
    
    # Create a mock pipeline
    mock_pipeline = mock.MagicMock()
    
    # Create a mock SyncLog
    mock_sync_log = mock.MagicMock(spec=SyncLog)
    mock_sync_log.id = 1
    mock_sync_log.status = "success"
    mock_sync_log.records_processed = 5
    mock_sync_log.records_succeeded = 5
    mock_sync_log.records_failed = 0
    
    mock_pipeline.run.return_value = mock_sync_log
    
    # Configure the factory to return our mock pipeline
    mock_pipeline_factory.create_pipeline.return_value = mock_pipeline
    
    # Prepare custom query parameters
    query_params = {
        "limit": 10,
        "filter": {
            "status": "active",
            "updated_after": "2023-01-01T00:00:00Z"
        }
    }
    
    # Execute
    result = run_entity_sync(1, query_params=query_params)
    
    # Verify
    assert result["status"] == "success"
    assert result["records_processed"] == 5
    
    # Verify pipeline was called with the correct parameters
    mock_pipeline.run.assert_called_once_with(
        incremental=True,
        batch_size=100,
        query_params=query_params
    )
    
    # Verify PipelineFactory was called with the right mapping
    mock_pipeline_factory.create_pipeline.assert_called_once_with(mock_mapping)


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.run_entity_sync")
@mock.patch("pyerp.sync.tasks.SyncMapping.objects.filter")
def test_run_all_mappings_no_active_mappings(mock_filter, mock_run_entity_sync):
    """Test run_all_mappings task with no active mappings."""
    # Setup - return empty queryset
    mock_filter.return_value = []
    
    # Execute
    results = run_all_mappings()
    
    # Verify
    assert results == []
    mock_filter.assert_called_once_with(active=True)
    mock_run_entity_sync.delay.assert_not_called() 