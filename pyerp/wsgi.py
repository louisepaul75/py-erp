"""
WSGI config for pyERP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables

load_environment_variables()

# Set the default Django settings module if not defined
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")

# Get the WSGI application
application = get_wsgi_application()
