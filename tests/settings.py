"""
Test-specific settings for pyERP.
"""

from pyerp.config.settings.test import *

# Explicitly include the apps needed for testing
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_yasg",
    "django_celery_results",
    "django_celery_beat",
    # Local apps
    "users",
    "pyerp.core",
    "pyerp.core.models",  # Explicitly include models
    "pyerp.business_modules.products",
    "pyerp.business_modules.sales",
    "pyerp.business_modules.inventory",
    "pyerp.business_modules.production",
    "pyerp.monitoring",
    "pyerp.sync",
    "pyerp.external_api",
    "admin_tools",
]

# Use a simple database setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Ensure tests don't make real external requests
MIDDLEWARE += [
    'django.middleware.csrf.CsrfViewMiddleware',
]

# Disable migrations
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations() 