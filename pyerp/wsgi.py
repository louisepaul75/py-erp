"""
WSGI config for pyERP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Set the Django settings module based on environment variable or default to development
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')

# Get the WSGI application
application = get_wsgi_application() 