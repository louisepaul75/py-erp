"""Management command to synchronize sales records from legacy ERP."""

import json
# import os # Unused
# from pathlib import Path # Unused
from datetime import timedelta
import time

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.utils import timezone
# from django.apps import apps # Unused
# from django.db.utils import OperationalError # Unused

from pyerp.utils.logging import get_logger
# Use the correct logger instance
from pyerp.sync.models import SyncMapping  # Import the model
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
        self.start_time = time.time()

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
                "implementation)"
            ),
        )
        parser.add_argument(
            "--filters",
            type=str,
            help="JSON string with additional filters to apply",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with additional logging",
        )
        parser.add_argument(
            "--days",
            type=int,
            help="Only sync records modified in the last N days",
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
        """Command handler."""
        self.debug = options["debug"]
        start_time = timezone.now()
        self.stdout.write(
            f"Starting sales record sync process at {start_time}"
        )

        # Build filters dictionary from command line options
        filters = {}
        if options["filters"]:
            try:
                filters.update(json.loads(options["filters"]))
            except json.JSONDecodeError:
                raise CommandError("Invalid JSON format for --filters option")

        if options["top"]:
            # Note: OData $top might behave differently than intended here.
            # It limits the total records returned, not necessarily the *most
            # recent*. A date sort might be needed in the extractor config if
            # strict recency is required.
            filters["$top"] = options["top"]
            self.stdout.write(
                f"Applying $top filter: {options['top']} "
                "(Note: May not be strictly 'most recent')"
            )

        # Handle date filtering ('Datum' seems to be the legacy date field)
        # date_filter_added = False # Unused variable
        if options["days"]:
            days = options["days"]
            modified_since = timezone.now() - timedelta(days=days)
            date_str = modified_since.strftime("%Y-%m-%d")
            filters["Datum"] = {"gt": date_str}
            # date_filter_added = True
            self.stdout.write(
                f"Applying Datum filter: > {date_str} ({days} days ago)"
            )
        elif (
            not options["full"]
            and not filters.get("modified_date")  # Check both potential fields
            and not filters.get("Datum")
        ):  # Default incremental filter for 'Datum'
            # Use Datum based on config and previous logic
            default_days = 5 * 365
            five_years_ago = timezone.now() - timedelta(days=default_days)
            date_str = five_years_ago.strftime("%Y-%m-%d")
            filters["Datum"] = {"gt": date_str}
            # date_filter_added = True
            self.stdout.write(
                f"Applying default incremental Datum filter: > {date_str} "
                "(last 5 years)"
            )

        # --- Step 1: Fetch Parent Record IDs (AbsNr) using all filters ---
        self.stdout.write(self.style.NOTICE(
            "\n=== Step 1: Fetching parent record IDs (AbsNr) ==="
        ))
        parent_record_ids = []
        try:
            # Get the sync mapping for sales_records
            # record_mapping = get_sync_mapping(entity_type="sales_records")
            # Use direct model query
            record_mapping = SyncMapping.objects.get(
                entity_type="sales_records"
            )
            if not record_mapping:
                raise CommandError(
                    "Could not find SyncMapping for 'sales_records'"
                )

            # Create a temporary pipeline just for extraction
            temp_pipeline = PipelineFactory.create_pipeline(record_mapping)

            # Use the extractor's fetch_data method directly
            # We only need the AbsNr field
            query_params = {
                "select_fields": ["AbsNr"]  # Only fetch the ID
            }
            # Add filters directly to query_params if they exist
            # The extractor will handle keys like 'Datum', '$top', etc.
            if filters:
                query_params.update(filters)

            fetched_data = temp_pipeline.fetch_data(query_params=query_params)

            # Extract the unique AbsNr values
            parent_record_ids = list(
                set(
                    record.get('AbsNr')
                    for record in fetched_data
                    if record.get('AbsNr') is not None
                )
            )
            self.stdout.write(
                f"Found {len(parent_record_ids)} unique parent record IDs "
                "(AbsNr)"
            )
            if self.debug and parent_record_ids:
                self.stdout.write(f"Sample IDs: {parent_record_ids[:10]}...")

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to fetch parent record IDs: {e}")
            )
            if self.debug:
                import traceback
                traceback.print_exc()
            raise CommandError("Could not fetch parent IDs, aborting sync.")

        if not parent_record_ids:
            self.stdout.write(self.style.WARNING(
                "No parent record IDs found matching filters. "
                "Skipping item sync."
            ))
            # We still run the record sync in case it needs to perform other
            # actions or if the filter logic there differs slightly.

        # --- Step 2: Run Full Sales Records Sync (using original filters) ---
        self.stdout.write(self.style.NOTICE(
            "\n=== Step 2: Running Sales Records Sync ==="
        ))
        records_sync_successful = True
        try:
            # Build options for the record sync command call
            record_run_sync_options = {
                "full": options["full"],
                "batch_size": options["batch_size"],
                "debug": self.debug,
                "fail_on_filter_error": options["fail_on_filter_error"],
                "clear_cache": options["clear_cache"],
                # Pass the original, combined filters
                "filters": json.dumps(filters) if filters else None,
            }
            call_command(
                "run_sync",
                entity_type="sales_records",
                **record_run_sync_options
            )
            self.stdout.write(
                self.style.SUCCESS("Sales records sync finished.")
            )
        except Exception as e:
            records_sync_successful = False
            self.stderr.write(
                self.style.ERROR(f"Sales records sync failed: {e}")
            )
            if self.debug:
                import traceback
                traceback.print_exc()
            # Decide whether to continue to item sync if records failed
            # For now, we continue, but log the failure.

        # --- Step 3: Run Sales Record Items Sync (using ONLY fetched AbsNr) ---
        self.stdout.write(self.style.NOTICE(
            "\n=== Step 3: Running Sales Record Items Sync ==="
        ))
        items_sync_successful = True
        if not parent_record_ids:
            self.stdout.write(self.style.WARNING(
                "Skipping item sync as no parent IDs were found."
            ))
            items_sync_successful = True  # Mark as successful (nothing to do)
        else:
            try:
                # Prepare filters for items: ONLY use the parent IDs
                item_filters = {"parent_record_ids": parent_record_ids}
                self.stdout.write(
                    f"Filtering item sync using {len(parent_record_ids)} "
                    "fetched AbsNr IDs."
                )

                item_run_sync_options = {
                    "full": options["full"],
                    "batch_size": options["batch_size"],
                    "debug": self.debug,
                    "fail_on_filter_error": options["fail_on_filter_error"],
                    # Crucially, DO NOT clear cache again if records sync
                    # cleared it
                    "clear_cache": False,
                    # Pass ONLY the parent ID filter
                    "filters": json.dumps(item_filters),
                }

                call_command(
                    "run_sync",
                    entity_type="sales_record_items",
                    **item_run_sync_options
                )
                self.stdout.write(
                    self.style.SUCCESS("Sales record items sync finished.")
                )
            except Exception as e:
                items_sync_successful = False
                self.stderr.write(
                    self.style.ERROR(f"Sales record items sync failed: {e}")
                )
                if self.debug:
                    import traceback
                    traceback.print_exc()

        # --- Step 4: Report Overall Status ---
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        self.stdout.write(
            f"\nSales record sync command finished in {duration:.2f} seconds"
        )

        if records_sync_successful and items_sync_successful:
            self.stdout.write(self.style.SUCCESS(
                "All sales record sync steps completed successfully."
            ))
        else:
            raise CommandError("One or more sales record sync steps failed.")

