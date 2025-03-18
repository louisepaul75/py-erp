"""
Middleware components for pyERP.

This module contains custom middleware components used by the pyERP application
to handle various cross-cutting concerns like authentication, database connections,
and logging.
"""

import os
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db.utils import DatabaseError, InterfaceError, OperationalError
from rest_framework import status
from django.utils.deprecation import MiddlewareMixin

# Set up logging
from pyerp.utils.logging import get_logger
logger = get_logger(__name__)


class DatabaseConnectionMiddleware:
    """
    Middleware to handle database connection issues gracefully.
    
    This middleware catches database connection exceptions and provides
    helpful error messages.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.db_connection_tested = False

    def __call__(self, request):
        # Only test connection once per initialization
        if not self.db_connection_tested:
            self._test_db_connection()
            self.db_connection_tested = True

        return self.get_response(request)

    def _test_db_connection(self):
        """Test the database connection on startup."""
        from django.db import connections
        from django.conf import settings
        import psycopg2

        # Only check PostgreSQL connections
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
            return

        try:
            # Attempt to connect to PostgreSQL
            db_settings = settings.DATABASES['default']
            print(f"Attempting to connect to PostgreSQL at {db_settings['HOST']}:{db_settings['PORT']}")
            
            # Get password from environment variable if not set in settings
            password = db_settings['PASSWORD'] or os.environ.get('DB_PASSWORD', '')
            
            # Test connection directly with psycopg2 for clearer error messages
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=password,
                host=db_settings['HOST'],
                port=db_settings['PORT'],
                connect_timeout=5
            )
            conn.close()
            
            # If we got here, connection succeeded
            print("PostgreSQL connection successful!")
            
        except Exception as e:
            print(f"ERROR: Could not connect to PostgreSQL: {str(e)}")
            logger.error(f"Database connection error: {str(e)}")


class AuthExemptMiddleware(MiddlewareMixin):
    """
    Middleware to exempt specific paths from authentication requirements.

    This middleware runs before Django's AuthenticationMiddleware and marks
    certain requests to bypass the authentication check.
    """

    def process_request(self, request):
        auth_exempt_paths = [
            "/health/",
            "/api/health/",
            "/monitoring/health-check/public/",
            "/monitoring/health-checks/",
        ]

        # Check if current path should be exempt from authentication
        if any(request.path.startswith(path) for path in auth_exempt_paths):
            request._auth_exempt = True

            # Create a dummy user to bypass authentication checks
            class AnonymousUser:
                is_authenticated = True
                is_active = True
                is_superuser = True

                def has_perm(self, *args, **kwargs):
                    return True

                def has_perms(self, *args, **kwargs):
                    return True

                def has_module_perms(self, *args, **kwargs):
                    return True

                def is_anonymous(self):
                    return False

            # Set the anonymous user on the request
            request.user = AnonymousUser()

    def process_response(self, request, response):
        is_exempt = getattr(request, "_auth_exempt", False)

        if (
            is_exempt
            and response.status_code == 302
            and response.get("Location", "").startswith(settings.LOGIN_URL)
        ):
            msg = f"Canceled auth redirect for exempt path: {request.path}"
            logger.debug(msg)

            # Instead of redirecting, pass through to the view
            if hasattr(request, "_auth_exempt_response"):
                return request._auth_exempt_response
            return JsonResponse(
                {
                    "status": "bypassed_auth",
                    "message": "Auth bypassed for health check",
                },
            )

        return response
