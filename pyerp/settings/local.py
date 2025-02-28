"""
Local development settings for pyERP project.

These settings are designed for local development without external dependencies.
Uses SQLite as the database and in-memory options for Redis/Celery.
"""

import os
from pathlib import Path
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

# Use SQLite database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Check for DATABASE_URL and use that if provided
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    db_url = os.environ.get('DATABASE_URL')
    # Only use it if it's sqlite:// to avoid importing MySQL
    if db_url.startswith('sqlite://'):
        print(f"Using DATABASE_URL with SQLite: {db_url}")
        DATABASES['default'] = dj_database_url.parse(db_url)

# Disable security features for local development
# These settings will be overridden by settings_https.py if it's imported
# SECURE_SSL_REDIRECT = False
# SECURE_HSTS_SECONDS = 0
# SECURE_HSTS_INCLUDE_SUBDOMAINS = False
# SECURE_HSTS_PRELOAD = False
# CSRF_COOKIE_SECURE = False
# SESSION_COOKIE_SECURE = False

# CORS settings - allow all origins in local development
CORS_ALLOW_ALL_ORIGINS = True

# Use dummy cache for local development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email configuration for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery settings for local development
CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery-results.sqlite'

# Static files for local development
STATIC_URL = '/static/'
MEDIA_URL = '/media/' 