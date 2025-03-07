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
        self.validators = {}  # Field validators
        self.form_validators = []  # Form-level validators

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
        if field_name not in self.validators:
            self.validators[field_name] = []

        self.validators[field_name].append(validator)

    def add_form_validator(
        self,
        validator_func: Callable[
            [dict[str, Any]],
            ValidationResult | dict[str, list[str]] | None,
        ],
    ):
        """
        Add a form-level validator function.

        Args:
            validator_func: Function that validates the entire form
        """
        self.form_validators.append(validator_func)

    def apply_validators(
        self, field_name: str, value: Any
    ) -> ValidationResult:
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
        if field_name not in self.validators:
            return result

        # Apply each validator
        for validator in self.validators[field_name]:
            validator_result = validator(value, field_name=field_name)
            if validator_result:
                result.merge(validator_result)

        return result

    def apply_form_validators(
        self, cleaned_data: dict[str, Any]
    ) -> ValidationResult:
        """
        Apply all form-level validators.

        Args:
            cleaned_data: Dictionary of cleaned form data

        Returns:
            ValidationResult with combined results of all form validators
        """
        result = ValidationResult()

        for validator in self.form_validators:
            validator_result = validator(cleaned_data)
            if validator_result:
                if isinstance(validator_result, dict):
                    for field_name, messages in validator_result.items():
                        for message in messages:
                            result.add_error(field_name, message)
                elif isinstance(validator_result, ValidationResult):
                    result.merge(validator_result)

        return result

    def clean(self):
        """
        Clean and validate the form data.

        This method is called by Django's form validation process.
        It applies field-level and form-level validators.

        Returns:
            Cleaned form data

        Raises:
            ValidationError: If validation fails
        """
        cleaned_data = super().clean()

        # Apply form-level validators
        form_result = self.apply_form_validators(cleaned_data)

        # Add any validation errors to the form
        for field_name, messages in form_result.errors.items():
            for message in messages:
                self.add_error(field_name, message)

        return cleaned_data

    def __getattribute__(self, name):
        """
        Override attribute access to handle dynamic field cleaning methods.

        This allows field validators to be called during Django's form
        validation.
        """
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if name.startswith("clean_") and name[6:] in self.validators:
                field_name = name[6:]

                def clean_field():
                    value = self.cleaned_data.get(field_name)
                    result = self.apply_validators(field_name, value)
                    if result.has_errors():
                        raise ValidationError(result.errors[field_name])
                    return value

                return clean_field
            raise e


class ValidatedModelForm(ValidatedFormMixin, forms.ModelForm):
    """
    Base class for validated model forms.

    This class combines Django's ModelForm with our validation framework.
    """

    def clean(self):
        """
        Clean and validate the form data.

        This method is called by Django's form validation process.
        It applies field-level and form-level validators.

        Returns:
            Cleaned form data

        Raises:
            ValidationError: If validation fails
        """
        cleaned_data = super().clean()

        # Apply form-level validators
        form_result = self.apply_form_validators(cleaned_data)

        # Add any validation errors to the form
        for field_name, messages in form_result.errors.items():
            for message in messages:
                self.add_error(field_name, message)

        return cleaned_data


class ValidatedForm(ValidatedFormMixin, forms.Form):
    """
    Base class for validated forms.

    This class combines Django's Form with our validation framework.
    """

    def is_valid(self):
        """
        Check if the form is valid.

        This method is called to validate the form data.
        It applies field-level and form-level validators.

        Returns:
            bool: True if the form is valid, False otherwise
        """
        is_valid = super().is_valid()
        if not is_valid:
            return False

        # Apply form-level validators
        form_result = self.apply_form_validators(self.cleaned_data)

        # Add any validation errors to the form
        for field_name, messages in form_result.errors.items():
            for message in messages:
                self.add_error(field_name, message)

        return not form_result.has_errors()
