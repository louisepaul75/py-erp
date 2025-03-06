#!/usr/bin/env python
"""
Temporary script to list products in the database.
"""

import os

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

# Import models after Django setup
from pyerp.products.models import Product, ProductCategory


def main():
    """List all products in the database."""
    print("=== Product Categories ===")
    categories = ProductCategory.objects.all()
    print(f"Total categories: {categories.count()}")
    for category in categories:
        print(f"- {category.code}: {category.name}")

    print("\n=== Products ===")
    products = Product.objects.all()
    print(f"Total products: {products.count()}")

    if products.count() > 0:
        print("\nProduct details:")
        for product in products:
            print(f"- SKU: {product.sku}")
            print(f"  Name: {product.name}")
            print(f"  Base SKU: {product.base_sku}")
            print(f"  Variant: {product.variant_code}")
            print(f"  Category: {product.category}")
            print(f"  Parent: {product.parent}")
            print(f"  Is Parent: {product.is_parent}")
            print("  ---")
    else:
        print("No products found in the database.")


if __name__ == "__main__":
    main()
