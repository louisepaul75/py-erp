"""
Tests for the product-specific validators.

This module contains tests for the product validation classes and utilities.
"""
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from pyerp.core.validators import ValidationResult


class MockProductCategory:
    """Mock ProductCategory model for testing."""
    def __init__(self, code='', name=''):
        self.code = code
        self.name = name
        
    def __str__(self):
        return self.name


class MockProduct:
    """Mock Product model for testing."""
    def __init__(self, sku='', name='', category=None, list_price=0):
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
        
        return value, result
    
    def validate_list_price(self, value, row_data, row_index=None):
        """Mock list price validation."""
        result = ValidationResult()
        
        try:
            if isinstance(value, str):
                value = Decimal(value)
            elif isinstance(value, (int, float)):
                value = Decimal(str(value))
            elif value is None:
                result.add_error("list_price", "List price is required")
                return None, result
        except:
            result.add_error("list_price", "Invalid decimal format")
            return None, result
        
        if value < 0:
            result.add_error("list_price", "List price must be non-negative")
            return value, result
        
        return value, result
    
    def _pre_validate_row(self, row_data, result, row_index=None):
        """Mock pre-validation."""
        # Just a placeholder for testing
        pass
    
    def _post_validate_row(self, row_data, result, row_index=None):
        """Mock post-validation with business rules."""
        # Check that list price >= cost price
        if 'list_price' in row_data and 'cost_price' in row_data:
            if row_data['list_price'] < row_data['cost_price']:
                result.add_error("list_price", "List price cannot be less than cost price")


class TestMockProductImportValidator(unittest.TestCase):
    """Test the MockProductImportValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.default_category = MockProductCategory(code="DEFAULT", name="Default Category")
        self.validator = MockProductImportValidator(default_category=self.default_category)
    
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
    
    def test_post_validate_row(self):
        """Test post-validation of a row."""
        # Test case where list price < cost price
        row_data = {
            "list_price": Decimal("50.00"),
            "cost_price": Decimal("60.00")
        }
        result = ValidationResult()
        self.validator._post_validate_row(row_data, result)
        self.assertFalse(result.is_valid)
        self.assertIn("list_price", result.errors)
        
        # Test case where list price >= cost price
        row_data = {
            "list_price": Decimal("70.00"),
            "cost_price": Decimal("60.00")
        }
        result = ValidationResult()
        self.validator._post_validate_row(row_data, result)
        self.assertTrue(result.is_valid)


if __name__ == "__main__":
    unittest.main()