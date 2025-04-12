"""
Development settings for pyERP project.

These settings extend the base settings with development-specific configurations.
"""

import os
import sys
from datetime import timedelta

import dj_database_url  # noqa: F401
import psycopg2

from .base import *  # noqa

# Ensure CorsMiddleware is placed correctly
# It's often best placed high, before CommonMiddleware
if 'corsheaders.middleware.CorsMiddleware' not in MIDDLEWARE:
    try:
        # Attempt to insert before CommonMiddleware
        common_middleware_index = MIDDLEWARE.index(
            'django.middleware.common.CommonMiddleware'
        )
        MIDDLEWARE.insert(
            common_middleware_index, 'corsheaders.middleware.CorsMiddleware'
        )
    except ValueError:
        # If CommonMiddleware isn't found, insert at the beginning
        MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

# Ensure corsheaders app is installed (likely already in base.py, but double-check)
if 'corsheaders' not in INSTALLED_APPS:
    INSTALLED_APPS += ['corsheaders']

# Import HTTPS settings
_https_settings_imported = False
try:
    from .settings_https import *  # noqa
    _https_settings_imported = True
    print("INFO: Loaded HTTPS settings for development environment.")
except ImportError:
    pass

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

# Prevent Django from automatically appending trailing slashes to URLs
# This fixes issues with PATCH requests where the browser might strip the trailing slash
APPEND_SLASH = True

# Get ALLOWED_HOSTS from environment variable
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "host.docker.internal", "192.168.65.1"]

# Database configuration with SQLite fallback
# Import the updated values from base settings if 1Password was used
db_host = globals().get('db_host', os.environ.get("DB_HOST", "192.168.73.65"))
db_port = globals().get('db_port', os.environ.get("DB_PORT", "5432"))
db_name = globals().get('db_name', os.environ.get("DB_NAME", "pyerp_testing"))
db_user = globals().get('db_user', os.environ.get("DB_USER", "postgres"))
db_password = globals().get('db_password', os.environ.get("DB_PASSWORD", ""))
db_engine = globals().get('db_engine', os.environ.get("DB_ENGINE", "django.db.backends.postgresql"))
db_credentials_source = globals().get('db_credentials_source', "environment variables (development)")

# Define PostgreSQL connection parameters
PG_PARAMS = {
    "ENGINE": db_engine,
    "NAME": db_name,
    "USER": db_user,
    "PASSWORD": db_password,
    "HOST": db_host,
    "PORT": db_port,
    "OPTIONS": {
        "connect_timeout": 10,  # Connection timeout in seconds
        "client_encoding": "UTF8",
        "sslmode": "prefer",
    },
}

# Define SQLite connection parameters as fallback
SQLITE_PARAMS = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "development_db.sqlite3"),
}

# Try to connect to PostgreSQL, use SQLite if it fails
try:
    sys.stderr.write(
        f"Attempting to connect to PostgreSQL at {PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n"
    )
    sys.stderr.write(
        f"Using database credential source: {db_credentials_source}\n"
    )
    sys.stderr.write(
        f"Username: {PG_PARAMS['USER']}, Password length: {len(PG_PARAMS['PASSWORD']) if PG_PARAMS['PASSWORD'] else 0}\n"
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
        "SUCCESS: Using PostgreSQL database at "
        f"{PG_PARAMS['HOST']}:{PG_PARAMS['PORT']}\n",
    )
except (OSError, psycopg2.OperationalError) as e:
    sys.stderr.write(f"ERROR: Could not connect to PostgreSQL: {e!s}\n")
    sys.stderr.write("FALLBACK: Using SQLite for development\n")
    DATABASES = {"default": SQLITE_PARAMS}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "access-control-allow-origin",
    "access-control-allow-credentials",
]

CORS_EXPOSE_HEADERS = [
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "set-cookie"
]

# Add CSRF trusted origin for the React frontend
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]

# Logging configuration for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    # Add root logger configuration
    "root": {
        "handlers": ["console"],
        "level": "DEBUG", 
    },
    "loggers": {
        "django.security.authentication": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "rest_framework_simplejwt": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "users": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# JWT settings for development
SIMPLE_JWT.update(
    {
        "ACCESS_TOKEN_LIFETIME": timedelta(
            days=1,
        ),  # Longer lifetime for development
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
        "AUTH_COOKIE_SECURE": False,  # Allow non-HTTPS in development
        "AUTH_COOKIE_HTTP_ONLY": True,
        "AUTH_COOKIE_SAMESITE": "Lax",
        "AUTH_COOKIE_PATH": "/",
    },
)

# DEBUG TOOLBAR SETTINGS
INSTALLED_APPS += ["debug_toolbar"]  # noqa
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
# Provide a default value for USE_DOCKER here as well
if env("USE_DOCKER", default="yes") == "yes":
    import socket

    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
    except socket.gaierror:
        # Handle case where hostname resolution fails
        hostname = "localhost" # Default hostname
        ips = ["127.0.0.1"]  # Default IP list
        INTERNAL_IPS.append("127.0.0.1") # Add default loopback

    # Add Docker gateway
    try:
        gateway_ip = socket.gethostbyname("host.docker.internal")
        INTERNAL_IPS.append(gateway_ip)
    except socket.gaierror:
        # Handle case where host.docker.internal is not resolvable
        pass 

# Django Debug Toolbar
def show_toolbar_callback(request):
    """Determine whether to show the Debug Toolbar."""
    # Always disable toolbar for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return False
        
    # Disable toolbar for API requests or static/media files
    path = request.path_info
    if (path.startswith(('/api/', '/static/', '/media/')) or 
        'application/json' in request.headers.get('Accept', '')):
        return False
        
    # Only show in DEBUG mode for other requests
    return settings.DEBUG

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar_callback,
}

# Email backend for development
EMAIL_BACKEND = "pyerp.utils.email_system.backends.LoggingEmailBackend"

# 1Password Connect settings
EMAIL_USE_1PASSWORD = os.environ.get("EMAIL_USE_1PASSWORD", "").lower() == "true"
EMAIL_1PASSWORD_ITEM_NAME = os.environ.get("EMAIL_1PASSWORD_ITEM_NAME", "")
OP_CONNECT_HOST = os.environ.get(
    "OP_CONNECT_HOST", "http://192.168.73.65:8080"
)
OP_CONNECT_TOKEN = os.environ.get("OP_CONNECT_TOKEN", "")
OP_CONNECT_VAULT = os.environ.get("OP_CONNECT_VAULT", "dev")

# Import anymail settings for reference, but use console backend
from .anymail import *  # noqa

# Override anymail settings for development
ANYMAIL = {
    **ANYMAIL,
    "DEBUG_API_REQUESTS": True,
}

# Add email_system to installed apps
INSTALLED_APPS += ["pyerp.utils.email_system"]  # noqa

# Set this to True to actually send emails in development (using the configured ESP)
USE_ANYMAIL_IN_DEV = os.environ.get(
    "USE_ANYMAIL_IN_DEV", ""
).lower() == "true"
if USE_ANYMAIL_IN_DEV:
    # Always use the logging email backend for simplicity in development
    EMAIL_BACKEND = "pyerp.utils.email_system.backends.LoggingEmailBackend"

# Disable password validators during development
AUTH_PASSWORD_VALIDATORS = []

# For development, disable CSRF token check unless HTTPS settings were loaded
if not _https_settings_imported:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

# Local development specific REST Framework settings
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] += [  # noqa
    "rest_framework.authentication.BasicAuthentication",
]

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = (
    os.environ.get("CELERY_TASK_ALWAYS_EAGER", "True").lower() == "true"
)

# Override Spectacular settings to only show v1 endpoints
SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,
    'TITLE': 'pyERP API (v1)',
    'DESCRIPTION': """
## API Versioning Notice

**IMPORTANT:** This API supports both versioned (/api/v1/...) and non-versioned (/api/...) endpoints. 

⚠️ **Please use only versioned endpoints (/api/v1/...) for all new integrations.**

Non-versioned endpoints are maintained for backward compatibility but may be removed in future releases. 
Some endpoints might appear duplicated in this documentation - always prefer the versioned variant.
    """,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SCHEMA_PATH_PREFIX_INCLUDE': [r'/api/v1/'],
    'SCHEMA_PATH_PREFIX_EXCLUDE': [],
    # Add table of contents and search functionality
    'SWAGGER_UI_SETTINGS': {
        'docExpansion': 'list',
        'filter': True,
        'deepLinking': True,
    },
    # Add tag sorting for better organization
    'TAGS_SORTER': 'alpha',
    'OPERATIONS_SORTER': 'alpha',
}

# GENERAL
# -----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="607a3WJ4w7A4v0kXF32R2Q5hR5l1wL9uR4hF4zG7aF6vA5pG1jJ0gW4pW8vQ4gS0",
)

# CACHES
# -----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
# -----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# django-debug-toolbar
# -----------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
# INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405 # Remove this duplicate entry
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405 # Remove this duplicate entry
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER", default="yes") == "yes":
    import socket

    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
    except socket.gaierror:
        # Handle case where hostname resolution fails
        hostname = "localhost" # Default hostname
        ips = ["127.0.0.1"]  # Default IP list
        INTERNAL_IPS.append("127.0.0.1") # Add default loopback

    # Add Docker gateway
    try:
        gateway_ip = socket.gethostbyname("host.docker.internal")
        INTERNAL_IPS.append(gateway_ip)
    except socket.gaierror:
        # Handle case where host.docker.internal is not resolvable
        pass 

# django-extensions
# -----------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# Celery
# -----------------------------------------------------------------------------
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True

# CORS Configuration for Development
# -----------------------------------------------------------------------------
# INSTALLED_APPS += ['corsheaders'] # Remove this duplicate entry
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Add CORS middleware first
    *MIDDLEWARE # Unpack existing middleware after CORS
] 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # React frontend
    "http://127.0.0.1:3000", # Also allow this variant
]
# Or, allow all origins for simplicity in local dev (less secure):
# CORS_ALLOW_ALL_ORIGINS = True

# Your stuff...
# -----------------------------------------------------------------------------

ROOT_URLCONF = "pyerp.urls"
