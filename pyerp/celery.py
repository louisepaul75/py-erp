import os
from pathlib import Path  # noqa: F401

from celery import Celery

# Load environment variables using centralized loader
from pyerp.utils.env_loader import load_environment_variables
load_environment_variables()

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')

# Create Celery instance
app = Celery('pyerp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes
app.config_from_object('django.conf:settings', namespace='CELERY')
  # noqa: F841

# Load task modules from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
  # noqa: F841


def debug_task(self):
    """Debug task to test Celery functionality."""
    print(f'Request: {self.request!r}')
