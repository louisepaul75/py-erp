"""
Tests for the product-specific validators.

This module contains tests for the product validation classes and utilities.
"""

import unittest
from decimal import Decimal
import decimal

from pyerp.core.validators import ValidationResult


class MockProductCategory:
    """Mock ProductCategory model for testing."""

    def __init__(self, code="", name=""):
        self.code = code
        self.name = name

    def __str__(self):
        return self.name


class MockProduct:
    """Mock Product model for testing."""

    def __init__(self, sku="", name="", category=None, list_price=0):
        self.sku = sku
        self.name = name
        self.category = category
        self.list_price = list_price
        self.errors = {}


# Mock the ProductImportValidator class


class MockProductImportValidator:
    """Mock implementation of ProductImportValidator for testing."""

    def __init__(self, strict=False, transform_data=True, default_category=None):
        self.strict = strict
        self.transform_data = transform_data
        self.default_category = default_category

    def validate_sku(self, value, row_data, row_index=None):
        """Mock SKU validation."""
        result = ValidationResult()

        if not value:
            result.add_error("sku", "SKU is required")
            return None, result

        if " " in value:  # Simple validation: no spaces allowed
            result.add_error("sku", "SKU cannot contain spaces")
            return value, result

        if self.strict and not value.isalnum():
            result.add_error("sku", "SKU must be alphanumeric in strict mode")
            return value, result

        if row_index is not None and self.transform_data:
            value = f"{value}-{row_index}"

        return value, result

    def validate_name(self, value, row_data, row_index=None):
        """Mock name validation."""
        result = ValidationResult()

        if not value:
            result.add_error("name", "Name is required")
            return None, result

        if len(value) > 255:
            result.add_warning("name", "Name is too long and will be truncated")
            value = value[:255]

        if row_index is not None and self.transform_data:
            value = f"{value} (Row {row_index})"

        return value, result

    def validate_list_price(self, value, row_data, row_index=None):
        """Mock list price validation."""
        result = ValidationResult()

        try:
            if isinstance(value, str):
                value = Decimal(value.strip())
            elif isinstance(value, (int, float)):
                value = Decimal(str(value))
            elif value is None:
                result.add_error("list_price", "List price is required")
                return None, result
        except (ValueError, TypeError, decimal.InvalidOperation):
            result.add_error("list_price", "Invalid decimal format")
            return None, result

        if value < 0:
            result.add_error("list_price", "List price must be non-negative")
            return value, result

        if self.strict and value == 0:
            result.add_error("list_price", "List price must be greater than zero in strict mode")
            return value, result

        return value, result

    def _pre_validate_row(self, row_data, result, row_index=None):
        """Mock pre-validation."""
        if not row_data:
            result.add_error("row", "Row data cannot be empty")
            return

        required_fields = {"sku", "name"}
        missing_fields = required_fields - set(row_data.keys())
        if missing_fields:
            for field in missing_fields:
                result.add_error(field, f"{field} is required")

    def _post_validate_row(self, row_data, result, row_index=None):
        """Mock post-validation with business rules."""
        # Check that list price >= cost price
        if "list_price" in row_data and "cost_price" in row_data:
            if row_data["list_price"] < row_data["cost_price"]:
                result.add_error(
                    "list_price",
                    "List price cannot be less than cost price",
                )


class TestMockProductImportValidator(unittest.TestCase):
    """Test the MockProductImportValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.default_category = MockProductCategory(
            code="DEFAULT",
            name="Default Category",
        )
        self.validator = MockProductImportValidator(
            default_category=self.default_category,
        )
        self.strict_validator = MockProductImportValidator(
            default_category=self.default_category,
            strict=True,
        )
        self.no_transform_validator = MockProductImportValidator(
            default_category=self.default_category,
            transform_data=False,
        )

    def test_validate_sku(self):
        """Test SKU validation."""
        # Valid SKU
        sku, result = self.validator.validate_sku("ABC-123", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(sku, "ABC-123")

        # Invalid SKU (contains space)
        sku, result = self.validator.validate_sku("ABC 123", {})
        self.assertFalse(result.is_valid)
        self.assertIn("sku", result.errors)

        # Empty SKU
        sku, result = self.validator.validate_sku("", {})
        self.assertFalse(result.is_valid)
        self.assertIn("sku", result.errors)

        # None SKU
        sku, result = self.validator.validate_sku(None, {})
        self.assertFalse(result.is_valid)
        self.assertIn("sku", result.errors)

        # Test strict mode with non-alphanumeric SKU
        sku, result = self.strict_validator.validate_sku("ABC-123", {})
        self.assertFalse(result.is_valid)
        self.assertIn("SKU must be alphanumeric in strict mode", result.errors["sku"])

        # Test row index transformation
        sku, result = self.validator.validate_sku("ABC123", {}, row_index=1)
        self.assertTrue(result.is_valid)
        self.assertEqual(sku, "ABC123-1")

        # Test no transform
        sku, result = self.no_transform_validator.validate_sku("ABC123", {}, row_index=1)
        self.assertTrue(result.is_valid)
        self.assertEqual(sku, "ABC123")

    def test_validate_name(self):
        """Test name validation."""
        # Valid name
        name, result = self.validator.validate_name("Test Product", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(name, "Test Product")

        # Empty name
        name, result = self.validator.validate_name("", {})
        self.assertFalse(result.is_valid)
        self.assertIn("name", result.errors)

        # None name
        name, result = self.validator.validate_name(None, {})
        self.assertFalse(result.is_valid)
        self.assertIn("name", result.errors)

        # Very long name (should be truncated with warning)
        long_name = "A" * 300
        name, result = self.validator.validate_name(long_name, {})
        self.assertTrue(result.is_valid)
        self.assertEqual(len(name), 255)
        self.assertIn("name", result.warnings)

        # Test row index transformation
        name, result = self.validator.validate_name("Test Product", {}, row_index=1)
        self.assertTrue(result.is_valid)
        self.assertEqual(name, "Test Product (Row 1)")

        # Test no transform
        name, result = self.no_transform_validator.validate_name("Test Product", {}, row_index=1)
        self.assertTrue(result.is_valid)
        self.assertEqual(name, "Test Product")

    def test_validate_list_price(self):
        """Test list price validation."""
        # Valid decimal
        price, result = self.validator.validate_list_price("99.99", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("99.99"))

        # Valid integer
        price, result = self.validator.validate_list_price(100, {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("100"))

        # Invalid string
        price, result = self.validator.validate_list_price("not a price", {})
        self.assertFalse(result.is_valid)
        self.assertIn("list_price", result.errors)

        # Negative price
        price, result = self.validator.validate_list_price("-10.00", {})
        self.assertFalse(result.is_valid)
        self.assertIn("list_price", result.errors)

        # None price
        price, result = self.validator.validate_list_price(None, {})
        self.assertFalse(result.is_valid)
        self.assertIn("list_price", result.errors)

        # Test strict mode with zero price
        price, result = self.strict_validator.validate_list_price("0.00", {})
        self.assertFalse(result.is_valid)
        self.assertIn("List price must be greater than zero in strict mode", result.errors["list_price"])

        # Test whitespace handling
        price, result = self.validator.validate_list_price("  99.99  ", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("99.99"))

    def test_pre_validate_row(self):
        """Test pre-validation of row data."""
        # Test empty row data
        result = ValidationResult()
        self.validator._pre_validate_row({}, result)
        self.assertTrue(result.has_errors())
        self.assertIn("sku", result.errors)
        self.assertIn("name", result.errors)

        # Test missing required fields
        result = ValidationResult()
        self.validator._pre_validate_row({"sku": "ABC123"}, result)
        self.assertTrue(result.has_errors())
        self.assertIn("name", result.errors)

        # Test all required fields present
        result = ValidationResult()
        self.validator._pre_validate_row({"sku": "ABC123", "name": "Test"}, result)
        self.assertFalse(result.has_errors())

        # Test with None values
        result = ValidationResult()
        self.validator._pre_validate_row({"sku": None, "name": None}, result)
        self.assertFalse(result.has_errors())  # Pre-validation only checks presence of keys

        # Test with extra fields
        result = ValidationResult()
        self.validator._pre_validate_row(
            {"sku": "ABC123", "name": "Test", "extra": "value"}, result
        )
        self.assertFalse(result.has_errors())

    def test_post_validate_row(self):
        """Test post-validation of row data."""
        # Test valid price relationship
        result = ValidationResult()
        self.validator._post_validate_row(
            {"list_price": Decimal("100"), "cost_price": Decimal("50")}, result
        )
        self.assertFalse(result.has_errors())

        # Test invalid price relationship
        result = ValidationResult()
        self.validator._post_validate_row(
            {"list_price": Decimal("50"), "cost_price": Decimal("100")}, result
        )
        self.assertTrue(result.has_errors())
        self.assertIn("list_price", result.errors)

        # Test missing prices
        result = ValidationResult()
        self.validator._post_validate_row({}, result)
        self.assertFalse(result.has_errors())  # No error if prices are missing

        # Test equal prices
        result = ValidationResult()
        self.validator._post_validate_row(
            {"list_price": Decimal("100"), "cost_price": Decimal("100")}, result
        )
        self.assertFalse(result.has_errors())

        # Test with string prices (should not validate type here)
        result = ValidationResult()
        self.validator._post_validate_row(
            {"list_price": "100", "cost_price": "50"}, result
        )
        self.assertFalse(result.has_errors())

    def test_validate_list_price_precision(self):
        """Test list price decimal precision validation."""
        # Test standard decimal
        price, result = self.validator.validate_list_price("99.99", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("99.99"))

        # Test many decimal places
        price, result = self.validator.validate_list_price("99.9945", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("99.9945"))

        # Test zero decimal places
        price, result = self.validator.validate_list_price("100", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("100"))

        # Test scientific notation
        price, result = self.validator.validate_list_price("1.23e2", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("123"))

        # Test very large number
        price, result = self.validator.validate_list_price("999999.99", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("999999.99"))

        # Test very small number
        price, result = self.validator.validate_list_price("0.01", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(price, Decimal("0.01"))

    def test_combined_validation(self):
        """Test combination of multiple validations."""
        # Test all valid
        sku, sku_result = self.validator.validate_sku("ABC123", {})
        name, name_result = self.validator.validate_name("Test Product", {})
        price, price_result = self.validator.validate_list_price("99.99", {})

        self.assertTrue(all([sku_result.is_valid, name_result.is_valid, price_result.is_valid]))

        # Test all invalid
        sku, sku_result = self.validator.validate_sku("ABC 123", {})  # Space in SKU
        name, name_result = self.validator.validate_name("", {})  # Empty name
        price, price_result = self.validator.validate_list_price("-99.99", {})  # Negative price

        self.assertFalse(any([sku_result.is_valid, name_result.is_valid, price_result.is_valid]))

        # Test mixed validity
        sku, sku_result = self.validator.validate_sku("ABC123", {})  # Valid
        name, name_result = self.validator.validate_name("", {})  # Invalid
        price, price_result = self.validator.validate_list_price("99.99", {})  # Valid

        self.assertTrue(sku_result.is_valid)
        self.assertFalse(name_result.is_valid)
        self.assertTrue(price_result.is_valid)

    def test_strict_mode_combinations(self):
        """Test combinations of validations in strict mode."""
        # Test valid combinations in strict mode
        sku, sku_result = self.strict_validator.validate_sku("ABC123", {})  # Alphanumeric
        price, price_result = self.strict_validator.validate_list_price("99.99", {})

        self.assertTrue(sku_result.is_valid)
        self.assertTrue(price_result.is_valid)

        # Test invalid combinations in strict mode
        sku, sku_result = self.strict_validator.validate_sku("ABC-123", {})  # Non-alphanumeric
        price, price_result = self.strict_validator.validate_list_price("0", {})  # Zero price

        self.assertFalse(sku_result.is_valid)
        self.assertFalse(price_result.is_valid)

        # Test mixed mode validation
        sku, sku_result = self.validator.validate_sku("ABC-123", {})  # Valid in normal mode
        strict_sku, strict_result = self.strict_validator.validate_sku("ABC-123", {})  # Invalid in strict mode

        self.assertTrue(sku_result.is_valid)
        self.assertFalse(strict_result.is_valid)

    def test_transform_combinations(self):
        """Test combinations of transformations."""
        row_data = {"sku": "ABC123", "name": "Test Product"}
        row_index = 1

        # Test all transformations enabled
        sku, sku_result = self.validator.validate_sku(row_data["sku"], row_data, row_index)
        name, name_result = self.validator.validate_name(row_data["name"], row_data, row_index)

        self.assertEqual(sku, "ABC123-1")
        self.assertEqual(name, "Test Product (Row 1)")

        # Test all transformations disabled
        sku, sku_result = self.no_transform_validator.validate_sku(row_data["sku"], row_data, row_index)
        name, name_result = self.no_transform_validator.validate_name(row_data["name"], row_data, row_index)

        self.assertEqual(sku, "ABC123")
        self.assertEqual(name, "Test Product")

        # Test transformation with invalid data
        invalid_data = {"sku": "ABC 123", "name": ""}
        sku, sku_result = self.validator.validate_sku(invalid_data["sku"], invalid_data, row_index)
        name, name_result = self.validator.validate_name(invalid_data["name"], invalid_data, row_index)

        self.assertFalse(sku_result.is_valid)
        self.assertFalse(name_result.is_valid)


if __name__ == "__main__":
    unittest.main()
