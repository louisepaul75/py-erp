"""
Middleware for the Core app.
"""

import logging
import json
from django.http import JsonResponse, HttpResponse
from django.db.utils import OperationalError, InterfaceError, DatabaseError
from django.conf import settings
from rest_framework import status

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
        # Define paths that should work even when DB is down
        db_optional_paths = [
            '/health/',
            '/api/health/',
            '/admin/login/',
            '/login/',
            '/static/',
        ]
        
        # Check if current path should be excluded from DB connection requirement
        path_is_db_optional = any(
            request.path.startswith(path) for path in db_optional_paths
        )
        
        try:
            # Try to process the request normally
            response = self.get_response(request)
            return response
            
        except (OperationalError, InterfaceError, DatabaseError) as e:
            # Log the database error
            logger.error(f"Database connection error: {str(e)}")
            
            # For API requests, return a JSON response
            if request.path.startswith('/api/') and not path_is_db_optional:
                return JsonResponse({
                    'error': 'Database connection error',
                    'message': 'The system is currently unable to connect to the database. Please try again later.',
                    'status': 'service_unavailable'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # For non-API requests or excluded paths, return a HTML response or try to proceed
            if path_is_db_optional:
                # For paths that should work without DB, let them continue
                # The view will handle any further DB errors
                return self.get_response(request)
            else:
                # Show a user-friendly error page for HTML requests
                error_message = """
                <html>
                    <head>
                        <title>Temporary Service Interruption</title>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
                            h1 { color: #333; }
                            .error-container { background-color: #f8f9fa; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
                            .error-message { color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 5px; margin-top: 20px; }
                        </style>
                    </head>
                    <body>
                        <div class="error-container">
                            <h1>Temporary Service Interruption</h1>
                            <p>We're currently experiencing technical difficulties connecting to our database.</p>
                            <p>Our team has been notified and is working to resolve this issue as quickly as possible.</p>
                            <p>Please try again later. We apologize for any inconvenience.</p>
                            
                            <div class="error-message">
                                Error: Unable to connect to database
                            </div>
                        </div>
                    </body>
                </html>
                """
                return HttpResponse(error_message, status=status.HTTP_503_SERVICE_UNAVAILABLE, content_type='text/html') 