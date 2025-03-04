"""
JWT settings for pyERP project.

These settings configure the JWT authentication for the REST API.
"""

from datetime import timedelta
import os

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production'),  # Explicitly use Django's SECRET_KEY
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    # Custom settings
    'AUTH_COOKIE': 'access_token',  # Cookie name for storing the JWT token
    'AUTH_COOKIE_DOMAIN': None,     # Domain for the cookie
    'AUTH_COOKIE_SECURE': False,    # Whether the cookie should be secure (HTTPS only)
    'AUTH_COOKIE_HTTP_ONLY': True,  # Whether the cookie should be HTTP only
    'AUTH_COOKIE_PATH': '/',        # Path for the cookie
    'AUTH_COOKIE_SAMESITE': 'Lax',  # SameSite attribute for the cookie
} 