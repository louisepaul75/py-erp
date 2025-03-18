"""
Tests for the ImportValidator class in pyerp.core.validators.
"""

import pytest

from pyerp.core.validators import (
    ImportValidator,
    RequiredValidator,
    SkipRowException,
    ValidationResult,
)


class SimpleImportValidator(ImportValidator):
    """Simple implementation of ImportValidator for testing."""

    def validate_name(self, value, row_data, row_index=None):
        """Validate name field."""
        result = ValidationResult()
        if not value:
            result.add_error("name", "Name is required")
            return None, result
        return value, result

    def validate_age(self, value, row_data, row_index=None):
        """Validate age field."""
        result = ValidationResult()
        try:
            age = int(value)
            if age < 0:
                result.add_error("age", "Age cannot be negative")
                return None, result
            if age < 18:
                result.add_warning("age", "Person is under 18")
            return age, result
        except (ValueError, TypeError):
            result.add_error("age", "Invalid age format")
            return None, result

    def cross_validate_row(self, validated_data):
        """Cross-validate fields."""
        result = ValidationResult()
        if "name" in validated_data and "age" in validated_data:
            if validated_data["name"] == "Admin" and validated_data["age"] < 30:
                result.add_error("name", "Admin must be at least 30 years old")
        return result


class TestImportValidator:
    """Tests for the ImportValidator class."""

    def test_init(self):
        """Test initialization of ImportValidator."""
        validator = ImportValidator()
        assert validator.strict is False
        assert validator.transform_data is True

        validator = ImportValidator(strict=True, transform_data=False)
        assert validator.strict is True
        assert validator.transform_data is False

    def test_validate_row_success(self):
        """Test successful row validation."""
        validator = SimpleImportValidator()
        row_data = {"name": "John", "age": "25", "email": "john@example.com"}
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is True
        assert validated_data["name"] == "John"
        assert validated_data["age"] == 25
        assert validated_data["email"] == "john@example.com"
        assert not result.errors

    def test_validate_row_with_field_error(self):
        """Test row validation with field error."""
        validator = SimpleImportValidator()
        row_data = {"name": "", "age": "25"}
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is False
        assert "name" in result.errors
        assert "Name is required" in result.errors["name"][0]

    def test_validate_row_with_field_warning(self):
        """Test row validation with field warning."""
        validator = SimpleImportValidator()
        row_data = {"name": "John", "age": "16"}
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is True
        assert "age" in result.warnings
        assert "Person is under 18" in result.warnings["age"][0]

    def test_validate_row_with_strict_mode(self):
        """Test row validation in strict mode."""
        validator = SimpleImportValidator(strict=True)
        row_data = {"name": "John", "age": "16"}
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is False
        assert "age" in result.errors
        assert "Warning treated as error: Person is under 18" in result.errors["age"][0]

    def test_validate_row_with_cross_validation(self):
        """Test row validation with cross-field validation."""
        validator = SimpleImportValidator()
        row_data = {"name": "Admin", "age": "25"}
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is False
        assert "name" in result.errors
        assert "Admin must be at least 30 years old" in result.errors["name"][0]

    def test_validate_row_with_exception(self):
        """Test row validation with exception in validator."""
        class ExceptionValidator(ImportValidator):
            def validate_field(self, value, row_data, row_index=None):
                raise ValueError("Unexpected error")
        
        validator = ExceptionValidator()
        row_data = {"field": "value"}
        
        is_valid, validated_data, result = validator.validate_row(row_data)
        
        assert is_valid is False
        assert "field" in result.errors
        assert "Validation error: Unexpected error" in result.errors["field"][0]

    def test_validate_row_with_skip_exception(self):
        """Test row validation with SkipRowException."""
        class SkipValidator(ImportValidator):
            def validate_field(self, value, row_data, row_index=None):
                raise SkipRowException("Skip this row")
        
        validator = SkipValidator()
        row_data = {"field": "value"}
        
        with pytest.raises(SkipRowException) as excinfo:
            validator.validate_row(row_data)
        
        assert "Skip this row" in str(excinfo.value)

    def test_post_validate_row(self):
        """Test _post_validate_row method."""
        validator = ImportValidator()
        result = validator._post_validate_row({}, ValidationResult())
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True 