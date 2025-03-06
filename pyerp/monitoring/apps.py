"""
Django app configuration for the monitoring app.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _  # noqa: F401


class MonitoringAppConfig(AppConfig):
    """Configuration for the monitoring app."""

    name = 'pyerp.monitoring'  # noqa: F841
    verbose_name = _('Monitoring')  # noqa: F841

    def ready(self):
        """
        Initialize app when Django starts.
        This is where we can register signal handlers or perform other initialization.  # noqa: E501
        """
        try:
            import pyerp.monitoring.signals  # noqa
        except ImportError:
            pass
