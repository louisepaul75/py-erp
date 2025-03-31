"""
Tests for the form validation module.

This module tests the functionality of the form validation framework in
pyerp/core/form_validation.py, ensuring that form validators work correctly
with Django forms.
"""

import unittest
from unittest.mock import patch  # Used in the cleaned_data mock setup

from django import forms

from pyerp.core.form_validation import ValidatedForm, ValidatedFormMixin
from pyerp.core.validators import (
    ValidationResult,
    RequiredValidator,
    LengthValidator,
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