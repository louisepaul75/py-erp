"""
Pytest configuration for sync module tests.

This file configures the test environment for sync module tests
and provides fixtures for testing sync functionality.
"""
import pytest
from unittest import mock
from django.utils import timezone
from datetime import timedelta

from pyerp.sync.models import (
    SyncSource,
    SyncTarget,
    SyncMapping,
    SyncState,
    SyncLog,
    SyncLogDetail
)


@pytest.fixture
def sync_source():
    """Create a mock SyncSource for testing."""
    source = mock.MagicMock(spec=SyncSource)
    source.name = "test_source"
    source.__str__.return_value = "test_source"
    return source


@pytest.fixture
def sync_target():
    """Create a mock SyncTarget for testing."""
    target = mock.MagicMock(spec=SyncTarget)
    target.name = "test_target"
    target.__str__.return_value = "test_target"
    return target


@pytest.fixture
def sync_mapping(sync_source, sync_target):
    """Create a mock SyncMapping for testing."""
    mapping = mock.MagicMock(spec=SyncMapping)
    mapping.source = sync_source
    mapping.target = sync_target
    mapping.entity_type = "test_entity"
    mapping.__str__.return_value = (
        f"{sync_source} → {sync_target} (test_entity)"
    )
    return mapping


@pytest.fixture
def test_times():
    """Create test timestamps for testing."""
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    return {"now": now, "yesterday": yesterday}


@pytest.fixture
def sync_state(sync_mapping, test_times):
    """Create a mock SyncState for testing."""
    sync_state = mock.MagicMock(spec=SyncState)
    sync_state.mapping = sync_mapping
    sync_state.last_sync_time = test_times["yesterday"]
    sync_state.last_successful_sync_time = test_times["yesterday"]
    sync_state.last_sync_id = "123"
    sync_state.last_successful_id = "123"
    return sync_state


@pytest.fixture
def sync_log(sync_mapping):
    """Create a mock SyncLog for testing."""
    sync_log = mock.MagicMock(spec=SyncLog)
    sync_log.mapping = sync_mapping
    sync_log.status = "started"
    sync_log.is_full_sync = False
    sync_log.sync_params = {"batch_size": 100}
    sync_log.__str__.return_value = f"Sync {sync_mapping} - started"
    return sync_log


@pytest.fixture
def sync_log_detail(sync_log):
    """Create a mock SyncLogDetail for testing."""
    sync_log_detail = mock.MagicMock(spec=SyncLogDetail)
    sync_log_detail.sync_log = sync_log
    sync_log_detail.record_id = "456"
    sync_log_detail.status = "success"
    sync_log_detail.details = {"field1": "value1"}
    sync_log_detail.__str__.return_value = f"{sync_log} - 456"
    return sync_log_detail 