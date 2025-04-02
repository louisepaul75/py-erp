"""
API utilities for pyERP.

This module provides utilities for integrating Django forms, particularly the
validation framework, with Django REST Framework views.
"""

from rest_framework.response import Response
from rest_framework import status

from pyerp.core.form_validation import ValidatedForm


def process_form_validation(form):
    """
    Process form validation and return appropriate response.
    
    Args:
        form: An instance of ValidatedForm that has been initialized with data
        
    Returns:
        tuple: (is_valid, response_or_none) where response_or_none is a Response
               object with validation errors if the form is invalid, or None if valid
    """
    # Use the direct validation method instead of is_valid()
    if isinstance(form, ValidatedForm):
        # Use the form's data if it's a Django form
        validation_result = form.validate(form.data)
        
        if validation_result.has_errors():
            return False, Response(
                {"errors": validation_result.errors, "success": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        return True, None
    else:
        # Fallback to is_valid() for non-ValidatedForm instances
        if not form.is_valid():
            return False, Response(
                {"errors": form.errors, "success": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        return True, None


def validate_form_data(form_class, data, partial=False, instance=None):
    """
    Create and validate a form with the given data.
    
    Args:
        form_class: A ValidatedForm subclass
        data: Dict of data to validate
        partial: Whether to perform partial validation
        instance: Optional instance for model forms
        
    Returns:
        tuple: (form, is_valid, response_or_none) where response_or_none is a Response
               object with validation errors if the form is invalid, or None if valid
    """
    if instance:
        form = form_class(data, instance=instance, partial=partial)
    else:
        form = form_class(data)
    
    # Direct validation for ValidatedForm instances
    if isinstance(form, ValidatedForm):
        validation_result = form.validate(data)
        if validation_result.has_errors():
            response = Response(
                {"errors": validation_result.errors, "success": False},
                status=status.HTTP_400_BAD_REQUEST
            )
            return form, False, response
        return form, True, None
    else:
        # Fallback to normal form validation
        is_valid, response = process_form_validation(form)
        return form, is_valid, response 