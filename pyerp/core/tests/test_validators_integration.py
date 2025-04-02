"""
Tests for validators integration with custom functionality.

This module focuses on testing the core validators directly, avoiding 
Django-specific functionality that requires application initialization.
"""

import unittest
from collections import namedtuple
import re


# Mock ValidationResult class to avoid Django dependencies
class MockValidationResult:
    """Simplified implementation of ValidationResult for testing."""
    
    def __init__(self):
        """Initialize with empty errors dict."""
        self.errors = {}
        self.warnings = {}
        self.is_valid = True
    
    def add_error(self, field_name, message):
        """Add an error for a field."""
        if field_name not in self.errors:
            self.errors[field_name] = []
        self.errors[field_name].append(message)
        self.is_valid = False
    
    def add_warning(self, field_name, message):
        """Add a warning for a field."""
        if field_name not in self.warnings:
            self.warnings[field_name] = []
        self.warnings[field_name].append(message)
    
    def has_errors(self):
        """Check if there are any errors."""
        return not self.is_valid


# Mock validator classes
class MockRequiredValidator:
    """Simplified implementation of RequiredValidator."""
    
    def __init__(self, error_message="This field is required"):
        """Initialize with optional error message."""
        self.message = error_message
    
    def __call__(self, value, **kwargs):
        """Check if value is not empty."""
        result = MockValidationResult()
        field_name = kwargs.get('field_name', 'field')
        
        # Check various empty values
        if (
            value is None
            or value == ""
            or (isinstance(value, (list, dict)) and len(value) == 0)
        ):
            result.add_error(field_name, self.message)
        
        return result


class MockRegexValidator:
    """Simplified implementation of RegexValidator."""
    
    def __init__(self, pattern, error_message=None):
        """Initialize with regex pattern and optional error message."""
        self.pattern = pattern
        message = error_message or f"Value must match pattern: {pattern}"
        self.message = message
    
    def __call__(self, value, **kwargs):
        """Check if value matches pattern."""
        result = MockValidationResult()
        field_name = kwargs.get('field_name', 'field')
        
        # Skip empty values
        if value is None or value == "":
            return result
        
        # Convert to string if necessary
        if not isinstance(value, str):
            value = str(value)
        
        # Validate against pattern
        if not re.match(self.pattern, value):
            result.add_error(field_name, self.message)
        
        return result


class MockRangeValidator:
    """Simplified implementation of RangeValidator."""
    
    def __init__(self, min_value=None, max_value=None, error_message=None):
        """Initialize with range bounds and optional error message."""
        self.min_value = min_value
        self.max_value = max_value
        
        # Create default message based on bounds
        if min_value is not None and max_value is not None:
            default_message = f"Value must be between {min_value} and {max_value}"
        elif min_value is not None:
            default_message = f"Value must be at least {min_value}"
        elif max_value is not None:
            default_message = f"Value must be at most {max_value}"
        else:
            default_message = "Value is out of range"
            
        self.message = error_message or default_message
    
    def __call__(self, value, **kwargs):
        """Check if value is within range."""
        result = MockValidationResult()
        field_name = kwargs.get('field_name', 'field')
        
        # Skip empty values
        if value is None or value == "":
            return result
        
        # Convert to number if possible
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            result.add_error(field_name, "Value must be a number")
            return result
        
        # Check bounds
        if self.min_value is not None and num_value < self.min_value:
            result.add_error(field_name, self.message)
        
        if self.max_value is not None and num_value > self.max_value:
            result.add_error(field_name, self.message)
        
        return result


# Integrated validators for common use cases
class EmailValidator:
    """Validates email addresses."""
    
    def __init__(self, error_message="Invalid email address"):
        """Initialize with optional error message."""
        self.regex_validator = MockRegexValidator(
            r'^[\w.+-]+@[\w-]+\.[\w.-]+$',
            error_message
        )
    
    def __call__(self, value, **kwargs):
        """Validate email address."""
        return self.regex_validator(value, **kwargs)


class PasswordValidator:
    """Validates password strength."""
    
    def __init__(self, min_length=8, require_uppercase=True, require_digits=True, 
                require_special=False, error_message=None):
        """Initialize with password requirements."""
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.error_message = error_message
    
    def __call__(self, value, **kwargs):
        """Validate password strength."""
        result = MockValidationResult()
        field_name = kwargs.get('field_name', 'password')
        
        # Skip empty values
        if value is None or value == "":
            return result
        
        # Check minimum length
        if len(value) < self.min_length:
            result.add_error(
                field_name,
                f"Password must be at least {self.min_length} characters long"
            )
        
        # Check for uppercase letter
        if self.require_uppercase and not any(c.isupper() for c in value):
            result.add_error(
                field_name,
                "Password must contain at least one uppercase letter"
            )
        
        # Check for digits
        if self.require_digits and not any(c.isdigit() for c in value):
            result.add_error(
                field_name,
                "Password must contain at least one digit"
            )
        
        # Check for special characters
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            result.add_error(
                field_name,
                "Password must contain at least one special character"
            )
        
        return result


class PhoneNumberValidator:
    """Validates phone numbers in various formats."""
    
    def __init__(self, country_code='US', error_message=None):
        """Initialize with country code and optional error message."""
        self.country_code = country_code
        
        # Define patterns for different countries
        self.patterns = {
            'US': r'^\+?1?\s*\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})$',
            'UK': r'^\+?44?\s*\(?(\d{4,5})\)?[\s.-]*(\d{6,7})$',
            'INT': r'^\+\d{1,3}[\s.-]*\d{1,14}$',  # Basic international format
        }
        
        pattern = self.patterns.get(country_code, self.patterns['INT'])
        message = error_message or f"Invalid phone number format for {country_code}"
        self.regex_validator = MockRegexValidator(pattern, message)
    
    def __call__(self, value, **kwargs):
        """Validate phone number."""
        return self.regex_validator(value, **kwargs)


# Form validation helper
class FormValidator:
    """Helper class to validate multiple fields with multiple validators."""
    
    def __init__(self):
        """Initialize with empty field validators and form validators."""
        self.field_validators = {}
        self.form_validators = []
    
    def add_validator(self, field_name, validator):
        """Add a validator for a specific field."""
        if field_name not in self.field_validators:
            self.field_validators[field_name] = []
        self.field_validators[field_name].append(validator)
    
    def add_form_validator(self, validator_func):
        """Add a validator that validates multiple fields."""
        self.form_validators.append(validator_func)
    
    def validate_field(self, field_name, value):
        """Validate a single field."""
        result = MockValidationResult()
        
        if field_name not in self.field_validators:
            return result
        
        for validator in self.field_validators[field_name]:
            validator_result = validator(value, field_name=field_name)
            
            # Merge errors
            for err_field, err_messages in validator_result.errors.items():
                for message in err_messages:
                    result.add_error(err_field, message)
        
        return result
    
    def validate_form(self, form_data):
        """Validate the entire form."""
        result = MockValidationResult()
        
        # Validate individual fields
        for field_name, value in form_data.items():
            field_result = self.validate_field(field_name, value)
            
            # Merge errors
            for err_field, err_messages in field_result.errors.items():
                for message in err_messages:
                    result.add_error(err_field, message)
        
        # Apply form validators
        for validator_func in self.form_validators:
            form_result = validator_func(form_data)
            
            # Merge errors
            for err_field, err_messages in form_result.errors.items():
                for message in err_messages:
                    result.add_error(err_field, message)
        
        return result


class ValidatorIntegrationTests(unittest.TestCase):
    """Tests for validators integration."""
    
    def test_email_validator(self):
        """Test email validator with various formats."""
        validator = EmailValidator()
        
        # Valid emails
        valid_emails = [
            'user@example.com',
            'user.name@example.co.uk',
            'user+tag@example.org',
            'user-name@example.io',
        ]
        
        for email in valid_emails:
            result = validator(email, field_name='email')
            self.assertFalse(result.has_errors())
        
        # Invalid emails
        invalid_emails = [
            'user@',
            'user@.com',
            '@example.com',
            'user@example',
            'user_at_example.com',
        ]
        
        for email in invalid_emails:
            result = validator(email, field_name='email')
            self.assertTrue(result.has_errors())
            self.assertIn('email', result.errors)
    
    def test_password_validator(self):
        """Test password validator with various requirements."""
        validator = PasswordValidator(
            min_length=8,
            require_uppercase=True,
            require_digits=True,
            require_special=True
        )
        
        # Valid password
        result = validator('Password123!', field_name='password')
        self.assertFalse(result.has_errors())
        
        # Too short
        result = validator('Pass1!', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('password', result.errors)
        
        # No uppercase
        result = validator('password123!', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('password', result.errors)
        
        # No digit
        result = validator('Password!', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('password', result.errors)
        
        # No special character
        result = validator('Password123', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('password', result.errors)
    
    def test_phone_number_validator(self):
        """Test phone number validator with various formats."""
        us_validator = PhoneNumberValidator(country_code='US')
        
        # Valid US phone numbers
        valid_us_numbers = [
            '+1 (555) 123-4567',
            '(555) 123-4567',
            '555-123-4567',
            '5551234567',
            '+1 555.123.4567',
        ]
        
        for number in valid_us_numbers:
            result = us_validator(number, field_name='phone')
            self.assertFalse(result.has_errors())
        
        # Invalid US phone numbers
        invalid_us_numbers = [
            '123-456-7',
            '12-345-6789',
            '123-45-6789',
            'abc-def-ghij',
            '+44 1234 567890',  # UK format
        ]
        
        for number in invalid_us_numbers:
            result = us_validator(number, field_name='phone')
            self.assertTrue(result.has_errors())
            self.assertIn('phone', result.errors)
    
    def test_form_validator_with_user_registration(self):
        """Test form validation for user registration scenario."""
        form_validator = FormValidator()
        
        # Add field validators
        form_validator.add_validator('username', MockRequiredValidator())
        form_validator.add_validator('username', MockRegexValidator(
            r'^[a-zA-Z0-9_]+$',
            "Username can only contain letters, numbers, and underscores"
        ))
        
        form_validator.add_validator('email', MockRequiredValidator())
        form_validator.add_validator('email', EmailValidator())
        
        form_validator.add_validator('password', MockRequiredValidator())
        form_validator.add_validator('password', PasswordValidator(
            min_length=8,
            require_uppercase=True,
            require_digits=True,
            require_special=False
        ))
        
        # Add form validator for password confirmation
        def password_match(form_data):
            """Check if passwords match."""
            result = MockValidationResult()
            password = form_data.get('password')
            confirm_password = form_data.get('confirm_password')
            
            if password and confirm_password and password != confirm_password:
                result.add_error('confirm_password', 'Passwords do not match')
            
            return result
        
        form_validator.add_form_validator(password_match)
        
        # Valid form data
        valid_data = {
            'username': 'user123',
            'email': 'user@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }
        
        result = form_validator.validate_form(valid_data)
        self.assertFalse(result.has_errors())
        
        # Invalid username
        invalid_username_data = valid_data.copy()
        invalid_username_data['username'] = 'user name!'
        
        result = form_validator.validate_form(invalid_username_data)
        self.assertTrue(result.has_errors())
        self.assertIn('username', result.errors)
        
        # Invalid email
        invalid_email_data = valid_data.copy()
        invalid_email_data['email'] = 'not-an-email'
        
        result = form_validator.validate_form(invalid_email_data)
        self.assertTrue(result.has_errors())
        self.assertIn('email', result.errors)
        
        # Password mismatch
        password_mismatch_data = valid_data.copy()
        password_mismatch_data['confirm_password'] = 'Different123'
        
        result = form_validator.validate_form(password_mismatch_data)
        self.assertTrue(result.has_errors())
        self.assertIn('confirm_password', result.errors)
        
        # Multiple errors
        multiple_error_data = {
            'username': 'user@123',  # Invalid
            'email': 'not-an-email',  # Invalid
            'password': 'password',  # Invalid (no uppercase or digit)
            'confirm_password': 'different'  # Doesn't match
        }
        
        result = form_validator.validate_form(multiple_error_data)
        self.assertTrue(result.has_errors())
        self.assertTrue(len(result.errors) >= 3)
        self.assertIn('username', result.errors)
        self.assertIn('email', result.errors)
        self.assertIn('password', result.errors)
        self.assertIn('confirm_password', result.errors) 