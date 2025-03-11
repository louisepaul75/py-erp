"""
Development settings for pyERP project.

These settings extend the base settings with development-specific configurations.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url  # noqa: F401
import psycopg2

from .base import *  # noqa
from .base import BASE_DIR, SIMPLE_JWT

# Import HTTPS settings
try:
    from .settings_https import *  # noqa
except ImportError:
    pass

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"

# Get ALLOWED_HOSTS from environment variable
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1",
).split(",")

# Database configuration with SQLite fallback
# Define PostgreSQL connection parameters
PG_PARAMS = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("DB_NAME", "pyerp_testing"),
    "USER": os.environ.get("DB_USER", "postgres"),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST": os.environ.get("DB_HOST", "192.168.73.65"),
    "PORT": os.environ.get("DB_PORT", "5432"),
    "OPTIONS": {
        "connect_timeout": 10,  # Connection timeout in seconds
        "client_encoding": "UTF8",
        "sslmode": "prefer",
        "gssencmode": "disable",  # Disable GSSAPI/Kerberos encryption
    },
}

# Define SQLite connection parameters as fallback
SQLITE_PARAMS = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "development_db.sqlite3"),
}

# Try to connect to PostgreSQL, use SQLite if it fails
try:
    sys.stderr.write(
        "Attempting to connect to PostgreSQL at "
        f"{PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n",
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
    DATABASES = {"default": PG_PARAMS}
    sys.stderr.write(
        "SUCCESS: Using PostgreSQL database at "
        f"{PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n",
    )
except (OSError, psycopg2.OperationalError) as e:
    sys.stderr.write(f"ERROR: Could not connect to PostgreSQL: {e!s}\n")
    sys.stderr.write("FALLBACK: Using SQLite for development\n")
    DATABASES = {"default": SQLITE_PARAMS}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = (
    os.environ.get("CORS_ALLOW_ALL_ORIGINS", "True").lower() == "true"
)
CORS_ALLOW_CREDENTIALS = (
    os.environ.get("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
)
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000",
).split(",")

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Logging configuration for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.security.authentication": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "rest_framework_simplejwt": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# JWT settings for development
SIMPLE_JWT.update(
    {
        "ACCESS_TOKEN_LIFETIME": timedelta(
            days=1,
        ),  # Longer lifetime for development
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
        "AUTH_COOKIE_SECURE": False,  # Allow non-HTTPS in development
    },
)

# DEBUG TOOLBAR SETTINGS
INSTALLED_APPS += ["debug_toolbar"]  # noqa
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa

INTERNAL_IPS = [
    "127.0.0.1",
]

# Django Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Import anymail settings for reference, but use console backend
from .anymail import *  # noqa

# Override anymail settings for development
ANYMAIL = {
    **ANYMAIL,
    "DEBUG_API_REQUESTS": True,
}

# Set this to True to actually send emails in development (using the configured ESP)
USE_ANYMAIL_IN_DEV = os.environ.get("USE_ANYMAIL_IN_DEV", "").lower() == "true"
if USE_ANYMAIL_IN_DEV:
    # If ANYMAIL_ESP is set to "smtp", use the standard Django SMTP backend
    if os.environ.get("ANYMAIL_ESP", "").lower() == "smtp":
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    else:
        # Otherwise use the anymail backend for the specified ESP
        EMAIL_BACKEND = "anymail.backends.{esp_name}.EmailBackend".format(
            esp_name=os.environ.get("ANYMAIL_ESP", "sendgrid").lower()
        )

# Disable password validators during development
AUTH_PASSWORD_VALIDATORS = []

# For development, disable CSRF token check
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Local development specific REST Framework settings
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] += [  # noqa
    "rest_framework.authentication.BasicAuthentication",
]

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = (
    os.environ.get("CELERY_TASK_ALWAYS_EAGER", "True").lower() == "true"
)
