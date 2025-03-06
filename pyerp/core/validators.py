"""
Data validation framework for pyERP.

This module provides a flexible, extensible validation system for ensuring data integrity  # noqa: E501
throughout the application. It supports field-level validation, cross-field business rules,  # noqa: E501
and special handling for import data.
"""
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Dict, List, Callable, Optional, Tuple, Union  # noqa: F401
from django.core.exceptions import ValidationError


class ValidationResult:
    """
    Container for validation outcomes.

    Tracks validity status, errors, warnings, and additional context.
    """

    def __init__(self):

        """Initialize a ValidationResult with default values."""
        self.errors = {}
        self.warnings = {}
        self.context = {}
        self.is_valid = True

    def add_error(self, field_name: str, message: str):
        """
        Add an error for a specific field.

        Args:
            field_name: The name of the field with the error
            message: The error message
        """
        if field_name not in self.errors:
            self.errors[field_name] = []

        self.errors[field_name].append(message)
        self.is_valid = False

    def add_warning(self, field_name: str, message: str):
        """
        Add a warning for a specific field.

        Warnings don't affect validity but are useful for non-critical issues.

        Args:
            field_name: The name of the field with the warning
            message: The warning message
        """
        if field_name not in self.warnings:
            self.warnings[field_name] = []

        self.warnings[field_name].append(message)

    def merge(self, other_result):
        """
        Merge another ValidationResult into this one.

        Args:
            other_result: Another ValidationResult instance to merge
        """
        for field_name, messages in other_result.errors.items():
            for message in messages:
                self.add_error(field_name, message)

 # Merge warnings
        for field_name, messages in other_result.warnings.items():
            for message in messages:
                self.add_warning(field_name, message)

 # Merge context
        self.context.update(other_result.context)

    def __str__(self):
        """Return a string representation of the validation result."""
        if self.is_valid:
            return "Valid"

        error_messages = []
        for field, messages in self.errors.items():
            for message in messages:
                error_messages.append(f"{field}: {message}")

        return "Invalid: " + ", ".join(error_messages)


class ValidationError(Exception):
    """Exception raised for validation errors."""

    def __init__(self, message):
        """Initialize with error message."""
        self.message = message
        super().__init__(self.message)


class ImportValidationError(Exception):
    """Exception raised for validation errors during import."""

    def __init__(self, errors):

        """Initialize with validation errors dictionary."""
        self.errors = errors
        message = self._format_errors()
        super().__init__(message)

    def _format_errors(self):
        """Format errors into a readable message."""
        messages = []
        for field, errors in self.errors.items():
            field_errors = ', '.join(errors)
            messages.append(f"{field}: {field_errors}")

        return '; '.join(messages)


class SkipRowException(Exception):
    """
    Exception raised to signal that a row should be skipped during import.

    This is used when a row should be ignored rather than treated as an error.
    """

    def __init__(self, reason=""):
        """Initialize with reason for skipping."""
        self.reason = reason
        super().__init__(f"Row skipped: {reason}" if reason else "Row skipped")


class Validator:
    """
    Base class for all validators.

    Validators are responsible for checking if values meet specific criteria.
    """

    def __init__(self, message=None):
        """
        Initialize the validator.

        Args:
            message: Custom error message to use when validation fails
        """
        self.message = message

    def _validate(self, value, result, **kwargs):
        """
        Internal validation method to be implemented by subclasses.

        Args:
            value: The value to validate
            result: ValidationResult instance to record errors/warnings
            **kwargs: Additional context for validation
        """
        raise NotImplementedError("Subclasses must implement _validate")

    def __call__(self, value, **kwargs):
        """
        Call the validator on a value.

        Args:
            value: The value to validate
            **kwargs: Additional context for validation

        Returns:
            ValidationResult instance with validation outcome
        """
        result = ValidationResult()
        self._validate(value, result, **kwargs)
        return result


class RequiredValidator(Validator):
    """Validates that a value is not empty."""

    def __init__(self, error_message=None, message=None):
        """
        Initialize with optional custom error message.

        Args:
            error_message: Custom error message (preferred parameter name)
            message: Alternative parameter name for error message (for backward compatibility)  # noqa: E501
        """
        final_message = error_message or message or "This field is required"
        super().__init__(final_message)

    def _validate(self, value, result, **kwargs):
        """Check if value is not empty."""
        field_name = kwargs.get('field_name', 'field')

 # Check various empty values
        if value is None or value == "" or (
                                            isinstance(value, (list, dict)) and len(value) == 0  # noqa: E128
        ):
            result.add_error(field_name, self.message)


class RegexValidator(Validator):
    """Validates that a string matches a regular expression pattern."""

    def __init__(self, pattern, error_message=None):
        """
        Initialize with regex pattern and optional error message.

        Args:
            pattern: Regular expression pattern to match
            error_message: Custom error message
        """
        self.pattern = pattern if isinstance(pattern, str) else pattern
        message = error_message or f"Value must match pattern: {self.pattern}"
        super().__init__(message)

    def _validate(self, value, result, **kwargs):
        """Check if value matches the regex pattern."""
        field_name = kwargs.get('field_name', 'field')

 # Skip empty values (use RequiredValidator for that)
        if value is None or value == "":
            return

 # Convert to string if necessary
        if not isinstance(value, str):
            value = str(value)

 # Validate against pattern
        if not re.match(self.pattern, value):
            result.add_error(field_name, self.message)


class RangeValidator(Validator):
    """Validates that a numeric value is within a specified range."""

    def __init__(self, min_value=None, max_value=None, error_message=None):
        """
        Initialize with range bounds and optional error message.

        Args:
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            error_message: Custom error message
        """
        self.min_value = min_value
        self.max_value = max_value

 # Create default message based on bounds
        if min_value is not None and max_value is not None:
            default_message = f"Value must be between {min_value} and {max_value}"  # noqa: E501
        elif min_value is not None:
            default_message = f"Value must be at least {min_value}"
        elif max_value is not None:
            default_message = f"Value must be at most {max_value}"
        else:
            default_message = "Value is out of range"

        message = error_message or default_message
        super().__init__(message)

    def _validate(self, value, result, **kwargs):
        """Check if value is within range."""
        field_name = kwargs.get('field_name', 'field')

 # Skip empty values
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):  # noqa: E501
            return

 # Check if value is numeric
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            result.add_error(field_name, "Value must be a number")
            return

 # Check bounds
        if self.min_value is not None and num_value < self.min_value:
            message = self.message
            if "{min_value}" in message:
                message = message.replace("{min_value}", str(self.min_value))
            if "{max_value}" in message and self.max_value is not None:
                message = message.replace("{max_value}", str(self.max_value))
            result.add_error(field_name, message)

        if self.max_value is not None and num_value > self.max_value:
            message = self.message
            if "{min_value}" in message and self.min_value is not None:
                message = message.replace("{min_value}", str(self.min_value))
            if "{max_value}" in message:
                message = message.replace("{max_value}", str(self.max_value))
            result.add_error(field_name, message)


class LengthValidator(Validator):
    """Validates that a string's length is within specified bounds."""

    def __init__(self, min_length=None, max_length=None, error_message=None):
        """
        Initialize with length bounds and optional error message.

        Args:
            min_length: Minimum allowed length (inclusive)
            max_length: Maximum allowed length (inclusive)
            error_message: Custom error message
        """
        self.min_length = min_length
        self.max_length = max_length

 # Create default message based on bounds
        if min_length is not None and max_length is not None:
            default_message = f"Length must be between {min_length} and {max_length} characters"  # noqa: E501
        elif min_length is not None:
            default_message = f"Length must be at least {min_length} characters"  # noqa: E501
        elif max_length is not None:
            default_message = f"Length must be at most {max_length} characters"
        else:
            default_message = "Length is invalid"

        message = error_message or default_message
        super().__init__(message)

    def _validate(self, value, result, **kwargs):
        """Check if value's length is within range."""
        field_name = kwargs.get('field_name', 'field')

 # Skip empty values
        if value is None or value == "":
            return

 # Convert to string if necessary
        if not isinstance(value, str):
            value = str(value)

 # Check length bounds
        length = len(value)

        if self.min_length is not None and length < self.min_length:
            result.add_error(field_name, self.message)

        if self.max_length is not None and length > self.max_length:
            result.add_error(field_name, self.message)


class ChoiceValidator(Validator):
    """Validates that a value is one of a set of valid choices."""

    def __init__(self, choices, error_message=None):
        """
        Initialize with valid choices and optional error message.

        Args:
            choices: Collection of valid choices
            error_message: Custom error message
        """
        self.choices = choices
        message = error_message or f"Value must be one of: {', '.join(map(str, choices))}"  # noqa: E501
        super().__init__(message)

    def _validate(self, value, result, **kwargs):
        """Check if value is among valid choices."""
        field_name = kwargs.get('field_name', 'field')

 # Skip empty values
        if value is None or value == "":
            return

 # Check if value is in choices
        if value not in self.choices:
            result.add_error(field_name, self.message)


class DecimalValidator(Validator):
    """Validates that a value is a valid decimal number with specified precision."""  # noqa: E501

    def __init__(self, max_digits=None, decimal_places=None, error_message=None):  # noqa: E501
        """
        Initialize with precision constraints and optional error message.

        Args:
            max_digits: Maximum total digits allowed
            decimal_places: Maximum decimal places allowed
            error_message: Custom error message
        """
        self.max_digits = max_digits
        self.decimal_places = decimal_places

        default_message = "Value must be a valid decimal number"
        if max_digits is not None:
            default_message += f" with at most {max_digits} total digits"
        if decimal_places is not None:
            default_message += f" and {decimal_places} decimal places"

        message = error_message or default_message
        super().__init__(message)

    def _validate(self, value, result, **kwargs):
        """Check if value is a valid decimal with correct precision."""
        field_name = kwargs.get('field_name', 'field')

 # Skip empty values
        if value is None or value == "":
            return

 # Convert to Decimal if not already
        try:
            if not isinstance(value, Decimal):
                decimal_value = Decimal(str(value))
            else:
                decimal_value = value
        except (InvalidOperation, ValueError, TypeError):
            result.add_error(field_name, "Value must be a valid decimal number")  # noqa: E501
            return

 # Check precision constraints
        if self.max_digits is not None or self.decimal_places is not None:
            decimal_str = str(decimal_value)
            if 'E' in decimal_str or 'e' in decimal_str:  # Handle scientific notation  # noqa: E501
                decimal_str = str(decimal_value.normalize())

 # Split into integer and fractional parts
            parts = decimal_str.split('.')
            int_part = parts[0].lstrip('-')  # Remove negative sign
            decimal_part = parts[1] if len(parts) > 1 else ''

 # Check decimal places
            if self.decimal_places is not None and len(decimal_part) > self.decimal_places:  # noqa: E501
                result.add_error(
                    field_name,  # noqa: E128
                    f"Value must have at most {self.decimal_places} decimal places"  # noqa: E501
                )

 # Check total digits
            if self.max_digits is not None:
                total_digits = len(int_part) + len(decimal_part)
                if total_digits > self.max_digits:
                    result.add_error(
                        field_name,  # noqa: E128
                        f"Value must have at most {self.max_digits} total digits"  # noqa: E501
                    )


class SkuValidator(RegexValidator):
    """Validates that a value is a valid SKU format."""

    def __init__(self, error_message=None):
        """Initialize with default SKU pattern and optional error message."""
        pattern = r'^[A-Za-z0-9][A-Za-z0-9\-\.]*$'
        message = error_message or "SKU must be in a valid format (letters, numbers, hyphens, dots, no spaces)"  # noqa: E501
        super().__init__(pattern, message)


class CompoundValidator(Validator):
    """
    Combines multiple validators with configurable logic.

    Can require all validators to pass or just any one of them.
    """

    def __init__(self, validators, require_all_valid=True, error_message=None):
        """
        Initialize with a list of validators and validation logic.

        Args:
            validators: List of Validator instances
            require_all_valid: If True, all validators must pass; if False, at least one must pass  # noqa: E501
            error_message: Custom error message
        """
        self.validators = validators
        self.require_all_valid = require_all_valid

        default_message = "Validation failed"
        message = error_message or default_message
        super().__init__(message)

    def _validate(self, value, result, **kwargs):
        """Apply all validators according to configured logic."""
        field_name = kwargs.get('field_name', 'field')

        if not self.validators:
            return  # No validators to apply

 # Track validation results
        validation_results = []
        for validator in self.validators:
            validation_results.append(validator(value, **kwargs))

        if self.require_all_valid:
            for val_result in validation_results:
                result.merge(val_result)
        else:
            if all(not val_result.is_valid for val_result in validation_results):  # noqa: E501
                result.add_error(field_name, self.message)
                for val_result in validation_results:
                    for field, messages in val_result.errors.items():
                        for message in messages:
                            result.add_error(field, message)


class BusinessRuleValidator(Validator):
    """
    Validates business rules that span multiple fields.

    Uses a custom validation function to implement complex business logic.
    """

    def __init__(self, validation_func, error_message=None):
        """
        Initialize with a validation function and optional error message.

        Args:
            validation_func: Function that implements the business rule
            error_message: Custom error message
        """
        self.validation_func = validation_func
        message = error_message or "Business rule validation failed"
        super().__init__(message)

    def _validate(self, value, result, **kwargs):
        """Apply the business rule validation function."""
        if not self.validation_func(value, **kwargs):
            field_name = kwargs.get('field_name', 'field')
            result.add_error(field_name, self.message)


class ImportValidator:
    """
    Base class for import validation.

    Provides a framework for validating data during import processes,
    with support for field-level validation, data transformation,
    and cross-field validation.
    """

    def __init__(self, strict=False, transform_data=True):
        """
        Initialize import validator.

        Args:
            strict: If True, warnings are treated as errors
            transform_data: If True, data is transformed during validation
        """
        self.strict = strict
        self.transform_data = transform_data

    def validate_row(self, row_data, row_index=None):
        """
        Validate an entire row of data.

        Args:
            row_data: Dictionary containing the row data
            row_index: Optional index of the row for context

        Returns:
            Tuple of (is_valid, validated_data, result)
        """
        validated_data = {}
        result = ValidationResult()

 # Process each field in the row
        for field_name, value in row_data.items():
            validator_method_name = f"validate_{field_name}"
            validator_method = getattr(self, validator_method_name, None)

            if validator_method:
                try:
                    transformed_value, field_result = validator_method(
                        value, row_data, row_index=row_index  # noqa: E128
                    )

 # Handle validation result
                    if field_result.is_valid:
                        if self.transform_data:
                            validated_data[field_name] = transformed_value
                        else:
                            validated_data[field_name] = value

 # Handle field errors and warnings
                    for msg_type, messages_dict in [
                                                    ('errors', field_result.errors),  # noqa: E128
                                                    ('warnings', field_result.warnings)  # noqa: E501
                    ]:
                        for field, messages in messages_dict.items():
                            for message in messages:
                                if msg_type == 'errors':
                                    result.add_error(field, message)
                                else:
                                    result.add_warning(field, message)

                except SkipRowException as e:
                    raise

                except Exception as e:
                    result.add_error(field_name, f"Validation error: {str(e)}")

            else:
                validated_data[field_name] = value

 # Apply cross-field validation rules
        cross_field_result = self._post_validate_row(validated_data, result, row_index)  # noqa: E501
        if cross_field_result:
            result.merge(cross_field_result)

 # Handle warnings in strict mode
        if self.strict and result.warnings:
            for field, warnings in result.warnings.items():
                for warning in warnings:
                    result.add_error(field, f"Warning treated as error: {warning}")  # noqa: E501

        return result.is_valid, validated_data, result

    def _post_validate_row(self, validated_data, result, row_index=None):
        """
        Perform cross-field validation after individual fields are validated.

        Override this method to implement business rules that span multiple fields.  # noqa: E501

        Args:
            validated_data: Dictionary of validated field values
            result: Current ValidationResult
            row_index: Optional row index for context

        Returns:
            ValidationResult from cross-field validation
        """
        if hasattr(self, 'cross_validate_row'):
            return self.cross_validate_row(validated_data)
        return ValidationResult()


def validate_data(value, validators, context=None):
    """
    Apply a list of validators to a value.

    Args:
        value: The value to validate
        validators: List of Validator instances
        context: Additional context for validation

    Returns:
        ValidationResult with combined validation outcomes
    """
    context = context or {}
    result = ValidationResult()

    for validator in validators:
        validator_result = validator(value, **context)
        result.merge(validator_result)

    return result


def validate_model_data(instance):
    """
    Validate a model instance using Django's validation framework.

    Args:
        instance: Model instance to validate

    Raises:
        ValidationError: If validation fails
    """
    errors = {}

 # Get validators specific to this model type
    fields_to_validate = getattr(instance, '_validators', {})

 # Apply validators to each field
    for field_name, validators in fields_to_validate.items():
        value = getattr(instance, field_name, None)
        result = validate_data(value, validators, {'field_name': field_name})

        if not result.is_valid:
            errors.update(result.errors)

 # If errors were found, raise ValidationError
    if errors:
        raise ValidationError(errors)
