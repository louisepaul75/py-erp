"""
Middleware for the Core app.
"""

import logging
import json  # noqa: F401
from django.http import JsonResponse, HttpResponse
from django.db.utils import OperationalError, InterfaceError, DatabaseError
from django.conf import settings
from rest_framework import status
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect  # noqa: F401

 # Set up logging
logger = logging.getLogger('pyerp.core')


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
        db_optional_paths = [
            '/health/',  # noqa: E128
            '/api/health/',
            '/admin/login/',
            '/login/',
            '/static/',
            '/monitoring/health-check/public/',
        ]

 # Check if current path should be excluded from DB connection requirement  # noqa: E501
        path_is_db_optional = any(
            request.path.startswith(path) for path in db_optional_paths  # noqa: E128
        )

        try:
            response = self.get_response(request)
            return response

        except (OperationalError, InterfaceError, DatabaseError) as e:
            logger.error(f"Database connection error: {str(e)}")

 # If the path is in the exempt list, return a basic response
            if path_is_db_optional:
                if request.path.startswith('/health/') or request.path.startswith('/api/health/') or request.path.startswith('/monitoring/health-check/'):  # noqa: E501
                    return JsonResponse({
                        'status': 'db_error',  # noqa: E128
                        'message': 'Database connection is unavailable',
                        'error': str(e)
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                elif request.path.startswith('/static/'):
                    return HttpResponse('Static file not found', status=404)
                else:
                    return HttpResponse(
                        '<html><body><h1>Database Error</h1><p>The database is '  # noqa: E501
                        'currently unavailable. Please try again later.</p></body></html>',  # noqa: E501
                        content_type='text/html'  # noqa: F841
                    )
            else:
                if request.headers.get('accept') == 'application/json' or request.path.startswith('/api/'):  # noqa: E501
                    return JsonResponse({
                        'error': 'database_error',  # noqa: E128
                        'message': 'Database connection is unavailable',
                        'detail': str(e)
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return HttpResponse(
                        '<html><body><h1>Database Error</h1><p>The database is '  # noqa: E501
                        'currently unavailable. Please try again later.</p></body></html>',  # noqa: E501
                        content_type='text/html',  # noqa: F841
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )


class AuthExemptMiddleware(MiddlewareMixin):
    """
    Middleware to exempt specific paths from authentication requirements.

    This middleware runs before Django's AuthenticationMiddleware and marks
    certain requests to bypass the authentication check.
    """

    def process_request(self, request):
        auth_exempt_paths = [
            '/health/',  # noqa: E128
            '/api/health/',
            '/monitoring/health-check/public/',
        ]

 # Check if current path should be exempt from authentication
        if any(request.path.startswith(path) for path in auth_exempt_paths):
            setattr(request, '_auth_exempt', True)

 # Create a dummy user to bypass authentication checks
            class AnonymousUser:

                is_authenticated = True  # noqa: F841
                is_active = True  # noqa: F841
                is_superuser = True  # noqa: F841
                def has_perm(self, *args, **kwargs): return True


                def has_perms(self, *args, **kwargs): return True


                def has_module_perms(self, *args, **kwargs): return True


                def is_anonymous(self): return False


 # Set the anonymous user on the request
            request.user = AnonymousUser()

 # Always return None to continue processing
        return None

    def process_response(self, request, response):
        is_exempt = getattr(request, '_auth_exempt', False)

        if is_exempt and response.status_code == 302 and response.get('Location', '').startswith(settings.LOGIN_URL):  # noqa: E501
            logger.debug(f"Canceled authentication redirect for exempt path: {request.path}")  # noqa: E501

 # Instead of redirecting, pass through to the view
            if hasattr(request, '_auth_exempt_response'):
                return request._auth_exempt_response
            else:
                return JsonResponse({'status': 'bypassed_auth', 'message': 'Auth bypassed for health check'})  # noqa: E501

        return response
