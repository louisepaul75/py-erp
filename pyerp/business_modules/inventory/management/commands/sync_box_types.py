"""
Management command to synchronize box types from the legacy parameter table.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyerp.sync.pipeline import SyncPipeline
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
            # Initialize the sync pipeline for box types
            pipeline = SyncPipeline(
                component_name="box_types",
                config_file="inventory_sync.yaml",
                force_full_sync=force,
            )
            
            # Run the sync
            result = pipeline.run()
            
            # Log the results
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Box types sync completed in {duration:.2f} seconds"
                )
            )
            self.stdout.write(
                f"Processed {result.get('processed', 0)} records, "
                f"created {result.get('created', 0)}, "
                f"updated {result.get('updated', 0)}, "
                f"skipped {result.get('skipped', 0)}, "
                f"errors {result.get('errors', 0)}"
            )
            
            if result.get("errors", 0) > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"Encountered {result.get('errors', 0)} errors "
                        f"during sync"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during box types sync: {e}")
            )
            logger.exception("Error during box types sync")
            raise 