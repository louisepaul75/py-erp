"""Management command to synchronize sales records from legacy ERP."""

import json
import os
from pathlib import Path
from datetime import timedelta
import time

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.utils import timezone

from pyerp.utils.logging import get_logger


logger = get_logger(__name__)


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
            "--limit",
            type=int,
            help="Limit the number of records to sync",
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
        self.stdout.write(f"Starting sales record sync process at {start_time}")

        # Build common options for run_sync
        run_sync_options = {
            "full": options["full"],
            "batch_size": options["batch_size"],
            "debug": self.debug,
            "fail_on_filter_error": options["fail_on_filter_error"],
            "clear_cache": options["clear_cache"],
        }

        # Build filters dictionary
        filters = {}
        if options["filters"]:
            try:
                filters.update(json.loads(options["filters"]))
            except json.JSONDecodeError:
                raise CommandError("Invalid JSON format for --filters option")

        if options["limit"]:
            filters["$top"] = options["limit"]

        if options["days"]:
            days = options["days"]
            modified_since = timezone.now() - timedelta(days=days)
            date_str = modified_since.strftime("%Y-%m-%d")
            # Assuming the pipeline understands this filter structure
            filters["modified_date"] = {"gt": date_str}
            self.stdout.write(f"Filtering records modified since {date_str} ({days} days ago)")
        elif not options["full"] and not filters.get("modified_date") and not filters.get("Datum"): # Default incremental filter
            # Add default date filter for incremental sync (last 5 years) if not specified
            five_years_ago = timezone.now() - timedelta(days=5 * 365)
            date_str = five_years_ago.strftime("%Y-%m-%d")
            filters["Datum"] = {"gt": date_str} # Use 'Datum' based on previous logic
            self.stdout.write(f"Adding default incremental filter: records from {date_str} (last 5 years)")
        run_sync_options["filters"] = json.dumps(filters) if filters else None

        records_sync_successful = True
        items_sync_successful = True

        # --- Sync Sales Records ---
        self.stdout.write(self.style.NOTICE("\n=== Running Sales Records Sync via run_sync ==="))
        try:
            call_command(
                "run_sync",
                entity_type="sales_records",
                **run_sync_options
            )
            self.stdout.write(self.style.SUCCESS("Sales records sync finished."))
        except Exception as e:
            records_sync_successful = False
            self.stderr.write(self.style.ERROR(f"Sales records sync failed via run_sync: {e}"))
            if self.debug:
                import traceback
                traceback.print_exc()

        # --- Sync Sales Record Items ---
        # Run items sync regardless of record sync success/failure, unless records failed badly?
        # The item pipeline should handle skipping items for non-existent records.
        self.stdout.write(self.style.NOTICE("\n=== Running Sales Record Items Sync via run_sync ==="))
        try:
            # Remove record-specific filters ($top, date) for items sync
            item_filters = {}
            if options["filters"]:
                try:
                    item_filters.update(json.loads(options["filters"]))
                except json.JSONDecodeError:
                    pass # Ignore filter errors here, handled above

            item_run_sync_options = run_sync_options.copy()
            item_run_sync_options["filters"] = json.dumps(item_filters) if item_filters else None
            # Ensure cache is not cleared again if records sync cleared it
            item_run_sync_options["clear_cache"] = False if options["clear_cache"] else False

            call_command(
                "run_sync",
                entity_type="sales_record_items",
                **item_run_sync_options
            )
            self.stdout.write(self.style.SUCCESS("Sales record items sync finished."))
        except Exception as e:
            items_sync_successful = False
            self.stderr.write(self.style.ERROR(f"Sales record items sync failed via run_sync: {e}"))
            if self.debug:
                import traceback
                traceback.print_exc()

        # Report overall status
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        self.stdout.write(f"\nSales record sync command finished in {duration:.2f} seconds")

        if records_sync_successful and items_sync_successful:
            self.stdout.write(self.style.SUCCESS("All sales record sync steps completed successfully."))
        else:
            raise CommandError("One or more sales record sync steps failed.")
