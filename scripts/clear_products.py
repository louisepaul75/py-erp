#!/usr/bin/env python
"""
Script to clear the ParentProduct and VariantProduct tables.
Run with: python clear_products.py
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django models
from pyerp.products.models import ParentProduct, VariantProduct

# Count before deletion
parent_count_before = ParentProduct.objects.count()
variant_count_before = VariantProduct.objects.count()

print(f"Before deletion: {parent_count_before} parent products, {variant_count_before} variant products")

# Delete all records
parent_result = ParentProduct.objects.all().delete()
variant_result = VariantProduct.objects.all().delete()

# Count after deletion
parent_count_after = ParentProduct.objects.count()
variant_count_after = VariantProduct.objects.count()

print(f"After deletion: {parent_count_after} parent products, {variant_count_after} variant products")
print(f"Deleted: {parent_count_before - parent_count_after} parent products, {variant_count_before - variant_count_after} variant products")
print(f"Delete results: {parent_result}, {variant_result}") 