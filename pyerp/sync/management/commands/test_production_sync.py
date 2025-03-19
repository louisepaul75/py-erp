"""
Management command to test production sync with limited data.

This command tests the production order sync with a smaller dataset
to verify the sync process works correctly.
"""

import os
import yaml
import time
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pyerp.utils.logging import get_logger

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget


logger = get_logger(__name__)


class Command(BaseCommand):
    """Command to test production sync with limited data."""

    help = "Test production sync with a limited dataset"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of records to sync",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        limit = options["limit"]
        verbose = options["verbose"]

        try:
            # Create temporary config file for testing
            config_file = self._create_test_config(limit)
            self.stdout.write(f"Created test config at {config_file}")

            # Set up mappings using test config
            self.stdout.write("Setting up test mappings...")
            from django.core.management import call_command
            call_command("setup_production_sync", config_file=config_file)

            # Run the sync
            self.stdout.write(
                self.style.WARNING(f"Starting test sync with limit {limit}")
            )
            start_time = time.time()
            
            # Get mapping IDs
            order_mapping = SyncMapping.objects.filter(
                entity_type="production_order_test"
            ).first()
            
            item_mapping = SyncMapping.objects.filter(
                entity_type="production_order_item_test"
            ).first()
            
            if not order_mapping or not item_mapping:
                raise CommandError("Test mappings not found")
            
            from pyerp.sync.tasks import run_entity_sync
            
            # Sync orders
            self.stdout.write("Syncing production orders (test)...")
            order_result = run_entity_sync(
                mapping_id=order_mapping.id,
                incremental=False,
                batch_size=limit
            )
            
            if verbose:
                self.stdout.write(str(order_result))
            
            order_status = order_result.get("status", "unknown")
            order_count = order_result.get("processed", 0)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Test order sync completed with status: {order_status}"
                )
            )
            self.stdout.write(f"Processed {order_count} orders")
            
            # Get order IDs for filtering items
            from pyerp.business_modules.production.models import ProductionOrder
            order_numbers = list(ProductionOrder.objects.values_list('order_number', flat=True)[:limit])
            
            if not order_numbers:
                self.stdout.write(self.style.WARNING("No orders found to link items to"))
            else:
                self.stdout.write(f"Found {len(order_numbers)} orders for linking items")
                
                # Sync items
                self.stdout.write("Syncing production order items (test)...")
                
                # Create filter query for items based on orders
                filter_query = [["W_Auftr_Nr", "in", order_numbers]]
                
                item_result = run_entity_sync(
                    mapping_id=item_mapping.id,
                    incremental=False,
                    batch_size=limit * 2,  # Items usually have more records
                    query_params={"filter_query": filter_query}
                )
                
                if verbose:
                    self.stdout.write(str(item_result))
                
                item_status = item_result.get("status", "unknown")
                item_count = item_result.get("processed", 0)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Test item sync completed with status: {item_status}"
                    )
                )
                self.stdout.write(f"Processed {item_count} items")
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Test sync completed in {duration:.2f} seconds"
                )
            )
            
            # Clean up test config
            if os.path.exists(config_file):
                os.remove(config_file)
                self.stdout.write(f"Removed test config file")

            # Show results
            from pyerp.business_modules.production.models import ProductionOrder, ProductionOrderItem
            
            order_count = ProductionOrder.objects.count()
            item_count = ProductionOrderItem.objects.count()
            
            self.stdout.write(self.style.SUCCESS(f"Production Orders in database: {order_count}"))
            self.stdout.write(self.style.SUCCESS(f"Production Order Items in database: {item_count}"))

        except Exception as e:
            logger.error(f"Test sync failed: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Error during test: {e}"))
            raise CommandError(f"Test failed: {e}")

    def _create_test_config(self, limit: int) -> str:
        """Create a temporary config file for testing.

        Args:
            limit: Maximum number of records to sync

        Returns:
            Path to the created config file
        """
        # Base config from standard location
        base_config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "production_sync.yaml",
        )
        
        # Test config file path
        test_config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "production_sync_test.yaml",
        )
        
        try:
            # Load base config
            with open(base_config_file, "r") as f:
                config = yaml.safe_load(f)
            
            # Modify for testing
            for mapping in config.get("mappings", []):
                # Change entity types to avoid conflict with real syncs
                if mapping.get("entity_type") == "production_order":
                    mapping["entity_type"] = "production_order_test"
                    # Set limit in extractor config
                    mapping["mapping_config"]["extractor_config"]["page_size"] = limit
                elif mapping.get("entity_type") == "production_order_item":
                    mapping["entity_type"] = "production_order_item_test"
                    # Set limit in extractor config
                    mapping["mapping_config"]["extractor_config"]["page_size"] = limit * 2
            
            # Write modified config
            with open(test_config_file, "w") as f:
                yaml.dump(config, f)
            
            return test_config_file
        except Exception as e:
            logger.error(f"Failed to create test config: {e}", exc_info=True)
            raise CommandError(f"Failed to create test config: {e}") 