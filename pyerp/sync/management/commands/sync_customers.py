"""Management command to sync both customers and addresses from legacy ERP."""

import logging
# Re-add necessary imports
from pyerp.sync.pipeline import PipelineFactory
from django.core.management.base import CommandError # For mapping errors

# Remove unused imports
# from datetime import timedelta 
# from pathlib import Path
# from typing import Any, Dict, NamedTuple

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from django.apps import apps

# from pyerp.sync.pipeline import PipelineFactory
# from pyerp.sync.models import SyncMapping # Keep SyncMapping if get_mapping needs it, otherwise remove
# Actually, get_mapping is part of BaseSyncCommand, so SyncMapping is likely not needed here directly.
from pyerp.sync.models import SyncMapping # Keep SyncMapping for get_mapping
from .base_sync_command import BaseSyncCommand


logger = logging.getLogger(__name__)


class Command(BaseSyncCommand):
    """Django management command to sync customers and addresses."""

    help = "Sync customers and addresses from legacy ERP system"

    # Map specific filter arguments for this command
    filter_key_map = {
        'customer_number': 'KundenNr',
        # Add other specific mappings if needed
    }

    # Specify which arguments from options should be used for filtering
    filter_arg_keys = ['days', 'customer_number', 'top']

    def add_arguments(self, parser):
        """Add command line arguments."""
        # Add arguments from base class first
        super().add_arguments(parser)

        # Remove arguments handled by base class: --env, --days, --batch-size, --force-update, --debug
        # Add command-specific arguments
        parser.add_argument(
            "--customer-number",
            type=str,
            help="Sync specific customer by customer number (maps to KundenNr filter)",
        )
        parser.add_argument(
            "--skip-customers",
            action="store_true",
            help="Skip customer synchronization",
        )
        parser.add_argument(
            "--skip-addresses",
            action="store_true",
            help="Skip address synchronization",
        )
        # Note: --force-update is handled by the base command if needed via options passed to run_sync_via_command

    def handle(self, *args, **options):
        """Execute the command using direct pipeline execution."""
        self.stdout.write("Starting customer & address sync process")

        # Fetch mappings first
        customer_mapping = None
        address_mapping = None
        try:
            if not options["skip_customers"]:
                customer_mapping = self.get_mapping(entity_type="customer")
            if not options["skip_addresses"]:
                address_mapping = self.get_mapping(entity_type="address")
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Failed to get required sync mappings: {e}"))
            # Re-raise or exit if mappings are critical
            raise CommandError("Sync cannot proceed without required mappings.") from e

        # Build base query parameters (handles --top, --days, --filters JSON)
        # Use customer mapping (if exists) for config like timestamp field
        effective_mapping_for_base_params = customer_mapping if customer_mapping else address_mapping
        base_query_params = self.build_query_params(options, effective_mapping_for_base_params)

        # Add command-specific filters manually
        if options.get("customer_number"):
            filter_key = self.filter_key_map.get('customer_number', 'customer_number')
            if filter_key in base_query_params:
                self.stdout.write(self.style.WARNING(f"Filter key '{filter_key}' from --customer-number already exists in query params (e.g., from --filters). Overwriting."))
            base_query_params[filter_key] = options["customer_number"]
            self.stdout.write(f"Added specific filter from --customer-number: {filter_key}={options['customer_number']}")

        # --- Sync Customers (Direct Pipeline Execution) ---
        if not options["skip_customers"]:
            self.stdout.write("\nRunning customer sync pipeline...")
            try:
                customer_pipeline = PipelineFactory.create_pipeline(customer_mapping)
                fail_on_filter = options.get("fail_on_filter_error", True)

                if options.get("clear_cache"):
                    self.stdout.write("Clearing customer extractor cache...")
                    customer_pipeline.extractor.clear_cache()

                with customer_pipeline.extractor:
                    source_data = customer_pipeline.extractor.extract(
                        query_params=base_query_params,
                        fail_on_filter_error=fail_on_filter
                    )
                self.stdout.write(f"Extracted {len(source_data)} customer records")

                if source_data:
                    transformed_data = customer_pipeline.transformer.transform(source_data)
                    self.stdout.write(f"Transformed {len(transformed_data)} customer records")
                    load_result = customer_pipeline.loader.load(
                        transformed_data,
                        update_existing=options.get("force_update") or options.get("full"),
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Customer load finished: {load_result.created} created, "
                            f"{load_result.updated} updated, {load_result.skipped} skipped, "
                            f"{load_result.errors} errors."
                        )
                    )
                    if load_result.error_details:
                        self.stdout.write(self.style.WARNING("Customer Load Errors:"))
                        for err in load_result.error_details[:10]:
                            self.stdout.write(f"- {err}")
                        if len(load_result.error_details) > 10:
                            self.stdout.write(f"... and {len(load_result.error_details) - 10} more errors.")
                else:
                    self.stdout.write("No customer records extracted, skipping transform and load.")

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Customer sync pipeline failed: {e}"))
                if options.get("debug"):
                    import traceback
                    traceback.print_exc()
                # Consider stopping the whole command on failure

        # --- Sync Addresses (Direct Pipeline Execution) ---
        if not options["skip_addresses"]:
            self.stdout.write("\nRunning address sync pipeline...")
            try:
                address_pipeline = PipelineFactory.create_pipeline(address_mapping)
                fail_on_filter = options.get("fail_on_filter_error", True)

                # Clear cache only if customers were skipped and clear_cache is set
                if options.get("clear_cache") and options.get("skip_customers"):
                    self.stdout.write("Clearing address extractor cache (customers skipped)...")
                    address_pipeline.extractor.clear_cache()

                # Address query params - start with base, potentially adjust
                address_query_params = base_query_params.copy()
                # If --customer-number was used, the KundenNr filter is in address_query_params.
                # We assume the address extractor can either use it (if relevant) or ignore it.
                # No specific adjustment needed unless a problem is identified.
                self.stdout.write(f"Using query params for addresses: {address_query_params}")

                with address_pipeline.extractor:
                    source_data = address_pipeline.extractor.extract(
                        query_params=address_query_params,
                        fail_on_filter_error=fail_on_filter
                    )
                self.stdout.write(f"Extracted {len(source_data)} address records")

                if source_data:
                    transformed_data = address_pipeline.transformer.transform(source_data)
                    self.stdout.write(f"Transformed {len(transformed_data)} address records")
                    load_result = address_pipeline.loader.load(
                        transformed_data,
                        update_existing=options.get("force_update") or options.get("full"),
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Address load finished: {load_result.created} created, "
                            f"{load_result.updated} updated, {load_result.skipped} skipped, "
                            f"{load_result.errors} errors."
                        )
                    )
                    if load_result.error_details:
                        self.stdout.write(self.style.WARNING("Address Load Errors:"))
                        for err in load_result.error_details[:10]:
                            self.stdout.write(f"- {err}")
                        if len(load_result.error_details) > 10:
                            self.stdout.write(f"... and {len(load_result.error_details) - 10} more errors.")
                else:
                    self.stdout.write("No address records extracted, skipping transform and load.")

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Address sync pipeline failed: {e}"))
                if options.get("debug"):
                    import traceback
                    traceback.print_exc()

        self.stdout.write("\nCustomer & address sync process complete.")
