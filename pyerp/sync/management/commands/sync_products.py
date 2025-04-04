"""Sync parent and variant products from legacy ERP."""

import logging
import yaml
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, NamedTuple, List, Optional
import os
import json

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory

# Configure database logging to ERROR level
db_logger = logging.getLogger("django.db.backends")
db_logger.setLevel(logging.ERROR)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add console handler with custom formatter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.propagate = False


class LoadResult(NamedTuple):
    """Result of a load operation."""

    created: int
    updated: int
    skipped: int
    errors: int
    error_details: list


class Command(BaseCommand):
    """Django management command to sync parent and variant products."""

    help = "Sync parent and variant products from legacy ERP system"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--env",
            type=str,
            default="live",
            choices=["dev", "live"],
            help="Environment to use (dev or live)",
        )
        parser.add_argument(
            "--days",
            type=int,
            help="Only sync records modified in the last N days",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of records to process in each batch",
        )
        parser.add_argument(
            "--sku",
            type=str,
            help="Sync specific product by SKU",
        )
        parser.add_argument(
            "--skip-parents",
            action="store_true",
            help="Skip parent product synchronization",
        )
        parser.add_argument(
            "--skip-variants",
            action="store_true",
            help="Skip variant product synchronization",
        )
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="Update records even if not modified",
        )
        parser.add_argument(
            "--top",
            type=int,
            help="Only process the first N records",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output",
        )
        parser.add_argument(
            "--fail-on-filter-error",
            action="store_false",
            dest="fail_on_filter_error",
            default=True,
            help="Don't fail if date filter doesn't work (default: fail)",
        )
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear extractor cache before running",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)

        self.stdout.write(self.style.SUCCESS("Starting product sync process"))
        start_time = timezone.now()

        try:
            # Convert query_params to JSON string for filters argument
            filters_json = json.dumps(options) if options else None

            parent_sync_successful = True
            variant_sync_successful = True

            # Sync parent products if not skipped
            if not options["skip_parents"]:
                self.stdout.write(
                    self.style.NOTICE("\n=== Running Parent Product Sync via run_sync ===")
                )
                try:
                    call_command(
                        "run_sync",
                        entity_type="parent_product",
                        source="products_sync",
                        target="products.ParentProduct",
                        full=options["force_update"],
                        batch_size=options["batch_size"],
                        filters=filters_json,
                        debug=options["debug"],
                        fail_on_filter_error=options["fail_on_filter_error"],
                        clear_cache=options["clear_cache"],
                    )
                    self.stdout.write(self.style.SUCCESS("Parent product sync finished."))
                except Exception as e:
                    parent_sync_successful = False
                    self.stderr.write(self.style.ERROR(f"Parent product sync failed via run_sync: {e}"))

            # Sync variants if not skipped
            if not options["skip_variants"]:
                self.stdout.write(
                    self.style.NOTICE("\n=== Running Variant Product Sync via run_sync ===")
                )
                try:
                    call_command(
                        "run_sync",
                        entity_type="product_variant",
                        source="products_sync_variants",
                        target="products.VariantProduct",
                        full=options["force_update"],
                        batch_size=options["batch_size"],
                        filters=filters_json,
                        debug=options["debug"],
                        fail_on_filter_error=options["fail_on_filter_error"],
                        clear_cache=False if not options["skip_parents"] and options["clear_cache"] else options["clear_cache"],
                    )
                    self.stdout.write(self.style.SUCCESS("Variant product sync finished."))
                except Exception as e:
                    variant_sync_successful = False
                    self.stderr.write(self.style.ERROR(f"Variant product sync failed via run_sync: {e}"))

            # Print total duration
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nProduct sync command finished in: {duration:.2f} seconds"
                )
            )

            # Report overall status based on individual runs
            if parent_sync_successful and variant_sync_successful:
                self.stdout.write(self.style.SUCCESS("All product sync steps completed successfully."))
            else:
                raise CommandError("One or more product sync steps failed.")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"\nProduct sync command failed: {e}"))
            raise
