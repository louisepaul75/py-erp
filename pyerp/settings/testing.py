"""
Testing settings for pyERP project.

These settings extend the base settings with testing-specific configurations
focused on test performance and isolation.
"""

import os
import sys
import dj_database_url
from .base import *  # noqa
from pathlib import Path

# Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables
load_environment_variables(verbose=True)

# Print environment variables for debugging
print(f"DB_NAME: {os.environ.get('DB_NAME', 'not set')}")
print(f"DB_USER: {os.environ.get('DB_USER', 'not set')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD', 'not set')}")
print(f"DB_HOST: {os.environ.get('DB_HOST', 'not set')}")
print(f"DB_PORT: {os.environ.get('DB_PORT', 'not set')}")

# Configure for test environment
DEBUG = True

# Remove debug toolbar for tests
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'debug_toolbar' not in middleware]

ALLOWED_HOSTS = ['*']

# Database configuration for tests
# Try to use PostgreSQL first, fall back to SQLite if connection fails
import socket
import psycopg2

# Define PostgreSQL connection parameters
PG_PARAMS = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
    'USER': os.environ.get('DB_USER', 'postgres'),
    'PASSWORD': os.environ.get('DB_PASSWORD', ''),
    'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
    'PORT': os.environ.get('DB_PORT', '5432'),
    'TEST': {
        'NAME': 'test_pyerp_testing',
    },
}

# Define SQLite connection parameters as fallback
SQLITE_PARAMS = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
}

# Try to connect to PostgreSQL, use SQLite if it fails
try:
    # Force more verbose output during tests
    sys.stderr.write(f"Attempting to connect to PostgreSQL at {PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n")
    
    conn = psycopg2.connect(
        dbname=PG_PARAMS['NAME'],
        user=PG_PARAMS['USER'],
        password=PG_PARAMS['PASSWORD'],
        host=PG_PARAMS['HOST'],
        port=PG_PARAMS['PORT'],
        connect_timeout=5  # Slightly longer timeout
    )
    conn.close()
    DATABASES = {'default': PG_PARAMS}
    sys.stderr.write(f"SUCCESS: Using PostgreSQL database at {PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n")
except (psycopg2.OperationalError, socket.error) as e:
    sys.stderr.write(f"ERROR: Could not connect to PostgreSQL: {str(e)}\n")
    sys.stderr.write("FALLBACK: Using SQLite for testing\n")
    DATABASES = {'default': SQLITE_PARAMS}

# Use the fastest possible password hasher
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Simplify password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Disable template debug mode for faster tests
for template in TEMPLATES:
    template['OPTIONS']['debug'] = False

# Use console email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'WARNING',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
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
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '',
    }
}

# Disable CSRF validation in tests
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Media settings for tests
MEDIA_ROOT = BASE_DIR / 'test_media' 