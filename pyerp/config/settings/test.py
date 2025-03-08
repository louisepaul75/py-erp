"""
Test settings for pyERP project.

These settings extend the development settings with test-specific configurations.  # noqa: E501
"""

from .development import *  # noqa
import sys
import socket  # noqa: F401
from pathlib import Path  # noqa: F401
from .base import *

# Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables

load_environment_variables(verbose=True)

# Remove debug toolbar from installed apps
if "debug_toolbar" in INSTALLED_APPS:
    INSTALLED_APPS.remove("debug_toolbar")

# Remove debug toolbar middleware
if "debug_toolbar.middleware.DebugToolbarMiddleware" in MIDDLEWARE:
    MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")

# Configure debug toolbar for tests
DEBUG_TOOLBAR_CONFIG = {
    "IS_RUNNING_TESTS": True,
}

# Configure model field types for Python 3.12
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
FIELD_TYPES = {
    "AutoField": "django.db.models.BigAutoField",
    "BigAutoField": "django.db.models.BigAutoField",
    "SmallAutoField": "django.db.models.SmallAutoField",
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}

# REST Framework test settings
REST_FRAMEWORK = {
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.MultiPartRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}
