"""
Development settings for pyERP project.

These settings extend the base settings with development-specific configurations.  # noqa: E501
"""

import os
import dj_database_url  # noqa: F401
from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
  # noqa: F841
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

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
CORS_ALLOW_ALL_ORIGINS = True
  # noqa: F841

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
