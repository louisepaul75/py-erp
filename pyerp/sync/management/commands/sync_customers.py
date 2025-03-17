"""Management command to sync both customers and addresses from legacy ERP."""

import logging
import yaml
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, NamedTuple

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.apps import apps

from pyerp.sync.pipeline import PipelineFactory
from pyerp.sync.models import SyncMapping


logger = logging.getLogger(__name__)


class LoadResult(NamedTuple):
    """Result of a load operation."""

    created: int
    updated: int
    skipped: int
    errors: int
    error_details: list


class Command(BaseCommand):
    """Django management command to sync customers and addresses."""

    help = "Sync customers and addresses from legacy ERP system"

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
            default=500,
            help="Number of records to process in each batch",
        )
        parser.add_argument(
            "--customer-number",
            type=str,
            help="Sync specific customer by customer number",
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
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="Update records even if not modified",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)

        self.stdout.write("Starting customer sync process")

        try:
            # Load configuration
            config_path = (
                Path(__file__).resolve().parent.parent.parent
                / "config"
                / "customers_sync.yaml"
            )
            self.stdout.write(f"Loading config from: {config_path}")

            with open(config_path) as f:
                config = yaml.safe_load(f)

            # Set up query parameters
            query_params = {}

            # Filter by days if specified
            if options["days"]:
                days_ago = timezone.now() - timedelta(days=options["days"])
                query_params["modified_date"] = {"gt": days_ago.strftime("%Y-%m-%d")}
                days = options["days"]
                msg = f"Filtering records modified in the last {days} days"
                self.stdout.write(msg)

            # Filter by customer number if specified
            if options["customer_number"]:
                query_params["KundenNr"] = options["customer_number"]

            # Set batch size
            batch_size = options["batch_size"]
            self.stdout.write(f"Using batch size: {batch_size}")

            # Sync customers if not skipped
            if not options["skip_customers"]:
                self.stdout.write("\nStarting customer sync...")
                customer_result = self._sync_customers(
                    config,
                    batch_size,
                    query_params,
                    options["force_update"],
                )

                # Print customer sync results
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nCustomer sync completed:"
                        f"\n- Created: {customer_result.created}"
                        f"\n- Updated: {customer_result.updated}"
                        f"\n- Skipped: {customer_result.skipped}"
                        f"\n- Errors: {customer_result.errors}"
                    )
                )

                if customer_result.error_details:
                    self.stdout.write(self.style.WARNING("\nCustomer sync errors:"))
                    for error in customer_result.error_details:
                        if isinstance(error, dict) and "error" in error:
                            self.stdout.write(f"- {error['error']}")
                        elif isinstance(error, dict) and "error_message" in error:
                            self.stdout.write(f"- {error['error_message']}")
                        else:
                            self.stdout.write(f"- {error}")

            # Sync addresses if not skipped
            if not options["skip_addresses"]:
                self.stdout.write("\nStarting address sync...")
                address_result = self._sync_addresses(
                    config,
                    batch_size,
                    query_params,
                    options["force_update"],
                )

                # Print address sync results
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nAddress sync completed:"
                        f"\n- Created: {address_result.created}"
                        f"\n- Updated: {address_result.updated}"
                        f"\n- Skipped: {address_result.skipped}"
                        f"\n- Errors: {address_result.errors}"
                    )
                )

                if address_result.error_details:
                    self.stdout.write(self.style.WARNING("\nAddress sync errors:"))
                    for error in address_result.error_details:
                        if isinstance(error, dict) and "error" in error:
                            self.stdout.write(f"- {error['error']}")
                        elif isinstance(error, dict) and "error_message" in error:
                            self.stdout.write(f"- {error['error_message']}")
                        else:
                            self.stdout.write(f"- {error}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nSync failed: {e}"))
            raise

    def _sync_customers(
        self,
        config: Dict[str, Any],
        batch_size: int,
        query_params: Dict[str, Any],
        force_update: bool,
    ) -> LoadResult:
        """Run customer sync pipeline.

        Args:
            config: Configuration dictionary
            batch_size: Number of records per batch
            query_params: Query parameters for filtering
            force_update: Whether to update unmodified records

        Returns:
            LoadResult containing sync statistics
        """
        # Get the sync mapping
        try:
            mapping = SyncMapping.objects.get(
                entity_type="customer",
                source__name="customers_sync",
                target__name=("sales.Customer"),
            )
        except SyncMapping.DoesNotExist:
            raise RuntimeError(
                "Customer sync mapping not found. "
                "Please run setup_customer_sync first."
            )

        # Create pipeline using factory
        pipeline = PipelineFactory.create_pipeline(mapping)

        # Get existing customer numbers for prefiltering
        Customer = apps.get_model("sales", "Customer")
        existing_customer_numbers = set(
            Customer.objects.values_list("customer_number", flat=True)
        )
        self.stdout.write(f"Found {len(existing_customer_numbers)} existing customers")

        # Extract data with optimized approach
        with pipeline.extractor:
            source_data = pipeline.extractor.extract(
                query_params=query_params, fail_on_filter_error=True
            )

        self.stdout.write(f"Extracted {len(source_data)} customer records")

        # Prefilter records to separate new and existing
        new_records, existing_records = pipeline.transformer.prefilter_records(
            source_data,
            existing_keys=existing_customer_numbers,
            key_field="customer_number",
        )

        self.stdout.write(
            f"Prefiltered: {len(new_records)} new, "
            f"{len(existing_records)} existing customers"
        )

        # Process new records
        created = 0
        if new_records:
            self.stdout.write("Processing new customer records...")
            transformed_new = pipeline.transformer.transform(new_records)
            new_result = pipeline.loader.load(transformed_new, update_existing=False)
            created = new_result.created

        # Process existing records if needed
        updated = 0
        if existing_records and force_update:
            self.stdout.write("Processing existing customer records...")
            transformed_existing = pipeline.transformer.transform(existing_records)
            existing_result = pipeline.loader.load(
                transformed_existing, update_existing=True
            )
            updated = existing_result.updated
        else:
            self.stdout.write("Skipping existing customer records")

        # Create a combined result
        errors = []

        return LoadResult(
            created=created,
            updated=updated,
            skipped=len(existing_records) if not force_update else 0,
            errors=len(errors),
            error_details=errors,
        )

    def _sync_addresses(
        self,
        config: Dict[str, Any],
        batch_size: int,
        query_params: Dict[str, Any],
        force_update: bool,
    ) -> LoadResult:
        """Run address sync pipeline.

        Args:
            config: Configuration dictionary
            batch_size: Number of records per batch
            query_params: Query parameters for filtering
            force_update: Whether to update unmodified records

        Returns:
            LoadResult containing sync statistics
        """
        # Get the sync mapping
        try:
            mapping = SyncMapping.objects.get(
                entity_type="address",
                source__name="customers_sync_addresses",
                target__name=("sales.Address"),
            )
        except SyncMapping.DoesNotExist:
            raise RuntimeError(
                "Address sync mapping not found. "
                "Please run setup_customer_sync first."
            )

        # Create pipeline using factory
        pipeline = PipelineFactory.create_pipeline(mapping)

        # Get existing address legacy IDs for prefiltering
        Address = apps.get_model("sales", "Address")
        existing_address_ids = set(Address.objects.values_list("legacy_id", flat=True))
        self.stdout.write(f"Found {len(existing_address_ids)} existing addresses")

        # Extract data with optimized approach
        with pipeline.extractor:
            source_data = pipeline.extractor.extract(
                query_params=query_params, fail_on_filter_error=True
            )

        self.stdout.write(f"Extracted {len(source_data)} address records")

        # Prefilter records to separate new and existing
        new_records, existing_records = pipeline.transformer.prefilter_records(
            source_data, existing_keys=existing_address_ids, key_field="legacy_id"
        )

        self.stdout.write(
            f"Prefiltered: {len(new_records)} new, "
            f"{len(existing_records)} existing addresses"
        )

        # Process new records
        created = 0
        if new_records:
            self.stdout.write("Processing new address records...")
            transformed_new = pipeline.transformer.transform(new_records)
            new_result = pipeline.loader.load(transformed_new, update_existing=False)
            created = new_result.created

        # Process existing records if needed
        updated = 0
        if existing_records and force_update:
            self.stdout.write("Processing existing address records...")
            transformed_existing = pipeline.transformer.transform(existing_records)
            existing_result = pipeline.loader.load(
                transformed_existing, update_existing=True
            )
            updated = existing_result.updated
        else:
            self.stdout.write("Skipping existing address records")

        # Create a combined result
        errors = []

        return LoadResult(
            created=created,
            updated=updated,
            skipped=len(existing_records) if not force_update else 0,
            errors=len(errors),
            error_details=errors,
        )
