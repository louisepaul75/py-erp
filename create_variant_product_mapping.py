#!/usr/bin/env python
"""
Script to create the EntityMappingConfig for VariantProduct
"""
import os
import sys
import django
import json

# Set up Django environment
sys.path.append('')  # Add the project directory to path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

from pyerp.legacy_sync.models import EntityMappingConfig

# Check if the config already exists
if EntityMappingConfig.objects.filter(entity_type='variant_product').exists():
    print("EntityMappingConfig for variant_product already exists, updating...")
    config = EntityMappingConfig.objects.get(entity_type='variant_product')
else:
    print("Creating new EntityMappingConfig for variant_product...")
    config = EntityMappingConfig(entity_type='variant_product')

# Set up the config - using a more generic table name that might be used in the legacy system
# This can be updated later when the correct table name is confirmed
config.legacy_table = 'Artikel'  # Try with 'Artikel' instead of 'Produkte'
config.new_model = 'pyerp.products.models.VariantProduct'

# Define the field mappings
# This is a simplified mapping - our custom map_variant_product_fields function
# will handle the complex mappings
field_mappings = {
    "ID": {
        "new_field": "legacy_id",
        "required": True
    },
    "EAN": {
        "new_field": "ean",
        "required": False
    },
    "SKU": {
        "new_field": "sku",
        "required": False
    },
    "Artikelbezeichnung": {
        "new_field": "name",
        "required": True
    },
    # Alternative field names that might be used in the legacy system
    "ArtikelID": {
        "new_field": "legacy_id",
        "required": False
    },
    "Bezeichnung": {
        "new_field": "name",
        "required": False
    },
    "Artikelnummer": {
        "new_field": "sku",
        "required": False
    },
    # Most fields will be handled in the map_variant_product_fields function
    # The field_mappings here are primarily for the basic fields that can be mapped directly
}

config.field_mappings = field_mappings
config.is_active = True
config.save()

print(f"EntityMappingConfig for variant_product saved with ID: {config.id}")
print("Note: The complex field mappings for pricing, physical attributes, and dates")
print("will be handled by the custom map_variant_product_fields function in sync_tasks.py")
print("\nIf you encounter 404 errors when trying to sync, you may need to update the legacy_table")
print("value in the EntityMappingConfig to match the actual table name in the legacy system.") 