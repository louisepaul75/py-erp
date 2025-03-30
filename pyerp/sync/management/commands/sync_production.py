"""
Management command to synchronize production orders and items from legacy ERP.

This command allows syncing production orders and their line items from the legacy ERP
to the pyERP system, either as a full sync or an incremental update.
"""

import time
from typing import Any, Dict, List, Optional
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from pyerp.utils.logging import get_logger

from pyerp.sync.tasks import (
    run_production_sync,
    create_production_mappings,
    sync_molds,
    sync_mold_products,
    run_entity_sync,
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
            help=(
                "Time to wait between syncing orders and order items in seconds"
            ),
        )
        parser.add_argument(
            "--orders-only",
            action="store_true",
            help="Only sync production orders, not order items",
        )
        parser.add_argument(
            "--items-only",
            action="store_true",
            help="Only sync production order items, not order items",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )
        parser.add_argument(
            "--days",
            type=int,
            help="Only sync records modified in the last N days",
        )
        parser.add_argument(
            "--skip-molds",
            action="store_true",
            help="Skip syncing molds and mold products",
        )
        parser.add_argument(
            "--molds-only",
            action="store_true",
            help="Only sync molds and mold products",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        incremental = options["incremental"]
        batch_size = options["batch_size"]
        wait_time = options["wait"]
        orders_only = options["orders_only"]
        items_only = options["items_only"]
        verbose = options["verbose"]
        days = options.get("days")
        skip_molds = options["skip_molds"]
        molds_only = options["molds_only"]

        if (orders_only or items_only) and molds_only:
            raise CommandError(
                "Cannot specify both --orders-only/--items-only and --molds-only"
            )
        if molds_only and skip_molds:
            raise CommandError(
                "Cannot specify both --molds-only and --skip-molds"
            )

        # Determine which parts to run
        run_orders = not items_only and not molds_only
        run_items = not orders_only and not molds_only
        run_molds = not skip_molds and not orders_only and not items_only

        # If molds_only is specified, only run molds and mold products
        if molds_only:
            run_orders = False
            run_items = False
            run_molds = True

        try:
            # Mappings for Orders/Items are needed only if running them
            production_order_mapping_id = None
            production_order_item_mapping_id = None
            if run_orders or run_items:
                production_order_mapping_id, \
                    production_order_item_mapping_id = \
                    create_production_mappings()
                if not production_order_mapping_id or \
                        not production_order_item_mapping_id:
                    raise CommandError(
                        "Failed to create or retrieve sync mappings for "
                        "orders/items"
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully created/updated order/item sync mappings"
                    )
                )

            sync_type = "incremental" if incremental else "full"
            self.stdout.write(
                self.style.WARNING(
                    f"Starting {sync_type} production sync with batch size "
                    f"{batch_size}"
                )
            )

            # Apply days filter if specified (relevant for orders/items)
            query_params_orders = {}
            query_params_items = {}
            if days is not None:
                modified_since = timezone.now() - timedelta(days=days)
                date_str = modified_since.strftime("%Y-%m-%d")
                query_params_orders = {
                    "filter_query": [["modified_date", ">", date_str]]
                }
                query_params_items = {
                    "filter_query": [["modified_date", ">", date_str]]
                }
                self.stdout.write(
                    f"Filtering orders/items modified in the last {days} days "
                    f"(since {date_str})"
                )

            start_time = time.time()
            results = []

            # --- Sync Molds and Mold Products (if not skipped) ---
            if run_molds:
                self.stdout.write("Syncing molds...")
                mold_result = sync_molds(
                    incremental=incremental, batch_size=batch_size
                )
                results.append(mold_result)
                if verbose:
                    self.stdout.write(str(mold_result))
                mold_status = mold_result.get("status", "unknown")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Mold sync completed with status: {mold_status}"
                    )
                )

                self.stdout.write("Syncing mold products...")
                mold_product_result = sync_mold_products(
                    incremental=incremental, batch_size=batch_size
                )
                results.append(mold_product_result)
                if verbose:
                    self.stdout.write(str(mold_product_result))
                mold_product_status = mold_product_result.get("status", "unknown")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Mold product sync completed with status: "
                        f"{mold_product_status}"
                    )
                )
                
                if wait_time > 0 and (run_orders or run_items):
                    self.stdout.write(
                        f"Waiting {wait_time} seconds before syncing "
                        f"orders/items..."
                    )
                    time.sleep(wait_time)

            # --- Sync Production Orders (if not skipped) ---
            if run_orders:
                self.stdout.write("Syncing production orders...")
                self.stdout.write(f"Using filter: {query_params_orders}")
                
                order_result = run_entity_sync(
                    mapping_id=production_order_mapping_id,
                    incremental=incremental,
                    batch_size=batch_size,
                    query_params=query_params_orders,
                )
                
                results.append(order_result)
                
                if verbose:
                    self.stdout.write(str(order_result))
                
                order_status = order_result.get("status", "unknown")
                order_count = order_result.get("records_processed", 0)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Production order sync completed with status: {order_status}"
                    )
                )
                self.stdout.write(
                    f"Processed {order_count} production orders"
                )
                
                if wait_time > 0:
                    self.stdout.write(
                        f"Waiting {wait_time} seconds before syncing items..."
                    )
                    time.sleep(wait_time)

            # --- Sync Production Order Items (if not skipped) ---
            if run_items:
                self.stdout.write("Syncing production order items...")
                self.stdout.write(f"Using filter: {query_params_items}")
                
                item_result = run_entity_sync(
                    mapping_id=production_order_item_mapping_id,
                    incremental=incremental,
                    batch_size=batch_size,
                    query_params=query_params_items,
                )
                
                results.append(item_result)
                
                if verbose:
                    self.stdout.write(str(item_result))
                
                item_status = item_result.get("status", "unknown")
                item_count = item_result.get("records_processed", 0)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Production order item sync completed with status: "
                        f"{item_status}"
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
            
            # Return results as string to avoid error
            return str(results)

        except Exception as e:
            logger.error(f"Production sync failed: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Error during sync: {e}"))
            raise CommandError(f"Sync failed: {e}") 