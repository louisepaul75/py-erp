"""
Tests for the importproducts management command.
"""
import pytest
import tempfile
import csv
import os
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from io import StringIO

from pyerp.management.commands.importproducts import Command, ProductImportValidator
from pyerp.core.validators import ValidationResult


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    with open(tmp_file.name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sku', 'name', 'category', 'list_price', 'description'])
        writer.writerow(['SKU001', 'Test Product 1', 'Electronics', '99.99', 'A test product'])
        writer.writerow(['SKU002', 'Test Product 2', 'Furniture', '199.99', 'Another test product'])
        writer.writerow(['', '', 'Electronics', 'invalid', 'Invalid product'])  # Invalid row
    
    yield tmp_file.name
    # Clean up
    os.unlink(tmp_file.name)


@pytest.mark.unit
class TestProductImportValidator:
    """Tests for the ProductImportValidator class."""
    


    


    
    def test_validate_sku(self):
        """Test SKU validation."""
        validator = ProductImportValidator()
        
        # Valid SKU
        sku, result = validator.validate_sku('SKU001', {})
        assert sku == 'SKU001'
        assert not result.errors
        
        # Empty SKU
        sku, result = validator.validate_sku('', {})
        assert sku is None
        assert 'sku' in result.errors
        assert 'required' in result.errors['sku'][0].lower()
    

    
    def test_validate_name(self):
        """Test name validation."""
        validator = ProductImportValidator()
        
        # Valid name
        name, result = validator.validate_name('Test Product', {})
        assert name == 'Test Product'
        assert not result.errors
        
        # Empty name
        name, result = validator.validate_name('', {})
        assert name is None
        assert 'name' in result.errors
        assert 'required' in result.errors['name'][0].lower()
    

    
    def test_validate_list_price(self):
        """Test list price validation."""
        validator = ProductImportValidator()
        
        # Valid price
        price, result = validator.validate_list_price('99.99', {})
        assert price == 99.99
        assert not result.errors
        
        # Negative price
        price, result = validator.validate_list_price('-10.50', {})
        assert price is None
        assert 'list_price' in result.errors
        assert 'negative' in result.errors['list_price'][0].lower()
        
        # Invalid format
        price, result = validator.validate_list_price('invalid', {})
        assert price is None
        assert 'list_price' in result.errors
        assert 'invalid' in result.errors['list_price'][0].lower()


@pytest.mark.unit
class TestImportProductsCommand:
    """Tests for the importproducts command."""
    

    
    def test_create_product_validator(self):
        """Test creating a product validator."""
        command = Command()
        validator = command.create_product_validator(strict=True, default_category='Electronics')
        
        assert isinstance(validator, ProductImportValidator)
        assert validator.strict is True
        assert validator.default_category == 'Electronics'
    

    
    def test_validate_products(self):
        """Test product validation."""
        command = Command()
        validator = command.create_product_validator()
        
        data = [
            {'sku': 'SKU001', 'name': 'Test Product', 'list_price': '99.99'},
            {'sku': '', 'name': 'Missing SKU', 'list_price': '49.99'},  # Invalid - missing SKU
            {'sku': 'SKU002', 'name': '', 'list_price': '29.99'},  # Invalid - missing name
        ]
        
        valid_products, errors = command.validate_products(data, validator)
        
        assert len(valid_products) == 1
        assert len(errors) == 2
        assert valid_products[0]['sku'] == 'SKU001'
    
    @patch('pyerp.management.commands.importproducts.Command.get_products_from_file')
    @patch('pyerp.management.commands.importproducts.Command.create_or_update_product')

    def test_handle_with_valid_file(self, mock_create, mock_get_products, sample_csv_file):
        """Test handling a valid file."""
        mock_get_products.return_value = [
            {'sku': 'SKU001', 'name': 'Test Product 1', 'category': 'Electronics', 'list_price': '99.99'},
            {'sku': 'SKU002', 'name': 'Test Product 2', 'category': 'Furniture', 'list_price': '199.99'}
        ]
        
        out = StringIO()
        cmd = Command()
        cmd.stdout = out
        cmd.handle(file_path=sample_csv_file)
        
        # Verify the mock was called with the sample file
        mock_get_products.assert_called_once_with(sample_csv_file)
        
        # Verify create_or_update_product was called twice (once for each valid product)
        assert mock_create.call_count == 2
        
        # Check output contains success message
        output = out.getvalue()
        assert 'successfully' in output.lower()
    
    @patch('pyerp.management.commands.importproducts.Command.get_products_from_file')

    def test_handle_with_invalid_data(self, mock_get_products, sample_csv_file):
        """Test handling invalid data."""
        # Return some invalid data
        mock_get_products.return_value = [
            {'sku': '', 'name': '', 'category': 'Electronics', 'list_price': 'invalid'}
        ]
        
        out = StringIO()
        err = StringIO()
        
        cmd = Command()
        cmd.stdout = out
        cmd.stderr = err
        result = cmd.handle(file_path=sample_csv_file)
        
        # Check error output contains validation errors
        error_output = err.getvalue()
        assert 'error' in error_output.lower() or 'no valid products' in error_output.lower()
        assert not result  # Should return False for invalid data