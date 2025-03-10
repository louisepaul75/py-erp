"""
Unit tests for the legacy ERP API exceptions.

These tests verify that the exception classes work correctly and provide
appropriate error information.
"""

import unittest

from pyerp.external_api.legacy_erp.exceptions import (
    LegacyERPError,
    ConnectionError,
    AuthenticationError,
    ResponseError,
)


class TestLegacyERPExceptions(unittest.TestCase):
    """Test cases for legacy ERP API exceptions."""

    def test_legacy_erp_error(self):
        """Test the base LegacyERPError exception."""
        error = LegacyERPError("Test error message")
        self.assertEqual(str(error), "Test error message")

    def test_connection_error(self):
        """Test the ConnectionError exception."""
        error = ConnectionError("Failed to connect to API")
        self.assertEqual(str(error), "Failed to connect to API")
        self.assertIsInstance(error, LegacyERPError)

    def test_authentication_error(self):
        """Test the AuthenticationError exception."""
        error = AuthenticationError("Invalid credentials")
        self.assertEqual(str(error), "Invalid credentials")
        self.assertIsInstance(error, LegacyERPError)

    def test_response_error(self):
        """Test the ResponseError exception."""
        error = ResponseError(404, "Resource not found")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(str(error), "API Error (404): Resource not found")
        self.assertIsInstance(error, LegacyERPError)


if __name__ == "__main__":
    unittest.main()
