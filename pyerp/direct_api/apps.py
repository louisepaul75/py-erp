"""
Django application configuration for the direct_api app.
"""

from django.apps import AppConfig


class DirectApiConfig(AppConfig):
    """Configuration for the direct_api app."""

    name = 'pyerp.direct_api'  # noqa: F841
    verbose_name = 'Direct API Client for Legacy ERP'  # noqa: F841
  # noqa: F841

    def ready(self):
        """
        Initialize the app when Django starts.
        """
        # Import signals or perform other initialization here
        pass
