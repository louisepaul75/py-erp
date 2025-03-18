"""
Django app configuration for the monitoring app.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MonitoringAppConfig(AppConfig):
    """Configuration for the monitoring app."""

    name = "pyerp.monitoring"
    verbose_name = _("Monitoring")

    def ready(self):
        """
        Import signals to register them.
        """
        try:
            # Using import inside a function to avoid circular imports
            import pyerp.monitoring.signals  # noqa: F401
        except ImportError:
            pass
