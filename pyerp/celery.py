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
    # Import signals and logging for profiling
    from celery.signals import worker_init, beat_init, task_prerun
    import logging
    import os

    logger = logging.getLogger(__name__)
    PROFILING_ENABLED = os.environ.get("ENABLE_MEMORY_PROFILING", "false").lower() == "true"

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

    # --- Memory Profiling Signal Handlers ---
    if PROFILING_ENABLED:
        try:
            from pyerp.core import memory_profiler

            @worker_init.connect(weak=False)
            def worker_init_handler(**kwargs):
                """Configure memory profiler when a Celery worker starts."""
                identifier = f"celery_worker_{os.getpid()}"
                memory_profiler.configure_profiler(identifier)
                logger.info(f"Celery worker_init: Memory profiler configured for {identifier}.")

            @beat_init.connect(weak=False)
            def beat_init_handler(**kwargs):
                """Configure memory profiler when Celery beat starts."""
                identifier = f"celery_beat_{os.getpid()}"
                memory_profiler.configure_profiler(identifier)
                logger.info(f"Celery beat_init: Memory profiler configured for {identifier}.")

            # Use task_prerun to take snapshots before tasks (adjust frequency if needed)
            @task_prerun.connect(weak=False)
            def task_prerun_handler(**kwargs):
                """Take memory snapshot before executing a task."""
                task_id = kwargs.get('task_id')
                task_name = kwargs.get('sender').name if kwargs.get('sender') else 'unknown_task'
                logger.debug(f"[{memory_profiler._process_identifier}] task_prerun signal received for task_id: {task_id}, task_name: {task_name}")
                memory_profiler.take_snapshot_if_needed()
                # Optionally log task details: logger.debug(f"Taking snapshot before task: {kwargs.get('task_id')}")

            logger.info("Celery memory profiling signal handlers connected.")

        except ImportError:
            logger.error("Celery: Failed to import memory_profiler. Profiling disabled.")
        except Exception as e:
            logger.error(f"Celery: Error configuring memory profiler signals: {e}", exc_info=True)
    else:
        logger.debug("Celery memory profiling signal handlers disabled.")
