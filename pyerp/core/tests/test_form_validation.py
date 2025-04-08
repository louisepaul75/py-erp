"""
Tests for the form validation module.

This module tests the functionality of the form validation framework in
pyerp/core/form_validation.py, ensuring that form validators work correctly
with Django forms.
"""

import unittest
from django import forms
from django.db import models # Move import

# Import ValidatedModelForm here as well
from pyerp.core.form_validation import ValidatedForm, ValidatedModelForm
from pyerp.core.validators import (
    ValidationResult,
    RequiredValidator,
    LengthValidator,
    RegexValidator,
    RangeValidator,
    ChoiceValidator,
    DecimalValidator,
)


class SimpleValidator:
    """Simple validator for testing."""
    
    def __init__(self, should_fail=False, message="Validation error"):
        self.should_fail = should_fail
        self.message = message
        
    def __call__(self, value, **kwargs):
        result = ValidationResult()
        if self.should_fail:
            result.add_error(kwargs.get('field_name', 'field'), self.message)
        return result


class SimpleValidatedForm(ValidatedForm):
    """Test form with validation."""
    
    name = forms.CharField(max_length=100)
    age = forms.IntegerField()
    
    def setup_validators(self):
        self.add_validator('name', RequiredValidator())
        self.add_validator('name', LengthValidator(min_length=3))
        self.add_validator('age', RequiredValidator())


class ValidatedFormTests(unittest.TestCase):
    """Tests for ValidatedForm."""
    
    def test_valid_form(self):
        """Test validation with valid data."""
        form = SimpleValidatedForm(data={'name': 'John Doe', 'age': 30})
        self.assertTrue(form.is_valid())
        
    def test_invalid_name_length(self):
        """Test validation with name that's too short."""
        form = SimpleValidatedForm(data={'name': 'Jo', 'age': 30})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
    def test_missing_field(self):
        """Test validation with missing required field."""
        form = SimpleValidatedForm(data={'name': 'John'})
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)

    def test_multiple_validators(self):
        """Test that multiple validators work on the same field."""
        form = SimpleValidatedForm(data={'age': 30})  # Missing name
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class FormWithFormLevelValidator(ValidatedForm):
    """Test form with form-level validation."""
    
    name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    def setup_validators(self):
        self.add_validator('name', RequiredValidator())
        self.add_validator('password', RequiredValidator())
        self.add_validator('confirm_password', RequiredValidator())
        
        def password_match(cleaned_data):
            result = ValidationResult()
            pwd = cleaned_data.get('password')
            confirm_pwd = cleaned_data.get('confirm_password')
            if pwd != confirm_pwd:
                result.add_error('confirm_password', 'Passwords do not match')
            return result
            
        self.add_form_validator(password_match)


class FormLevelValidationTests(unittest.TestCase):
    """Tests for form-level validation."""
    
    def test_matching_passwords(self):
        """Test form validation with matching passwords."""
        form = FormWithFormLevelValidator(data={
            'name': 'John',
            'password': 'secret123',
            'confirm_password': 'secret123'
        })
        self.assertTrue(form.is_valid())
        
    def test_mismatched_passwords(self):
        """Test form validation with mismatched passwords."""
        form = FormWithFormLevelValidator(data={
            'name': 'John',
            'password': 'secret123',
            'confirm_password': 'different'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
        error_msg = form.errors['confirm_password'][0]
        self.assertEqual(error_msg, 'Passwords do not match')

    def test_form_validator_returns_dict(self):
        """Test form validator returning a dictionary of errors."""
        class FormWithDictValidator(ValidatedForm):
            field_a = forms.CharField()

            def setup_validators(self):
                def dict_validator(cleaned_data):
                    if cleaned_data.get('field_a') == 'fail':
                        return {'field_a': ['Failed via dict.']}
                    return None  # Return None for valid case
                self.add_form_validator(dict_validator)

        # Test valid case
        form_valid = FormWithDictValidator(data={'field_a': 'ok'})
        self.assertTrue(form_valid.is_valid())

        # Test invalid case
        form_invalid = FormWithDictValidator(data={'field_a': 'fail'})
        self.assertFalse(form_invalid.is_valid())
        self.assertIn('field_a', form_invalid.errors)
        self.assertEqual(form_invalid.errors['field_a'][0],
                         'Failed via dict.')


class ValidatedFormMixinTests(unittest.TestCase):
    """Tests for ValidatedFormMixin methods."""
    
    def test_apply_validators(self):
        """Test the apply_validators method."""
        form = SimpleValidatedForm()
        
        # Test with valid data
        result = form.apply_validators('name', 'John Doe')
        self.assertFalse(result.has_errors())
        
        # Test with invalid data
        result = form.apply_validators('name', 'Jo')
        self.assertTrue(result.has_errors())
        self.assertIn('name', result.errors)
    
    def test_dynamic_clean_method(self):
        """Test that dynamic clean_field methods are created."""
        form = SimpleValidatedForm(data={'name': 'Jo', 'age': 30})
        
        # The form should have a clean_name method
        self.assertTrue(hasattr(form, 'clean_name'))
        
        # We need to initialize cleaned_data before calling the method
        form.cleaned_data = {'name': 'Jo', 'age': 30}
        
        # Calling the method should apply validators and raise ValidationError
        with self.assertRaises(forms.ValidationError):
            form.clean_name()

    def test_apply_validators_empty_result(self):
        """Test apply_validators with validators returning None or empty results."""
        class TestForm(ValidatedForm):
            field1 = forms.CharField()
            field2 = forms.CharField()

            def setup_validators(self):
                # Validator returning None
                self.add_validator('field1', lambda v, **k: None)
                # Validator returning empty ValidationResult
                self.add_validator('field2', lambda v, **k: ValidationResult())

        form = TestForm()
        result1 = form.apply_validators('field1', 'value')
        self.assertFalse(result1.has_errors())

        result2 = form.apply_validators('field2', 'value')
        self.assertFalse(result2.has_errors())

    def test_mixin_validate_method_valid(self):
        """Test the mixin's .validate() method with valid data."""
        form = SimpleValidatedForm() # Uses Required and Length validators
        data = {'name': 'Valid Name', 'age': 30}
        result = form.validate(data)
        self.assertFalse(result.has_errors())

    def test_mixin_validate_method_invalid_field(self):
        """Test the mixin's .validate() method with field validator errors."""
        form = SimpleValidatedForm()
        data = {'name': 'No', 'age': 30} # Name too short
        result = form.validate(data)
        self.assertTrue(result.has_errors())
        self.assertIn('name', result.errors)

    def test_mixin_validate_method_invalid_form(self):
        """Test the mixin's .validate() method with form validator errors."""
        form = FormWithFormLevelValidator() # Checks password match
        data = {
            'name': 'Test',
            'password': 'one',
            'confirm_password': 'two' # Mismatch
        }
        # Need to add field validators for this form instance
        form.add_validator('name', RequiredValidator())
        form.add_validator('password', RequiredValidator())
        form.add_validator('confirm_password', RequiredValidator())

        result = form.validate(data)
        self.assertTrue(result.has_errors())
        self.assertIn('confirm_password', result.errors)
        self.assertEqual(
            result.errors['confirm_password'][0], 'Passwords do not match'
        )

    def test_mixin_validate_method_no_validators(self):
        """Test .validate() when no validators are defined for a field."""
        class NoValidatorsForm(ValidatedForm):
            field_a = forms.CharField()

            # No setup_validators override

        form = NoValidatorsForm()
        data = {'field_a': 'some value'}
        result = form.validate(data)
        self.assertFalse(result.has_errors())  # Should be valid


# --- Tests for ValidatedModelForm ---

# Dummy model needed for ModelForm tests
# (models import is already at the top)

class DummyModel(models.Model):
    char_field = models.CharField(max_length=50)
    int_field = models.IntegerField()

    class Meta:
        app_label = 'core'  # Required for tests without a real app


# (ValidatedModelForm import is already at the top)

class SimpleValidatedModelForm(ValidatedModelForm):
    class Meta:
        model = DummyModel
        fields = ['char_field', 'int_field']

    def setup_validators(self):
        self.add_validator('char_field', RequiredValidator())
        self.add_validator(
            'int_field', RangeValidator(min_value=1, max_value=100)
        )

        # Add a form-level validator
        def check_fields_together(cleaned_data):
            result = ValidationResult()
            char_val = cleaned_data.get('char_field')
            int_val = cleaned_data.get('int_field', 0)
            if char_val == 'invalid' and int_val > 50:
                result.add_error('__all__', 'Invalid combination')
            return result
        self.add_form_validator(check_fields_together)


class ValidatedModelFormTests(unittest.TestCase):
    """Tests for ValidatedModelForm."""

    def test_model_form_valid(self):
        """Test ValidatedModelForm with valid data."""
        form = SimpleValidatedModelForm(data={'char_field': 'Valid', 'int_field': 50})
        self.assertTrue(form.is_valid())

    def test_model_form_invalid_field(self):
        """Test ValidatedModelForm with field validation error."""
        form = SimpleValidatedModelForm(
            data={'char_field': 'Valid', 'int_field': 101}  # Too high
        )
        self.assertFalse(form.is_valid())
        self.assertIn('int_field', form.errors)

    def test_model_form_invalid_form_level(self):
        """Test ValidatedModelForm with form-level validation error."""
        form = SimpleValidatedModelForm(
            data={'char_field': 'invalid', 'int_field': 60}  # Invalid combo
        )
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], 'Invalid combination')

    def test_model_form_save(self):
        """Test saving a valid ValidatedModelForm."""
        form = SimpleValidatedModelForm(
            data={'char_field': 'SaveMe', 'int_field': 42}
        )
        self.assertTrue(form.is_valid())
        # Use commit=False as we don't have a real DB connection configured
        # here easily.
        instance = form.save(commit=False)
        self.assertIsInstance(instance, DummyModel)
        self.assertEqual(instance.char_field, 'SaveMe')
        self.assertEqual(instance.int_field, 42)


class ComplexValidatedForm(ValidatedForm):
    """Test form with multiple validation types."""
    
    email = forms.EmailField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    quantity = forms.IntegerField()
    category = forms.ChoiceField(choices=[
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books')
    ])
    
    def setup_validators(self):
        # Email validation
        self.add_validator('email', RequiredValidator(
            error_message="Email is required"
        ))
        self.add_validator('email', RegexValidator(
            r'^[\w.+-]+@[\w-]+\.[\w.-]+$',
            error_message="Please enter a valid email address"
        ))
        
        # Price validation
        self.add_validator('price', DecimalValidator(
            max_digits=10, 
            decimal_places=2,
            error_message=(
                "Price must be a valid amount with at most 2 decimal places")
        ))
        self.add_validator('price', RangeValidator(
            min_value=0.01,
            max_value=9999.99,
            error_message="Price must be between $0.01 and $9,999.99")
        )

        # Quantity validation
        self.add_validator('quantity', RequiredValidator(
            error_message="Quantity is required"
        ))
        self.add_validator('quantity', RangeValidator(
            min_value=1,
            max_value=100,
            error_message="Quantity must be between 1 and 100")
        )

        # Category validation
        self.add_validator('category', ChoiceValidator(
            choices=['electronics', 'clothing', 'books'],
            error_message="Please select a valid category")
        )


class ComplexValidationTests(unittest.TestCase):
    """Tests for various validator types."""
    
    def test_valid_complex_form(self):
        """Test complex form with valid data."""
        form = ComplexValidatedForm(data={
            'email': 'user@example.com',
            'price': '99.99',
            'quantity': 5,
            'category': 'electronics'
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_email(self):
        """Test validation with invalid email."""
        form = ComplexValidatedForm(data={
            'email': 'not-an-email',
            'price': '99.99',
            'quantity': 5,
            'category': 'electronics'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        # Django's built-in validation error message for email field
        self.assertIn('Gib eine gültige E-Mail Adresse an.',
                      form.errors['email'][0])

    def test_invalid_price_format(self):
        """Test validation with invalid price format."""
        form = ComplexValidatedForm(data={
            'email': 'user@example.com',
            'price': 'not-a-price',
            'quantity': 5,
            'category': 'electronics'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
    
    def test_price_out_of_range(self):
        """Test validation with price out of range."""
        form = ComplexValidatedForm(data={
            'email': 'user@example.com',
            'price': '10000.00',  # Over max
            'quantity': 5,
            'category': 'electronics'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertEqual(
            form.errors['price'][0],
            "Price must be between $0.01 and $9,999.99"
        )

        # Test below minimum
        form = ComplexValidatedForm(data={
            'email': 'user@example.com',
            'price': '0.00',  # Under min
            'quantity': 5,
            'category': 'electronics'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
    
    def test_quantity_out_of_range(self):
        """Test validation with quantity out of range."""
        form = ComplexValidatedForm(data={
            'email': 'user@example.com',
            'price': '99.99',
            'quantity': 101,  # Over max
            'category': 'electronics'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        self.assertEqual(
            form.errors['quantity'][0],
            "Quantity must be between 1 and 100"
        )

        # Test below minimum
        form = ComplexValidatedForm(data={
            'email': 'user@example.com',
            'price': '99.99',
            'quantity': 0,  # Under min
            'category': 'electronics'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
    
    def test_invalid_category(self):
        """Test validation with invalid category."""
        form = ComplexValidatedForm(data={
            'email': 'user@example.com',
            'price': '99.99',
            'quantity': 5,
            'category': 'not-a-category'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
        # Django's built-in validation error message for choice field should
        # contain the invalid value.
        self.assertTrue('not-a-category' in form.errors['category'][0])


class AdvancedValidatedForm(ValidatedForm):
    """Test form with advanced validation scenarios."""
    
    username = forms.CharField(max_length=100)
    website = forms.URLField(required=False)
    birthday = forms.DateField(required=False)
    agreement = forms.BooleanField()
    product_code = forms.CharField(max_length=10, required=False)
    
    def setup_validators(self):
        # Username validation with multiple requirements
        self.add_validator('username', RequiredValidator())
        self.add_validator('username', LengthValidator(min_length=4, max_length=20))
        self.add_validator('username', RegexValidator(
            r'^[a-zA-Z0-9_]+$',
            error_message=(
                "Username can only contain letters, numbers, and underscores")
        ))

        # Website validation - use standard URL validation
        # (Testing Django's built-in URLField validation)
        
        # Product code format validation (when provided)
        self.add_validator('product_code', RegexValidator(
            r'^[A-Z]{2}-\d{4}$',
            error_message="Product code must be in format XX-1234")
        )

        # Agreement must be checked
        self.add_validator('agreement', RequiredValidator(
            error_message="You must agree to the terms")
        )

        # Form-level validation: if birthday provided, must be reasonable
        def validate_birthday(cleaned_data):
            result = ValidationResult()
            from datetime import date, timedelta
            
            birthday = cleaned_data.get('birthday')
            if birthday and birthday > date.today():
                result.add_error('birthday', "Birthday cannot be in the future")
            elif birthday and birthday < date.today() - timedelta(days=365 * 120):
                result.add_error(
                    'birthday', "Please enter a reasonable birth date"
                )

            return result
            
        self.add_form_validator(validate_birthday)


class AdvancedValidationTests(unittest.TestCase):
    """Tests for advanced validation scenarios."""
    
    def test_valid_form(self):
        """Test with valid data."""
        from datetime import date
        
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123',
            'website': 'https://example.com',
            'birthday': date(1990, 1, 1),
            'agreement': True,
            'product_code': 'AB-1234'
        })
        self.assertTrue(form.is_valid())
    
    def test_username_validation(self):
        """Test username validation rules."""
        # Too short
        form = AdvancedValidatedForm(data={
            'username': 'abc',
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Invalid characters
        form = AdvancedValidatedForm(data={
            'username': 'user@name',
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn(
            "Username can only contain letters, numbers, and underscores",
            form.errors['username'][0]
        )

        # Too long
        form = AdvancedValidatedForm(data={
            'username': 'x' * 21,
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_invalid_url(self):
        """Test URL field validation."""
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123',
            'website': 'not-a-valid-url',
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)
    
    def test_future_birthday(self):
        """Test birthday validation (future date)."""
        from datetime import date, timedelta
        
        future_date = date.today() + timedelta(days=10)
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123',
            'birthday': future_date,
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('birthday', form.errors)
        self.assertEqual(
            "Birthday cannot be in the future", form.errors['birthday'][0]
        )

    def test_implausible_birthday(self):
        """Test birthday validation (extremely old)."""
        from datetime import date, timedelta
        
        old_date = date.today() - timedelta(days=365*150)
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123',
            'birthday': old_date,
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('birthday', form.errors)
        self.assertEqual(
            "Please enter a reasonable birth date", form.errors['birthday'][0]
        )

    def test_invalid_product_code(self):
        """Test product code validation."""
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123',
            'agreement': True,
            'product_code': 'invalid'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('product_code', form.errors)
        
        # Test empty product code (should be valid as field is optional)
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123',
            'agreement': True,
            'product_code': ''
        })
        self.assertTrue(form.is_valid())
    
    def test_agreement_required(self):
        """Test agreement checkbox is required."""
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123',
            'agreement': False
        })
        self.assertFalse(form.is_valid())
        self.assertIn('agreement', form.errors)
        
        # Not providing agreement field at all
        form = AdvancedValidatedForm(data={
            'username': 'valid_user123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('agreement', form.errors)


class ValidationPerformanceForm(ValidatedForm):
    """Form to test validation performance with a large number of validators."""
    
    field1 = forms.CharField(max_length=100)
    field2 = forms.CharField(max_length=100)
    field3 = forms.CharField(max_length=100)
    
    def setup_validators(self):
        # Add multiple validators to simulate complex form
        for i in range(1, 4):
            field_name = f'field{i}'
            self.add_validator(field_name, RequiredValidator())
            self.add_validator(
                field_name, LengthValidator(min_length=2, max_length=50)
            )
            self.add_validator(field_name, RegexValidator(r'^[a-zA-Z0-9 ]+$'))


class ValidationPerformanceTests(unittest.TestCase):
    """Tests for validation performance and edge cases."""
    
    def test_multiple_field_errors(self):
        """Test form with multiple fields having errors."""
        form = ValidationPerformanceForm(data={
            'field1': 'a',  # Too short
            'field2': 'valid',
            'field3': 'invalid@$#'  # Invalid characters
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Two fields should have errors
        self.assertIn('field1', form.errors)
        self.assertIn('field3', form.errors)
    
    def test_empty_form(self):
        """Test form with no data."""
        form = ValidationPerformanceForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)  # All fields should be required
    
    def test_validators_initialization(self):
        """Test that validators are properly initialized."""
        form = ValidationPerformanceForm()
        # Each field has 3 validators
        self.assertEqual(len(form.validators['field1']), 3)
        self.assertEqual(len(form.validators['field2']), 3)
        self.assertEqual(len(form.validators['field3']), 3)
        
        # Test validators are of correct types
        self.assertIsInstance(form.validators['field1'][0], RequiredValidator)
        self.assertIsInstance(form.validators['field1'][1], LengthValidator)
        self.assertIsInstance(form.validators['field1'][2], RegexValidator)


class RegistrationForm(ValidatedForm):
    """Realistic user registration form with validation."""
    
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    terms_accepted = forms.BooleanField()
    
    def setup_validators(self):
        # Username validation
        self.add_validator('username', RequiredValidator())
        self.add_validator('username', LengthValidator(min_length=3, max_length=30))
        self.add_validator('username', RegexValidator(
            r'^[a-zA-Z0-9_]+$',
            error_message=(
                "Username can only contain letters, numbers, and underscores")
        ))

        # Email validation
        self.add_validator('email', RequiredValidator())
        self.add_validator('email', RegexValidator(
            r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            error_message="Please enter a valid email address")
        )

        # Password validation
        self.add_validator('password', RequiredValidator())
        self.add_validator('password', LengthValidator(
            min_length=8,
            error_message="Password must be at least 8 characters long")
        )
        self.add_validator('password', RegexValidator(
            r'.*[A-Z].*',
            error_message="Password must contain at least one uppercase letter")
        )
        self.add_validator('password', RegexValidator(
            r'.*[a-z].*',
            error_message="Password must contain at least one lowercase letter")
        )
        self.add_validator('password', RegexValidator(
            r'.*[0-9].*',
            error_message="Password must contain at least one number")
        )

        # Terms acceptance
        self.add_validator('terms_accepted', RequiredValidator(
            error_message="You must accept the terms and conditions")
        )

        # Form-level validation
        def passwords_match(cleaned_data):
            result = ValidationResult()
            password = cleaned_data.get('password')
            confirm = cleaned_data.get('confirm_password')
            
            if password and confirm and password != confirm:
                result.add_error('confirm_password', "Passwords do not match")
                
            return result
            
        self.add_form_validator(passwords_match)


class RegistrationFormTests(unittest.TestCase):
    """Tests for user registration form."""
    
    def test_valid_registration(self):
        """Test registration with valid data."""
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'ValidPass123',
            'confirm_password': 'ValidPass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'terms_accepted': True
        })
        self.assertTrue(form.is_valid())
    
    def test_weak_password(self):
        """Test registration with weak password."""
        # Password without uppercase
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'terms_accepted': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Password without number
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'PasswordOnly',
            'confirm_password': 'PasswordOnly',
            'terms_accepted': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Password too short
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'Short1',
            'confirm_password': 'Short1',
            'terms_accepted': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
    
    def test_password_mismatch(self):
        """Test registration with mismatched passwords."""
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'ValidPass123',
            'confirm_password': 'DifferentPass123',
            'terms_accepted': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
        self.assertEqual(
            "Passwords do not match", form.errors['confirm_password'][0]
        )

    def test_invalid_username(self):
        """Test registration with invalid username."""
        form = RegistrationForm(data={
            'username': 'invalid user@123',
            'email': 'user@example.com',
            'password': 'ValidPass123',
            'confirm_password': 'ValidPass123',
            'terms_accepted': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
    def test_terms_not_accepted(self):
        """Test registration without accepting terms."""
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'ValidPass123',
            'confirm_password': 'ValidPass123',
            'terms_accepted': False
        })
        self.assertFalse(form.is_valid())
        self.assertIn('terms_accepted', form.errors)
        
    def test_multiple_validation_errors(self):
        """Test with multiple validation errors at once."""
        form = RegistrationForm(data={
            'username': 'x',  # Too short
            'email': 'invalid-email',  # Invalid email
            'password': 'weak',  # Too short, no uppercase, no number
            'confirm_password': 'different',  # Mismatch
            'terms_accepted': False  # Not accepted
        })
        self.assertFalse(form.is_valid())
        
        # Check that we have errors for all problematic fields
        error_fields = form.errors.keys()
        # At least 4 fields should have errors
        self.assertGreaterEqual(len(error_fields), 4)
        self.assertIn('username', error_fields)
        self.assertIn('email', error_fields)
        self.assertIn('password', error_fields)
        self.assertIn('terms_accepted', error_fields)


class ConditionalValidationForm(ValidatedForm):
    """Form with conditional validation rules."""
    
    payment_method = forms.ChoiceField(choices=[
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal')
    ])
    
    credit_card_number = forms.CharField(max_length=19, required=False)
    credit_card_expiry = forms.CharField(max_length=7, required=False)
    credit_card_cvv = forms.CharField(max_length=4, required=False)
    
    bank_account = forms.CharField(max_length=20, required=False)
    bank_routing = forms.CharField(max_length=9, required=False)
    
    paypal_email = forms.EmailField(required=False)
    
    def setup_validators(self):
        # Base validation for payment method
        self.add_validator('payment_method', RequiredValidator())
        self.add_validator('payment_method', ChoiceValidator(
            choices=['credit_card', 'bank_transfer', 'paypal']
        ))
        
        # Conditional validation based on payment method
        def validate_payment_details(cleaned_data):
            result = ValidationResult()
            payment_method = cleaned_data.get('payment_method')
            
            if payment_method == 'credit_card':
                # Credit card fields are required
                cc_number = cleaned_data.get('credit_card_number')
                cc_expiry = cleaned_data.get('credit_card_expiry')
                cc_cvv = cleaned_data.get('credit_card_cvv')
                
                if not cc_number:
                    result.add_error('credit_card_number', 'Credit card number is required')
                elif not any(char.isdigit() for char in cc_number):
                    result.add_error(
                        'credit_card_number',
                        'Credit card number must contain digits')
                    )

                if not cc_expiry:
                    result.add_error(
                        'credit_card_expiry', 'Expiry date is required'
                    )

                if not cc_cvv:
                    result.add_error('credit_card_cvv', 'CVV is required')
                elif not cc_cvv.isdigit():
                    result.add_error(
                        'credit_card_cvv', 'CVV must be numeric'
                    )

            elif payment_method == 'bank_transfer':
                # Bank fields are required
                bank_account = cleaned_data.get('bank_account')
                bank_routing = cleaned_data.get('bank_routing')
                
                if not bank_account:
                    result.add_error(
                        'bank_account', 'Bank account number is required'
                    )

                if not bank_routing:
                    result.add_error(
                        'bank_routing', 'Routing number is required'
                    )

            elif payment_method == 'paypal':
                # PayPal email is required
                paypal_email = cleaned_data.get('paypal_email')
                
                if not paypal_email:
                    result.add_error(
                        'paypal_email', 'PayPal email is required'
                    )

            return result
            
        self.add_form_validator(validate_payment_details)


class ConditionalValidationTests(unittest.TestCase):
    """Tests for conditional validation."""
    
    def test_credit_card_payment(self):
        """Test valid credit card payment."""
        form = ConditionalValidationForm(data={
            'payment_method': 'credit_card',
            'credit_card_number': '4111111111111111',
            'credit_card_expiry': '12/2025',
            'credit_card_cvv': '123'
        })
        self.assertTrue(form.is_valid())
    
    def test_missing_credit_card_details(self):
        """Test credit card payment with missing details."""
        form = ConditionalValidationForm(data={
            'payment_method': 'credit_card',
            'credit_card_number': '4111111111111111',
            # Missing expiry
            'credit_card_cvv': '123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('credit_card_expiry', form.errors)
        
        # Missing all credit card details
        form = ConditionalValidationForm(data={
            'payment_method': 'credit_card'
        })
        self.assertFalse(form.is_valid())
        # All three cc fields should have errors
        self.assertEqual(len(form.errors), 3)

    def test_bank_transfer_payment(self):
        """Test valid bank transfer payment."""
        form = ConditionalValidationForm(data={
            'payment_method': 'bank_transfer',
            'bank_account': '12345678901234',
            'bank_routing': '123456789'
        })
        self.assertTrue(form.is_valid())
    
    def test_missing_bank_details(self):
        """Test bank transfer with missing details."""
        form = ConditionalValidationForm(data={
            'payment_method': 'bank_transfer',
            # Missing both account and routing
        })
        self.assertFalse(form.is_valid())
        # Both bank fields should have errors
        self.assertEqual(len(form.errors), 2)

    def test_paypal_payment(self):
        """Test valid PayPal payment."""
        form = ConditionalValidationForm(data={
            'payment_method': 'paypal',
            'paypal_email': 'user@example.com'
        })
        self.assertTrue(form.is_valid())
    
    def test_missing_paypal_email(self):
        """Test PayPal payment with missing email."""
        form = ConditionalValidationForm(data={
            'payment_method': 'paypal'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('paypal_email', form.errors)
    
    def test_invalid_payment_method(self):
        """Test with invalid payment method."""
        form = ConditionalValidationForm(data={
            'payment_method': 'invalid_method'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('payment_method', form.errors)


class ValidationErrorMessageForm(ValidatedForm):
    """Form to test custom error messages."""
    
    name = forms.CharField(max_length=100, required=False)
    age = forms.IntegerField(required=False)
    email = forms.EmailField(required=False)
    
    def setup_validators(self):
        self.add_validator('name', RequiredValidator(
            error_message="Please provide your name"
        ))
        self.add_validator('age', RangeValidator(
            min_value=18, 
            max_value=100,
            error_message="Age must be between {min_value} and {max_value}")
        )
        self.add_validator('email', RegexValidator(
            r'^[\w.+-]+@example\.com$',
            error_message="Email must be an @example.com address")
        )


class ValidationErrorMessageTests(unittest.TestCase):
    """Tests for custom error messages in validators."""
    
    def test_custom_required_message(self):
        """Test custom message for required field."""
        form = ValidationErrorMessageForm(data={
            'age': 25,
            'email': 'test@example.com'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertEqual(
            "Please provide your name", form.errors['name'][0]
        )

    def test_custom_range_message(self):
        """Test custom message for range validation."""
        form = ValidationErrorMessageForm(data={
            'name': 'John',
            'age': 15,  # Below minimum
            'email': 'test@example.com'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)
        self.assertEqual(
            "Age must be between 18 and 100", form.errors['age'][0]
        )

    def test_custom_regex_message(self):
        """Test custom message for regex validation."""
        form = ValidationErrorMessageForm(data={
            'name': 'John',
            'age': 25,
            'email': 'test@gmail.com'  # Not example.com
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(
            "Email must be an @example.com address", form.errors['email'][0]
        )


class ValidationErrorHandlingForm(ValidatedForm):
    """Form to test error handling scenarios."""
    
    field = forms.CharField()
    
    def setup_validators(self):
        # Add a validator that will raise an exception
        def problematic_validator(value, **kwargs):
            if value == 'trigger_error':
                # Simulate a validator with a bug
                raise RuntimeError("Validator error")
            result = ValidationResult()
            return result
        
        self.add_validator('field', problematic_validator)
        
        # Add a form validator that will raise an exception
        def problematic_form_validator(cleaned_data):
            if cleaned_data.get('field') == 'trigger_form_error':
                # Simulate a form validator with a bug
                raise ValueError("Form validator error")
            result = ValidationResult()
            return result
            
        self.add_form_validator(problematic_form_validator)
        
    # Override apply_validators to catch exceptions
    def apply_validators(self, field_name, value):
        try:
            return super().apply_validators(field_name, value)
        except Exception as e:
            result = ValidationResult()
            result.add_error(field_name, f"Validation error: {str(e)}")
            return result
            
    # Override apply_form_validators to catch exceptions
    def apply_form_validators(self, cleaned_data):
        try:
            return super().apply_form_validators(cleaned_data)
        except Exception as e:
            result = ValidationResult()
            result.add_error('__all__', f"Form validation error: {str(e)}")
            return result


class EmptyStringValidationForm(ValidatedForm):
    """Form to test validation of empty strings vs None."""
    
    required_field = forms.CharField()
    optional_field = forms.CharField(required=False)
    
    def setup_validators(self):
        # Required field should not be empty
        self.add_validator('required_field', RequiredValidator())
        
        # Optional field validation when provided
        self.add_validator('optional_field', LengthValidator(
            min_length=2,
            error_message="If provided, must be at least 2 characters"
        ))


class EmptyStringValidationTests(unittest.TestCase):
    """Tests for validation of empty strings vs None."""
    
    def test_required_field_empty_string(self):
        """Test empty string in required field."""
        form = EmptyStringValidationForm(data={
            'required_field': '',
            'optional_field': 'valid'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('required_field', form.errors)
    
    def test_optional_field_empty_string(self):
        """Test empty string in optional field."""
        form = EmptyStringValidationForm(data={
            'required_field': 'valid',
            'optional_field': ''
        })
        # Empty string should pass since field is optional
        self.assertTrue(form.is_valid())
    
    def test_optional_field_too_short(self):
        """Test too short value in optional field."""
        form = EmptyStringValidationForm(data={
            'required_field': 'valid',
            'optional_field': 'x'  # Too short when provided
        })
        self.assertFalse(form.is_valid())
        self.assertIn('optional_field', form.errors)
        self.assertEqual(
            "If provided, must be at least 2 characters",
            form.errors['optional_field'][0]
        )
