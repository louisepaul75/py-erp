"""
Tests for the import validation functionality.

This module contains tests for the import validation classes and utilities
used during data import processes.
"""

import types
from unittest.mock import MagicMock, patch

import pytest

from pyerp.core.validators import ImportValidator, SkipRowException, ValidationResult

# Mock necessary imports


class MockImportProducts:
    """Mock importproducts module."""

    class Command:
        """Mock Command class."""

        def create_product_validator(self):
            """Create a mock validator."""
            return MagicMock()

        def validate_products(self, data):
            """Validate products with a mock."""
            return []

        def handle(self, *args, **options):
            """Handle command with mock."""
            return True


# Mock the import


importproducts = MagicMock()
importproducts.Command = MockImportProducts.Command


class TestImportValidator:
    """Tests for the generic ImportValidator class."""

    @pytest.fixture
    def test_validator(self):
        """Create a test validator for testing."""

        class TestImportValidator(ImportValidator):
            """Test implementation of ImportValidator."""

            def validate_name(self, value, row_data):
                """Validate name field."""
                resultt = ValidationResult()
                if not value:
                    resultt.add_error("name", "Name is required")
                    return resultt

                if len(value) < 3:
                    resultt.add_error("name", "Name must be at least 3 characters")
                return resultt

            def validate_age(self, value, row_data):
                """Validate age field."""
                resultt = ValidationResult()
                try:
                    age = int(value)
                    if age < 18:
                        resultt.add_error("age", "Must be at least 18 years old")
                except (ValueError, TypeError):
                    resultt.add_error("age", "Invalid age format")
                return resultt

            def cross_validate_row(self, validated_data):
                """Cross-validate row data."""
                resultt = ValidationResult()
                # Implement cross-validation logic
                return resultt

        return TestImportValidator(strict=False, transform_data=True)

    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        return self.TestImportValidator(strict=False, transform_data=True)

    @pytest.fixture
    def strict_validator(self):
        """Create a strict validator instance for testing."""
        return self.TestImportValidator(strict=True, transform_data=True)

    def test_validate_row_valid(self, test_validator):
        """Test validation of a valid row."""
        # Setup test data
        row_data = {
            "name": "Test Product",
            "code": "TP-123",
            "active": True,
        }

        # Validate row
        is_valid, validated_data, resultt = test_validator.validate_row(row_data)

        # Check resultts
        assert is_valid
        assert "name" in validated_data
        assert validated_data["name"] == "Test Product"
        assert not resultt.has_errors()

    def test_validate_row_with_errors(self, validator):
        """Test validating a row with errors."""
        row_data = {
            "name": "Te",  # Too short
            "code": "test-123",  # Non-alphanumeric
            "active": "yes",
        }

        is_valid, validated_data, resultt = validator.validate_row(row_data)

        assert not is_valid
        assert not resultt.is_valid
        assert "name" in resultt.errors
        assert "Name must be at least 3 characters" in resultt.errors["name"][0]
        assert "code" in resultt.errors
        assert "Code must be alphanumeric" in resultt.errors["code"][0]

    def test_validate_row_with_warnings(self, validator):
        """Test validating a row with warnings but no errors."""
        row_data = {
            "name": "Test Item",
            "code": "",  # Missing code (warning)
            "active": "yes",
        }

        is_valid, validated_data, resultt = validator.validate_row(row_data)

        # Still valid because warnings don't invalidate
        assert is_valid
        assert resultt.is_valid
        assert "code" in resultt.warnings
        assert "Code is recommended" in resultt.warnings["code"][0]

    def test_strict_validation(self, strict_validator):
        """Test strict validation where warnings are treated as errors."""
        row_data = {
            "name": "Test Item",
            "code": "",  # Missing code (warning)
            "active": "yes",
        }

        is_valid, validated_data, resultt = strict_validator.validate_row(row_data)

        # Invalid in strict mode
        assert not is_valid
        assert not resultt.is_valid
        assert "code" in resultt.errors
        assert "Code is recommended" in resultt.errors["code"][0]

    def test_cross_validation(self, validator):
        """Test cross-field validation rules."""
        # Rule: 'inactive' in name requires active=False
        row_data = {
            "name": "Inactive Test Item",
            "code": "TEST123",
            "active": "yes",  # Should be 'no' for inactive items
        }

        is_valid, validated_data, resultt = validator.validate_row(row_data)

        assert not is_valid
        assert not resultt.is_valid
        assert "active" in resultt.errors
        assert (
            "Items with 'inactive' in the name must be set as inactive"
            in resultt.errors["active"][0]
        )

    def test_missing_validation_method(self, validator):
        """Test behavior when validation method is missing."""
        # Add a field without a corresponding validate_* method
        row_data = {
            "name": "Test Item",
            "code": "TEST123",
            "active": "yes",
            "unknown_field": "value",  # No validate_unknown_field method
        }

        is_valid, validated_data, resultt = validator.validate_row(row_data)

        # Should still be valid, unknown field should be passed through
        assert is_valid
        assert resultt.is_valid
        assert "unknown_field" in validated_data
        assert validated_data["unknown_field"] == "value"

    def test_skip_row_exception(self, validator):
        """Test handling of SkipRowException."""
        # Create a validation method that raises SkipRowException

        def validate_test(self, value, row_data):
            if value == "skip":
                raise SkipRowException("Test skip with reason")
            return value, ValidationResult()

        # Add the method to the validator
        validator.validate_test = types.MethodType(validate_test, validator)

        # Test row that should be skipped
        row_data = {
            "name": "Test Item",
            "code": "TEST123",
            "active": "yes",
            "test": "skip",  # Should trigger skip
        }

        with pytest.raises(SkipRowException) as exc:
            validator.validate_row(row_data)

        assert "Test skip with reason" in str(exc.value)


class TestProductImportCommand:
    """Tests for the product import command using validation."""

    @pytest.fixture
    def command(self):
        """Create a command instance for testing."""
        return importproducts.Command()

    def test_create_product_validator(self, command):
        """Test creation of product validator."""
        with patch(
            "pyerp.products.validators.ProductImportValidator",
        ) as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator_class.return_value = mock_validator

            # Create validator with default category
            default_category = MagicMock()
            validator = command.create_product_validator(
                strict=True,
                default_category=default_category,
            )

            # Check validator creation
            mock_validator_class.assert_called_once_with(
                strict=True,
                transform_data=True,
                default_category=default_category,
            )
            assert validator is mock_validator

    def test_validate_products(self, command):
        """Test validation of products data."""
        # Mock validator
        mock_validator = MagicMock()

        # Set up mock validation resultts
        valid_resultt = (True, {"sku": "VALID-1", "name": "Valid Product"}, MagicMock())
        mock_validator.validate_row.side_effect = [
            valid_resultt,  # First row valid
            SkipRowException("Skip test"),  # Second row skipped
            (False, {}, MagicMock()),  # Third row invalid
        ]

        # Sample product data
        products_data = [
            {"sku": "VALID-1", "name": "Valid Product"},
            {"sku": "SKIP-1", "name": "Skip Product"},
            {"sku": "INVALID-1", "name": ""},
        ]

        # Mock logger
        mock_logger = MagicMock()

        # Call validate_products
        validated_products = list(
            command.validate_products(
                products_data,
                validator=mock_validator,
                logger=mock_logger,
            ),
        )

        # Check resultts
        assert len(validated_products) == 1
        assert validated_products[0] == valid_resultt[1]

        # Check validator calls
        assert mock_validator.validate_row.call_count == 3

        # Check logging
        assert mock_logger.warning.call_count == 1  # For skipped row
        assert mock_logger.error.call_count == 1  # For invalid row

    def test_handle_product_validation(self, command):
        """Test handle method with product validation."""
        # Mock methods
        command.load_json_data = MagicMock(
            return_value=[
                {"sku": "TEST-1", "name": "Test Product 1"},
                {"sku": "TEST-2", "name": "Test Product 2"},
            ],
        )
        command.create_product_validator = MagicMock()
        command.validate_products = MagicMock(
            return_value=[
                {"sku": "TEST-1", "name": "Test Product 1"},
            ],
        )
        command.create_or_update_product = MagicMock()

        # Call handle with options
        with patch("pyerp.products.models.ProductCategory.objects.get") as mock_get:
            default_category = MagicMock()
            mock_get.return_value = default_category

            command.handle(
                file_path="test.json",
                default_category="DEFAULT",
                strict=True,
            )

            # Check validator creation
            command.create_product_validator.assert_called_once_with(
                strict=True,
                default_category=default_category,
            )

            # Check product creation
            command.create_or_update_product.assert_called_once_with(
                {"sku": "TEST-1", "name": "Test Product 1"},
                default_category=default_category,
            )


# Import here for test_skip_row_exception
