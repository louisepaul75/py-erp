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
    EmailValidator,
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
        
        # Check if condition applies
        cleaned_data = kwargs.get('cleaned_data', {})
        if cleaned_data.get(self.condition_field) == self.condition_value:
            if not value:  # Simple validation: require value if condition met
                result.add_error(field_name, self.message)
                
        return result


class FormWithConditionalValidation(ValidatedForm):
    """Form with conditional validation logic."""
    
    user_type = forms.ChoiceField(
        choices=[('customer', 'Customer'), ('staff', 'Staff'), ('supplier', 'Supplier')],
        required=True
    )
    company_name = forms.CharField(max_length=100, required=False)
    tax_id = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=True)
    
    def setup_validators(self):
        self.add_validator('email', EmailValidator())
        
        # Conditional validation for company_name (required for suppliers)
        self.add_validator('company_name', 
                          ConditionalValidator('user_type', 'supplier', 
                                              'Company name is required for suppliers'))
        
        # Conditional validation for tax_id (required for suppliers and staff)
        def tax_id_validator(cleaned_data):
            result = ValidationResult()
            if cleaned_data.get('user_type') in ['supplier', 'staff']:
                if not cleaned_data.get('tax_id'):
                    result.add_error('tax_id', 'Tax ID is required for suppliers and staff')
            return result
            
        self.add_form_validator(tax_id_validator)


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
        self.add_validator('username', RequiredValidator())
        self.add_validator('username', LengthValidator(min_length=3, max_length=30))
        self.add_validator('email', EmailValidator())
    
    def clean_username(self):
        """Custom clean method for username."""
        username = self.cleaned_data.get('username', '')
        
        # Apply custom validation not covered by validators
        if username.lower() in ['admin', 'administrator', 'root', 'superuser']:
            raise ValidationError('This username is reserved')
            
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
        
    def test_validator_and_clean_method_interaction(self):
        """Test interaction between validators and clean methods."""
        form = CustomCleanMethodForm({
            'username': 'a',  # Too short (validator will catch)
            'email': 'admin@example.com'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('length', form.errors['username'][0].lower())
        
        # Now use "admin" (validator passes, clean method fails)
        form = CustomCleanMethodForm({
            'username': 'admin',  # Reserved name
            'email': 'admin@example.com'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('reserved', form.errors['username'][0].lower())
        
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