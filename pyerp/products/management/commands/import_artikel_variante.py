"""
Management command to import product variants from the legacy Artikel_Variante table.  # noqa: E501
"""

import os  # noqa: F401
import sys
import logging
import pandas as pd  # noqa: F401
from django.core.management.base import BaseCommand
from django.db import transaction
from pyerp.products.models import ParentProduct, VariantProduct, ProductCategory  # noqa: E501
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    # Import the WSZ_api modules
    from wsz_api.getTable import fetch_data_from_api
except ImportError as e:
    logger.error(f"Failed to import WSZ_api modules: {e}")
    raise


class Command(BaseCommand):
    help = 'Import product variants from the legacy Artikel_Variante table'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            '--limit',  # noqa: E128
            type=int,  # noqa: F841
  # noqa: F841
            default=None,  # noqa: F841
            help='Limit the number of variants to import'  # noqa: F841
        )
        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Perform a dry run without saving to the database'  # noqa: F841
        )
        parser.add_argument(
            '--skip-existing',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Skip variants that already exist in the database'  # noqa: F841
  # noqa: F841
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']

        self.stdout.write(self.style.NOTICE('Starting product variant import...'))  # noqa: E501

        # Create uncategorized category if it doesn't exist
        uncategorized, _ = ProductCategory.objects.get_or_create(
            code='UNCATEGORIZED',  # noqa: E128
            defaults={'name': 'Uncategorized'}  # noqa: F841
        )

        try:
            # Fetch data from Artikel_Variante
            self.stdout.write('Fetching data from Artikel_Variante table...')
            df = fetch_data_from_api(
                table_name="Artikel_Variante",  # noqa: F841
  # noqa: F841
                top=limit,  # noqa: F841
  # noqa: F841
                new_data_only=False  # noqa: F841
  # noqa: F841
            )

            self.stdout.write(self.style.SUCCESS(f'Fetched {len(df)} records'))

            # Track statistics
            stats = {
                'total': len(df),  # noqa: E128
                'created': 0,
                'skipped': 0,
                'errors': 0,
                'parent_not_found': 0
            }

            # Process each variant
            for index, row in df.iterrows():
                try:
                    # Extract data from the row
                    legacy_id = row['UID']
                    alte_nummer = row['alteNummer']
                    nummer = row['Nummer'] if 'Nummer' in row and pd.notna(row['Nummer']) else None  # noqa: E501
                    bezeichnung = row['Bezeichnung']
                    ref_old = row['refOld'] if 'refOld' in row else None

                    # Skip if the variant already exists and skip_existing is True  # noqa: E501
                    if skip_existing and VariantProduct.objects.filter(legacy_id=legacy_id).exists():  # noqa: E501
                        self.stdout.write(f'Skipping existing variant: {alte_nummer}')  # noqa: E501
                        stats['skipped'] += 1
                        continue

                    # Determine the primary SKU - use Nummer if available, otherwise fallback to alteNummer  # noqa: E501
                    primary_sku = str(nummer) if nummer is not None else alte_nummer  # noqa: E501

                    # Parse SKU and variant code - split by the last hyphen
                    if '-' in alte_nummer:
                        # Split by the last hyphen
                        last_hyphen_index = alte_nummer.rfind('-')
                        base_sku = alte_nummer[:last_hyphen_index]  # Everything before the last hyphen  # noqa: E501
                        variant_code = alte_nummer[last_hyphen_index+1:]  # Everything after the last hyphen  # noqa: E501
                    else:
                        base_sku = alte_nummer
                        variant_code = ''

                    # Find parent product by base_sku
                    parent = None
                    if base_sku:
                        parent_candidates = ParentProduct.objects.filter(base_sku=base_sku)  # noqa: E501
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    if not parent and ref_old:
                        # Try to find parent by legacy_id
                        parent_candidates = ParentProduct.objects.filter(legacy_id=str(ref_old))  # noqa: E501
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    if not parent:
                        self.stdout.write(
                            self.style.WARNING(f'Parent product not found for variant: {alte_nummer}')  # noqa: E501
                        )
                        stats['parent_not_found'] += 1
                        continue  # Skip this variant since we need a parent

                    # Extract pricing information
                    list_price = Decimal('0.00')
                    cost_price = Decimal('0.00')

                    if 'Preise' in row and row['Preise'] is not None:
                        prices = row['Preise']
                        if isinstance(prices, dict) and 'Coll' in prices:
                            for price_item in prices['Coll']:
                                if isinstance(price_item, dict):
                                    if price_item.get('Art') == 'Laden':
                                        list_price = Decimal(str(price_item.get('Preis', 0)))  # noqa: E501
                                    elif price_item.get('Art') == 'Einkauf':
                                        cost_price = Decimal(str(price_item.get('Preis', 0)))  # noqa: E501

                    # Create variant data
                    variant_data = {
                        'sku': primary_sku,  # Use Nummer as primary SKU  # noqa: E128
                        'base_sku': base_sku,
                        'variant_code': variant_code,
                        'name': bezeichnung,
                        'legacy_id': legacy_id,
                        'legacy_sku': alte_nummer,  # Store alteNummer as legacy_sku  # noqa: E501
                        'parent': parent,
                        'list_price': list_price,
                        'cost_price': cost_price,
                        'category': parent.category,
                    }

                    # Print variant data in dry run mode
                    if dry_run:
                        self.stdout.write(f'Would create variant: {variant_data}')  # noqa: E501
                        stats['created'] += 1
                        continue

                    # Create or update the variant
                    with transaction.atomic():
                        variant, created = VariantProduct.objects.update_or_create(  # noqa: E501
                            legacy_id=legacy_id,
  # noqa: F841
                            defaults=variant_data  # noqa: F841
  # noqa: F841
                        )

                        if created:
                            self.stdout.write(f'Created variant: {variant.sku}')  # noqa: E501
                        else:
                            self.stdout.write(f'Updated variant: {variant.sku}')  # noqa: E501

                        stats['created'] += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing variant {index}: {str(e)}')  # noqa: E501
                    )
                    stats['errors'] += 1

            # Print summary
            self.stdout.write(self.style.SUCCESS(
                "\nImport summary:\n"  # noqa: E128
                f"Total records: {stats['total']}\n"
                f"Created/Updated: {stats['created']}\n"
                f"Skipped: {stats['skipped']}\n"
                f"Errors: {stats['errors']}\n"
                f"Parent not found: {stats['parent_not_found']}"
            ))

            if dry_run:
                self.stdout.write(self.style.NOTICE(
                    'This was a dry run. No changes were made to the database.'  # noqa: E128
                ))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing variants: {str(e)}')  # noqa: E128
            )
            raise
