# pyerp/buchhaltungsbutler/exceptions.py

class BuchhaltungsButlerError(Exception):
    """Base exception class for BuchhaltungsButler API errors."""
    pass

class AuthenticationError(BuchhaltungsButlerError):
    """Exception raised for authentication errors (401, 403)."""
    pass

class APIRequestError(BuchhaltungsButlerError):
    """Exception raised for failed API requests (non-2xx status codes)."""
    def __init__(self, status_code, response_text):
        self.status_code = status_code
        self.response_text = response_text
        message = (
            f"API request failed with status {status_code}. "
            f"Response: {response_text[:500]}" # Truncate long responses
        )
        super().__init__(message)

class RateLimitError(BuchhaltungsButlerError):
    """Exception raised when the API rate limit is exceeded (429)."""
    pass

# Add more specific exceptions as needed 