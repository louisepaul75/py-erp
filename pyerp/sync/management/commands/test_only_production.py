import pytest
"""
Direct test command for production sync.

This command directly calls the legacy ERP client to get production data,
applies transformations, and inserts the records into the database,
without using the full sync framework to avoid triggering other syncs.
"""

import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pyerp.utils.logging import get_logger

from pyerp.external_api.legacy_erp import LegacyERPClient
from pyerp.sync.transformers.production import (
    ProductionOrderTransformer,
    ProductionOrderItemTransformer,
)
from pyerp.business_modules.production.models import (
    ProductionOrder,
    ProductionOrderItem,
)


logger = get_logger(__name__)


class Command(BaseCommand):
    """Direct test command for production sync."""

    help = "Test only production sync directly without triggering other syncs"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of records to fetch",
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
            # Start timer
            start_time = time.time()
            
            self.stdout.write(self.style.WARNING(
                f"Starting direct production sync test with limit {limit}"
            ))
            
            # 1. Directly create the legacy ERP client
            client = LegacyERPClient(environment="live")
            
            # 2. Fetch production orders directly
            self.stdout.write("Fetching production orders...")
            production_orders = client.fetch_table(
                table_name="Werksauftraege",
                top=limit
            )
            
            if verbose:
                self.stdout.write(f"Fetched {len(production_orders)} production orders")
                if not production_orders.empty:
                    self.stdout.write("Sample record:")
                    self.stdout.write(str(production_orders.iloc[0]))
            
            # 3. Transform production orders
            self.stdout.write("Transforming production orders...")
            transformer_config = {
                "field_mappings": {
                    "WerkAufNr": "order_number",
                    "Form_Nr": "form_number",
                    "Stückzahl": "quantity", 
                    "Status": "status",
                    "eingestellt": "creation_date",
                    "Termin": "planned_date",
                    "Prio": "priority",
                    "__KEY": "legacy_key",
                    "UUID": "legacy_id",
                    "linked_Form": "legacy_form_id"
                }
            }
            
            transformer = ProductionOrderTransformer(transformer_config)
            order_records = production_orders.to_dict('records')
            transformed_orders = transformer.transform(order_records)
            
            if verbose:
                self.stdout.write(f"Transformed {len(transformed_orders)} production orders")
                if transformed_orders:
                    self.stdout.write("Sample transformed record:")
                    self.stdout.write(str(transformed_orders[0]))
            
            # 4. Save production orders to database
            self.stdout.write("Saving production orders...")
            
            # Get valid model fields to filter out extraneous fields
            valid_fields = [f.name for f in ProductionOrder._meta.get_fields()]
            self.stdout.write(f"Valid ProductionOrder fields: {valid_fields}")
            
            with transaction.atomic():
                order_map = {}  # Maps order_number to ProductionOrder instance
                
                for order_data in transformed_orders:
                    # Extract only valid model fields
                    filtered_data = {}
                    for key, value in order_data.items():
                        if key in valid_fields:
                            filtered_data[key] = value
                    
                    order_number = filtered_data.pop('order_number')
                    
                    order, created = ProductionOrder.objects.update_or_create(
                        order_number=order_number,
                        defaults=filtered_data
                    )
                    
                    order_map[order_number] = order
                    action = "Created" if created else "Updated"
                    if verbose:
                        self.stdout.write(f"{action} order {order_number}")
            
            self.stdout.write(self.style.SUCCESS(
                f"Successfully saved {len(order_map)} production orders"
            ))
            
            # 5. Get order numbers and fetch related items
            order_numbers = list(order_map.keys())
            
            if order_numbers:
                # 6. Fetch production order items
                self.stdout.write("Fetching production order items...")
                production_order_items = client.fetch_table(
                    table_name="WerksauftrPos",
                    filter_query=[["W_Auftr_Nr", "in", order_numbers]]
                )
                
                if verbose:
                    self.stdout.write(f"Fetched {len(production_order_items)} production order items")
                    if not production_order_items.empty:
                        self.stdout.write("Sample item record:")
                        self.stdout.write(str(production_order_items.iloc[0]))
                
                # 7. Transform production order items
                self.stdout.write("Transforming production order items...")
                item_transformer_config = {
                    "field_mappings": {
                        "W_Auftr_Nr": "production_order__order_number",
                        "Arbeitsgang": "operation_type",
                        "St_Soll": "target_quantity",
                        "St_Haben": "completed_quantity",
                        "St_Rest": "remaining_quantity",
                        "WAP_Nr": "item_number",
                        "Datum_begin": "start_date",
                        "Status": "status",
                        "Art_Nr": "product_sku",
                        "Anteil": "product_share",
                        "Zeit": "estimated_time",
                        "St_Std": "standard_time",
                        "Wert": "value",
                        "__KEY": "legacy_key",
                        "UUID": "legacy_id"
                    }
                }
                
                item_transformer = ProductionOrderItemTransformer(item_transformer_config)
                item_records = production_order_items.to_dict('records')
                transformed_items = item_transformer.transform(item_records)
                
                if verbose:
                    self.stdout.write(f"Transformed {len(transformed_items)} production order items")
                    if transformed_items:
                        self.stdout.write("Sample transformed item:")
                        self.stdout.write(str(transformed_items[0]))
                
                # Get valid item model fields
                valid_item_fields = [f.name for f in ProductionOrderItem._meta.get_fields()]
                self.stdout.write(f"Valid ProductionOrderItem fields: {valid_item_fields}")
                
                # 8. Save production order items to database
                self.stdout.write("Saving production order items...")
                with transaction.atomic():
                    items_created = 0
                    items_updated = 0
                    
                    for item_data in transformed_items:
                        # Get the production order reference
                        production_order_data = item_data.pop('production_order', None)
                        if not production_order_data or 'order_number' not in production_order_data:
                            self.stdout.write(self.style.WARNING(
                                f"Skipping item with missing production order reference"
                            ))
                            continue
                        
                        order_number = production_order_data['order_number']
                        
                        # Get the production order instance
                        if order_number not in order_map:
                            order = ProductionOrder.objects.filter(
                                order_number=order_number
                            ).first()
                            
                            if not order:
                                self.stdout.write(self.style.WARNING(
                                    f"Skipping item for missing order {order_number}"
                                ))
                                continue
                                
                            order_map[order_number] = order
                        
                        # Filter out invalid fields
                        filtered_item_data = {}
                        for key, value in item_data.items():
                            if key in valid_item_fields:
                                filtered_item_data[key] = value
                        
                        # Link to the order
                        filtered_item_data['production_order'] = order_map[order_number]
                        item_number = filtered_item_data.get('item_number')
                        
                        # Update or create the item
                        item, created = ProductionOrderItem.objects.update_or_create(
                            production_order=filtered_item_data['production_order'],
                            item_number=item_number,
                            defaults=filtered_item_data
                        )
                        
                        if created:
                            items_created += 1
                        else:
                            items_updated += 1
                
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully saved {items_created} new and updated {items_updated} existing items"
                ))
            
            # 9. End timer and report results
            end_time = time.time()
            duration = end_time - start_time
            
            # Show results
            order_count = ProductionOrder.objects.count()
            item_count = ProductionOrderItem.objects.count()
            
            self.stdout.write(self.style.SUCCESS(
                f"Direct test completed in {duration:.2f} seconds"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"Total Production Orders in database: {order_count}"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"Total Production Order Items in database: {item_count}"
            ))

        except Exception as e:
            logger.error(f"Direct test failed: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Error during test: {e}"))
            raise CommandError(f"Test failed: {e}") 