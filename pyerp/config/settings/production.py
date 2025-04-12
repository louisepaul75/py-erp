"""
Production settings for pyERP project.

These settings extend the base settings with production-specific configurations
focused on security and performance.
"""

import os

import dj_database_url  # noqa: F401

from .base import *  # noqa
from .base import MIDDLEWARE as BASE_MIDDLEWARE # Import base middleware

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Conditionally import HTTPS settings for local proxy setups
if os.environ.get("USE_LOCAL_HTTPS_PROXY", "False").lower() == "true":
    try:
        from .settings_https import *  # noqa
        print(
            "INFO: Loaded HTTPS proxy settings for local production environment."
        )
    except ImportError:
        print(
            "WARNING: USE_LOCAL_HTTPS_PROXY is true, but "
            "settings_https.py not found."
        )

# Must be set from environment in production
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Database configuration - REMOVED TO USE BASE SETTINGS WITH 1PASSWORD
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ.get("DB_NAME", "pyerp_production"),
#         "USER": os.environ.get("DB_USER", "admin"),
#         "PASSWORD": os.environ.get("DB_PASSWORD", ""),
#         "HOST": os.environ.get("DB_HOST", "192.168.73.64"),
#         "PORT": os.environ.get("DB_PORT", "5432"),
#         "OPTIONS": {
#             "connect_timeout": 10,  # Connection timeout in seconds
#             "client_encoding": "UTF8",
#             "sslmode": "prefer",
#         },
#     },
# }

# Alternative DATABASE_URL configuration (commented out)

#     'default': dj_database_url.config(
#         default=os.environ.get(
#             'DATABASE_URL',
#             'postgresql://user:password@localhost:5432/pyerp_production'

#     )
# }

# Production security settings
# Only set SECURE_SSL_REDIRECT if not using a local proxy override
if not os.environ.get("USE_LOCAL_HTTPS_PROXY", "False").lower() == "true":
    SECURE_SSL_REDIRECT = True
else:
    SECURE_SSL_REDIRECT = False  # Let the local proxy handle redirects

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Set cookie security based on whether HTTPS is effectively enabled
_use_local_https = os.environ.get("USE_LOCAL_HTTPS_PROXY", "False").lower() == "true"
CSRF_COOKIE_SECURE = _use_local_https or SECURE_SSL_REDIRECT
SESSION_COOKIE_SECURE = _use_local_https or SECURE_SSL_REDIRECT

# CORS settings - only allow specific origins in production
CORS_ALLOWED_ORIGINS = [
    origin
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
CORS_ALLOW_ALL_ORIGINS = False

# Cache settings
try:
    import django_redis  # noqa: F401

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get(
                "REDIS_URL", "redis://localhost:6379/1"
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        },
    }
    print("Django Redis cache enabled")
except ImportError:
    print("WARNING: django_redis not found, falling back to LocMemCache")
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pyerp-fallback",
        },
    }

# AWS S3 settings for static and media files
if os.environ.get("USE_S3", "False").lower() == "true":
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    # S3 static settings
    STATIC_LOCATION = "static"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
    STATICFILES_STORAGE = "pyerp.core.storage_backends.StaticStorage"

    # S3 media settings
    MEDIA_LOCATION = "media"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"
    DEFAULT_FILE_STORAGE = "pyerp.core.storage_backends.MediaStorage"

# Email configuration for production
if os.environ.get("ANYMAIL_ESP", "").lower() == "smtp":
    # Use logging SMTP backend for SMTP
    EMAIL_BACKEND = "pyerp.utils.email_system.backends.LoggingEmailBackend"
else:
    # Use logging anymail backend for other ESPs
    EMAIL_BACKEND = "pyerp.utils.email_system.backends.LoggingAnymailBackend"

# Import anymail settings
from .anymail import *  # noqa

# Middleware configuration - Extend base middleware
MIDDLEWARE = BASE_MIDDLEWARE + [
    # Add production-specific middleware here, if any, or ensure they are
    # already in BASE_MIDDLEWARE if appropriate.
    # Example: Middleware specific to production logging or monitoring
    # "pyerp.middleware.request_logger_middleware.RequestLoggerMiddleware",
    # Note: SecurityMiddleware, SessionMiddleware, CorsMiddleware,
    # CommonMiddleware, CsrfViewMiddleware, AuthMiddleware, MessagesMiddleware,
    # LocaleMiddleware, ClickjackingMiddleware, AccountMiddleware
    # should already be in BASE_MIDDLEWARE.
    # Ensure Whitenoise is correctly placed (often high up)
]

# Ensure Whitenoise is placed correctly (after SecurityMiddleware)
if 'whitenoise.middleware.WhiteNoiseMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('whitenoise.middleware.WhiteNoiseMiddleware')
if 'django.middleware.security.SecurityMiddleware' in MIDDLEWARE:
    whitenoise_insert_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1
    MIDDLEWARE.insert(whitenoise_insert_index, 'whitenoise.middleware.WhiteNoiseMiddleware')
else: # If SecurityMiddleware is not present for some reason, add it near the top
    MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Conditionally add memory profiler middleware if enabled
if os.environ.get("ENABLE_MEMORY_PROFILING", "false").lower() == "true":
    # Insert after security/session/cors but before request-specific logic
    insert_index = MIDDLEWARE.index("django.middleware.common.CommonMiddleware")
    MIDDLEWARE.insert(insert_index, "pyerp.middleware.memory_profiler_middleware.MemoryProfilerMiddleware")
    print("INFO: Memory Profiler Middleware enabled.")

# Add email_system to installed apps
INSTALLED_APPS += ["pyerp.utils.email_system"]  # noqa

# Legacy email settings (kept for backwards compatibility)
# These will be used if ANYMAIL_ESP is not set
if os.environ.get("ANYMAIL_ESP") is None and os.environ.get("EMAIL_HOST"):
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

# Celery settings for production
CELERY_TASK_ALWAYS_EAGER = False

# Sentry monitoring (uncomment to enable)
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
#


# )
