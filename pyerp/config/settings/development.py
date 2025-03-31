"""
Development settings for pyERP project.

These settings extend the base settings with development-specific configurations.
"""

import os
import sys
from datetime import timedelta

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
DEBUG_PROPAGATE_EXCEPTIONS = True

# Prevent Django from automatically appending trailing slashes to URLs
# This fixes issues with PATCH requests where the browser might strip the trailing slash
APPEND_SLASH = False

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
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:5173",
    "http://localhost:8050",
    "http://127.0.0.1:8050",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000"
]

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
    "access-control-allow-origin",
    "access-control-allow-credentials",
]

CORS_EXPOSE_HEADERS = [
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "set-cookie"
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
        "AUTH_COOKIE_HTTP_ONLY": True,
        "AUTH_COOKIE_SAMESITE": "Lax",
        "AUTH_COOKIE_PATH": "/",
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
EMAIL_BACKEND = "pyerp.utils.email_system.backends.LoggingEmailBackend"

# 1Password Connect settings
EMAIL_USE_1PASSWORD = os.environ.get("EMAIL_USE_1PASSWORD", "").lower() == "true"
EMAIL_1PASSWORD_ITEM_NAME = os.environ.get("EMAIL_1PASSWORD_ITEM_NAME", "")
OP_CONNECT_HOST = os.environ.get("OP_CONNECT_HOST", "http://192.168.73.65:8080")
OP_CONNECT_TOKEN = os.environ.get("OP_CONNECT_TOKEN", "")
OP_CONNECT_VAULT = os.environ.get("OP_CONNECT_VAULT", "dev")

# Import anymail settings for reference, but use console backend
from .anymail import *  # noqa

# Override anymail settings for development
ANYMAIL = {
    **ANYMAIL,
    "DEBUG_API_REQUESTS": True,
}

# Add email_system to installed apps
INSTALLED_APPS += ["pyerp.utils.email_system"]  # noqa

# Set this to True to actually send emails in development (using the configured ESP)
USE_ANYMAIL_IN_DEV = os.environ.get("USE_ANYMAIL_IN_DEV", "").lower() == "true"
if USE_ANYMAIL_IN_DEV:
    # Always use the logging email backend for simplicity in development
    EMAIL_BACKEND = "pyerp.utils.email_system.backends.LoggingEmailBackend"

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
