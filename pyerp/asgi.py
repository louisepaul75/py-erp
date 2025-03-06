"""
ASGI config for pyERP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from pathlib import Path  # noqa: F401

from django.core.asgi import get_asgi_application

 # Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables
load_environment_variables()

 # Set the Django settings module based on environment or default to development  # noqa: E501
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')

 # Get the ASGI application
application = get_asgi_application()  # noqa: F841
