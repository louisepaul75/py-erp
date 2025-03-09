"""
Middleware for the Core app.
"""

import logging
import os

from django.conf import settings
from django.db.utils import DatabaseError, InterfaceError, OperationalError
from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

# Set up logging
logger = logging.getLogger("pyerp.core")


class DatabaseConnectionMiddleware:
    """
    Middleware to handle database connection errors gracefully.

    This middleware catches database connection errors and returns a friendly
    response instead of crashing the application. It allows certain endpoints
    (like health check) to function normally even when database is unavailable.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Special handling for health check endpoint
        if request.path.endswith("/health/"):
            try:
                response = self.get_response(request)
                # Return if we already have a JsonResponse
                if isinstance(response, JsonResponse):
                    return response

                # Generate our own response for non-JSON responses
                try:
                    env_module = settings.DJANGO_SETTINGS_MODULE
                    env = env_module.split(".")[-1]
                except AttributeError:
                    # Handle missing DJANGO_SETTINGS_MODULE
                    django_settings = os.environ.get(
                        "DJANGO_SETTINGS_MODULE", "unknown"
                    )
                    env = django_settings.split(".")[-1]

                try:
                    from django.db import connection

                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                    db_status = "ok"
                    error_msg = None
                except Exception as e:
                    db_status = "error"
                    error_msg = str(e)
                    msg = "Database health check failed: {}"
                    logger.error(msg.format(e))

                status_code = (
                    status.HTTP_200_OK
                    if db_status == "ok"
                    else status.HTTP_503_SERVICE_UNAVAILABLE
                )

                health_status = "healthy" if db_status == "ok" else "unhealthy"
                db_conn_status = "connected" if db_status == "ok" else "error"
                msg = error_msg if error_msg else "Database is connected"

                return JsonResponse(
                    {
                        "status": health_status,
                        "database": {
                            "status": db_conn_status,
                            "message": msg,
                        },
                        "environment": env,
                        "version": getattr(settings, "APP_VERSION", "unknown"),
                    },
                    status=status_code,
                )
            except Exception as e:
                try:
                    env_module = settings.DJANGO_SETTINGS_MODULE
                    env = env_module.split(".")[-1]
                except AttributeError:
                    # Handle missing DJANGO_SETTINGS_MODULE
                    django_settings = os.environ.get(
                        "DJANGO_SETTINGS_MODULE", "unknown"
                    )
                    env = django_settings.split(".")[-1]

                return JsonResponse(
                    {
                        "status": "unhealthy",
                        "database": {
                            "status": "error",
                            "message": str(e),
                        },
                        "environment": env,
                        "version": getattr(settings, "APP_VERSION", "unknown"),
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        # Handle other paths that don't require database access
        db_optional_paths = [
            "/health/",
            "/api/health/",
            "/admin/login/",
            "/login/",
            "/static/",
            "/media/",
            "/staticfiles/",
            "/assets/",
            "/favicon.ico",
            "/robots.txt",
            "/manifest.json",
            "/service-worker.js",
            "/.well-known/",
            "/sitemap.xml",
            "/monitoring/health-check/public/",
            "/monitoring/health-checks/",
        ]

        # Check for static file extensions that don't need database access
        static_extensions = [
            '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
            '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map'
        ]
        
        # Check if path is optional or has a static extension
        is_optional = any(
            request.path.startswith(path) for path in db_optional_paths
        )
        has_static_extension = any(
            request.path.endswith(ext) for ext in static_extensions
        )
        
        if is_optional or has_static_extension:
            return self.get_response(request)

        # Handle database errors for all other paths
        try:
            return self.get_response(request)
        except (DatabaseError, InterfaceError, OperationalError) as e:
            msg = "Database error: {}"
            logger.error(msg.format(e))
            if request.path.startswith("/api/"):
                return JsonResponse(
                    {"error": "Database connection error"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            return HttpResponse(
                "Database connection error",
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


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

    # Always return None to continue processing

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
