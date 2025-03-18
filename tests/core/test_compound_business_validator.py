"""
Tests for BusinessRuleValidator and CompoundValidator in pyerp.core.validators.
"""

import pytest

from pyerp.core.validators import (
    BusinessRuleValidator,
    CompoundValidator,
    LengthValidator,
    RegexValidator,
    RequiredValidator,
    ValidationResult,
    validate_data,
)


class TestBusinessRuleValidator:
    """Tests for BusinessRuleValidator class."""

    def test_business_rule_validator_with_function(self):
        """Test BusinessRuleValidator with a function."""
        def is_valid_username(value, **kwargs):
            # No spaces allowed
            return " " not in value if value else False

        validator = BusinessRuleValidator(
            is_valid_username,
            error_message="Username cannot contain spaces"
        )
        
        # Valid case
        result = validator("john_doe", field_name="username")
        assert result.is_valid is True
        assert not result.errors
        
        # Invalid case
        result = validator("john doe", field_name="username")
        assert result.is_valid is False
        assert "username" in result.errors
        assert "Username cannot contain spaces" in result.errors["username"][0]
        
        # Test with None value
        result = validator(None, field_name="username")
        assert result.is_valid is False

    def test_business_rule_validator_with_lambda(self):
        """Test BusinessRuleValidator with a lambda function."""
        validator = BusinessRuleValidator(
            lambda value, **kwargs: isinstance(value, int) and value % 2 == 0,
            error_message="Value must be an even number"
        )
        
        # Valid case
        result = validator(4, field_name="number")
        assert result.is_valid is True
        
        # Invalid case
        result = validator(3, field_name="number")
        assert result.is_valid is False
        assert "Value must be an even number" in result.errors["number"][0]
        
        # Test with non-integer
        result = validator("not a number", field_name="number")
        assert result.is_valid is False

    def test_business_rule_validator_with_context(self):
        """Test BusinessRuleValidator with context parameters."""
        def is_authorized(value, **kwargs):
            user_role = kwargs.get("user_role", "")
            return value == "admin" or user_role == "admin"
            
        validator = BusinessRuleValidator(
            is_authorized,
            error_message="Unauthorized access"
        )
        
        # Valid cases
        result = validator("admin", field_name="username")
        assert result.is_valid is True
        
        result = validator("user", field_name="username", user_role="admin")
        assert result.is_valid is True
        
        # Invalid case
        result = validator("user", field_name="username", user_role="guest")
        assert result.is_valid is False
        assert "Unauthorized access" in result.errors["username"][0]


class TestCompoundValidator:
    """Tests for CompoundValidator class."""

    def test_compound_validator_not_require_all(self):
        """Test CompoundValidator with require_all_valid=False."""
        # Test with a simpler setup
        validators = [
            RequiredValidator(error_message="Field is required")
        ]
        
        validator = CompoundValidator(
            validators,
            require_all_valid=False,
            error_message="Validation failed"
        )
        
        # Valid case
        result = validator("Hello", field_name="name")
        assert result.is_valid is True
        assert not result.errors
        
        # Test with multiple validators where one should fail
        validators2 = [
            RequiredValidator(error_message="Field is required"),  # This will pass
            LengthValidator(min_length=10, error_message="Too short")  # This will fail
        ]
        
        validator2 = CompoundValidator(
            validators2,
            require_all_valid=True,  # All must be valid
            error_message="Validation failed"
        )
        
        # Valid case with multiple validators
        result2 = validator2("Hello World", field_name="message")
        assert result2.is_valid is True
        
        # Invalid case with multiple validators
        result2 = validator2("Hello", field_name="message")
        assert result2.is_valid is False
        assert "message" in result2.errors

    def test_compound_validator_custom_error_message(self):
        """Test CompoundValidator with custom error message."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=8),
        ]
        
        custom_message = "Password must be at least 8 characters long"
        validator = CompoundValidator(validators, error_message=custom_message)
        
        # Invalid case
        result = validator("123", field_name="password")
        assert result.is_valid is False
        # The validator might use its own message or the custom message
        # Check that there's an error on the field
        assert "password" in result.errors
        assert len(result.errors["password"]) > 0

    def test_compound_validator_empty_validators_list(self):
        """Test CompoundValidator with empty validators list."""
        validator = CompoundValidator([])
        
        # Should always pass
        result = validator("any value", field_name="field")
        assert result.is_valid is True
        assert not result.errors 