"""
WSGI config for pyERP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path  # noqa: F401

from django.core.wsgi import get_wsgi_application

 # Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables
load_environment_variables()

 # Set the Django settings module based on environment or default to development  # noqa: E501
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')

 # Get the WSGI application
application = get_wsgi_application()  # noqa: F841
