"""
Tests for the sync exceptions module.

This module tests the exception classes in the sync module.
"""

import pytest
from pyerp.sync.exceptions import (
    SyncError,
    ExtractError, 
    TransformError,
    LoadError,
    ValidationError,
    ConfigurationError
)


def test_sync_error_base_class():
    """Test that SyncError is a base exception class."""
    assert issubclass(SyncError, Exception)
    
    # Test that it can be instantiated with a message
    error_msg = "General sync error"
    error = SyncError(error_msg)
    assert str(error) == error_msg


def test_extract_error():
    """Test the ExtractError exception."""
    assert issubclass(ExtractError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Failed to extract data"
    error = ExtractError(error_msg)
    assert str(error) == error_msg


def test_transform_error():
    """Test the TransformError exception."""
    assert issubclass(TransformError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Failed to transform data"
    error = TransformError(error_msg)
    assert str(error) == error_msg


def test_load_error():
    """Test the LoadError exception."""
    assert issubclass(LoadError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Failed to load data"
    error = LoadError(error_msg)
    assert str(error) == error_msg


def test_validation_error():
    """Test the ValidationError exception."""
    assert issubclass(ValidationError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Data validation failed"
    error = ValidationError(error_msg)
    assert str(error) == error_msg


def test_configuration_error():
    """Test the ConfigurationError exception."""
    assert issubclass(ConfigurationError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Invalid configuration"
    error = ConfigurationError(error_msg)
    assert str(error) == error_msg


def test_raising_sync_errors():
    """Test that sync errors can be raised and caught appropriately."""
    # Test raising and catching a specific sync error
    with pytest.raises(ExtractError) as exc_info:
        raise ExtractError("Could not connect to source")
    assert "Could not connect to source" in str(exc_info.value)
    
    # Test that we can catch a specific error type with SyncError
    try:
        raise LoadError("Database connection failed")
    except SyncError as e:
        assert "Database connection failed" in str(e) 