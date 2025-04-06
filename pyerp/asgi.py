"""
ASGI config for pyERP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Import and use the centralized environment loader
from pyerp.utils.env_loader import load_environment_variables

load_environment_variables(verbose=True)

# Set the default Django settings module if not defined
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")

# Get the ASGI application
application = get_asgi_application()
