"""
Base settings for pyERP project.

These settings are common to all environments and will be imported by environment-specific
settings files.
"""

import os
from pathlib import Path

import dj_database_url
from .jwt import SIMPLE_JWT  # Import JWT settings

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',  # Add JWT app
    'django_filters',
    'corsheaders',
    'drf_yasg',
    'django_celery_results',
    'django_celery_beat',
]

LOCAL_APPS = [
    'pyerp.core',
    'pyerp.products',
    # Make optional apps conditional to prevent crashes
    'pyerp.monitoring',  # Always include the monitoring app
]

# Basic required apps that must exist
REQUIRED_APPS = ['pyerp.core', 'pyerp.products']

# Other apps that are loaded conditionally
OPTIONAL_APPS = [
    'pyerp.sales',
    'pyerp.inventory', 
    'pyerp.production',
    'pyerp.legacy_sync',
]

# Initialize LOCAL_APPS with required apps
LOCAL_APPS = REQUIRED_APPS.copy()

# Try to import each optional app - if it fails, we'll skip it
for app in OPTIONAL_APPS:
    try:
        __import__(app)
        LOCAL_APPS.append(app)
        print(f"{app} module found and added to INSTALLED_APPS")
    except ImportError:
        print(f"WARNING: {app} module could not be imported, skipping it in INSTALLED_APPS")

# Make sure monitoring app is always included
if 'pyerp.monitoring' not in LOCAL_APPS:
    LOCAL_APPS.append('pyerp.monitoring')

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'pyerp.core.middleware.AuthExemptMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pyerp.core.middleware.DatabaseConnectionMiddleware',
]

ROOT_URLCONF = 'pyerp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'pyerp' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pyerp.wsgi.application'

# Authentication settings
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# First try to use DATABASE_URL if provided
if 'DATABASE_URL' in os.environ:
    # Parse database configuration from DATABASE_URL
    print(f"Using DATABASE_URL: {os.environ.get('DATABASE_URL', '').replace('://', '://****:****@')}")
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to explicit database settings
    print("DATABASE_URL not provided, using explicit database settings")
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

# If SQLite is in use but filename has no path, ensure it's in a writable location
if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    db_name = DATABASES['default']['NAME']
    if not os.path.isabs(db_name):
        DATABASES['default']['NAME'] = os.path.join(BASE_DIR, db_name)

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'de'  # Set German as the default language

# Define supported languages
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]

# Set the location of the translation files
LOCALE_PATHS = [
    BASE_DIR / 'pyerp' / 'locale',
]

# Language cookie settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # 1 year
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SECURE = False
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = None

# Language detection settings
USE_I18N = True
USE_L10N = True

# Session settings
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
SESSION_SAVE_EVERY_REQUEST = True  # Save the session at every request

TIME_ZONE = 'UTC'
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'pyerp' / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cache configuration - use dummy cache in development for better debugging
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Media files (User Uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Celery settings
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
JSON_LOGGING = os.environ.get('JSON_LOGGING', 'False').lower() == 'true'
try:
    LOG_FILE_SIZE_LIMIT = int(os.environ.get('LOG_FILE_SIZE_LIMIT', 2097152))  # Default to 2MB
except ValueError:
    # Fallback in case the environment variable has issues
    LOG_FILE_SIZE_LIMIT = 2097152  # 2MB in bytes

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'rename_fields': {
                'asctime': 'timestamp',
                'levelname': 'level',
            },
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'app_file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 10,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 10,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'performance_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'performance.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 5,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'data_sync_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'data_sync.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 10,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'app_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'app_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console', 'app_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'pyerp': {
            'handlers': ['console', 'app_file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'pyerp.legacy_sync': {
            'handlers': ['console', 'data_sync_file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'pyerp.performance': {
            'handlers': ['performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'pyerp.products.image_api': {
            'handlers': ['console', 'data_sync_file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Image API Configuration
IMAGE_API = {
    'BASE_URL': os.environ.get('IMAGE_API_URL', 'http://webapp.zinnfiguren.de/api/'),
    'USERNAME': os.environ.get('IMAGE_API_USERNAME', ''),
    'PASSWORD': os.environ.get('IMAGE_API_PASSWORD', ''),
    'TIMEOUT': 30,  # Default value
    'CACHE_ENABLED': os.environ.get('IMAGE_API_CACHE_ENABLED', 'True').lower() == 'true',
    'CACHE_TIMEOUT': 3600,  # Default to 1 hour
}

# Try to get IMAGE_API_TIMEOUT from environment
try:
    IMAGE_API['TIMEOUT'] = int(os.environ.get('IMAGE_API_TIMEOUT', 30))
except ValueError:
    # Keep default if conversion fails
    pass

# Try to get IMAGE_API_CACHE_TIMEOUT from environment
try:
    IMAGE_API['CACHE_TIMEOUT'] = int(os.environ.get('IMAGE_API_CACHE_TIMEOUT', 3600))
except ValueError:
    # Keep default if conversion fails
    pass

# Custom CSRF failure view
CSRF_FAILURE_VIEW = 'pyerp.core.views.csrf_failure'

# CSRF Trusted Origins - important for Docker environments
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
if not any(CSRF_TRUSTED_ORIGINS):
    # Default trusted origins if not specified in environment
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8050',
        'http://127.0.0.1:8050',
    ]

# Update loggers for image API
LOGGING['loggers']['pyerp.products.image_api'] = {
    'handlers': ['console', 'data_sync_file'],
    'level': LOG_LEVEL,
    'propagate': False,
} 