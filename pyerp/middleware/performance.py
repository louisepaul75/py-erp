"""
Performance monitoring middleware for measuring request duration and logging performance metrics.
"""
import time
import logging
from pyerp.middleware.request_id import get_request_id

# Set up a dedicated logger for performance metrics
logger = logging.getLogger('pyerp.performance')

class PerformanceMonitoringMiddleware:
    """
    Middleware that measures request duration and logs performance metrics.
    This helps identify slow endpoints and performance bottlenecks.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start timer
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Only log performance for non-static URLs
        if not self._is_static_request(request.path):
            # Get request path and method
            path = request.path
            method = request.method
            
            # Get request ID for correlation
            request_id = get_request_id()
            
            # Log performance data
            self._log_performance(
                path=path, 
                method=method, 
                duration_ms=duration_ms, 
                status_code=response.status_code,
                request_id=request_id
            )
        
        return response
    
    def _is_static_request(self, path):
        """
        Check if the request is for a static file.
        
        Args:
            path: The request path
            
        Returns:
            True if the request is for a static file, False otherwise
        """
        static_prefixes = [
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        return any(path.startswith(prefix) for prefix in static_prefixes)
    
    def _log_performance(self, path, method, duration_ms, status_code, request_id=None):
        """
        Log performance data for a request.
        
        Args:
            path: The request path
            method: The HTTP method
            duration_ms: The request duration in milliseconds
            status_code: The HTTP status code
            request_id: The request ID for correlation
        """
        # Categorize response time
        category = 'normal'
        if duration_ms > 1000:  # More than 1 second
            category = 'slow'
        if duration_ms > 3000:  # More than 3 seconds
            category = 'very_slow'
        
        # Log at appropriate level based on duration
        log_data = {
            'path': path,
            'method': method,
            'duration_ms': duration_ms,
            'status_code': status_code,
            'category': category,
        }
        
        # Add request ID if available
        if request_id:
            log_data['request_id'] = request_id
        
        if category == 'very_slow':
            logger.warning(f"Very slow request: {path}", extra=log_data)
        elif category == 'slow':
            logger.info(f"Slow request: {path}", extra=log_data)
        else:
            logger.debug(f"Request: {path}", extra=log_data) 