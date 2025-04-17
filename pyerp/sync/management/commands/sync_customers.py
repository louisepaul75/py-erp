"""Management command to sync both customers and addresses from legacy ERP."""

import logging
import contextlib # Import needed for context management
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
# from pyerp.sync.models import SyncMapping # Keep SyncMapping for get_mapping - Unused
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
        """Execute the command using a unified, batched pipeline execution."""
        self.stdout.write("Starting customer & address sync process (batched)")

        # --- Get Mappings ---
        customer_mapping = None
        address_mapping = None
        try:
            if not options.get("skip_customers"):
                customer_mapping = self.get_mapping(entity_type="customer")
            if not options.get("skip_addresses"):
                address_mapping = self.get_mapping(entity_type="address")
        except CommandError as e:
            raise CommandError(f"Failed to get required sync mappings: {e}") from e

        # Check if we can proceed with customers
        if options.get("skip_customers") or not customer_mapping:
            self.stdout.write("Customer sync skipped (by option or missing mapping).")
            # If skipping customers, we implicitly skip addresses derived from them
            return

        # Determine if address sync is enabled
        sync_addresses_enabled = not options.get("skip_addresses") and address_mapping
        if not sync_addresses_enabled:
             self.stdout.write("Address sync will be skipped (by option or missing mapping).")

        # --- Initialize Pipelines ---
        try:
            customer_pipeline = PipelineFactory.create_pipeline(customer_mapping)
            address_pipeline = None
            if sync_addresses_enabled:
                address_pipeline = PipelineFactory.create_pipeline(address_mapping)
        except Exception as e:
            raise CommandError(f"Failed to initialize pipelines: {e}") from e

        # --- Build Initial Customer Query Params ---
        # Remove batch_size from params passed to extractor, handle separately
        batch_size = options.pop("batch_size", 100) # Use provided or default
        customer_query_params = self.build_query_params(options, customer_mapping)
        self.stdout.write(f"Initial query params for customers (excluding pagination): {customer_query_params}")
        self.stdout.write(f"Using batch size: {batch_size}")


        # Clear cache if requested
        if options.get("clear_cache"):
            self.stdout.write("Clearing extractor caches...")
            try:
                # Use classmethod to clear cache without needing an instance context
                if hasattr(customer_pipeline.extractor, 'clear_cache'):
                     customer_pipeline.extractor.__class__.clear_cache()
                if address_pipeline and hasattr(address_pipeline.extractor, 'clear_cache'):
                     address_pipeline.extractor.__class__.clear_cache()
            except Exception as cache_err:
                self.stderr.write(self.style.WARNING(f"Could not clear cache: {cache_err}"))

        # --- Batch Processing Loop ---
        batch_num = 0
        total_customers_processed = 0
        total_customers_created = 0
        total_customers_updated = 0
        total_customers_skipped = 0
        total_customers_errors = 0
        total_addresses_processed = 0
        total_addresses_created = 0
        total_addresses_updated = 0
        total_addresses_skipped = 0
        total_addresses_errors = 0
        overall_success = True

        try:
            # Get extractor instances
            customer_extractor = customer_pipeline.extractor
            address_extractor = address_pipeline.extractor if address_pipeline else None

            # Use context managers for connection handling within the loop
            with customer_extractor, (address_extractor or contextlib.nullcontext()) as managed_addr_extractor:

                # Iterate through customer batches using the new generator method
                for customer_batch in customer_extractor.extract_batched(
                    query_params=customer_query_params,
                    batch_size=batch_size,
                    # fail_on_filter_error is not directly applicable here as errors are raised
                ):
                    batch_num += 1
                    self.stdout.write(f"\n--- Processing Customer Batch {batch_num} ({len(customer_batch)} records) ---")

                    if not customer_batch:
                        # Should theoretically not happen if extractor handles empty lists correctly, but good safety check
                        self.stdout.write("Empty customer batch received, skipping.")
                        continue

                    batch_address_ids_to_fetch = []
                    batch_customers_succeeded = False
                    try:
                        # --- Process Customer Batch ---
                        # Collect AdrNr BEFORE transforming, in case transform fails partially
                        # Ensure AdrNr exists and is not None/empty
                        raw_address_ids = [
                            d.get('AdrNr') for d in customer_batch
                            if d.get('AdrNr') is not None and str(d.get('AdrNr')).strip() != ''
                        ]
                        # Ensure IDs are suitable for filtering (e.g., convert to int if needed)
                        # Assuming AdrNr are integers or strings that can be used directly in filters
                        batch_address_ids_to_fetch = list(set(filter(None, raw_address_ids)))

                        self.stdout.write(f"Collected {len(batch_address_ids_to_fetch)} unique, valid legacy address numbers for this batch.")

                        transformed_customers = customer_pipeline.transformer.transform(customer_batch)
                        self.stdout.write(f"Transformed {len(transformed_customers)} customer records for batch {batch_num}")

                        if transformed_customers:
                            load_result_cust = customer_pipeline.loader.load(
                                transformed_customers,
                                update_existing=options.get("force_update") or options.get("full"),
                            )
                            self.stdout.write(
                                f"Customer Batch {batch_num} Load Result: "
                                f"{load_result_cust.created} created, {load_result_cust.updated} updated, "
                                f"{load_result_cust.skipped} skipped, {load_result_cust.errors} errors."
                            )
                            total_customers_processed += len(transformed_customers) # Use count passed to loader
                            total_customers_created += load_result_cust.created
                            total_customers_updated += load_result_cust.updated
                            total_customers_skipped += load_result_cust.skipped
                            total_customers_errors += load_result_cust.errors
                            if load_result_cust.errors > 0:
                                overall_success = False
                                batch_customers_succeeded = False # Mark batch as problematic
                                self.stderr.write(self.style.ERROR(f"Errors occurred loading customer batch {batch_num}."))
                                for i, err in enumerate(load_result_cust.error_details):
                                     if i < 5: # Log first 5 errors
                                        self.stderr.write(f"  - {err}")
                                     elif i == 5:
                                        self.stderr.write(f"  ... ({len(load_result_cust.error_details) - 5} more errors)")
                                        break
                            else:
                                batch_customers_succeeded = True # Mark batch as successful
                        else:
                            self.stdout.write(f"No transformable customer records found in batch {batch_num}.")
                            # Treat as success for the customer part if no errors, allows addresses to proceed
                            batch_customers_succeeded = True

                    except Exception as cust_batch_err:
                        overall_success = False
                        batch_customers_succeeded = False
                        total_customers_errors += len(customer_batch) # Count all in batch as errors
                        self.stderr.write(self.style.ERROR(f"Critical error processing customer batch {batch_num}: {cust_batch_err}"))
                        logger.error(f"Customer batch {batch_num} failed critically", exc_info=True)
                        # Prevent address processing for this critically failed batch
                        batch_address_ids_to_fetch = []

                    # --- Process Address Batch (if customers were processed ok and addresses enabled/needed) ---
                    if sync_addresses_enabled and batch_customers_succeeded and batch_address_ids_to_fetch:
                        self.stdout.write(f"--- Processing Addresses for Customer Batch {batch_num} ---")
                        try:
                             # Ensure address_extractor is available (it should be if sync_addresses_enabled is True)
                            if managed_addr_extractor is None:
                                 raise CommandError("Address extractor is unexpectedly None.")

                            # Build filter based on collected AdrNr for this batch
                            # Handle potentially large number of IDs - the extractor/API must support 'OR' style filtering
                            address_filter_list = [["AdrNr", "=", adr_id] for adr_id in batch_address_ids_to_fetch]
                            # Check if the filter list is too large, potentially split into chunks if needed
                            # For now, assume the API handles the list size.
                            address_query_params = {"filter_query": address_filter_list}
                            self.stdout.write(f"Querying {len(batch_address_ids_to_fetch)} specific addresses for batch {batch_num}.")

                            # Extract addresses using the regular extract method, filtered by IDs
                            # No batching needed here as we fetch specific IDs
                            address_batch = managed_addr_extractor.extract(
                                query_params=address_query_params,
                                fail_on_filter_error=True # Fail if address extraction itself errors
                            )
                            self.stdout.write(f"Extracted {len(address_batch)} address records for batch {batch_num}.")

                            if address_batch:
                                transformed_addresses = address_pipeline.transformer.transform(address_batch)
                                self.stdout.write(f"Transformed {len(transformed_addresses)} address records for batch {batch_num}")

                                if transformed_addresses:
                                    load_result_addr = address_pipeline.loader.load(
                                        transformed_addresses,
                                        update_existing=options.get("force_update") or options.get("full"),
                                    )
                                    self.stdout.write(
                                        f"Address Batch {batch_num} Load Result: "
                                        f"{load_result_addr.created} created, {load_result_addr.updated} updated, "
                                        f"{load_result_addr.skipped} skipped, {load_result_addr.errors} errors."
                                    )
                                    total_addresses_processed += len(transformed_addresses) # Use count passed to loader
                                    total_addresses_created += load_result_addr.created
                                    total_addresses_updated += load_result_addr.updated
                                    total_addresses_skipped += load_result_addr.skipped
                                    total_addresses_errors += load_result_addr.errors
                                    if load_result_addr.errors > 0:
                                        overall_success = False
                                        self.stderr.write(self.style.ERROR(f"Errors occurred loading address batch {batch_num}."))
                                        # Log first few errors
                                        for i, err in enumerate(load_result_addr.error_details):
                                            if i < 5:
                                                self.stderr.write(f"  - {err}")
                                            elif i == 5:
                                                self.stderr.write(f"  ... ({len(load_result_addr.error_details) - 5} more errors)")
                                                break
                                else:
                                    self.stdout.write(f"No transformable address records found in batch {batch_num}.")
                            else:
                                self.stdout.write(f"No address records extracted for batch {batch_num} (expected {len(batch_address_ids_to_fetch)}).")

                        except Exception as addr_batch_err:
                            overall_success = False
                            total_addresses_errors += len(batch_address_ids_to_fetch) # Estimate errors
                            self.stderr.write(self.style.ERROR(f"Critical error processing address batch {batch_num}: {addr_batch_err}"))
                            logger.error(f"Address batch {batch_num} failed critically", exc_info=True)

                    elif sync_addresses_enabled and not batch_address_ids_to_fetch:
                         self.stdout.write(f"No valid address IDs collected from customer batch {batch_num}, skipping address fetch.")
                    elif sync_addresses_enabled and not batch_customers_succeeded:
                         self.stdout.write(f"Skipping address processing for batch {batch_num} due to customer processing errors.")

                    # End of loop for one batch

        except Exception as e:
            # Catch errors during the setup or the main batch loop iteration itself
            overall_success = False
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred during the sync process: {e}"))
            logger.error("Sync failed during main batch processing loop", exc_info=True)
            # We might be in the middle of processing, stats might be incomplete.
            # Re-raise as CommandError to signal failure clearly.
            raise CommandError(f"Sync aborted due to unexpected error: {e}") from e

        # --- Final Summary ---
        self.stdout.write("\n" + "="*20 + " Sync Summary " + "="*20)
        self.stdout.write(f"Processed {batch_num} customer batches.")
        self.stdout.write(
            f"Customers Totals: Processed={total_customers_processed}, Created={total_customers_created}, "
            f"Updated={total_customers_updated}, Skipped={total_customers_skipped}, Errors={total_customers_errors}"
        )
        if sync_addresses_enabled:
            self.stdout.write(
                f"Addresses Totals: Processed={total_addresses_processed}, Created={total_addresses_created}, "
                f"Updated={total_addresses_updated}, Skipped={total_addresses_skipped}, Errors={total_addresses_errors}"
            )
        else:
            self.stdout.write("Address sync was disabled or skipped.")
        self.stdout.write("="*54)


        if not overall_success or total_customers_errors > 0 or total_addresses_errors > 0:
            raise CommandError(f"Sync process completed with errors. Customers: {total_customers_errors} errors. Addresses: {total_addresses_errors} errors.")
        else:
            self.stdout.write(self.style.SUCCESS("Customer & address sync process completed successfully."))
