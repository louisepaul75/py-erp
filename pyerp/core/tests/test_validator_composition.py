"""
Tests for validator composition patterns.

This module tests how validators can be combined and composed to
create more complex validation workflows.
"""

from django.test import TestCase
from django import forms

from pyerp.core.form_validation import ValidatedForm
from pyerp.core.validators import (
    ValidationResult,
    Validator,
    RequiredValidator,
    RegexValidator,
    RangeValidator,
    LengthValidator,
    ChoiceValidator,
    CompoundValidator,
    BusinessRuleValidator,
)


class ConditionalValidator(Validator):
    """Validator that applies only if a condition is met."""
    
    def __init__(self, condition_func, validator, error_message=None):
        """
        Initialize with a condition function and a validator.
        
        Args:
            condition_func: Function that determines if validation should occur
            validator: Validator to apply if condition is met
            error_message: Optional error message
        """
        self.condition_func = condition_func
        self.validator = validator
        message = error_message or "Validation failed"
        super().__init__(message)
    
    def _validate(self, value, result, **kwargs):
        """Apply validator only if condition is met."""
        # Check if condition applies
        if self.condition_func(value, **kwargs):
            # Apply the validator
            validator_result = self.validator(value, **kwargs)
            result.merge(validator_result)


class AndValidator(CompoundValidator):
    """Validator that requires all child validators to pass."""
    
    def __init__(self, validators, error_message=None):
        """Initialize with list of validators that must all pass."""
        super().__init__(validators, require_all_valid=True, error_message=error_message)


class OrValidator(CompoundValidator):
    """Validator that requires at least one child validator to pass."""
    
    def __init__(self, validators, error_message=None):
        """Initialize with list of validators where at least one must pass."""
        super().__init__(validators, require_all_valid=False, error_message=error_message)


class CompositeAddressForm(ValidatedForm):
    """Form with composite address validation."""
    
    address_type = forms.ChoiceField(choices=[
        ('domestic', 'Domestic'),
        ('international', 'International'),
    ])
    street = forms.CharField(max_length=100)
    city = forms.CharField(max_length=50)
    state = forms.CharField(max_length=50)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=50)
    
    def setup_validators(self):
        """Set up form validators with composition."""
        # Basic validation
        self.add_validator('address_type', RequiredValidator())
        self.add_validator('street', RequiredValidator())
        self.add_validator('city', RequiredValidator())
        
        # Conditional validation for domestic addresses
        is_domestic = lambda value, **kwargs: kwargs.get('form') and kwargs.get('form').cleaned_data.get('address_type') == 'domestic'
        
        # US state validator (required for domestic)
        us_state_validator = AndValidator([
            RequiredValidator(error_message="State is required for domestic addresses"),
            ChoiceValidator(
                choices=[
                    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
                    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
                    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
                    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 
                    'DC',
                ],
                error_message="Please enter a valid US state code (e.g., CA for California)"
            )
        ])
        
        self.add_validator('state', ConditionalValidator(
            is_domestic,
            us_state_validator,
            error_message="Invalid state for domestic address"
        ))
        
        # US ZIP code validator (required for domestic)
        us_zip_validator = AndValidator([
            RequiredValidator(error_message="ZIP code is required for domestic addresses"),
            RegexValidator(
                r'^\d{5}(-\d{4})?$',
                error_message="ZIP code must be in format 12345 or 12345-6789"
            )
        ])
        
        self.add_validator('postal_code', ConditionalValidator(
            is_domestic,
            us_zip_validator,
            error_message="Invalid ZIP code format"
        ))
        
        # Country should be "United States" for domestic
        def validate_country(value, **kwargs):
            result = ValidationResult()
            field_name = kwargs.get('field_name', 'country')
            form = kwargs.get('form')
            
            if form and form.cleaned_data.get('address_type') == 'domestic':
                if value.upper() != 'UNITED STATES' and value.upper() != 'USA' and value.upper() != 'US':
                    result.add_error(field_name, "Country must be 'United States' for domestic addresses")
            
            return result
        
        self.add_validator('country', BusinessRuleValidator(validate_country))
        
        # International address validation
        is_international = lambda value, **kwargs: kwargs.get('form') and kwargs.get('form').cleaned_data.get('address_type') == 'international'
        
        # For international, country is required
        self.add_validator('country', ConditionalValidator(
            is_international,
            RequiredValidator(error_message="Country is required for international addresses"),
            error_message="Country is required"
        ))
        
        # For international, state is optional but city is required
        self.add_validator('city', ConditionalValidator(
            is_international,
            RequiredValidator(error_message="City is required for international addresses"),
            error_message="City is required"
        ))


class ProductSearchForm(ValidatedForm):
    """Form with OR condition validation for product search."""
    
    name = forms.CharField(max_length=100, required=False)
    sku = forms.CharField(max_length=50, required=False)
    barcode = forms.CharField(max_length=50, required=False)
    min_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    category = forms.ChoiceField(choices=[
        ('', 'All Categories'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
    ], required=False)
    
    def setup_validators(self):
        """Set up form validation with OR condition."""
        # At least one search criteria must be provided
        def at_least_one_criteria(cleaned_data):
            result = ValidationResult()
            
            has_criteria = (
                cleaned_data.get('name') or 
                cleaned_data.get('sku') or 
                cleaned_data.get('barcode') or 
                cleaned_data.get('min_price') is not None or 
                cleaned_data.get('max_price') is not None or 
                cleaned_data.get('category')
            )
            
            if not has_criteria:
                result.add_error('__all__', "At least one search criteria must be provided")
            
            return result
        
        self.add_form_validator(at_least_one_criteria)
        
        # If price range is provided, ensure min_price <= max_price
        def price_range_validator(cleaned_data):
            result = ValidationResult()
            
            min_price = cleaned_data.get('min_price')
            max_price = cleaned_data.get('max_price')
            
            if min_price is not None and max_price is not None:
                if min_price > max_price:
                    result.add_error('min_price', "Minimum price cannot be greater than maximum price")
                    result.add_error('max_price', "Maximum price cannot be less than minimum price")
            
            return result
        
        self.add_form_validator(price_range_validator)
        
        # If SKU is provided, validate format
        self.add_validator('sku', OrValidator([
            LengthValidator(min_length=0, max_length=0),  # Empty is valid
            RegexValidator(
                r'^[A-Za-z0-9\-]+$',
                error_message="SKU can only contain letters, numbers, and hyphens"
            )
        ]))
        
        # If barcode is provided, validate format (UPC/EAN)
        self.add_validator('barcode', OrValidator([
            LengthValidator(min_length=0, max_length=0),  # Empty is valid
            RegexValidator(
                r'^\d{12,13}$',
                error_message="Barcode must be 12 digits (UPC) or 13 digits (EAN)"
            )
        ]))


class ValidatorCompositionTests(TestCase):
    """Tests for validating composition patterns."""
    
    def test_conditional_validator(self):
        """Test conditional validator."""
        # Create a conditional validator that only validates non-empty values
        is_not_empty = lambda value, **kwargs: value and len(value) > 0
        length_validator = LengthValidator(min_length=5, max_length=10)
        conditional_validator = ConditionalValidator(is_not_empty, length_validator)
        
        # Test with empty value (condition not met, should pass)
        result = conditional_validator("", field_name="test")
        self.assertFalse(result.has_errors())
        
        # Test with value that meets condition but fails validation
        result = conditional_validator("abc", field_name="test")
        self.assertTrue(result.has_errors())
        self.assertIn("test", result.errors)
        
        # Test with value that meets condition and passes validation
        result = conditional_validator("abcdef", field_name="test")
        self.assertFalse(result.has_errors())
    
    def test_and_validator(self):
        """Test AND validator (all must pass)."""
        # Create validators
        length_validator = LengthValidator(min_length=5, max_length=10)
        regex_validator = RegexValidator(r'^[a-z]+$', error_message="Must be lowercase letters only")
        
        # Create AND validator
        and_validator = AndValidator([length_validator, regex_validator])
        
        # Test with value passing both validators
        result = and_validator("abcdef", field_name="test")
        self.assertFalse(result.has_errors())
        
        # Test with value failing length validator
        result = and_validator("abc", field_name="test")
        self.assertTrue(result.has_errors())
        self.assertIn("test", result.errors)
        
        # Test with value failing regex validator
        result = and_validator("Abcdef", field_name="test")
        self.assertTrue(result.has_errors())
        self.assertIn("test", result.errors)
        
        # Test with value failing both validators
        result = and_validator("Ab", field_name="test")
        self.assertTrue(result.has_errors())
        self.assertIn("test", result.errors)
        self.assertEqual(len(result.errors["test"]), 2)
    
    def test_or_validator(self):
        """Test OR validator (at least one must pass)."""
        # Create validators
        digit_validator = RegexValidator(r'^\d+$', error_message="Must be digits only")
        alpha_validator = RegexValidator(r'^[a-zA-Z]+$', error_message="Must be letters only")
        
        # Create OR validator
        or_validator = OrValidator([digit_validator, alpha_validator])
        
        # Test with value passing digit validator
        result = or_validator("12345", field_name="test")
        self.assertFalse(result.has_errors())
        
        # Test with value passing alpha validator
        result = or_validator("abcdef", field_name="test")
        self.assertFalse(result.has_errors())
        
        # Test with value failing both validators
        result = or_validator("abc123", field_name="test")
        self.assertTrue(result.has_errors())
        self.assertIn("test", result.errors)
    
    def test_domestic_address_validation(self):
        """Test composite validation for domestic addresses."""
        # Test valid domestic address
        form = CompositeAddressForm(data={
            'address_type': 'domestic',
            'street': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94107',
            'country': 'United States'
        })
        self.assertTrue(form.is_valid())
        
        # Test invalid state for domestic address
        form = CompositeAddressForm(data={
            'address_type': 'domestic',
            'street': '123 Main St',
            'city': 'San Francisco',
            'state': 'California',  # Should be CA
            'postal_code': '94107',
            'country': 'United States'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('state', form.errors)
        
        # Test invalid ZIP code for domestic address
        form = CompositeAddressForm(data={
            'address_type': 'domestic',
            'street': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': 'ABC',  # Invalid format
            'country': 'United States'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('postal_code', form.errors)
        
        # Test invalid country for domestic address
        form = CompositeAddressForm(data={
            'address_type': 'domestic',
            'street': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94107',
            'country': 'Canada'  # Should be United States
        })
        self.assertFalse(form.is_valid())
        self.assertIn('country', form.errors)
    
    def test_international_address_validation(self):
        """Test composite validation for international addresses."""
        # Test valid international address
        form = CompositeAddressForm(data={
            'address_type': 'international',
            'street': '123 Main St',
            'city': 'London',
            'state': 'Greater London',  # Any state is valid
            'postal_code': 'SW1A 1AA',  # Any postal code is valid
            'country': 'United Kingdom'
        })
        self.assertTrue(form.is_valid())
        
        # Test international address without country
        form = CompositeAddressForm(data={
            'address_type': 'international',
            'street': '123 Main St',
            'city': 'London',
            'state': 'Greater London',
            'postal_code': 'SW1A 1AA',
            'country': ''  # Missing country
        })
        self.assertFalse(form.is_valid())
        self.assertIn('country', form.errors)
        
        # Test international address without city
        form = CompositeAddressForm(data={
            'address_type': 'international',
            'street': '123 Main St',
            'city': '',  # Missing city
            'state': 'Greater London',
            'postal_code': 'SW1A 1AA',
            'country': 'United Kingdom'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('city', form.errors)
    
    def test_product_search_validation(self):
        """Test OR condition validation for product search."""
        # Test with no search criteria
        form = ProductSearchForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        
        # Test with name criteria
        form = ProductSearchForm(data={'name': 'Test Product'})
        self.assertTrue(form.is_valid())
        
        # Test with SKU criteria
        form = ProductSearchForm(data={'sku': 'TST-123'})
        self.assertTrue(form.is_valid())
        
        # Test with invalid SKU format
        form = ProductSearchForm(data={'sku': 'TST 123'})  # Space is invalid
        self.assertFalse(form.is_valid())
        self.assertIn('sku', form.errors)
        
        # Test with invalid barcode format
        form = ProductSearchForm(data={'barcode': '123'})  # Too short
        self.assertFalse(form.is_valid())
        self.assertIn('barcode', form.errors)
        
        # Test with valid barcode
        form = ProductSearchForm(data={'barcode': '123456789012'})  # 12 digits (UPC)
        self.assertTrue(form.is_valid())
        
        # Test with price range criteria
        form = ProductSearchForm(data={'min_price': '10.00', 'max_price': '50.00'})
        self.assertTrue(form.is_valid())
        
        # Test with invalid price range
        form = ProductSearchForm(data={'min_price': '50.00', 'max_price': '10.00'})
        self.assertFalse(form.is_valid())
        self.assertIn('min_price', form.errors)
        self.assertIn('max_price', form.errors)
        
        # Test with category criteria
        form = ProductSearchForm(data={'category': 'electronics'})
        self.assertTrue(form.is_valid())
        
        # Test with multiple criteria
        form = ProductSearchForm(data={
            'name': 'Test',
            'min_price': '10.00',
            'max_price': '50.00',
            'category': 'electronics'
        })
        self.assertTrue(form.is_valid()) 