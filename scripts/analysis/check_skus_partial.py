#!/usr/bin/env python
"""
Script to check for partial matches between product SKUs and article numbers.
"""

import os

import django
from django.core.management.base import BaseCommand

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

from pyerp.external_api.images_cms.client import ImageAPIClient
from pyerp.products.models import Product


def main():
    """Check for partial matches between product SKUs and article numbers."""
    # Initialize API client
    client = ImageAPIClient()

    # Get all article numbers from the first 5 pages of the API
    article_numbers = set()
    for page in range(1, 6):
        print(f"Fetching page {page} from API...")
        data = client.get_all_images(page=page, page_size=20)

        if not data or not data.get("results"):
            continue

        for item in data.get("results", []):
            for article in item.get("articles", []):
                if article.get("number"):
                    article_numbers.add(article.get("number"))

    print(f"\nFound {len(article_numbers)} unique article numbers in the API")
    print(f"Sample article numbers: {list(article_numbers)[:10]}")

    # Get all product SKUs from the database
    product_skus = set(Product.objects.exclude(sku="").values_list("sku", flat=True))
    print(f"\nFound {len(product_skus)} unique product SKUs in the database")
    print(f"Sample product SKUs: {list(product_skus)[:10]}")

    # Check for exact matches
    exact_matches = article_numbers.intersection(product_skus)
    print(
        f"\nFound {len(exact_matches)} exact matches between article numbers and product SKUs",
    )
    if exact_matches:
        print(f"Sample exact matches: {list(exact_matches)[:10]}")

    # Check for partial matches
    print("\nChecking for partial matches...")
    partial_matches = []
    for sku in list(product_skus)[:100]:  # Check first 100 SKUs for performance
        for article_number in article_numbers:
            if sku in article_number or article_number in sku:
                partial_matches.append((sku, article_number))
                if len(partial_matches) >= 10:
                    break
        if len(partial_matches) >= 10:
            break

    print(f"Found {len(partial_matches)} partial matches")
    for sku, article_number in partial_matches:
        print(f"SKU: {sku}, Article Number: {article_number}")


if __name__ == "__main__":
    main()
