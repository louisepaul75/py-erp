"""
Local override settings for pyERP project.

These settings override the base settings to improve database performance.
"""

from .base import *  # noqa

# Override database settings to improve performance
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'UZ3*cMrCuFJm-fTA7csE'),
        'HOST': os.environ.get('DB_HOST', '192.168.73.65'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Keep connections open for 10 minutes
        'CONN_HEALTH_CHECKS': True,  # Enable connection health checks
        'OPTIONS': {
            'connect_timeout': 10,  # Connection timeout in seconds
        },
    }
}

# Print a message to confirm these settings are being used
print("Using local_override.py settings with optimized database connection settings") 