"""
Testing settings for pyERP project.

These settings extend the base settings with testing-specific configurations
focused on test performance and isolation.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

from .base import *

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
env_path = PROJECT_ROOT / "config" / "env" / ".env"
print(f"Loading environment variables from: {env_path}")
load_dotenv(dotenv_path=env_path)

# Print environment variables for debugging
print(f"DB_NAME: {os.environ.get('DB_NAME', 'not set')}")
print(f"DB_USER: {os.environ.get('DB_USER', 'not set')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD', 'not set')}")
print(f"DB_HOST: {os.environ.get('DB_HOST', 'not set')}")
print(f"DB_PORT: {os.environ.get('DB_PORT', 'not set')}")

# Configure for test environment
DEBUG = True

# Remove debug toolbar for tests
if "debug_toolbar" in INSTALLED_APPS:
    INSTALLED_APPS.remove("debug_toolbar")

MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE if "debug_toolbar" not in middleware
]

ALLOWED_HOSTS = ["*"]

# Database configuration for tests
# Try to use PostgreSQL first, fall back to SQLite if connection fails

import psycopg2

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

# Use the fastest possible password hasher
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Simplify password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Disable template debug mode for faster tests
for template in TEMPLATES:
    template["OPTIONS"]["debug"] = False

# Use console email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

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

# Celery settings for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable migrations when running tests


class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Use simple caching for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# Disable CSRF validation in tests
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Media settings for tests
MEDIA_ROOT = BASE_DIR / "test_media"

# Debug toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    "IS_RUNNING_TESTS": False,
}
