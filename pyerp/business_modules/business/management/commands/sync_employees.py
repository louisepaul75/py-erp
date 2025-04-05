"""Management command to run employee sync."""

# Remove direct BaseCommand import and sync_employees task import
# import json # No longer needed for parsing filters here
# from django.core.management.base import BaseCommand
from django.utils import timezone # Keep if needed for other logic, remove if not

# Import the new base command
from pyerp.sync.management.commands.base_sync_command import BaseSyncCommand
# from pyerp.sync.tasks import sync_employees # No longer calling task directly


# Inherit from BaseSyncCommand
class Command(BaseSyncCommand):
    """Command to run employee sync using the base sync structure."""

    help = "Synchronize employee data from legacy ERP using BaseSyncCommand"
    entity_type = 'employee' # Define the entity type for this command

    # Remove add_arguments - handled by BaseSyncCommand
    # def add_arguments(self, parser):
    #     """Add command arguments."""
    #     ...

    def handle(self, *args, **options):
        """Run the command using the BaseSyncCommand framework."""
        self.stdout.write(self.style.SUCCESS(f"Starting {self.entity_type} sync..."))
        start_time = timezone.now()

        try:
            # 1. Get the mapping configuration
            mapping = self.get_mapping(self.entity_type)
            if not mapping:
                # Error message handled by get_mapping
                return 

            # 2. Build query parameters from command options
            query_params = self.build_query_params(options)

            # 3. Run the sync using the base command's runner
            # run_sync_via_command handles printing success/failure details
            success = self.run_sync_via_command(
                entity_type=self.entity_type,
                options=options,
                query_params=query_params
            ) 

            # Optional: Add final duration summary if needed, 
            # but run_sync_via_command often reports its own stats/duration.
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            final_status = "completed successfully" if success else "failed"
            self.stdout.write(
                f"{self.entity_type.capitalize()} sync {final_status} in {duration:.2f} seconds."
            )

        except Exception as e:
            # Catch any unexpected errors during setup/execution
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred during {self.entity_type} sync: {e}"))
            # Optionally re-raise or handle specific exceptions as needed

        # Removed old logic:
        # start_time = timezone.now()
        # ... manual filter parsing ...
        # ... direct call to sync_employees ...
        # ... manual result reporting ... 