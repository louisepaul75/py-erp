import uuid
import threading

# Thread local storage for the request ID
_request_id = threading.local()

def get_request_id():
    """
    Get the current request ID from thread local storage.
    Returns None if no request ID is set.
    """
    return getattr(_request_id, 'value', None)

class RequestIDMiddleware:
    """
    Middleware that adds a unique request ID to each request.
    This ID can be used for tracing requests across the system.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Generate a new request ID
        request_id = str(uuid.uuid4())
        
        # Store it in thread local storage
        _request_id.value = request_id
        
        # Add it to the request object
        request.request_id = request_id
        
        # Process the request
        response = self.get_response(request)
        
        # Add the request ID to the response headers
        response['X-Request-ID'] = request_id
        
        # Clear the thread local storage
        del _request_id.value
        
        return response 