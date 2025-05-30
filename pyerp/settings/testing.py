"""
Testing settings for pyERP project.

These settings extend the base settings with testing-specific configurations
focused on test performance and isolation.
"""

import os
import sys
from pathlib import Path  # noqa: F401

import dj_database_url  # noqa: F401
import psycopg2

# Completely disable ddtrace before any other imports
os.environ["DD_TRACE_ENABLED"] = "false"
os.environ["DD_PROFILING_ENABLED"] = "false"

# Unload ddtrace module if it's already loaded to prevent metaclass conflicts
if "ddtrace" in sys.modules:
    del sys.modules["ddtrace"]
    # Also unload any ddtrace submodules
    for module_name in list(sys.modules.keys()):
        if module_name.startswith("ddtrace."):
            del sys.modules[module_name]

# Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables  # noqa: E402

from pyerp.config.settings.base import *  # noqa: F403

load_environment_variables(verbose=True)

# Print environment variables for debugging
print(f"DB_NAME: {os.environ.get('DB_NAME', 'not set')}")
print(f"DB_USER: {os.environ.get('DB_USER', 'not set')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD', 'not set')}")
print(f"DB_HOST: {os.environ.get('DB_HOST', 'not set')}")
print(f"DB_PORT: {os.environ.get('DB_PORT', 'not set')}")

# Configure for test environment
DEBUG = True

# Add required apps
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    'django_celery_beat',
    'django_celery_results',
    'admin_tools',
    
    # Core apps
    'pyerp.core',
    'users',
    'pyerp.sync',
    'pyerp.monitoring',
    'pyerp.external_api',
    'pyerp.legacy_sync',
    'pyerp.middleware',
    
    # Business modules
    'pyerp.business_modules.products',
    'pyerp.business_modules.inventory',
    'pyerp.business_modules.sales',
    'pyerp.business_modules.production',
    'pyerp.business_modules.business',
    
    # Utility apps
    'pyerp.utils.email_system',
]

# Remove debug toolbar for tests
if "debug_toolbar" in INSTALLED_APPS:
    INSTALLED_APPS.remove("debug_toolbar")

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Remove ddtrace middleware if present
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE if "ddtrace" not in middleware
]

ALLOWED_HOSTS = ["*"]

# Database configuration for tests
# Try to use PostgreSQL first, fall back to SQLite if connection fails

# Define PostgreSQL connection parameters
PG_PARAMS = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("DB_NAME", "pyerp_testing"),
    "USER": os.environ.get("DB_USER", "postgres"),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST": os.environ.get("DB_HOST", "192.168.73.65"),
    "PORT": os.environ.get("DB_PORT", "5432"),
    "TEST": {
        "NAME": "test_pyerp_testing",
    },
}

# Define SQLite connection parameters as fallback
SQLITE_PARAMS = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
}

# Try to connect to PostgreSQL, use SQLite if it fails
try:
    sys.stderr.write(
        f"Attempting to connect to PostgreSQL at {PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n",
    )

    conn = psycopg2.connect(
        dbname=PG_PARAMS["NAME"],
        user=PG_PARAMS["USER"],
        password=PG_PARAMS["PASSWORD"],
        host=PG_PARAMS["HOST"],
        port=PG_PARAMS["PORT"],
        connect_timeout=5,
    )
    conn.close()
    DATABASES = {"default": PG_PARAMS}
    sys.stderr.write(
        f"SUCCESS: Using PostgreSQL database at {PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n",
    )
except (OSError, psycopg2.OperationalError) as e:
    sys.stderr.write(f"ERROR: Could not connect to PostgreSQL: {e!s}\n")
    sys.stderr.write("FALLBACK: Using SQLite for testing\n")
    DATABASES = {"default": SQLITE_PARAMS}

# Use the fastest possible password hasher
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Simplify password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Disable template debug mode for faster tests
for template in TEMPLATES:
    template["OPTIONS"]["debug"] = False

# Use console email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "propagate": False,
            "level": "WARNING",
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
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
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# Disable CSRF validation in tests
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Media settings for tests
MEDIA_ROOT = BASE_DIR / "test_media"

# Fix for metaclass conflicts in Django's PostgreSQL fields
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.db.models import Field
from django.db.models.fields.mixins import CheckFieldDefaultMixin

# Ensure SearchVectorField has the correct metaclass
if not isinstance(SearchVectorField, type(Field)):
    SearchVectorField.__class__ = type(Field)

# Fix ArrayField metaclass conflict
if not isinstance(ArrayField, type(Field)):
    # Create a new metaclass that combines both base classes
    class CombinedMetaclass(type(CheckFieldDefaultMixin), type(Field)):
        pass

    # Create a new class with the combined metaclass
    class FixedArrayField(ArrayField):
        __metaclass__ = CombinedMetaclass

    # Replace the original ArrayField with our fixed version
    import django.contrib.postgres.fields

    django.contrib.postgres.fields.ArrayField = FixedArrayField
