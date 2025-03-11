"""
Logging middleware for pyERP

This module provides middleware classes for logging HTTP requests and responses
in the pyERP system.
"""

import time
import uuid
from django.utils.deprecation import MiddlewareMixin

from pyerp.utils.logging import get_logger, log_performance

logger = get_logger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs details about requests and responses.
    
    This middleware adds a unique request ID to each request and logs:
    - Incoming request details
    - Response status and timing
    - Performance metrics
    """
    
    def process_request(self, request):
        """Process the request and add timing information."""
        # Generate a unique ID for this request
        request.id = str(uuid.uuid4())
        
        # Start timing the request
        request.start_time = time.time()
        
        # Extract user information safely
        user = getattr(request, 'user', None)
        user_info = (
            str(user.id) if user and hasattr(user, 'id') and user.id else 'anonymous'
        )
        
        # Log the request
        logger.info(
            f"Request {request.method} {request.path}",
            extra={
                'request_id': request.id,
                'method': request.method,
                'path': request.path,
                'user': user_info,
                'ip': self.get_client_ip(request),
            }
        )
        
        return None
    
    def process_response(self, request, response):
        """Process the response and log timing information."""
        # Skip if this is a streaming response
        if not hasattr(response, 'status_code'):
            return response
            
        # Skip if request object doesn't have timing info (added by process_request)
        if not hasattr(request, 'start_time'):
            return response
            
        # Calculate request duration
        duration = time.time() - request.start_time
        duration_ms = int(duration * 1000)
        
        # Get the view name if available
        view_name = getattr(request, 'view_name', 'unknown_view')
        
        # Log basic response info
        logger.info(
            f"Response {response.status_code} in {duration_ms}ms",
            extra={
                'request_id': getattr(request, 'id', 'unknown'),
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'view': view_name,
                'path': request.path,
            }
        )
        
        # Log performance metrics for slower requests (> 500ms)
        if duration_ms > 500:
            log_performance(
                f"slow_request.{view_name}",
                duration_ms,
                {
                    'request_id': getattr(request, 'id', 'unknown'),
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                }
            )
            
        return response

    def process_exception(self, request, exception):
        """Log unhandled exceptions."""
        logger.error(
            f"Unhandled exception in {request.path}: {str(exception)}",
            exc_info=exception,
            extra={
                'request_id': getattr(request, 'id', 'unknown'),
                'path': request.path,
                'method': request.method,
            }
        )
        return None
    
    def get_client_ip(self, request):
        """Extract the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can be a comma-separated list of IPs.
            # The client's IP will be the first one.
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip 