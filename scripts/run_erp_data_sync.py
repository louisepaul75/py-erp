#!/usr/bin/env python
"""
Script to import ERP data (Artikel_Familie and Artikel_Variante) using the SimpleAPIClient from getTable.py.
"""

import os
import sys

import django

# Add the project root to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

# Import Django models and the SimpleAPIClient from getTable.py
from pyerp.direct_api.scripts.getTable import SimpleAPIClient
from pyerp.products.models import ParentProduct, VariantProduct


def import_artikel_familie(limit=None, dry_run=False):
    """
    Import Artikel_Familie records as parent products.

    Args:
        limit: Maximum number of records to import
        dry_run: If True, don't save changes to the database

    Returns:
        tuple: (created_count, updated_count, skipped_count)
    """
    print("Fetching Artikel_Familie data...")
    try:
        # Initialize the API client
        client = SimpleAPIClient()

        # Fetch data from the legacy ERP
        df = client.fetch_table(
            "Artikel_Familie",
            top=limit or 1000,
            new_data_only=False,
        )

        if df is None or len(df) == 0:
            print("No data returned from Artikel_Familie table")
            return (0, 0, 0)

        print(f"Retrieved {len(df)} Artikel_Familie records")

        # Initialize counters
        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Process each record
        for index, row in df.iterrows():
            # Extract data from the row
            uid = row.get("UID")
            key = row.get("__KEY")
            nummer = row.get("Nummer")
            bezeichnung = row.get("Bezeichnung")

            if not nummer or not bezeichnung:
                print(f"Skipping record with missing required fields: {row}")
                skipped_count += 1
                continue

            # Try to find existing parent product
            parent = None
            try:
                parent = ParentProduct.objects.get(sku=nummer)
                print(f"Found existing parent product: {parent.sku} - {parent.name}")
                updated = False

                # Update fields if needed
                if parent.name != bezeichnung:
                    parent.name = bezeichnung
                    updated = True

                if parent.legacy_id != key:
                    parent.legacy_id = key
                    updated = True

                if updated and not dry_run:
                    parent.save()
                    updated_count += 1
                    print(f"Updated parent product: {parent.sku} - {parent.name}")
                else:
                    skipped_count += 1

            except ParentProduct.DoesNotExist:
                # Create new parent product
                parent = ParentProduct(
                    sku=nummer,
                    name=bezeichnung,
                    legacy_id=key,
                    is_active=True,
                )

                if not dry_run:
                    parent.save()
                    created_count += 1
                    print(f"Created parent product: {parent.sku} - {parent.name}")
                else:
                    print(f"Would create parent product: {nummer} - {bezeichnung}")
                    created_count += 1

        return (created_count, updated_count, skipped_count)

    except Exception as e:
        print(f"Error fetching or processing data: {e!s}")
        return (0, 0, 0)


def import_artikel_variante(limit=None, dry_run=False):
    """
    Import Artikel_Variante records as variant products.

    Args:
        limit: Maximum number of records to import
        dry_run: If True, don't save changes to the database

    Returns:
        tuple: (created_count, updated_count, skipped_count, parent_not_found_count)
    """
    print("Fetching Artikel_Variante data...")
    try:
        # Initialize the API client
        client = SimpleAPIClient()

        # Fetch data from the legacy ERP
        df = client.fetch_table(
            "Artikel_Variante",
            top=limit or 1000,
            new_data_only=False,
        )

        if df is None or len(df) == 0:
            print("No data returned from Artikel_Variante table")
            return (0, 0, 0, 0)

        print(f"Retrieved {len(df)} Artikel_Variante records")

        # Initialize counters
        created_count = 0
        updated_count = 0
        skipped_count = 0
        parent_not_found_count = 0

        # Process each record
        for index, row in df.iterrows():
            # Extract data from the row
            uid = row.get("UID")
            key = row.get("__KEY")
            nummer = row.get("Nummer")
            bezeichnung = row.get("Bezeichnung")
            familie_key = row.get("Familie_")

            if not nummer or not bezeichnung:
                print(f"Skipping record with missing required fields: {row}")
                skipped_count += 1
                continue

            # Try to find parent product if Familie_ is provided
            parent = None
            if familie_key:
                try:
                    parent = ParentProduct.objects.get(legacy_id=familie_key)
                except ParentProduct.DoesNotExist:
                    print(f"Parent product not found for Familie_ {familie_key}")
                    parent_not_found_count += 1

            # Try to find existing variant product
            variant = None
            try:
                variant = VariantProduct.objects.get(sku=nummer)
                print(f"Found existing variant product: {variant.sku} - {variant.name}")
                updated = False

                # Update fields if needed
                if variant.name != bezeichnung:
                    variant.name = bezeichnung
                    updated = True

                if variant.legacy_id != key:
                    variant.legacy_id = key
                    updated = True

                if parent and variant.parent != parent:
                    variant.parent = parent
                    updated = True

                if updated and not dry_run:
                    variant.save()
                    updated_count += 1
                    print(f"Updated variant product: {variant.sku} - {variant.name}")
                else:
                    skipped_count += 1

            except VariantProduct.DoesNotExist:
                # Create new variant product
                variant = VariantProduct(
                    sku=nummer,
                    name=bezeichnung,
                    legacy_id=key,
                    parent=parent,
                    is_active=True,
                )

                if not dry_run:
                    variant.save()
                    created_count += 1
                    print(f"Created variant product: {variant.sku} - {variant.name}")
                else:
                    print(f"Would create variant product: {nummer} - {bezeichnung}")
                    created_count += 1

        return (created_count, updated_count, skipped_count, parent_not_found_count)

    except Exception as e:
        print(f"Error fetching or processing data: {e!s}")
        return (0, 0, 0, 0)


def main():
    """Main function to run the import process."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Import ERP data (Artikel_Familie and Artikel_Variante)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without making changes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of records to import",
    )
    parser.add_argument(
        "--skip-familie",
        action="store_true",
        help="Skip importing Artikel_Familie",
    )
    parser.add_argument(
        "--skip-variante",
        action="store_true",
        help="Skip importing Artikel_Variante",
    )

    args = parser.parse_args()

    # Import Artikel_Familie if not skipped
    if not args.skip_familie:
        print("\n=== Importing Artikel_Familie ===")
        created, updated, skipped = import_artikel_familie(
            limit=args.limit,
            dry_run=args.dry_run,
        )
        print(
            f"\nArtikel_Familie import completed: {created} created, {updated} updated, {skipped} skipped",
        )

    # Import Artikel_Variante if not skipped
    if not args.skip_variante:
        print("\n=== Importing Artikel_Variante ===")
        created, updated, skipped, parent_not_found = import_artikel_variante(
            limit=args.limit,
            dry_run=args.dry_run,
        )
        print(
            f"\nArtikel_Variante import completed: {created} created, {updated} updated, {skipped} skipped, {parent_not_found} parent not found",
        )


if __name__ == "__main__":
    main()
