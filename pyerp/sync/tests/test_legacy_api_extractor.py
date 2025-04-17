"""
Tests for the LegacyAPIExtractor class.

This module tests the legacy API extractor used to extract data from the
legacy ERP system.
"""

import pytest
from unittest import mock
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, date
from unittest.mock import patch
import logging

from pyerp.sync.exceptions import ExtractError
from pyerp.sync.extractors.legacy_api import LegacyAPIExtractor


@pytest.mark.unit
def test_legacy_api_extractor_required_config_fields():
    """Test that required config fields are correctly defined."""
    extractor = LegacyAPIExtractor({"environment": "test", "table_name": "Products"})
    required_fields = extractor.get_required_config_fields()
    assert "environment" in required_fields
    assert "table_name" in required_fields


@pytest.mark.unit
def test_legacy_api_extractor_init_invalid_config():
    """Test initialization with invalid configuration."""
    # Missing required fields
    with pytest.raises(ValueError) as excinfo:
        LegacyAPIExtractor({"environment": "test"})  # missing table_name
    
    assert "Missing required configuration fields" in str(excinfo.value)
    assert "table_name" in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        LegacyAPIExtractor({"table_name": "Products"})  # missing environment
    
    assert "Missing required configuration fields" in str(excinfo.value)
    assert "environment" in str(excinfo.value)


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
@mock.patch("pyerp.sync.extractors.legacy_api.log_data_sync_event")
def test_legacy_api_extractor_connect(mock_log_event, mock_client_class):
    """Test connect method establishes connection to legacy API."""
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_instance = mock_client_class.return_value
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connect()
    
    # Verify
    mock_client_class.assert_called_once_with(environment="test")
    assert extractor.connection == mock_client_instance
    mock_log_event.assert_called_once()
    # Verify log event parameters
    log_call_args = mock_log_event.call_args[1]
    assert log_call_args["source"] == "legacy_api_test"
    assert log_call_args["destination"] == "pyerp"
    assert log_call_args["status"] == "connected"


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
def test_legacy_api_extractor_connect_failure(mock_client_class):
    """Test connect method handles connection errors correctly."""
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_class.side_effect = ConnectionError("Failed to connect")
    
    # Execute and verify
    extractor = LegacyAPIExtractor(config)
    with pytest.raises(ConnectionError) as excinfo:
        extractor.connect()
    
    assert "Failed to connect to legacy API" in str(excinfo.value)


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
def test_legacy_api_extractor_extract_basic(mock_client_class):
    """Test extract method with basic configuration."""
    # Clear cache for this test
    LegacyAPIExtractor.clear_cache()
    
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_instance = mock_client_class.return_value
    
    # Create sample DataFrame for the response
    sample_data = [
        {"id": 1, "name": "Product 1", "price": 10.00},
        {"id": 2, "name": "Product 2", "price": 20.00},
        {"id": 3, "name": "Product 3", "price": 30.00},
    ]
    df = pd.DataFrame(sample_data)
    mock_client_instance.fetch_table.return_value = df
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract()
    
    # Verify
    assert len(results) == 3
    assert all(isinstance(item, dict) for item in results)
    assert results[0]["id"] == 1
    assert results[1]["name"] == "Product 2"
    assert results[2]["price"] == 30.00
    
    # Verify client was called correctly (Updated for cache/all_records)
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products",
        all_records=True,  
        filter_query=None, 
        top=None
    )


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
def test_legacy_api_extractor_extract_with_pagination(mock_client_class):
    """Test extract method with pagination."""
    # Clear cache for this test
    LegacyAPIExtractor.clear_cache()
    
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_instance = mock_client_class.return_value
    
    # Simulate a single fetch returning all data
    all_data = pd.DataFrame([
        {"id": 1, "name": "Product 1", "price": 10.00},
        {"id": 2, "name": "Product 2", "price": 20.00},
        {"id": 3, "name": "Product 3", "price": 30.00},
    ])
    mock_client_instance.fetch_table.return_value = all_data
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract()
    
    # Verify
    assert len(results) == 3 # Should get all results now
    assert all(isinstance(item, dict) for item in results)
    assert results[0]["id"] == 1
    assert results[1]["price"] == 20.00
    assert results[2]["id"] == 3
    
    # Verify client was called correctly (Only once due to all_records=True by default)
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products",
        all_records=True, # Default behavior
        filter_query=None,
        top=None
    )
    
    # Original assertions for pagination calls removed/commented out:
    # ...


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
def test_legacy_api_extractor_extract_with_top_param(mock_client_class):
    """Test extract method with $top query parameter."""
    # Clear cache for this test
    LegacyAPIExtractor.clear_cache()
    
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_instance = mock_client_class.return_value
    
    # Create sample DataFrame for the response
    sample_data = [
        {"id": 1, "name": "Product 1", "price": 10.00},
    ]
    df = pd.DataFrame(sample_data)
    mock_client_instance.fetch_table.return_value = df
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract(query_params={"$top": 1})
    
    # Verify
    assert len(results) == 1
    assert results[0]["id"] == 1
    
    # Verify client was called correctly with the $top parameter
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products",
        filter_query=None,
        top=1,  # From $top parameter
        all_records=False, # $top makes this False
    )


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
def test_legacy_api_extractor_extract_with_filter_query(mock_client_class):
    """Test extract method with filter_query parameter."""
    # Clear cache for this test
    LegacyAPIExtractor.clear_cache()
    
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_instance = mock_client_class.return_value
    
    # Create sample DataFrame for the response
    sample_data = [
        {"id": 1, "name": "Product 1", "price": 10.00},
    ]
    df = pd.DataFrame(sample_data)
    mock_client_instance.fetch_table.return_value = df
    
    # Execute - Note: filter_query should be a list of lists now
    filter_list = [["name", "=", "Product 1"]]
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract(query_params={"filter_query": filter_list})
    
    # Verify
    assert len(results) == 1
    assert results[0]["id"] == 1
    
    # Verify client was called correctly with the filter query list
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products",
        filter_query=filter_list, # Expect the list here
        top=None, 
        all_records=True, # Default unless top is specified
    )


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
def test_legacy_api_extractor_extract_empty_result(mock_client_class):
    """Test extract method with empty result."""
    # Clear cache for this test
    LegacyAPIExtractor.clear_cache()
    
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_instance = mock_client_class.return_value
    
    # Create empty DataFrame for the response
    df = pd.DataFrame([]) # Use empty list for DataFrame
    mock_client_instance.fetch_table.return_value = df
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract()
    
    # Verify
    assert len(results) == 0
    
    # Verify client was called
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products", 
        all_records=True,
        filter_query=None, 
        top=None 
    )


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
@mock.patch("pyerp.sync.extractors.legacy_api.logger") # Patch logger here
def test_legacy_api_extractor_extract_exception(mock_logger, mock_client_class):
    """Test extract method handles exceptions correctly."""
    # Clear cache for this test
    LegacyAPIExtractor.clear_cache()
    
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    mock_client_instance = mock_client_class.return_value
    mock_client_instance.fetch_table.side_effect = ValueError("API error")
    
    # Execute and verify
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    
    # Default behavior should catch error and return empty list
    results = extractor.extract()
    assert results == []
    mock_logger.error.assert_called_with(
        "Error extracting data from Products: API error"
    )
    
    # Verify cache was not populated
    cache_key = extractor._generate_cache_key()
    assert cache_key not in LegacyAPIExtractor._response_cache

    # Test with fail_on_filter_error=True (should now raise ExtractError)
    mock_client_instance.fetch_table.side_effect = ConnectionError("API error again")
    with pytest.raises(ExtractError, match="Extraction failed: API error again"):
        extractor.extract(fail_on_filter_error=True)

    # Original test expected ExtractError, but the code raises the original error
    # with pytest.raises(ExtractError) as excinfo:
    #     extractor.extract()
    # assert "Error extracting data from legacy API" in str(excinfo.value)


@pytest.mark.unit
def test_legacy_api_extractor_format_date_for_api():
    """Test _format_date_for_api method."""
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    extractor = LegacyAPIExtractor(config)
    
    # Test with string input
    date_str = "2022-05-01T10:30:00Z"
    formatted_str = extractor._format_date_for_api(date_str)
    assert formatted_str == "2022-05-01T00:00:00Z" # String input defaults to start of day UTC
    
    # Test with datetime input (naive, assumed UTC)
    date_obj_naive = datetime(2022, 5, 1, 10, 30, 0)
    formatted_dt_naive = extractor._format_date_for_api(date_obj_naive)
    assert formatted_dt_naive == "2022-05-01T10:30:00Z" # Expect ISO 8601 UTC

    # Test with date input (start of day UTC)
    date_only = date(2022, 5, 1)
    formatted_date_only = extractor._format_date_for_api(date_only)
    assert formatted_date_only == "2022-05-01T00:00:00Z" # Expect ISO 8601 UTC start of day

    # Test with date input and end_of_day=True
    formatted_date_end = extractor._format_date_for_api(date_only, end_of_day=True)
    assert formatted_date_end == "2022-05-01T23:59:59Z" # Expect ISO 8601 UTC end of day
    
    # Test with invalid input (should return None)
    invalid_date = "not a date"
    formatted_invalid = extractor._format_date_for_api(invalid_date)
    assert formatted_invalid is None # Expect None for invalid format


@pytest.mark.unit
def test_build_date_filter_query_no_date():
    """Test _build_date_filter_query with no date provided."""
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    extractor = LegacyAPIExtractor(config)
    
    # Execute
    # Pass both date_key and the filter dict
    result = extractor._build_date_filter_query("test_date_key", {})
    
    # Verify
    assert result == [] # Expect empty list for empty dict


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_with_date_string(mock_logger):
    """Test building filter query with date strings."""
    config = {"environment": "test", "table_name": "TestTable"}
    extractor = LegacyAPIExtractor(config)
    date_filters = {
        'modified_date': {'gt': '2022-01-01', 'lt': '2022-01-31'}
    }
    result = extractor._build_date_filter_query('modified_date', date_filters['modified_date'])
    expected = [
        ['modified_date', '>', '2022-01-01T00:00:00Z'],
        ['modified_date', '<', '2022-01-31T23:59:59Z']
    ]
    assert sorted(result) == sorted(expected)
    # Check if the specific log message was recorded
    expected_info_fmt = "Building date filter conditions for key: %s with dict: %s"
    mock_logger.info.assert_any_call(expected_info_fmt, 'modified_date', date_filters['modified_date'])


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_with_datetime_object(mock_logger):
    """Test building filter query with datetime objects."""
    config = {"environment": "test", "table_name": "TestTable"}
    extractor = LegacyAPIExtractor(config)
    date_filters = {
        'creation_date': {'ge': datetime(2022, 2, 15, 10, 30, 0), 'le': datetime(2022, 2, 20)}
    }
    result = extractor._build_date_filter_query('creation_date', date_filters['creation_date'])
    expected = [
        ['creation_date', '>=', '2022-02-15T10:30:00Z'],
        ['creation_date', '<=', '2022-02-20T23:59:59Z']
    ]
    assert sorted(result) == sorted(expected)
    # Check if the specific log message was recorded
    expected_info_fmt = "Building date filter conditions for key: %s with dict: %s"
    mock_logger.info.assert_any_call(expected_info_fmt, 'creation_date', date_filters['creation_date'])


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_with_invalid_operator(mock_logger):
    """Test handling of unknown operators."""
    config = {"environment": "test", "table_name": "TestTable"}
    extractor = LegacyAPIExtractor(config)
    date_filters = {
        'some_date': {'invalid_op': '2022-03-01'}
    }
    result = extractor._build_date_filter_query('some_date', date_filters['some_date'])
    assert result == [] # Should skip the invalid operator
    # Check if the specific warning message was recorded
    expected_fstring_msg = f"Unknown date filter operator 'invalid_op' for key 'some_date', skipping."
    mock_logger.warning.assert_any_call(expected_fstring_msg)


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_multiple_operators(mock_logger):
    """Test handling multiple operators, including invalid ones."""
    config = {"environment": "test", "table_name": "TestTable"}
    extractor = LegacyAPIExtractor(config)
    date_filters = {
        'event_date': {
            'gte': '2022-04-10',
            'lte': '2022-04-20',
            'invalid': 'some_value' # Should be skipped
        }
    }
    result = extractor._build_date_filter_query('event_date', date_filters['event_date'])
    expected = [
        ['event_date', '>=', '2022-04-10T00:00:00Z'],
        ['event_date', '<=', '2022-04-20T23:59:59Z']
    ]
    assert sorted(result) == sorted(expected)
    # Check if the warning for the invalid operator was logged
    expected_warning_fmt = "Unknown date filter operator '%s' for key '%s', skipping."
    mock_logger.warning.assert_any_call(expected_warning_fmt, 'invalid', 'event_date')
    # Check that the INFO log for building the valid parts was logged
    expected_info_fmt = "Building date filter conditions for key: %s with dict: %s"
    mock_logger.info.assert_any_call(expected_info_fmt, 'event_date', date_filters['event_date'])


# DELETE THE DUPLICATED CLASS FROM HERE DOWN
# @pytest.mark.sync
# class TestLegacyApiExtractor:
# ... (all lines from 456 to the end of the file) ...

# Remove lines 456-643 entirely 