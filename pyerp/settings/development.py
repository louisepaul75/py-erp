"""
Development settings for pyERP project.

These settings extend the base settings with development-specific configurations.
"""

import os
import dj_database_url
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
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database configuration using SQLite for development simplicity
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR.parent, 'db.sqlite3'),
#     }
# }

# MySQL configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
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

# CORS settings
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True').lower() == 'true'
CORS_ALLOW_CREDENTIALS = os.environ.get('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
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
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.security.authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'rest_framework_simplejwt': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# JWT settings for development
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),  # Longer lifetime for development
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_COOKIE_SECURE': False,  # Allow non-HTTPS in development
})

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