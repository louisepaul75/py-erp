"""
Tests for validation exception classes in pyerp.core.validators.
"""

import pytest

from pyerp.core.validators import ImportValidationError, SkipRowException


class TestImportValidationError:
    """Tests for ImportValidationError class."""

    def test_init_with_single_error(self):
        """Test initialization with a single error."""
        errors = {"field1": ["Error message"]}
        error = ImportValidationError(errors)
        
        assert error.errors == errors
        assert "field1: Error message" in str(error)

    def test_init_with_multiple_errors(self):
        """Test initialization with multiple errors."""
        errors = {
            "field1": ["Error message 1", "Error message 2"],
            "field2": ["Error message 3"]
        }
        error = ImportValidationError(errors)
        
        assert error.errors == errors
        assert "field1: Error message 1, Error message 2" in str(error)
        assert "field2: Error message 3" in str(error)
        assert ";" in str(error)  # Makes sure errors are separated by semicolons

    def test_format_errors(self):
        """Test the _format_errors method."""
        errors = {"field1": ["Error 1"], "field2": ["Error 2"]}
        error = ImportValidationError(errors)
        
        formatted = error._format_errors()
        assert "field1: Error 1" in formatted
        assert "field2: Error 2" in formatted
        assert ";" in formatted


class TestSkipRowException:
    """Tests for SkipRowException class."""

    def test_init_with_reason(self):
        """Test initialization with a reason."""
        exception = SkipRowException("Test reason")
        
        assert exception.reason == "Test reason"
        assert "Row skipped: Test reason" in str(exception)

    def test_init_without_reason(self):
        """Test initialization without a reason."""
        exception = SkipRowException()
        
        assert exception.reason == ""
        assert "Row skipped" in str(exception)
        assert "Row skipped:" not in str(exception)  # No colon when no reason 