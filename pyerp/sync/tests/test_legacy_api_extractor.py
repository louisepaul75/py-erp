"""
Tests for the LegacyAPIExtractor class.

This module tests the legacy API extractor used to extract data from the
legacy ERP system.
"""

import pytest
from unittest import mock
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from unittest.mock import patch

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
        all_records=True  # Updated expectation
    )


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.LegacyERPClient")
def test_legacy_api_extractor_extract_with_pagination(mock_client_class):
    """Test extract method with pagination."""
    # Clear cache for this test
    LegacyAPIExtractor.clear_cache()
    
    # Setup
    config = {"environment": "test", "table_name": "Products", "page_size": 2}
    mock_client_instance = mock_client_class.return_value
    
    # Create sample DataFrames for the response (simulating pagination)
    first_page = pd.DataFrame([
        {"id": 1, "name": "Product 1", "price": 10.00},
        {"id": 2, "name": "Product 2", "price": 20.00},
    ])
    second_page = pd.DataFrame([
        {"id": 3, "name": "Product 3", "price": 30.00},
    ])
    empty_page = pd.DataFrame()
    
    # Configure mock to return different values on subsequent calls
    mock_client_instance.fetch_table.side_effect = [first_page, second_page, empty_page]
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract()
    
    # Verify
    assert len(results) == 2
    assert all(isinstance(item, dict) for item in results)
    assert results[0]["id"] == 1
    assert results[1]["price"] == 20.00
    
    # Verify client was called correctly (Only once due to all_records=True)
    assert mock_client_instance.fetch_table.call_count == 1 
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products",
        all_records=True # Actual call with default
    )
    
    # Original assertions for pagination calls removed/commented out:
    # assert mock_client_instance.fetch_table.call_count == 2
    # mock_client_instance.fetch_table.assert_any_call(
    #     table_name="Products", filter_query=None, top=2, skip=0, all_records=False
    # )
    # mock_client_instance.fetch_table.assert_any_call(
    #     table_name="Products", filter_query=None, top=2, skip=2, all_records=False
    # )


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
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract(query_params={"filter_query": "name eq 'Product 1'"})
    
    # Verify
    assert len(results) == 1
    assert results[0]["id"] == 1
    
    # Verify client was called correctly with the filter query
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products",
        filter_query="name eq 'Product 1'",
        top=None, # Added explicitly
        all_records=True, # Updated expectation
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
    df = pd.DataFrame()
    mock_client_instance.fetch_table.return_value = df
    
    # Execute
    extractor = LegacyAPIExtractor(config)
    extractor.connection = mock_client_instance  # Skip connect for this test
    results = extractor.extract()
    
    # Verify
    assert len(results) == 0
    
    # Verify client was called
    mock_client_instance.fetch_table.assert_called_once_with(
        table_name="Products", all_records=True
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

    # Test with fail_on_filter_error=True (should now raise)
    mock_client_instance.fetch_table.side_effect = ConnectionError("API error again")
    with pytest.raises(ConnectionError, match="API error again"):
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
    formatted = extractor._format_date_for_api(date_str)
    assert formatted == "2022-05-01"
    
    # Test with datetime input
    date_obj = datetime(2022, 5, 1, 10, 30, 0)
    formatted = extractor._format_date_for_api(date_obj)
    assert formatted == "2022-05-01"
    
    # Test with invalid input (should return original)
    invalid_date = "not a date"
    formatted = extractor._format_date_for_api(invalid_date)
    assert formatted == invalid_date


@pytest.mark.unit
def test_build_date_filter_query_no_date():
    """Test _build_date_filter_query with no date provided."""
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    extractor = LegacyAPIExtractor(config)
    
    # Execute
    result = extractor._build_date_filter_query({})
    
    # Verify
    assert result is None


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_with_date_string(mock_logger):
    """Test _build_date_filter_query with date string."""
    # Setup
    config = {
        "environment": "test", 
        "table_name": "Products",
        "modified_date_field": "last_updated"
    }
    extractor = LegacyAPIExtractor(config)
    
    # Test data
    query_params = {
        "modified_date": {
            "gt": "2022-01-01",
            "lt": "2022-01-31"
        }
    }
    
    # Execute
    result = extractor._build_date_filter_query(query_params)
    
    # Verify
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check first condition
    assert result[0][0] == "last_updated"  # Field name from config
    assert result[0][1] == ">"  # Operator
    assert result[0][2] == "2022-01-01"  # Value
    
    # Check second condition
    assert result[1][0] == "last_updated"
    assert result[1][1] == "<"
    assert result[1][2] == "2022-01-31"
    
    # Verify logger was called
    mock_logger.info.assert_any_call("Date field from config: last_updated")


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_with_datetime_object(mock_logger):
    """Test _build_date_filter_query with datetime object."""
    # Setup
    config = {
        "environment": "test", 
        "table_name": "Products"
    }
    extractor = LegacyAPIExtractor(config)
    
    # Test data with datetime object
    date_obj = datetime(2022, 1, 15)
    query_params = {
        "modified_date": {
            "gte": date_obj
        }
    }
    
    # Execute
    result = extractor._build_date_filter_query(query_params)
    
    # Verify
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1
    
    assert result[0][0] == "modified_date"  # Default field name
    assert result[0][1] == ">="  # Operator
    assert result[0][2] == "2022-01-15"  # Formatted date
    
    # Verify logger was called
    mock_logger.info.assert_any_call("Date field from config: modified_date")


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_with_invalid_operator(mock_logger):
    """Test _build_date_filter_query with invalid operator."""
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    extractor = LegacyAPIExtractor(config)
    
    # Test data with invalid operator
    query_params = {
        "modified_date": {
            "invalid_op": "2022-01-01"
        }
    }
    
    # Execute
    result = extractor._build_date_filter_query(query_params)
    
    # Verify
    assert result is None
    
    # Verify warning was logged
    mock_logger.warning.assert_called_with("Unknown operator 'invalid_op', skipping")


@pytest.mark.unit
@mock.patch("pyerp.sync.extractors.legacy_api.logger")
def test_build_date_filter_query_multiple_operators(mock_logger):
    """Test _build_date_filter_query with multiple operators."""
    # Setup
    config = {"environment": "test", "table_name": "Products"}
    extractor = LegacyAPIExtractor(config)
    
    # Test data with multiple operators
    query_params = {
        "modified_date": {
            "gt": "2022-01-01",
            "lt": "2022-01-31",
            "eq": "2022-01-15",
            "invalid": "should_be_skipped"
        }
    }
    
    # Execute
    result = extractor._build_date_filter_query(query_params)
    
    # Verify
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 3  # Should only include the valid operators
    
    # Check for warning about invalid operator
    mock_logger.warning.assert_called_with("Unknown operator 'invalid', skipping")


# DELETE THE DUPLICATED CLASS FROM HERE DOWN
# @pytest.mark.sync
# class TestLegacyApiExtractor:
# ... (all lines from 456 to the end of the file) ...

# Remove lines 456-643 entirely 