"""
Tests for YAML utility functions in the sync tasks module.

This module tests the helper functions for loading and processing YAML
configuration files in the tasks.py module.
"""

import os
import pytest
from unittest import mock
import yaml

from pyerp.sync.tasks import (
    _load_sales_record_yaml,
    get_sales_record_mappings,
    create_sales_record_mappings,
)


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.yaml.safe_load")
@mock.patch("pyerp.sync.tasks.open", new_callable=mock.mock_open, read_data="data")
def test_load_sales_record_yaml(mock_file, mock_yaml_load):
    """Test loading sales record YAML configuration."""
    # Setup
    mock_yaml_load.return_value = {"mappings": []}
    
    # Execute
    result = _load_sales_record_yaml()
    
    # Verify
    assert mock_file.call_count == 1
    assert "sales_record_sync.yaml" in mock_file.call_args[0][0]
    mock_yaml_load.assert_called_once_with(mock_file.return_value)
    assert result == {"mappings": []}


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks.yaml.safe_load")
@mock.patch("pyerp.sync.tasks.open", mock.mock_open())
def test_load_sales_record_yaml_exception(mock_yaml_load):
    """Test loading sales record YAML configuration with exception."""
    # Setup
    mock_yaml_load.side_effect = Exception("YAML error")
    
    # Execute
    result = _load_sales_record_yaml()
    
    # Verify
    assert result == {}


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks._load_sales_record_yaml")
def test_get_sales_record_mappings(mock_load_yaml):
    """Test getting sales record mappings."""
    # Setup
    mock_load_yaml.return_value = {
        "mappings": [
            {"entity_type": "sales_record", "id": 1},
            {"entity_type": "sales_record_item", "id": 2},
            {"entity_type": "other", "id": 3},
        ]
    }
    
    # Execute
    sr_mapping, sr_item_mapping = get_sales_record_mappings()
    
    # Verify
    assert sr_mapping["id"] == 1
    assert sr_item_mapping["id"] == 2
    mock_load_yaml.assert_called_once()


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks._load_sales_record_yaml")
def test_get_sales_record_mappings_missing(mock_load_yaml):
    """Test getting sales record mappings when mappings are missing."""
    # Setup - missing item mapping
    mock_load_yaml.return_value = {
        "mappings": [
            {"entity_type": "sales_record", "id": 1},
            {"entity_type": "other", "id": 3},
        ]
    }
    
    # Execute
    sr_mapping, sr_item_mapping = get_sales_record_mappings()
    
    # Verify
    assert sr_mapping["id"] == 1
    assert sr_item_mapping is None
    
    # Setup - empty mappings
    mock_load_yaml.return_value = {"mappings": []}
    
    # Execute
    sr_mapping, sr_item_mapping = get_sales_record_mappings()
    
    # Verify
    assert sr_mapping is None
    assert sr_item_mapping is None


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks._load_sales_record_yaml")
def test_create_sales_record_mappings(mock_load_yaml):
    """Test creating sales record mappings."""
    # Setup
    mock_load_yaml.return_value = {
        "mappings": [
            {"entity_type": "sales_record", "id": 1},
            {"entity_type": "sales_record_item", "id": 2},
        ]
    }
    
    # Execute
    sr_mapping, sr_item_mapping = create_sales_record_mappings()
    
    # Verify
    assert sr_mapping["id"] == 1
    assert sr_item_mapping["id"] == 2
    mock_load_yaml.assert_called_once()


@pytest.mark.unit
@mock.patch("pyerp.sync.tasks._load_sales_record_yaml")
def test_create_sales_record_mappings_not_found(mock_load_yaml):
    """Test creating sales record mappings when mappings are not found."""
    # Setup - empty configuration
    mock_load_yaml.return_value = {"mappings": []}
    
    # Execute
    sr_mapping, sr_item_mapping = create_sales_record_mappings()
    
    # Verify
    assert sr_mapping is None
    assert sr_item_mapping is None 