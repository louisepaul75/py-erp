"""
Celery app configuration for pyERP.
"""

import os
from celery import Celery

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")

# Create Celery instance
app = Celery("pyerp")

# Use Django settings for Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load tasks from all registered apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery functionality."""
    print(f"Request: {self.request!r}")
