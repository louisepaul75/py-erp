"""
Celery configuration entry point.
This module imports the configured Celery app from settings.
"""

import os

# Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables

load_environment_variables()

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")

from celery import Celery

# Create Celery instance
app = Celery("pyerp")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery functionality."""
    print(f"Request: {self.request!r}")
