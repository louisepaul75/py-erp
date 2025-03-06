"""
Production settings for pyERP project.

These settings extend the base settings with production-specific configurations
focused on security and performance.
"""

import os
import dj_database_url  # noqa: F401
from .base import *  # noqa

 # SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

 # Must be set from environment in production
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

 # Database configuration
DATABASES = {  # noqa: F841
    'default': {  # noqa: E128
    'ENGINE': 'django.db.backends.postgresql',
             'NAME': os.environ.get('DB_NAME', 'pyerp_production'),
             'USER': os.environ.get('DB_USER', 'admin'),
             'PASSWORD': os.environ.get('DB_PASSWORD', ''),
             'HOST': os.environ.get('DB_HOST', '192.168.73.64'),
             'PORT': os.environ.get('DB_PORT', '5432'),
             }
}

 # Alternative DATABASE_URL configuration (commented out)

 # noqa: F841
 #     'default': dj_database_url.config(
 #         default=os.environ.get(  # noqa: E128
 #             'DATABASE_URL',
  #             'postgresql://user:password@localhost:5432/pyerp_production'

 # noqa: F841
 #     )
 # }

 # Production security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

 # CORS settings - only allow specific origins in production
CORS_ALLOWED_ORIGINS = [origin for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]  # noqa: E501
CORS_ALLOW_ALL_ORIGINS = False

 # Cache settings
try:
    import django_redis  # noqa: F401
    CACHES = {  # noqa: F841
        'default': {  # noqa: E128
        'BACKEND': 'django_redis.cache.RedisCache',
              'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),  # noqa: E501
              'OPTIONS': {
                  'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # noqa: E128
              }
              }
    }
    print("Django Redis cache enabled")
except ImportError:
    print("WARNING: django_redis not found, falling back to LocMemCache")
    CACHES = {  # noqa: F841
        'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # noqa: E128
        'LOCATION': 'pyerp-fallback',
    }
    }

 # AWS S3 settings for static and media files
if os.environ.get('USE_S3', 'False').lower() == 'true':
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')  # noqa: F841
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')  # noqa: F841
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'  # noqa: F841
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}  # noqa: F841

 # S3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'  # noqa: F841
    STATICFILES_STORAGE = 'pyerp.core.storage_backends.StaticStorage'  # noqa: F841

 # S3 media settings
    MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'  # noqa: F841
    DEFAULT_FILE_STORAGE = 'pyerp.core.storage_backends.MediaStorage'  # noqa: F841

 # Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')  # noqa: F841
try:
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))  # noqa: F841
except ValueError:
    EMAIL_PORT = 587  # noqa: F841
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

 # Celery settings for production
CELERY_TASK_ALWAYS_EAGER = False

 # Sentry monitoring (uncomment to enable)
 # import sentry_sdk
 # from sentry_sdk.integrations.django import DjangoIntegration
 #

 # noqa: F841

 # noqa: F841

 # noqa: F841

 # noqa: F841
 # )
