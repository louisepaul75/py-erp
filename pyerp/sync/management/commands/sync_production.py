"""
Management command to synchronize production orders and items from legacy ERP.

This command allows syncing production orders and their line items from the legacy ERP
to the pyERP system, either as a full sync or an incremental update.
"""

import time
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pyerp.utils.logging import get_logger

from pyerp.sync.tasks import (
    run_production_sync,
    create_production_mappings,
)


logger = get_logger(__name__)


class Command(BaseCommand):
    """Command to sync production orders from legacy ERP."""

    help = "Synchronize production orders and items from legacy ERP"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--incremental",
            action="store_true",
            help="Only sync records modified since last sync",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of records to process in each batch",
        )
        parser.add_argument(
            "--wait",
            type=int,
            default=0,
            help="Time to wait between syncing orders and order items in seconds",
        )
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
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        incremental = options["incremental"]
        batch_size = options["batch_size"]
        wait_time = options["wait"]
        orders_only = options["orders_only"]
        items_only = options["items_only"]
        verbose = options["verbose"]

        if orders_only and items_only:
            raise CommandError("Cannot specify both --orders-only and --items-only")

        try:
            # Create or update sync mappings
            production_order_mapping_id, production_order_item_mapping_id = create_production_mappings()

            if not production_order_mapping_id or not production_order_item_mapping_id:
                raise CommandError("Failed to create or retrieve sync mappings")

            self.stdout.write(
                self.style.SUCCESS("Successfully created/updated sync mappings")
            )

            sync_type = "incremental" if incremental else "full"
            self.stdout.write(
                self.style.WARNING(
                    f"Starting {sync_type} production sync with batch size {batch_size}"
                )
            )

            start_time = time.time()
            results = []

            if not items_only:
                # Sync production orders
                self.stdout.write("Syncing production orders...")
                from pyerp.sync.tasks import run_entity_sync
                
                order_result = run_entity_sync(
                    mapping_id=production_order_mapping_id,
                    incremental=incremental,
                    batch_size=batch_size,
                )
                
                results.append(order_result)
                
                if verbose:
                    self.stdout.write(str(order_result))
                
                order_status = order_result.get("status", "unknown")
                order_count = order_result.get("processed", 0)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Production order sync completed with status: {order_status}"
                    )
                )
                self.stdout.write(
                    f"Processed {order_count} production orders"
                )
                
                if wait_time > 0:
                    self.stdout.write(f"Waiting {wait_time} seconds before syncing items...")
                    time.sleep(wait_time)

            if not orders_only:
                # Sync production order items
                self.stdout.write("Syncing production order items...")
                from pyerp.sync.tasks import run_entity_sync
                
                item_result = run_entity_sync(
                    mapping_id=production_order_item_mapping_id,
                    incremental=incremental,
                    batch_size=batch_size,
                )
                
                results.append(item_result)
                
                if verbose:
                    self.stdout.write(str(item_result))
                
                item_status = item_result.get("status", "unknown")
                item_count = item_result.get("processed", 0)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Production order item sync completed with status: {item_status}"
                    )
                )
                self.stdout.write(
                    f"Processed {item_count} production order items"
                )

            end_time = time.time()
            duration = end_time - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Production sync completed in {duration:.2f} seconds"
                )
            )
            
            return results

        except Exception as e:
            logger.error(f"Production sync failed: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Error during sync: {e}"))
            raise CommandError(f"Sync failed: {e}") 