"""
Views for the Core app.
"""

import json
import logging
import os
import subprocess

from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Set up logging
logger = logging.getLogger("pyerp.core")

# Language session key constant (compatible with Django 5.1+)
LANGUAGE_SESSION_KEY = "django_language"

from pyerp.core.models import UserPreference
from pyerp.core.serializers import UserPreferenceSerializer


@require_GET
@csrf_exempt
def health_check(request):
    """
    Health check endpoint to verify the system is running.
    Checks database connection and returns system status.
    This view is intentionally not protected by authentication to allow
    external monitoring.
    """
    logger.debug("Health check requested")

    # Get environment and version info
    environment = os.environ.get("DJANGO_ENV", "development")
    version = getattr(settings, "APP_VERSION", "unknown")

    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        response_data = {
            "status": "healthy",
            "database": {"status": "connected", "message": "Database is connected"},
            "environment": environment,
            "version": version,
        }
        status_code = status.HTTP_200_OK

    except OperationalError as e:
        # Specific handling for database connection errors
        msg = f"Database connection error: {e!s}"
        logger.error(msg)
        response_data = {
            "status": "unhealthy",
            "database": {"status": "error", "message": msg},
            "environment": environment,
            "version": version,
        }
        status_code = status.HTTP_200_OK  # Still return 200 for monitoring systems

    except Exception as e:
        msg = f"Unexpected error during health check: {e!s}"
        logger.error(msg)
        response_data = {
            "status": "unhealthy",
            "database": {"status": "error", "message": msg},
            "environment": environment,
            "version": version,
        }
        status_code = status.HTTP_200_OK  # Still return 200 for monitoring systems

    # Create response with explicit content type
    response = JsonResponse(response_data, status=status_code)
    response["Content-Type"] = "application/json"

    # Disable debug-related middleware processing
    request._dont_enforce_csrf_checks = True
    if hasattr(request, "_auth_exempt"):
        request._auth_exempt_response = response

    return response


@require_GET
@csrf_exempt
def git_branch(request):
    """
    Get the current git branch name.
    Only available in development mode.
    """
    if not settings.DEBUG:
        return JsonResponse(
            {"error": "Not available in production"},
            status=403,
        )

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        return JsonResponse({"branch": branch})
    except subprocess.CalledProcessError:
        return JsonResponse(
            {"error": "Could not get branch name"},
            status=500,
        )


class UserProfileView(APIView):
    """View to retrieve and update the authenticated user's profile."""

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
        allowed_fields = ["first_name", "last_name", "email"]
        updated_fields = {}

        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
                updated_fields[field] = request.data[field]

        if updated_fields:
            user.save()
            fields_str = ", ".join(updated_fields.keys())
            msg = f"User {user.username} updated profile fields: {fields_str}"
            logger.info(msg)
            return Response(
                {
                    "message": "Profile updated successfully",
                    "updated_fields": updated_fields,
                },
            )

        return Response(
            {"message": "No valid fields to update"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DashboardSummaryView(APIView):
    """View to retrieve and update dashboard data."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get summary data and user's dashboard configuration."""
        msg = f"Dashboard summary requested by {request.user.username}"
        logger.debug(msg)

        # Get or create user preferences
        user_pref, created = UserPreference.objects.get_or_create(
            user=request.user
        )
        
        # Get dashboard modules configuration
        dashboard_modules = user_pref.get_dashboard_modules()

        # Example summary data - this would be fetched from the database
        response_data = {
            "pending_orders": 0,
            "low_stock_items": 0,
            "sales_today": 0,
            "production_status": "normal",
            "recent_activities": [],
            "dashboard_modules": dashboard_modules,
        }

        return Response(response_data)
        
    def patch(self, request):
        """Update user's dashboard configuration."""
        msg = f"Dashboard config update requested by {request.user.username}"
        logger.debug(msg)
        
        # Get or create user preferences
        user_pref, created = UserPreference.objects.get_or_create(
            user=request.user
        )
        
        if 'modules' in request.data:
            # Save dashboard modules configuration
            modules = request.data['modules']
            user_pref.save_dashboard_config(modules)
            
            return Response({
                "message": "Dashboard configuration updated successfully",
                "dashboard_modules": modules
            })
        
        return Response(
            {"message": "No valid configuration data provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SystemSettingsView(APIView):
    """View to retrieve and update system settings."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get system settings."""
        if not request.user.is_staff:
            msg = f"Unauthorized settings access by {request.user.username}"
            logger.warning(msg)
            return Response(
                {"error": "You do not have permission to view settings"},
                status=status.HTTP_403_FORBIDDEN,
            )

        msg = f"System settings requested by {request.user.username}"
        logger.debug(msg)

        # Example settings - this would be fetched from the database
        response_data = {
            "company_name": "Example Corp",
            "timezone": settings.TIME_ZONE,
            "decimal_precision": 2,
            "default_currency": "USD",
        }

        return Response(response_data)

    def patch(self, request):
        """Update system settings."""
        if not request.user.is_superuser:
            msg = f"Unauthorized settings update by {request.user.username}"
            logger.warning(msg)
            return Response(
                {"error": "You do not have permission to update settings"},
                status=status.HTTP_403_FORBIDDEN,
            )

        msg = f"Settings update requested by {request.user.username}"
        logger.debug(msg)

        # This would typically update settings in the database
        return Response({"message": "Settings updated successfully"})


@require_GET
def test_db_error(request):
    """Test view to simulate a database connection error."""
    logger.info("Simulating database connection error for testing")
    msg = "This is a simulated database connection error for testing"
    raise OperationalError(msg)


def csrf_failure(request, reason=""):
    """Custom view for CSRF failures with detailed error information."""
    context = {
        "reason": reason,
        "cookies_enabled": request.COOKIES,
        "csrf_cookie": request.META.get("CSRF_COOKIE", None),
        "http_referer": request.META.get("HTTP_REFERER", None),
        "http_host": request.META.get("HTTP_HOST", None),
    }
    return render(request, "csrf_failure.html", context)


class VueAppView(TemplateView):
    """View for rendering the React.js application as the main frontend."""

    template_name = "base/react_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["debug"] = settings.DEBUG

        # Parse Vue.js manifest for correct asset paths in production
        if not settings.DEBUG:
            manifest_path = os.path.join(settings.STATIC_ROOT, "vue", "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path) as f:
                    try:
                        manifest = json.load(f)
                        context["vue_manifest"] = manifest
                    except json.JSONDecodeError:
                        pass

        return context
