"""
Unit tests for the asgi.py module.
"""

import os
import pytest
import importlib
from unittest.mock import patch, MagicMock
import sys


@pytest.mark.unit
class TestASGIConfiguration:
    """Tests for ASGI configuration in pyerp.asgi."""

    def test_asgi_module_exists(self):
        """Test the ASGI module exists and has the required attributes."""
        import pyerp.asgi
        
        # Verify the module has an application attribute
        assert hasattr(pyerp.asgi, 'application')
        
    @patch('django.core.asgi.get_asgi_application')
    def test_get_asgi_application_called(self, mock_get_asgi_application):
        """Test that get_asgi_application is called during module import."""
        # Configure the mock
        mock_asgi_app = MagicMock()
        mock_get_asgi_application.return_value = mock_asgi_app
        
        # Clear the module if it's already imported
        if 'pyerp.asgi' in sys.modules:
            del sys.modules['pyerp.asgi']
            
        # Import the module (which will trigger get_asgi_application)
        import pyerp.asgi
        
        # Verify get_asgi_application was called
        mock_get_asgi_application.assert_called_once()
        
    def test_django_settings_module_set(self):
        """Test that DJANGO_SETTINGS_MODULE environment variable is set."""
        # Import the module
        import pyerp.asgi
        
        # Verify DJANGO_SETTINGS_MODULE is set to some value
        assert 'DJANGO_SETTINGS_MODULE' in os.environ
        assert os.environ['DJANGO_SETTINGS_MODULE'].startswith('pyerp.config.settings') 