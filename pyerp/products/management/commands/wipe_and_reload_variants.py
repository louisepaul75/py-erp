"""
Management command to wipe all variant products and reload them from Artikel_Variante.  # noqa: E501
"""

import logging
import os  # noqa: F401
import sys
import pandas as pd  # noqa: F401
from django.core.management.base import BaseCommand
from django.db import transaction
from pyerp.products.models import ParentProduct, VariantProduct, ProductCategory  # noqa: E501
from decimal import Decimal

 # Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

 # Now import from wsz_api
from wsz_api.getTable import fetch_data_from_api

 # Configure logging
logger = logging.getLogger(__name__)  # noqa: F841


class Command(BaseCommand):
    help = 'Wipe all variant products and reload them from Artikel_Variante'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Run without making changes to the database'  # noqa: F841
        )
        parser.add_argument(
            '--limit',  # noqa: E128
            type=int,  # noqa: F841
            help='Limit the number of Artikel_Variante records to import'  # noqa: F841
        )
        parser.add_argument(
            '--preserve-existing',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Preserve existing variants (will not delete variants)'  # noqa: F841
        )
        parser.add_argument(
            '--batch-size',  # noqa: E128
            type=int,  # noqa: F841
            default=50,  # noqa: F841
            help='Number of records to process in each transaction batch'  # noqa: F841
        )
        parser.add_argument(
            '--start-from',  # noqa: E128
            type=int,  # noqa: F841
            default=0,  # noqa: F841
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
        preserve_existing = options['preserve_existing']
        batch_size = options['batch_size']
        start_from = options['start_from']
        verbose = options['verbose']

        self.stdout.write(self.style.NOTICE('Starting variant product wipe and reload from Artikel_Variante...'))  # noqa: E501

 # Get current count of variant products
        initial_count = VariantProduct.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Current variant product count: {initial_count}'))  # noqa: E501

 # Wipe all variant products if not preserving existing
        if not preserve_existing and not dry_run:
            self.stdout.write(self.style.WARNING('Deleting all variant products...'))  # noqa: E501
            deleted_count = VariantProduct.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} variant products'))  # noqa: E501
        elif preserve_existing:
            self.stdout.write(self.style.WARNING('Preserving existing variant products...'))  # noqa: E501

 # Create default category if it doesn't exist
        default_category, _ = ProductCategory.objects.get_or_create(
            code='UNCATEGORIZED',  # noqa: E128
            defaults={'name': 'Uncategorized'}  # noqa: F841
        )

 # Fetch data from legacy Artikel_Variante table using wsz_api
        self.stdout.write(self.style.NOTICE('Fetching Artikel_Variante data from legacy ERP...'))  # noqa: E501
        try:
            artikel_variante_df = fetch_data_from_api('Artikel_Variante', top=10000, new_data_only=False)  # noqa: E501

            if artikel_variante_df is None or len(artikel_variante_df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from Artikel_Variante table"))  # noqa: E501
                return

            total_records = len(artikel_variante_df)
            self.stdout.write(self.style.SUCCESS(f'Fetched {total_records} records from Artikel_Variante'))  # noqa: E501

 # Print sample data for debugging
            self.stdout.write("Sample columns from first record:")
            if total_records > 0:
                first_row = artikel_variante_df.iloc[0]
                self.stdout.write(f"Available columns: {list(first_row.keys())}")  # noqa: E501
                self.stdout.write(f"UID: {first_row.get('UID', 'N/A')}")
                self.stdout.write(f"__KEY: {first_row.get('__KEY', 'N/A')}")
                self.stdout.write(f"Nummer: {first_row.get('Nummer', 'N/A')}")
                self.stdout.write(f"Familie_: {first_row.get('Familie_', 'N/A')}")  # noqa: E501

 # Limit records if specified
            if limit is not None and limit > 0:
                artikel_variante_df = artikel_variante_df.head(limit)
                self.stdout.write(self.style.NOTICE(f'Limited to {limit} records'))  # noqa: E501

 # Create mapping from Familie_ to ParentProduct
            familie_to_parent = {}
            for _, parent_product in ParentProduct.objects.all().values_list('id', 'legacy_id'):  # noqa: E501
                if parent_product:
                    familie_to_parent[parent_product] = parent_product

            self.stdout.write(f'Loaded {len(familie_to_parent)} parent products for Familie_ mapping')  # noqa: E501

 # Track statistics
            stats = {
                     'total': len(artikel_variante_df),  # noqa: E128
                     'created': 0,
                     'updated': 0,
                     'errors': 0,
                     'parent_not_found': 0
            }

 # Process records in batches to prevent transaction errors
            records = artikel_variante_df.iloc[start_from:].to_dict('records')
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
                            variant_key = row['__KEY']  # Primary key in the source database  # noqa: E501
                            variant_uid = row.get('UID', None)  # UID field from Artikel_Variante  # noqa: E501
                            product_name = row['Bezeichnung'] if pd.notna(row['Bezeichnung']) else "Unnamed Variant"  # noqa: E501

 # Get the Nummer field and ensure it's a string
                            nummer = row['Nummer'] if pd.notna(row['Nummer']) else None  # noqa: E501
                            alte_nummer = row['alteNummer'] if pd.notna(row['alteNummer']) else None  # noqa: E501

                            if nummer is not None:
                                nummer = str(nummer)
                            elif alte_nummer is not None:
                                nummer = str(alte_nummer)
                            else:
                                self.stdout.write(self.style.WARNING(f"Skipping record {record_index}: No Nummer or alteNummer field"))  # noqa: E501
                                stats['errors'] += 1
                                continue

                            is_active = bool(row['aktiv']) if pd.notna(row.get('aktiv')) else True  # noqa: E501

 # Generate a product SKU from the Nummer field
                            sku = nummer

 # Parse SKU and variant code - split by the last hyphen  # noqa: E501
                            if alte_nummer and '-' in alte_nummer:
                                last_hyphen_index = alte_nummer.rfind('-')
                                base_sku = alte_nummer[:last_hyphen_index]  # Everything before the last hyphen  # noqa: E501
                                variant_code = alte_nummer[last_hyphen_index+1:]  # Everything after the last hyphen  # noqa: E501
                            else:
                                base_sku = alte_nummer if alte_nummer else nummer  # noqa: E501
                                variant_code = ''

 # Get Familie_ reference for parent product
                            familie_id = row.get('Familie_', None)
                            parent = None

 # Try to find parent by Familie_ first
                            if familie_id in familie_to_parent:
                                try:
                                    parent = ParentProduct.objects.get(legacy_id=familie_id)  # noqa: E501
                                except ParentProduct.DoesNotExist:
                                    pass

 # If no parent found by Familie_, try base_sku
                            if parent is None and base_sku:
                                try:
                                    parent = ParentProduct.objects.filter(base_sku=base_sku).first()  # noqa: E501
                                except Exception:
                                    pass

                            if parent is None:
                                if verbose:
                                    self.stdout.write(self.style.WARNING(f"No parent product found for variant {record_index}: {sku}"))  # noqa: E501
                                stats['parent_not_found'] += 1

 # Get additional attributes if available
                            description = None
                            if pd.notna(row.get('Beschreibung')):
                                try:
                                    if isinstance(row['Beschreibung'], dict) and 'DE' in row['Beschreibung']:  # noqa: E501
                                        description = row['Beschreibung']['DE']
                                    elif isinstance(row['Beschreibung'], str):
                                        description = row['Beschreibung']
                                except:
                                    description = str(row['Beschreibung'])

 # Extract pricing information
                            list_price = Decimal('0.00')  # noqa: F841
                            cost_price = Decimal('0.00')  # noqa: F841

                            if 'Preise' in row and row['Preise'] is not None:
                                prices = row['Preise']
                                if isinstance(prices, dict) and 'Coll' in prices:  # noqa: E501
                                    for price_item in prices['Coll']:
                                        if isinstance(price_item, dict):
                                            if price_item.get('Art') == 'Laden':  # noqa: E501
                                                list_price = Decimal(str(price_item.get('Preis', 0)))  # noqa: E501
                                            elif price_item.get('Art') == 'Einkauf':  # noqa: E501
                                                cost_price = Decimal(str(price_item.get('Preis', 0)))  # noqa: E501

 # Check if variant exists (only if preserving existing)  # noqa: E501
                            if preserve_existing:
                                try:
                                    existing_variant = VariantProduct.objects.get(legacy_uid=variant_uid)  # noqa: E501
                                    exists = True
                                except VariantProduct.DoesNotExist:
                                    try:
                                        existing_variant = VariantProduct.objects.get(sku=sku)  # noqa: E501
                                        exists = True
                                    except VariantProduct.DoesNotExist:
                                        try:
                                            existing_variant = VariantProduct.objects.get(legacy_id=variant_key)  # noqa: E501
                                            exists = True
                                        except VariantProduct.DoesNotExist:
                                            existing_variant = VariantProduct()
                                            exists = False
                            else:
                                existing_variant = VariantProduct()
                                exists = False

 # Set variant product fields
                            existing_variant.sku = sku
                            existing_variant.legacy_sku = alte_nummer
                            existing_variant.base_sku = base_sku
                            existing_variant.variant_code = variant_code
                            existing_variant.legacy_id = variant_key
                            existing_variant.legacy_uid = variant_uid  # Store UID separately  # noqa: E501

 # Store original field names for display purposes
                            existing_variant.legacy_key = variant_key
                            existing_variant.legacy_uid_original = variant_uid
                            existing_variant.legacy_familie = familie_id

                            existing_variant.name = product_name
                            existing_variant.description = description
                            existing_variant.is_active = is_active
                            existing_variant.parent = parent

 # Debug info
                            if verbose:
                                self.stdout.write(f"Record {record_index}: KEY={variant_key}, UID={variant_uid}, Familie_={familie_id}")  # noqa: E501

 # Save the product if not a dry run
                            if not dry_run:
                                existing_variant.save()
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
        final_count = VariantProduct.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Final variant product count: {final_count}'))  # noqa: E501

 # Print summary
        self.stdout.write("\nReload summary:")
        self.stdout.write(f"Total records processed: {stats['total']}")
        self.stdout.write(f"Created: {stats['created']}")
        self.stdout.write(f"Updated: {stats['updated']}")
        self.stdout.write(f"Errors: {stats['errors']}")
        self.stdout.write(f"Parent not found: {stats['parent_not_found']}")

        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Run 'python manage.py fix_variant_parent_relationships' to update any missing variant-parent relationships")  # noqa: E501
        self.stdout.write("2. Verify the changes with 'python manage.py test_product_split'")  # noqa: E501
