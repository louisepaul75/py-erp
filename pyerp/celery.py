import os
from pathlib import Path

from celery import Celery
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
env_file = Path('../') / '.env'
if env_file.exists():
    load_dotenv(str(env_file))

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')

# Create Celery instance
app = Celery('pyerp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery functionality."""
    print(f'Request: {self.request!r}') 