"""
Base settings for pyERP project.

These settings are common to all environments and will be imported by environment-specific  # noqa: E501
settings files.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

import environ  # Add this import
import dj_database_url  # noqa: F401
from celery.schedules import crontab # Import for CELERY_BEAT_SCHEDULE

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize django-environ
env = environ.Env()

# Attempt to read .env file, if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

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

# Image API settings
IMAGE_API_URL = os.environ.get("IMAGE_API_URL", "http://db07.wsz.local/api/")
IMAGE_API_USERNAME = os.environ.get("IMAGE_API_USERNAME", "admin")
IMAGE_API_PASSWORD = os.environ.get("IMAGE_API_PASSWORD", "")
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
    "pyerp.business_modules.business",  # Business management (HR, finance, etc.)
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
    "http://localhost:3000",  # Allow React frontend
    "http://127.0.0.1:3000",  # Also allow 127.0.0.1
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

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Get password with explicit fallback to environment variable
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
if not DB_PASSWORD:
    print("WARNING: Database password not found in environment variables!")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "pyerp_testing"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": DB_PASSWORD,
        "HOST": os.environ.get("DB_HOST", "192.168.73.65"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "connect_timeout": 5,
        },
    }
}

# Print database connection info for debugging
print(
    f"Database settings: NAME={DATABASES['default']['NAME']}, "
    f"HOST={DATABASES['default']['HOST']}, "
    f"USER={DATABASES['default']['USER']}"
)
print(
    f"Database password is "
    f"{'set' if DATABASES['default']['PASSWORD'] else 'NOT SET'}"
)

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
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
from django.utils.translation import gettext_lazy as _

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
    "sync.scheduled_incremental_sync": {
        "task": "sync.run_incremental_sync",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"expires": 290.0},
    },
    "sync.scheduled_full_sync": {
        "task": "sync.run_full_sync",
        "schedule": crontab(hour=2, minute=0),  # Run at 2:00 AM daily
        "options": {"expires": 3600.0},
    },
    "sync.incremental_sales_record_sync": {
        "task": "sync.run_incremental_sales_record_sync",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
        "options": {"expires": 900.0},
    },
    "sync.full_sales_record_sync": {
        "task": "sync.run_full_sales_record_sync",
        "schedule": crontab(hour=3, minute=0),  # Run at 3:00 AM daily
        "options": {"expires": 3600.0},
    },
    "sync.scheduled_employee_sync": {
        "task": "pyerp.sync.tasks.scheduled_employee_sync",  # Note: Using full path
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"expires": 240.0},  # Expires after 4 minutes
    },
    "sync.nightly_full_employee_sync": {
        "task": "pyerp.sync.tasks.nightly_full_employee_sync",  # Note: Using full path
        "schedule": crontab(hour=2, minute=15),  # Run at 2:15 AM daily
        "options": {"expires": 10800.0},  # Expires after 3 hours
    },
    # Add other periodic tasks here if needed
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
#             "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
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

# Image API Configuration
IMAGE_API = {
    "BASE_URL": os.environ.get(
        "IMAGE_API_URL", "http://webapp.zinnfiguren.de/api/"
    ),
    "USERNAME": os.environ.get("IMAGE_API_USERNAME", ""),
    "PASSWORD": os.environ.get("IMAGE_API_PASSWORD", ""),
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
