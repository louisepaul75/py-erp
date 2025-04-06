"""
Management command to synchronize production orders and items from legacy ERP.

This command allows syncing production orders (werksauftraege) and their line items 
(werksauftrpos) from the legacy ERP to the pyERP system. It supports filtering 
like --top to fetch N parent orders and then their corresponding items.
"""

# import time  # Keep for potential wait logic if reintroduced - Removed as not used
import traceback
# from typing import Any, Dict, List, Optional # Removed as not explicitly used

from django.core.management.base import BaseCommand, CommandError
# from django.db import transaction # Removed unused import
from django.utils import timezone
from pyerp.utils.logging import get_logger

# Import necessary components
from pyerp.sync.pipeline import PipelineFactory
from .base_sync_command import BaseSyncCommand

logger = get_logger(__name__)


class Command(BaseSyncCommand): # Inherit from BaseSyncCommand
    """
    Command to sync production orders (werksauftraege) and items (werksauftrpos).
    Handles parent/child relationship, respecting filters like --top.
    """

    help = "Synchronize production orders (werksauftraege) and items (werksauftrpos)"

    # Define legacy key field names (Assuming standard names)
    PARENT_ENTITY_TYPE = "production_orders"
    PARENT_LEGACY_KEY_FIELD = "AuftragsNr" # Key field in werksauftraege
    CHILD_ENTITY_TYPE = "production_order_items"
    CHILD_PARENT_LINK_FIELD = "AuftragsNr" # Field in werksauftrpos linking back

    def add_arguments(self, parser):
        """Add command arguments, inheriting from BaseSyncCommand."""
        super().add_arguments(parser) # Adds --full, --batch-size, --top, --filters, --debug, --days etc.

        # Add command-specific arguments
        parser.add_argument(
            "--orders-only",
            action="store_true",
            help="Only sync production orders, not order items",
        )
        parser.add_argument(
            "--items-only",
            action="store_true",
            help="Only sync production order items, not orders",
        )
        # Remove mold-related args for now, can be added back if needed
        # parser.add_argument(
        #     "--skip-molds",
        #     action="store_true",
        #     help="Skip syncing molds and mold products",
        # )
        # parser.add_argument(
        #     "--molds-only",
        #     action="store_true",
        #     help="Only sync molds and mold products",
        # )

    def handle(self, *args, **options):
        """Orchestrate the multi-stage production sync process."""
        command_start_time = timezone.now()
        self.debug = options.get("debug", False) # Set debug flag from base class arg
        log_prefix = f"[sync_production - {command_start_time.isoformat()}]"
        logger.info(
            f"{log_prefix} Starting production order & items sync orchestrator..."
        )
        self.stdout.write(
            f"{log_prefix} Starting production sync process at {command_start_time}"
        )

        # Determine parts to run
        run_orders = not options.get("items_only", False)
        run_items = not options.get("orders_only", False)

        # --- Fetch Mappings ---
        parent_mapping = None
        child_mapping = None
        try:
            if run_orders:
                parent_mapping = self.get_mapping(
                    entity_type=self.PARENT_ENTITY_TYPE
                )
            if run_items:
                # Fetch child mapping even if only running items, needed for context
                child_mapping = self.get_mapping(
                    entity_type=self.CHILD_ENTITY_TYPE
                )
            if run_orders and not parent_mapping:
                raise CommandError(f"Mapping not found for {self.PARENT_ENTITY_TYPE}")
            if run_items and not child_mapping:
                raise CommandError(f"Mapping not found for {self.CHILD_ENTITY_TYPE}")

        except CommandError as e:
            self.stderr.write(self.style.ERROR(
                f"{log_prefix} Failed to get required sync mappings: {e}"
            ))
            raise CommandError(
                "Sync cannot proceed without required mappings."
            ) from e

        # --- Build Initial Query Parameters ---
        # Use parent mapping for context if available, otherwise None
        initial_query_params = self.build_query_params(
            options, parent_mapping if parent_mapping else None
        )
        logger.info(
            f"{log_prefix} Initial query parameters built: {initial_query_params}"
        )

        # --- Step 1: Fetch Parent Record IDs (AuftragsNr) ---
        parent_record_ids = []
        if run_items: # Only need parent IDs if we are going to fetch children
            self.stdout.write(self.style.NOTICE(
                f"\n{log_prefix} === Step 1: Fetching parent record IDs "
                f"({self.PARENT_LEGACY_KEY_FIELD}) ===\n"
            ))
            logger.info(f"{log_prefix} Starting Step 1: Fetch Parent Record IDs")
            if not parent_mapping:
                # Should have been caught earlier, but double check
                raise CommandError("Cannot fetch parent IDs without parent mapping.")

            try:
                parent_pipeline_for_id_fetch = PipelineFactory.create_pipeline(
                    parent_mapping
                )
                id_fetch_params = {
                    **initial_query_params,
                    "select_fields": [self.PARENT_LEGACY_KEY_FIELD],
                }
                logger.info(
                    f"{log_prefix} Querying extractor for parent IDs with params: "
                    f"{id_fetch_params}"
                )

                # Clear cache if requested (only for this first extractor call)
                if options.get("clear_cache"):
                    self.stdout.write(
                        f"{log_prefix} Clearing parent ({self.PARENT_ENTITY_TYPE}) "
                        "extractor cache..."
                    )
                    parent_pipeline_for_id_fetch.extractor.clear_cache()

                with parent_pipeline_for_id_fetch.extractor:
                    fetched_data_for_ids = (
                        parent_pipeline_for_id_fetch.extractor.extract(
                            query_params=id_fetch_params,
                            fail_on_filter_error=options.get(
                                "fail_on_filter_error", True
                            )
                        )
                    )
                logger.info(
                    f"{log_prefix} Extractor returned {len(fetched_data_for_ids)} "
                    "potential parent records for ID extraction."
                )

                # Extract the unique parent key values
                parent_record_ids = list(
                    set(
                        str(record.get(self.PARENT_LEGACY_KEY_FIELD))
                        for record in fetched_data_for_ids
                        if record.get(self.PARENT_LEGACY_KEY_FIELD) is not None
                    )
                )
                self.stdout.write(
                    f"{log_prefix} Found {len(parent_record_ids)} unique parent "
                    f"record IDs ({self.PARENT_LEGACY_KEY_FIELD})."
                )
                logger.info(
                    f"{log_prefix} Step 1: Found {len(parent_record_ids)} unique "
                    "parent IDs."
                )
                if self.debug and parent_record_ids:
                    self.stdout.write(
                        f"{log_prefix} Sample Parent IDs: {parent_record_ids[:10]}..."
                    )

            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"{log_prefix} Step 1 Failed: Could not fetch parent record IDs "
                    f"({self.PARENT_LEGACY_KEY_FIELD}): {e}"
                ))
                logger.error(
                    f"{log_prefix} Step 1: Failed to fetch parent IDs: {e}",
                    exc_info=self.debug
                )
                if self.debug:
                    traceback.print_exc()
                # If we can't get IDs and need them for items, abort.
                raise CommandError(
                    "Could not fetch parent IDs, aborting sync. Error: {e}"
                )
        elif not run_orders and run_items:
            # Running items only, but need a way to filter them.
            # If --top or other filters applied, Step 1 runs. If no filters,
            # parent_record_ids remains empty.
            logger.warning(
                f"{log_prefix} Running items-only sync. Parent ID fetching "
                f"skipped unless filters like --top are applied."
            )

        # --- Step 2: Run Parent Sync (Production Orders) ---
        parent_sync_successful = True # Assume success unless an error occurs or skipped
        if run_orders:
            self.stdout.write(self.style.NOTICE(
                f"\n{log_prefix} === Step 2: Running Parent Sync "
                f"({self.PARENT_ENTITY_TYPE}) ===\n"
            ))
            logger.info(
                f"{log_prefix} Starting Step 2: {self.PARENT_ENTITY_TYPE} Sync"
            )
            if not parent_mapping:
                raise CommandError("Cannot sync parents without parent mapping.")

            try:
                parent_pipeline = PipelineFactory.create_pipeline(parent_mapping)

                self.stdout.write(
                    f"{log_prefix} Using query params for parent sync: "
                    f"{initial_query_params}"
                )
                # Clear cache here if only running parents and clear_cache is set
                if options.get("clear_cache") and not run_items:
                    self.stdout.write(
                        f"{log_prefix} Clearing parent ({self.PARENT_ENTITY_TYPE}) "
                        "extractor cache..."
                    )
                    parent_pipeline.extractor.clear_cache()

                with parent_pipeline.extractor:
                    parent_source_data = parent_pipeline.extractor.extract(
                        query_params=initial_query_params, # Use initial params
                        fail_on_filter_error=options.get(
                            "fail_on_filter_error", True
                        )
                    )
                self.stdout.write(
                    f"{log_prefix} Extracted {len(parent_source_data)} parent "
                    f"records ({self.PARENT_ENTITY_TYPE})."
                )

                if parent_source_data:
                    transformed_parent_data = (
                        parent_pipeline.transformer.transform(parent_source_data)
                    )
                    self.stdout.write(
                        f"{log_prefix} Transformed {len(transformed_parent_data)} "
                        "parent records."
                    )
                    load_result = parent_pipeline.loader.load(
                        transformed_parent_data,
                        update_existing=(
                            options.get("force_update") or options.get("full")
                        ),
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"{log_prefix} Parent ({self.PARENT_ENTITY_TYPE}) load finished: "
                        f"{load_result.created} created, "
                        f"{load_result.updated} updated, {load_result.skipped} skipped, "
                        f"{load_result.errors} errors.\\n" # Added newline for clarity
                    ))
                    self._log_load_errors(log_prefix, "Parent", load_result)
                else:
                    self.stdout.write(
                        f"{log_prefix} No parent records extracted, skipping "
                        "transform and load.\n" # Added newline
                    )

                # parent_sync_successful = True # Already initialized to True
                logger.info(
                    f"{log_prefix} Step 2: {self.PARENT_ENTITY_TYPE} Sync finished "
                    "successfully.\n" # Added newline
                )

            except Exception as e:
                parent_sync_successful = False # Set to False on error
                self.stderr.write(self.style.ERROR(
                    f"{log_prefix} Step 2 Failed: {self.PARENT_ENTITY_TYPE} sync "
                    f"pipeline error: {e}\n" # Added newline
                ))
                logger.error(
                    f"{log_prefix} Step 2: {self.PARENT_ENTITY_TYPE} Sync failed: {e}",
                    exc_info=self.debug
                )
                if self.debug:
                    traceback.print_exc()
                # Continue to item sync, logging the failure.

        # --- Step 3: Run Child Sync (Production Order Items) ---
        child_sync_successful = True # Assume success unless error or skipped
        if run_items:
            self.stdout.write(self.style.NOTICE(
                f"\n{log_prefix} === Step 3: Running Child Sync "
                f"({self.CHILD_ENTITY_TYPE}) ===\n"
            ))
            logger.info(
                f"{log_prefix} Starting Step 3: {self.CHILD_ENTITY_TYPE} Sync"
            )
            if not child_mapping:
                raise CommandError("Cannot sync children without child mapping.")

            if not parent_record_ids:
                # This happens if Step 1 failed or --items-only without filters
                message = (
                    f"Skipping child ({self.CHILD_ENTITY_TYPE}) sync as no parent "
                    f"IDs ({self.PARENT_LEGACY_KEY_FIELD}) were found/fetched.\n" # Added newline
                )
                self.stdout.write(self.style.WARNING(f"{log_prefix} {message}"))
                logger.warning(f"{log_prefix} Step 3: {message}")
                # child_sync_successful = True # Already initialized
            else:
                try:
                    child_pipeline = PipelineFactory.create_pipeline(child_mapping)
                    item_filters = {
                        "parent_record_ids": parent_record_ids,
                        "parent_field": self.CHILD_PARENT_LINK_FIELD
                    }
                    self.stdout.write(
                        f"{log_prefix} Filtering child sync using "
                        f"{len(parent_record_ids)} parent IDs "
                        f"({self.PARENT_LEGACY_KEY_FIELD}) from Step 1.\n" # Added newline
                    )
                    logger.info(
                        f"{log_prefix} Filtering child sync with item_filters: "
                        f"{item_filters}"
                    )

                    batch_size = options.get("batch_size", 100)

                    with child_pipeline.extractor:
                        child_source_data = child_pipeline.extractor.extract(
                            query_params=item_filters,
                            fail_on_filter_error=options.get(
                                "fail_on_filter_error", True
                            )
                        )
                    self.stdout.write(
                        f"{log_prefix} Extracted {len(child_source_data)} "
                        f"child records ({self.CHILD_ENTITY_TYPE}).\n" # Added newline
                    )

                    if child_source_data:
                        transformed_child_data = (
                            child_pipeline.transformer.transform(child_source_data)
                        )
                        self.stdout.write(
                            f"{log_prefix} Transformed {len(transformed_child_data)} "
                            "child records.\n" # Added newline
                        )
                        load_result = child_pipeline.loader.load(
                            transformed_child_data,
                            update_existing=(
                               options.get("force_update") or options.get("full")
                            ),
                            batch_size=batch_size
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f"{log_prefix} Child ({self.CHILD_ENTITY_TYPE}) load finished: "
                            f"{load_result.created} created, "
                            f"{load_result.updated} updated, {load_result.skipped} skipped, "
                            f"{load_result.errors} errors.\\n" # Added newline
                        ))
                        self._log_load_errors(log_prefix, "Child", load_result)
                    else:
                        self.stdout.write(
                            f"{log_prefix} No child records extracted, skipping "
                            "transform and load.\n" # Added newline
                        )

                    # child_sync_successful = True # Already initialized
                    logger.info(
                        f"{log_prefix} Step 3: {self.CHILD_ENTITY_TYPE} Sync finished "
                        "successfully.\n" # Added newline
                    )

                except Exception as e:
                    child_sync_successful = False # Set to False on error
                    self.stderr.write(self.style.ERROR(
                        f"{log_prefix} Step 3 Failed: {self.CHILD_ENTITY_TYPE} sync "
                        f"pipeline error: {e}\n" # Added newline
                    ))
                    logger.error(
                        f"{log_prefix} Step 3: {self.CHILD_ENTITY_TYPE} Sync failed: {e}",
                        exc_info=self.debug
                    )
                    if self.debug:
                        traceback.print_exc()

        # --- Step 4: Report Overall Status ---
        end_time = timezone.now()
        duration = (end_time - command_start_time).total_seconds()
        logger.info(
            f"{log_prefix} Orchestrator finished in {duration:.2f} seconds.\n" # Added newline
        )
        self.stdout.write(
            f"\n{log_prefix} Production sync command finished in "
            f"{duration:.2f} seconds\n" # Added newline
        )

        if parent_sync_successful and child_sync_successful:
            success_msg = (
                f"{log_prefix} All production sync steps completed successfully.\n" # Added newline
            )
            self.stdout.write(self.style.SUCCESS(success_msg))
            logger.info(success_msg)
        else:
            error_msg = (
                f"{log_prefix} One or more production sync steps failed. "
                "Check logs for details.\n" # Added newline
            )
            logger.error(error_msg)
            # Determine if the overall command should fail based on which step failed
            command_failed = False
            if not parent_sync_successful and run_orders:
                self.stdout.write(self.style.WARNING(
                    f"{log_prefix} Note: Parent sync (Step 2) encountered an error.\n" # Added newline
                ))
                command_failed = True # If required parent step fails, command fails
            if not child_sync_successful and run_items:
                 self.stdout.write(self.style.WARNING(
                    f"{log_prefix} Note: Child sync (Step 3) encountered an error.\n" # Added newline
                ))
                 # Fail if child sync was required (i.e., not --orders-only)
                 if not options.get("orders_only", False):
                     command_failed = True

            if command_failed:
                raise CommandError(error_msg)
            else:
                # Errors occurred in optional/skipped steps, issue a warning
                self.stdout.write(self.style.WARNING(error_msg))

    def _log_load_errors(self, log_prefix, step_name, load_result):
        """Helper to log loader errors."""
        if load_result.error_details:
            self.stdout.write(self.style.WARNING(
                f"{log_prefix} {step_name} Load Errors:"
            ))
            for i, err in enumerate(load_result.error_details):
                if i < 10:
                    self.stdout.write(f"- {err}")
                else:
                    self.stdout.write(
                        f"... and {len(load_result.error_details) - 10} more errors."
                    )
                    break
            logger.warning(f"{log_prefix} {step_name} Load encountered {load_result.errors} errors. First few: {load_result.error_details[:5]}")

# Removed old handle logic and imports
# ... (rest of the file if anything else existed)
# Ensure no old handle method remains 