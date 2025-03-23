"""
Tests for the WSGI configuration.
"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest


@pytest.mark.unit
class TestWSGIConfiguration:
    """Test the WSGI configuration module."""

    def test_wsgi_module_exists(self):
        """Verify that the WSGI module can be imported."""
        try:
            import pyerp.wsgi
            assert hasattr(pyerp.wsgi, 'application')
        except ImportError:
            pytest.fail("Could not import the WSGI module")

    @patch('pyerp.utils.env_loader.load_environment_variables')
    def test_environment_variables_loaded(self, mock_load_env):
        """Test that environment variables are loaded."""
        # Clear the module from sys.modules to force reload
        if 'pyerp.wsgi' in sys.modules:
            del sys.modules['pyerp.wsgi']
        
        # Import the module to trigger environment loading
        import pyerp.wsgi
        
        # Verify the function was called
        mock_load_env.assert_called_once()

    @patch('os.environ.setdefault')
    def test_django_settings_module_set(self, mock_setdefault):
        """Test that the Django settings module is set if not defined."""
        # Clear the module from sys.modules to force reload
        if 'pyerp.wsgi' in sys.modules:
            del sys.modules['pyerp.wsgi']
        
        # Import the module to trigger settings module setting
        import pyerp.wsgi
        
        # Verify the function was called with expected arguments
        mock_setdefault.assert_called_with(
            "DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development"
        )

    @patch('django.core.wsgi.get_wsgi_application')
    def test_get_wsgi_application_called(self, mock_get_app):
        """Test that get_wsgi_application is called to initialize the WSGI app."""
        # Configure mock
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app
        
        # Clear the module from sys.modules to force reload
        if 'pyerp.wsgi' in sys.modules:
            del sys.modules['pyerp.wsgi']
        
        # Import the module to trigger application creation
        import pyerp.wsgi
        
        # Verify the function was called
        mock_get_app.assert_called_once()
        
        # Verify the application attribute is set correctly
        assert pyerp.wsgi.application == mock_app 