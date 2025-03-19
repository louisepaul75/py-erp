"""
Celery app configuration for pyERP.
"""

import os

# Skip initialization if SKIP_CELERY_IMPORT is set
# This helps prevent circular imports when running tests
if os.environ.get("SKIP_CELERY_IMPORT") == "1":
    # Create placeholders to prevent import errors
    app = None
    
    # Mock the states module to prevent import errors in django_celery_results
    class states:
        """Mock states module with essential constants."""
        PENDING = 'PENDING'
        RECEIVED = 'RECEIVED'
        STARTED = 'STARTED'
        SUCCESS = 'SUCCESS'
        FAILURE = 'FAILURE'
        REVOKED = 'REVOKED'
        RETRY = 'RETRY'
        IGNORED = 'IGNORED'
        
        READY_STATES = frozenset({SUCCESS, FAILURE, REVOKED})
        UNREADY_STATES = frozenset({PENDING, RECEIVED, STARTED, RETRY})
        EXCEPTION_STATES = frozenset({FAILURE, RETRY, REVOKED})
        PROPAGATE_STATES = frozenset({FAILURE, REVOKED})
    
    def debug_task(*args, **kwargs):
        """Placeholder for debug task when Celery is skipped."""
        pass
else:
    from celery import Celery, states

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
