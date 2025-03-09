"""
Tests for the direct_api exceptions module.
"""

from django.test import TestCase

from pyerp.direct_api.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError as APIConnectionError,
    DataError,
    DirectAPIError,
    RateLimitError,
    ResponseError,
    SessionError,
)


class TestExceptions(TestCase):
    """Tests for the exceptions module."""

    def test_base_exception(self):
        """Test the base DirectAPIError exception."""
        error = DirectAPIError("Test error message")
        self.assertEqual(str(error), "Test error message")

    def test_response_error(self):
        """Test the ResponseError exception."""
        error = ResponseError(400, "Bad request")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(str(error), "API error 400: Bad request")

        # Create an instance with response_body
        error = ResponseError(
            status_code=500,
            message="Server error",
            response_body={"error": "Internal server error"},
        )
        self.assertEqual(error.status_code, 500)
        self.assertEqual(
            error.response_body,
            {"error": "Internal server error"}
        )

    def test_connection_error(self):
        """Test the ConnectionError exception."""
        error = APIConnectionError("Connection refused")
        self.assertEqual(str(error), "Connection refused")

        # Check inheritance from DirectAPIError
        self.assertIsInstance(error, DirectAPIError)

    def test_authentication_error(self):
        """Test the AuthenticationError exception."""
        error = AuthenticationError("Invalid credentials")
        self.assertEqual(str(error), "Invalid credentials")

        # Check inheritance
        self.assertIsInstance(error, DirectAPIError)

    def test_data_error(self):
        """Test the DataError exception."""
        error = DataError("Invalid data format")
        self.assertEqual(str(error), "Invalid data format")

        # Check inheritance
        self.assertIsInstance(error, DirectAPIError)

    def test_rate_limit_error(self):
        """Test the RateLimitError exception."""
        error = RateLimitError(429, "Too many requests")
        self.assertEqual(str(error), "API error 429: Too many requests")

        # Check inheritance
        self.assertIsInstance(error, ResponseError)

    def test_session_error(self):
        """Test the SessionError exception."""
        error = SessionError("Session expired")
        self.assertEqual(str(error), "Session expired")

        # Check inheritance
        self.assertIsInstance(error, DirectAPIError)

    def test_configuration_error(self):
        """Test the ConfigurationError exception."""
        error = ConfigurationError("Missing API URL")
        self.assertEqual(str(error), "Missing API URL")

        # Check inheritance
        self.assertIsInstance(error, DirectAPIError)

    def test_exception_hierarchy(self):
        """Test the exception inheritance hierarchy."""
        base_error = DirectAPIError("Base error")
        response_error = ResponseError(400, "Response error")
        connection_error = APIConnectionError("Connection error")
        auth_error = AuthenticationError("Auth error")
        data_error = DataError("Data error")
        rate_limit_error = RateLimitError(429, "Rate limit error")

        # Test that all exceptions inherit from DirectAPIError
        self.assertIsInstance(base_error, DirectAPIError)
        self.assertIsInstance(response_error, DirectAPIError)
        self.assertIsInstance(connection_error, DirectAPIError)
        self.assertIsInstance(auth_error, DirectAPIError)
        self.assertIsInstance(data_error, DirectAPIError)
        self.assertIsInstance(rate_limit_error, DirectAPIError)

        # Test specific inheritance relationships
        self.assertIsInstance(response_error, ResponseError)
        self.assertIsInstance(auth_error, AuthenticationError)
        self.assertIsInstance(rate_limit_error, ResponseError)

        # Test that exceptions can be caught by their parent types
        try:
            raise auth_error
        except DirectAPIError as e:
            self.assertEqual(e, auth_error)

        try:
            raise rate_limit_error
        except ResponseError as e:
            self.assertEqual(e, rate_limit_error)
