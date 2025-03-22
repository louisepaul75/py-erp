"""Management command to run employee sync."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyerp.sync.tasks import sync_employees


class Command(BaseCommand):
    """Command to run employee sync."""

    help = "Synchronize employee data from legacy ERP"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--full",
            action="store_true",
            help="Run full sync (not incremental)",
        )
        parser.add_argument(
            "--filters",
            type=str,
            help="JSON string with filters to apply",
        )

    def handle(self, *args, **options):
        """Run the command."""
        start_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting employee sync at {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        )

        # Run sync
        full_sync = options.get("full", False)
        filters = None
        
        if options.get("filters"):
            import json
            try:
                filters = json.loads(options["filters"])
            except json.JSONDecodeError:
                self.stdout.write(
                    self.style.ERROR("Invalid JSON format for filters")
                )
                return
        
        self.stdout.write(
            f"Running {'full' if full_sync else 'incremental'} sync with filters: {filters}"
        )
        
        result = sync_employees(full_sync=full_sync, filters=filters)
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        if result["status"] == "success":
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sync completed in {duration:.2f}s: "
                    f"{result.get('records_processed', 0)} total, "
                    f"{result.get('records_succeeded', 0)} success, "
                    f"{result.get('records_failed', 0)} failed"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Sync failed: {result.get('message', 'Unknown error')}"
                )
            ) 