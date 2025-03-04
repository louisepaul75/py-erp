"""
Views for the Core app.
"""

import logging
import json
import os

from django.conf import settings
from django.db import connection
from django.http import JsonResponse, HttpResponseRedirect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.http import require_GET, require_http_methods
from django.db.utils import OperationalError
from django.utils.translation import activate, get_language
from django.utils import translation
from django.shortcuts import render
from django.views.generic import TemplateView

# Set up logging
logger = logging.getLogger('pyerp.core')

# Language session key constant (compatible with Django 5.1+)
LANGUAGE_SESSION_KEY = 'django_language'

def health_check(request):
    """
    Health check endpoint to verify the system is running.
    Checks database connection and returns system status.
    """
    logger.debug("Health check requested")
    
    # Check database connection
    db_status = "ok"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as e:
        db_status = "error"
        logger.error(f"Database health check failed: {e}")
    
    # Get environment and debug status
    environment = settings.DJANGO_SETTINGS_MODULE.split('.')[-1]
    
    # Return system status
    response_data = {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "environment": environment,
        "version": getattr(settings, 'APP_VERSION', 'unknown'),
    }
    
    status_code = status.HTTP_200_OK if db_status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JsonResponse(response_data, status=status_code)


class UserProfileView(APIView):
    """
    View to retrieve and update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get the authenticated user's profile."""
        logger.debug(f"User profile requested by {request.user.username}")
        
        user = request.user
        response_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined,
        }
        
        return Response(response_data)
    
    def patch(self, request):
        """Update the authenticated user's profile."""
        user = request.user
        logger.debug(f"User profile update requested by {user.username}")
        
        # Only allow updating specific fields
        allowed_fields = ['first_name', 'last_name', 'email']
        updated_fields = {}
        
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
                updated_fields[field] = request.data[field]
        
        if updated_fields:
            user.save()
            logger.info(f"User {user.username} updated profile fields: {', '.join(updated_fields.keys())}")
            return Response({"message": "Profile updated successfully", "updated_fields": updated_fields})
        
        return Response({"message": "No valid fields to update"}, status=status.HTTP_400_BAD_REQUEST)


class DashboardSummaryView(APIView):
    """
    View to retrieve summary data for the dashboard.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get summary data for the dashboard."""
        logger.debug(f"Dashboard summary requested by {request.user.username}")
        
        # Example summary data - in a real implementation, this would be fetched from the database
        response_data = {
            "pending_orders": 0,
            "low_stock_items": 0,
            "sales_today": 0,
            "production_status": "normal",
            "recent_activities": [],
        }
        
        return Response(response_data)


class SystemSettingsView(APIView):
    """
    View to retrieve and update system settings.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get system settings."""
        # Check if user has permission to view system settings
        if not request.user.is_staff:
            logger.warning(f"Unauthorized system settings access attempt by {request.user.username}")
            return Response(
                {"error": "You do not have permission to view system settings"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        logger.debug(f"System settings requested by {request.user.username}")
        
        # Example settings data - in a real implementation, this would be fetched from the database
        response_data = {
            "company_name": "Example Corp",
            "timezone": settings.TIME_ZONE,
            "decimal_precision": 2,
            "default_currency": "USD",
        }
        
        return Response(response_data)
    
    def patch(self, request):
        """Update system settings."""
        # Check if user has permission to update system settings
        if not request.user.is_superuser:
            logger.warning(f"Unauthorized system settings update attempt by {request.user.username}")
            return Response(
                {"error": "You do not have permission to update system settings"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        logger.debug(f"System settings update requested by {request.user.username}")
        
        # This would typically update settings in the database
        # For demonstration, we'll just acknowledge the request
        return Response({"message": "Settings updated successfully"})


@require_GET
def test_db_error(request):
    """
    Test view to simulate a database connection error.
    This is for testing the database connection middleware.
    """
    # Intentionally raise a database connection error
    logger.info("Simulating database connection error for testing")
    raise OperationalError("This is a simulated database connection error for testing")


def csrf_failure(request, reason=""):
    """
    Custom view for CSRF failures that provides more detailed error information.
    """
    context = {
        'reason': reason,
        'cookies_enabled': request.COOKIES,
        'csrf_cookie': request.META.get('CSRF_COOKIE', None),
        'http_referer': request.META.get('HTTP_REFERER', None),
        'http_host': request.META.get('HTTP_HOST', None),
    }
    return render(request, 'csrf_failure.html', context)


class VueAppView(TemplateView):
    """View for rendering the Vue.js application as the main frontend."""
    template_name = 'base/vue_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Explicitly pass debug flag to template
        context['debug'] = settings.DEBUG
        
        # In production mode, parse the Vue.js manifest to get correct asset paths
        if not settings.DEBUG:
            manifest_path = os.path.join(settings.STATIC_ROOT, 'vue', 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    try:
                        manifest = json.load(f)
                        context['vue_manifest'] = manifest
                    except json.JSONDecodeError:
                        pass
        
        return context 