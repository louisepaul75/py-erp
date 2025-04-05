"""Management command to synchronize sales records from legacy ERP."""

import json
# import os # Unused
# from pathlib import Path # Unused
from datetime import timedelta
import time
import traceback # Added for debug printing

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.utils import timezone
# from django.apps import apps # Unused
# from django.db.utils import OperationalError # Unused

# Remove unused SalesRecord import
# from pyerp.business_modules.sales.models import SalesRecord
from pyerp.utils.logging import get_logger
# Use the correct logger instance
# Restore necessary imports for fetching IDs first
from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory
# from pyerp.sync.utils import get_sync_mapping # REMOVED - Incorrect location
# from pyerp.sync.models import get_sync_mapping # Function doesn't exist

# import logging # Unused
logger = get_logger(__name__)  # Use configured logger


class Command(BaseCommand):
    """Command to synchronize sales records from legacy ERP."""

    help = "Synchronize sales records from legacy ERP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store command start time for logging/tracking
        self.command_start_time = timezone.now()

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform a full sync instead of incremental",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of records to process in each batch",
        )
        parser.add_argument(
            "--top",
            type=int,
            help=(
                "Limit the number of records to sync by taking the top N "
                "most recent records (Note: Behavior depends on extractor "
                "implementation and usually requires a sort filter)"
            ),
        )
        parser.add_argument(
            "--filters",
            type=str,
            help='JSON string with additional filters (e.g., \'{"$filter": "startswith(Belegart,\\\'R\\\')"}\')',
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with additional logging",
        )
        parser.add_argument(
            "--days",
            type=int,
            help="Only sync records modified/created in the last N days (uses 'Datum' field)",
        )
        parser.add_argument(
            "--fail-on-filter-error",
            action="store_false", # Corrected action to store_false
            dest="fail_on_filter_error", # Keep dest name
            default=True,
            help="Don't fail if date filter doesn't work (default: fail)",
        )
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear extractor cache before running",
        )

    def handle(self, *args, **options):
        """Command handler orchestrating the sync process."""
        self.debug = options["debug"]
        log_prefix = f"[sync_sales_records - {self.command_start_time.isoformat()}]"
        logger.info(f"{log_prefix} Starting sales record sync orchestrator...")
        self.stdout.write(
            f"{log_prefix} Starting sales record sync process at {self.command_start_time}"
        )

        # Build base filters dictionary from command line options
        base_filters = {}
        raw_custom_filters = options["filters"]
        custom_filters_parsed = {}
        if raw_custom_filters:
            try:
                custom_filters_parsed = json.loads(raw_custom_filters)
                if not isinstance(custom_filters_parsed, dict):
                     # Handle case where user provides just a raw OData string
                     # Log a warning as this format isn't directly processed by extractor via this path
                     logger.warning(
                         f"{log_prefix} Received raw string for --filters. "
                         f"Only dictionary format (e.g., {{\"$top\": 10}}) is fully processed. "
                         f"Raw $filter strings are currently ignored by the extractor in this command."
                     )
                     # Reset parsed dict if it wasn't a dict initially
                     custom_filters_parsed = {}
                else:
                    # Check if the problematic $filter key is present
                    if "$filter" in custom_filters_parsed:
                        logger.warning(
                            f"{log_prefix} The '--filters' argument included an OData '$filter' key: "
                            f"'{custom_filters_parsed['$filter']}'. This key is currently ignored "
                            f"by the underlying LegacyAPIExtractor when passed via this command. "
                            f"Other keys like '$top' will still be processed."
                        )
                        # We don't remove it, just warn. The extractor will ignore it.

                    # Merge the parsed dictionary into base_filters
                    base_filters.update(custom_filters_parsed)
                    logger.info(f"{log_prefix} Parsed custom filters: {custom_filters_parsed}")

            except json.JSONDecodeError as e:
                logger.error(f"{log_prefix} Invalid JSON for --filters: {e}")
                raise CommandError(f"Invalid JSON format for --filters option: {e}")

        # --- $top Handling (Applies to both ID fetch and record sync) ---
        if options["top"]:
            # Add/overwrite $top from command line argument
            base_filters["$top"] = options["top"]
            self.stdout.write(
                f"{log_prefix} Applying $top filter: {options['top']} "
                "(Note: May not be strictly 'most recent' without $orderby)"
            )
            logger.info(f"{log_prefix} Applied $top filter: {options['top']}")

        # --- Date Filtering Logic (Applies to both ID fetch and record sync) ---
        date_filter_key = "Datum" # Legacy field name for date filtering
        date_filter_applied = False
        # Check if a date filter is already provided directly in custom filters
        if date_filter_key in base_filters:
             logger.info(f"{log_prefix} Custom date filter found for '{date_filter_key}' in --filters, skipping automatic date filter.")
             date_filter_applied = True # Consider it applied if present

        # Apply --days filter if not already filtered by date
        if not date_filter_applied and options["days"]:
            days = options["days"]
            modified_since = self.command_start_time - timedelta(days=days)
            # Use the format the extractor expects: { "operator": "value" }
            date_str = modified_since.strftime("%Y-%m-%d")
            base_filters[date_filter_key] = {"gte": date_str} # Use 'gte' for >=

            self.stdout.write(
                f"{log_prefix} Applying date filter: {date_filter_key} >= {date_str} ({days} days ago)"
            )
            # Format dict string separately for logging clarity
            date_filter_dict_str = f"{{'{date_filter_key}': {{'gte': '{date_str}'}}}}\""
            logger.info(f"{log_prefix} Applied --days filter: {date_filter_dict_str}")
            date_filter_applied = True

        # Apply default incremental filter if not --full and no other date filter applied
        elif not date_filter_applied and not options["full"]:
            default_days = 5 * 365 # Default to 5 years for incremental
            five_years_ago = self.command_start_time - timedelta(days=default_days)
            date_str = five_years_ago.strftime("%Y-%m-%d")
            base_filters[date_filter_key] = {"gte": date_str}

            self.stdout.write(
                f"{log_prefix} Applying default incremental date filter: {date_filter_key} >= {date_str} (last {default_days} days)"
            )
            # Format dict string separately for logging clarity
            date_filter_dict_str = f"{{'{date_filter_key}': {{'gte': '{date_str}'}}}}\""
            logger.info(f"{log_prefix} Applied default incremental filter: {date_filter_dict_str}")
            date_filter_applied = True

        # --- Step 1: Fetch Potential Parent Record IDs (AbsNr) using base filters ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 1: Fetching potential parent record IDs (AbsNr) ==="
        ))
        logger.info(f"{log_prefix} Starting Step 1: Fetch Parent Record IDs")
        parent_record_ids = []
        try:
            # Get the sync mapping for sales_records to access its extractor config
            record_mapping = SyncMapping.objects.get(entity_type="sales_records")
            if not record_mapping:
                logger.error(f"{log_prefix} Could not find SyncMapping for 'sales_records'.")
                raise CommandError("Could not find SyncMapping for 'sales_records'")

            # Create a temporary pipeline instance JUST for extraction
            # We use the mapping to ensure we get the correct extractor + config
            temp_pipeline = PipelineFactory.create_pipeline(record_mapping)
            logger.info(f"{log_prefix} Using extractor {type(temp_pipeline.extractor).__name__} for ID fetching.")

            # Prepare query parameters for fetching ONLY the IDs
            # We use the *base_filters* compiled from command options
            id_query_params = {
                "select_fields": ["AbsNr"],  # Legacy ID field name
                # Spread the compiled base filters (e.g., {"Datum": {...}, "$top": ...})
                # The extractor should handle these keys directly
                **base_filters
            }
            logger.info(f"{log_prefix} Querying extractor for parent IDs with params: {id_query_params}")

            # Use the extractor's fetch_data method directly
            # The extractor should handle applying the filters (like $filter, $top)
            fetched_data = temp_pipeline.fetch_data(query_params=id_query_params)
            logger.info(f"{log_prefix} Extractor returned {len(fetched_data)} potential parent records.")

            # Extract the unique AbsNr values (convert to string for consistency)
            parent_record_ids = list(
                set(
                    str(record.get('AbsNr')) # Ensure string conversion
                    for record in fetched_data
                    if record.get('AbsNr') is not None
                )
            )
            self.stdout.write(
                f"{log_prefix} Found {len(parent_record_ids)} unique potential parent record IDs (AbsNr)."
            )
            logger.info(f"{log_prefix} Step 1: Found {len(parent_record_ids)} unique potential parent IDs.")
            if self.debug and parent_record_ids:
                self.stdout.write(f"{log_prefix} Sample Potential IDs: {parent_record_ids[:10]}...")

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"{log_prefix} Failed to fetch potential parent record IDs: {e}")
            )
            logger.error(f"{log_prefix} Step 1: Failed to fetch parent IDs: {e}", exc_info=self.debug)
            if self.debug:
                traceback.print_exc()
            # If we can't get the IDs, we cannot proceed with item sync correctly. Abort.
            raise CommandError(f"Could not fetch parent IDs, aborting sync. Error: {e}")

        # --- Step 2: Run Full Sales Records Sync (using same base filters) ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 2: Running Sales Records Sync ==="
        ))
        logger.info(f"{log_prefix} Starting Step 2: Sales Records Sync")
        records_sync_successful = True
        try:
            # Build options for the run_sync command call
            record_run_sync_options = {
                "full": options["full"], # Pass through full sync flag
                "batch_size": options["batch_size"],
                "debug": self.debug,
                "fail_on_filter_error": options["fail_on_filter_error"],
                "clear_cache": options["clear_cache"],
                # Pass the original combined base_filters as a JSON string
                # The run_sync command will pass this dict to the extractor
                "filters": json.dumps(base_filters) if base_filters else None,
            }
            logger.info(f"{log_prefix} Calling run_sync for 'sales_records' with options: {record_run_sync_options}")
            call_command(
                "run_sync",
                entity_type="sales_records",
                **record_run_sync_options
            )
            self.stdout.write(
                self.style.SUCCESS(f"{log_prefix} Sales records sync finished.")
            )
            logger.info(f"{log_prefix} Step 2: Sales Records Sync finished successfully.")

        except Exception as e:
            records_sync_successful = False
            self.stderr.write(
                self.style.ERROR(f"{log_prefix} Sales records sync failed: {e}")
            )
            logger.error(f"{log_prefix} Step 2: Sales Records Sync failed: {e}", exc_info=self.debug)
            if self.debug:
                traceback.print_exc()
            # Decide whether to continue to item sync if records failed
            # We will continue based on the initially fetched IDs, but log the failure.

        # --- Step 3: Run Sales Record Items Sync (using ONLY initially fetched AbsNr) ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 3: Running Sales Record Items Sync ==="
        ))
        logger.info(f"{log_prefix} Starting Step 3: Sales Record Items Sync")
        items_sync_successful = True
        if not parent_record_ids:
            # This case happens if Step 1 found no matching parent IDs
            message = "Skipping item sync as no potential parent IDs were found matching initial filters."
            self.stdout.write(self.style.WARNING(f"{log_prefix} {message}"))
            logger.warning(f"{log_prefix} Step 3: {message}")
            items_sync_successful = True # Mark as successful (nothing to do)
        else:
            try:
                # Prepare filters for items: ONLY use the initially fetched parent IDs
                # using the specific key the extractor expects
                item_filters = {"parent_record_ids": parent_record_ids}
                self.stdout.write(
                    f"{log_prefix} Filtering item sync using {len(parent_record_ids)} "
                    "initially fetched potential parent AbsNr IDs."
                )
                logger.info(f"{log_prefix} Filtering item sync with {len(parent_record_ids)} parent_record_ids from Step 1.")

                item_run_sync_options = {
                    # Pass 'full' flag for consistency, though its effect might be limited for items
                    "full": options["full"],
                    "batch_size": options["batch_size"],
                    "debug": self.debug,
                    "fail_on_filter_error": options["fail_on_filter_error"],
                    # DO NOT clear cache again if records sync might have used/cleared it
                    "clear_cache": False,
                    # Pass ONLY the parent ID filter using the specific key
                    "filters": json.dumps(item_filters),
                }
                logger.info(f"{log_prefix} Calling run_sync for 'sales_record_items' with options: {item_run_sync_options}")

                call_command(
                    "run_sync",
                    entity_type="sales_record_items",
                    **item_run_sync_options
                )
                self.stdout.write(
                    self.style.SUCCESS(f"{log_prefix} Sales record items sync finished.")
                )
                logger.info(f"{log_prefix} Step 3: Sales Record Items Sync finished successfully.")

            except Exception as e:
                items_sync_successful = False
                self.stderr.write(
                    self.style.ERROR(f"{log_prefix} Sales record items sync failed: {e}")
                )
                logger.error(f"{log_prefix} Step 3: Sales Record Items Sync failed: {e}", exc_info=self.debug)
                if self.debug:
                    traceback.print_exc()

        # --- Step 4: Report Overall Status ---
        end_time = timezone.now()
        duration = (end_time - self.command_start_time).total_seconds()
        logger.info(f"{log_prefix} Orchestrator finished in {duration:.2f} seconds.")
        self.stdout.write(
            f"\n{log_prefix} Sales record sync command finished in {duration:.2f} seconds"
        )

        # Overall success depends on both the record sync *and* the item sync finishing without exceptions
        # Note: This doesn't guarantee correctness, just absence of raised exceptions in the calls.
        if records_sync_successful and items_sync_successful:
            success_msg = f"{log_prefix} All sales record sync steps completed without raising exceptions."
            self.stdout.write(self.style.SUCCESS(success_msg))
            logger.info(success_msg)
        else:
            error_msg = f"{log_prefix} One or more sales record sync steps failed. Check logs for details."
            logger.error(error_msg)
            # Raise CommandError only if the initial ID fetch failed or if item sync explicitly failed.
            # If only record sync failed but we proceeded, we report success with warnings in logs.
            if not parent_record_ids and not records_sync_successful: # Initial fetch failed case handled earlier
                 pass # Already raised
            elif not items_sync_successful:
                 raise CommandError(error_msg)
            else: # Only record sync failed, items might have run (or been skipped)
                 self.stdout.write(self.style.WARNING(f"{log_prefix} Note: Sales records sync (Step 2) encountered an error. Item sync proceeded based on initially fetched IDs."))
                 logger.warning(f"{log_prefix} Command finished, but Step 2 (Sales Records Sync) failed.")

