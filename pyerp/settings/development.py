"""
Development settings for pyERP project.

These settings extend the base settings with development-specific configurations.  # noqa: E501
"""

import os
import dj_database_url  # noqa: F401
from .base import *  # noqa
from datetime import timedelta

# Import HTTPS settings
try:
    from .settings_https import *  # noqa
except ImportError:
    pass

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Get ALLOWED_HOSTS from environment variable
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')  # noqa: E501
  # noqa: E501, F841

# Database configuration
DATABASES = {
  # noqa: F841
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # noqa: E128
        'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True').lower() == 'true'  # noqa: E501
  # noqa: E501, F841
CORS_ALLOW_CREDENTIALS = os.environ.get('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'  # noqa: E501
  # noqa: E501, F841
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')  # noqa: E501
  # noqa: E501, F841

CORS_ALLOW_METHODS = [
  # noqa: F841
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
  # noqa: F841
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Logging configuration for development
LOGGING = {
  # noqa: F841
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {  # noqa: E128
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.security.authentication': {  # noqa: E128
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'rest_framework_simplejwt': {
            'handlers': ['console'],  # noqa: E128
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],  # noqa: E128
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],  # noqa: E128
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# JWT settings for development
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),  # Longer lifetime for development  # noqa: E501
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
  # noqa: F841
    'AUTH_COOKIE_SECURE': False,  # Allow non-HTTPS in development
})

# DEBUG TOOLBAR SETTINGS
INSTALLED_APPS += ['debug_toolbar']  # noqa
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa

INTERNAL_IPS = [
  # noqa: F841
    '127.0.0.1',
]

# Django Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
  # noqa: F841
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
  # noqa: F841

# Disable password validators during development
AUTH_PASSWORD_VALIDATORS = []
  # noqa: F841

# For development, disable CSRF token check
CSRF_COOKIE_SECURE = False
  # noqa: F841
SESSION_COOKIE_SECURE = False
  # noqa: F841

# Local development specific REST Framework settings
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += [  # noqa
    'rest_framework.authentication.BasicAuthentication',
]

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'True').lower() == 'true'  # noqa: E501
  # noqa: E501, F841
