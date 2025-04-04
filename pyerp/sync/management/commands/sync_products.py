"""Sync parent and variant products from legacy ERP."""

import logging
import yaml
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, NamedTuple, List, Optional
import os

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory

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
            "--top",
            type=int,
            help="Only process the first N records",
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
        parser.add_argument(
            "--skip-fetch",
            action="store_true",
            help="Skip initial data fetch (use only with --fetch-only)",
        )
        parser.add_argument(
            "--fetch-only",
            action="store_true",
            help="Only fetch data, don't process it",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)

        self.stdout.write(self.style.SUCCESS("Starting product sync process"))
        start_time = timezone.now()

        try:
            # Clear any existing caches to ensure fresh data
            self._clear_extractor_caches()
            
            # Load configuration
            config_path = (
                Path(__file__).resolve().parent.parent.parent
                / "config"
                / "products_sync.yaml"
            )
            self.stdout.write(f"Loading config from: {config_path}")

            with open(config_path) as f:
                config = yaml.safe_load(f)

            # Set up query parameters
            query_params = {}

            # Filter by days if specified
            if options["days"]:
                days_ago = timezone.now() - timedelta(days=options["days"])
                query_params["modified_date"] = {
                    "gt": days_ago.strftime("%Y-%m-%d")
                }
                days = options["days"]
                msg = f"Filtering records modified in the last {days} days"
                self.stdout.write(msg)

            # Filter by SKU if specified
            if options["sku"]:
                query_params["Nummer"] = options["sku"]
                self.stdout.write(f"Filtering by SKU: {options['sku']}")

            # Set limit if top parameter specified
            limit = options.get("top")
            if limit:
                query_params["$top"] = limit
                self.stdout.write(f"Limiting to first {limit} records")
                # Also set batch_size to match limit to prevent extra processing
                batch_size = limit
            else:
                # Set batch size from options if no limit specified
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

            # Cache for shared data
            shared_data_cache = {}
            
            # If fetch-only mode, just fetch data and exit
            if options["fetch_only"]:
                self._fetch_data_to_cache(
                    "parent_product", 
                    query_params, 
                    fail_on_filter_error,
                    shared_data_cache
                )
                self._fetch_data_to_cache(
                    "product_variant", 
                    query_params, 
                    fail_on_filter_error,
                    shared_data_cache
                )
                self.stdout.write(
                    self.style.SUCCESS("Data fetch completed successfully")
                )
                return
                
            # Skip initial fetch if requested
            if not options["skip_fetch"]:
                # Pre-fetch the data once to avoid repeated API calls
                if not options["skip_parents"]:
                    self.stdout.write(
                        self.style.NOTICE(
                            "\n=== Fetching Parent Product Data ==="
                        )
                    )
                    self._fetch_data_to_cache(
                        "parent_product", 
                        query_params, 
                        fail_on_filter_error,
                        shared_data_cache
                    )
                    
                if not options["skip_variants"]:
                    self.stdout.write(
                        self.style.NOTICE(
                            "\n=== Fetching Variant Product Data ==="
                        )
                    )
                    self._fetch_data_to_cache(
                        "product_variant", 
                        query_params, 
                        fail_on_filter_error,
                        shared_data_cache
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
                    shared_data_cache.get("parent_product"),
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
                        # Check if error_message exists, otherwise use a default
                        error_msg = error.get("error_message", "Unknown error")
                        self.stdout.write(f"- {error_msg}")

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
                    shared_data_cache.get("product_variant"),
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
                        # Check if error_message exists, otherwise use a default
                        error_msg = error.get("error_message", "Unknown error")
                        self.stdout.write(f"- {error_msg}")

            # Print total duration
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nTotal sync duration: {duration:.2f} seconds"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nSync failed: {e}"))
            raise

    def _fetch_data_to_cache(
        self,
        entity_type: str,
        query_params: Dict[str, Any],
        fail_on_filter_error: bool,
        cache: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Fetch data for an entity type and store in cache.
        
        Args:
            entity_type: Type of entity to fetch data for
            query_params: Query parameters for filtering
            fail_on_filter_error: Whether to fail if filter doesn't work
            cache: Dictionary to store fetched data in
        """
        # Get appropriate mapping based on entity type
        mapping_params = {
            "entity_type": entity_type,
            "active": True,
        }
        
        if entity_type == "parent_product":
            mapping_params.update({
                "source__name": "products_sync",
                "target__name": "products.ParentProduct",
            })
        elif entity_type == "product_variant":
            mapping_params.update({
                "source__name": "products_sync_variants",
                "target__name": "products.VariantProduct",
            })
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        try:
            mapping = SyncMapping.objects.get(**mapping_params)
            self.stdout.write(f"Found mapping for {entity_type}: {mapping}")
            
            # Create pipeline
            pipeline = PipelineFactory.create_pipeline(mapping)
            
            # Execute a special fetch-only run to get data
            self.stdout.write(f"Fetching data for {entity_type}...")
            
            try:
                # First try using the fetch_data method if available
                if hasattr(pipeline, "fetch_data"):
                    data = pipeline.fetch_data(
                        query_params=query_params,
                        fail_on_filter_error=fail_on_filter_error
                    )
                    
                    # Store in cache
                    cache[entity_type] = data
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Fetched {len(data)} records for {entity_type}"
                        )
                    )
                else:
                    # If pipeline doesn't support fetch_data, log a warning
                    self.stdout.write(
                        self.style.WARNING(
                            f"Pipeline for {entity_type} doesn't support "
                            f"fetch_data method. Will use direct API calls."
                        )
                    )
            except Exception as e:
                # If fetch_data fails, we'll still try running the full pipeline
                self.stdout.write(
                    self.style.WARNING(
                        f"Error with fetch_data: {e}. Falling back to run() method."
                    )
                )
                
                # We'll leave cache empty - pipeline.run() will be used instead
                
        except SyncMapping.DoesNotExist:
            self.stderr.write(
                f"No active mapping found for {entity_type}"
            )
        except Exception as e:
            self.stderr.write(f"Error fetching data for {entity_type}: {e}")
            # We don't raise the exception here to allow the process to continue
            # with direct API calls

    def _sync_parents(
        self,
        config: Dict[str, Any],
        batch_size: int,
        query_params: Dict[str, Any],
        force_update: bool,
        fail_on_filter_error: bool = False,
        cached_data: Optional[Any] = None,
    ) -> LoadResult:
        """Run parent product sync pipeline.

        Args:
            config: Configuration dictionary
            batch_size: Number of records per batch
            query_params: Query parameters for filtering
            force_update: Whether to update unmodified records
            fail_on_filter_error: Whether to fail if filter doesn't work
            cached_data: Pre-fetched data to use instead of making API calls

        Returns:
            LoadResult containing sync statistics
        """
        try:
            # Get mapping for parent products
            mapping = SyncMapping.objects.get(
                entity_type="parent_product",
                active=True,
                source__name="products_sync",
                target__name="products.ParentProduct",
            )
            
            # Log mapping details for debugging
            self.stdout.write(f"Found mapping: {mapping}")
            self.stdout.write(f"Source config: {mapping.source.config}")
            self.stdout.write(f"Target config: {mapping.target.config}")
            self.stdout.write(f"Mapping config: {mapping.mapping_config}")

            # If no cached data was provided, check if data is available in extractor cache
            if cached_data is None:
                # Import LegacyAPIExtractor to check cache
                from pyerp.sync.extractors.legacy_api import LegacyAPIExtractor
                
                # Get table name from source config
                table_name = "Artikel_Familie"
                if mapping.source.config and "config" in mapping.source.config:
                    if "table_name" in mapping.source.config["config"]:
                        table_name = mapping.source.config["config"]["table_name"]
                
                # Check if data is already in cache
                cached_data = LegacyAPIExtractor.get_cached_data(table_name, query_params)
                if cached_data is not None:
                    if hasattr(cached_data, 'to_dict') and callable(cached_data.to_dict):
                        # Convert DataFrame to list of dictionaries
                        cached_data = cached_data.to_dict(orient="records")
                        self.stdout.write(f"Converted DataFrame to {len(cached_data)} dictionary records")
                    self.stdout.write(f"Using {len(cached_data)} cached records from extractor cache")

            # Create pipeline using factory
            pipeline = PipelineFactory.create_pipeline(mapping)
            
            # Check if we have usable cached data and the pipeline supports run_with_data
            use_cached_data = cached_data is not None and len(cached_data) > 0
            has_run_with_data = hasattr(pipeline, "run_with_data")
            
            # If we have cached data, use it instead of making API calls
            if use_cached_data and has_run_with_data:
                self.stdout.write("Using pre-fetched data for parent products")
                sync_log = pipeline.run_with_data(
                    data=cached_data,
                    incremental=not force_update,
                    batch_size=batch_size,
                    query_params=query_params,
                )
            else:
                # Fall back to run with API calls if no cached data
                if cached_data is not None:
                    self.stdout.write(
                        self.style.WARNING(
                            "Pipeline doesn't support using pre-fetched data. "
                            "Will make API calls instead."
                        )
                    )
                sync_log = pipeline.run(
                    incremental=not force_update,
                    batch_size=batch_size,
                    query_params=query_params,
                    fail_on_filter_error=fail_on_filter_error,
                )

            return LoadResult(
                created=sync_log.records_created,
                updated=0,  # Not tracked separately in new system
                skipped=sync_log.records_processed - sync_log.records_created,
                errors=sync_log.records_failed,
                error_details=[],  # SyncLog doesn't have a details attribute
            )
        except Exception as e:
            self.stderr.write(f"Error in parent product sync: {e}")
            # For debugging, print more details if it's a configuration error
            if "Missing required configuration" in str(e):
                self.stderr.write("Configuration error details:")
                # Check environment variables
                env_vars = [
                    f"LEGACY_ERP_ENV: {os.environ.get('LEGACY_ERP_ENVIRONMENT', 'Not set')}",
                    f"LEGACY_ERP_TABLE: {os.environ.get('LEGACY_ERP_TABLE_NAME', 'Not set')}"
                ]
                self.stderr.write("\n".join(env_vars))
            raise

    def _sync_variants(
        self,
        config: Dict[str, Any],
        batch_size: int,
        query_params: Dict[str, Any],
        force_update: bool,
        fail_on_filter_error: bool = False,
        cached_data: Optional[List[Dict[str, Any]]] = None,
    ) -> LoadResult:
        """Run variant product sync pipeline.

        Args:
            config: Configuration dictionary
            batch_size: Number of records per batch
            query_params: Query parameters for filtering
            force_update: Whether to update unmodified records
            fail_on_filter_error: Whether to fail if filter doesn't work
            cached_data: Pre-fetched data to use instead of making API calls

        Returns:
            LoadResult containing sync statistics
        """
        try:
            # Get mapping for variant products
            mapping = SyncMapping.objects.get(
                entity_type="product_variant",
                active=True,
                source__name="products_sync_variants",
                target__name="products.VariantProduct",
            )
            
            # Log mapping details for debugging
            self.stdout.write(f"Found mapping: {mapping}")
            self.stdout.write(f"Source config: {mapping.source.config}")
            self.stdout.write(f"Target config: {mapping.target.config}")
            self.stdout.write(f"Mapping config: {mapping.mapping_config}")

            # If no cached data was provided, check if data is available in extractor cache
            if cached_data is None:
                # Import LegacyAPIExtractor to check cache
                from pyerp.sync.extractors.legacy_api import LegacyAPIExtractor
                
                # Get table name from source config
                table_name = "Artikel_Variante"
                if mapping.source.config and "config" in mapping.source.config:
                    if "table_name" in mapping.source.config["config"]:
                        table_name = mapping.source.config["config"]["table_name"]
                
                # Check if data is already in cache
                cached_data = LegacyAPIExtractor.get_cached_data(table_name, query_params)
                if cached_data:
                    if hasattr(cached_data, 'to_dict') and callable(cached_data.to_dict):
                        # Convert DataFrame to list of dictionaries
                        cached_data = cached_data.to_dict(orient="records")
                        self.stdout.write(f"Converted DataFrame to {len(cached_data)} dictionary records")
                    self.stdout.write(f"Using {len(cached_data)} cached records from extractor cache")

            # Create pipeline using factory
            pipeline = PipelineFactory.create_pipeline(mapping)
            
            # If we have cached data, use it instead of making API calls
            if cached_data and hasattr(pipeline, "run_with_data"):
                self.stdout.write("Using pre-fetched data for variant products")
                sync_log = pipeline.run_with_data(
                    data=cached_data,
                    incremental=not force_update,
                    batch_size=batch_size,
                    query_params=query_params,
                )
            else:
                # Run pipeline with API calls if no cached data or
                # if pipeline doesn't support run_with_data
                if cached_data:
                    self.stdout.write(
                        self.style.WARNING(
                            "Pipeline doesn't support using pre-fetched data. "
                            "Will make API calls instead."
                        )
                    )
                sync_log = pipeline.run(
                    incremental=not force_update,
                    batch_size=batch_size,
                    query_params=query_params,
                    fail_on_filter_error=fail_on_filter_error,
                )

            return LoadResult(
                created=sync_log.records_created,
                updated=0,  # Not tracked separately in new system
                skipped=sync_log.records_processed - sync_log.records_created,
                errors=sync_log.records_failed,
                error_details=[],  # SyncLog doesn't have a details attribute
            )
        except Exception as e:
            self.stderr.write(f"Error in variant product sync: {e}")
            # For debugging, print more details if it's a configuration error
            if "Missing required configuration" in str(e):
                self.stderr.write("Configuration error details:")
                # Check environment variables
                env_vars = [
                    f"LEGACY_ERP_ENV: {os.environ.get('LEGACY_ERP_ENVIRONMENT', 'Not set')}",
                    f"LEGACY_ERP_TABLE: {os.environ.get('LEGACY_ERP_TABLE_NAME', 'Not set')}"
                ]
                self.stderr.write("\n".join(env_vars))
            raise

    def _clear_extractor_caches(self):
        """Clear any caches used by extractors."""
        try:
            # Import the extractor class to clear its cache
            from pyerp.sync.extractors.legacy_api import LegacyAPIExtractor
            LegacyAPIExtractor.clear_cache()
            self.stdout.write("Cleared API extractors cache")
        except (ImportError, AttributeError) as e:
            self.stdout.write(self.style.WARNING(f"Could not clear cache: {e}"))
        except Exception as e:
            self.stderr.write(f"Error clearing cache: {e}")
