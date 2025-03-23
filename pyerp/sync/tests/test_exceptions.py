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


























@pytest.mark.unit
def test_sync_error_base_class():
    """Test that SyncError is a base exception class."""
    assert issubclass(SyncError, Exception)
    
    # Test that it can be instantiated with a message
    error_msg = "General sync error"
    error = SyncError(error_msg)
    assert str(error) == error_msg






@pytest.mark.unit
def test_extract_error():
    """Test that ExtractError is a subclass of SyncError."""
    assert issubclass(ExtractError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Error during data extraction"
    error = ExtractError(error_msg)
    assert str(error) == error_msg






@pytest.mark.unit
def test_transform_error():
    """Test that TransformError is a subclass of SyncError."""
    assert issubclass(TransformError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Error during data transformation"
    error = TransformError(error_msg)
    assert str(error) == error_msg






@pytest.mark.unit
def test_load_error():
    """Test that LoadError is a subclass of SyncError."""
    assert issubclass(LoadError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Error during data loading"
    error = LoadError(error_msg)
    assert str(error) == error_msg






@pytest.mark.unit
def test_validation_error():
    """Test that ValidationError is a subclass of SyncError."""
    assert issubclass(ValidationError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Data validation failed"
    error = ValidationError(error_msg)
    assert str(error) == error_msg






@pytest.mark.unit
def test_configuration_error():
    """Test that ConfigurationError is a subclass of SyncError."""
    assert issubclass(ConfigurationError, SyncError)
    
    # Test that it can be instantiated with a message
    error_msg = "Invalid configuration"
    error = ConfigurationError(error_msg)
    assert str(error) == error_msg






@pytest.mark.unit
def test_raising_sync_errors():
    """Test that all SyncError subclasses can be caught as SyncError."""
    # Create a list of error classes and their messages
    error_classes = [
        (ExtractError, "Extract error"),
        (TransformError, "Transform error"),
        (LoadError, "Load error"),
        (ValidationError, "Validation error"),
        (ConfigurationError, "Configuration error"),
    ]
    
    # Test that each error type can be caught as a SyncError
    for error_class, error_msg in error_classes:
        try:
            raise error_class(error_msg)
        except SyncError as e:
            assert str(e) == error_msg
        except Exception:
            assert False, f"{error_class.__name__} was not caught as SyncError" 