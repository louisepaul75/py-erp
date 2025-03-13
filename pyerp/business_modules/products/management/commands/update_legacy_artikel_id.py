"""
Management command to populate the legacy_artikel_id field for existing VariantProduct records.

This command queries the legacy system to get the ID_Artikel_Stamm values for each product
and updates the corresponding VariantProduct records in our system.
"""

import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.business_modules.products.models import VariantProduct
from pyerp.external_api.legacy_erp.client import LegacyERPClient
import pandas as pd

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to update legacy_artikel_id field for VariantProduct records."""

    help = 'Populate legacy_artikel_id field for existing VariantProduct records'

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without making any changes',
        )

    def handle(self, *args, **options):
        """Execute the command."""
        dry_run = options.get('dry_run', False)
        if dry_run:
            self.stdout.write(self.style.WARNING('Performing dry run - no changes will be made'))

        start_time = datetime.now()
        self.stdout.write(f"Starting update at {start_time}")

        # Fetch legacy products
        legacy_products_df = self.fetch_legacy_products()
        
        # Update legacy_artikel_id for existing products
        self.update_legacy_artikel_ids(legacy_products_df, dry_run)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        self.stdout.write(self.style.SUCCESS(f"Update completed in {duration:.2f} seconds"))

    def fetch_legacy_products(self):
        """
        Fetch products from the legacy system.
        
        Returns:
            DataFrame containing product data with ID and Nummer columns
        """
        client = LegacyERPClient(environment="live")
        self.stdout.write("Fetching products from legacy system...")
        
        # Fetch products from Artikel_Variante table
        df = client.fetch_table(
            table_name="Artikel_Variante",
            all_records=True
        )
        
        # Print all columns for debugging
        self.stdout.write(f"Available columns: {', '.join(df.columns)}")
        
        # Keep only the columns we need
        if 'UID' in df.columns and 'Nummer' in df.columns:
            return df[['UID', 'Nummer', 'alteNummer']]
        else:
            missing_cols = []
            if 'UID' not in df.columns:
                missing_cols.append('UID')
            if 'Nummer' not in df.columns:
                missing_cols.append('Nummer')
            if 'alteNummer' not in df.columns:
                missing_cols.append('alteNummer')
            
            self.stdout.write(
                self.style.ERROR(f"Missing required columns: {', '.join(missing_cols)}")
            )
            return None

    def update_legacy_artikel_ids(self, legacy_products_df, dry_run=False):
        """
        Update the legacy_artikel_id field for existing VariantProduct records.
        
        Args:
            legacy_products_df: DataFrame containing legacy product data
            dry_run: If True, don't make any changes
        """
        if legacy_products_df is None or legacy_products_df.empty:
            self.stdout.write(self.style.ERROR("No legacy product data available"))
            return
        
        # Create a mapping from SKU to ID
        sku_to_id_map = {}
        legacy_sku_to_id_map = {}
        
        for _, row in legacy_products_df.iterrows():
            if pd.notna(row['Nummer']):
                sku_to_id_map[row['Nummer']] = row['UID']
            if pd.notna(row['alteNummer']):
                legacy_sku_to_id_map[row['alteNummer']] = row['UID']
        
        self.stdout.write(
            f"Created mapping for {len(sku_to_id_map)} SKUs and "
            f"{len(legacy_sku_to_id_map)} legacy SKUs"
        )
        
        # Get all products that need updating
        products = VariantProduct.objects.filter(legacy_artikel_id__isnull=True)
        self.stdout.write(f"Found {products.count()} products without legacy_artikel_id")
        
        updated_count = 0
        not_found_count = 0
        
        if not dry_run:
            with transaction.atomic():
                for product in products:
                    artikel_id = None
                    
                    # Try to match by SKU first
                    if product.sku in sku_to_id_map:
                        artikel_id = sku_to_id_map[product.sku]
                    # Then try to match by legacy_sku
                    elif product.legacy_sku and product.legacy_sku in legacy_sku_to_id_map:
                        artikel_id = legacy_sku_to_id_map[product.legacy_sku]
                    
                    if artikel_id:
                        product.legacy_artikel_id = artikel_id
                        product.save(update_fields=['legacy_artikel_id'])
                        updated_count += 1
                        if updated_count % 100 == 0:
                            self.stdout.write(f"Updated {updated_count} products so far")
                    else:
                        not_found_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Could not find legacy ID for product {product.sku} "
                                f"(legacy_sku: {product.legacy_sku})"
                            )
                        )
        else:
            # Dry run - just count how many would be updated
            for product in products:
                artikel_id = None
                
                # Try to match by SKU first
                if product.sku in sku_to_id_map:
                    artikel_id = sku_to_id_map[product.sku]
                # Then try to match by legacy_sku
                elif product.legacy_sku and product.legacy_sku in legacy_sku_to_id_map:
                    artikel_id = legacy_sku_to_id_map[product.legacy_sku]
                
                if artikel_id:
                    updated_count += 1
                    if updated_count % 100 == 0:
                        self.stdout.write(f"Would update {updated_count} products so far")
                else:
                    not_found_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"{'Would update' if dry_run else 'Updated'} "
                              f"{updated_count} products with legacy_artikel_id")
        )
        self.stdout.write(
            self.style.WARNING(f"Could not find legacy ID for {not_found_count} products")
        ) 