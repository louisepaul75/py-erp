"""
Development settings for pyERP project.

These settings extend the base settings with development-specific configurations.
"""

import os
import dj_database_url
from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# Database configuration 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '192.168.73.64'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Alternative DATABASE_URL configuration (commented out)
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.environ.get(
#             'DATABASE_URL', 
#             'mysql://user:password@localhost:3306/pyerp_testing'
#         ),
#         conn_max_age=600,
#     )
# }

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# DEBUG TOOLBAR SETTINGS
INSTALLED_APPS += ['debug_toolbar']  # noqa
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa

INTERNAL_IPS = [
    '127.0.0.1',
]

# Django Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable password validators during development
AUTH_PASSWORD_VALIDATORS = []

# For development, disable CSRF token check
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Local development specific REST Framework settings
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += [  # noqa
    'rest_framework.authentication.BasicAuthentication',
]

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'True').lower() == 'true' 