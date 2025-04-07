"""
Test settings for pyERP project.

These settings extend the development settings with test-specific configurations.  # noqa: E501
"""

from .development import *  # noqa
import socket  # noqa: F401
from pathlib import Path  # noqa: F401
from .base import *
import os

# Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables

load_environment_variables(verbose=True)

# Remove debug toolbar from installed apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]

# Remove debug toolbar middleware
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

# Configure debug toolbar for tests
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: False,
    "IS_RUNNING_TESTS": False,
}

# Configure model field types for Django 5.x and Python 3.12
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configure database for tests - use file-based SQLite for better compatibility
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
        "TEST": {
            "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
        },
    }
}

# Configure migrations for tests
# MIGRATION_MODULES = {}  # Empty dictionary for migrations - Commented out to allow normal migrations

# Disable transaction management for tests to avoid SQLite issues
DATABASE_ROUTERS = []
# Add 'pyerp.sync' to prevent serialization issues during test setup
TEST_NON_SERIALIZED_APPS = ['pyerp.sync']

# Configure URL patterns for tests - USE MINIMAL URLS FOR ISOLATION
ROOT_URLCONF = 'pyerp.urls'

# Configure template settings for tests
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(BASE_DIR / "pyerp" / "templates"),
            str(BASE_DIR / "pyerp" / "business_modules" / "products" / "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
        },
    },
]

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Configure logging for tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
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

# Ensure models are created without migrations
# This is handled by MIGRATION_MODULES now

# Disable Celery for testing if requested
if os.environ.get("SKIP_CELERY_IMPORT") == "1":
    # Remove Celery apps from INSTALLED_APPS
    INSTALLED_APPS = [
        app for app in INSTALLED_APPS 
        if not any(celery_app in app.lower() for celery_app in [
            'celery', 
            'kombu', 
            'django_celery_results',
            'django_celery_beat'
        ])
    ]

# Media files
MEDIA_ROOT = Path(BASE_DIR).parent / "media" / "test"
MEDIA_URL = "/media/test/"

# Static files
STATIC_ROOT = Path(BASE_DIR).parent / "staticfiles" / "test"
STATIC_URL = "/static/test/"

# Disable external API calls
EXTERNAL_API_MOCK = True

# Dummy locations for S3 storage backends during tests
STATIC_LOCATION = "static-test"
MEDIA_LOCATION = "media-test"

# Test-specific settings
TEST_RUNNER = "django.test.runner.DiscoverRunner"
TEST_OUTPUT_DIR = Path(BASE_DIR).parent / "tests" / "output"
