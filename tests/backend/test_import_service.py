"""
Tests for the import service module.

This module contains tests for the product import service functionality.
"""

from unittest.mock import patch

import pytest

from tests.backend.test_commands import MockImportCommand
from tests.unit.mock_models import MockProductCategory


class TestValidator:
    """Base validator class for testing."""

    def __init__(self, options=None):
        """Initialize validator with options."""
        self.options = options or {}
        self.errors = []
        self.warnings = []

    def validate(self, data):
        """Validate data."""
        return True


class TestProductImportCommand:
    """Test cases for product import command."""

    def test_handle_product_validation(self):
        """Test handling product validation."""
        with patch(
            "pyerp.business_modules.products.models.ProductCategory",
            MockProductCategory,
        ):
            command = MockImportCommand()
            result = command.handle(
                file_path="test.json",
                strict=True,
                default_category="DEFAULT",
            )

            assert result == "Successfully imported 2 products"

    def test_handle_with_validation_errors(self):
        """Test handling validation errors."""
        with patch(
            "pyerp.business_modules.products.models.ProductCategory",
            MockProductCategory,
        ):
            command = MockImportCommand()
            with pytest.raises(ValueError):
                command.handle(
                    file_path="test.json",
                    strict=True,
                    default_category="DEFAULT",
                )


if __name__ == "__main__":
    pytest.main([__file__])
