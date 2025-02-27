"""
Tests for form validation utilities.

This module contains tests for the form validation classes and utilities
that integrate Django forms with the validation framework.
"""
import pytest
from unittest.mock import MagicMock, patch

from django import forms
from django.test import TestCase
from django.core.exceptions import ValidationError

from pyerp.core.validators import (
    Validator, RequiredValidator, ValidationResult, 
    RegexValidator, RangeValidator
)
from pyerp.core.form_validation import (
    ValidatedFormMixin, ValidatedModelForm, ValidatedForm
)

# Create a proper mock Product model class to use in tests
class MockOptions:
    """Mock Options class for Django model metadata."""
    def __init__(self):
        self.model_name = 'product'
        self.app_label = 'products'
        self.verbose_name = 'Product'
        self.object_name = 'Product'
        self.abstract = False
        self.swapped = False
        self.fields = {}
        self.private_fields = []
        self.many_to_many = []
        self.related_objects = []
        self.concrete_fields = []
        self.local_concrete_fields = []
        self.proxy = False
        self.auto_created = False
        self.get_fields = lambda: []

class Product:
    """Mock Product model for testing."""
    __name__ = 'Product'
    _meta = MockOptions()
    
    DoesNotExist = type('DoesNotExist', (Exception,), {})
    MultipleObjectsReturned = type('MultipleObjectsReturned', (Exception,), {})
    
    objects = MagicMock()
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def save(self, *args, **kwargs):
        pass
    
    def clean(self):
        pass

class TestValidatedFormMixin:
    """Tests for the ValidatedFormMixin class."""
    
    class TestForm(ValidatedFormMixin, forms.Form):
        """Test form implementation using ValidatedFormMixin."""
        name = forms.CharField(max_length=100)
        age = forms.IntegerField(required=False)
        email = forms.EmailField(required=False)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add validators to fields
            self.add_validator('name', RequiredValidator(
                error_message="Name is required"
            ))
            self.add_validator('age', RangeValidator(
                min_value=18, max_value=100,
                error_message="Age must be between {min_value} and {max_value}"
            ))
            self.add_validator('email', RegexValidator(
                pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                error_message="Invalid email format"
            ))
    
    @pytest.fixture
    def form(self):
        """Create a form instance for testing."""
        return self.TestForm()
    
    def test_add_validator(self, form):
        """Test adding validators to fields."""
        # Validators should be added in init
        assert 'name' in form.field_validators
        assert isinstance(form.field_validators['name'][0], RequiredValidator)
        
        # Add another validator
        new_validator = MagicMock(spec=Validator)
        form.add_validator('name', new_validator)
        
        assert len(form.field_validators['name']) == 2
        assert form.field_validators['name'][1] is new_validator
    
    def test_apply_validators(self, form):
        """Test applying validators to field values."""
        # Valid value for name
        result = form.apply_validators('name', 'Test Name')
        assert result.is_valid
        
        # Invalid value for age (below min)
        result = form.apply_validators('age', 10)
        assert not result.is_valid
        assert len(result.errors) == 1
        assert 'Age must be between 18 and 100' in result.errors['age'][0]
        
        # Invalid value for email
        result = form.apply_validators('email', 'not-an-email')
        assert not result.is_valid
        assert len(result.errors) == 1
        assert 'Invalid email format' in result.errors['email'][0]
    
    def test_clean_field(self, form):
        """Test cleaning individual fields with validation."""
        # Override clean_name to test integration
        form.cleaned_data = {}
        
        # Valid name
        form.cleaned_data['name'] = 'Test Name'
        value = form.clean_name()
        assert value == 'Test Name'
        
        # Invalid age
        form.cleaned_data['age'] = 15
        with pytest.raises(ValidationError) as exc:
            form.clean_age()
        
        assert 'Age must be between 18 and 100' in str(exc.value)
    
    def test_clean(self, form):
        """Test the clean method that applies all validators."""
        # Create a form with valid data
        test_form = self.TestForm(data={
            'name': 'Test Name',
            'age': 25,
            'email': 'test@example.com'
        })
        
        # Clean should succeed
        cleaned_data = test_form.clean()
        assert cleaned_data['name'] == 'Test Name'
        assert cleaned_data['age'] == 25
        assert cleaned_data['email'] == 'test@example.com'
        
        # Create a form with invalid data
        invalid_form = self.TestForm(data={
            'name': '',  # Empty name
            'age': 15,   # Age too low
            'email': 'not-an-email'  # Invalid email
        })
        
        # Clean should raise ValidationError
        with pytest.raises(ValidationError):
            invalid_form.clean()
        
        # Errors should be populated
        assert 'name' in invalid_form.errors
        assert 'age' in invalid_form.errors
        assert 'email' in invalid_form.errors


class TestValidatedModelForm:
    """Tests for the ValidatedModelForm class."""
    
    class ProductForm(ValidatedModelForm):
        """Test model form implementation."""
        
        class Meta:
            model = Product
            fields = ['name', 'sku', 'list_price']
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add validators
            self.add_validator('sku', RegexValidator(
                pattern=r'^[A-Z0-9-]+$',
                error_message="SKU must contain only uppercase letters, numbers, and hyphens"
            ))
            
            # Add a form-level validator
            self.add_form_validator(self.validate_prices)
        
        def validate_prices(self, cleaned_data):
            """Validate that list_price is positive."""
            result = ValidationResult()
            if 'list_price' in cleaned_data and cleaned_data['list_price'] <= 0:
                result.add_error('list_price', "List price must be positive")
            return result
    
    @pytest.fixture
    def model_form(self):
        """Create a model form instance for testing."""
        with patch.object(self.ProductForm, 'Meta'):
            self.ProductForm.Meta.model = Product
            return self.ProductForm()
    
    def test_model_instance_validation(self, model_form):
        """Test validation of model instance."""
        # Mock model instance
        instance = MagicMock()
        model_form.instance = instance
        
        # Mock _post_clean to avoid actual model validation
        with patch.object(model_form, '_post_clean'):
            # Test clean with form validators
            with patch.object(model_form, 'apply_validators') as mock_apply:
                mock_apply.return_value = ValidationResult()  # Valid result
                
                # Call clean
                model_form.cleaned_data = {
                    'sku': 'TEST-123',
                    'name': 'Test Product',
                    'list_price': 100
                }
                model_form.clean()
                
                # Should have called apply_validators for each field
                assert mock_apply.call_count == 3
    
    def test_form_level_validation(self, model_form):
        """Test form-level validators."""
        # Test with positive list_price
        model_form.cleaned_data = {
            'sku': 'TEST-123',
            'name': 'Test Product',
            'list_price': 100
        }
        
        # This should pass
        form_result = model_form.apply_form_validators(model_form.cleaned_data)
        assert form_result.is_valid
        
        # Test with negative list_price
        model_form.cleaned_data = {
            'sku': 'TEST-123',
            'name': 'Test Product',
            'list_price': -50
        }
        
        # This should fail
        form_result = model_form.apply_form_validators(model_form.cleaned_data)
        assert not form_result.is_valid
        assert 'list_price' in form_result.errors
        assert 'List price must be positive' in form_result.errors['list_price'][0]


class TestValidatedForm:
    """Tests for the ValidatedForm class."""
    
    class ContactForm(ValidatedForm):
        """Test form implementation."""
        name = forms.CharField(max_length=100)
        email = forms.EmailField()
        message = forms.CharField(widget=forms.Textarea)
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add validators
            self.add_validator('name', RequiredValidator(
                error_message="Name is required"
            ))
            self.add_validator('email', RegexValidator(
                pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                error_message="Invalid email format"
            ))
            
            # Add a form-level validator
            self.add_form_validator(self.validate_message_length)
        
        def validate_message_length(self, cleaned_data):
            """Validate that message is at least 20 characters."""
            result = ValidationResult()
            if 'message' in cleaned_data and len(cleaned_data['message']) < 20:
                result.add_error(
                    'message', 
                    "Message must be at least 20 characters long"
                )
            return result
    
    @pytest.fixture
    def form(self):
        """Create a form instance for testing."""
        return self.ContactForm()
    
    def test_form_init(self, form):
        """Test form initialization with validators."""
        # Check if field validators are added
        assert 'name' in form.field_validators
        assert 'email' in form.field_validators
        assert isinstance(form.field_validators['name'][0], RequiredValidator)
        
        # Check if form validators are added
        assert len(form.form_validators) == 1
        assert form.form_validators[0] == form.validate_message_length
    
    def test_is_valid(self):
        """Test form validation with is_valid."""
        # Create a form with valid data
        form = self.ContactForm(data={
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message that is longer than 20 characters.'
        })
        
        # Form should be valid
        assert form.is_valid()
        
        # Create a form with invalid data
        invalid_form = self.ContactForm(data={
            'name': '',  # Empty name
            'email': 'not-an-email',  # Invalid email
            'message': 'Too short'  # Message too short
        })
        
        # Form should be invalid
        assert not invalid_form.is_valid()
        
        # Errors should be populated
        assert 'name' in invalid_form.errors
        assert 'email' in invalid_form.errors
        assert 'message' in invalid_form.errors
    
    def test_clean(self, form):
        """Test the clean method."""
        # Add data to the form
        form.cleaned_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message.'
        }
        
        # Clean should apply all validators
        with patch.object(form, 'apply_validators') as mock_apply:
            mock_apply.return_value = ValidationResult()  # Valid result
            
            # Call clean
            form.clean()
            
            # Should have called apply_validators for each field
            assert mock_apply.call_count == 3 