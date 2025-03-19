"""Test settings for pyERP."""

import os
import django
from django.conf import settings

# Configure Django settings before importing anything else
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.test")

# Skip Celery and related apps for testing to avoid import issues
if os.environ.get("SKIP_CELERY_IMPORT") == "1":
    # First get the current list
    from pyerp.config.settings.test import INSTALLED_APPS
    
    # Filter out celery-related apps
    filtered_apps = [
        app for app in INSTALLED_APPS 
        if 'celery' not in app.lower() and 'kombu' not in app.lower()
    ]
    
    # Set the filtered apps back
    os.environ["DJANGO_FILTERED_INSTALLED_APPS"] = ",".join(filtered_apps)

# Now setup Django
django.setup()

# If we're skipping Celery, modify the installed apps
if os.environ.get("SKIP_CELERY_IMPORT") == "1" and os.environ.get("DJANGO_FILTERED_INSTALLED_APPS"):
    filtered_apps = os.environ.get("DJANGO_FILTERED_INSTALLED_APPS").split(",")
    settings.INSTALLED_APPS = filtered_apps

# REST Framework settings
settings.REST_FRAMEWORK = {
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.MultiPartRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# Use in-memory SQLite for tests
settings.DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {
            "NAME": ":memory:",
        },
    }
}

# Disable password hashing for faster tests
settings.PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


settings.MIGRATION_MODULES = DisableMigrations()

# Configure Django model fields for Python 3.12
settings.DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
settings.FIELD_TYPES = {
    "AutoField": "django.db.models.BigAutoField",
    "BigAutoField": "django.db.models.BigAutoField",
    "SmallAutoField": "django.db.models.SmallAutoField",
}

# Configure model field types for Python 3.12
settings.MODELS = {
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    "FIELD_TYPES": {
        "AutoField": "django.db.models.BigAutoField",
        "BigAutoField": "django.db.models.BigAutoField",
        "SmallAutoField": "django.db.models.SmallAutoField",
    },
}

# Configure test database
settings.TEST_RUNNER = "django.test.runner.DiscoverRunner"
settings.TEST_NON_SERIALIZED_APPS = []
settings.FIXTURE_DIRS = []
settings.SERIALIZATION_MODULES = {}
