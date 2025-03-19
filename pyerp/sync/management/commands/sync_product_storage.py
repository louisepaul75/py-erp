"""Management command for synchronizing product storage data."""

import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize product storage data from legacy system."""

    help = "Synchronize product storage data from legacy system"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of records to process in each batch",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform full sync instead of incremental",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)

        self.stdout.write("Starting product storage synchronization...")

        # First sync Artikel_Lagerorte
        self.stdout.write("\nStep 1: Syncing product storage from Artikel_Lagerorte...")
        call_command(
            "sync_inventory",
            component="product_storage_artikel_lagerorte",
            batch_size=options["batch_size"],
            full=options["full"],
            debug=options["debug"],
        )

        # Then sync Lager_Schuetten
        self.stdout.write("\nStep 2: Syncing product storage from Lager_Schuetten...")
        call_command(
            "sync_inventory",
            component="product_storage_lager_schuetten",
            batch_size=options["batch_size"],
            full=options["full"],
            debug=options["debug"],
        )

        self.stdout.write(
            self.style.SUCCESS("\nProduct storage synchronization completed!")
        )
