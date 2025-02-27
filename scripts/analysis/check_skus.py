#!/usr/bin/env python
"""
Script to check the SKUs in our database.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

from pyerp.products.models import Product

def main():
    """Check the SKUs in our database."""
    # Get total count
    total_products = Product.objects.count()
    print(f"Total products: {total_products}")
    
    # Get sample SKUs
    print("\nSample SKUs from database:")
    for i, product in enumerate(Product.objects.all()[:10]):
        print(f"{i+1}. SKU: {product.sku}, Name: {product.name}")
    
    # Check if any SKUs match the article numbers from the API
    api_article_numbers = ['214808', '229092']
    print("\nChecking if any products match the article numbers from the API:")
    for article_number in api_article_numbers:
        products = Product.objects.filter(sku=article_number)
        if products.exists():
            print(f"Found match for {article_number}: {products.first().name}")
        else:
            print(f"No match found for {article_number}")

if __name__ == '__main__':
    main() 