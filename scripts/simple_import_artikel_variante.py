#!/usr/bin/env python
"""
Script to import Artikel_Variante records as variant products with minimal columns.
Only imports: __KEY, UID, Familie_, Nummer (as sku), and alteNummer (as legacy_sku).
"""

import os
import sys

import django
import pandas as pd

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now we can import Django models
from django.db import transaction

from pyerp.products.models import ParentProduct, VariantProduct

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r"C:\Users\Joan-Admin\PycharmProjects\WSZ_api"
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    # Import the WSZ_api modules
    from wsz_api.getTable import fetch_data_from_api
except ImportError as e:
    print(f"Failed to import WSZ_api modules: {e}")
    sys.exit(1)


def import_artikel_variante(limit=None, skip_existing=False, dry_run=False):
    """
    Import Artikel_Variante records as variant products with minimal columns.

    Args:
        limit (int, optional): Limit the number of records to import. Defaults to None (no limit).
        skip_existing (bool, optional): Skip existing products instead of updating them. Defaults to False.
        dry_run (bool, optional): If True, don't save changes to the database. Defaults to False.

    Returns:
        tuple: (created_count, updated_count, skipped_count, parent_not_found_count)
    """
    print("Fetching Artikel_Variante data...")
    try:
        # Fetch data from the 4D database
        df = fetch_data_from_api("Artikel_Variante", top=limit, new_data_only=False)

        if df is None or len(df) == 0:
            print("No data returned from Artikel_Variante table")
            return (0, 0, 0, 0)

        # Select ONLY the required columns (if they exist)
        required_columns = ["__KEY", "UID", "Familie_", "Nummer", "alteNummer"]
        for col in required_columns:
            if col not in df.columns:
                print(f"Warning: Required column '{col}' not found in data")

        # Track counts
        created = 0
        updated = 0
        skipped = 0
        errors = 0
        parent_not_found = 0

        # Use a transaction to ensure all-or-nothing
        if not dry_run:
            transaction.set_autocommit(False)

        try:
            # Process each record
            for index, row in df.iterrows():
                try:
                    # Extract ONLY the specified columns
                    key = (
                        row["__KEY"]
                        if "__KEY" in row and pd.notna(row["__KEY"])
                        else None
                    )
                    legacy_id = (
                        row["UID"] if "UID" in row and pd.notna(row["UID"]) else None
                    )
                    familie_ = (
                        row["Familie_"]
                        if "Familie_" in row and pd.notna(row["Familie_"])
                        else None
                    )
                    nummer = (
                        row["Nummer"]
                        if "Nummer" in row and pd.notna(row["Nummer"])
                        else None
                    )
                    alte_nummer = (
                        row["alteNummer"]
                        if "alteNummer" in row and pd.notna(row["alteNummer"])
                        else None
                    )

                    # Skip if no legacy_id available
                    if not legacy_id:
                        skipped += 1
                        print(f"Skipping variant with no UID: {index}")
                        continue

                    # Skip if the variant already exists and skip_existing is True
                    if (
                        skip_existing
                        and VariantProduct.objects.filter(legacy_id=legacy_id).exists()
                    ):
                        skipped += 1
                        print(f"Skipping existing variant: {alte_nummer}")
                        continue

                    # Use Nummer as the primary SKU if available, otherwise use alteNummer
                    primary_sku = str(nummer) if nummer is not None else alte_nummer

                    # Find parent product by Familie_ field
                    parent = None
                    if familie_:
                        parent_candidates = ParentProduct.objects.filter(
                            legacy_id=familie_,
                        )
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    # If parent not found by Familie_, try to find by base_sku
                    if not parent and alte_nummer and "-" in alte_nummer:
                        # Extract base_sku from alteNummer (everything before the last hyphen)
                        last_hyphen_index = alte_nummer.rfind("-")
                        base_sku = alte_nummer[:last_hyphen_index]
                        variant_code = alte_nummer[last_hyphen_index + 1 :]

                        # Try to find parent by base_sku
                        parent_candidates = ParentProduct.objects.filter(
                            base_sku=base_sku,
                        )
                        if parent_candidates.exists():
                            parent = parent_candidates.first()
                    else:
                        # If no hyphen in alteNummer, use the whole SKU as base_sku
                        base_sku = alte_nummer
                        variant_code = ""

                    # If still no parent, skip this variant
                    if not parent:
                        parent_not_found += 1
                        print(
                            f"Parent product not found for variant: {alte_nummer} - Skipping",
                        )
                        continue

                    # Create variant data with ONLY the specified fields
                    variant_data = {
                        "sku": primary_sku,
                        "base_sku": base_sku if "base_sku" in locals() else alte_nummer,
                        "variant_code": (
                            variant_code if "variant_code" in locals() else ""
                        ),
                        "name": f"Variant {primary_sku}",  # Simple name since Bezeichnung not included
                        "legacy_id": legacy_id,
                        "legacy_sku": alte_nummer,
                        "parent": parent,
                        "is_active": True,  # Default to active
                        # Store the original keys from legacy system
                        "legacy_key": key,
                    }

                    # Print variant data in dry run mode
                    if dry_run:
                        print(f"Would create variant: {variant_data}")
                        created += 1
                        continue

                    # Create or update the variant
                    with transaction.atomic():
                        variant, created_status = (
                            VariantProduct.objects.update_or_create(
                                legacy_id=legacy_id,
                                defaults=variant_data,
                            )
                        )

                        if created_status:
                            created += 1
                            print(f"Created variant: {variant.sku}")
                        else:
                            updated += 1
                            print(f"Updated variant: {variant.sku}")

                except Exception as e:
                    errors += 1
                    print(f"Error processing variant {index}: {e!s}")

            # Commit the transaction if not a dry run
            if not dry_run:
                transaction.commit()
                print("Committed changes to database")
            else:
                print("DRY RUN - No changes were made to the database")

            # Print summary
            print("\nImport summary:")
            print(f"Total records: {len(df)}")
            print(f"Created/Updated: {created + updated}")
            print(f"Skipped: {skipped}")
            print(f"Errors: {errors}")
            print(f"Parent not found: {parent_not_found}")

            return (created, updated, skipped, parent_not_found)

        except Exception as e:
            # Rollback the transaction if not a dry run
            if not dry_run:
                transaction.rollback()
            print(f"Error during import, rolling back: {e!s}")
            return (0, 0, 0, 0)

        finally:
            # Reset autocommit
            if not dry_run:
                transaction.set_autocommit(True)

    except Exception as e:
        print(f"Error fetching data: {e!s}")
        return (0, 0, 0, 0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Import Artikel_Variante with minimal columns",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of records to import",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip existing products",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without saving",
    )

    args = parser.parse_args()

    created, updated, skipped, parent_not_found = import_artikel_variante(
        limit=args.limit,
        skip_existing=args.skip_existing,
        dry_run=args.dry_run,
    )

    print(
        f"Import completed: {created} created, {updated} updated, {skipped} skipped, {parent_not_found} missing parents",
    )
