# pyerp/sync/tests/test_base_sync_command.py
import pytest
import json
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone as dt_timezone
from unittest.mock import patch, MagicMock

from django.core.management import CommandError, call_command
from django.utils import timezone

from pyerp.sync.management.commands.base_sync_command import BaseSyncCommand
from pyerp.sync.models import SyncMapping

# A concrete command for testing purposes
class TestSyncCommand(BaseSyncCommand):
    help = "Test sync command"
    entity_type = "test_entity" # Example entity type

    def handle(self, *args, **options):
        # Minimal implementation for testing base class methods
        self.stdout.write(f"Handling command for {self.entity_type}")
        # Example: Build params and maybe call run_sync_via_command
        query_params = self.build_query_params(options)
        # self.run_sync_via_command(self.entity_type, options, query_params)
        self.stdout.write("Handle finished.")


@pytest.fixture
def test_command():
    """Provides an instance of the concrete test command."""
    return TestSyncCommand()

@pytest.fixture
def mock_sync_mapping():
    """Provides a mock SyncMapping object."""
    mapping = MagicMock(spec=SyncMapping)
    mapping.id = 1
    mapping.entity_type = "test_entity"
    mapping.active = True
    # Add other fields if needed by tests
    return mapping

@pytest.fixture(autouse=True)
def mock_timezone_now(mocker):
    """Mocks django.utils.timezone.now() to return a fixed datetime."""
    mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt_timezone.utc)
    mocker.patch('django.utils.timezone.now', return_value=mock_now)
    return mock_now

# --- Test add_arguments ---

def test_add_arguments(test_command):
    """Verify common arguments are added."""
    parser = ArgumentParser()
    test_command.add_arguments(parser)
    args = parser.parse_args([]) # Parse with no actual args to check defaults/presence

    assert hasattr(args, 'full')
    assert hasattr(args, 'force_update')
    assert hasattr(args, 'batch_size')
    assert hasattr(args, 'top')
    assert hasattr(args, 'days')
    assert hasattr(args, 'filters')
    assert hasattr(args, 'debug')
    assert hasattr(args, 'fail_on_filter_error')
    assert hasattr(args, 'clear_cache')

    assert args.batch_size == 100 # Check default
    assert args.fail_on_filter_error is True # Check default


# --- Test build_query_params ---

@pytest.mark.parametrize(
    "options, expected_params",
    [
        ({}, {}), # No options
        ({'top': 50}, {'$top': 50}), # Top
        ({'days': 7}, {'filter_query': [['modified_date', '>=', '2023-12-25']]}), # Days
        (
            {'filters': '{"custom_field": "value1"}'},
            {'custom_field': 'value1'}
        ), # Custom filters
        (
            {'days': 3, 'filters': '{"status": "active"}'},
            {'status': 'active', 'filter_query': [['modified_date', '>=', '2023-12-29']]}
        ), # Days and custom filters
        (
            {'top': 10, 'days': 1},
            {'$top': 10, 'filter_query': [['modified_date', '>=', '2023-12-31']]}
        ), # Top and Days
        (
            {'top': 20, 'filters': '{"priority": 1}'},
            {'$top': 20, 'priority': 1}
        ), # Top and filters
        (
             {'top': 5, 'days': 2, 'filters': '{"type": "A"}'},
             {'$top': 5, 'type': 'A', 'filter_query': [['modified_date', '>=', '2023-12-30']]}
        ), # All three: top, days, filters
    ],
    ids=[
        "no_options",
        "top_only",
        "days_only",
        "filters_only",
        "days_and_filters",
        "top_and_days",
        "top_and_filters",
        "top_days_and_filters",
    ]
)
def test_build_query_params_combinations(test_command, options, expected_params, mock_timezone_now):
    """Test build_query_params with various option combinations."""
    # Ensure default options are present if not provided
    full_options = {
        'full': False, 'force_update': False, 'batch_size': 100, 'top': None,
        'days': None, 'filters': None, 'debug': False,
        'fail_on_filter_error': True, 'clear_cache': False,
        **options # Override with specific test options
    }
    params = test_command.build_query_params(full_options)

    # Sort filter_query lists for consistent comparison if present
    if 'filter_query' in params:
        params['filter_query'].sort()
    if 'filter_query' in expected_params:
        expected_params['filter_query'].sort()

    assert params == expected_params

def test_build_query_params_invalid_filters_json(test_command, caplog):
    """Test build_query_params with invalid JSON in --filters."""
    options = {'filters': '{"invalid json', 'days': None, 'top': None}
    params = test_command.build_query_params(options)
    assert params == {} # Invalid JSON should be ignored
    assert any(
        rec.levelname == "WARNING" and "Invalid JSON format for --filters option" in rec.message
        for rec in caplog.records
    )

def test_build_query_params_non_dict_filters_json(test_command, caplog):
    """Test build_query_params with valid JSON that isn't a dictionary."""
    options = {'filters': '[1, 2, 3]', 'days': None, 'top': None}
    params = test_command.build_query_params(options)
    assert params == {} # Non-dict JSON should be ignored
    assert any(
        rec.levelname == "WARNING" and "Ignoring --filters: Expected JSON dict" in rec.message
        for rec in caplog.records
    )

def test_build_query_params_negative_days(test_command, caplog):
    """Test build_query_params with a negative value for --days."""
    options = {'days': -5, 'filters': None, 'top': None}
    params = test_command.build_query_params(options)
    assert 'filter_query' not in params # Negative days ignored
    assert any(
        rec.levelname == "WARNING" and "Ignoring --days: Value must be non-negative" in rec.message
        for rec in caplog.records
    )

def test_build_query_params_invalid_days_value(test_command, caplog):
    """Test build_query_params with a non-integer value for --days."""
    options = {'days': 'abc', 'filters': None, 'top': None}
    params = test_command.build_query_params(options)
    assert 'filter_query' not in params # Invalid days ignored
    assert any(
        rec.levelname == "WARNING" and "Invalid value for --days" in rec.message
        for rec in caplog.records
    )


# --- Test get_mapping ---

@patch('pyerp.sync.models.SyncMapping.objects.get')
def test_get_mapping_success(mock_get, test_command, mock_sync_mapping):
    """Test get_mapping when a single active mapping exists."""
    mock_get.return_value = mock_sync_mapping
    mapping = test_command.get_mapping("test_entity")
    mock_get.assert_called_once_with(entity_type="test_entity", active=True)
    assert mapping == mock_sync_mapping

@patch('pyerp.sync.models.SyncMapping.objects.get')
def test_get_mapping_not_found(mock_get, test_command):
    """Test get_mapping when no active mapping is found."""
    mock_get.side_effect = SyncMapping.DoesNotExist
    with pytest.raises(CommandError, match="No active SyncMapping found"):
        test_command.get_mapping("test_entity")
    mock_get.assert_called_once_with(entity_type="test_entity", active=True)

@patch('pyerp.sync.models.SyncMapping.objects.get')
def test_get_mapping_multiple_found(mock_get, test_command):
    """Test get_mapping when multiple active mappings are found."""
    mock_get.side_effect = SyncMapping.MultipleObjectsReturned
    with pytest.raises(CommandError, match="Multiple active SyncMappings found"):
        test_command.get_mapping("test_entity")
    mock_get.assert_called_once_with(entity_type="test_entity", active=True)


# --- Test run_sync_via_command ---

@patch('django.core.management.call_command')
@patch.object(TestSyncCommand, 'build_query_params') # Mock on the Test class
def test_run_sync_via_command_basic(mock_build_params, mock_call_command, test_command):
    """Test basic call flow of run_sync_via_command when params are built."""
    entity_type = "customer"
    options = {
        'full': False, 'force_update': False, 'batch_size': 50, 'top': None,
        'days': None, 'filters': None, 'debug': False,
        'fail_on_filter_error': True, 'clear_cache': False
    }
    # Define what build_query_params should return for this test
    built_params = {'status': 'active'}
    mock_build_params.return_value = built_params

    # Call without providing query_params, so build_query_params is invoked
    test_command.run_sync_via_command(entity_type, options, query_params=None)

    mock_build_params.assert_called_once_with(options) # Called when query_params is None
    expected_filters = {'filter_query': [['status', '=', 'active']]}
    expected_filters_json = json.dumps(expected_filters)
    expected_call_options = {
        'entity_type': entity_type,
        'full': False,
        'batch_size': 50,
        'filters': expected_filters_json,
        'debug': False,
        'fail_on_filter_error': True,
        'clear_cache': False, # Default to False, handle() controls actual value
    }
    mock_call_command.assert_called_once_with("run_sync", **expected_call_options)

@patch('django.core.management.call_command')
@patch.object(TestSyncCommand, 'build_query_params') # Mock build_params again
def test_run_sync_via_command_with_provided_params(mock_build_params, mock_call_command, test_command):
    """Test run_sync_via_command when query_params are provided directly."""
    entity_type = "product"
    options = { # Base options used for flags like 'full', 'debug' etc.
        'full': True, 'force_update': False, 'batch_size': 200, 'top': None,
        'days': None, 'filters': None, 'debug': True,
        'fail_on_filter_error': False, 'clear_cache': True # Assume handle() set this
    }
    # Specific params for this call, overriding anything from base options
    query_params = {
        '$top': 25,
        'legacy_id__in': ['id1', 'id2'],
        'warehouse_code': 'WH01'
    }

    # Call WITH query_params provided
    test_command.run_sync_via_command(entity_type, options, query_params)

    # build_query_params should NOT have been called
    mock_build_params.assert_not_called()

    expected_filters = {
        '$top': 25,
        # legacy_id__in becomes __KEY filter_query items
        'filter_query': [
            ['__KEY', '=', 'id1'], ['__KEY', '=', 'id2'],
            ['warehouse_code', '=', 'WH01']
        ]
    }
    # Sort filter_query for consistent comparison
    expected_filters['filter_query'].sort()
    expected_filters_json = json.dumps(expected_filters)

    expected_call_options = {
        'entity_type': entity_type,
        'full': True, # Takes from options
        'batch_size': 200, # Takes from options
        'filters': expected_filters_json, # Built from provided query_params
        'debug': True, # Takes from options
        'fail_on_filter_error': False, # Takes from options
        'clear_cache': True, # Takes from options
    }
    mock_call_command.assert_called_once_with("run_sync", **expected_call_options)


@patch('django.core.management.call_command')
def test_run_sync_via_command_filter_mapping(mock_call_command, test_command):
    """Test specific filter mappings (legacy_id, __in, basic)."""
    query_params = {
        'legacy_id': 'abc', # Should map to __KEY = abc
        'status__in': ['A', 'B'], # Should map to status=A OR status=B
        'name': 'Test Product', # Basic equality
        'price': 10.99 # Basic equality
    }
    options = {'batch_size': 100, 'debug': False, 'fail_on_filter_error': True} # Minimal options

    test_command.run_sync_via_command("item", options, query_params)

    expected_filters = {
        'filter_query': [
            ['__KEY', '=', 'abc'],
            ['status', '=', 'A'],
            ['status', '=', 'B'],
            ['name', '=', 'Test Product'],
            ['price', '=', 10.99],
        ]
    }
    # Sort for consistent comparison
    expected_filters['filter_query'].sort()
    filters_json = json.dumps(expected_filters)

    mock_call_command.assert_called_once()
    call_args, call_kwargs = mock_call_command.call_args
    assert call_args == ("run_sync",)
    # Sort the filter_query within the actual call args for comparison
    actual_filters_dict = json.loads(call_kwargs['filters'])
    if 'filter_query' in actual_filters_dict:
        actual_filters_dict['filter_query'].sort()
    assert actual_filters_dict == expected_filters
    assert call_kwargs['entity_type'] == "item"
    assert call_kwargs['batch_size'] == 100


@patch('django.core.management.call_command')
def test_run_sync_via_command_parent_filters(mock_call_command, test_command):
    """Test handling of parent_record_ids and parent_field."""
    query_params = {
        'parent_record_ids': [101, 102],
        'parent_field': 'invoice_id'
    }
    options = {'batch_size': 100, 'debug': False, 'fail_on_filter_error': True}

    test_command.run_sync_via_command("invoice_line", options, query_params)

    # These should be passed directly in filters, not in filter_query
    expected_filters = {
        'parent_record_ids': [101, 102],
        'parent_field': 'invoice_id'
    }
    filters_json = json.dumps(expected_filters)

    mock_call_command.assert_called_once()
    call_args, call_kwargs = mock_call_command.call_args
    assert call_kwargs['filters'] == filters_json
    # Ensure filter_query wasn't added for these specific keys
    actual_filters_dict = json.loads(filters_json)
    assert 'filter_query' not in actual_filters_dict


@patch('django.core.management.call_command')
def test_run_sync_via_command_call_command_error(mock_call_command, test_command, capsys):
    """Test run_sync_via_command when call_command raises CommandError."""
    entity_type = "order"
    options = {'batch_size': 100, 'debug': False, 'fail_on_filter_error': True}
    query_params = {}
    error_message = "Simulated CommandError from run_sync"
    mock_call_command.side_effect = CommandError(error_message)

    # Mock the stderr write method directly
    with patch.object(test_command.stderr, 'write') as mock_stderr_write:
        with pytest.raises(CommandError, match=error_message):
            test_command.run_sync_via_command(entity_type, options, query_params)

        # Check that stderr.write was called with the expected message
        mock_stderr_write.assert_called_once()
        # Extract the message passed to write (stripping potential style codes)
        # This assumes the first argument to write is the message string.
        # A more robust check might involve inspecting the style application if needed.
        args, kwargs = mock_stderr_write.call_args
        written_message = args[0] # Assuming message is the first positional arg
        assert f"run_sync command for '{entity_type}' failed: {error_message}" in written_message

@patch('django.core.management.call_command')
@patch('traceback.print_exc') # Mock traceback printing
def test_run_sync_via_command_call_command_exception(mock_print_exc, mock_call_command, test_command, capsys):
    """Test run_sync_via_command when call_command raises a generic Exception."""
    entity_type = "shipment"
    options = {'batch_size': 100, 'debug': True, 'fail_on_filter_error': True} # Debug True
    query_params = {}
    error_message = "Simulated generic Exception"
    mock_call_command.side_effect = Exception(error_message)

    # Mock the stderr write method and the style.ERROR method
    with patch.object(test_command.stderr, 'write') as mock_stderr_write, \
         patch.object(test_command.style, 'ERROR', lambda x: x): # Mock style.ERROR
        result = test_command.run_sync_via_command(entity_type, options, query_params)

        assert result is False # Should return False on generic exception

        # Check that stderr.write was called with the expected message
        mock_stderr_write.assert_called_once()
        args, kwargs = mock_stderr_write.call_args
        written_message = args[0]
        # Now the assertion should pass as styling is mocked
        assert f"Unexpected error during run_sync for '{entity_type}': {error_message}" == written_message

    mock_print_exc.assert_called_once() # Traceback should be printed in debug mode

@patch('django.core.management.call_command')
@patch('traceback.print_exc') # Mock traceback printing
def test_run_sync_via_command_call_command_exception_no_debug(mock_print_exc, mock_call_command, test_command, capsys):
    """Test run_sync_via_command exception path without debug."""
    entity_type = "shipment"
    options = {'batch_size': 100, 'debug': False, 'fail_on_filter_error': True} # Debug False
    query_params = {}
    error_message = "Simulated generic Exception"
    mock_call_command.side_effect = Exception(error_message)

    # Mock the stderr write method and the style.ERROR method
    with patch.object(test_command.stderr, 'write') as mock_stderr_write, \
         patch.object(test_command.style, 'ERROR', lambda x: x): # Mock style.ERROR
        result = test_command.run_sync_via_command(entity_type, options, query_params)

        assert result is False

        # Check that stderr.write was called
        mock_stderr_write.assert_called_once()
        args, kwargs = mock_stderr_write.call_args
        written_message = args[0]
        # Now the assertion should pass as styling is mocked
        assert f"Unexpected error during run_sync for '{entity_type}': {error_message}" == written_message

    mock_print_exc.assert_not_called() # Traceback should NOT be printed

# Test case for when query_params is None and get_mapping is needed (though currently build doesn't use mapping)
@patch('django.core.management.call_command')
@patch.object(TestSyncCommand, 'build_query_params')
@patch.object(TestSyncCommand, 'get_mapping') # Mock get_mapping as well
def test_run_sync_via_command_builds_params_if_none(mock_get_mapping, mock_build_params, mock_call_command, test_command, mock_sync_mapping):
    """Verify build_query_params is called if query_params is None."""
    entity_type = "warehouse"
    options = {'batch_size': 100, 'debug': False, 'fail_on_filter_error': True}
    # Simulate build_query_params returning something simple
    mock_build_params.return_value = {'location': 'main'}
    # Simulate get_mapping returning a mock (even if build_params doesn't use it now)
    mock_get_mapping.return_value = mock_sync_mapping

    test_command.run_sync_via_command(entity_type, options, query_params=None)

    # Assert get_mapping was called because query_params was None
    # This check is currently commented out because build_query_params
    # was refactored to not *require* mapping for default timestamp.
    # If build_query_params changes to require mapping again, uncomment this.
    # mock_get_mapping.assert_called_once_with(entity_type)

    # Assert build_query_params was called
    mock_build_params.assert_called_once_with(options) # Mapping argument removed from call

    # Assert call_command was called with correctly built filters
    expected_filters = {'filter_query': [['location', '=', 'main']]}
    expected_filters_json = json.dumps(expected_filters)
    expected_call_options = {
        'entity_type': entity_type,
        'batch_size': 100,
        'filters': expected_filters_json,
        'debug': False,
        'fail_on_filter_error': True,
        'full': False,
        'clear_cache': False,
    }
    mock_call_command.assert_called_once_with("run_sync", **expected_call_options)

# Test case for empty filter_query list
@patch('django.core.management.call_command')
@patch.object(TestSyncCommand, 'build_query_params')
def test_run_sync_via_command_no_filters(mock_build_params, mock_call_command, test_command):
    """Test run_sync_via_command when no filters are generated."""
    entity_type = "category"
    options = {'batch_size': 100, 'debug': False, 'fail_on_filter_error': True}
    # Simulate build_query_params returning an empty dict
    mock_build_params.return_value = {}

    test_command.run_sync_via_command(entity_type, options, query_params=None)

    mock_build_params.assert_called_once_with(options)
    # call_command should be called with filters=None omitted
    expected_call_options = {
        'entity_type': entity_type,
        'batch_size': 100,
        # 'filters': None, # Expect key to be omitted
        'debug': False,
        'fail_on_filter_error': True,
        'full': False,
        'clear_cache': False
    }
    mock_call_command.assert_called_once_with("run_sync", **expected_call_options) 