"""
Base settings for pyERP project.
"""

import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Assuming settings is inside pyerp/settings

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-test-key-for-base-settings'

# Site ID for Django Sites framework
SITE_ID = 1

# Debug settings
DEBUG = True

# Base installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # Add sites framework
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'allauth', # Add allauth
    'allauth.account',
    'allauth.socialaccount',
    'pyerp.core',
    'pyerp.business_modules.products',
    'pyerp.business_modules.business',
    'pyerp.business_modules.production',
    'pyerp.business_modules.inventory', # Add inventory app
    'pyerp.sync',
    'users',
    'django_celery_results', # Add celery results app
    'django_celery_beat', # Add celery beat app
    'pyerp.monitoring', # Add monitoring app
    'pyerp.utils.email_system', # Add email system app
]

# Base middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Add allauth middleware
    'users.middleware.UpdateLastSeenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Logging configuration
LOG_LEVEL = 'INFO'

# Debug toolbar settings
if DEBUG and not any(arg.startswith('test') for arg in sys.argv):
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://localhost",
    # Add other origins as needed (e.g., production frontend URL)
]
CORS_ALLOW_CREDENTIALS = True

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_LOCATION = 'static' # Example for storage backend config

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_LOCATION = 'media' # Example for storage backend config

# Root URL configuration
ROOT_URLCONF = 'pyerp.urls'

# WSGI application
WSGI_APPLICATION = 'pyerp.wsgi.application'

# ... rest of the file remains unchanged ... 