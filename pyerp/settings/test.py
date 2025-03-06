"""
Test settings for pyERP project.

These settings extend the development settings with test-specific configurations.  # noqa: E501
"""

from .development import *  # noqa
import os
import sys
import socket  # noqa: F401
import psycopg2
from pathlib import Path  # noqa: F401
from .base import *  # noqa: F401

 # Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables
load_environment_variables(verbose=True)

 # Remove debug toolbar from installed apps
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

 # Remove debug toolbar middleware
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

 # Configure debug toolbar for tests
DEBUG_TOOLBAR_CONFIG = {
    'IS_RUNNING_TESTS': True,
}

 # Define PostgreSQL connection parameters
PG_PARAMS = {
    'ENGINE': 'django.db.backends.postgresql',  # noqa: E128
             'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
             'USER': os.environ.get('DB_USER', 'postgres'),
             'PASSWORD': os.environ.get('DB_PASSWORD', ''),
             'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
             'PORT': os.environ.get('DB_PORT', '5432'),
             'TEST': {
                 'NAME': 'test_pyerp_testing',  # noqa: E128
             },
}

 # Define SQLite connection parameters as fallback
SQLITE_PARAMS = {
    'ENGINE': 'django.db.backends.sqlite3',  # noqa: E128
    'NAME': 'file:memorydb_default?mode=memory&cache=shared',
    'TEST': {
    'NAME': 'file:memorydb_default?mode=memory&cache=shared',
},
}

 # Try to connect to PostgreSQL, fall back to SQLite if connection fails
try:
    print("Attempting to connect to PostgreSQL at {}:{}".format(PG_PARAMS['HOST'], PG_PARAMS['PORT']))  # noqa: E501
    conn = psycopg2.connect(
        dbname=PG_PARAMS['NAME'],  # noqa: F841
        user=PG_PARAMS['USER'],  # noqa: F841
        password=PG_PARAMS['PASSWORD'],  # noqa: F841
        host=PG_PARAMS['HOST'],  # noqa: F841
        port=PG_PARAMS['PORT'],  # noqa: F841
        connect_timeout=5  # noqa: F841
    )
    conn.close()
    print("SUCCESS: Connected to PostgreSQL")
    DATABASES = {'default': PG_PARAMS}  # noqa: F841
except Exception as e:
    print("ERROR: Could not connect to PostgreSQL:", str(e))
    print("\nFALLBACK: Using SQLite for testing")
    DATABASES = {'default': SQLITE_PARAMS}  # noqa: F841

 # Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

 # Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
    'console': {  # noqa: E128
    'class': 'logging.StreamHandler',
    'stream': sys.stdout,
},
           },
           'loggers': {
               'django': {  # noqa: E128
           'handlers': ['console'],
           'level': 'WARNING',
           },
           },
}
