"""
Tests for form validation.

This module tests the form validation functionality.
"""
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from pyerp.core.form_validation import ValidatedForm, ValidationResult


class MockField:
    """Mock for Django form field."""
    
    def __init__(self, **kwargs):
        self.required = kwargs.get('required', True)
        self.help_text = kwargs.get('help_text', '')
        self.label = kwargs.get('label', '')
        self.initial = kwargs.get('initial', None)
        self.widget = kwargs.get('widget', None)
        self.validators = []


class MockModelForm(ValidatedForm):
    """Mock for Django ModelForm."""
    
    class Meta:
        """Meta class for the form."""
        model = None
        fields = []
    
    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)


# Create a mock Product class for testing
class Product:
    """Mock Product class for testing."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = kwargs.get('id', None)
    
    def save(self):
        """Mock save method."""
        if not self.id:
            self.id = 1  # Simulate saving to database
        return self
    
    def clean(self):
        """Mock clean method."""
        pass
    
    def __str__(self):
        """String representation."""
        return getattr(self, 'name', 'Mock Product')


class TestValidatedForm:
    """Tests for the ValidatedForm class."""
    
    def test_add_validator(self):
        """Test adding a validator to a form."""
        form = ValidatedForm()
        validator = lambda x, y: None
        form.add_validator('field', validator)
        
        assert 'field' in form.validators
        assert validator in form.validators['field']
    
    def test_add_form_validator(self):
        """Test adding a form-level validator."""
        form = ValidatedForm()
        validator = lambda x: None
        form.add_form_validator(validator)
        
        assert validator in form.form_validators
    
    def test_is_valid_no_validators(self):
        """Test is_valid with no validators."""
        form = ValidatedForm({'field': 'value'})
        assert form.is_valid()
        assert form.cleaned_data == {'field': 'value'}
    
    def test_is_valid_with_field_validator_passing(self):
        """Test is_valid with a passing field validator."""
        form = ValidatedForm({'field': 'value'})
        form.add_validator('field', lambda x, y: None)
        
        assert form.is_valid()
        assert not form.errors
    
    def test_is_valid_with_field_validator_failing(self):
        """Test is_valid with a failing field validator."""
        form = ValidatedForm({'field': 'value'})
        form.add_validator('field', lambda x, y: 'Error message')
        
        assert not form.is_valid()
        assert 'field' in form.errors
        assert 'Error message' in form.errors['field']
    
    def test_is_valid_with_form_validator_passing(self):
        """Test is_valid with a passing form validator."""
        form = ValidatedForm({'field': 'value'})
        form.add_form_validator(lambda x: None)
        
        assert form.is_valid()
        assert not form.errors
    
    def test_is_valid_with_form_validator_failing_dict(self):
        """Test is_valid with a failing form validator returning a dict."""
        form = ValidatedForm({'field': 'value'})
        form.add_form_validator(lambda x: {'field': 'Error message'})
        
        assert not form.is_valid()
        assert 'field' in form.errors
        assert 'Error message' in form.errors['field']
    
    def test_is_valid_with_form_validator_failing_validation_result(self):
        """Test is_valid with a failing form validator returning a ValidationResult."""
        form = ValidatedForm({'field': 'value'})
        
        def validator(cleaned_data):
            result = ValidationResult()
            result.add_error('field', 'Error message')
            return result
        
        form.add_form_validator(validator)
        
        assert not form.is_valid()
        assert 'field' in form.errors
        assert 'Error message' in form.errors['field']


class TestValidatedModelForm:
    """Tests for the ValidatedModelForm class."""
    
    class ProductForm(MockModelForm):
        """Test model form implementation."""
        
        class Meta:
            model = Product  # This uses the mock Product class defined above
            fields = ['name', 'sku', 'list_price']
        
        def __init__(self, data=None, **kwargs):
            """Initialize the form with validators."""
            super().__init__(data, **kwargs)
            
            # Set up fields
            self.fields['name'] = MockField(help_text='Product name')
            self.fields['sku'] = MockField(help_text='Stock Keeping Unit')
            self.fields['list_price'] = MockField(help_text='Retail price')
            
            # Add validators
            self.add_validator('sku', self.validate_sku)
            self.add_validator(None, self.validate_prices)  # Form-level validator
        
        def validate_sku(self, value, cleaned_data):
            """Validate that the SKU follows the required format."""
            if not value or not value.startswith('SKU-'):
                return 'SKU must start with "SKU-"'
            return None
        
        def validate_prices(self, cleaned_data):
            """Validate that the list price is positive."""
            list_price = cleaned_data.get('list_price')
            if list_price is not None and list_price <= 0:
                return {'list_price': 'List price must be positive'}
            return None
    
    def test_model_form_init_with_instance(self):
        """Test initializing a model form with an instance."""
        instance = Product(name='Test Product', sku='SKU-001', list_price=Decimal('99.99'))
        form = self.ProductForm(instance=instance)
        
        assert form.instance == instance
    
    def test_model_form_valid(self):
        """Test that a valid model form passes validation."""
        form = self.ProductForm({
            'name': 'Test Product',
            'sku': 'SKU-001',
            'list_price': Decimal('99.99')
        })
        
        assert form.is_valid()
        assert not form.errors
    
    def test_model_form_invalid_field(self):
        """Test that field validators catch invalid data in model forms."""
        form = self.ProductForm({
            'name': 'Test Product',
            'sku': 'INVALID-001',  # Doesn't start with SKU-
            'list_price': Decimal('-10.00')  # Negative price
        })
        
        assert not form.is_valid()
        assert 'sku' in form.errors
        assert 'list_price' in form.errors
        assert 'SKU must start with "SKU-"' in form.errors['sku']
        assert 'List price must be positive' in form.errors['list_price']
    
    def test_model_form_partial_data(self):
        """Test that partial data is validated correctly."""
        form = self.ProductForm({
            'name': 'Test Product',
            'sku': 'SKU-001',
            # Missing list_price
        })
        
        # This should be valid since list_price is not required
        assert form.is_valid()
        assert not form.errors 