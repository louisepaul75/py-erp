"""
Tests for the import validation functionality.

This module contains tests for the import validation classes and utilities
used during data import processes.
"""
import pytest
from unittest.mock import MagicMock, patch, call
from decimal import Decimal

from pyerp.core.validators import (
    ImportValidator, ValidationResult, SkipRowException
)
from pyerp.management.commands import importproducts


class TestImportValidator:
    """Tests for the generic ImportValidator class."""
    
    class TestImportValidator(ImportValidator):
        """Test implementation of ImportValidator."""
        
        def validate_name(self, value, row_data):
            """Validate name field."""
            result = ValidationResult()
            if not value:
                result.add_error('name', "Name is required")
                return value, result
            
            if len(value) < 3:
                result.add_error('name', "Name must be at least 3 characters")
            
            return value, result
        
        def validate_code(self, value, row_data):
            """Validate code field."""
            result = ValidationResult()
            if not value:
                # Use warning instead of error for code
                result.add_warning('code', "Code is recommended")
                return value, result
            
            # Transform to uppercase
            value = value.upper()
            
            if not value.isalnum():
                result.add_error('code', "Code must be alphanumeric")
            
            return value, result
        
        def validate_active(self, value, row_data):
            """Validate active field with default transformation."""
            result = ValidationResult()
            
            # Transform various inputs to boolean
            if isinstance(value, str):
                value = value.lower() in ('yes', 'true', '1', 'y', 't')
            elif value is None:
                value = False
            
            return bool(value), result
        
        def cross_validate_row(self, validated_data):
            """Cross-validate fields within the row."""
            result = ValidationResult()
            
            # Example rule: If name contains "inactive", active should be False
            if ('name' in validated_data and 
                'active' in validated_data and
                'inactive' in validated_data['name'].lower() and
                validated_data['active']):
                
                result.add_error(
                    'active', 
                    "Items with 'inactive' in the name must be set as inactive"
                )
            
            return result
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        return self.TestImportValidator(strict=False, transform_data=True)
    
    @pytest.fixture
    def strict_validator(self):
        """Create a strict validator instance for testing."""
        return self.TestImportValidator(strict=True, transform_data=True)
    
    def test_validate_row_valid(self, validator):
        """Test validating a valid row."""
        row_data = {
            'name': 'Test Item',
            'code': 'test123',
            'active': 'yes'
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid
        assert validated_data['name'] == 'Test Item'
        assert validated_data['code'] == 'TEST123'  # Transformed to uppercase
        assert validated_data['active'] is True  # Transformed to boolean
        assert result.is_valid
    
    def test_validate_row_with_errors(self, validator):
        """Test validating a row with errors."""
        row_data = {
            'name': 'Te',  # Too short
            'code': 'test-123',  # Non-alphanumeric
            'active': 'yes'
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert not is_valid
        assert not result.is_valid
        assert 'name' in result.errors
        assert 'Name must be at least 3 characters' in result.errors['name'][0]
        assert 'code' in result.errors
        assert 'Code must be alphanumeric' in result.errors['code'][0]
    
    def test_validate_row_with_warnings(self, validator):
        """Test validating a row with warnings but no errors."""
        row_data = {
            'name': 'Test Item',
            'code': '',  # Missing code (warning)
            'active': 'yes'
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        # Still valid because warnings don't invalidate
        assert is_valid
        assert result.is_valid
        assert 'code' in result.warnings
        assert 'Code is recommended' in result.warnings['code'][0]
    
    def test_strict_validation(self, strict_validator):
        """Test strict validation where warnings are treated as errors."""
        row_data = {
            'name': 'Test Item',
            'code': '',  # Missing code (warning)
            'active': 'yes'
        }
        
        is_valid, validated_data, result = strict_validator.validate_row(row_data)
        
        # Invalid in strict mode
        assert not is_valid
        assert not result.is_valid
        assert 'code' in result.errors
        assert 'Code is recommended' in result.errors['code'][0]
    
    def test_cross_validation(self, validator):
        """Test cross-field validation rules."""
        # Rule: 'inactive' in name requires active=False
        row_data = {
            'name': 'Inactive Test Item',
            'code': 'TEST123',
            'active': 'yes'  # Should be 'no' for inactive items
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert not is_valid
        assert not result.is_valid
        assert 'active' in result.errors
        assert "Items with 'inactive' in the name must be set as inactive" in result.errors['active'][0]
    
    def test_missing_validation_method(self, validator):
        """Test behavior when validation method is missing."""
        # Add a field without a corresponding validate_* method
        row_data = {
            'name': 'Test Item',
            'code': 'TEST123',
            'active': 'yes',
            'unknown_field': 'value'  # No validate_unknown_field method
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        # Should still be valid, unknown field should be passed through
        assert is_valid
        assert result.is_valid
        assert 'unknown_field' in validated_data
        assert validated_data['unknown_field'] == 'value'
    
    def test_skip_row_exception(self, validator):
        """Test handling of SkipRowException."""
        # Create a validation method that raises SkipRowException
        def validate_test(self, value, row_data):
            if value == 'skip':
                raise SkipRowException("Test skip with reason")
            return value, ValidationResult()
        
        # Add the method to the validator
        validator.validate_test = types.MethodType(validate_test, validator)
        
        # Test row that should be skipped
        row_data = {
            'name': 'Test Item',
            'code': 'TEST123',
            'active': 'yes',
            'test': 'skip'  # Should trigger skip
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
        with patch('pyerp.products.validators.ProductImportValidator') as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator_class.return_value = mock_validator
            
            # Create validator with default category
            default_category = MagicMock()
            validator = command.create_product_validator(
                strict=True,
                default_category=default_category
            )
            
            # Check validator creation
            mock_validator_class.assert_called_once_with(
                strict=True,
                transform_data=True,
                default_category=default_category
            )
            assert validator is mock_validator
    
    def test_validate_products(self, command):
        """Test validation of products data."""
        # Mock validator
        mock_validator = MagicMock()
        
        # Set up mock validation results
        valid_result = (True, {'sku': 'VALID-1', 'name': 'Valid Product'}, MagicMock())
        mock_validator.validate_row.side_effect = [
            valid_result,  # First row valid
            SkipRowException("Skip test"),  # Second row skipped
            (False, {}, MagicMock())  # Third row invalid
        ]
        
        # Sample product data
        products_data = [
            {'sku': 'VALID-1', 'name': 'Valid Product'},
            {'sku': 'SKIP-1', 'name': 'Skip Product'},
            {'sku': 'INVALID-1', 'name': ''}
        ]
        
        # Mock logger
        mock_logger = MagicMock()
        
        # Call validate_products
        validated_products = list(command.validate_products(
            products_data,
            validator=mock_validator,
            logger=mock_logger
        ))
        
        # Check results
        assert len(validated_products) == 1
        assert validated_products[0] == valid_result[1]
        
        # Check validator calls
        assert mock_validator.validate_row.call_count == 3
        
        # Check logging
        assert mock_logger.warning.call_count == 1  # For skipped row
        assert mock_logger.error.call_count == 1  # For invalid row
    
    def test_handle_product_validation(self, command):
        """Test handle method with product validation."""
        # Mock methods
        command.load_json_data = MagicMock(return_value=[
            {'sku': 'TEST-1', 'name': 'Test Product 1'},
            {'sku': 'TEST-2', 'name': 'Test Product 2'}
        ])
        command.create_product_validator = MagicMock()
        command.validate_products = MagicMock(return_value=[
            {'sku': 'TEST-1', 'name': 'Test Product 1'}
        ])
        command.create_or_update_product = MagicMock()
        
        # Call handle with options
        with patch('pyerp.products.models.ProductCategory.objects.get') as mock_get:
            default_category = MagicMock()
            mock_get.return_value = default_category
            
            command.handle(
                file_path='test.json',
                default_category='DEFAULT',
                strict=True
            )
            
            # Check validator creation
            command.create_product_validator.assert_called_once_with(
                strict=True,
                default_category=default_category
            )
            
            # Check product creation
            command.create_or_update_product.assert_called_once_with(
                {'sku': 'TEST-1', 'name': 'Test Product 1'},
                default_category=default_category
            )


# Import here for test_skip_row_exception
import types 