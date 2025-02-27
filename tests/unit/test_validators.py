"""
Tests for the core validation framework.

This module contains tests for the validation classes and utilities.
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from pyerp.core.validators import (
    ValidationResult, Validator, RequiredValidator, RegexValidator,
    RangeValidator, LengthValidator, ChoiceValidator, CompoundValidator,
    BusinessRuleValidator, ImportValidator, validate_data, SkuValidator,
    DecimalValidator, ImportValidationError
)


class TestValidationResult:
    """Tests for the ValidationResult class."""

    def test_init(self):
        """Test initialization of ValidationResult."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == {}
        assert result.warnings == {}
        assert result.context == {}

    def test_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult()
        result.add_error('field1', 'Error 1')
        
        assert result.is_valid is False
        assert 'field1' in result.errors
        assert result.errors['field1'] == ['Error 1']
        
        # Add another error for the same field
        result.add_error('field1', 'Error 2')
        assert result.errors['field1'] == ['Error 1', 'Error 2']
        
        # Add error for a different field
        result.add_error('field2', 'Error 3')
        assert 'field2' in result.errors
        assert result.errors['field2'] == ['Error 3']

    def test_add_warning(self):
        """Test adding warnings to ValidationResult."""
        result = ValidationResult()
        result.add_warning('field1', 'Warning 1')
        
        assert result.is_valid is True  # Warnings don't affect validity
        assert 'field1' in result.warnings
        assert result.warnings['field1'] == ['Warning 1']
        
        # Add another warning for the same field
        result.add_warning('field1', 'Warning 2')
        assert result.warnings['field1'] == ['Warning 1', 'Warning 2']

    def test_merge(self):
        """Test merging two ValidationResults."""
        result1 = ValidationResult()
        result1.add_error('field1', 'Error 1')
        result1.add_warning('field2', 'Warning 1')
        result1.context['key1'] = 'value1'
        
        result2 = ValidationResult()
        result2.add_error('field3', 'Error 2')
        result2.add_warning('field4', 'Warning 2')
        result2.context['key2'] = 'value2'
        
        result1.merge(result2)
        
        assert result1.is_valid is False
        assert result1.errors == {
            'field1': ['Error 1'],
            'field3': ['Error 2']
        }
        assert result1.warnings == {
            'field2': ['Warning 1'],
            'field4': ['Warning 2']
        }
        assert result1.context == {
            'key1': 'value1',
            'key2': 'value2'
        }

    def test_str(self):
        """Test string representation."""
        result = ValidationResult()
        assert str(result) == "Valid"
        
        result.add_error('field1', 'Error 1')
        assert str(result) == "Invalid: field1: Error 1"
        
        result.add_error('field2', 'Error 2')
        assert "field1: Error 1" in str(result)
        assert "field2: Error 2" in str(result)


class TestValidator:
    """Tests for the base Validator class."""

    def test_validator_interface(self):
        """Test that validators must implement _validate."""
        validator = Validator()
        
        # Base validator should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            validator("test")


class TestRequiredValidator:
    """Tests for RequiredValidator."""

    def test_valid_values(self):
        """Test validator with valid values."""
        validator = RequiredValidator()
        
        assert validator("test").is_valid
        assert validator(123).is_valid
        assert validator([1, 2, 3]).is_valid
        assert validator({"key": "value"}).is_valid

    def test_invalid_values(self):
        """Test validator with invalid values."""
        validator = RequiredValidator()
        
        assert not validator(None).is_valid
        assert not validator("").is_valid
        assert not validator([]).is_valid
        assert not validator({}).is_valid

    def test_custom_message(self):
        """Test with a custom error message."""
        custom_msg = "This field cannot be empty!"
        validator = RequiredValidator(message=custom_msg)
        
        result = validator("", field_name="test_field")
        assert not result.is_valid
        assert result.errors["test_field"] == [custom_msg]


class TestRegexValidator:
    """Tests for RegexValidator."""

    def test_valid_values(self):
        """Test validator with valid values."""
        validator = RegexValidator(r"^[A-Z]{3}\d{3}$")
        
        assert validator("ABC123").is_valid
        assert validator("XYZ789").is_valid

    def test_invalid_values(self):
        """Test validator with invalid values."""
        validator = RegexValidator(r"^[A-Z]{3}\d{3}$")
        
        assert not validator("abc123").is_valid  # lowercase
        assert not validator("AB123").is_valid   # too few letters
        assert not validator("ABCD123").is_valid # too many letters
        assert not validator("ABC12").is_valid   # too few digits
        assert not validator("ABC1234").is_valid # too many digits


class TestRangeValidator:
    """Tests for RangeValidator."""

    def test_min_value(self):
        """Test minimum value validation."""
        validator = RangeValidator(min_value=10)
        
        assert validator(10).is_valid
        assert validator(11).is_valid
        assert not validator(9).is_valid

    def test_max_value(self):
        """Test maximum value validation."""
        validator = RangeValidator(max_value=10)
        
        assert validator(10).is_valid
        assert validator(9).is_valid
        assert not validator(11).is_valid

    def test_min_and_max_value(self):
        """Test both min and max value validation."""
        validator = RangeValidator(min_value=5, max_value=10)
        
        assert validator(5).is_valid
        assert validator(7).is_valid
        assert validator(10).is_valid
        assert not validator(4).is_valid
        assert not validator(11).is_valid

    def test_non_numeric_value(self):
        """Test with non-numeric values."""
        validator = RangeValidator(min_value=5, max_value=10)
        
        result = validator("not a number", field_name="test_field")
        assert not result.is_valid
        assert "Value must be a number" in result.errors["test_field"][0]

    def test_skip_empty_values(self):
        """Test that empty values are skipped."""
        validator = RangeValidator(min_value=5, max_value=10)
        
        assert validator(None).is_valid
        assert validator("").is_valid
        assert validator("  ").is_valid


class TestDecimalValidator:
    """Tests for DecimalValidator."""

    def test_valid_decimal(self):
        """Test with valid decimal values."""
        validator = DecimalValidator(max_digits=5, decimal_places=2)
        
        assert validator(Decimal("123.45")).is_valid
        assert validator("123.45").is_valid
        assert validator(123.45).is_valid

    def test_invalid_precision(self):
        """Test with invalid precision."""
        validator = DecimalValidator(max_digits=5, decimal_places=2)
        
        # Too many total digits
        assert not validator(Decimal("1234.56")).is_valid
        
        # Too many decimal places
        assert not validator(Decimal("123.456")).is_valid

    def test_invalid_format(self):
        """Test with invalid formats."""
        validator = DecimalValidator(max_digits=5, decimal_places=2)
        
        result = validator("not a decimal", field_name="price")
        assert not result.is_valid
        assert "must be a valid decimal number" in result.errors["price"][0]


class TestSkuValidator:
    """Tests for SkuValidator."""

    def test_valid_skus(self):
        """Test with valid SKUs."""
        validator = SkuValidator()
        
        assert validator("ABC123").is_valid
        assert validator("A-1").is_valid
        assert validator("TEST-123").is_valid
        assert validator("TEST123").is_valid
        assert validator("AB.123").is_valid

    def test_invalid_skus(self):
        """Test with invalid SKUs."""
        validator = SkuValidator()
        
        # Cannot start with special characters
        assert not validator("-ABC123").is_valid
        assert not validator(".ABC123").is_valid
        
        # Cannot contain invalid characters
        assert not validator("ABC 123").is_valid  # space
        assert not validator("ABC/123").is_valid  # slash
        assert not validator("ABC&123").is_valid  # ampersand


class TestImportValidator:
    """Tests for ImportValidator."""

    class SampleImportValidator(ImportValidator):
        """Sample implementation for testing."""
        
        def validate_name(self, value, row_data, row_index=None):
            result = ValidationResult()
            
            if not value:
                result.add_error('name', "Name is required")
                return value, result
            
            if len(value) < 3:
                result.add_error('name', "Name must be at least 3 characters")
            
            return value.strip(), result
        
        def validate_age(self, value, row_data, row_index=None):
            result = ValidationResult()
            
            try:
                age = int(value)
                if age < 0:
                    result.add_error('age', "Age cannot be negative")
                elif age < 18:
                    result.add_warning('age', "Person is underage")
                
                return age, result
            except (ValueError, TypeError):
                result.add_error('age', "Age must be a number")
                return 0, result
        
        def _post_validate_row(self, row_data, result, row_index=None):
            # Add a sample cross-field validation
            if row_data.get('is_vip') and row_data.get('age', 0) < 21:
                result.add_error('is_vip', "VIP status requires age 21+")

    def test_validate_row_valid(self):
        """Test validating a valid row."""
        validator = self.SampleImportValidator()
        
        row_data = {
            'name': ' John Doe ',  # Has extra spaces, should be trimmed
            'age': '25',  # String, should be converted to int
            'is_vip': True
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is True
        assert validated_data['name'] == 'John Doe'  # Spaces trimmed
        assert validated_data['age'] == 25  # Converted to int
        assert validated_data['is_vip'] is True

    def test_validate_row_with_errors(self):
        """Test validating a row with errors."""
        validator = self.SampleImportValidator()
        
        row_data = {
            'name': 'Jo',  # Too short
            'age': 'not_a_number',
            'is_vip': True
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is False
        assert 'name' in result.errors
        assert 'Name must be at least 3 characters' in result.errors['name'][0]
        assert 'age' in result.errors
        assert 'Age must be a number' in result.errors['age'][0]

    def test_validate_row_with_warnings(self):
        """Test validating a row with warnings but no errors."""
        validator = self.SampleImportValidator()
        
        row_data = {
            'name': 'John Doe',
            'age': '17',  # Underage (warning)
            'is_vip': False
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is True  # Warnings don't affect validity
        assert 'age' in result.warnings
        assert 'Person is underage' in result.warnings['age'][0]

    def test_validate_row_with_strict_mode(self):
        """Test strict mode where warnings are treated as errors."""
        validator = self.SampleImportValidator(strict=True)
        
        row_data = {
            'name': 'John Doe',
            'age': '17',  # Underage (warning becomes error in strict mode)
            'is_vip': False
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is False  # In strict mode, warnings make it invalid
        assert 'age' in result.errors
        assert 'Warning treated as error' in result.errors['age'][0]

    def test_cross_field_validation(self):
        """Test cross-field validation rules."""
        validator = self.SampleImportValidator()
        
        row_data = {
            'name': 'John Doe',
            'age': '20',  # Under 21
            'is_vip': True  # VIP requires 21+
        }
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is False
        assert 'is_vip' in result.errors
        assert 'VIP status requires age 21+' in result.errors['is_vip'][0]


class TestCompoundValidator:
    """Tests for CompoundValidator."""

    def test_all_valid(self):
        """Test when all validators should pass."""
        validator = CompoundValidator([
            RequiredValidator(),
            LengthValidator(min_length=3, max_length=10)
        ])
        
        result = validator("test", field_name="name")
        assert result.is_valid

    def test_some_invalid_require_all(self):
        """Test when some validators fail and require_all_valid=True."""
        validator = CompoundValidator([
            RequiredValidator(),
            LengthValidator(min_length=5, max_length=10)
        ], require_all_valid=True)
        
        result = validator("test", field_name="name")  # Too short
        assert not result.is_valid
        assert "name" in result.errors

    def test_some_invalid_require_any(self):
        """Test when some validators pass and require_all_valid=False."""
        validator = CompoundValidator([
            RequiredValidator(),  # This passes
            RegexValidator(r"^\d+$")  # This fails (not digits)
        ], require_all_valid=False)
        
        result = validator("test", field_name="value")
        assert result.is_valid  # Only one needed to pass

    def test_all_invalid_require_any(self):
        """Test when all validators fail and require_all_valid=False."""
        validator = CompoundValidator([
            LengthValidator(min_length=5),  # This fails (too short)
            RegexValidator(r"^\d+$")  # This fails (not digits)
        ], require_all_valid=False)
        
        result = validator("test", field_name="value")
        assert not result.is_valid  # All failed


def test_validate_data_utility():
    """Test the validate_data utility function."""
    validators = [
        RequiredValidator(),
        LengthValidator(min_length=3)
    ]
    
    # Valid data
    result = validate_data("test", validators, {"field_name": "name"})
    assert result.is_valid
    
    # Invalid data
    result = validate_data("", validators, {"field_name": "name"})
    assert not result.is_valid
    assert "name" in result.errors 