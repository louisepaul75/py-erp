"""
Testing settings for pyERP project.

These settings extend the base settings with testing-specific configurations
focused on test performance and isolation.
"""

import os
import dj_database_url
from .base import *  # noqa

# Configure for test environment
DEBUG = False

# Remove debug toolbar for tests
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'debug_toolbar' not in middleware]

ALLOWED_HOSTS = ['*']

# Use PostgreSQL database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Alternative DATABASE_URL configuration (commented out)
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.environ.get(
#             'DATABASE_URL', 
#             'postgresql://postgres:password@localhost:5432/pyerp_testing'
#         ),
#         conn_max_age=600,
#     )
# }

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
    },
    'loggers': {
        '': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
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

# Debug toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    'IS_RUNNING_TESTS': False,
} 