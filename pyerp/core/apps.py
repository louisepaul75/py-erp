"""
Core app configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _  # noqa: F401


class CoreConfig(AppConfig):
    """Configuration for the core app."""

    default_auto_field = 'django.db.models.BigAutoField'  # noqa: F841
  # noqa: F841
    name = 'pyerp.core'  # noqa: F841
    verbose_name = _('Core')  # noqa: F841
  # noqa: F841

    def ready(self):
        """
        Initialize app when Django is ready.
        Import signals to ensure they are registered.
        """
        # Import signals to ensure they are registered
        import pyerp.core.signals  # noqa
