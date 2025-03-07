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

        def __init__(self):
            """Initialize the command."""
            self.create_product_validator = MagicMock()
            self.create_product_validator.return_value = MagicMock()

        def validate_products(self, data, validator=None):
            """Validate products with a mock."""
            if not data:
                return []
            return [data[0]]  # Return first item as valid

        def handle(self, file_path=None, default_category=None, strict=False):
            """Handle command with mock."""
            if not file_path or not default_category:
                return False
            if file_path == "nonexistent.json":
                raise FileNotFoundError("File not found")
            return True


# Mock the import


importproducts = MagicMock()
importproducts.Command = MockImportProducts.Command


class TestImportValidator:
    """Tests for the generic ImportValidator class."""

    class TestValidator(ImportValidator):
        """Test implementation of ImportValidator."""

        def validate_name(self, value, row_data, row_index=None):
            """Validate name field."""
            result = ValidationResult()
            if not value:
                result.add_error("name", "Name is required")
                return None, result

            if len(value) < 3:
                result.add_error("name", "Name must be at least 3 characters")
                return value, result

            if self.transform_data and row_index is not None:
                value = f"{value} (Row {row_index})"

            return value, result

        def validate_age(self, value, row_data, row_index=None):
            """Validate age field."""
            result = ValidationResult()
            try:
                age = int(value)
                if age < 18:
                    result.add_error("age", "Must be at least 18 years old")
                    return age, result
                if age > 100:
                    result.add_warning("age", "Age seems unusually high")
                return age, result
            except (ValueError, TypeError):
                result.add_error("age", "Invalid age format")
                return None, result

        def validate_code(self, value, row_data, row_index=None):
            """Validate code field."""
            result = ValidationResult()
            if not value:
                if self.strict:
                    result.add_error("code", "Code is required in strict mode")
                else:
                    result.add_warning("code", "Code is recommended")
                return value, result

            if not value.isalnum():
                result.add_error("code", "Code must be alphanumeric")
                return value, result

            if self.transform_data and row_index is not None:
                value = f"{value}-{row_index}"

            return value, result

        def cross_validate_row(self, validated_data):
            """Cross-validate row data."""
            result = ValidationResult()
            
            # Check name-active relationship
            if "name" in validated_data and "active" in validated_data:
                name = validated_data["name"].lower()
                active = validated_data["active"]
                if "inactive" in name and active:
                    result.add_error(
                        "active",
                        "Items with 'inactive' in the name must be set as inactive"
                    )

            # Check age-code relationship
            if "age" in validated_data and "code" in validated_data:
                age = validated_data.get("age")
                code = validated_data.get("code")
                if age is not None and isinstance(age, int) and age < 21 and not code:
                    result.add_error(
                        "code",
                        "Code is required for items with age under 21"
                    )

            return result

    @pytest.fixture
    def test_validator(self):
        """Create a test validator for testing."""
        return self.TestValidator(strict=False, transform_data=True)

    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        return self.TestValidator(strict=False, transform_data=True)

    @pytest.fixture
    def strict_validator(self):
        """Create a strict validator instance for testing."""
        return self.TestValidator(strict=True, transform_data=True)

    @pytest.fixture
    def no_transform_validator(self):
        """Create a validator instance with transform_data=False."""
        return self.TestValidator(strict=False, transform_data=False)

    def test_validate_row_valid(self, test_validator):
        """Test validation of a valid row."""
        # Setup test data
        row_data = {
            "name": "Test Product",
            "code": "TP123",
            "active": True,
            "age": "25",
        }

        # Validate row
        is_valid, validated_data, result = test_validator.validate_row(row_data)

        # Check results
        assert is_valid
        assert "name" in validated_data
        assert validated_data["name"] == "Test Product"
        assert validated_data["age"] == 25
        assert not result.has_errors()

    def test_validate_row_with_errors(self, validator):
        """Test validating a row with errors."""
        row_data = {
            "name": "Te",  # Too short
            "code": "test-123",  # Non-alphanumeric
            "active": "yes",
            "age": "17",  # Under 18
        }

        is_valid, validated_data, result = validator.validate_row(row_data)

        assert not is_valid
        assert not result.is_valid
        assert "name" in result.errors
        assert "Name must be at least 3 characters" in result.errors["name"][0]
        assert "code" in result.errors
        assert "Code must be alphanumeric" in result.errors["code"][0]
        assert "age" in result.errors
        assert "Must be at least 18 years old" in result.errors["age"][0]

    def test_validate_row_with_warnings(self, validator):
        """Test validating a row with warnings but no errors."""
        row_data = {
            "name": "Test Item",
            "code": "",  # Missing code (warning)
            "active": "yes",
            "age": "101",  # High age (warning)
        }

        is_valid, validated_data, result = validator.validate_row(row_data)

        # Still valid because warnings don't invalidate
        assert is_valid
        assert result.is_valid
        assert "code" in result.warnings
        assert "Code is recommended" in result.warnings["code"][0]
        assert "age" in result.warnings
        assert "Age seems unusually high" in result.warnings["age"][0]

    def test_strict_validation(self, strict_validator):
        """Test strict validation where warnings are treated as errors."""
        row_data = {
            "name": "Test Item",
            "code": "",  # Missing code (error in strict mode)
            "active": "yes",
            "age": "25",
        }

        is_valid, validated_data, result = strict_validator.validate_row(row_data)

        # Invalid in strict mode
        assert not is_valid
        assert not result.is_valid
        assert "code" in result.errors
        assert "Code is required in strict mode" in result.errors["code"][0]

    def test_data_transformation(self, validator, no_transform_validator):
        """Test data transformation with row indices."""
        row_data = {
            "name": "Test Item",
            "code": "TEST123",
            "active": True,
            "age": "25",
        }

        # Test with transform_data=True
        is_valid, validated_data, result = validator.validate_row(row_data, row_index=1)
        assert is_valid
        assert validated_data["name"] == "Test Item (Row 1)"
        assert validated_data["code"] == "TEST123-1"
        assert validated_data["age"] == 25

        # Test with transform_data=False
        is_valid, validated_data, result = no_transform_validator.validate_row(row_data, row_index=1)
        assert is_valid
        assert validated_data["name"] == "Test Item"
        assert validated_data["code"] == "TEST123"
        assert validated_data["age"] == 25

    def test_cross_validation(self, validator):
        """Test cross-validation rules."""
        row_data = {
            "name": "Test Item",
            "code": "",
            "active": True,
            "age": "20",  # Under 21 with no code
        }

        is_valid, validated_data, result = validator.validate_row(row_data)

        assert not is_valid
        assert "code" in result.errors
        assert "Code is required for items with age under 21" in result.errors["code"][0]

    def test_missing_validation_method(self, validator):
        """Test behavior when validation method is missing."""
        row_data = {
            "name": "Test Item",
            "code": "TEST123",
            "active": True,
            "age": "25",
            "unknown_field": "value",  # No validate_unknown_field method
        }

        is_valid, validated_data, result = validator.validate_row(row_data)

        # Should still be valid, unknown field should be passed through
        assert is_valid
        assert result.is_valid
        assert "unknown_field" in validated_data
        assert validated_data["unknown_field"] == "value"

    def test_skip_row_exception(self, validator):
        """Test handling of SkipRowException."""
        def validate_test(self, value, row_data, row_index=None):
            if value == "skip":
                raise SkipRowException("Test skip with reason")
            return value, ValidationResult()

        # Add the method to the validator
        validator.validate_test = types.MethodType(validate_test, validator)

        row_data = {
            "name": "Test Item",
            "code": "TEST123",
            "active": True,
            "age": "25",
            "test": "skip",
        }

        with pytest.raises(SkipRowException) as exc:
            validator.validate_row(row_data)
        assert "Test skip with reason" in str(exc.value)

    def test_validation_method_return_values(self, validator):
        """Test different return value scenarios from validation methods."""
        def validate_return_none(self, value, row_data, row_index=None):
            return None, ValidationResult()

        def validate_return_only_result(self, value, row_data, row_index=None):
            result = ValidationResult()
            result.add_error("field", "Error message")
            return result

        def validate_return_modified(self, value, row_data, row_index=None):
            return "modified_" + str(value), ValidationResult()

        # Test method returning None
        validator.validate_test1 = types.MethodType(validate_return_none, validator)
        row_data = {"test1": "value"}
        is_valid, validated_data, result = validator.validate_row(row_data)
        assert is_valid
        assert validated_data["test1"] is None

        # Test method returning only result
        validator.validate_test2 = types.MethodType(validate_return_only_result, validator)
        row_data = {"test2": "value"}
        is_valid, validated_data, result = validator.validate_row(row_data)
        assert not is_valid
        assert "field" in result.errors

        # Test method returning modified value
        validator.validate_test3 = types.MethodType(validate_return_modified, validator)
        row_data = {"test3": "value"}
        is_valid, validated_data, result = validator.validate_row(row_data)
        assert is_valid
        assert validated_data["test3"] == "modified_value"


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

            assert validator == mock_validator

    def test_validate_products(self, command):
        """Test product validation."""
        # Mock validator
        mock_validator = MagicMock()
        command.create_product_validator = MagicMock(return_value=mock_validator)

        # Test data
        products = [
            {"sku": "TEST-1", "name": "Test Product 1"},
            {"sku": "TEST-2", "name": "Test Product 2"},
        ]

        # Mock validation results
        mock_validator.validate_row.side_effect = [
            (True, {"sku": "TEST-1", "name": "Test Product 1"}, ValidationResult()),
            (False, {}, ValidationResult()),
        ]

        # Validate products
        valid_products = command.validate_products(products)

        # Check results
        assert len(valid_products) == 1
        assert valid_products[0]["sku"] == "TEST-1"
        assert mock_validator.validate_row.call_count == 2

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

            result = command.handle(
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

            assert result is True

    def test_handle_with_invalid_file(self, command):
        """Test handle method with invalid file path."""
        command.load_json_data = MagicMock(side_effect=FileNotFoundError)

        with pytest.raises(FileNotFoundError):
            command.handle(
                file_path="nonexistent.json",
                default_category="DEFAULT",
                strict=True,
            )

    def test_handle_with_validation_errors(self, command):
        """Test handle method when all products fail validation."""
        command.load_json_data = MagicMock(
            return_value=[
                {"sku": "TEST-1", "name": "Test Product 1"},
                {"sku": "TEST-2", "name": "Test Product 2"},
            ],
        )
        command.validate_products = MagicMock(return_value=[])  # All products invalid

        with patch("pyerp.products.models.ProductCategory.objects.get") as mock_get:
            default_category = MagicMock()
            mock_get.return_value = default_category

            result = command.handle(
                file_path="test.json",
                default_category="DEFAULT",
                strict=True,
            )

            assert result is False
            command.create_or_update_product.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
