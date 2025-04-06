"""
Tests for the integration between views and the form validation framework.

This module tests that forms using our validation framework work correctly
when processed by views, ensuring that validation errors are properly
handled and returned to the user.
"""

import json
import unittest
from unittest.mock import patch
from django.test import RequestFactory
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from pyerp.core.form_validation import ValidatedForm
from pyerp.core.validators import (
    ValidationResult,
    RequiredValidator,
    RegexValidator,
    RangeValidator,
    ChoiceValidator,
)


# Test form for view integration
class UserRegistrationForm(ValidatedForm):
    """User registration form with various validations."""
    
    def setup_validators(self):
        # Username validation
        self.add_validator('username', RequiredValidator(
            error_message="Username is required"
        ))
        self.add_validator('username', RegexValidator(
            r'^[a-zA-Z0-9_]+$',
            error_message="Username can only contain letters, numbers, and underscores"
        ))
        
        # Email validation
        self.add_validator('email', RequiredValidator(
            error_message="Email is required"
        ))
        self.add_validator('email', RegexValidator(
            r'^[\w.+-]+@[\w-]+\.[\w.-]+$',
            error_message="Please enter a valid email address"
        ))
        
        # Password validation
        self.add_validator('password', RequiredValidator(
            error_message="Password is required"
        ))
        self.add_validator('password', RegexValidator(
            r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            error_message="Password must be at least 8 characters with at least one letter and one number"
        ))
        
        # User type validation
        self.add_validator('user_type', ChoiceValidator(
            choices=['customer', 'supplier', 'staff'],
            error_message="Please select a valid user type"
        ))
        
        # Form-level validation for password confirmation
        def password_match(cleaned_data):
            result = ValidationResult()
            password = cleaned_data.get('password')
            confirm_password = cleaned_data.get('confirm_password')
            
            if password and confirm_password and password != confirm_password:
                result.add_error('confirm_password', 'Passwords do not match')
            
            return result
        
        self.add_form_validator(password_match)
    
    # Override validate to apply field validators
    def validate(self, data):
        """Apply all field validators for manual validation."""
        result = ValidationResult()
        
        # Apply field validators manually
        for field_name, value in data.items():
            if field_name in self.validators:
                for validator in self.validators[field_name]:
                    validator_result = validator(value, field_name=field_name)
                    result.merge(validator_result)
        
        # Apply form validators as well
        if not result.has_errors():
            form_result = self.apply_form_validators(data)
            result.merge(form_result)
            
        return result


# A simpler view for testing that directly accepts form data
class SimpleUserRegistrationView(View):
    """Simple view for user registration that doesn't need request.body."""
    
    def post(self, request, form_data):
        """Process registration form data."""
        try:
            form = UserRegistrationForm(form_data)
            
            # Manual validation
            validation_result = form.validate(form_data)
            
            if validation_result.has_errors():
                # Return validation errors with 400 status
                return JsonResponse({
                    'success': False,
                    'errors': validation_result.errors
                }, status=400)
            else:
                # In a real view, we would create the user here
                return JsonResponse({
                    'success': True,
                    'message': 'User registered successfully'
                })
                
        except Exception as e:
            print(f"Error in view: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ViewFormIntegrationTests(unittest.TestCase):
    """Tests for view and form validation integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.view = SimpleUserRegistrationView().post
    
    def test_valid_form_submission(self):
        """Test valid form data is processed correctly."""
        # Prepare valid form data
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'user_type': 'customer'
        }
        
        # Create a dummy request (not actually used by our simplified view)
        request = {}
        
        # Process the form data directly
        response = self.view(request, form_data)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.assertEqual(content['message'], 'User registered successfully')
    
    def test_invalid_username(self):
        """Test validation for invalid username."""
        # Prepare form data with invalid username (contains special characters)
        form_data = {
            'username': 'test user@123',  # Contains spaces and special characters
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'user_type': 'customer'
        }
        
        # Create a dummy request (not actually used by our simplified view)
        request = {}
        
        # Process the form data directly
        response = self.view(request, form_data)
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('username', content['errors'])
        self.assertEqual(
            content['errors']['username'][0],
            "Username can only contain letters, numbers, and underscores"
        )
    
    def test_invalid_email(self):
        """Test validation for invalid email format."""
        # Prepare form data with invalid email
        form_data = {
            'username': 'testuser',
            'email': 'not-an-email',  # Invalid email format
            'password': 'password123',
            'confirm_password': 'password123',
            'user_type': 'customer'
        }
        
        # Create a dummy request (not actually used by our simplified view)
        request = {}
        
        # Process the form data directly
        response = self.view(request, form_data)
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('email', content['errors'])
    
    def test_password_mismatch(self):
        """Test validation for mismatched passwords."""
        # Prepare form data with password mismatch
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different123',  # Different from password
            'user_type': 'customer'
        }
        
        # Create a dummy request (not actually used by our simplified view)
        request = {}
        
        # Process the form data directly
        response = self.view(request, form_data)
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('confirm_password', content['errors'])
        self.assertEqual(content['errors']['confirm_password'][0], 'Passwords do not match')
    
    def test_invalid_user_type(self):
        """Test validation for invalid user type."""
        # Prepare form data with invalid user type
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'user_type': 'admin'  # Not in allowed choices
        }
        
        # Create a dummy request (not actually used by our simplified view)
        request = {}
        
        # Process the form data directly
        response = self.view(request, form_data)
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('user_type', content['errors'])
        self.assertEqual(
            content['errors']['user_type'][0],
            "Please select a valid user type"
        )
    
    def test_multiple_validation_errors(self):
        """Test multiple validation errors are returned correctly."""
        # Prepare form data with multiple validation issues
        form_data = {
            'username': 'test@user',  # Invalid username
            'email': 'not-an-email',  # Invalid email
            'password': 'short',  # Too short and missing number
            'confirm_password': 'different',  # Doesn't match
            'user_type': 'invalid'  # Invalid choice
        }
        
        # Create a dummy request (not actually used by our simplified view)
        request = {}
        
        # Process the form data directly
        response = self.view(request, form_data)
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        
        # Should have multiple error fields
        self.assertGreaterEqual(len(content['errors']), 3)
        self.assertIn('username', content['errors'])
        self.assertIn('email', content['errors'])
        self.assertIn('password', content['errors'])
        self.assertIn('user_type', content['errors'])


# Optional: Similar tests could be added for HTML form submission
# using Django's template system if needed 