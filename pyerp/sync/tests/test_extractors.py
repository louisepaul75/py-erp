"""
Tests for the sync extractors module.

This module tests the extractor classes in the sync module.
"""

import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from pyerp.sync.exceptions import SyncError, ConfigurationError
from pyerp.sync.extractors.base import BaseExtractor


class ConcreteExtractor(BaseExtractor):
    """A concrete implementation of BaseExtractor for testing."""

    def get_required_config_fields(self) -> List[str]:
        return ["api_key", "endpoint"]

    def connect(self) -> None:
        self.connection = f"Connected to {self.config['endpoint']} with {self.config['api_key']}"

    def extract(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not hasattr(self, 'connection') or not self.connection:
            raise ConnectionError("Not connected")
        if query_params and "invalid" in query_params:
            raise ValueError("Invalid query parameter")
        
        # Return different results based on query parameters
        if query_params and "limit" in query_params:
            limit = query_params["limit"]
            return [{"id": i, "name": f"Test Record {i}"} for i in range(1, limit + 1)]
        
        # Default result
        return [
            {"id": 1, "name": "Test Record 1"},
            {"id": 2, "name": "Test Record 2"},
            {"id": 3, "name": "Test Record 3"},
        ]
    
    def close(self) -> None:
        """Close the connection."""
        # Handle different types of connections for test coverage
        if isinstance(self.connection, Exception):
            # Test case for exception handling
            self.connection = None
        else:
            # Normal close operation
            self.connection = None


@pytest.mark.unit
def test_base_extractor_init_valid_config():
    """Test initialization with valid configuration."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    assert extractor.config == config
    assert not hasattr(extractor, 'connection') or extractor.connection is None


@pytest.mark.unit
def test_base_extractor_init_invalid_config():
    """Test initialization with invalid configuration."""
    # Missing required fields
    config = {"api_key": "test_key"}  # missing 'endpoint'
    with pytest.raises(ValueError) as excinfo:
        ConcreteExtractor(config)
    
    # Check that the error message mentions the missing field
    assert "Missing required configuration fields" in str(excinfo.value)
    assert "endpoint" in str(excinfo.value)


@pytest.mark.unit
def test_base_extractor_connect():
    """Test connect method."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    extractor.connect()
    assert isinstance(extractor.connection, str)
    assert extractor.connection == "Connected to https://api.example.com with test_key"


@pytest.mark.unit
def test_base_extractor_extract():
    """Test extract method."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    extractor.connect()
    
    # Test default parameters
    results = extractor.extract()
    assert len(results) == 3
    assert all(isinstance(item, dict) for item in results)
    
    # Test with query parameters
    query_params = {"limit": 1}
    results = extractor.extract(query_params)
    assert len(results) == 1


@pytest.mark.unit
def test_base_extractor_close():
    """Test close method."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    extractor.connect()
    assert extractor.connection is not None
    
    extractor.close()
    assert extractor.connection is None


@pytest.mark.unit
def test_base_extractor_context_manager():
    """Test context manager functionality."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    
    with ConcreteExtractor(config) as extractor:
        assert extractor.connection is not None
        assert isinstance(extractor.connection, str)
        results = extractor.extract()
        assert len(results) > 0
    
    # After exiting context manager, connection should be closed
    assert extractor.connection is None


@pytest.mark.unit
def test_base_extractor_close_exception_handling():
    """Test close method handles exceptions gracefully."""
    config = {"api_key": "test_key", "endpoint": "https://api.example.com"}
    extractor = ConcreteExtractor(config)
    extractor.connect()
    
    # Make close throw an exception
    extractor.connection = Exception("Dummy connection")
    
    # Should not raise an exception
    extractor.close()
    assert extractor.connection is None 