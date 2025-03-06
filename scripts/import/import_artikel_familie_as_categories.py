"""
Script to import Artikel_Familie data as product categories.
This script fetches data from the legacy 4D system and creates/updates
product categories in the Django database.
"""

import os
import sys
import traceback

# Add the project root to the path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Setup Django environment
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings.development")
django.setup()

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r"C:\Users\Joan-Admin\PycharmProjects\WSZ_api"
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    import pandas as pd

    # Import Django models
    from django.db import transaction
    from django.utils.text import slugify

    from pyerp.products.models import ProductCategory
    from wsz_api.getTable import fetch_data_from_api

    def import_artikel_familie_as_categories(
        limit=None,
        update_existing=True,
        dry_run=False,
    ):
        """
        Import Artikel_Familie records as product categories.

        Args:
            limit (int, optional): Limit the number of records to import. Defaults to None (no limit).
            update_existing (bool, optional): Update existing categories if they already exist. Defaults to True.
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
                        family_name = (
                            row["Bezeichnung"]
                            if pd.notna(row["Bezeichnung"])
                            else "Unnamed Family"
                        )
                        nummer = int(row["Nummer"]) if pd.notna(row["Nummer"]) else None
                        active = bool(row["aktiv"]) if pd.notna(row["aktiv"]) else True

                        # Generate a slug
                        slug = slugify(family_name)

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

                        # Check if category exists
                        try:
                            category = ProductCategory.objects.get(legacy_id=familie_id)
                            exists = True
                        except ProductCategory.DoesNotExist:
                            category = ProductCategory(legacy_id=familie_id)
                            exists = False

                        # Update or create category
                        if not exists or update_existing:
                            # Set category attributes
                            category.name = family_name
                            category.slug = slug
                            category.description = description
                            category.is_active = active

                            # Set reference fields
                            category.legacy_id = familie_id
                            category.legacy_nummer = nummer

                            # Save category if not in dry run mode
                            if not dry_run:
                                category.save()

                            if exists:
                                updated += 1
                                print(
                                    f"Updated category '{family_name}' (ID: {familie_id})",
                                )
                            else:
                                created += 1
                                print(
                                    f"Created category '{family_name}' (ID: {familie_id})",
                                )
                        else:
                            skipped += 1
                            print(
                                f"Skipped existing category '{family_name}' (ID: {familie_id})",
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

    if __name__ == "__main__":
        import argparse

        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="Import Artikel_Familie data as product categories",
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
            help="Update existing categories",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without saving to the database",
        )

        args = parser.parse_args()

        # Run the import
        created, updated, skipped = import_artikel_familie_as_categories(
            limit=args.limit if args.limit > 0 else None,
            update_existing=args.update,
            dry_run=args.dry_run,
        )

        print(
            f"\nImport completed. Created: {created}, Updated: {updated}, Skipped: {skipped}",
        )

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print(
        "Please make sure the required packages are installed and the module paths are correct.",
    )
