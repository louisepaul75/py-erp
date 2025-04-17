"""Management command to deactivate duplicate active SyncMapping entries."""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pyerp.sync.models import SyncMapping

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Finds and deactivates duplicate active SyncMapping entries for a given
    entity type, keeping only the one with the highest ID.
    """

    help = (
        "Deactivates duplicate active SyncMapping entries, keeping the highest ID."
    )

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "entity_type",
            type=str,
            nargs='?', # Make entity_type optional
            default="sales_records", # Default to sales_records
            help="The entity_type to check for duplicate active mappings (default: sales_records)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Execute the command."""
        entity_type = options["entity_type"]
        self.stdout.write(
            f"Checking for duplicate active SyncMappings for entity_type='{entity_type}'..."
        )

        try:
            # Find all active mappings for the given entity type, ordered by ID
            active_mappings = SyncMapping.objects.filter(
                entity_type=entity_type, active=True
            ).order_by("-id") # Highest ID first

            count = active_mappings.count()

            if count <= 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"No duplicate active mappings found for '{entity_type}'."
                    )
                )
                return

            self.stdout.write(
                self.style.WARNING(
                    f"Found {count} active mappings for '{entity_type}'. Keeping the newest (ID: {active_mappings.first().id})."
                )
            )

            # Get the ID of the mapping to keep (the one with the highest ID)
            mapping_to_keep_id = active_mappings.first().id

            # Find mappings to deactivate (all active ones except the one to keep)
            mappings_to_deactivate = SyncMapping.objects.filter(
                entity_type=entity_type, active=True
            ).exclude(id=mapping_to_keep_id)

            num_to_deactivate = mappings_to_deactivate.count()

            if num_to_deactivate > 0:
                # Deactivate them
                updated_count = mappings_to_deactivate.update(active=False)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully deactivated {updated_count} duplicate mapping(s) for '{entity_type}'."
                    )
                )
            else:
                # This case shouldn't technically be reached if count > 1, but included for safety
                self.stdout.write(
                    self.style.NOTICE(
                        f"No mappings needed deactivation for '{entity_type}' (after excluding the one to keep)."
                    )
                )


        except Exception as e:
            logger.error(f"Error during deduplication for '{entity_type}': {e}", exc_info=True)
            raise CommandError(
                f"Failed to deduplicate mappings for '{entity_type}'. Error: {e}"
            ) 