"""
Custom exceptions for the legacy ERP API module.

This module defines a hierarchy of exceptions for the legacy ERP API client
to provide better error handling and more specific error types.
"""


class LegacyERPError(Exception):
    """Base exception for all Legacy ERP API errors."""


class AuthenticationError(LegacyERPError):
    """Raised when authentication fails."""


class ConnectionError(LegacyERPError):
    """Raised when unable to connect to the API."""


class ServerUnavailableError(ConnectionError):
    """Raised when the server is unavailable or unreachable.

    This is a specific type of connection error that indicates the server
    is down, not responding, or cannot be reached. This allows for specific
    handling of server unavailability in the application.
    """

    def __init__(
        self,
        message="The legacy ERP server is currently unavailable",
        inner_exception=None,
    ):
        self.inner_exception = inner_exception
        super().__init__(message)


class ResponseError(LegacyERPError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code, message, response_body=None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"API Error ({status_code}): {message}")


class RateLimitError(ResponseError):
    """Raised when rate limits are exceeded."""


class DataError(LegacyERPError):
    """Raised when there's an issue with the data format."""


class SessionError(LegacyERPError):
    """Raised when there's an issue with the session management."""


class ConfigurationError(LegacyERPError):
    """Raised when there's an issue with the API configuration."""
