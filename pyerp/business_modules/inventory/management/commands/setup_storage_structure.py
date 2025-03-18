"""Management command to set up the dual-table storage structure."""

import os
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Set up the dual-table storage structure for inventory management.

    This command performs the following steps:
    1. Creates and runs migrations to implement the new schema
    2. Sets up synchronization configuration for the new tables
    3. Validates the database schema after changes
    """

    help = "Set up the dual-table storage structure for inventory management"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--skip-migrations",
            action="store_true",
            help="Skip creating and running migrations",
        )
        parser.add_argument(
            "--skip-sync-setup",
            action="store_true",
            help="Skip setting up synchronization configuration",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreating migrations even if they exist",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(
            self.style.SUCCESS("Setting up dual-table storage structure...")
        )

        # Step 1: Make and run migrations
        if not options["skip_migrations"]:
            self._run_migrations(force=options["force"])

        # Step 2: Set up synchronization
        if not options["skip_sync_setup"]:
            self._setup_sync()

        # Step 3: Validate schema
        self._validate_schema()

        self.stdout.write(
            self.style.SUCCESS("Dual-table storage structure setup complete!")
        )

    def _run_migrations(self, force=False):
        """Create and run migrations for the new schema."""
        self.stdout.write("Creating migrations for the new schema...")

        # Check if migrations already exist
        migrations_dir = os.path.join(
            settings.BASE_DIR, "pyerp", "business_modules", "inventory", "migrations"
        )

        # Create migrations
        try:
            call_command("makemigrations", "inventory")
            self.stdout.write(
                self.style.SUCCESS("Created migrations for the new schema")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating migrations: {e}"))
            raise

        # Run migrations
        try:
            self.stdout.write("Running migrations...")
            call_command("migrate", "inventory")
            self.stdout.write(self.style.SUCCESS("Migrations applied successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error running migrations: {e}"))
            raise

    def _setup_sync(self):
        """Set up synchronization for the new tables."""
        self.stdout.write("Setting up synchronization configuration...")

        try:
            call_command("setup_inventory_sync")
            self.stdout.write(
                self.style.SUCCESS("Synchronization configuration updated")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error setting up synchronization: {e}")
            )
            raise

    def _validate_schema(self):
        """Validate the database schema after changes."""
        self.stdout.write("Validating database schema...")

        # Check that our new tables exist
        tables_to_check = [
            "inventory_productstorage",
            "inventory_boxstorage",
        ]

        with connection.cursor() as cursor:
            for table in tables_to_check:
                cursor.execute(
                    "SELECT EXISTS (SELECT FROM information_schema.tables "
                    "WHERE table_name = %s)",
                    [table],
                )
                exists = cursor.fetchone()[0]

                if exists:
                    self.stdout.write(
                        self.style.SUCCESS(f"Table {table} exists in the database")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Table {table} does not exist in the database"
                        )
                    )

        # Run Django's system check framework
        self.stdout.write("Running system checks...")
        call_command("check", "inventory")
        self.stdout.write(self.style.SUCCESS("System checks passed"))
