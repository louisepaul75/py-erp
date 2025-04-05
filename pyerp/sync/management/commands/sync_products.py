"""Sync parent and variant products from legacy ERP."""

import logging
# import yaml # Unused
# from datetime import timedelta # Unused, moved to base
# from pathlib import Path # Unused
# from typing import Any, Dict, NamedTuple, List, Optional # Unused
# import os # Unused
# import json # Moved to base

from django.core.management import CommandError # Keep CommandError
# from django.core.management import call_command # Used via helper
# from django.core.management.base import BaseCommand # Use BaseSyncCommand
from django.utils import timezone

# from pyerp.sync.models import SyncMapping # Used via helper
# from pyerp.sync.pipeline import PipelineFactory # Not directly used

# Import the base command
from .base_sync_command import BaseSyncCommand

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


# class LoadResult(NamedTuple): # Not used anymore
#     """Result of a load operation."""
#     created: int
#     updated: int
#     skipped: int
#     errors: int
#     error_details: list


# Inherit from BaseSyncCommand
class Command(BaseSyncCommand):
    """Django management command to sync parent and variant products."""

    help = "Sync parent and variant products from legacy ERP system"

    def add_arguments(self, parser):
        """Add command line arguments specific to product sync."""
        # Call super to add common arguments
        super().add_arguments(parser)

        # Remove common arguments already defined in BaseSyncCommand:
        # --days, --batch-size, --top, --debug, --fail-on-filter-error, --clear-cache, --force-update

        # Add product-specific arguments
        parser.add_argument(
            "--sku",
            type=str,
            help="Sync specific product by SKU (passed via --filters if extractor supports it).",
            # Note: This needs to be handled in build_query_params or passed via --filters
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
        # Remove --env, as it seems unused/handled differently now
        # parser.add_argument(
        #     "--env",
        #     type=str,
        #     default="live",
        #     choices=["dev", "live"],
        #     help="Environment to use (dev or live)",
        # )

    # Override build_query_params if SKU needs special handling
    def build_query_params(self, options, mapping=None):
        """Build query params, adding SKU filter if provided."""
        query_params = super().build_query_params(options, mapping)

        if options.get("sku"):
            # Add SKU filter - Assumes extractor knows how to handle "sku"
            # If extractor expects a different format (e.g., OData), adjust here
            # or require it to be passed via --filters JSON.
            sku_value = options["sku"]
            if "sku" in query_params:
                 logger.warning(f"SKU filter provided via --sku ('{sku_value}') and also found in --filters. Prioritizing --sku.")
            query_params["sku"] = sku_value
            logger.info(f"Adding SKU filter: {sku_value}")

        return query_params


    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging based on debug flag
        if options["debug"]:
            logger.setLevel(logging.DEBUG)
            # Ensure console handler level is also debug if logger is
            console_handler.setLevel(logging.DEBUG)

        self.stdout.write(self.style.SUCCESS("Starting product sync process"))
        start_time = timezone.now()

        # Overall status tracking
        overall_success = True
        parent_sync_successful = True
        variant_sync_successful = True

        # Determine which steps to run
        run_parents = not options.get("skip_parents", False)
        run_variants = not options.get("skip_variants", False)

        # Determine if cache should be cleared (only on the first step)
        clear_cache_flag = options.get("clear_cache", False)
        clear_cache_for_parent = clear_cache_flag if run_parents else False
        # Clear for variants only if parents were skipped *and* clear flag is set
        clear_cache_for_variant = clear_cache_flag if not run_parents and run_variants else False

        try:
            # Sync parent products if not skipped
            if run_parents:
                self.stdout.write(
                    self.style.NOTICE("\n=== Running Parent Product Sync ===")
                )
                # Get mapping for parents
                parent_mapping = self.get_mapping("parent_product") # Use helper
                # Build query params using base logic + SKU override
                parent_query_params = self.build_query_params(options, parent_mapping)
                # Update options for this specific call
                parent_options = options.copy()
                parent_options["clear_cache"] = clear_cache_for_parent
                # Call run_sync via helper
                parent_sync_successful = self.run_sync_via_command(
                    entity_type="parent_product",
                    options=parent_options,
                    query_params=parent_query_params
                )
                if not parent_sync_successful:
                     overall_success = False # Mark overall failure
                     self.stderr.write(self.style.ERROR("Parent product sync step failed."))
                else:
                     self.stdout.write(self.style.SUCCESS("Parent product sync finished."))
            else:
                self.stdout.write(self.style.NOTICE("\n=== Skipping Parent Product Sync ==="))

            # Sync variants if not skipped
            if run_variants:
                self.stdout.write(
                    self.style.NOTICE("\n=== Running Variant Product Sync ===")
                )
                 # Get mapping for variants
                variant_mapping = self.get_mapping("product_variant") # Use helper
                # Build query params using base logic + SKU override
                variant_query_params = self.build_query_params(options, variant_mapping)
                # Update options for this specific call
                variant_options = options.copy()
                variant_options["clear_cache"] = clear_cache_for_variant
                # Call run_sync via helper
                variant_sync_successful = self.run_sync_via_command(
                    entity_type="product_variant",
                    options=variant_options,
                    query_params=variant_query_params
                )
                if not variant_sync_successful:
                     overall_success = False # Mark overall failure
                     self.stderr.write(self.style.ERROR("Variant product sync step failed."))
                else:
                     self.stdout.write(self.style.SUCCESS("Variant product sync finished."))
            else:
                self.stdout.write(self.style.NOTICE("\n=== Skipping Variant Product Sync ==="))

            # Print total duration
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nProduct sync command finished in: {duration:.2f} seconds"
                )
            )

            # Report overall status based on individual runs
            if overall_success:
                self.stdout.write(self.style.SUCCESS("All executed product sync steps completed successfully."))
            else:
                # Raise CommandError to ensure non-zero exit code for scripts
                raise CommandError("One or more product sync steps failed. Check logs for details.")

        except CommandError as e:
            # Catch CommandErrors raised by get_mapping or run_sync_via_command
            self.stderr.write(self.style.ERROR(f"\nProduct sync command failed: {e}"))
            raise # Re-raise CommandError to ensure correct exit code
        except Exception as e:
            # Catch any other unexpected errors
            self.stderr.write(self.style.ERROR(f"\nAn unexpected error occurred during product sync: {e}"))
            # Log traceback if debug is enabled
            if options.get("debug"):
                import traceback
                traceback.print_exc()
            # Raise CommandError for unexpected errors too
            raise CommandError(f"Unexpected error during product sync: {e}") from e
