"""
Tests for the validator framework.

This module tests the functionality of the validator framework in
pyerp/core/validators.py, ensuring that validators work correctly with various
types of input data.
"""

import unittest
import re

from pyerp.core.validators import (
    ValidationResult,
    RequiredValidator,
    RegexValidator,
    RangeValidator,
    LengthValidator,
    ChoiceValidator,
    DecimalValidator,
    Validator,
    ImportValidationError,
    SkipRowException,
)


class ValidationResultTests(unittest.TestCase):
    """Tests for the ValidationResult class."""

    def test_initialization(self):
        """Test initialization of ValidationResult."""
        result = ValidationResult()
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, {})
        self.assertEqual(result.warnings, {})
        self.assertEqual(result.context, {})

    def test_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult()
        result.add_error("name", "Name is required")
        
        # Check if error was added
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors, {"name": ["Name is required"]})
        
        # Add another error for the same field
        result.add_error("name", "Name is too short")
        self.assertEqual(
            result.errors, {"name": ["Name is required", "Name is too short"]}
        )
        
        # Add error for a different field
        result.add_error("age", "Age must be positive")
        self.assertEqual(
            result.errors, 
            {
                "name": ["Name is required", "Name is too short"],
                "age": ["Age must be positive"]
            }
        )

    def test_add_warning(self):
        """Test adding warnings to ValidationResult."""
        result = ValidationResult()
        result.add_warning("password", "Password is weak")
        
        # Warnings don't affect validity
        self.assertTrue(result.is_valid)
        self.assertEqual(result.warnings, {"password": ["Password is weak"]})

    def test_merge(self):
        """Test merging two ValidationResults."""
        result1 = ValidationResult()
        result1.add_error("name", "Name is required")
        result1.add_warning("age", "Age is high")
        result1.context["user_id"] = 123
        
        result2 = ValidationResult()
        result2.add_error("email", "Email is invalid")
        result2.add_warning("password", "Password is weak")
        result2.context["session_id"] = "abc123"
        
        # Merge result2 into result1
        result1.merge(result2)
        
        # Check that errors, warnings and context were merged
        self.assertFalse(result1.is_valid)
        self.assertEqual(
            result1.errors, 
            {"name": ["Name is required"], "email": ["Email is invalid"]}
        )
        self.assertEqual(
            result1.warnings, 
            {"age": ["Age is high"], "password": ["Password is weak"]}
        )
        self.assertEqual(
            result1.context, {"user_id": 123, "session_id": "abc123"}
        )

    def test_has_errors(self):
        """Test has_errors method."""
        result = ValidationResult()
        self.assertFalse(result.has_errors())
        
        result.add_error("name", "Name is required")
        self.assertTrue(result.has_errors())

    def test_str_representation(self):
        """Test string representation of ValidationResult."""
        result = ValidationResult()
        self.assertEqual(str(result), "Valid")
        
        result.add_error("name", "Name is required")
        self.assertEqual(str(result), "Invalid: name: Name is required")
        
        result.add_error("age", "Age must be positive")
        # Order might vary, so check contents rather than exact string
        self.assertIn("name: Name is required", str(result))
        self.assertIn("age: Age must be positive", str(result))


class RequiredValidatorTests(unittest.TestCase):
    """Tests for the RequiredValidator class."""
    
    def test_empty_values(self):
        """Test validation with empty values."""
        validator = RequiredValidator()
        
        # Test None
        result = validator(None, field_name="name")
        self.assertTrue(result.has_errors())
        self.assertEqual(result.errors["name"][0], "This field is required")
        
        # Test empty string
        result = validator("", field_name="name")
        self.assertTrue(result.has_errors())
        
        # Test empty list
        result = validator([], field_name="items")
        self.assertTrue(result.has_errors())
        
        # Test empty dict
        result = validator({}, field_name="data")
        self.assertTrue(result.has_errors())

    def test_non_empty_values(self):
        """Test validation with non-empty values."""
        validator = RequiredValidator()
        
        # Test non-empty string
        result = validator("John", field_name="name")
        self.assertFalse(result.has_errors())
        
        # Test non-empty list
        result = validator([1, 2, 3], field_name="items")
        self.assertFalse(result.has_errors())
        
        # Test non-empty dict
        result = validator({"key": "value"}, field_name="data")
        self.assertFalse(result.has_errors())
        
        # Test zero (should be valid)
        result = validator(0, field_name="count")
        self.assertFalse(result.has_errors())
        
        # Test False (should be valid)
        result = validator(False, field_name="active")
        self.assertFalse(result.has_errors())

    def test_custom_message(self):
        """Test RequiredValidator with custom error message."""
        validator = RequiredValidator(error_message="Field cannot be empty")
        result = validator(None, field_name="name")
        self.assertEqual(result.errors["name"][0], "Field cannot be empty")
        
        # Test backward-compatible message parameter
        validator = RequiredValidator(message="Please fill this field")
        result = validator(None, field_name="name")
        self.assertEqual(result.errors["name"][0], "Please fill this field")


class RegexValidatorTests(unittest.TestCase):
    """Tests for the RegexValidator class."""
    
    def test_matching_pattern(self):
        """Test validation with matching pattern."""
        # Email pattern validator
        email_validator = RegexValidator(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
        
        # Valid email
        result = email_validator("user@example.com", field_name="email")
        self.assertFalse(result.has_errors())

    def test_non_matching_pattern(self):
        """Test validation with non-matching pattern."""
        # Email pattern validator
        email_validator = RegexValidator(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
        
        # Invalid email
        result = email_validator("not-an-email", field_name="email")
        self.assertTrue(result.has_errors())
        self.assertIn("email", result.errors)

    def test_empty_values(self):
        """Test validation with empty values - should be skipped."""
        validator = RegexValidator(r"^\d+$")
        
        # None should be skipped
        result = validator(None, field_name="code")
        self.assertFalse(result.has_errors())
        
        # Empty string should be skipped
        result = validator("", field_name="code")
        self.assertFalse(result.has_errors())

    def test_non_string_values(self):
        """Test validation with non-string values."""
        # Digit-only validator
        validator = RegexValidator(r"^\d+$")
        
        # Numeric values should be converted to string
        result = validator(123, field_name="code")
        self.assertFalse(result.has_errors())
        
        # Object with __str__ method
        class TestObject:
            def __str__(self):
                return "123"
        
        result = validator(TestObject(), field_name="code")
        self.assertFalse(result.has_errors())

    def test_custom_message(self):
        """Test RegexValidator with custom error message."""
        validator = RegexValidator(
            r"^\d{5}$", 
            error_message="Please enter a 5-digit ZIP code"
        )
        result = validator("12345", field_name="zip")
        self.assertFalse(result.has_errors())
        
        result = validator("1234", field_name="zip")
        self.assertTrue(result.has_errors())
        self.assertEqual(
            result.errors["zip"][0], "Please enter a 5-digit ZIP code"
        )


class RangeValidatorTests(unittest.TestCase):
    """Tests for the RangeValidator class."""

    def test_in_range_value(self):
        """Test validation with values in range."""
        # Age validator (0-120)
        validator = RangeValidator(min_value=0, max_value=120)
        
        # Test values in range
        result = validator(0, field_name="age")
        self.assertFalse(result.has_errors())
        
        result = validator(50, field_name="age")
        self.assertFalse(result.has_errors())
        
        result = validator(120, field_name="age")
        self.assertFalse(result.has_errors())
        
        # Test string value (should be converted)
        result = validator("75", field_name="age")
        self.assertFalse(result.has_errors())

    def test_out_of_range_value(self):
        """Test validation with values out of range."""
        # Age validator (0-120)
        validator = RangeValidator(min_value=0, max_value=120)
        
        # Test values out of range
        result = validator(-1, field_name="age")
        self.assertTrue(result.has_errors())
        
        result = validator(121, field_name="age")
        self.assertTrue(result.has_errors())

    def test_min_only(self):
        """Test RangeValidator with only min_value."""
        validator = RangeValidator(min_value=18)
        
        # Test values
        result = validator(17, field_name="age")
        self.assertTrue(result.has_errors())
        
        result = validator(18, field_name="age")
        self.assertFalse(result.has_errors())
        
        result = validator(999, field_name="age")
        self.assertFalse(result.has_errors())

    def test_max_only(self):
        """Test RangeValidator with only max_value."""
        validator = RangeValidator(max_value=100)
        
        # Test values
        result = validator(100, field_name="percentage")
        self.assertFalse(result.has_errors())
        
        result = validator(101, field_name="percentage")
        self.assertTrue(result.has_errors())
        
        result = validator(-50, field_name="percentage")
        self.assertFalse(result.has_errors())

    def test_non_numeric_value(self):
        """Test validation with non-numeric values."""
        validator = RangeValidator(min_value=0, max_value=100)
        
        # Test non-numeric value
        result = validator("not-a-number", field_name="percentage")
        self.assertTrue(result.has_errors())
        self.assertEqual(
            result.errors["percentage"][0], "Value must be a number"
        )

    def test_empty_values(self):
        """Test validation with empty values - should be skipped."""
        validator = RangeValidator(min_value=0, max_value=100)
        
        # None should be skipped
        result = validator(None, field_name="percentage")
        self.assertFalse(result.has_errors())
        
        # Empty string should be skipped
        result = validator("", field_name="percentage")
        self.assertFalse(result.has_errors())
        
        # Whitespace string should be skipped
        result = validator("   ", field_name="percentage")
        self.assertFalse(result.has_errors())

    def test_custom_message(self):
        """Test RangeValidator with custom error message."""
        validator = RangeValidator(
            min_value=18, 
            max_value=65,
            error_message="Age must be between {min_value} and {max_value}"
        )
        
        result = validator(17, field_name="age")
        self.assertTrue(result.has_errors())
        self.assertEqual(
            result.errors["age"][0], "Age must be between 18 and 65"
        )


class LengthValidatorTests(unittest.TestCase):
    """Tests for the LengthValidator class."""

    def test_valid_length(self):
        """Test validation with valid length values."""
        # Username validator (3-20 chars)
        validator = LengthValidator(min_length=3, max_length=20)
        
        # Test valid lengths
        result = validator("abc", field_name="username")
        self.assertFalse(result.has_errors())
        
        result = validator("user123", field_name="username")
        self.assertFalse(result.has_errors())
        
        result = validator("a" * 20, field_name="username")
        self.assertFalse(result.has_errors())

    def test_invalid_length(self):
        """Test validation with invalid length values."""
        # Username validator (3-20 chars)
        validator = LengthValidator(min_length=3, max_length=20)
        
        # Test too short
        result = validator("ab", field_name="username")
        self.assertTrue(result.has_errors())
        
        # Test too long
        result = validator("a" * 21, field_name="username")
        self.assertTrue(result.has_errors())

    def test_min_length_only(self):
        """Test LengthValidator with only min_length."""
        validator = LengthValidator(min_length=8)
        
        # Test too short
        result = validator("abc123", field_name="password")
        self.assertTrue(result.has_errors())
        
        # Test valid
        result = validator("abc12345", field_name="password")
        self.assertFalse(result.has_errors())
        
        result = validator("a" * 100, field_name="password")
        self.assertFalse(result.has_errors())

    def test_max_length_only(self):
        """Test LengthValidator with only max_length."""
        validator = LengthValidator(max_length=140)
        
        # Test valid
        result = validator("Short tweet", field_name="tweet")
        self.assertFalse(result.has_errors())
        
        # Test too long
        result = validator("a" * 141, field_name="tweet")
        self.assertTrue(result.has_errors())
        
        # Test empty string (should be valid)
        result = validator("", field_name="tweet")
        self.assertFalse(result.has_errors())

    def test_empty_values(self):
        """Test validation with empty values - should be skipped."""
        validator = LengthValidator(min_length=3, max_length=20)
        
        # None should be skipped
        result = validator(None, field_name="username")
        self.assertFalse(result.has_errors())
        
        # Empty string should be skipped
        result = validator("", field_name="username")
        self.assertFalse(result.has_errors())

    def test_non_string_values(self):
        """Test validation with non-string values."""
        validator = LengthValidator(min_length=2, max_length=3)
        
        # Test number (should be converted to string)
        result = validator(42, field_name="code")  # "42" has length 2
        self.assertFalse(result.has_errors())
        
        # Test list (should be converted to string)
        result = validator([1, 2], field_name="items")  # "[1, 2]" has length > 3
        self.assertTrue(result.has_errors())

    def test_custom_message(self):
        """Test LengthValidator with custom error message."""
        custom_msg = "Username must be between 3 and 20 characters"
        validator = LengthValidator(
            min_length=3, 
            max_length=20,
            error_message=custom_msg
        )
        
        result = validator("a", field_name="username")
        self.assertTrue(result.has_errors())
        self.assertEqual(result.errors["username"][0], custom_msg)


class ChoiceValidatorTests(unittest.TestCase):
    """Tests for the ChoiceValidator class."""
    
    def test_valid_choice(self):
        """Test validation with valid choices."""
        # Status validator
        status_choices = ["pending", "active", "inactive", "deleted"]
        validator = ChoiceValidator(choices=status_choices)
        
        # Test valid choices
        for status in status_choices:
            result = validator(status, field_name="status")
            self.assertFalse(result.has_errors())

    def test_invalid_choice(self):
        """Test validation with invalid choices."""
        # Status validator
        status_choices = ["pending", "active", "inactive", "deleted"]
        validator = ChoiceValidator(choices=status_choices)
        
        # Test invalid choice
        result = validator("unknown", field_name="status")
        self.assertTrue(result.has_errors())
        self.assertIn("status", result.errors)

    def test_empty_values(self):
        """Test validation with empty values - should be skipped."""
        validator = ChoiceValidator(choices=["yes", "no"])
        
        # None should be skipped
        result = validator(None, field_name="response")
        self.assertFalse(result.has_errors())
        
        # Empty string should be skipped
        result = validator("", field_name="response")
        self.assertFalse(result.has_errors())

    def test_custom_message(self):
        """Test ChoiceValidator with custom error message."""
        custom_msg = "Please select a valid payment method"
        validator = ChoiceValidator(
            choices=["credit", "debit", "paypal"],
            error_message=custom_msg
        )
        
        result = validator("bitcoin", field_name="payment_method")
        self.assertTrue(result.has_errors())
        self.assertEqual(
            result.errors["payment_method"][0], custom_msg
        )

    def test_non_string_choices(self):
        """Test ChoiceValidator with non-string choices."""
        # Numeric status codes
        status_codes = [100, 200, 404, 500]
        validator = ChoiceValidator(choices=status_codes)
        
        # Test valid numeric choice
        result = validator(200, field_name="status_code")
        self.assertFalse(result.has_errors())
        
        # Test invalid numeric choice
        result = validator(403, field_name="status_code")
        self.assertTrue(result.has_errors())
        
        # Test string that matches a numeric choice
        result = validator("200", field_name="status_code")
        self.assertTrue(result.has_errors())


class ExceptionTests(unittest.TestCase):
    """Tests for validator-related exceptions."""
    
    def test_import_validation_error(self):
        """Test ImportValidationError with single and multiple errors."""
        # Single error
        errors = {"name": ["Name is required"]}
        exc = ImportValidationError(errors)
        self.assertEqual(str(exc), "name: Name is required")
        
        # Multiple errors for one field
        errors = {"name": ["Name is required", "Name is too short"]}
        exc = ImportValidationError(errors)
        self.assertEqual(str(exc), "name: Name is required, Name is too short")
        
        # Multiple fields with errors
        errors = {
            "name": ["Name is required"],
            "email": ["Email is invalid"]
        }
        exc = ImportValidationError(errors)
        self.assertTrue(
            str(exc) == "name: Name is required; email: Email is invalid" or
            str(exc) == "email: Email is invalid; name: Name is required"
        )

    def test_skip_row_exception(self):
        """Test SkipRowException with and without reason."""
        # Without reason
        exc = SkipRowException()
        self.assertEqual(str(exc), "Row skipped")
        
        # With reason
        exc = SkipRowException("Invalid data format")
        self.assertEqual(str(exc), "Row skipped: Invalid data format") 