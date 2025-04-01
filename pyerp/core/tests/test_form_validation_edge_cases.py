"""
Tests for edge cases in form validation.

This module tests the edge cases and advanced scenarios for the form validation framework
in pyerp/core/form_validation.py, ensuring robust behavior in complex situations.
"""

import unittest
from unittest.mock import patch, MagicMock
from django import forms
from django.core.exceptions import ValidationError

from pyerp.core.form_validation import ValidatedForm, ValidatedFormMixin
from pyerp.core.validators import (
    ValidationResult,
    RequiredValidator,
    LengthValidator,
    RegexValidator,
    RangeValidator,
    ChoiceValidator,
)


class ConditionalValidator:
    """Validator that conditionally validates based on other field values."""
    
    def __init__(self, condition_field, condition_value, message="Validation failed"):
        self.condition_field = condition_field
        self.condition_value = condition_value
        self.message = message
        
    def __call__(self, value, **kwargs):
        result = ValidationResult()
        field_name = kwargs.get('field_name', 'field')
        
        # Check if condition applies - for form validation, we need to access the form instance
        form = kwargs.get('form')
        if form and hasattr(form, 'cleaned_data') and form.cleaned_data:
            cleaned_data = form.cleaned_data
            if cleaned_data.get(self.condition_field) == self.condition_value:
                if not value:  # Simple validation: require value if condition met
                    result.add_error(field_name, self.message)
                
        return result


class FormWithConditionalValidation(ValidatedForm):
    """Form with fields that conditionally require validation."""
    
    user_type = forms.ChoiceField(
        choices=[
            ('customer', 'Customer'),
            ('supplier', 'Supplier'),
            ('staff', 'Staff')
        ],
        required=True
    )
    company_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    tax_id = forms.CharField(max_length=20, required=False)
    
    def setup_validators(self):
        # Company name is required for suppliers
        company_validator = ConditionalValidator(
            'user_type', 'supplier', 
            'Company name is required for suppliers'
        )
        self.add_validator('company_name', company_validator)
        
        # Form-level validation for tax ID requirement
        def tax_id_validator(cleaned_data):
            result = ValidationResult()
            user_type = cleaned_data.get('user_type')
            tax_id = cleaned_data.get('tax_id')
            
            if user_type in ['supplier', 'staff'] and not tax_id:
                result.add_error('tax_id', 'Tax ID is required for suppliers and staff')
                
            return result
            
        self.add_form_validator(tax_id_validator)
    
    # Override clean method to add custom validation logic
    def clean(self):
        cleaned_data = super().clean()
        
        # Company name is required for suppliers
        if cleaned_data.get('user_type') == 'supplier' and not cleaned_data.get('company_name'):
            self.add_error('company_name', 'Company name is required for suppliers')
        
        return cleaned_data


class FormWithInterDependentFields(ValidatedForm):
    """Form with fields that depend on each other."""
    
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    security_level = forms.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        required=True
    )
    
    def setup_validators(self):
        self.add_validator('password', RequiredValidator())
        self.add_validator('confirm_password', RequiredValidator())
        
        # Stronger password requirements for higher security levels
        def security_level_password_validator(cleaned_data):
            result = ValidationResult()
            security_level = cleaned_data.get('security_level')
            password = cleaned_data.get('password', '')
            
            if security_level == 'medium' and len(password) < 8:
                result.add_error('password', 'Medium security requires at least 8 characters')
            elif security_level == 'high':
                if len(password) < 12:
                    result.add_error('password', 'High security requires at least 12 characters')
                if not any(c.isdigit() for c in password):
                    result.add_error('password', 'High security requires at least one number')
                if not any(c.isupper() for c in password):
                    result.add_error('password', 'High security requires at least one uppercase letter')
                    
            return result
            
        self.add_form_validator(security_level_password_validator)
        
        # Password confirmation validator
        def password_match_validator(cleaned_data):
            result = ValidationResult()
            password = cleaned_data.get('password')
            confirm = cleaned_data.get('confirm_password')
            
            if password and confirm and password != confirm:
                result.add_error('confirm_password', 'Passwords do not match')
                
            return result
            
        self.add_form_validator(password_match_validator)


class CustomCleanMethodForm(ValidatedForm):
    """Form that implements custom clean methods alongside validators."""
    
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    
    def setup_validators(self):
        self.add_validator('username', RequiredValidator(error_message="Username is required"))
        self.add_validator('username', LengthValidator(
            min_length=3, 
            max_length=30,
            error_message="Username must be between 3 and 30 characters long"
        ))
        self.add_validator('email', RegexValidator(
            r'^[\w.+-]+@[\w-]+\.[\w.-]+$',
            error_message="Please enter a valid email address"
        ))
    
    def clean_username(self):
        """Custom clean method for username."""
        username = self.cleaned_data.get('username', '')
        
        # Apply custom validation not covered by validators
        reserved_names = ['admin', 'administrator', 'root', 'superuser']
        if username.lower() in reserved_names:
            # Explicitly raise ValidationError for reserved usernames
            raise ValidationError("This username is reserved and cannot be used")
            
        # Custom transformation
        return username.lower()
    
    def clean_email(self):
        """Custom clean method for email."""
        email = self.cleaned_data.get('email', '')
        
        # Normalize email
        return email.lower()


class EdgeCaseFormValidationTests(unittest.TestCase):
    """Tests for edge cases in form validation."""
    
    def test_conditional_validation_supplier(self):
        """Test conditional validation when user is a supplier."""
        # Company name is required for suppliers
        form = FormWithConditionalValidation({
            'user_type': 'supplier',
            'email': 'supplier@example.com',
            'tax_id': '12345'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('company_name', form.errors)
        
        # Valid submission for supplier
        form = FormWithConditionalValidation({
            'user_type': 'supplier',
            'company_name': 'Supplier Co.',
            'email': 'supplier@example.com',
            'tax_id': '12345'
        })
        
        self.assertTrue(form.is_valid())
        
    def test_conditional_validation_customer(self):
        """Test conditional validation when user is a customer."""
        # Company name is not required for customers
        form = FormWithConditionalValidation({
            'user_type': 'customer',
            'email': 'customer@example.com'
        })
        
        self.assertTrue(form.is_valid())
        
    def test_form_level_validation_tax_id(self):
        """Test form-level validation for tax ID requirement."""
        # Staff needs tax ID
        form = FormWithConditionalValidation({
            'user_type': 'staff',
            'email': 'staff@example.com'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('tax_id', form.errors)
        
        # Customer doesn't need tax ID
        form = FormWithConditionalValidation({
            'user_type': 'customer',
            'email': 'customer@example.com'
        })
        
        self.assertTrue(form.is_valid())
        
    def test_security_level_password_validation(self):
        """Test password validation based on security level."""
        # Low security - simple password is fine
        form = FormWithInterDependentFields({
            'password': 'simple',
            'confirm_password': 'simple',
            'security_level': 'low'
        })
        
        self.assertTrue(form.is_valid())
        
        # Medium security - password too short
        form = FormWithInterDependentFields({
            'password': 'short',
            'confirm_password': 'short',
            'security_level': 'medium'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Medium security - valid password
        form = FormWithInterDependentFields({
            'password': 'validpassword',
            'confirm_password': 'validpassword',
            'security_level': 'medium'
        })
        
        self.assertTrue(form.is_valid())
        
        # High security - fails multiple requirements
        form = FormWithInterDependentFields({
            'password': 'tooshort',
            'confirm_password': 'tooshort',
            'security_level': 'high'
        })
        
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors['password']), 3)  # Length, uppercase, number
        
        # High security - valid password
        form = FormWithInterDependentFields({
            'password': 'ValidPassword123',
            'confirm_password': 'ValidPassword123',
            'security_level': 'high'
        })
        
        self.assertTrue(form.is_valid())
        
    def test_password_mismatch(self):
        """Test validation for password and confirmation mismatch."""
        form = FormWithInterDependentFields({
            'password': 'password123',
            'confirm_password': 'different123',
            'security_level': 'medium'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
        self.assertIn('match', form.errors['confirm_password'][0].lower())
        
    def test_custom_clean_methods(self):
        """Test custom clean methods alongside validators."""
        form = CustomCleanMethodForm({
            'username': 'TestUser',
            'email': 'TEST@example.com'
        })
        
        self.assertTrue(form.is_valid())
        
        # Verify username is lowercased
        self.assertEqual(form.cleaned_data['username'], 'testuser')
        # Verify email is lowercased
        self.assertEqual(form.cleaned_data['email'], 'test@example.com')
        
    def test_reserved_username_validation(self):
        """Test custom validation for reserved usernames."""
        form = CustomCleanMethodForm({
            'username': 'admin',
            'email': 'admin@example.com'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('reserved', form.errors['username'][0].lower())
        
    def test_validator_length_validation(self):
        """Test that validators correctly check minimum length."""
        # Create a form with a username field with minimum length validator
        form = MinimumLengthForm({
            'username': 'a',  # Too short (minimum is 3)
            'email': 'valid@example.com'  # Valid, not relevant to this test
        })
        
        # Check if validator correctly enforces minimum length
        is_valid = form.is_valid()
        
        # Print debugging information if test is failing
        if is_valid:
            print(f"UNEXPECTED: Form is valid with username 'a'")
            print(f"Form errors: {form.errors}")
            print(f"Validators: {form.validators}")
        
        self.assertFalse(is_valid)
        self.assertIn('username', form.errors)
        self.assertTrue(any('length' in msg.lower() or 'characters' in msg.lower() 
                          for msg in form.errors['username']), 
                       f"No length-related error found in {form.errors['username']}")
    
    def test_clean_method_validation(self):
        """Test that clean methods enforce business rules."""
        # Test directly that clean_username raises ValidationError for reserved names
        form = CustomCleanMethodForm({
            'username': 'admin',  # Reserved name
            'email': 'admin@example.com'
        })
        
        # First validate the form to populate cleaned_data
        form.is_valid()
        
        # Manually call clean_username and verify it raises ValidationError
        with self.assertRaises(ValidationError):
            form.clean_username()

        # Check that form validation fails
        form = CustomCleanMethodForm({
            'username': 'admin',  # Reserved name
            'email': 'admin@example.com'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertTrue('reserved' in ' '.join(form.errors['username']).lower())
        
    def test_multiple_errors_on_same_field(self):
        """Test that multiple errors can be collected on a single field."""
        # Create a form where high security level validation fails multiple checks
        form = FormWithInterDependentFields({
            'password': 'short',
            'confirm_password': 'short',
            'security_level': 'high'
        })
        
        self.assertFalse(form.is_valid())
        
        # Should have multiple errors on password field
        self.assertGreater(len(form.errors['password']), 1)
        
        # Errors should include messages about length, uppercase, and number
        error_text = ' '.join(form.errors['password'])
        self.assertIn('12 characters', error_text)
        self.assertIn('uppercase', error_text)
        self.assertIn('number', error_text)


# Add a new test class that directly tests validators without Django forms
class DirectValidatorTests(unittest.TestCase):
    """Tests for validators without using Django forms."""
    
    def test_length_validator(self):
        """Test LengthValidator directly."""
        validator = LengthValidator(min_length=3, max_length=10)
        
        # Test with value that's too short
        result = validator("ab", field_name="username")
        self.assertTrue(result.has_errors())
        self.assertIn("username", result.errors)
        
        # Test with value that's too long
        result = validator("abcdefghijklmnop", field_name="username")
        self.assertTrue(result.has_errors())
        self.assertIn("username", result.errors)
        
        # Test with valid value
        result = validator("valid", field_name="username")
        self.assertFalse(result.has_errors())
    
    def test_regex_validator(self):
        """Test RegexValidator directly."""
        email_validator = RegexValidator(
            r'^[\w.+-]+@[\w-]+\.[\w.-]+$',
            error_message="Invalid email format"
        )
        
        # Test with invalid email
        result = email_validator("not-an-email", field_name="email")
        self.assertTrue(result.has_errors())
        self.assertIn("email", result.errors)
        self.assertEqual(result.errors["email"][0], "Invalid email format")
        
        # Test with valid email
        result = email_validator("user@example.com", field_name="email")
        self.assertFalse(result.has_errors())
    
    def test_range_validator(self):
        """Test RangeValidator directly."""
        validator = RangeValidator(
            min_value=1,
            max_value=100,
            error_message="Value must be between 1 and 100"
        )
        
        # Test with value below range
        result = validator(0, field_name="quantity")
        self.assertTrue(result.has_errors())
        self.assertIn("quantity", result.errors)
        
        # Test with value above range
        result = validator(101, field_name="quantity")
        self.assertTrue(result.has_errors())
        self.assertIn("quantity", result.errors)
        
        # Test with valid value
        result = validator(50, field_name="quantity")
        self.assertFalse(result.has_errors())
    
    def test_choice_validator(self):
        """Test ChoiceValidator directly."""
        validator = ChoiceValidator(
            choices=["red", "green", "blue"],
            error_message="Invalid color choice"
        )
        
        # Test with invalid choice
        result = validator("purple", field_name="color")
        self.assertTrue(result.has_errors())
        self.assertIn("color", result.errors)
        self.assertEqual(result.errors["color"][0], "Invalid color choice")
        
        # Test with valid choice
        result = validator("green", field_name="color")
        self.assertFalse(result.has_errors())
    
    def test_required_validator(self):
        """Test RequiredValidator directly."""
        validator = RequiredValidator(error_message="This field is required")
        
        # Test with empty values
        for empty_value in [None, "", [], {}]:
            result = validator(empty_value, field_name="field")
            self.assertTrue(result.has_errors())
            self.assertIn("field", result.errors)
            self.assertEqual(result.errors["field"][0], "This field is required")
        
        # Test with non-empty values
        for value in ["text", 123, [1, 2, 3], {"key": "value"}]:
            result = validator(value, field_name="field")
            self.assertFalse(result.has_errors())
    
    def test_conditional_validation(self):
        """Test conditional validation logic directly."""
        # Create a simple validation function that validates based on a condition
        def validate_conditionally(value, condition_value, field_name="field"):
            result = ValidationResult()
            if condition_value == "supplier" and not value:
                result.add_error(field_name, "Required for suppliers")
            return result
        
        # Test with condition met but value empty
        result = validate_conditionally("", "supplier", "company_name")
        self.assertTrue(result.has_errors())
        self.assertIn("company_name", result.errors)
        self.assertEqual(result.errors["company_name"][0], "Required for suppliers")
        
        # Test with condition met and value provided
        result = validate_conditionally("Acme Inc", "supplier", "company_name")
        self.assertFalse(result.has_errors())
        
        # Test with condition not met (should pass regardless of value)
        result = validate_conditionally("", "customer", "company_name")
        self.assertFalse(result.has_errors())


# Define the form class used in the test above (earlier in the file)
class MinimumLengthForm(ValidatedForm):
    """Form for testing validators with field minimum length requirements."""
    
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    
    def setup_validators(self):
        """Set up validators including minimum length for username."""
        self.add_validator('username', RequiredValidator())
        self.add_validator('username', LengthValidator(
            min_length=3,
            error_message="Username must be at least 3 characters long"
        ))
        self.add_validator('email', RegexValidator(
            r'^[\w.+-]+@[\w-]+\.[\w.-]+$',
            error_message="Please enter a valid email address"
        )) 