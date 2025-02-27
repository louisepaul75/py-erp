import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from pyerp.products.models import ParentProduct, ProductCategory
from wsz_api.getTable import fetch_data_from_api


class Command(BaseCommand):
    help = 'Import Artikel_Familie records as parent products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of records to import',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip existing products instead of updating them',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to the database',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        skip_existing = options.get('skip_existing', False)
        dry_run = options.get('dry_run', False)

        created, updated, skipped = self.import_artikel_familie(
            limit=limit,
            skip_existing=skip_existing,
            dry_run=dry_run
        )

        self.stdout.write(self.style.SUCCESS(
            f"Import completed: {created} created, {updated} updated, {skipped} skipped"
        ))

    def import_artikel_familie(self, limit=None, skip_existing=False, dry_run=False):
        """
        Import Artikel_Familie records as parent products.
        
        Args:
            limit (int, optional): Limit the number of records to import. Defaults to None (no limit).
            skip_existing (bool, optional): Skip existing products instead of updating them. Defaults to False.
            dry_run (bool, optional): If True, don't save changes to the database. Defaults to False.
            
        Returns:
            tuple: (created_count, updated_count, skipped_count)
        """
        self.stdout.write("Fetching Artikel_Familie data...")
        try:
            # Fetch data from the 4D database
            df = fetch_data_from_api('Artikel_Familie', top=10000, new_data_only=False)
            
            if df is None or len(df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from Artikel_Familie table"))
                return (0, 0, 0)
            
            # Limit records if specified
            if limit is not None and limit > 0:
                df = df.head(limit)
            
            self.stdout.write(f"Processing {len(df)} Artikel_Familie records...")
            
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
                        # Get essential data
                        familie_id = row['__KEY']
                        product_name = row['Bezeichnung'] if pd.notna(row['Bezeichnung']) else "Unnamed Product Family"
                        nummer = int(row['Nummer']) if pd.notna(row['Nummer']) else None
                        is_active = bool(row['aktiv']) if pd.notna(row['aktiv']) else True
                        
                        # Generate a product SKU based on the nummer field
                        sku = f"{nummer}" if nummer is not None else f"FAMILIE-{familie_id[:8]}"
                        
                        # Get additional attributes if available
                        description = None
                        if pd.notna(row.get('Beschreibung')):
                            try:
                                # Handle the multilingual description object
                                if isinstance(row['Beschreibung'], dict) and 'DE' in row['Beschreibung']:
                                    description = row['Beschreibung']['DE']
                                elif isinstance(row['Beschreibung'], str):
                                    description = row['Beschreibung']
                            except:
                                # Fall back if parsing fails
                                description = str(row['Beschreibung'])
                        
                        # Get physical attributes if available
                        weight = int(row['Gewicht']) if pd.notna(row.get('Gewicht')) else None
                        width = float(row['Masse_Breite']) if pd.notna(row.get('Masse_Breite')) else None
                        height = float(row['Masse_Hoehe']) if pd.notna(row.get('Masse_Hoehe')) else None
                        depth = float(row['Masse_Tiefe']) if pd.notna(row.get('Masse_Tiefe')) else None
                        
                        # Format dimensions if available
                        dimensions = None
                        if width is not None and height is not None and depth is not None:
                            dimensions = f"{width}x{height}x{depth}"
                        
                        # Get category if available
                        category = None
                        if pd.notna(row.get('Gruppe')):
                            try:
                                category = ProductCategory.objects.get(code=row['Gruppe'])
                            except ProductCategory.DoesNotExist:
                                pass
                        
                        # Check if product exists
                        try:
                            parent_product = ParentProduct.objects.get(legacy_id=familie_id)
                            exists = True
                        except ParentProduct.DoesNotExist:
                            try:
                                parent_product = ParentProduct.objects.get(sku=sku)
                                exists = True
                            except ParentProduct.DoesNotExist:
                                parent_product = ParentProduct(legacy_id=familie_id)
                                exists = False
                        
                        # Skip if requested and product exists
                        if exists and skip_existing:
                            skipped += 1
                            self.stdout.write(f"Skipping existing product: {sku} - {product_name}")
                            continue
                        
                        # Update product fields
                        parent_product.sku = sku
                        parent_product.base_sku = sku  # For parent products, base_sku is the same as sku
                        parent_product.name = product_name
                        parent_product.description = description
                        parent_product.is_active = is_active
                        parent_product.weight = weight
                        parent_product.dimensions = dimensions
                        parent_product.category = category
                        
                        # Save the product if not a dry run
                        if not dry_run:
                            parent_product.save()
                        
                        # Update counts
                        if exists:
                            updated += 1
                            self.stdout.write(f"Updated parent product: {sku} - {product_name}")
                        else:
                            created += 1
                            self.stdout.write(f"Created parent product: {sku} - {product_name}")
                    
                    except Exception as e:
                        errors += 1
                        self.stdout.write(self.style.ERROR(f"Error processing record {index}: {str(e)}"))
                
                # Commit the transaction if not a dry run
                if not dry_run:
                    transaction.commit()
                    self.stdout.write(self.style.SUCCESS(f"Committed changes to database"))
                else:
                    self.stdout.write(self.style.WARNING(f"DRY RUN - No changes were saved to the database"))
                
                # Return counts
                return (created, updated, skipped)
            
            except Exception as e:
                # Rollback the transaction if not a dry run
                if not dry_run:
                    transaction.rollback()
                self.stdout.write(self.style.ERROR(f"Error during import, rolling back: {str(e)}"))
                return (0, 0, 0)
            
            finally:
                # Reset autocommit
                if not dry_run:
                    transaction.set_autocommit(True)
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data: {str(e)}"))
            return (0, 0, 0) 