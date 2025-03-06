"""
Form validation utilities for pyERP.

This module provides integration between Django forms and the validation framework,  # noqa: E501
allowing reuse of validators and consistent validation behavior across the application.  # noqa: E501
"""

from collections.abc import Callable
from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from pyerp.core.validators import ValidationResult, Validator


class ValidatedFormMixin:
    """
    Mixin for Django forms to integrate with the validation framework.

    This mixin allows adding validators to form fields and handling
    validation consistently across the application.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with empty validator dictionaries."""
        super().__init__(*args, **kwargs)

        # Initialize validator containers
        self.field_validators = {}
        self.form_validators = []

        # Set up validators
        self.setup_validators()

    def setup_validators(self):
        """
        Hook for adding validators to fields.

        Override this method to define field validators.
        """

    def add_validator(self, field_name: str, validator: Validator):
        """
        Add a validator to a field.

        Args:
            field_name: Name of the field to validate
            validator: Validator instance to apply
        """
        if field_name not in self.field_validators:
            self.field_validators[field_name] = []

        self.field_validators[field_name].append(validator)

    def add_form_validator(
        self,
        validator_func: Callable[[dict[str, Any]], ValidationResult],
    ):
        """
        Add a form-level validator function.

        Args:
            validator_func: Function that validates the entire form
        """
        self.form_validators.append(validator_func)

    def apply_validators(self, field_name: str, value: Any) -> ValidationResult:
        """
        Apply all validators for a field.

        Args:
            field_name: Name of the field to validate
            value: Value to validate

        Returns:
            ValidationResult with combined results of all validators
        """
        result = ValidationResult()

        # Skip if no validators defined for this field
        if field_name not in self.field_validators:
            return result

        # Apply each validator
        for validator in self.field_validators[field_name]:
            validator_result = validator(value, field_name=field_name)
            result.merge(validator_result)

        return result

    def apply_form_validators(self, cleaned_data: dict[str, Any]) -> ValidationResult:
        """
        Apply all form-level validators.

        Args:
            cleaned_data: Dictionary of cleaned form data

        Returns:
            ValidationResult with combined results of all form validators
        """
        result = ValidationResult()

        # Apply each form validator
        for validator_func in self.form_validators:
            validator_result = validator_func(cleaned_data)
            result.merge(validator_result)

        return result

    def clean(self):
        """
        Clean the form data and apply validators.

        This extends Django's form cleaning process to use our validators.

        Returns:
            Dictionary of cleaned data

        Raises:
            ValidationError: If validation fails
        """
        cleaned_data = super().clean()

        # Apply field validators through clean_<field> methods
        for field_name in list(cleaned_data.keys()):
            if field_name in self.field_validators:
                pass

        # Apply form-level validators
        form_result = self.apply_form_validators(cleaned_data)

        # If form validation failed, add errors
        if not form_result.is_valid:
            for field_name, error_messages in form_result.errors.items():
                for message in error_messages:
                    self.add_error(field_name, message)

        return cleaned_data

    def __getattribute__(self, name):
        """
        Custom attribute getter to handle dynamic clean_<field> methods.

        This allows validators to be called automatically during form cleaning.
        """
        if name.startswith("clean_") and not name == "clean":
            field_name = name[6:]  # Remove 'clean_' prefix

            # Check if we have validators for this field
            try:
                field_validators = object.__getattribute__(self, "field_validators")
                if field_name in field_validators:

                    def clean_field():
                        value = self.cleaned_data.get(field_name)

                        # Apply validators
                        validation_result = self.apply_validators(field_name, value)

                        # If validation failed, raise ValidationError
                        if not validation_result.is_valid:
                            errors = []
                            for field, messages in validation_result.errors.items():
                                errors.extend(messages)
                            raise ValidationError(errors)

                        return value

                    # Return the dynamic method
                    return clean_field
            except (AttributeError, KeyError):
                pass

        # Fall back to normal attribute lookup
        return object.__getattribute__(self, name)


class ValidatedModelForm(ValidatedFormMixin, forms.ModelForm):
    """
    Model form with validation framework integration.

    This class extends Django's ModelForm with the validation framework,
    allowing validators to be applied to model form fields.
    """

    def clean(self):
        """
        Clean the form and validate the associated model.

        This extends the validation to include model instance validation.

        Returns:
            Dictionary of cleaned data

        Raises:
            ValidationError: If validation fails
        """
        cleaned_data = super().clean()

        # Additional model-specific validation can be added here

        return cleaned_data


class ValidatedForm(ValidatedFormMixin, forms.Form):
    """
    Form with validation framework integration.

    This class extends Django's Form with the validation framework,
    allowing validators to be applied to form fields.
    """

    def is_valid(self):
        """
        Check if the form is valid.

        This extends Django's is_valid method to ensure proper validation.

        Returns:
            Boolean indicating if the form is valid
        """
        is_valid = super().is_valid()

        # Add form-level validation
        if is_valid and self.form_validators:
            form_result = self.apply_form_validators(self.cleaned_data)

            if not form_result.is_valid:
                for field_name, error_messages in form_result.errors.items():
                    for message in error_messages:
                        self.add_error(field_name, message)

                # Form is invalid if form validators failed
                is_valid = False

        return is_valid
