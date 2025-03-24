"""Management command to run employee sync."""

import json
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
        time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        self.stdout.write(
            self.style.SUCCESS(f"Starting employee sync at {time_str}")
        )

        # Run sync
        full_sync = options.get("full", False)
        filters = None
        
        # Parse filters if provided
        if options.get("filters"):
            try:
                filters = json.loads(options["filters"])
                filter_msg = f"with filters: {filters}" if filters else ""
                sync_type = 'full' if full_sync else 'incremental'
                self.stdout.write(f"Running {sync_type} sync {filter_msg}")
            except json.JSONDecodeError:
                error_msg = "Invalid JSON format for filters"
                self.stdout.write(
                    self.style.ERROR(f"Sync failed: {error_msg}")
                )
                return
        else:
            # No filters provided
            sync_type = 'full' if full_sync else 'incremental'
            self.stdout.write(f"Running {sync_type} sync")
        
        # Execute sync
        try:
            # Call the sync_employees function with the specified parameters
            result = sync_employees(full_sync=full_sync, filters=filters)
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            # Check the status of the result
            if result.get("status") == "success":
                total = result.get('records_processed', 0)
                success = result.get('records_succeeded', 0)
                failed = result.get('records_failed', 0)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sync completed in {duration:.2f}s: "
                        f"{total} total, {success} success, {failed} failed"
                    )
                )
            else:
                # This is important for test_sync_employees_command_failure
                error_msg = result.get('message', 'Unknown error')
                self.stdout.write(
                    self.style.ERROR(f"Sync failed: {error_msg}")
                )
        except Exception as e:
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(
                self.style.ERROR(f"Sync failed: {str(e)}")
            ) 