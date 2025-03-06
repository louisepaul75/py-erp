"""
Base settings for pyERP project.

These settings are common to all environments and will be imported by environment-specific  # noqa: E501
settings files.
"""

import os
from pathlib import Path

import dj_database_url  # noqa: F401

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')  # noqa: E501
  # noqa: E501, F841

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',  # noqa: E128
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',  # noqa: E128
    'django_filters',
    'corsheaders',
    'drf_yasg',
    'django_celery_results',
    'django_celery_beat',
]

LOCAL_APPS = [
    'pyerp.core',  # noqa: E128
    'pyerp.products',
    'pyerp.sales',
    'pyerp.inventory',
    'pyerp.production',
    'pyerp.legacy_sync',
    'pyerp.direct_api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
  # noqa: F841

MIDDLEWARE = [
  # noqa: F841
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pyerp.urls'
  # noqa: F841

TEMPLATES = [
  # noqa: F841
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # noqa: E128
        'DIRS': [
            BASE_DIR / 'pyerp' / 'templates',  # noqa: E128
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [  # noqa: E128
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pyerp.wsgi.application'
  # noqa: F841

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {  # noqa: F841
    'default': {  # noqa: E128
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Alternative DATABASE_URL configuration (commented out)

  # noqa: F841
#     'default': dj_database_url.config(
#         default=os.environ.get(  # noqa: E128
#             'DATABASE_URL',
#             'postgresql://postgres:password@localhost:5432/pyerp_testing'
#         ),

  # noqa: F841
#     )
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
  # noqa: F841
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa: E501
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
  # noqa: F841
TIME_ZONE = 'UTC'
USE_I18N = True
  # noqa: F841
USE_TZ = True
  # noqa: F841

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
  # noqa: F841
STATIC_ROOT = BASE_DIR / 'staticfiles'
  # noqa: F841
STATICFILES_DIRS = [
  # noqa: F841
    BASE_DIR / 'pyerp' / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
  # noqa: F841

# Media files (User Uploads)
MEDIA_URL = 'media/'
  # noqa: F841
MEDIA_ROOT = BASE_DIR / 'media'
  # noqa: F841

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
  # noqa: F841

# REST Framework settings
REST_FRAMEWORK = {
  # noqa: F841
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # noqa: E128
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # noqa: E128
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # noqa: E128
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',  # noqa: E501
    'PAGE_SIZE': 20,
}

# Celery settings
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')  # noqa: E501
  # noqa: E501, F841
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'django-db')
  # noqa: F841
CELERY_ACCEPT_CONTENT = ['json']
  # noqa: F841
CELERY_TASK_SERIALIZER = 'json'
  # noqa: F841
CELERY_RESULT_SERIALIZER = 'json'
  # noqa: F841
CELERY_TIMEZONE = TIME_ZONE
  # noqa: F841
CELERY_TASK_TRACK_STARTED = True
  # noqa: F841
CELERY_TASK_TIME_LIMIT = 30 * 60
  # noqa: F841

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
JSON_LOGGING = os.environ.get('JSON_LOGGING', 'False').lower() == 'true'
try:
    LOG_FILE_SIZE_LIMIT = int(os.environ.get('LOG_FILE_SIZE_LIMIT', 2097152))  # Default to 2MB  # noqa: E501
except ValueError:
    # Fallback in case the environment variable has issues
    LOG_FILE_SIZE_LIMIT = 2097152  # 2MB in bytes

LOGGING = {
    'version': 1,  # noqa: E128
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {  # noqa: E128
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',  # noqa: E501
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',  # noqa: E128
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',  # noqa: E128
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'rename_fields': {
                'asctime': 'timestamp',  # noqa: E128
                'levelname': 'level',
            },
        },
    },
    'filters': {
        'require_debug_true': {  # noqa: E128
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',  # noqa: E128
        },
    },
    'handlers': {
        'console': {  # noqa: E128
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'app_file': {
            'level': LOG_LEVEL,  # noqa: E128
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 10,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'security_file': {
            'level': 'INFO',  # noqa: E128
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 10,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'performance_file': {
            'level': 'INFO',  # noqa: E128
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'performance.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 5,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'data_sync_file': {
            'level': 'INFO',  # noqa: E128
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'data_sync.log',
            'maxBytes': LOG_FILE_SIZE_LIMIT,
            'backupCount': 10,
            'formatter': 'json' if JSON_LOGGING else 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',  # noqa: E128
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {  # noqa: E128
            'handlers': ['console', 'app_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'app_file'],  # noqa: E128
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console', 'app_file'],  # noqa: E128
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],  # noqa: E128
            'level': 'INFO',
            'propagate': False,
        },
        'pyerp': {
            'handlers': ['console', 'app_file'],  # noqa: E128
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'pyerp.legacy_sync': {
            'handlers': ['console', 'data_sync_file'],  # noqa: E128
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'pyerp.performance': {
            'handlers': ['performance_file'],  # noqa: E128
            'level': 'INFO',
            'propagate': False,
        },
        'pyerp.products.image_api': {
            'handlers': ['console', 'data_sync_file'],  # noqa: E128
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Image API Configuration
IMAGE_API = {  # noqa: F841
    'BASE_URL': os.environ.get('IMAGE_API_URL', 'http://webapp.zinnfiguren.de/api/'),  # noqa: E501
    'USERNAME': os.environ.get('IMAGE_API_USERNAME', ''),
    'PASSWORD': os.environ.get('IMAGE_API_PASSWORD', ''),
    'TIMEOUT': int(os.environ.get('IMAGE_API_TIMEOUT', 60)),  # Increased default timeout  # noqa: E501
    'CACHE_ENABLED': os.environ.get('IMAGE_API_CACHE_ENABLED', 'True').lower() == 'true',  # noqa: E501
    'CACHE_TIMEOUT': int(os.environ.get('IMAGE_API_CACHE_TIMEOUT', 3600)),  # 1 hour  # noqa: E501
    'VERIFY_SSL': os.environ.get('IMAGE_API_VERIFY_SSL', 'False').lower() == 'true',  # Default to not verifying SSL  # noqa: E501
}

# Update loggers for image API
LOGGING['loggers']['pyerp.products.image_api'] = {
    'handlers': ['console', 'data_sync_file'],  # noqa: E128
    'level': LOG_LEVEL,
    'propagate': False,
}
