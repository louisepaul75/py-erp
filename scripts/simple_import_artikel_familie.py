#!/usr/bin/env python
"""
Script to import Artikel_Familie records as parent products with minimal columns.
Only imports: __KEY (as legacy_id), UID, Bezeichnung (as name), and Nummer (as sku).
"""
import os
import sys
import django
import pandas as pd

# Add the project root to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

# Now we can import Django models
from django.db import transaction
from pyerp.products.models import ParentProduct

# Add the WSZ_api path to the Python path
WSZ_API_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wsz_api')
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    # Import the WSZ_api modules
    from wsz_api.getTable import fetch_data_from_api
except ImportError as e:
    print(f"Failed to import WSZ_api modules: {e}")
    sys.exit(1)

def import_artikel_familie(limit=None, skip_existing=False, dry_run=False):
    """
    Import Artikel_Familie records as parent products with minimal columns.
    
    Args:
        limit (int, optional): Limit the number of records to import. Defaults to None (no limit).
        skip_existing (bool, optional): Skip existing products instead of updating them. Defaults to False.
        dry_run (bool, optional): If True, don't save changes to the database. Defaults to False.
        
    Returns:
        tuple: (created_count, updated_count, skipped_count)
    """
    print("Fetching Artikel_Familie data...")
    try:
        # Fetch data from the 4D database
        df = fetch_data_from_api('Artikel_Familie', top=10000, new_data_only=False)
        
        if df is None or len(df) == 0:
            print("No data returned from Artikel_Familie table")
            return (0, 0, 0)
        
        # Select ONLY the required columns (if they exist)
        required_columns = ['__KEY', 'UID', 'Bezeichnung', 'Nummer']
        for col in required_columns:
            if col not in df.columns:
                print(f"Warning: Required column '{col}' not found in data")
        
        # Limit records if specified
        if limit is not None and limit > 0:
            df = df.head(limit)
        
        print(f"Processing {len(df)} Artikel_Familie records...")
        
        # Track counts
        created = 0
        updated = 0
        skipped = 0
        errors = 0
        
        # Use a transaction to ensure all-or-nothing
        if not dry_run:
            transaction.set_autocommit(False)
        
        try:
            # Process each record
            for index, row in df.iterrows():
                try:
                    # Get ONLY the specified columns
                    key = row['__KEY'] if '__KEY' in row and pd.notna(row['__KEY']) else None
                    uid = row['UID'] if 'UID' in row and pd.notna(row['UID']) else None
                    product_name = row['Bezeichnung'] if 'Bezeichnung' in row and pd.notna(row['Bezeichnung']) else "Unnamed Product Family"
                    nummer = row['Nummer'] if 'Nummer' in row and pd.notna(row['Nummer']) else None
                    
                    # Skip if no __KEY available
                    if not key:
                        skipped += 1
                        print(f"Skipping family with no __KEY: {index}")
                        continue
                    
                    # Generate a product SKU based on the nummer field
                    sku = f"{nummer}" if nummer is not None else f"FAMILIE-{key[:8]}"
                    
                    # Check if product exists
                    try:
                        parent_product = ParentProduct.objects.get(legacy_id=key)
                        exists = True
                    except ParentProduct.DoesNotExist:
                        try:
                            parent_product = ParentProduct.objects.get(sku=sku)
                            exists = True
                        except ParentProduct.DoesNotExist:
                            parent_product = ParentProduct(legacy_id=key)
                            exists = False
                    
                    # Skip if requested and product exists
                    if exists and skip_existing:
                        skipped += 1
                        print(f"Skipping existing product: {sku} - {product_name}")
                        continue
                    
                    # Update ONLY the essential product fields
                    parent_product.sku = sku
                    parent_product.base_sku = sku  # For parent products, base_sku is the same as sku
                    parent_product.name = product_name
                    parent_product.is_active = True  # Default to active
                    parent_product.legacy_id = key
                    parent_product.legacy_uid = uid
                    
                    # Print what would be saved in dry run mode
                    if dry_run:
                        print(f"Would {'update' if exists else 'create'} parent product: {sku} - {product_name}")
                        if exists:
                            updated += 1
                        else:
                            created += 1
                        continue
                    
                    # Save the product
                    parent_product.save()
                    
                    # Update counts
                    if exists:
                        updated += 1
                        print(f"Updated parent product: {sku} - {product_name}")
                    else:
                        created += 1
                        print(f"Created parent product: {sku} - {product_name}")
                
                except Exception as e:
                    errors += 1
                    print(f"Error processing record {index}: {str(e)}")
            
            # Commit the transaction if not a dry run
            if not dry_run:
                transaction.commit()
                print(f"Committed changes to database")
            else:
                print(f"DRY RUN - No changes were saved to the database")
            
            # Print final counts
            print(f"\nImport summary:")
            print(f"Total records: {len(df)}")
            print(f"Created: {created}")
            print(f"Updated: {updated}")
            print(f"Skipped: {skipped}")
            print(f"Errors: {errors}")
            
            # Return counts
            return (created, updated, skipped)
        
        except Exception as e:
            # Rollback the transaction if not a dry run
            if not dry_run:
                transaction.rollback()
            print(f"Error during import, rolling back: {str(e)}")
            return (0, 0, 0)
        
        finally:
            # Reset autocommit
            if not dry_run:
                transaction.set_autocommit(True)
    
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return (0, 0, 0)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Artikel_Familie with minimal columns')
    parser.add_argument('--limit', type=int, help='Limit the number of records to import')
    parser.add_argument('--skip-existing', action='store_true', help='Skip existing products')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without saving')
    
    args = parser.parse_args()
    
    created, updated, skipped = import_artikel_familie(
        limit=args.limit,
        skip_existing=args.skip_existing,
        dry_run=args.dry_run
    )
    
    print(f"Import completed: {created} created, {updated} updated, {skipped} skipped") 