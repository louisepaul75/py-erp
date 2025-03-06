import os
import sys

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings.development")
django.setup()

# Import Django models and database connection
from django.db import connection
from django.db.models import Count

from pyerp.products.models import Product


def list_tables():
    """List all tables in the database"""
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("\n=== TABLES IN DATABASE ===")
        for table in tables:
            print(f"- {table[0]}")


def check_product_table_structure():
    """Check if there are separate parent and variant tables or a single products table"""
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE products_product")
        columns = cursor.fetchall()

        print("\n=== PRODUCT TABLE STRUCTURE ===")
        for column in columns:
            print(f"- {column[0]}: {column[1]}")

        # Check if there are is_parent and parent_id fields
        has_is_parent = any(column[0] == "is_parent" for column in columns)
        has_parent_id = any(column[0] == "parent_id" for column in columns)

        if has_is_parent and has_parent_id:
            print(
                "\nCONCLUSION: There is a single 'products_product' table that stores both parent and variant products.",
            )
            print("Parent products have is_parent=True and parent_id=NULL")
            print(
                "Variant products have is_parent=False and parent_id pointing to their parent product",
            )
        else:
            print(
                "\nCONCLUSION: The product table structure is different than expected.",
            )


def count_products_by_type():
    """Count products by type (parent vs variant)"""
    total = Product.objects.count()
    parents = Product.objects.filter(is_parent=True).count()
    variants = Product.objects.filter(is_parent=False).count()

    print("\n=== PRODUCT COUNTS ===")
    print(f"Total products: {total}")
    print(f"Parent products: {parents}")
    print(f"Variant products: {variants}")

    # Count variants per parent
    parents_with_variants = (
        Product.objects.filter(is_parent=True)
        .annotate(
            variant_count=Count("variants"),
        )
        .filter(variant_count__gt=0)
        .count()
    )

    print(f"Parents with variants: {parents_with_variants}")


if __name__ == "__main__":
    try:
        list_tables()
        check_product_table_structure()
        count_products_by_type()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
