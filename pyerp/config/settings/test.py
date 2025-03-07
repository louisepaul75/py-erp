"""
Test settings for pyERP project.

These settings extend the development settings with test-specific configurations.  # noqa: E501
"""

from .development import *  # noqa
import os
import sys
import socket  # noqa: F401
import psycopg2
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

# Define PostgreSQL connection parameters
PG_PARAMS = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("DB_NAME", "pyerp_testing"),
    "USER": os.environ.get("DB_USER", "postgres"),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST": os.environ.get("DB_HOST", "192.168.73.65"),
    "PORT": os.environ.get("DB_PORT", "5432"),
    "TEST": {
        "NAME": "test_pyerp_testing",
    },
}

# Define SQLite connection parameters as fallback
SQLITE_PARAMS = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": "file:memorydb_default?mode=memory&cache=shared",
    "TEST": {
        "NAME": "file:memorydb_default?mode=memory&cache=shared",
    },
}

# Try to connect to PostgreSQL, fall back to SQLite if connection fails
try:
    print(
        "Attempting to connect to PostgreSQL at {}:{}".format(
            PG_PARAMS["HOST"],
            PG_PARAMS["PORT"],
        ),
    )
    conn = psycopg2.connect(
        dbname=PG_PARAMS["NAME"],
        user=PG_PARAMS["USER"],
        password=PG_PARAMS["PASSWORD"],
        host=PG_PARAMS["HOST"],
        port=PG_PARAMS["PORT"],
        connect_timeout=5,
    )
    conn.close()
    print("SUCCESS: Connected to PostgreSQL")
    DATABASES = {"default": PG_PARAMS}
except Exception as e:
    print("ERROR: Could not connect to PostgreSQL:", str(e))
    print("\nFALLBACK: Using SQLite for testing")
    DATABASES = {"default": SQLITE_PARAMS}

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
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.MultiPartRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
