"""
Management command to fix SKU and legacy_id mappings in the parent product table by importing from legacy Artikel_Familie.
"""

import logging
import os
import sys
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from pyerp.products.models import ParentProduct

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

# Now import from wsz_api
from wsz_api.getTable import fetch_data_from_api

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix SKU and legacy_id fields for parent products based on Artikel_Familie data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to the database'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of products to process'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of parents to process in each transaction batch'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        batch_size = options['batch_size']

        self.stdout.write(self.style.NOTICE('Starting parent product SKU mapping fix from Artikel_Familie...'))
        
        # Get all parent products
        parent_products = ParentProduct.objects.all()
        
        if limit:
            parent_products = parent_products[:limit]
        
        total_parents = parent_products.count()
        self.stdout.write(self.style.SUCCESS(f'Found {total_parents} parent products to check'))
        
        # Fetch data from legacy Artikel_Familie table using wsz_api
        self.stdout.write(self.style.NOTICE('Fetching Artikel_Familie data from legacy ERP...'))
        try:
            # Use wsz_api to fetch the data
            artikel_familie_df = fetch_data_from_api('Artikel_Familie', top=10000, new_data_only=False)
            
            if artikel_familie_df is None or len(artikel_familie_df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from Artikel_Familie table"))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Fetched {len(artikel_familie_df)} records from Artikel_Familie'))
            
            # Create mappings by different fields for flexible matching
            legacy_data_by_id = {}       # Key is the __KEY value
            legacy_data_by_nummer = {}   # Key is the Nummer value
            legacy_data_by_oldart = {}   # Key is the oldArtKalk value
            
            for index, row in artikel_familie_df.iterrows():
                id_val = row['__KEY']
                nummer_val = str(int(row['Nummer'])) if pd.notna(row.get('Nummer')) else None
                oldart_val = str(row['oldArtKalk']) if pd.notna(row.get('oldArtKalk')) else None
                
                record = {
                    'id': id_val,
                    'nummer': nummer_val, 
                    'oldArtKalk': oldart_val
                }
                
                if id_val:
                    legacy_data_by_id[id_val] = record
                
                if nummer_val:
                    legacy_data_by_nummer[nummer_val] = record
                
                if oldart_val:
                    legacy_data_by_oldart[oldart_val] = record
            
            self.stdout.write(self.style.SUCCESS(
                f'Processed {len(legacy_data_by_id)} records from Artikel_Familie '
                f'({len(legacy_data_by_nummer)} with valid Nummer values, '
                f'{len(legacy_data_by_oldart)} with valid oldArtKalk values)'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data from Artikel_Familie API: {str(e)}"))
            return
        
        # Track statistics
        stats = {
            'total': total_parents,
            'fixed': 0,
            'already_correct': 0,
            'errors': 0
        }
        
        # Process parents in batches
        for i in range(0, total_parents, batch_size):
            batch = parent_products[i:i+batch_size]
            self.stdout.write(self.style.NOTICE(f'Processing batch {i//batch_size + 1} of {(total_parents + batch_size - 1)//batch_size}'))
            
            # Process each parent product in this batch
            with transaction.atomic():
                for parent in batch:
                    try:
                        # Print current values
                        self.stdout.write(f"Checking parent: ID={parent.id}, SKU={parent.sku}, Legacy ID={parent.legacy_id}")
                        
                        # Try to find a match in the legacy data using multiple matching strategies
                        legacy_record = None
                        match_type = None
                        
                        # Strategy 1: Try to match by legacy_id against ID
                        if parent.legacy_id and parent.legacy_id in legacy_data_by_id:
                            legacy_record = legacy_data_by_id[parent.legacy_id]
                            match_type = "legacy_id_to_id"
                        
                        # Strategy 2: Try to match by SKU against Nummer
                        elif parent.sku and parent.sku in legacy_data_by_nummer:
                            legacy_record = legacy_data_by_nummer[parent.sku]
                            match_type = "sku_to_nummer"
                        
                        # Strategy 3: Try to match by legacy_id against Nummer (handling swapped fields)
                        elif parent.legacy_id and parent.legacy_id in legacy_data_by_nummer:
                            legacy_record = legacy_data_by_nummer[parent.legacy_id]
                            match_type = "legacy_id_to_nummer"
                        
                        # Strategy 4: Try to match by SKU against ID (handling swapped fields)
                        elif parent.sku and parent.sku in legacy_data_by_id:
                            legacy_record = legacy_data_by_id[parent.sku]
                            match_type = "sku_to_id"
                            
                        # Strategy 5: Try to match by SKU against oldArtKalk
                        elif parent.sku and parent.sku in legacy_data_by_oldart:
                            legacy_record = legacy_data_by_oldart[parent.sku]
                            match_type = "sku_to_oldart"
                            
                        # Strategy 6: Try to match by legacy_id against oldArtKalk
                        elif parent.legacy_id and parent.legacy_id in legacy_data_by_oldart:
                            legacy_record = legacy_data_by_oldart[parent.legacy_id]
                            match_type = "legacy_id_to_oldart"
                        
                        # If we found a match
                        if legacy_record:
                            new_sku = legacy_record['nummer']
                            new_legacy_id = legacy_record['oldArtKalk'] or legacy_record['id']
                            
                            # Check if update is needed
                            if parent.sku != new_sku or parent.legacy_id != new_legacy_id:
                                old_sku = parent.sku
                                old_legacy_id = parent.legacy_id
                                
                                self.stdout.write(self.style.WARNING(
                                    f"Match found using strategy '{match_type}' for parent ID={parent.id}\n"
                                    f"  - Changing SKU from {old_sku} to {new_sku}\n"
                                    f"  - Changing legacy ID from {old_legacy_id} to {new_legacy_id}"
                                ))
                                
                                if not dry_run:
                                    parent.sku = new_sku
                                    parent.legacy_id = new_legacy_id
                                    parent.save()
                                
                                stats['fixed'] += 1
                            else:
                                self.stdout.write(self.style.SUCCESS(
                                    f"Parent ID={parent.id} already has correct SKU and legacy ID"
                                ))
                                stats['already_correct'] += 1
                        else:
                            self.stdout.write(self.style.ERROR(
                                f"No matching record found in Artikel_Familie for parent ID={parent.id}, SKU={parent.sku}, Legacy ID={parent.legacy_id}"
                            ))
                            stats['errors'] += 1
                    
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"Error processing parent ID={parent.id}: {str(e)}"
                        ))
                        stats['errors'] += 1
            
            # Commit or rollback the batch transaction
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes were saved to the database for this batch"))
                transaction.set_rollback(True)
        
        # Print summary
        self.stdout.write("\nFix summary:")
        self.stdout.write(f"Total parents: {stats['total']}")
        self.stdout.write(f"Fixed: {stats['fixed']}")
        self.stdout.write(f"Already correct: {stats['already_correct']}")
        self.stdout.write(f"Errors: {stats['errors']}")
        
        self.stdout.write("\nNOTE: Fixing parent SKUs may affect variant-parent relationships. You may need to update variant products to maintain proper relationships.")
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Run 'python manage.py fix_variant_parent_relationships' to update variant-parent relationships ")
        self.stdout.write("2. Verify the changes with 'python manage.py test_product_split'") 