"""
Management command to synchronize box types from the legacy parameter table.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    """
    Command to synchronize box types from the legacy parameter table.
    """

    help = "Synchronize box types from the legacy parameter table"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force full sync even if incremental sync is configured",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        debug = options.get("debug", False)
        force = options.get("force", False)

        if debug:
            logger.info("Debug mode enabled")

        start_time = timezone.now()
        self.stdout.write(f"Starting box types sync at {start_time}")

        try:
            # Get the box_types mapping
            mappings = SyncMapping.objects.filter(entity_type="box_types", active=True)

            if not mappings.exists():
                self.stdout.write(self.style.ERROR("No active box_types mapping found"))
                return

            # Use the first active mapping
            mapping = mappings.first()
            self.stdout.write(f"Using mapping: {mapping}")

            # Create the pipeline using PipelineFactory
            pipeline = PipelineFactory.create_pipeline(mapping)

            # Run the sync
            sync_log = pipeline.run(incremental=not force, batch_size=100)

            # Log the results
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()

            if sync_log.status == "completed":
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Box types sync completed in {duration:.2f} seconds"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Box types sync completed with status {sync_log.status} "
                        f"in {duration:.2f} seconds"
                    )
                )

            self.stdout.write(
                f"Processed {sync_log.records_processed} records, "
                f"succeeded {sync_log.records_succeeded}, "
                f"failed {sync_log.records_failed}"
            )

            if sync_log.error_message:
                self.stdout.write(self.style.ERROR(f"Error: {sync_log.error_message}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during box types sync: {e}"))
            logger.exception("Error during box types sync")
            raise
