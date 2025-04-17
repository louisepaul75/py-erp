"""
Script to import Artikel_Familie data as parent products.
This script fetches data from the legacy 4D system and creates/updates
parent products in the Django database based on the Artikel_Familie records.
"""

import os
import sys
import traceback

# Add the project root to the path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Setup Django environment
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r"C:\Users\Joan-Admin\PycharmProjects\WSZ_api"
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    from decimal import Decimal

    import pandas as pd

    # Import Django models
    from django.db import transaction
    from django.utils.text import slugify

    from pyerp.products.models import Product
    from wsz_api.getTable import fetch_data_from_api

    def import_artikel_familie_as_parent_products(
        limit=None,
        update_existing=True,
        dry_run=False,
    ):
        """
        Import Artikel_Familie records as parent products.

        Args:
            limit (int, optional): Limit the number of records to import. Defaults to None (no limit).
            update_existing (bool, optional): Update existing parents if they already exist. Defaults to True.
            dry_run (bool, optional): If True, don't save changes to the database. Defaults to False.

        Returns:
            tuple: (created_count, updated_count, skipped_count)
        """
        print("Fetching Artikel_Familie data...")
        try:
            # Fetch data from the 4D database
            df = fetch_data_from_api("Artikel_Familie", top=10000, new_data_only=False)

            if df is None or len(df) == 0:
                print("No data returned from Artikel_Familie table")
                return (0, 0, 0)

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
                        # Get essential data
                        familie_id = row["__KEY"]
                        product_name = (
                            row["Bezeichnung"]
                            if pd.notna(row["Bezeichnung"])
                            else "Unnamed Product Family"
                        )
                        nummer = int(row["Nummer"]) if pd.notna(row["Nummer"]) else None
                        is_active = (
                            bool(row["aktiv"]) if pd.notna(row["aktiv"]) else True
                        )

                        # Generate a product SKU based on the nummer field
                        sku = (
                            f"{nummer}"
                            if nummer is not None
                            else f"FAMILIE-{familie_id[:8]}"
                        )

                        # Generate a slug
                        slug = slugify(product_name)

                        # Get additional attributes if available
                        description = None
                        if pd.notna(row.get("Beschreibung")):
                            try:
                                # Handle the multilingual description object
                                if (
                                    isinstance(row["Beschreibung"], dict)
                                    and "DE" in row["Beschreibung"]
                                ):
                                    description = row["Beschreibung"]["DE"]
                                elif isinstance(row["Beschreibung"], str):
                                    description = row["Beschreibung"]
                            except:
                                # Fall back if parsing fails
                                description = str(row["Beschreibung"])

                        # Get physical attributes if available
                        weight = (
                            int(row["Gewicht"])
                            if pd.notna(row.get("Gewicht"))
                            else None
                        )
                        width = (
                            float(row["Masse_Breite"])
                            if pd.notna(row.get("Masse_Breite"))
                            else None
                        )
                        height = (
                            float(row["Masse_Hoehe"])
                            if pd.notna(row.get("Masse_Hoehe"))
                            else None
                        )
                        depth = (
                            float(row["Masse_Tiefe"])
                            if pd.notna(row.get("Masse_Tiefe"))
                            else None
                        )

                        # Check if parent product exists
                        try:
                            product = Product.objects.get(legacy_id=familie_id)
                            exists = True
                        except Product.DoesNotExist:
                            product = Product(legacy_id=familie_id)
                            exists = False

                        # Update or create parent product
                        if not exists or update_existing:
                            # Set product attributes
                            product.name = product_name
                            product.sku = sku
                            product.slug = slug
                            product.description = description
                            product.is_active = is_active

                            # Set physical attributes if available
                            if weight is not None:
                                product.weight = weight
                            if width is not None:
                                product.width = width
                            if height is not None:
                                product.height = height
                            if depth is not None:
                                product.depth = depth

                            # Set as a parent product
                            product.is_parent = True
                            product.is_variant = False

                            # Set reference fields
                            product.legacy_id = familie_id
                            product.legacy_nummer = nummer

                            # Save product if not in dry run mode
                            if not dry_run:
                                product.save()

                            if exists:
                                updated += 1
                                print(
                                    f"Updated parent product '{product_name}' (ID: {familie_id}, SKU: {sku})",
                                )
                            else:
                                created += 1
                                print(
                                    f"Created parent product '{product_name}' (ID: {familie_id}, SKU: {sku})",
                                )
                        else:
                            skipped += 1
                            print(
                                f"Skipped existing parent product '{product_name}' (ID: {familie_id})",
                            )

                    except Exception as e:
                        errors += 1
                        print(
                            f"Error processing record {index} ({row.get('__KEY', 'unknown')}): {e!s}",
                        )
                        traceback.print_exc()

                # Commit transaction if not in dry run mode
                if not dry_run:
                    transaction.commit()
                    print(
                        f"Transaction committed. Created: {created}, Updated: {updated}, Skipped: {skipped}, Errors: {errors}",
                    )
                else:
                    print(
                        f"Dry run completed. Would have: Created: {created}, Updated: {updated}, Skipped: {skipped}, Errors: {errors}",
                    )

                return (created, updated, skipped)

            except Exception as e:
                # Rollback in case of error if not in dry run mode
                if not dry_run:
                    transaction.rollback()
                print(f"Error during import, transaction rolled back: {e!s}")
                traceback.print_exc()
                return (0, 0, 0)

            finally:
                # Reset autocommit setting if not in dry run mode
                if not dry_run:
                    transaction.set_autocommit(True)

        except Exception as e:
            print(f"Error fetching or processing Artikel_Familie data: {e!s}")
            traceback.print_exc()
            return (0, 0, 0)

    def update_variant_parent_relationships(dry_run=False):
        """
        Update the parent-child relationships between product variants and parent products.
        This links variants (from Artikel_Variante) to their parents (from Artikel_Familie)
        using the Familie_ field.

        Args:
            dry_run (bool, optional): If True, don't save changes to the database. Defaults to False.

        Returns:
            int: Number of updated relationships
        """
        print("Fetching Artikel_Variante data to update parent-child relationships...")
        try:
            # Fetch data from the 4D database
            df = fetch_data_from_api("Artikel_Variante", top=10000, new_data_only=False)

            if df is None or len(df) == 0:
                print("No data returned from Artikel_Variante table")
                return 0

            print(f"Retrieved {len(df)} records from Artikel_Variante")

            # Track count of updated relationships
            updated = 0
            errors = 0

            # Use a transaction to ensure all-or-nothing
            if not dry_run:
                transaction.set_autocommit(False)

            try:
                # Process each record
                for index, row in df.iterrows():
                    try:
                        # Get the variant and parent IDs
                        variant_id = row["__KEY"]
                        famille_id = (
                            row["Familie_"] if pd.notna(row.get("Familie_")) else None
                        )

                        if not famille_id:
                            continue  # Skip if no parent ID

                        # Find the variant product
                        try:
                            variant = Product.objects.get(legacy_id=variant_id)
                        except Product.DoesNotExist:
                            print(
                                f"Variant product with legacy_id {variant_id} not found",
                            )
                            continue

                        # Find the parent product
                        try:
                            parent = Product.objects.get(legacy_id=famille_id)
                        except Product.DoesNotExist:
                            print(
                                f"Parent product with legacy_id {famille_id} not found",
                            )
                            continue

                        # Update the parent-child relationship
                        if variant.parent != parent:
                            variant.parent = parent
                            variant.is_variant = True

                            # Save the updates if not in dry run mode
                            if not dry_run:
                                variant.save()

                            updated += 1
                            print(
                                f"Updated variant '{variant.name}' (SKU: {variant.sku}) with parent '{parent.name}' (SKU: {parent.sku})",
                            )

                    except Exception as e:
                        errors += 1
                        print(
                            f"Error updating relationship for variant {row.get('__KEY', 'unknown')}: {e!s}",
                        )
                        traceback.print_exc()

                # Commit transaction if not in dry run mode
                if not dry_run:
                    transaction.commit()
                    print(
                        f"Transaction committed. Updated {updated} parent-child relationships, Errors: {errors}",
                    )
                else:
                    print(
                        f"Dry run completed. Would have updated {updated} parent-child relationships, Errors: {errors}",
                    )

                return updated

            except Exception as e:
                # Rollback in case of error if not in dry run mode
                if not dry_run:
                    transaction.rollback()
                print(
                    f"Error during relationship updates, transaction rolled back: {e!s}",
                )
                traceback.print_exc()
                return 0

            finally:
                # Reset autocommit setting if not in dry run mode
                if not dry_run:
                    transaction.set_autocommit(True)

        except Exception as e:
            print(f"Error fetching or processing Artikel_Variante data: {e!s}")
            traceback.print_exc()
            return 0

    if __name__ == "__main__":
        import argparse

        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="Import Artikel_Familie data as parent products",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit the number of records to import",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing parent products",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without saving to the database",
        )
        parser.add_argument(
            "--update-relationships",
            action="store_true",
            help="Update parent-child relationships",
        )

        args = parser.parse_args()

        # Run the import
        if not args.update_relationships:
            created, updated, skipped = import_artikel_familie_as_parent_products(
                limit=args.limit if args.limit > 0 else None,
                update_existing=args.update,
                dry_run=args.dry_run,
            )

            print(
                f"\nImport completed. Created: {created}, Updated: {updated}, Skipped: {skipped}",
            )
        else:
            updated = update_variant_parent_relationships(dry_run=args.dry_run)
            print(f"\nRelationship updates completed. Updated: {updated}")

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print(
        "Please make sure the required packages are installed and the module paths are correct.",
    )
