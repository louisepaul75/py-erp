"""
Tests for validator edge cases and boundary conditions.

This module tests the behavior of validators when handling edge cases,
boundary conditions and unusual inputs to ensure robust validation functionality.
"""

import unittest
from decimal import Decimal
import datetime

from pyerp.core.validators import (
    ValidationResult,
    RequiredValidator,
    LengthValidator,
    RegexValidator,
    RangeValidator,
    ChoiceValidator,
    DecimalValidator,
)


class EmptyValueTests(unittest.TestCase):
    """Tests for validators behavior with various empty value formats."""
    
    def setUp(self):
        """Set up test environment."""
        self.result = ValidationResult()
    
    def test_required_validator_with_empty_values(self):
        """Test RequiredValidator with different types of empty values."""
        validator = RequiredValidator(error_message="Required test")
        
        # Standard empty values
        empty_values = [None, "", [], {}]
        
        for value in empty_values:
            result = validator(value, field_name="test_field")
            self.assertTrue(
                result.has_errors(),
                f"Required validator should fail for empty value: {value}"
            )
            self.assertIn("test_field", result.errors)
            self.assertEqual(result.errors["test_field"][0], "Required test")
    
    def test_required_validator_with_falsy_values(self):
        """Test RequiredValidator with falsy but non-empty values."""
        validator = RequiredValidator(error_message="Required test")
        
        # Falsy but not empty values
        falsy_values = [0, False, 0.0, Decimal('0'), set()]
        
        for value in falsy_values:
            result = validator(value, field_name="test_field")
            self.assertFalse(result.has_errors())
    
    def test_other_validators_with_empty_values(self):
        """Test non-required validators with empty values (should skip validation)."""
        validators = [
            LengthValidator(min_length=5),
            RegexValidator(r'^[a-z]+$'),
            RangeValidator(min_value=1, max_value=10),
            ChoiceValidator(choices=["a", "b", "c"]),
            DecimalValidator(max_digits=5, decimal_places=2)
        ]
        
        empty_values = [None, ""]
        
        for validator in validators:
            for value in empty_values:
                result = validator(value, field_name="test_field")
                # Should skip validation for empty values
                self.assertFalse(result.has_errors())


class BoundaryValueTests(unittest.TestCase):
    """Tests for validators behavior at boundary values."""
    
    def test_length_validator_boundaries(self):
        """Test LengthValidator at exact boundary values."""
        min_validator = LengthValidator(min_length=5)
        max_validator = LengthValidator(max_length=10)
        range_validator = LengthValidator(min_length=5, max_length=10)
        
        # Exactly at minimum bound
        result = min_validator("12345", field_name="test_field")
        self.assertFalse(result.has_errors())
        
        # Just below minimum bound
        result = min_validator("1234", field_name="test_field")
        self.assertTrue(result.has_errors())
        
        # Exactly at maximum bound
        result = max_validator("1234567890", field_name="test_field")
        self.assertFalse(result.has_errors())
        
        # Just above maximum bound
        result = max_validator("12345678901", field_name="test_field")
        self.assertTrue(result.has_errors())
        
        # At both bounds (min and max)
        result = range_validator("12345", field_name="test_field")  # Minimum length
        self.assertFalse(result.has_errors())
        
        result = range_validator("1234567890", field_name="test_field")  # Maximum length
        self.assertFalse(result.has_errors())
    
    def test_range_validator_boundaries(self):
        """Test RangeValidator at exact boundary values."""
        validator = RangeValidator(min_value=5, max_value=10)
        
        # Exactly at minimum bound
        result = validator(5, field_name="test_field")
        self.assertFalse(result.has_errors())
        
        # Just below minimum bound
        result = validator(4.999, field_name="test_field")
        self.assertTrue(result.has_errors())
        
        # Exactly at maximum bound
        result = validator(10, field_name="test_field")
        self.assertFalse(result.has_errors())
        
        # Just above maximum bound
        result = validator(10.001, field_name="test_field")
        self.assertTrue(result.has_errors())
        
        # Testing with string representation of numbers
        result = validator("5", field_name="test_field")
        self.assertFalse(result.has_errors())
        
        result = validator("10", field_name="test_field")
        self.assertFalse(result.has_errors())
    
    def test_decimal_validator_boundaries(self):
        """Test DecimalValidator at precision boundaries."""
        # 5 digits total, 2 decimal places
        validator = DecimalValidator(max_digits=5, decimal_places=2)
        
        # Valid values
        valid_values = [
            "123.45",  # Exactly 5 digits with 2 decimal places
            "0.01",    # Minimum positive with 2 decimal places
            "-9.99",   # Negative with 2 decimal places
            123.45,    # Numeric input
            Decimal("123.45")  # Decimal input
        ]
        
        for value in valid_values:
            result = validator(value, field_name="test_field")
            self.assertFalse(result.has_errors())
        
        # Invalid values - too many total digits
        result = validator("1234.56", field_name="test_field")  # 6 digits total
        self.assertTrue(result.has_errors())
        
        # Invalid values - too many decimal places
        result = validator("12.345", field_name="test_field")  # 3 decimal places
        self.assertTrue(result.has_errors())


class EdgeCaseInputTests(unittest.TestCase):
    """Tests for validators with unusual or extreme inputs."""
    
    def test_regex_validator_with_special_patterns(self):
        """Test RegexValidator with special regex patterns and edge cases."""
        # Testing empty string regex
        empty_validator = RegexValidator(r'^$')
        result = empty_validator("", field_name="test_field")
        self.assertFalse(result.has_errors())
        
        result = empty_validator("not empty", field_name="test_field")
        self.assertTrue(result.has_errors())
        
        # Testing multi-line input
        multi_line_validator = RegexValidator(r'^.*$', error_message="Single line only")
        result = multi_line_validator("line1\nline2", field_name="test_field")
        self.assertTrue(result.has_errors())
        
        # Testing with Unicode characters using standard character classes
        unicode_validator = RegexValidator(r'^[\w\s]+$', error_message="Letters, numbers, and spaces only")
        result = unicode_validator("ñáéíóú äëïöü", field_name="test_field")
        self.assertFalse(result.has_errors())
        
        # Testing with very long input
        long_validator = RegexValidator(r'^[a-z]+$')
        long_input = "a" * 10000  # Very long string
        result = long_validator(long_input, field_name="test_field")
        self.assertFalse(result.has_errors())
    
    def test_choice_validator_with_edge_cases(self):
        """Test ChoiceValidator with edge case choices."""
        # Empty string as a valid choice
        validator = ChoiceValidator(choices=["", "option1", "option2"])
        
        result = validator("", field_name="test_field")
        self.assertFalse(result.has_errors())
        
        # Case sensitivity
        case_validator = ChoiceValidator(choices=["Option"])
        
        result = case_validator("option", field_name="test_field")
        self.assertTrue(result.has_errors())
        
        # Numeric and string choices
        mixed_validator = ChoiceValidator(choices=[1, "1", 2, "2"])
        
        result = mixed_validator(1, field_name="test_field")
        self.assertFalse(result.has_errors())
        
        result = mixed_validator("1", field_name="test_field")
        self.assertFalse(result.has_errors())
        
        # Choices containing None
        none_validator = ChoiceValidator(choices=[None, "option1"])
        
        result = none_validator(None, field_name="test_field")
        self.assertFalse(result.has_errors())


class ValidationErrorMessageTests(unittest.TestCase):
    """Tests for customizing and formatting validation error messages."""
    
    def test_custom_error_messages(self):
        """Test validators with custom error messages."""
        # Custom message for RequiredValidator
        req_validator = RequiredValidator(error_message="Custom required message")
        result = req_validator(None, field_name="test_field")
        self.assertEqual(result.errors["test_field"][0], "Custom required message")
        
        # Custom message for LengthValidator
        len_validator = LengthValidator(
            min_length=5, 
            max_length=10,
            error_message="Custom length message"
        )
        result = len_validator("1234", field_name="test_field")
        self.assertEqual(result.errors["test_field"][0], "Custom length message")
        
        # Custom message for RangeValidator
        range_validator = RangeValidator(
            min_value=5, 
            max_value=10,
            error_message="Custom range message"
        )
        result = range_validator(4, field_name="test_field")
        self.assertEqual(result.errors["test_field"][0], "Custom range message")
    
    def test_template_message_formatting(self):
        """Test RangeValidator with template variables in error messages."""
        validator = RangeValidator(
            min_value=5, 
            max_value=10,
            error_message="Value must be between {min_value} and {max_value}"
        )
        
        result = validator(4, field_name="test_field")
        error_msg = result.errors["test_field"][0]
        self.assertIn("5", error_msg)
        self.assertIn("10", error_msg)


class ComplexValidationTests(unittest.TestCase):
    """Tests for complex validation scenarios combining multiple validators."""
    
    def test_chained_validation(self):
        """Test validation where one field depends on another field."""
        # Password and confirm password validation
        password_validator = LengthValidator(min_length=8, error_message="Password too short")
        
        def confirm_password_validator(value, **kwargs):
            """Validator for password confirmation."""
            result = ValidationResult()
            field_name = kwargs.get('field_name', 'confirm_password')
            context = kwargs.get('context', {})
            
            password = context.get('password', '')
            if value != password:
                result.add_error(field_name, "Passwords do not match")
            
            return result
        
        # Test with matching passwords
        password_result = password_validator("password123", field_name="password")
        confirm_result = confirm_password_validator(
            "password123", 
            field_name="confirm_password",
            context={"password": "password123"}
        )
        
        self.assertFalse(password_result.has_errors())
        self.assertFalse(confirm_result.has_errors())
        
        # Test with non-matching passwords
        confirm_result = confirm_password_validator(
            "different123", 
            field_name="confirm_password",
            context={"password": "password123"}
        )
        
        self.assertTrue(confirm_result.has_errors())
        self.assertEqual(
            confirm_result.errors["confirm_password"][0], 
            "Passwords do not match"
        )
    
    def test_multiple_errors_same_field(self):
        """Test handling multiple validation errors on the same field."""
        # Create validation result
        result = ValidationResult()
        
        # Add multiple errors to the same field
        result.add_error("test_field", "Error 1")
        result.add_error("test_field", "Error 2")
        result.add_error("test_field", "Error 3")
        
        # Check that all errors are recorded
        self.assertEqual(len(result.errors["test_field"]), 3)
        self.assertIn("Error 1", result.errors["test_field"])
        self.assertIn("Error 2", result.errors["test_field"])
        self.assertIn("Error 3", result.errors["test_field"])


class ValidationResultTests(unittest.TestCase):
    """Tests for the ValidationResult class."""
    
    def test_merging_validation_results(self):
        """Test merging multiple ValidationResult instances."""
        # Create first result with some errors
        result1 = ValidationResult()
        result1.add_error("field1", "Error 1")
        result1.add_error("field2", "Error 2")
        
        # Create second result with different errors
        result2 = ValidationResult()
        result2.add_error("field2", "Error 3")
        result2.add_error("field3", "Error 4")
        
        # Create empty result for merging
        merged = ValidationResult()
        
        # Manually merge results
        for field, messages in result1.errors.items():
            for message in messages:
                merged.add_error(field, message)
                
        for field, messages in result2.errors.items():
            for message in messages:
                merged.add_error(field, message)
        
        # Check merged result
        self.assertEqual(len(merged.errors), 3)  # Three distinct fields
        self.assertEqual(len(merged.errors["field1"]), 1)
        self.assertEqual(len(merged.errors["field2"]), 2)
        self.assertEqual(len(merged.errors["field3"]), 1)
    
    def test_warnings_functionality(self):
        """Test adding and checking warnings in ValidationResult."""
        result = ValidationResult()
        
        # Add warnings
        result.add_warning("field1", "Warning 1")
        result.add_warning("field1", "Warning 2")
        result.add_warning("field2", "Warning 3")
        
        # Check warnings
        self.assertEqual(len(result.warnings), 2)  # Two distinct fields
        self.assertEqual(len(result.warnings["field1"]), 2)
        self.assertEqual(len(result.warnings["field2"]), 1)
        
        # Warnings should not affect validity
        self.assertTrue(result.is_valid)
        
        # Add an error
        result.add_error("field3", "Error 1")
        
        # Now it should be invalid
        self.assertFalse(result.is_valid)
        
        # But warnings should still be intact
        self.assertEqual(len(result.warnings), 2)
        self.assertEqual(len(result.warnings["field1"]), 2) 