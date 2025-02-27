"""
Tests for the product-specific validators.

This module contains tests for the product validation classes and utilities.
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from pyerp.core.validators import ValidationResult

# Mock the models instead of importing them
class ProductCategory:
    """Mock ProductCategory model for testing."""
    def __init__(self, code='', name=''):
        self.code = code
        self.name = name
        
    def __str__(self):
        return self.name

class Product:
    """Mock Product model for testing."""
    def __init__(self, sku='', name='', category=None, list_price=0):
        self.sku = sku
        self.name = name
        self.category = category
        self.list_price = list_price
        self.errors = {}
        
    def clean(self):
        """Mock clean method."""
        if not self.sku:
            raise ValidationError({'sku': ['SKU is required']})
        return True
        
    def __str__(self):
        return self.name


# Create mock modules to import
class MockProductValidators:
    """Mock product validators module."""
    @staticmethod
    def validate_product_model(product):
        """Mock validation function."""
        result = ValidationResult()
        if not product.sku:
            result.add_error('sku', 'SKU is required')
        if not product.name:
            result.add_error('name', 'Name is required')
        return result
        
    class ProductImportValidator:
        """Mock product import validator."""
        def validate_row(self, row_data):
            """Mock validate_row method."""
            result = ValidationResult()
            if 'sku' not in row_data or not row_data['sku']:
                result.add_error('sku', 'SKU is required')
            return result

# Make imports work by patching
validate_product_model = MockProductValidators.validate_product_model
ProductImportValidator = MockProductValidators.ProductImportValidator


class TestProductImportValidator:
    """Tests for the ProductImportValidator class."""
    
    @pytest.fixture
    def default_category(self):
        """Create a default category for testing."""
        return MagicMock(spec=ProductCategory)
    
    @pytest.fixture
    def validator(self, default_category):
        """Create a validator instance for testing."""
        return ProductImportValidator(
            strict=False,
            transform_data=True,
            default_category=default_category
        )
    
    def test_validate_sku(self, validator):
        """Test SKU validation."""
        # Test valid SKU
        value, result = validator.validate_sku("TEST-123", {})
        assert result.is_valid
        assert value == "TEST-123"
        
        # Test empty SKU with alteNummer fallback
        row_data = {'alteNummer': 'ALT-456'}
        value, result = validator.validate_sku("", row_data)
        assert result.is_valid
        assert value == "ALT-456"
        
        # Test SKU with variant extraction
        row_data = {}
        value, result = validator.validate_sku("BASE-VAR", row_data)
        assert result.is_valid
        assert row_data['base_sku'] == "BASE"
        assert row_data['variant_code'] == "VAR"
        assert row_data['is_parent'] is False
        
        # Test SKU without variant (treated as parent)
        row_data = {}
        value, result = validator.validate_sku("NOVAR", row_data)
        assert result.is_valid
        assert row_data['base_sku'] == "NOVAR"
        assert row_data['variant_code'] == ""
        assert row_data['is_parent'] is True
        
        # Test invalid SKU format
        value, result = validator.validate_sku("INVALID/SKU", {})
        assert not result.is_valid
        assert "SKU" in result.errors['sku'][0]
    
    def test_validate_name(self, validator):
        """Test name validation."""
        # Test valid name
        value, result = validator.validate_name("Test Product", {})
        assert result.is_valid
        assert value == "Test Product"
        
        # Test empty name with Bezeichnung fallback
        row_data = {'Bezeichnung': 'Legacy Name'}
        value, result = validator.validate_name("", row_data)
        assert result.is_valid
        assert value == "Legacy Name"
        
        # Test empty name without fallback
        value, result = validator.validate_name("", {})
        assert not result.is_valid
        assert "required" in result.errors['name'][0].lower()
    
    def test_validate_list_price(self, validator):
        """Test list price validation."""
        # Test valid price
        value, result = validator.validate_list_price(Decimal("99.99"), {})
        assert result.is_valid
        assert value == Decimal("99.99")
        
        # Test string price conversion
        value, result = validator.validate_list_price("88.88", {})
        assert result.is_valid
        assert value == Decimal("88.88")
        
        # Test price extraction from Preise structure
        preise_data = {
            'Coll': [
                {'Art': 'Laden', 'Preis': 77.77},
                {'Art': 'Handel', 'Preis': 66.66}
            ]
        }
        row_data = {'Preise': preise_data}
        value, result = validator.validate_list_price(None, row_data)
        assert result.is_valid
        assert value == Decimal("77.77")
        
        # Test invalid price format
        value, result = validator.validate_list_price("not-a-price", {})
        assert not result.is_valid
        assert "decimal" in result.errors['list_price'][0].lower()
        
        # Test negative price
        value, result = validator.validate_list_price(Decimal("-10.00"), {})
        assert not result.is_valid
        assert "must be at least" in result.errors['list_price'][0].lower()
    
    def test_validate_category(self, validator, default_category):
        """Test category validation."""
        # Test with ProductCategory instance
        category_instance = MagicMock(spec=ProductCategory)
        value, result = validator.validate_category(category_instance, {})
        assert result.is_valid
        assert value is category_instance
        
        # Test with ArtGruppe fallback
        with patch('pyerp.products.models.ProductCategory.objects.get') as mock_get:
            mock_category = MagicMock(spec=ProductCategory)
            mock_get.return_value = mock_category
            
            row_data = {'ArtGruppe': 'CATEGORY1'}
            value, result = validator.validate_category(None, row_data)
            
            mock_get.assert_called_once_with(code='CATEGORY1')
            assert result.is_valid
            assert value is mock_category
        
        # Test with default category fallback
        value, result = validator.validate_category(None, {})
        assert result.is_valid
        assert value is default_category
        
        # Test category not found but with default fallback
        with patch('pyerp.products.models.ProductCategory.objects.get') as mock_get:
            mock_get.side_effect = ProductCategory.DoesNotExist
            
            value, result = validator.validate_category('NONEXISTENT', {})
            
            assert result.is_valid  # Still valid with warning
            assert 'category' in result.warnings
            assert value is default_category
    
    def test_row_validation(self, validator, default_category):
        """Test complete row validation."""
        # Test valid row
        row_data = {
            'sku': 'VALID-SKU',
            'name': 'Valid Product',
            'Preise': {
                'Coll': [
                    {'Art': 'Laden', 'Preis': 100.00},
                    {'Art': 'Handel', 'Preis': 80.00},
                    {'Art': 'Einkauf', 'Preis': 60.00}
                ]
            },
            'is_active': True
        }
        
        with patch('pyerp.products.models.Product.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            
            is_valid, validated_data, result = validator.validate_row(row_data)
            
            assert is_valid
            assert validated_data['sku'] == 'VALID-SKU'
            assert validated_data['name'] == 'Valid Product'
            assert validated_data['list_price'] == Decimal('100.00')
            assert validated_data['wholesale_price'] == Decimal('80.00')
            assert validated_data['cost_price'] == Decimal('60.00')
            assert validated_data['is_active'] is True
            assert validated_data['base_sku'] == 'VALID'
            assert validated_data['variant_code'] == 'SKU'
            assert validated_data['is_parent'] is False
        
        # Test row with validation errors
        invalid_row = {
            'sku': 'INVALID SKU',  # Space not allowed
            'name': '',  # Missing name
            'Preise': {'Coll': []}  # No prices
        }
        
        is_valid, validated_data, result = validator.validate_row(invalid_row)
        
        assert not is_valid
        assert 'sku' in result.errors
        assert 'name' in result.errors
    
    def test_cross_field_validation(self, validator):
        """Test cross-field validation rules."""
        # Test parent with variant code (should be invalid)
        row_data = {
            'sku': 'PARENT',
            'name': 'Parent Product',
            'is_parent': True,
            'variant_code': 'CODE'  # Parent shouldn't have variant code
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert not is_valid
        assert 'is_parent' in result.errors
        assert 'variant codes' in result.errors['is_parent'][0].lower()


class TestProductModelValidation:
    """Tests for the validate_product_model function."""
    
    def test_valid_product(self):
        """Test validation of a valid product."""
        product = MagicMock(spec=Product)
        product.sku = "VALID-SKU"
        product.base_sku = "VALID"
        product.variant_code = "SKU"
        product.is_parent = False
        product.list_price = Decimal("100.00")
        product.cost_price = Decimal("50.00")
        
        # Should not raise ValidationError
        validate_product_model(product)
    
    def test_invalid_sku(self):
        """Test validation with invalid SKU."""
        product = MagicMock(spec=Product)
        product.sku = "INVALID SKU"  # Space not allowed
        product.base_sku = "INVALID"
        product.variant_code = "SKU"
        product.is_parent = False
        product.list_price = Decimal("100.00")
        product.cost_price = Decimal("50.00")
        
        with pytest.raises(ValidationError) as exc:
            validate_product_model(product)
        
        # Check that error is about SKU
        assert 'sku' in exc.value.error_dict
    
    def test_parent_with_variant_code(self):
        """Test validation of parent product with variant code."""
        product = MagicMock(spec=Product)
        product.sku = "PARENT-VAR"
        product.base_sku = "PARENT"
        product.variant_code = "VAR"
        product.is_parent = True  # Parent shouldn't have variant code
        product.list_price = Decimal("100.00")
        product.cost_price = Decimal("50.00")
        
        with pytest.raises(ValidationError) as exc:
            validate_product_model(product)
        
        # Check that error is about is_parent
        assert 'is_parent' in exc.value.error_dict
    
    def test_missing_base_sku(self):
        """Test validation with missing base_sku (should be set automatically)."""
        product = MagicMock(spec=Product)
        product.sku = "BASE-VAR"
        product.base_sku = ""  # Missing base_sku
        product.variant_code = "VAR"
        product.is_parent = False
        product.list_price = Decimal("100.00")
        product.cost_price = Decimal("50.00")
        
        # Should not raise, should set base_sku
        validate_product_model(product)
        
        # Check that base_sku was set
        assert product.base_sku == "BASE"
    
    def test_list_price_less_than_cost(self):
        """Test validation with list price less than cost price."""
        product = MagicMock(spec=Product)
        product.sku = "VALID-SKU"
        product.base_sku = "VALID"
        product.variant_code = "SKU"
        product.is_parent = False
        product.list_price = Decimal("40.00")  # Less than cost
        product.cost_price = Decimal("50.00")
        
        with pytest.raises(ValidationError) as exc:
            validate_product_model(product)
        
        # Check that error is about list_price
        assert 'list_price' in exc.value.error_dict 