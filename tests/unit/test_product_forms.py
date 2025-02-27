"""
Tests for the product forms.

This module tests the forms in the products app.
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Import the mock models
from tests.unit.mock_models import MockProduct, MockProductCategory, MockQuerySet

# Import the forms module with patch to avoid Django app registry issues
with patch('django.apps.apps.get_model'):
    with patch('django.db.models.Model'):
        from pyerp.products.forms import ProductForm, ProductSearchForm


class TestProductForm:
    """Tests for the ProductForm."""
    
    @pytest.fixture
    def valid_form_data(self):
        """Create valid form data for testing."""
        return {
            'sku': 'TEST-SKU-001',
            'name': 'Test Product',
            'name_en': 'Test Product EN',
            'list_price': Decimal('100.00'),
            'cost_price': Decimal('50.00'),
            'is_active': True,
            'stock_quantity': 10,
        }
    
    @pytest.fixture
    def invalid_form_data(self):
        """Create invalid form data for testing."""
        return {
            'sku': 'TEST-SKU-002',
            'name': 'Test Product',
            'list_price': Decimal('40.00'),  # Less than cost_price
            'cost_price': Decimal('50.00'),
            'is_active': True,
            'is_parent': True,
            'variant_code': 'VAR1',  # Invalid for parent products
        }
    
    @pytest.fixture
    def existing_product(self):
        """Create an existing product for testing uniqueness validation."""
        return MockProduct(
            pk=1,
            sku='EXISTING-SKU',
            name='Existing Product',
            list_price=Decimal('100.00'),
            cost_price=Decimal('50.00'),
        )
    
    @patch('pyerp.products.forms.Product.objects.filter')
    def test_clean_sku_unique_new_product(self, mock_filter):
        """Test that the SKU uniqueness validation works for new products."""
        # Set up the mock to return an empty queryset (no existing products with this SKU)
        mock_queryset = MockQuerySet()
        mock_queryset.exists_return = False
        mock_filter.return_value = mock_queryset
        
        # Create a form with a new SKU
        form = ProductForm({'sku': 'NEW-SKU'})
        
        # Call the clean_sku method
        result = form.clean_sku()
        
        # Verify the result
        assert result == 'NEW-SKU'
        mock_filter.assert_called_once_with(sku='NEW-SKU')
    
    @patch('pyerp.products.forms.Product.objects.filter')
    def test_clean_sku_duplicate_new_product(self, mock_filter):
        """Test that the SKU uniqueness validation catches duplicates for new products."""
        # Set up the mock to return a queryset with an existing product
        mock_queryset = MockQuerySet([MockProduct(sku='DUPLICATE-SKU')])
        mock_queryset.exists_return = True
        mock_filter.return_value = mock_queryset
        
        # Create a form with a duplicate SKU
        form = ProductForm({'sku': 'DUPLICATE-SKU'})
        
        # Call the clean_sku method and expect a ValidationError
        with pytest.raises(Exception) as excinfo:
            form.clean_sku()
        
        # Verify the error message
        assert 'already exists' in str(excinfo.value)
        mock_filter.assert_called_once_with(sku='DUPLICATE-SKU')
    
    @patch('pyerp.products.forms.Product.objects.filter')
    def test_clean_sku_existing_product(self, mock_filter):
        """Test that the SKU uniqueness validation works for existing products."""
        # Set up the mock to return an empty queryset (no other products with this SKU)
        mock_queryset = MockQuerySet()
        mock_queryset.exists_return = False
        mock_filter.return_value = mock_queryset
        
        # Create a form for an existing product
        form = ProductForm({'sku': 'EXISTING-SKU'})
        form.instance = MockProduct(pk=1, sku='EXISTING-SKU')
        
        # Call the clean_sku method
        result = form.clean_sku()
        
        # Verify the result
        assert result == 'EXISTING-SKU'
        mock_filter.assert_called_once()
    
    def test_clean_parent_variant_validation(self):
        """Test validation of parent-variant relationship."""
        # Create a form with invalid data (parent product with variant code)
        form = ProductForm({
            'is_parent': True,
            'variant_code': 'VAR1',
        })
        
        # Call the clean method
        form.cleaned_data = {
            'is_parent': True,
            'variant_code': 'VAR1',
        }
        form.clean()
        
        # Verify that an error was added
        assert 'is_parent' in form.errors
        assert 'variant codes' in str(form.errors['is_parent'][0])
    
    def test_clean_price_validation(self):
        """Test validation of price relationship."""
        # Create a form with invalid data (list price less than cost price)
        form = ProductForm({
            'list_price': Decimal('40.00'),
            'cost_price': Decimal('50.00'),
        })
        
        # Call the clean method
        form.cleaned_data = {
            'list_price': Decimal('40.00'),
            'cost_price': Decimal('50.00'),
        }
        form.clean()
        
        # Verify that an error was added
        assert 'list_price' in form.errors
        assert 'less than cost price' in str(form.errors['list_price'][0])


class TestProductSearchForm:
    """Tests for the ProductSearchForm."""
    
    @pytest.fixture
    def valid_search_data(self):
        """Create valid search form data for testing."""
        return {
            'q': 'test product',
            'min_price': Decimal('10.00'),
            'max_price': Decimal('100.00'),
            'in_stock': True,
        }
    
    @pytest.fixture
    def invalid_search_data(self):
        """Create invalid search form data for testing."""
        return {
            'q': 'test product',
            'min_price': Decimal('100.00'),  # Greater than max_price
            'max_price': Decimal('50.00'),
            'in_stock': True,
        }
    
    @patch('pyerp.products.forms.ProductCategory.objects.all')
    def test_search_form_valid(self, mock_all, valid_search_data):
        """Test that the search form validates with valid data."""
        # Set up the mock to return a queryset of categories
        mock_all.return_value = MockQuerySet([
            MockProductCategory(code='CAT1', name='Category 1')
        ])
        
        # Create a form with valid data
        form = ProductSearchForm(valid_search_data)
        
        # Verify the form is valid
        assert form.is_valid()
    
    @patch('pyerp.products.forms.ProductCategory.objects.all')
    def test_search_form_invalid_price_range(self, mock_all, invalid_search_data):
        """Test that the search form validates price range correctly."""
        # Set up the mock to return a queryset of categories
        mock_all.return_value = MockQuerySet([
            MockProductCategory(code='CAT1', name='Category 1')
        ])
        
        # Create a form with invalid data
        form = ProductSearchForm(invalid_search_data)
        
        # Verify the form is invalid
        assert not form.is_valid()
        assert 'min_price' in form.errors
        assert 'less than maximum price' in str(form.errors['min_price'][0]) 