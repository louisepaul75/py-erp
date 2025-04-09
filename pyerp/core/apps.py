"""
Core app configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# Import necessary modules for profiling
import os
import logging

logger = logging.getLogger(__name__)


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
        from pyerp.utils.logging.logging_init import (
            initialize_logging,
            register_app_loggers,
        )
        from django.apps import apps

        initialize_logging()
        register_app_loggers(apps.get_app_configs())

        # Configure memory profiler if enabled
        if os.environ.get("ENABLE_MEMORY_PROFILING", "false").lower() == "true":
            try:
                from pyerp.core import memory_profiler
                # Use process ID to distinguish snapshots from different workers
                identifier = f"gunicorn_worker_{os.getpid()}"
                memory_profiler.configure_profiler(identifier)
                logger.info(f"CoreConfig: Memory profiler configured for {identifier}.")
            except ImportError:
                logger.error("CoreConfig: Failed to import memory_profiler. Profiling disabled.")
            except Exception as e:
                logger.error(f"CoreConfig: Error configuring memory profiler: {e}", exc_info=True)
        else:
            logger.debug("CoreConfig: Memory profiling not enabled.")
