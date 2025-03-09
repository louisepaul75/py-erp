"""
Tests for the direct_api settings module.
"""

import os

from django.test import TestCase, override_settings

from pyerp.direct_api.settings import (
    API_BASE_URL,
    API_ENVIRONMENTS,
    API_PAGINATION_ENABLED,
    API_PAGINATION_SIZE,
    API_REQUEST_TIMEOUT,
    API_SESSION_EXPIRY,
)


class TestSettings(TestCase):
    """Tests for the settings module."""

    def test_base_url_setting(self):
        """Test API_BASE_URL setting."""
        self.assertIsInstance(API_BASE_URL, str)
        self.assertTrue(len(API_BASE_URL) > 0)

    def test_environments_setting(self):
        """Test API_ENVIRONMENTS setting."""
        self.assertIsInstance(API_ENVIRONMENTS, dict)
        self.assertIn("live", API_ENVIRONMENTS)
        self.assertIn("test", API_ENVIRONMENTS)

        # Check structure of environment settings
        live_env = API_ENVIRONMENTS["live"]
        self.assertIn("base_url", live_env)
        self.assertIn("username", live_env)
        self.assertIn("password", live_env)

    @override_settings(LEGACY_API_BASE_URL="https://custom-api.example.com")
    def test_override_base_url(self):
        """Test overriding API_BASE_URL through Django settings."""
        import importlib

        from pyerp.direct_api import settings as api_settings

        # Clear any environment variables that might override settings
        if "LEGACY_ERP_API_LIVE" in os.environ:
            del os.environ["LEGACY_ERP_API_LIVE"]

        importlib.reload(api_settings)

        # Check that the override was applied
        self.assertEqual(api_settings.API_BASE_URL, "https://custom-api.example.com")

        # Restore original settings
        importlib.reload(api_settings)

    def test_timeout_setting(self):
        """Test API_REQUEST_TIMEOUT setting."""
        self.assertIsInstance(API_REQUEST_TIMEOUT, int)
        self.assertGreater(API_REQUEST_TIMEOUT, 0)

    def test_session_expiry_setting(self):
        """Test API_SESSION_EXPIRY setting."""
        self.assertIsInstance(API_SESSION_EXPIRY, int)
        self.assertGreater(API_SESSION_EXPIRY, 0)

    def test_pagination_settings(self):
        """Test pagination settings."""
        self.assertIsInstance(API_PAGINATION_ENABLED, bool)
        self.assertIsInstance(API_PAGINATION_SIZE, int)
        self.assertGreater(API_PAGINATION_SIZE, 0)

    @override_settings(
        LEGACY_API_ENVIRONMENTS={
            "custom": {
                "base_url": "https://custom.example.com",
                "username": "custom_user",
                "password": "custom_pass",
            },
        },
    )
    def test_override_environments(self):
        """Test overriding API_ENVIRONMENTS through Django settings."""
        import importlib

        from pyerp.direct_api import settings as api_settings

        importlib.reload(api_settings)

        # Check that the override was applied
        self.assertIn("custom", api_settings.API_ENVIRONMENTS)
        custom_env = api_settings.API_ENVIRONMENTS["custom"]
        self.assertEqual(custom_env["base_url"], "https://custom.example.com")
        self.assertEqual(custom_env["username"], "custom_user")

        # Restore original settings
        importlib.reload(api_settings)
