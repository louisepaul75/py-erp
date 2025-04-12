"""
Base settings for pyERP project.

These settings are common to all environments and will be imported by environment-specific  # noqa: E501
settings files.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path
import logging  # Add logging

import environ  # Add this import
import dj_database_url  # noqa: F401
from celery.schedules import crontab  # Import for CELERY_BEAT_SCHEDULE
from django.utils.translation import gettext_lazy as _  # Move import to top

# Import 1Password SDK
try:
    from onepasswordconnectsdk import client
    from onepasswordconnectsdk.models import Field, Item
except ImportError:
    client = None  # SDK not installed
    Item = None # Define Item as None if SDK not installed
    Field = None # Define Field as None if SDK not installed

# Basic logging configuration (configure more robustly if needed)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize django-environ
env = environ.Env()

# Attempt to read .env file, if it exists
# Corrected path joining for .env file
env_file_path = BASE_DIR / ".env"
if env_file_path.exists():
    with open(env_file_path, encoding='utf-8') as f: # Specify encoding
        environ.Env.read_env(env_file=f)
    logging.info(f"Loaded environment variables from: {env_file_path}")
else:
    logging.warning(f".env file not found at {env_file_path}. Relying on system environment variables.")

# Add the project root to Python path to ensure imports work
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from pyerp.version import get_version  # noqa: E402

# --- Logging Level --- 
# Define the log level, used by pyerp.utils.logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-change-me-in-production"
)

# Get application version
APP_VERSION = get_version()

# --- Remove the first IMAGE_API settings since we'll define them later ---
# Image API settings - Remove these lines, we'll use the 1Password values
IMAGE_API_URL = None  # Will be set later
IMAGE_API_USERNAME = None  # Will be set later
IMAGE_API_PASSWORD = None  # Will be set later
IMAGE_API_TIMEOUT = int(os.environ.get("IMAGE_API_TIMEOUT", "30"))
IMAGE_API_CACHE_ENABLED = (
    os.environ.get("IMAGE_API_CACHE_ENABLED", "True").lower() == "true"
)
IMAGE_API_CACHE_TIMEOUT = int(
    os.environ.get("IMAGE_API_CACHE_TIMEOUT", "3600")
)

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "django_celery_results",
    "django_celery_beat",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_framework_simplejwt",
]

LOCAL_APPS = [
    "users",  # Our custom users app
    "pyerp.core",
    "pyerp.business_modules.products",
    "pyerp.business_modules.sales",
    "pyerp.business_modules.inventory",
    "pyerp.business_modules.production",
    "pyerp.monitoring",
    "pyerp.sync",
    "pyerp.external_api.apps.ExternalApiConfig",
    "admin_tools",  # Admin tools app for database table view
    "pyerp.business_modules.business",  # Business management
    "sync_manager",  # App for managing sync workflows
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Allow React dev server
    "http://127.0.0.1:3000",  # Allow React dev server
    "https://localhost",      # Allow local HTTPS setup
]
# Allow credentials (like cookies) to be sent
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "pyerp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pyerp.wsgi.application"

# --- Initialize 1Password Connect Client ---
op_client = None
if client: # Check if SDK was imported successfully
    OP_CONNECT_HOST = os.environ.get("OP_CONNECT_HOST")
    OP_CONNECT_TOKEN = os.environ.get("OP_CONNECT_TOKEN")

    if OP_CONNECT_HOST and OP_CONNECT_TOKEN:
        try:
            # Add user-agent string
            op_client = client.new_client(
                OP_CONNECT_HOST,
                OP_CONNECT_TOKEN
            )
            # Optional: Test connection by trying to list vaults (add error handling if used)
            # op_client.get_vaults()
            logging.info("1Password Connect SDK initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize 1Password Connect SDK: {e}", exc_info=True)
            op_client = None # Ensure client is None if init fails
    else:
        logging.warning("OP_CONNECT_HOST or OP_CONNECT_TOKEN not found in environment. Cannot initialize 1Password SDK.")
else:
    logging.warning("onepasswordconnectsdk not installed. Secrets will be read from environment variables.")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# --- Fetch Database Credentials ---
db_host = os.environ.get("DB_HOST", "localhost") # Default added
db_port = os.environ.get("DB_PORT", "5432")      # Default added
db_name = os.environ.get("DB_NAME", "pyerp_testing")
db_user = os.environ.get("DB_USER", "postgres")   # Default added
db_password = os.environ.get("DB_PASSWORD", "")
db_engine = os.environ.get("DB_ENGINE", "django.db.backends.postgresql") # Get engine

db_credentials_source = "environment variables"

if op_client: # Check if client was initialized successfully
    try:
        # First, get the list of vaults and find the "dev" vault UUID
        vaults = op_client.get_vaults()
        vault_uuid = None
        op_vault_name = "dev"
        op_item_name = "postgres_db"
        
        for vault in vaults:
            if vault.name == op_vault_name:
                vault_uuid = vault.id
                break
                
        if not vault_uuid:
            logging.warning(f"Could not find vault named '{op_vault_name}' in 1Password.")
            
        else:
            logging.info(f"Found vault '{op_vault_name}' with UUID: {vault_uuid}")
            logging.info(f"Attempting to fetch DB credentials from 1Password: Vault='{op_vault_name}', Item='{op_item_name}'")

            # Get all items in the vault
            try:
                # First get all items in the vault
                items = op_client.get_items(vault_uuid)
                
                # Find our target item
                target_item = None
                for item in items:
                    if item.title == op_item_name:
                        target_item = item
                        break
                
                if target_item:
                    # Get the complete item with all fields
                    item = op_client.get_item(target_item.id, vault_uuid)
                    
                    # Process the item fields as before
                    if item and item.fields:
                        item_fields = {field.label: field.value for field in item.fields if field.value is not None}

                        # Get values, keeping existing env fallbacks if field not found in 1P
                        fetched_host = item_fields.get("server")
                        fetched_port = item_fields.get("port")
                        fetched_user = item_fields.get("username")
                        fetched_password = item_fields.get("password")

                        # Only update if value was actually fetched from 1Password
                        if fetched_host is not None:
                            db_host = fetched_host
                            logging.info(f"Using 1Password value for DB_HOST: {db_host}")
                        if fetched_port is not None:
                            db_port = fetched_port
                            logging.info(f"Using 1Password value for DB_PORT: {db_port}")
                        if fetched_user is not None:
                            db_user = fetched_user
                            logging.info(f"Using 1Password value for DB_USER: {db_user}")
                        if fetched_password is not None:
                            db_password = fetched_password
                            # Log password presence but not the actual value
                            logging.info(f"Using 1Password value for DB_PASSWORD: {'*' * (len(fetched_password) if fetched_password else 0)}")
                        else:
                            logging.warning("Password field was not found in 1Password or is empty")

                        # Check if at least one credential was fetched from 1Password
                        if any(val is not None for val in [fetched_host, fetched_port, fetched_user, fetched_password]):
                             db_credentials_source = "1Password"
                             logging.info("Successfully retrieved DB credentials from 1Password.")
                        else:
                             logging.warning(f"Could not find expected fields (server, port, username, password) in 1Password item '{op_item_name}'.")
                else:
                    logging.warning(f"Item '{op_item_name}' not found in vault '{op_vault_name}'.")
                    
            except Exception as e:
                logging.error(f"Error fetching items from vault: {e}", exc_info=True)
                
    except Exception as e:
        logging.error(f"Error accessing 1Password: {e}", exc_info=True)
        logging.warning("Falling back to environment variables for database credentials.")

# Use fetched or environment variable values
DATABASES = {
    "default": {
        "ENGINE": db_engine, # Use fetched/env engine
        "NAME": db_name,     # Keep using env var as requested
        "USER": db_user,
        "PASSWORD": db_password,
        "HOST": db_host,
        "PORT": db_port,
        "OPTIONS": {
            "connect_timeout": 5,
        },
    }
}

# Print database connection info for debugging (consider removing password log)
logging.info(
    f"Database settings source: {db_credentials_source}. "
    f"ENGINE={DATABASES['default']['ENGINE']}, "
    f"NAME={DATABASES['default']['NAME']}, "
    f"HOST={DATABASES['default']['HOST']}, "
    f"PORT={DATABASES['default']['PORT']}, "
    f"USER={DATABASES['default']['USER']}"
)
if not DATABASES['default']['PASSWORD']:
     logging.warning("Database password is NOT SET.")

# Alternative DATABASE_URL configuration (commented out)

#     'default': dj_database_url.config(
#         default=os.environ.get(
#             'DATABASE_URL',
#             'postgresql://postgres:password@localhost:5432/pyerp_testing'

#     )
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "de"  # German as default language
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
    ('cs', _('Czech')),
]

# Paths where Django should look for translation files
LOCALE_PATHS = [
    BASE_DIR / "pyerp" / "locale",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (User Uploads)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        # Add BrowsableAPIRenderer back if needed for development/debugging
        # in browser
        # "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
}

# Spectacular API Schema configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'pyERP API',
    'DESCRIPTION': 'API documentation for pyERP system',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'CONTACT': {
        'name': 'Support',
        'email': 'support@pyerp.example.com',
    },
    'LICENSE': {'name': 'Proprietary'},
    'TOS': 'https://www.pyerp.example.com/terms/',
    'COMPONENT_SPLIT_PATCH': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
    },
    'EXCLUDE_PATH_REGEX': [r'/api/token/'],
    
    # Show v1 endpoints in the schema, but continue to work with
    # non-versioned endpoints
    'SCHEMA_PATH_PREFIX_INCLUDE': [r'/api/v1/'],
    
    # Exclude non-versioned endpoints from the schema
    'SCHEMA_PATH_PREFIX_EXCLUDE': [
        r'^/api/(?!v1/|schema/|swagger/|redoc/).*$'
    ],
    
    # Verbessertes Filter-Handling
    'PREPROCESSING_HOOKS': ['pyerp.utils.api_docs.preprocess_filter_fields'],
    'ENUM_NAME_OVERRIDES': {
        'CustomerGroupEnum': ['Premium', 'Standard', 'Business'],
        'RecordTypeEnum': ['Order', 'Invoice', 'Return'],
        'PaymentStatusEnum': ['Pending', 'Paid', 'Cancelled', 'Refunded'],
        'FulfillmentStatusEnum': [
            'Pending', 'Shipped', 'Delivered', 'Cancelled'
        ],
    },
    
    # Ensure tags work correctly with versioned endpoints
    'TAGS_SORTER': 'alpha',
    'OPERATIONS_SORTER': 'alpha',
    'PATH_CONVERTER': {
        'api_path': r'/api/v1',
        'api_version': 'v1',
    },
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=240),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# Celery settings
CELERY_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379/0"
)
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", "django-db"
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Celery Beat Schedule Configuration
# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#beat-schedule
CELERY_BEAT_SCHEDULE = {
    # "sync.scheduled_incremental_sync": {  # COMMENTED OUT
    #     "task": "sync.run_incremental_sync",
    #     "schedule": 300.0,  # Every 5 minutes
    #     "options": {"expires": 290.0},
    # },
    # "sync.scheduled_full_sync": { # COMMENTED OUT
    #     "task": "sync.run_full_sync",
    #     "schedule": crontab(hour=2, minute=0),  # Run at 2:00 AM daily
    #     "options": {"expires": 3600.0},
    # },
    # "sync.incremental_sales_record_sync": { # COMMENTED OUT
    #     "task": "sync.run_incremental_sales_record_sync",
    #     "schedule": crontab(minute="*/15"),  # Every 15 minutes
    #     "options": {"expires": 900.0},
    # },
    # "sync.full_sales_record_sync": { # COMMENTED OUT
    #     "task": "sync.run_full_sales_record_sync",
    #     "schedule": crontab(hour=3, minute=0),  # Run at 3:00 AM daily
    #     "options": {"expires": 3600.0},
    # },
    # "sync.scheduled_employee_sync": { # COMMENTED OUT
    #     "task": (
    #         "pyerp.sync.tasks.scheduled_employee_sync"  # Note: Using full path
    #     ),
    #     "schedule": crontab(minute="*/5"),  # Every 5 minutes
    #     "options": {"expires": 240.0},  # Expires after 4 minutes
    # },
    # "sync.nightly_full_employee_sync": { # COMMENTED OUT
    #     "task": (
    #         "pyerp.sync.tasks.nightly_full_employee_sync"  # Note: Using full path # noqa E501
    #     ),
    #     "schedule": crontab(hour=2, minute=15),  # Run at 2:15 AM daily
    #     "options": {"expires": 10800.0},  # Expires after 3 hours
    # },
    # Add other periodic tasks here if needed (e.g., monitoring, cleanup)
}

# Ensure logs directory exists
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

# Logging Configuration - COMMENTED OUT TO USE pyerp.utils.logging
# LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
# JSON_LOGGING = os.environ.get("JSON_LOGGING", "False").lower() == "true"
# try:
#     LOG_FILE_SIZE_LIMIT = int(
#         os.environ.get("LOG_FILE_SIZE_LIMIT", 2097152)
#     )  # Default to 2MB
# except ValueError:
#     LOG_FILE_SIZE_LIMIT = 2097152  # 2MB in bytes
# 
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": (
#                 "{levelname} {asctime} {module} {process:d} {thread:d} " # noqa E501
#                 "{message}"
#             ),
#             "style": "{",
#         },
#         "simple": {
#             "format": "{levelname} {message}",
#             "style": "{",
#         },
#         "json": {
#             "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
#             "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
#             "rename_fields": {
#                 "asctime": "@timestamp",
#                 "levelname": "level",
#             },
#         },
#     },
#     "filters": {
#         "require_debug_true": {
#             "()": "django.utils.log.RequireDebugTrue",
#         },
#         "require_debug_false": {
#             "()": "django.utils.log.RequireDebugFalse",
#         },
#     },
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#             "formatter": "json" if JSON_LOGGING else "verbose",
#         },
#         "app_file": {
#             "level": LOG_LEVEL,
#             "class": "logging.handlers.RotatingFileHandler",
#             "filename": BASE_DIR / "logs" / "app.log",
#             "maxBytes": LOG_FILE_SIZE_LIMIT,
#             "backupCount": 10,
#             "formatter": "json" if JSON_LOGGING else "verbose",
#         },
#         "security_file": {
#             "level": "INFO",
#             "class": "logging.handlers.RotatingFileHandler",
#             "filename": BASE_DIR / "logs" / "security.log",
#             "maxBytes": LOG_FILE_SIZE_LIMIT,
#             "backupCount": 10,
#             "formatter": "json" if JSON_LOGGING else "verbose",
#         },
#         "performance_file": {
#             "level": "INFO",
#             "class": "logging.handlers.RotatingFileHandler",
#             "filename": BASE_DIR / "logs" / "performance.log",
#             "maxBytes": LOG_FILE_SIZE_LIMIT,
#             "backupCount": 5,
#             "formatter": "json" if JSON_LOGGING else "verbose",
#         },
#         "data_sync_file": {
#             "level": "INFO",
#             "class": "logging.handlers.RotatingFileHandler",
#             "filename": BASE_DIR / "logs" / "data_sync.log",
#             "maxBytes": LOG_FILE_SIZE_LIMIT,
#             "backupCount": 10,
#             "formatter": "json" if JSON_LOGGING else "verbose",
#         },
#         "mail_admins": {
#             "level": "ERROR",
#             "filters": ["require_debug_false"],
#             "class": "django.utils.log.AdminEmailHandler",
#             "formatter": "verbose",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console", "app_file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "django.server": {
#             "handlers": ["console", "app_file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "django.request": {
#             "handlers": ["mail_admins", "console", "app_file"],
#             "level": "ERROR",
#             "propagate": False,
#         },
#         "django.security": {
#             "handlers": ["security_file", "mail_admins"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "pyerp": {
#             "handlers": ["console", "app_file"],
#             "level": LOG_LEVEL,
#             "propagate": False,
#         },
#         "pyerp.sync": {
#             "handlers": ["console", "data_sync_file"],
#             "level": LOG_LEVEL,
#             "propagate": False,
#         },
#         "pyerp.performance": {
#             "handlers": ["performance_file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "pyerp.external_api.images_cms": {
#             "handlers": ["console", "data_sync_file"],
#             "level": LOG_LEVEL,
#             "propagate": False,
#         },
#     },
# }
# End of commented out LOGGING dict

# --- Fetch Image API Credentials ---
image_api_url = os.environ.get("IMAGE_API_URL", "http://db07.wsz.local/api/")
image_api_username = os.environ.get("IMAGE_API_USERNAME", "admin")
image_api_password = os.environ.get("IMAGE_API_PASSWORD", "")
image_api_credentials_source = "environment variables"

# Try to get Image API credentials from 1Password if the client is initialized
if op_client and vault_uuid:  # Use vault_uuid from the database credentials section
    try:
        op_image_item_name = "image_cms_api"
        logging.info(f"Attempting to fetch Image API credentials from 1Password: Vault='{op_vault_name}', Item='{op_image_item_name}'")
        
        # Get all items in the vault (reusing items list if available)
        items = globals().get('items') or op_client.get_items(vault_uuid)
        
        # Find the target item
        image_target_item = None
        for item in items:
            if item.title == op_image_item_name:
                image_target_item = item
                break
                
        if image_target_item:
            # Get the complete item with all fields
            image_item = op_client.get_item(image_target_item.id, vault_uuid)
            
            if image_item and image_item.fields:
                image_item_fields = {field.label: field.value for field in image_item.fields if field.value is not None}
                
                # Get values from 1Password fields
                fetched_url = image_item_fields.get("URL")
                fetched_username = image_item_fields.get("username")
                fetched_password = image_item_fields.get("password")
                
                # Update values if they were fetched
                if fetched_url is not None:
                    image_api_url = fetched_url
                    logging.info(f"Using 1Password value for IMAGE_API_URL: {image_api_url}")
                if fetched_username is not None:
                    image_api_username = fetched_username
                    logging.info(f"Using 1Password value for IMAGE_API_USERNAME: {image_api_username}")
                if fetched_password is not None:
                    image_api_password = fetched_password
                    # Log password presence but not the actual value
                    logging.info(f"Using 1Password value for IMAGE_API_PASSWORD: {'*' * (len(fetched_password) if fetched_password else 0)}")
                
                # Set credential source if at least one value was fetched
                if any(val is not None for val in [fetched_url, fetched_username, fetched_password]):
                    image_api_credentials_source = "1Password"
                    logging.info("Successfully retrieved Image API credentials from 1Password.")
        else:
            logging.warning(f"Item '{op_image_item_name}' not found in vault '{op_vault_name}'.")
            
    except Exception as e:
        logging.error(f"Error fetching Image API credentials from 1Password: {e}", exc_info=True)
        logging.warning("Falling back to environment variables for Image API credentials.")

# Update the initial Image API settings - these might be used directly in some code
IMAGE_API_URL = image_api_url
IMAGE_API_USERNAME = image_api_username
IMAGE_API_PASSWORD = image_api_password

# Print image API info for debugging
logging.info(
    f"Image API settings source: {image_api_credentials_source}. "
    f"URL={IMAGE_API_URL}, "
    f"USERNAME={IMAGE_API_USERNAME}"
)
if not IMAGE_API_PASSWORD:
    logging.warning("Image API password is NOT SET.")

# Image API Configuration
IMAGE_API = {
    "BASE_URL": image_api_url,  # Use the value fetched from 1Password
    "USERNAME": image_api_username,  # Use the value fetched from 1Password
    "PASSWORD": image_api_password,  # Use the value fetched from 1Password
    "TIMEOUT": int(
        os.environ.get("IMAGE_API_TIMEOUT", 60)
    ),  # Increased default timeout
    "CACHE_ENABLED": os.environ.get(
        "IMAGE_API_CACHE_ENABLED", "True"
    ).lower()
    == "true",
    "CACHE_TIMEOUT": int(
        os.environ.get("IMAGE_API_CACHE_TIMEOUT", 3600)
    ),  # 1 hour
    "VERIFY_SSL": os.environ.get(
        "IMAGE_API_VERIFY_SSL", "False"
    ).lower()
    == "true",  # Default to not verifying SSL
}

# Update loggers for image API - COMMENTED OUT, handled by pyerp.utils.logging
# LOGGING["loggers"]["pyerp.external_api.images_cms"] = {
#     "handlers": ["console", "data_sync_file"],
#     "level": LOG_LEVEL,
#     "propagate": False,
# }
