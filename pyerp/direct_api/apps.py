"""
Django application configuration for the direct_api app.
"""

from django.apps import AppConfig


class DirectApiConfig(AppConfig):
    """Configuration for the direct_api app."""
    
    name = 'pyerp.direct_api'
    verbose_name = 'Direct API Client for Legacy ERP'
    
    def ready(self):
        """
        Initialize the app when Django starts.
        """
        # Import signals or perform other initialization here
        pass 