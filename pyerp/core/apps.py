"""
Core app configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    """Configuration for the core app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pyerp.core"
    verbose_name = _("Core")

    def ready(self):
        """
        Initialize app when Django is ready.
        Import signals to ensure they are registered.
        """
        # Import signals to ensure they are registered
        from . import signals  # noqa

        # Initialize the centralized logging system
        from pyerp.utils.logging.logging_init import initialize_logging

        initialize_logging()
