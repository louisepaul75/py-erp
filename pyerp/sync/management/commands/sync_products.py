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

        # Check if specific parent(s) are targeted via --sku or --top
        is_targeted_sync = options.get("sku") is not None or options.get("top") is not None
        parent_legacy_ids_to_sync = [] # Used for targeted variant sync

        # Determine if cache should be cleared (only on the first step)
        clear_cache_flag = options.get("clear_cache", False)
        clear_cache_for_parent = clear_cache_flag if run_parents else False
        # Clear for variants only if parents were skipped *and* clear flag is set
        clear_cache_for_variant = clear_cache_flag if not run_parents and run_variants else False

        try:
            # === Step 1: Handle Parent Products ===
            if run_parents:
                self.stdout.write(
                    self.style.NOTICE("\n=== Step 1: Processing Parent Products ===")
                )
                parent_mapping = self.get_mapping("parent_product")
                initial_parent_query_params = self.build_query_params(options, parent_mapping)

                if is_targeted_sync:
                    # Fetch targeted parent data directly first
                    self.stdout.write(self.style.NOTICE("Targeted sync (--sku or --top detected): Fetching parent data first..."))
                    try:
                        # Import necessary class
                        from pyerp.sync.pipeline import PipelineFactory

                        # Create pipeline just for fetching
                        temp_pipeline = PipelineFactory.create_pipeline(parent_mapping)
                        logger.info(f"Using extractor {type(temp_pipeline.extractor).__name__} for parent ID fetching.")

                        # Use extractor's fetch_data method
                        fetched_parent_data = temp_pipeline.fetch_data(
                            query_params=initial_parent_query_params,
                            fail_on_filter_error=options["fail_on_filter_error"]
                        )

                        if fetched_parent_data:
                            self.stdout.write(self.style.SUCCESS(f"Fetched {len(fetched_parent_data)} targeted parent record(s)."))
                            # Extract legacy_id (assuming it comes from '__KEY') for variant filtering
                            parent_legacy_ids_to_sync = [
                                str(p.get('__KEY')) for p in fetched_parent_data if p.get('__KEY')
                            ]
                            logger.info(f"Extracted parent legacy IDs for variant sync: {parent_legacy_ids_to_sync}")

                            # Now, process *only* these fetched parents
                            # Bypass run_sync and directly use pipeline components
                            try:
                                # We already created the temp_pipeline for fetching
                                transformer = temp_pipeline.transformer
                                loader = temp_pipeline.loader
                                batch_size = options.get("batch_size", 100)

                                self.stdout.write(self.style.NOTICE(
                                    f"Directly processing {len(fetched_parent_data)} fetched parent records..."
                                ))

                                # Re-use pipeline's batch processing logic if possible,
                                # otherwise implement similar logic here.
                                # Assuming _process_batch exists and works similarly:
                                created_count, updated_count, failure_count = \
                                    temp_pipeline._process_batch(fetched_parent_data)

                                total_processed = len(fetched_parent_data)
                                total_failed = failure_count

                                self.stdout.write(f"Processing finished: Processed={total_processed}, Created={created_count}, Updated={updated_count}, Failed={total_failed}")

                                if total_failed > 0:
                                    self.stderr.write(self.style.ERROR("Errors occurred during direct processing of fetched parents."))
                                    parent_sync_successful = False
                                else:
                                    parent_sync_successful = True

                            except AttributeError as ae:
                                self.stderr.write(self.style.ERROR(f"Error accessing pipeline components for direct processing: {ae}"))
                                parent_sync_successful = False
                            except Exception as direct_proc_error:
                                self.stderr.write(self.style.ERROR(f"Error during direct processing of fetched parents: {direct_proc_error}"))
                                parent_sync_successful = False

                        else:
                            self.stdout.write(self.style.WARNING("No parent records found matching --sku or --top filters."))
                            parent_sync_successful = True # Considered successful as there's nothing to sync

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Failed to fetch or sync targeted parent products: {e}"))
                        logger.error("Error during targeted parent fetch/sync", exc_info=True)
                        parent_sync_successful = False
                        # If parent fetch/sync fails in targeted mode, maybe skip variants?
                        run_variants = False # Don't attempt variant sync if parent step failed here
                else:
                    # Non-targeted sync: run sync normally for parents
                    parent_options = options.copy()
                    parent_options["clear_cache"] = clear_cache_for_parent
                    parent_sync_successful = self.run_sync_via_command(
                        entity_type="parent_product",
                        options=parent_options,
                        query_params=initial_parent_query_params # Use standard filters
                    )

                # Update overall status
                if not parent_sync_successful:
                     overall_success = False
                     self.stderr.write(self.style.ERROR("Parent product sync step failed."))
                else:
                     self.stdout.write(self.style.SUCCESS("Parent product processing finished."))
            else:
                self.stdout.write(self.style.NOTICE("\n=== Skipping Parent Product Sync ==="))

            # === Step 2: Handle Variant Products ===
            if run_variants:
                self.stdout.write(
                    self.style.NOTICE("\n=== Step 2: Processing Variant Products ===")
                )
                variant_mapping = self.get_mapping("product_variant")
                variant_query_params = {}
                variant_options = options.copy()
                variant_options["clear_cache"] = clear_cache_for_variant # Set cache flag for this step

                if is_targeted_sync:
                    if parent_legacy_ids_to_sync:
                        # Filter variants based on fetched parent legacy IDs
                        # Use the extractor's dedicated mechanism:
                        # parent_record_ids: List of IDs
                        # parent_field: Name of the field in the source data to filter on
                        variant_query_params = {
                            "parent_record_ids": parent_legacy_ids_to_sync,
                            "parent_field": "Familie_" # Source field linking variants to parents
                        }
                        self.stdout.write(f"Filtering variants for {len(parent_legacy_ids_to_sync)} specific parent(s) using field 'Familie_'.")
                        logger.info(f"Running variant sync with filter: {variant_query_params}")
                    else:
                        # If targeted sync ran but found no parents, skip variant sync
                        self.stdout.write(self.style.WARNING("Skipping variant sync as no target parents were found or synced."))
                        variant_sync_successful = True # Skip is not failure
                else:
                    # Non-targeted sync: Build standard filters for variants
                    variant_query_params = self.build_query_params(options, variant_mapping)
                    self.stdout.write("Running variant sync with standard filters (e.g., --days).")

                # Only run if we have params (either standard or parent-derived)
                if variant_query_params is not None and variant_sync_successful:
                    # Clear potentially conflicting base filters if using parent ID filter
                    if is_targeted_sync and parent_legacy_ids_to_sync:
                        variant_options["top"] = None # Don't apply original --top to variants
                        variant_options["days"] = None # Don't apply original --days to variants
                        # Sku might be relevant if it was a variant SKU, but safer to clear
                        variant_options["sku"] = None
                        # We keep --debug, --batch-size etc.

                    variant_sync_successful = self.run_sync_via_command(
                        entity_type="product_variant",
                        options=variant_options,
                        query_params=variant_query_params
                    )

                # Update overall status
                if not variant_sync_successful:
                     overall_success = False
                     self.stderr.write(self.style.ERROR("Variant product sync step failed."))
                else:
                     # Check if we actually ran or skipped
                     if variant_query_params is not None:
                         self.stdout.write(self.style.SUCCESS("Variant product sync finished."))
            else:
                self.stdout.write(self.style.NOTICE("\n=== Skipping Variant Product Sync ==="))

            # === Step 3: Final Report ===
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
