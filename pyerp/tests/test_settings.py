"""
Test settings for pyERP project.

These settings override the base settings with test-specific configurations.
"""

from pyerp.config.settings.base import *  # noqa

# Configure debug settings
DEBUG = True

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

# Configure template settings for tests
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "pyerp", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
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
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}

# REST Framework test settings
REST_FRAMEWORK = {
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, "media", "test")
MEDIA_URL = "/media/test/"

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles", "test")
STATIC_URL = "/static/test/"

# Test-specific settings
TEST_RUNNER = "django.test.runner.DiscoverRunner" 