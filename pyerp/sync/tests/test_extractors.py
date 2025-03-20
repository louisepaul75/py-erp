"""
Tests for the sync extractors module.

This module tests the extractor classes in the sync module.
"""

import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from pyerp.sync.exceptions import SyncError
from pyerp.sync.extractors.base import BaseExtractor


class ConcreteExtractor(BaseExtractor):
    """A concrete implementation of BaseExtractor for testing."""

    def get_required_config_fields(self) -> List[str]:
        return ["api_key", "endpoint"]

    def connect(self) -> None:
        self.connection = mock.MagicMock()

    def extract(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.connection:
            raise ConnectionError("Not connected")
        if query_params and "invalid" in query_params:
            raise ValueError("Invalid query parameter")
        return [{"id": 1, "name": "Test Record"}]


def test_base_extractor_init_valid_config():
    """Test initialization with valid configuration."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    assert extractor.config == config
    assert extractor.connection is None


def test_base_extractor_init_invalid_config():
    """Test initialization with invalid configuration."""
    # Missing required fields
    config = {"api_key": "test_key"}  # missing 'endpoint'
    with pytest.raises(ValueError) as excinfo:
        ConcreteExtractor(config)
    assert "Missing required configuration fields" in str(excinfo.value)
    assert "endpoint" in str(excinfo.value)


def test_base_extractor_connect():
    """Test connecting to the data source."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    assert extractor.connection is None
    
    extractor.connect()
    assert extractor.connection is not None


def test_base_extractor_extract():
    """Test data extraction."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    
    # Should raise an error if not connected
    with pytest.raises(ConnectionError):
        extractor.extract()
    
    # Connect and then extract
    extractor.connect()
    data = extractor.extract()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
    
    # Test with invalid query parameters
    with pytest.raises(ValueError):
        extractor.extract({"invalid": True})


def test_base_extractor_close():
    """Test closing the connection."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    
    # Connect first
    extractor.connect()
    assert extractor.connection is not None
    
    # Close the connection
    extractor.close()
    assert extractor.connection is None
    
    # Test close when there's no connection
    extractor.close()  # Should not raise an error


def test_base_extractor_context_manager():
    """Test using the extractor as a context manager."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    
    # Test normal operation
    with ConcreteExtractor(config) as extractor:
        assert extractor.connection is not None
        data = extractor.extract()
        assert len(data) > 0
    
    # Connection should be closed after exiting the context
    assert extractor.connection is None
    
    # Test with an exception inside the context
    try:
        with ConcreteExtractor(config) as extractor:
            assert extractor.connection is not None
            raise RuntimeError("Test exception")
    except RuntimeError:
        pass
    
    # Connection should still be closed after an exception
    assert extractor.connection is None


def test_base_extractor_close_exception_handling():
    """Test handling of exceptions during close."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    
    # Mock a connection that raises an exception when closed
    extractor.connect()
    extractor.connection.close.side_effect = Exception("Connection close error")
    
    # Close should swallow the exception
    with mock.patch("pyerp.sync.extractors.base.logger") as mock_logger:
        extractor.close()
        mock_logger.warning.assert_called_once()
        assert "Connection close error" in mock_logger.warning.call_args[0][0]
    
    # Connection should still be set to None
    assert extractor.connection is None 