"""
Test settings for pyERP project.

These settings extend the development settings with test-specific configurations.
"""

from .development import *  # noqa

# Remove debug toolbar from installed apps
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# Remove debug toolbar middleware
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

# Configure debug toolbar for tests
DEBUG_TOOLBAR_CONFIG = {
    'IS_RUNNING_TESTS': True,
}

# Use in-memory SQLite for faster tests
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': ':memory:',
#     }
# }

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

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
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
} 