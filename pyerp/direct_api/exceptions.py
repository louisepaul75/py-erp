"""
Custom exceptions for the direct_api module.

This module defines a hierarchy of exceptions for the direct API client
to provide better error handling and more specific error types.
"""


class DirectAPIError(Exception):
    """Base exception for all Direct API errors."""
    pass


class AuthenticationError(DirectAPIError):
    """Raised when authentication fails."""
    pass


class ConnectionError(DirectAPIError):
    """Raised when unable to connect to the API."""
    pass


class ServerUnavailableError(ConnectionError):
    """Raised when the server is unavailable or unreachable.

    This is a specific type of connection error that indicates the server
    is down, not responding, or cannot be reached. This allows for specific
    handling of server unavailability in the application.
    """
    def __init__(self, message="The legacy ERP server is currently unavailable", inner_exception=None):  # noqa: E501
        self.inner_exception = inner_exception
        super().__init__(message)


class ResponseError(DirectAPIError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code, message, response_body=None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"API error {status_code}: {message}")


class RateLimitError(ResponseError):
    """Raised when rate limits are exceeded."""
    pass


class DataError(DirectAPIError):
    """Raised when there's an issue with the data format."""
    pass


class SessionError(DirectAPIError):
    """Raised when there's an issue with the session management."""
    pass


class ConfigurationError(DirectAPIError):
    """Raised when there's an issue with the API configuration."""
    pass
