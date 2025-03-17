"""Sync parent and variant products from legacy ERP."""

import logging
import yaml
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, NamedTuple

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory

# Configure database logging to ERROR level
db_logger = logging.getLogger('django.db.backends')
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
formatter = logging.Formatter('%(levelname)s: %(message)s')
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

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)
            
        self.stdout.write(self.style.SUCCESS("Starting product sync process"))
        start_time = timezone.now()
        
        try:
            # Load configuration
            config_path = (
                Path(__file__).resolve().parent.parent.parent /
                'config' / 'products_sync.yaml'
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
                days = options['days']
                msg = f"Filtering records modified in the last {days} days"
                self.stdout.write(msg)
                
            # Filter by SKU if specified
            if options["sku"]:
                query_params["Nummer"] = options["sku"]
                self.stdout.write(f"Filtering by SKU: {options['sku']}")
                
            # Set batch size
            batch_size = options["batch_size"]
            self.stdout.write(f"Using batch size: {batch_size}")
            
            # Get fail_on_filter_error option
            fail_on_filter_error = options["fail_on_filter_error"]
            if not fail_on_filter_error:
                self.stdout.write(
                    self.style.WARNING(
                        "Filter errors will be ignored (non-default behavior)"
                    )
                )
            else:
                self.stdout.write(
                    "Will fail if filter doesn't work (default behavior)"
                )
            
            # Sync parent products if not skipped
            if not options["skip_parents"]:
                self.stdout.write(
                    self.style.NOTICE("\n=== Starting Parent Product Sync ===")
                )
                parent_result = self._sync_parents(
                    config,
                    batch_size,
                    query_params,
                    options["force_update"],
                    fail_on_filter_error,
                )
                
                # Print parent sync results
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nParent product sync completed:"
                        f"\n- Created: {parent_result.created}"
                        f"\n- Updated: {parent_result.updated}"
                        f"\n- Skipped: {parent_result.skipped}"
                        f"\n- Errors: {parent_result.errors}"
                    )
                )

                if parent_result.error_details:
                    self.stdout.write(
                        self.style.WARNING("\nParent product sync errors:")
                    )
                    for error in parent_result.error_details:
                        # Check if error_message exists, otherwise use a default message
                        error_msg = error.get(
                            'error_message', 'Unknown error'
                        )
                        self.stdout.write(
                            f"- {error_msg}"
                        )

            # Sync variants if not skipped
            if not options["skip_variants"]:
                header = "\n=== Starting Variant Product Sync ==="
                self.stdout.write(self.style.NOTICE(header))
                variant_result = self._sync_variants(
                    config,
                    batch_size,
                    query_params,
                    options["force_update"],
                    fail_on_filter_error,
                )
                
                # Print variant sync results
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nVariant product sync completed:"
                        f"\n- Created: {variant_result.created}"
                        f"\n- Updated: {variant_result.updated}"
                        f"\n- Skipped: {variant_result.skipped}"
                        f"\n- Errors: {variant_result.errors}"
                    )
                )

                if variant_result.error_details:
                    self.stdout.write(
                        self.style.WARNING("\nVariant product sync errors:")
                    )
                    for error in variant_result.error_details:
                        # Check if error_message exists, otherwise use a default message
                        error_msg = error.get(
                            'error_message', 'Unknown error'
                        )
                        self.stdout.write(
                            f"- {error_msg}"
                        )

            # Print total duration
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nTotal sync duration: {duration:.2f} seconds"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\nSync failed: {e}")
            )
            raise

    def _sync_parents(
        self,
        config: Dict[str, Any],
        batch_size: int,
        query_params: Dict[str, Any],
        force_update: bool,
        fail_on_filter_error: bool = False,
    ) -> LoadResult:
        """Run parent product sync pipeline.
        
        Args:
            config: Configuration dictionary
            batch_size: Number of records per batch
            query_params: Query parameters for filtering
            force_update: Whether to update unmodified records
            fail_on_filter_error: Whether to fail if filter doesn't work
            
        Returns:
            LoadResult containing sync statistics
        """
        # Get mapping for parent products
        mapping = SyncMapping.objects.get(
            entity_type='parent_product',
            active=True,
            source__name='products_sync',
            target__name='products.ParentProduct'
        )
        
        # Create pipeline using factory
        pipeline = PipelineFactory.create_pipeline(mapping)
        
        # Run pipeline
        sync_log = pipeline.run(
            incremental=not force_update,
            batch_size=batch_size,
            query_params=query_params,
            fail_on_filter_error=fail_on_filter_error
        )
        
        return LoadResult(
            created=sync_log.records_succeeded,
            updated=0,  # Not tracked separately in new system
            skipped=sync_log.records_processed - sync_log.records_succeeded,
            errors=sync_log.records_failed,
            error_details=list(
                sync_log.details.filter(status='failed').values()
            )
        )

    def _sync_variants(
        self,
        config: Dict[str, Any],
        batch_size: int,
        query_params: Dict[str, Any],
        force_update: bool,
        fail_on_filter_error: bool = False,
    ) -> LoadResult:
        """Run variant product sync pipeline.
        
        Args:
            config: Configuration dictionary
            batch_size: Number of records per batch
            query_params: Query parameters for filtering
            force_update: Whether to update unmodified records
            fail_on_filter_error: Whether to fail if filter doesn't work
            
        Returns:
            LoadResult containing sync statistics
        """
        # Get mapping for variant products
        mapping = SyncMapping.objects.get(
            entity_type='product_variant',
            active=True,
            source__name='products_sync_variants',
            target__name='products.VariantProduct'
        )
        
        # Create pipeline using factory
        pipeline = PipelineFactory.create_pipeline(mapping)
        
        # Run pipeline
        sync_log = pipeline.run(
            incremental=not force_update,
            batch_size=batch_size,
            query_params=query_params,
            fail_on_filter_error=fail_on_filter_error
        )
        
        return LoadResult(
            created=sync_log.records_succeeded,
            updated=0,  # Not tracked separately in new system
            skipped=sync_log.records_processed - sync_log.records_succeeded,
            errors=sync_log.records_failed,
            error_details=list(
                sync_log.details.filter(status='failed').values()
            )
        ) 