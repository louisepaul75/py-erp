"""
Management command to wipe all parent products and reload them from Artikel_Familie.  # noqa: E501
"""

import logging
import os  # noqa: F401
import sys
import pandas as pd  # noqa: F401
from django.core.management.base import BaseCommand
from django.db import transaction
from pyerp.products.models import ParentProduct, ProductCategory

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

# Now import from wsz_api
from wsz_api.getTable import fetch_data_from_api

# Configure logging
logger = logging.getLogger(__name__)  # noqa: F841
  # noqa: F841


class Command(BaseCommand):
    help = 'Wipe all parent products and reload them from Artikel_Familie, using Nummer as SKU and storing UID'  # noqa: E501

    def add_arguments(self, parser):

        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Run without making changes to the database'  # noqa: F841
        )
        parser.add_argument(
            '--limit',  # noqa: E128
            type=int,  # noqa: F841
            help='Limit the number of Artikel_Familie records to import'  # noqa: F841
        )
        parser.add_argument(
            '--preserve-relationships',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Preserve parent-variant relationships (will not delete parents)'  # noqa: E501
        )
        parser.add_argument(
            '--batch-size',  # noqa: E128
            type=int,  # noqa: F841
            default=100,  # noqa: F841
            help='Number of records to process in each transaction batch'  # noqa: F841
        )
        parser.add_argument(
            '--start-from',  # noqa: E128
            type=int,  # noqa: F841
  # noqa: F841
            default=0,  # noqa: F841
  # noqa: F841
            help='Start processing from this record index'  # noqa: F841
        )
        parser.add_argument(
            '--verbose',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Print detailed information for each record'  # noqa: F841
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        preserve_relationships = options['preserve_relationships']
        batch_size = options['batch_size']
        start_from = options['start_from']
        verbose = options['verbose']

        self.stdout.write(self.style.NOTICE('Starting parent product wipe and reload from Artikel_Familie...'))  # noqa: E501

        # Get current count of parent products
        initial_count = ParentProduct.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Current parent product count: {initial_count}'))  # noqa: E501

        # Wipe all parent products if not preserving relationships
        if not preserve_relationships and not dry_run:
            self.stdout.write(self.style.WARNING('Deleting all parent products...'))  # noqa: E501
            deleted_count = ParentProduct.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} parent products'))  # noqa: E501
        elif preserve_relationships:
            self.stdout.write(self.style.WARNING('Preserving parent products for relationships...'))  # noqa: E501

        # Fetch data from legacy Artikel_Familie table using wsz_api
        self.stdout.write(self.style.NOTICE('Fetching Artikel_Familie data from legacy ERP...'))  # noqa: E501
        try:
            # Use wsz_api to fetch the data
            artikel_familie_df = fetch_data_from_api('Artikel_Familie', top=10000, new_data_only=False)  # noqa: E501

            if artikel_familie_df is None or len(artikel_familie_df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from Artikel_Familie table"))  # noqa: E501
                return

            total_records = len(artikel_familie_df)
            self.stdout.write(self.style.SUCCESS(f'Fetched {total_records} records from Artikel_Familie'))  # noqa: E501

            # Print sample data for debugging
            self.stdout.write("Sample columns from first record:")
            if total_records > 0:
                first_row = artikel_familie_df.iloc[0]
                self.stdout.write(f"Available columns: {list(first_row.keys())}")  # noqa: E501
                self.stdout.write(f"UID: {first_row.get('UID', 'N/A')}")
                self.stdout.write(f"__KEY: {first_row.get('__KEY', 'N/A')}")
                self.stdout.write(f"Nummer: {first_row.get('Nummer', 'N/A')}")

            # Limit records if specified
            if limit is not None and limit > 0:
                artikel_familie_df = artikel_familie_df.head(limit)
                self.stdout.write(self.style.NOTICE(f'Limited to {limit} records'))  # noqa: E501

            # Track statistics
            stats = {
                'total': len(artikel_familie_df),  # noqa: E128
                'created': 0,
                'updated': 0,
                'errors': 0
            }

            # Process records in batches to prevent transaction errors
            records = artikel_familie_df.iloc[start_from:].to_dict('records')
            batch_count = (len(records) + batch_size - 1) // batch_size  # ceiling division  # noqa: E501

            for batch_index in range(batch_count):
                batch_start = batch_index * batch_size
                batch_end = min((batch_index + 1) * batch_size, len(records))
                batch = records[batch_start:batch_end]

                self.stdout.write(self.style.NOTICE(f'Processing batch {batch_index + 1}/{batch_count} (records {batch_start + start_from} to {batch_end + start_from - 1})'))  # noqa: E501

                # Process batch in a transaction
                with transaction.atomic():
                    for i, row in enumerate(batch):
                        record_index = batch_start + i + start_from
                        try:
                            # Get essential data
                            familie_key = row['__KEY']  # Primary key in the source database  # noqa: E501
                            familie_uid = row.get('UID', None)  # UID field from Artikel_Familie  # noqa: E501
                            product_name = row['Bezeichnung'] if pd.notna(row['Bezeichnung']) else "Unnamed Product Family"  # noqa: E501

                            # Get the Nummer field and ensure it's a string
                            nummer = row['Nummer'] if pd.notna(row['Nummer']) else None  # noqa: E501
                            if nummer is not None:
                                nummer = str(nummer)
                            else:
                                # Skip records without a Nummer as we need this for the SKU  # noqa: E501
                                self.stdout.write(self.style.WARNING(f"Skipping record {record_index}: No Nummer field"))  # noqa: E501
                                stats['errors'] += 1
                                continue

                            is_active = bool(row['aktiv']) if pd.notna(row.get('aktiv')) else True  # noqa: E501

                            # Generate a product SKU directly from the Nummer field  # noqa: E501
                            sku = nummer

                            # Get additional attributes if available
                            description = None
                            if pd.notna(row.get('Beschreibung')):
                                try:
                                    # Handle the multilingual description object  # noqa: E501
                                    if isinstance(row['Beschreibung'], dict) and 'DE' in row['Beschreibung']:  # noqa: E501
                                        description = row['Beschreibung']['DE']
                                    elif isinstance(row['Beschreibung'], str):
                                        description = row['Beschreibung']
                                except:
                                    # Fall back if parsing fails
                                    description = str(row['Beschreibung'])

                            # Get physical attributes if available
                            weight = int(row['Gewicht']) if pd.notna(row.get('Gewicht')) else None  # noqa: E501
                            width = float(row['Masse_Breite']) if pd.notna(row.get('Masse_Breite')) else None  # noqa: E501
                            height = float(row['Masse_Hoehe']) if pd.notna(row.get('Masse_Hoehe')) else None  # noqa: E501
                            depth = float(row['Masse_Tiefe']) if pd.notna(row.get('Masse_Tiefe')) else None  # noqa: E501

                            # Format dimensions if available
                            dimensions = None
                            if width is not None and height is not None and depth is not None:  # noqa: E501
                                dimensions = f"{width}x{height}x{depth}"

                            # Get category if available
                            category = None
                            if pd.notna(row.get('Gruppe')):
                                try:
                                    category = ProductCategory.objects.get(code=row['Gruppe'])  # noqa: E501
                                except ProductCategory.DoesNotExist:
                                    pass

                            # Check if product exists (only relevant if we're preserving relationships)  # noqa: E501
                            if preserve_relationships:
                                try:
                                    # First try to find by SKU (Nummer)
                                    parent_product = ParentProduct.objects.get(sku=sku)  # noqa: E501
                                    exists = True
                                except ParentProduct.DoesNotExist:
                                    # Then try by UID or KEY
                                    try:
                                        parent_product = ParentProduct.objects.get(legacy_id=familie_uid)  # noqa: E501
                                        exists = True
                                    except ParentProduct.DoesNotExist:
                                        try:
                                            parent_product = ParentProduct.objects.get(legacy_id=familie_key)  # noqa: E501
                                            exists = True
                                        except ParentProduct.DoesNotExist:
                                            parent_product = ParentProduct()
                                            exists = False
                            else:
                                # If we wiped all parents, we're creating new ones  # noqa: E501
                                parent_product = ParentProduct()
                                exists = False

                            # Set parent product fields
                            parent_product.sku = sku
                            parent_product.base_sku = sku
  # noqa: E501, F841
                            parent_product.legacy_id = familie_uid if familie_uid else familie_key  # noqa: E501
  # noqa: E501, F841
                            parent_product.legacy_uid = familie_uid
  # noqa: E501, F841
                            parent_product.__KEY = familie_key
  # noqa: E501, F841
                            parent_product.UID = familie_uid
  # noqa: E501, F841
                            parent_product.name = product_name
                            parent_product.description = description
  # noqa: F841
                            parent_product.is_active = is_active
  # noqa: F841
                            parent_product.weight = weight
  # noqa: F841
                            parent_product.dimensions = dimensions
  # noqa: F841
                            parent_product.category = category
  # noqa: F841

                            # Save the product if not a dry run
                            if not dry_run:
                                parent_product.save()
                                if verbose:
                                    self.stdout.write(f"Processed record {record_index}: {sku} - {product_name}")  # noqa: E501

                            # Update counts
                            if exists:
                                stats['updated'] += 1
                            else:
                                stats['created'] += 1

                        except Exception as e:
                            stats['errors'] += 1
                            self.stdout.write(self.style.ERROR(f"Error processing record {record_index}: {str(e)}"))  # noqa: E501
                            # Print record data to help debug
                            if verbose:
                                self.stdout.write(f"Record data: {row}")

                            # Continue with next record instead of failing the whole batch  # noqa: E501
                            continue

                    # If it's a dry run, rollback the batch transaction
                    if dry_run:
                        self.stdout.write(self.style.WARNING("DRY RUN - No changes were saved for this batch"))  # noqa: E501
                        transaction.set_rollback(True)

                # Report batch progress
                self.stdout.write(self.style.SUCCESS(f'Completed batch {batch_index + 1}/{batch_count}'))  # noqa: E501
                self.stdout.write(f'Progress: Created: {stats["created"]}, Updated: {stats["updated"]}, Errors: {stats["errors"]}')  # noqa: E501

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching or processing data: {str(e)}"))  # noqa: E501
            return

        # Transaction completed, get final count
        final_count = ParentProduct.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Final parent product count: {final_count}'))  # noqa: E501

        # Print summary
        self.stdout.write("\nReload summary:")
        self.stdout.write(f"Total records processed: {stats['total']}")
        self.stdout.write(f"Created: {stats['created']}")
        self.stdout.write(f"Updated: {stats['updated']}")
        self.stdout.write(f"Errors: {stats['errors']}")

        self.stdout.write("\nNOTE: Reloading parent products may affect variant-parent relationships.")  # noqa: E501
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Run 'python manage.py fix_variant_parent_relationships' to update variant-parent relationships")  # noqa: E501
        self.stdout.write("2. Verify the changes with 'python manage.py test_product_split'")  # noqa: E501
