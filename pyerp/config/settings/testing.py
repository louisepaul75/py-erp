"""
Testing settings for pyERP project.

These settings extend the base settings with testing-specific configurations
focused on test performance and isolation.
"""

import os
import sys
import dj_database_url  # noqa: F401
from .base import *  # noqa
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
# Load environment variables from .env file
env_path = PROJECT_ROOT / 'config' / 'env' / '.env'
print(f"Loading environment variables from: {env_path}")
load_dotenv(dotenv_path=env_path)
  # noqa: F841

# Print environment variables for debugging
print(f"DB_NAME: {os.environ.get('DB_NAME', 'not set')}")
print(f"DB_USER: {os.environ.get('DB_USER', 'not set')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD', 'not set')}")
print(f"DB_HOST: {os.environ.get('DB_HOST', 'not set')}")
print(f"DB_PORT: {os.environ.get('DB_PORT', 'not set')}")

# Configure for test environment
DEBUG = True  # noqa: F841

# Remove debug toolbar for tests
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'debug_toolbar' not in middleware]  # noqa: E501
  # noqa: E501, F841

ALLOWED_HOSTS = ['*']
  # noqa: F841

# Database configuration for tests
# Try to use PostgreSQL first, fall back to SQLite if connection fails
import socket  # noqa: F401
import psycopg2

# Define PostgreSQL connection parameters
PG_PARAMS = {
    'ENGINE': 'django.db.backends.postgresql',  # noqa: E128
    'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
    'USER': os.environ.get('DB_USER', 'postgres'),
    'PASSWORD': os.environ.get('DB_PASSWORD', ''),
    'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
    'PORT': os.environ.get('DB_PORT', '5432'),
    'TEST': {
        'NAME': 'test_pyerp_testing',  # noqa: E128
    },
}

# Define SQLite connection parameters as fallback
SQLITE_PARAMS = {
    'ENGINE': 'django.db.backends.sqlite3',  # noqa: E128
    'NAME': 'file:memorydb_default?mode=memory&cache=shared',
    'TEST': {
        'NAME': 'file:memorydb_default?mode=memory&cache=shared',  # noqa: E128
    },
}

# Try to connect to PostgreSQL, fall back to SQLite if connection fails
try:
    print("Attempting to connect to PostgreSQL at {}:{}".format(PG_PARAMS['HOST'], PG_PARAMS['PORT']))  # noqa: E501
    conn = psycopg2.connect(
        dbname=PG_PARAMS['NAME'],  # noqa: F841
  # noqa: F841
        user=PG_PARAMS['USER'],  # noqa: F841
  # noqa: F841
        password=PG_PARAMS['PASSWORD'],  # noqa: F841
        host=PG_PARAMS['HOST'],  # noqa: F841
  # noqa: F841
        port=PG_PARAMS['PORT'],  # noqa: F841
  # noqa: F841
        connect_timeout=5  # noqa: F841
  # noqa: F841
    )
    conn.close()
    print("SUCCESS: Connected to PostgreSQL")
    DATABASES = {'default': PG_PARAMS}  # noqa: F841
except Exception as e:
    print("ERROR: Could not connect to PostgreSQL:", str(e))
    print("\nFALLBACK: Using SQLite for testing")
    DATABASES = {'default': SQLITE_PARAMS}  # noqa: F841
  # noqa: F841

# Use the fastest possible password hasher
PASSWORD_HASHERS = [
  # noqa: F841
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Simplify password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []
  # noqa: F841

# Disable template debug mode for faster tests
for template in TEMPLATES:
    template['OPTIONS']['debug'] = False

# Use console email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
  # noqa: F841

# Disable logging during tests
LOGGING = {
  # noqa: F841
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {  # noqa: E128
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'django': {  # noqa: E128
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# Celery settings for testing
CELERY_TASK_ALWAYS_EAGER = True
  # noqa: F841
CELERY_TASK_EAGER_PROPAGATES = True
  # noqa: F841

# Disable migrations when running tests


class DisableMigrations:
    def __contains__(self, item):

        return True

    def __getitem__(self, item):

        return None

MIGRATION_MODULES = DisableMigrations()
  # noqa: F841

# Use simple caching for tests
CACHES = {
  # noqa: F841
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # noqa: E128
        'LOCATION': '',
    }
}

# Disable CSRF validation in tests
CSRF_COOKIE_SECURE = False
  # noqa: F841
SESSION_COOKIE_SECURE = False
  # noqa: F841

# Media settings for tests
MEDIA_ROOT = BASE_DIR / 'test_media'
  # noqa: F841

# Debug toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
  # noqa: F841
    'IS_RUNNING_TESTS': False,
}
