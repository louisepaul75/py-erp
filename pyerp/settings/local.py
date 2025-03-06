"""
Local development settings for pyERP project.

These settings are designed for local development without external dependencies.  # noqa: E501
Uses SQLite as the database and in-memory options for Redis/Celery.
"""

import os
from pathlib import Path  # noqa: F401
from .base import *  # noqa

 # Import HTTPS settings
try:
    from .settings_https import *  # noqa
except ImportError:
    pass

 # Enable debug mode for local development
DEBUG = True

 # Allow all hosts for local development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

 # Database configuration
DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql',  # noqa: E128
             'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
             'USER': os.environ.get('DB_USER', 'postgres'),
             'PASSWORD': os.environ.get('DB_PASSWORD', ''),
             'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
             'PORT': os.environ.get('DB_PORT', '5432'),
             }
}

 # Disable security features for local development
 # These settings will be overridden by settings_https.py if it's imported

 # noqa: F841

 # noqa: F841

 # noqa: F841

 # noqa: F841
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

 # CORS settings - allow all origins in local development
CORS_ALLOW_ALL_ORIGINS = True

 # Use dummy cache for local development
CACHES = {
    'default': {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # noqa: E128
}
}

 # Email configuration for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

 # Celery settings for local development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'django-db'

 # Static files for local development
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
