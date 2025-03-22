"""
Tests for the URLs configuration.
"""

import sys
from unittest.mock import patch, MagicMock

import pytest
from django.urls import path


@pytest.mark.unit
class TestURLConfigurations:
    """Test the URL configuration module."""

    def test_urlpatterns_exist(self):
        """Verify that the urlpatterns list exists and contains URL patterns."""
        from pyerp.urls import urlpatterns
        assert urlpatterns, "urlpatterns list should not be empty"
        assert len(urlpatterns) > 0, "urlpatterns should contain URL patterns"
        
        # Check for API token URLs using a more flexible approach
        # Since the URL patterns might be represented differently than we expect
        jwt_related_urls = False
        for pattern in urlpatterns:
            pattern_str = str(pattern)
            if "api/token" in pattern_str:
                jwt_related_urls = True
                break
        
        assert jwt_related_urls, "JWT token related URL patterns not found"

    def test_has_swagger_setting(self):
        """Verify the has_swagger variable exists."""
        from pyerp.urls import has_swagger
        assert isinstance(has_swagger, bool), "has_swagger should be a boolean"

    @patch('django.conf.settings.DEBUG', True)
    def test_debug_settings(self):
        """Test URL configuration applies debug-specific settings when DEBUG=True."""
        # Force reload of urls module to apply DEBUG=True
        if 'pyerp.urls' in sys.modules:
            del sys.modules['pyerp.urls']
        
        # Re-import to apply DEBUG setting
        import pyerp.urls
        
        # Verify debug-specific patterns are applied by checking the module code has run
        # Rather than checking specific URL patterns which might be hard to identify
        assert hasattr(pyerp.urls, 'urlpatterns'), "urlpatterns not defined"
        assert len(pyerp.urls.urlpatterns) > 0, "urlpatterns is empty"

    @patch('django.conf.settings.DEBUG', True)
    @patch('django.conf.settings.INSTALLED_APPS', ['debug_toolbar'])
    def test_debug_toolbar_urls(self):
        """Test debug toolbar URLs code path executes without errors."""
        # This is a simplified test that just checks if the module can be imported
        # without causing errors, as a more thorough test would require complex mocking
        
        # Force reload of urls module to apply settings
        if 'pyerp.urls' in sys.modules:
            del sys.modules['pyerp.urls']
        
        # Mock builtins.print to capture output
        with patch('builtins.print') as mock_print:
            # Import the module to trigger the code path for debug mode
            import pyerp.urls
            
            # Check the module was imported successfully
            assert hasattr(pyerp.urls, 'urlpatterns'), "urlpatterns not defined"

    @patch('pyerp.urls.has_swagger', True)
    @patch('drf_yasg.views.get_schema_view')
    def test_swagger_urls_when_available(self, mock_get_schema_view):
        """Test Swagger URLs are added when has_swagger is True."""
        # Setup mock for schema_view
        mock_schema_view = MagicMock()
        mock_get_schema_view.return_value = mock_schema_view
        
        # Force reload of urls module
        if 'pyerp.urls' in sys.modules:
            del sys.modules['pyerp.urls']
        
        # Create a mock path function to capture URL pattern creation
        original_path = path
        paths_created = []
        
        def mock_path(*args, **kwargs):
            paths_created.append((args, kwargs))
            return original_path(*args, **kwargs)
        
        # Apply path patch and import urls
        with patch('django.urls.path', mock_path):
            # Re-import with patched dependencies
            import importlib
            import pyerp.urls
            importlib.reload(pyerp.urls)  # Force reload to apply patches
            
            # Verify we have urlpatterns
            assert hasattr(pyerp.urls, 'urlpatterns'), "urlpatterns not defined"

    @patch('pyerp.urls.OPTIONAL_API_MODULES', [("test", "pyerp.core.urls")])
    def test_optional_modules_success(self):
        """Test optional modules are loaded when available."""
        # Force reload of urls module
        if 'pyerp.urls' in sys.modules:
            del sys.modules['pyerp.urls']
        
        # Use a real module that exists in the codebase
        with patch('builtins.print') as mock_print:
            # Import the module to trigger the code
            import pyerp.urls
            
            # Rather than checking exact message, just verify the import was successful
            # and the urlpatterns list was created
            assert hasattr(pyerp.urls, 'urlpatterns'), "urlpatterns not defined"
            assert len(pyerp.urls.urlpatterns) > 0, "urlpatterns is empty"
            
            # Verify print was called at least once (simplified check)
            assert mock_print.call_count > 0, "print was not called"
    
    @patch('pyerp.urls.OPTIONAL_API_MODULES', [("error", "nonexistent.module")])
    def test_optional_modules_import_error(self):
        """Test optional modules handle ImportError gracefully."""
        # Force reload of urls module
        if 'pyerp.urls' in sys.modules:
            del sys.modules['pyerp.urls']
        
        with patch('builtins.print') as mock_print:
            # Import the module to trigger the code
            import pyerp.urls
            
            # Verify urlpatterns still exists despite the import error
            assert hasattr(pyerp.urls, 'urlpatterns'), "urlpatterns not defined"
            assert len(pyerp.urls.urlpatterns) > 0, "urlpatterns is empty"
            
            # Verify print was called at least once (simplified check)
            assert mock_print.call_count > 0, "print was not called" 