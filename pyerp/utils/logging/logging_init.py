"""
Logging initialization for pyERP

This module initializes the centralized logging system at application startup.
It should be imported early in the application lifecycle, typically in the 
Django AppConfig's ready() method or in the settings module.
"""

import os
import logging

from django.conf import settings
from django.utils.module_loading import import_string

from pyerp.utils import logging as pyerp_logging


def initialize_logging():
    """
    Initialize the centralized logging system.
    This function should be called once at application startup.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(settings.BASE_DIR, "logs"), exist_ok=True)

    # Configure Django's loggers to use our centralized configuration
    pyerp_logging.configure_django_loggers()

    # Get the root logger and configure it
    root_logger = logging.getLogger()

    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Set the root logger level
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Add a console handler in development
    if settings.DEBUG:
        root_logger.addHandler(pyerp_logging.create_console_handler())

    # Add a file handler for critical errors
    error_handler = pyerp_logging.create_file_handler("errors.log", logging.ERROR)
    root_logger.addHandler(error_handler)

    # Set up loggers for third-party libraries at appropriate levels
    third_party_loggers = {
        "urllib3": "WARNING",
        "requests": "WARNING",
        "celery": "INFO",
        "django.db.backends": "WARNING",
        "django.security": "INFO",
    }

    for logger_name, level in third_party_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level))

    # Log startup message
    startup_logger = pyerp_logging.get_logger("pyerp.startup")
    startup_logger.info(f"Logging initialized with LOG_LEVEL={settings.LOG_LEVEL}")


def register_app_loggers(app_configs):
    """
    Register loggers for Django applications.
    This can be called with Django's apps.get_app_configs() to set up
    loggers for all installed apps.

    Args:
        app_configs: List of Django AppConfig instances
    """
    for app_config in app_configs:
        app_name = app_config.name

        # Only configure pyerp apps
        if app_name.startswith("pyerp."):
            # Try to import a custom logger initializer if it exists
            try:
                initializer = import_string(f"{app_name}.logging.initialize")
                initializer()
            except (ImportError, AttributeError):
                # No custom initializer, set up a standard logger
                logger = pyerp_logging.get_logger(app_name)
                logger.setLevel(getattr(logging, settings.LOG_LEVEL))
