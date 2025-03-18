"""
Base settings for pyERP project.

These settings are common to all environments and will be imported by environment-specific  # noqa: E501
settings files.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url  # noqa: F401

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add the project root to Python path to ensure imports work
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from pyerp.version import get_version  # noqa: E402

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-production")

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
IMAGE_API_CACHE_TIMEOUT = int(os.environ.get("IMAGE_API_CACHE_TIMEOUT", "3600"))

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_yasg",
    "django_celery_results",
    "django_celery_beat",
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
    "pyerp.external_api",
    "admin_tools",  # Admin tools app for database table view
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "pyerp.core.middleware.DatabaseConnectionMiddleware",
    "pyerp.core.middleware.AuthExemptMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pyerp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "pyerp" / "templates",
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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "pyerp_testing"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "192.168.73.65"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

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
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
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
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "django-db")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
JSON_LOGGING = os.environ.get("JSON_LOGGING", "False").lower() == "true"
try:
    LOG_FILE_SIZE_LIMIT = int(
        os.environ.get("LOG_FILE_SIZE_LIMIT", 2097152)
    )  # Default to 2MB
except ValueError:
    LOG_FILE_SIZE_LIMIT = 2097152  # 2MB in bytes

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "rename_fields": {
                "asctime": "timestamp",
                "levelname": "level",
            },
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json" if JSON_LOGGING else "verbose",
        },
        "app_file": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",
            "maxBytes": LOG_FILE_SIZE_LIMIT,
            "backupCount": 10,
            "formatter": "json" if JSON_LOGGING else "verbose",
        },
        "security_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "security.log",
            "maxBytes": LOG_FILE_SIZE_LIMIT,
            "backupCount": 10,
            "formatter": "json" if JSON_LOGGING else "verbose",
        },
        "performance_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "performance.log",
            "maxBytes": LOG_FILE_SIZE_LIMIT,
            "backupCount": 5,
            "formatter": "json" if JSON_LOGGING else "verbose",
        },
        "data_sync_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "data_sync.log",
            "maxBytes": LOG_FILE_SIZE_LIMIT,
            "backupCount": 10,
            "formatter": "json" if JSON_LOGGING else "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins", "console", "app_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security_file", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "pyerp": {
            "handlers": ["console", "app_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "pyerp.sync": {
            "handlers": ["console", "data_sync_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "pyerp.performance": {
            "handlers": ["performance_file"],
            "level": "INFO",
            "propagate": False,
        },
        "pyerp.external_api.images_cms": {
            "handlers": ["console", "data_sync_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# Image API Configuration
IMAGE_API = {
    "BASE_URL": os.environ.get("IMAGE_API_URL", "http://webapp.zinnfiguren.de/api/"),
    "USERNAME": os.environ.get("IMAGE_API_USERNAME", ""),
    "PASSWORD": os.environ.get("IMAGE_API_PASSWORD", ""),
    "TIMEOUT": int(
        os.environ.get("IMAGE_API_TIMEOUT", 60)
    ),  # Increased default timeout
    "CACHE_ENABLED": os.environ.get("IMAGE_API_CACHE_ENABLED", "True").lower()
    == "true",
    "CACHE_TIMEOUT": int(os.environ.get("IMAGE_API_CACHE_TIMEOUT", 3600)),  # 1 hour
    "VERIFY_SSL": os.environ.get("IMAGE_API_VERIFY_SSL", "False").lower()
    == "true",  # Default to not verifying SSL
}

# Update loggers for image API
LOGGING["loggers"]["pyerp.external_api.images_cms"] = {
    "handlers": ["console", "data_sync_file"],
    "level": LOG_LEVEL,
    "propagate": False,
}
