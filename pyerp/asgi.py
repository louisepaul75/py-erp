"""
ASGI config for pyERP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from pathlib import Path

from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Set the Django settings module based on environment variable or default to development
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')

# Get the ASGI application
application = get_asgi_application() 