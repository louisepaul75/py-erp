#!/usr/bin/env python
"""
Script to clear the ParentProduct and VariantProduct tables, then recreate them with only
the necessary columns using the existing import scripts.
"""

import os
import subprocess
import sys

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings.development")
django.setup()

# Now we can import Django models
from pyerp.products.models import ParentProduct, VariantProduct


def clear_product_tables():
    """Clear the ParentProduct and VariantProduct tables."""
    # Count before deletion
    parent_count_before = ParentProduct.objects.count()
    variant_count_before = VariantProduct.objects.count()

    print(
        f"Before deletion: {parent_count_before} parent products, {variant_count_before} variant products",
    )

    # Delete all records
    variant_result = VariantProduct.objects.all().delete()
    parent_result = ParentProduct.objects.all().delete()

    # Count after deletion
    parent_count_after = ParentProduct.objects.count()
    variant_count_after = VariantProduct.objects.count()

    print(
        f"After deletion: {parent_count_after} parent products, {variant_count_after} variant products",
    )
    print(
        f"Deleted: {parent_count_before - parent_count_after} parent products, {variant_count_before - variant_count_after} variant products",
    )
    print(f"Delete results: parents={parent_result}, variants={variant_result}")


def run_import_commands():
    """Run the import scripts to recreate the tables with only necessary columns."""
    # First import parent products
    print("\n=== Importing Parent Products ===")
    parent_import_result = subprocess.run(
        [sys.executable, "manage.py", "wipe_and_reload_parents"],
        capture_output=True,
        text=True,
        check=False,
    )
    print(parent_import_result.stdout)
    if parent_import_result.stderr:
        print("Errors during parent import:")
        print(parent_import_result.stderr)

    # Then import variant products
    print("\n=== Importing Variant Products ===")
    variant_import_result = subprocess.run(
        [sys.executable, "manage.py", "import_artikel_variante"],
        capture_output=True,
        text=True,
        check=False,
    )
    print(variant_import_result.stdout)
    if variant_import_result.stderr:
        print("Errors during variant import:")
        print(variant_import_result.stderr)

    # Finally, fix parent-variant relationships
    print("\n=== Fixing Variant-Parent Relationships ===")
    fix_relationships_result = subprocess.run(
        [sys.executable, "manage.py", "fix_variant_parent_relationships"],
        capture_output=True,
        text=True,
        check=False,
    )
    print(fix_relationships_result.stdout)
    if fix_relationships_result.stderr:
        print("Errors during relationship fixing:")
        print(fix_relationships_result.stderr)


if __name__ == "__main__":
    print("Starting product table cleanup and recreation...")
    clear_product_tables()
    run_import_commands()
    print("Product table cleanup and recreation completed!")
