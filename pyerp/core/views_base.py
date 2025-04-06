"""
Base views for the pyERP application.

This module provides base classes for views used throughout the application,
particularly for API views that need to integrate with the form validation system.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from pyerp.core.form_validation import ValidatedForm


class FormValidatedAPIView(APIView):
    """
    Base API view that integrates with the pyERP form validation system.
    
    This view class provides methods to handle form validation and return
    appropriate responses based on validation results.
    """
    
    def validate_form(self, form_class, data, partial=False, instance=None):
        """
        Validate form data and return appropriate result.
        
        Args:
            form_class: The ValidatedForm subclass to use
            data: The data to validate
            partial: Whether this is a partial update
            instance: Optional instance for model forms
            
        Returns:
            tuple: (form, is_valid, response) where response is None if form is valid,
                  or a Response object with validation errors if invalid
        """
        if instance:
            form = form_class(data, instance=instance, partial=partial)
        else:
            form = form_class(data)
            
        if form.is_valid():
            return form, True, None
        
        # Form is invalid, return error response
        return form, False, Response(
            {"errors": form.errors, "success": False},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def process_form(self, form_class, request_data, instance=None, partial=False):
        """
        Process a form with request data and return appropriate response.
        
        Args:
            form_class: The ValidatedForm subclass to use
            request_data: The data from the request
            instance: Optional instance for model forms
            partial: Whether this is a partial update
        
        Returns:
            tuple: (form, success, response) where response is None if further
                  processing is needed, or a Response object if validation failed
        """
        form, is_valid, response = self.validate_form(
            form_class, request_data, partial=partial, instance=instance
        )
        
        if not is_valid:
            return form, False, response
            
        return form, True, None 