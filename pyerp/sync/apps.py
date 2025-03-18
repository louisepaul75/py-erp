"""App configuration for the sync module."""

from django.apps import AppConfig
from pyerp.utils.logging import get_logger


logger = get_logger(__name__)


class SyncConfig(AppConfig):
    """Configuration for the Sync app."""

    name = "pyerp.sync"
    verbose_name = "Data Synchronization"

    def ready(self):
        """Initialize the app and connect signals."""
        # Import and register signals
        try:
            # Import celery app and tasks
            from pyerp.celery_app import app as celery_app
            from . import tasks

            # Register periodic tasks
            for task_name in dir(tasks):
                task = getattr(tasks, task_name)
                if hasattr(task, "periodic_task"):
                    periodic_config = task.periodic_task
                    celery_app.conf.beat_schedule[periodic_config["name"]] = {
                        "task": f"pyerp.sync.tasks.{task_name}",
                        "schedule": periodic_config["schedule"],
                        "options": periodic_config.get("options", {}),
                    }

            logger.info("Sync app initialized with periodic tasks registered")

        except (ImportError, AttributeError) as e:
            # Handle the case where Celery is not available
            logger.warning(
                "Celery app not available, periodic tasks not registered: %s", str(e)
            )
