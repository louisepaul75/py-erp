import pandas as pd  # noqa: F401
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify  # noqa: F401
from pyerp.products.models import ParentProduct, ProductCategory
from wsz_api.getTable import fetch_data_from_api


class Command(BaseCommand):
    help = 'Import Artikel_Familie records as parent products'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            '--limit',  # noqa: E128
            type=int,  # noqa: F841
  # noqa: F841
            help='Limit the number of records to import',  # noqa: F841
        )
        parser.add_argument(
            '--skip-existing',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Skip existing products instead of updating them',  # noqa: F841
        )
        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Perform a dry run without saving to the database',  # noqa: F841
  # noqa: F841
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        skip_existing = options.get('skip_existing', False)
        dry_run = options.get('dry_run', False)

        created, updated, skipped = self.import_artikel_familie(
            limit=limit,  # noqa: E128
            skip_existing=skip_existing,
            dry_run=dry_run
        )

        self.stdout.write(self.style.SUCCESS(
            f"Import completed: {created} created, {updated} updated, {skipped} skipped"  # noqa: E501
        ))

    def import_artikel_familie(self, limit=None, skip_existing=False, dry_run=False):  # noqa: E501
        """
        Import Artikel_Familie records as parent products.

        Args:
            limit (int, optional): Limit the number of records to import. Defaults to None (no limit).  # noqa: E501
            skip_existing (bool, optional): Skip existing products instead of updating them. Defaults to False.  # noqa: E501
            dry_run (bool, optional): If True, don't save changes to the database. Defaults to False.  # noqa: E501

        Returns:
            tuple: (created_count, updated_count, skipped_count)
        """
        self.stdout.write("Fetching Artikel_Familie data...")
        try:
            # Fetch data from the 4D database
            df = fetch_data_from_api('Artikel_Familie', top=10000, new_data_only=False)  # noqa: E501

            if df is None or len(df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from Artikel_Familie table"))  # noqa: E501
                return (0, 0, 0)

            # Limit records if specified
            if limit is not None and limit > 0:
                df = df.head(limit)

            self.stdout.write(f"Processing {len(df)} Artikel_Familie records...")  # noqa: E501

            # Track counts
            created = 0
            updated = 0
            skipped = 0
            errors = 0  # noqa: F841

            # Use a transaction to ensure all-or-nothing
            if not dry_run:
                transaction.set_autocommit(False)

            try:
                # Process each record
                for index, row in df.iterrows():
                    try:
                        # Get essential data
                        familie_id = row['__KEY']
                        product_name = row['Bezeichnung'] if pd.notna(row['Bezeichnung']) else "Unnamed Product Family"  # noqa: E501
                        nummer = int(row['Nummer']) if pd.notna(row['Nummer']) else None  # noqa: E501
                        is_active = bool(row['aktiv']) if pd.notna(row['aktiv']) else True  # noqa: E501

                        # Generate a product SKU based on the nummer field
                        sku = f"{nummer}" if nummer is not None else f"FAMILIE-{familie_id[:8]}"  # noqa: E501

                        # Get additional attributes if available
                        description = None
                        if pd.notna(row.get('Beschreibung')):
                            try:
                                # Handle the multilingual description object
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

                        # Check if product exists
                        try:
                            parent_product = ParentProduct.objects.get(legacy_id=familie_id)  # noqa: E501
                            exists = True
                        except ParentProduct.DoesNotExist:
                            try:
                                parent_product = ParentProduct.objects.get(sku=sku)  # noqa: E501
                                exists = True
                            except ParentProduct.DoesNotExist:
                                parent_product = ParentProduct(legacy_id=familie_id)  # noqa: E501
                                exists = False

                        # Skip if requested and product exists
                        if exists and skip_existing:
                            skipped += 1
                            self.stdout.write(f"Skipping existing product: {sku} - {product_name}")  # noqa: E501
                            continue

                        # Update product fields
                        parent_product.sku = sku
                        parent_product.base_sku = sku
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

                        # Update counts
                        if exists:
                            updated += 1
                            self.stdout.write(f"Updated parent product: {sku} - {product_name}")  # noqa: E501
                        else:
                            created += 1
                            self.stdout.write(f"Created parent product: {sku} - {product_name}")  # noqa: E501

                    except Exception as e:
                        errors += 1
                        self.stdout.write(self.style.ERROR(f"Error processing record {index}: {str(e)}"))  # noqa: E501

                # Commit the transaction if not a dry run
                if not dry_run:
                    transaction.commit()
                    self.stdout.write(self.style.SUCCESS("Committed changes to database"))  # noqa: E501
                else:
                    self.stdout.write(self.style.WARNING("DRY RUN - No changes were saved to the database"))  # noqa: E501

                # Return counts
                return (created, updated, skipped)

            except Exception as e:
                # Rollback the transaction if not a dry run
                if not dry_run:
                    transaction.rollback()
                self.stdout.write(self.style.ERROR(f"Error during import, rolling back: {str(e)}"))  # noqa: E501
                return (0, 0, 0)

            finally:
                # Reset autocommit
                if not dry_run:
                    transaction.set_autocommit(True)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data: {str(e)}"))  # noqa: E501
            return (0, 0, 0)
